"""Bounded post-supervisor native measurements; no model or acceptance calls."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import time

P = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167')
D = P / 'follow-up'
spec = importlib.util.spec_from_file_location('closed_supervisor', P / 'supervisor/run_stage.py')
closed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(closed)
S = closed.base.SCRATCH
ROOT = S / 'post-supervisor-diagnosis'
BASELINE = ROOT / 'communication-baseline'
TEMPLATE = json.loads((P / 'evidence/format.json').read_text())['command']
IMAGE_INDEX = TEMPLATE.index('--entrypoint') + 2


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def command(workspace, label, args, test_environment=False):
    cmd = TEMPLATE[:IMAGE_INDEX + 1]
    cmd[cmd.index('--name') + 1] = 'score-com1167-followup-' + label
    cmd[cmd.index('--workdir') + 1] = str(workspace)
    tool_args = TEMPLATE[IMAGE_INDEX + 1:]
    cmd += tool_args[:tool_args.index('run')] + args
    if test_environment:
        env = closed.base.build_environment(S)
        env['HOME'] = str(S / 'container-home')
        cmd += ['--test_env=' + key + '=' + value for key, value in sorted(env.items())]
    return cmd


def measure(label, cmd, workspace, timeout=1800):
    closed.guard()
    record = {'kind': 'ad_hoc_deterministic_measurement', 'native_run_id': None,
              'command': cmd, 'cwd': str(workspace), 'started_at_epoch': time.time(),
              'timeout_seconds': timeout, 'subject_sha256': closed.base.source_hashes(workspace),
              'authority': 'User go after completed supervisor; no additional paid calls'}
    stdout = D / (label + '.stdout')
    stderr = D / (label + '.stderr')
    with stdout.open('wb') as out, stderr.open('wb') as err:
        process = subprocess.Popen(cmd, stdout=out, stderr=err, start_new_session=True)
        try:
            while process.poll() is None:
                closed.guard()
                if time.time() - record['started_at_epoch'] > timeout:
                    raise TimeoutError(label + ' exceeded its bound')
                time.sleep(1)
            record['exit_code'] = process.returncode
        except BaseException:
            subprocess.run(['/usr/bin/docker', 'rm', '--force', cmd[cmd.index('--name') + 1]],
                           capture_output=True, timeout=15)
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=15)
            raise
    record.update(finished_at_epoch=time.time(), stdout_sha256=closed.base.sha(stdout),
                  stderr_sha256=closed.base.sha(stderr))
    save(D / (label + '.json'), record)
    print(json.dumps({'check': label, 'exit_code': record['exit_code']}), flush=True)
    return record


def main():
    closed.guard()
    ROOT.mkdir(exist_ok=True)
    if BASELINE.exists():
        raise RuntimeError('Preserve prior workspace; do not overwrite it')
    proc = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'clone', '--no-hardlinks',
                           str(P / 'candidate'), str(BASELINE)], capture_output=True, text=True, check=True)
    (D / 'baseline-clone.stdout').write_text(proc.stdout)
    (D / 'baseline-clone.stderr').write_text(proc.stderr)
    head = subprocess.check_output(['git', '-C', str(BASELINE), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == 'e3d126c2d7569345cf5f790310702eb00cd86b06'
    assert not (BASELINE / 'score/mw/com/test/api_idempotency').exists()
    save(D / 'baseline-source-hashes.json', closed.base.source_hashes(BASELINE))
    original = BASELINE / 'BUILD'
    (D / 'baseline-BUILD.original').write_bytes(original.read_bytes())
    measure('baseline-copyright-original', command(BASELINE, 'base-cr-original', ['run', '//:copyright.check']), BASELINE)
    # Apply only the already documented utility-path correction to expose baseline findings.
    original.write_bytes((P / 'candidate/BUILD').read_bytes())
    save(D / 'baseline-measurement-overlay.json', {'path': 'BUILD', 'sha256': closed.base.sha(original),
         'purpose': 'Only existing copyright_checker filesystem-path correction; no issue 1167 files',
         'patch': subprocess.check_output(['git', '-C', str(BASELINE), 'diff', '--', 'BUILD'], text=True)})
    measure('baseline-copyright-path-overlay', command(BASELINE, 'base-cr-overlay', ['run', '//:copyright.check']), BASELINE)
    measure('baseline-visibility', command(BASELINE, 'base-visibility', ['test', '//quality/visibility_guard:visibility_guard_test', '--nocache_test_results'], True), BASELINE)
    native = Path(json.loads((P / 'evidence/format.json').read_text())['cwd'])
    measure('candidate-visibility', command(native, 'candidate-visibility', ['test', '//quality/visibility_guard:visibility_guard_test', '--nocache_test_results'], True), native)
    for label, tree in [('baseline', BASELINE), ('candidate', native)]:
        log = tree / 'bazel-testlogs/quality/visibility_guard/visibility_guard_test/test.log'
        if log.exists():
            (D / (label + '-visibility.test.log')).write_bytes(log.read_bytes())
    save(D / 'diagnosis-result.json', {'status': 'measurements_complete', 'paid_calls': 0,
         'original_supervisor_attempts_consumed': 3, 'source_changes_to_contribution': False,
         'acceptance': 'pending_offline_review'})


if __name__ == '__main__':
    main()
