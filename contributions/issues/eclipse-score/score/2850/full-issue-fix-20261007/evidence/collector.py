"""Measure native checks in the bound isolated checkout and preserve raw output."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, '/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import build_environment, validate_run_root

PACKET = Path(__file__).resolve().parent
ROOT = Path(json.loads((PACKET / 'workspace.json').read_text())['root'])
IMAGE = 'sha256:8332c7a66af3f1cfdb04ce803ce4b7711a976fb2bcbdda3cdae598c96c11fa88'
OLD = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-communication-bug-recovery-fw8j963z')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def run(label, command, repository='communication', extra_env=None):
    validate_run_root(ROOT)
    output = PACKET / 'evidence'
    output.mkdir(exist_ok=True)
    receipt = output / f'{label}.json'
    if receipt.exists():
        raise FileExistsError(receipt)
    cwd = ROOT / repository
    subjects = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=cwd).decode().split('\0')
    record = {
        'command': command, 'cwd': str(cwd), 'started_at': time.time(),
        'baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd, text=True).strip(),
        'subject_hashes': {name: digest(cwd / name) for name in subjects if name and (cwd / name).is_file()},
        'carried_evidence': False,
    }
    stdout, stderr = output / f'{label}.stdout', output / f'{label}.stderr'
    with stdout.open('wb') as out, stderr.open('wb') as err:
        process = subprocess.Popen(command, cwd=cwd, env={**os.environ, **build_environment(ROOT), **(extra_env or {})}, stdout=out, stderr=err)
        try:
            while process.poll() is None:
                validate_run_root(ROOT)
                time.sleep(2)
        except BaseException:
            process.terminate()
            process.wait()
            raise
    final_subjects = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=cwd).decode().split('\0')
    final_hashes = {name: digest(cwd / name) for name in final_subjects if name and (cwd / name).is_file()}
    record['source_unchanged_during_check'] = final_hashes == record['subject_hashes']
    record['final_subject_hashes'] = final_hashes
    record.update(exit_code=process.returncode, finished_at=time.time(), stdout_sha256=digest(stdout), stderr_sha256=digest(stderr))
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(label, process.returncode, flush=True)
    return process.returncode


def bazel(label, args, repository='communication'):
    validate_run_root(ROOT)
    for name in ['tools', 'container-home', 'container-tmp', 'container-var-tmp', 'repository-cache']:
        (ROOT / name).mkdir(exist_ok=True)
    version = (ROOT / repository / '.bazelversion').read_text().strip()
    binary = ROOT / f'tools/bazel-{version}'
    if not binary.exists():
        source = OLD if version == '8.7.0' else ROOT.parent / 'score-3115-upstream-p_lepjsx'
        shutil.copy2(source / f'tools/bazel-{version}', binary)
    if version == '8.6.0' and digest(binary) != '9860da9c9386bbc023feed8f43af3105d338727d77b644fa6aeca45a4a11957c':
        raise ValueError('Pinned Bazel 8.6.0 binary digest mismatch')
    command = ['docker', 'run', '--rm', '--read-only', '--network', 'host', '--user', '1000:1000',
               '--cpus', '8', '--memory', '16g', '--cap-add', 'SYS_ADMIN',
               '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
               '--mount', f'type=bind,source={ROOT},target={ROOT}',
               '--mount', f'type=bind,source={ROOT / "container-tmp"},target=/tmp',
               '--mount', f'type=bind,source={ROOT / "container-var-tmp"},target=/var/tmp',
               '--workdir', str(ROOT / repository), '--env', 'HOME=' + str(ROOT / 'container-home')]
    environment = build_environment(ROOT)
    environment.pop('TEST_TMPDIR', None)
    for key, value in environment.items():
        command += ['--env', key + '=' + value]
    command += ['--entrypoint', str(binary), IMAGE, '--output_user_root=' + str(ROOT / f'bazel-{repository}'), '--batch', *args]
    return run(label, command, repository)


if __name__ == '__main__':
    raise SystemExit(bazel(sys.argv[1], sys.argv[2:]))


def container(label, args, repository='docs-as-code'):
    """Run project tooling in the recorded image with task-scoped Bazel/cache paths."""
    import shlex
    validate_run_root(ROOT)
    directory = ROOT / 'tools/bin'
    directory.mkdir(exist_ok=True)
    shim = directory / 'bazel'
    shim.write_text('#!/bin/sh\nexec ' + shlex.quote(str(ROOT / 'tools/bazel-8.6.0')) + ' --output_user_root=' + shlex.quote(str(ROOT / 'bazel-docs-as-code')) + ' --batch "$@"\n')
    shim.chmod(0o755)
    command = ['docker', 'run', '--rm', '--read-only', '--network', 'host', '--user', '1000:1000',
               '--cpus', '8', '--memory', '16g', '--cap-add', 'SYS_ADMIN',
               '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
               '--mount', f'type=bind,source={ROOT},target={ROOT}',
               '--mount', f'type=bind,source={ROOT / "container-tmp"},target=/tmp',
               '--mount', f'type=bind,source={ROOT / "container-var-tmp"},target=/var/tmp',
               '--workdir', str(ROOT / repository), '--env', 'HOME=' + str(ROOT / 'container-home'),
               '--env', 'PATH=' + str(directory) + ':/usr/local/bin:/usr/bin:/bin']
    for key, value in build_environment(ROOT).items():
        command += ['--env', key + '=' + value]
    command += ['--entrypoint', args[0], IMAGE, *args[1:]]
    return run(label, command, repository)
