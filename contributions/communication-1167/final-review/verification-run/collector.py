"""No-model native measurement/export, derived from preserved stable collectors."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from score_sw_fabric.storage import build_environment, validate_run_root
HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / 'configuration.json').read_text())
SCRATCH = Path(CONFIG['scratch_root'])
SERVER = 'http://127.0.0.1:43916'
AUTH_FILE = Path('/home/jefferson/.local/state/s-core/fabro/someip84-server/cli-auth.json')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def api(route, raw=False):
    token = json.loads(AUTH_FILE.read_text())['servers'][SERVER]['token']
    req = urllib.request.Request(SERVER + route, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=15) as response:
        body = response.read(20_000_001)
    if len(body) > 20_000_000:
        raise ValueError('Native response exceeds export bound')
    return body if raw else json.loads(body)


def source_hashes(tree):
    return {str(p.relative_to(tree)): sha(p) for p in tree.rglob('*')
            if p.is_file() and not p.is_symlink() and '.git' not in p.relative_to(tree).parts}


def guard():
    validate_run_root(SCRATCH)
    mount = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(SCRATCH), '-o', 'SOURCE,UUID'], text=True))['filesystems'][0]
    if mount['source'] != CONFIG['required_device'] or mount['uuid'] != CONFIG['expected_uuid']:
        raise ValueError('Bound image/device changed; stop without relocating')
    for relative, expected in json.loads((HERE / 'frozen-inputs.json').read_text()).items():
        if sha(HERE / relative) != expected:
            raise ValueError('Frozen verification input changed: ' + relative)

def measure(command, label, cwd, env, timeout):
    if label in {'focused', 'test-all'}:
        inherited = build_environment(SCRATCH)
        inherited['HOME'] = str(SCRATCH / 'container-home')
        inherited.pop('TEST_TMPDIR', None)
        command = command + ['--test_env=' + key + '=' + value for key, value in sorted(inherited.items())]
    record = {'command': command, 'cwd': str(cwd), 'fabro_run_id': (HERE / 'current-native-run-id').read_text().strip(), 'started_at_epoch': time.time(),
              'timeout_seconds': timeout, 'subject_sha256': json.loads((HERE / 'candidate-hashes.json').read_text())}
    (HERE / 'evidence').mkdir(exist_ok=True)
    out = HERE / 'evidence' / (label + '.stdout')
    err = HERE / 'evidence' / (label + '.stderr')
    with out.open('wb') as stdout, err.open('wb') as stderr:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            while process.poll() is None:
                guard()
                if time.time() - record['started_at_epoch'] > timeout:
                    raise TimeoutError('Measured command exceeded its bound')
                time.sleep(1)
            record['exit_code'] = process.returncode
        except BaseException as exc:
            if command[:2] == ['/usr/bin/docker', 'run'] and '--name' in command:
                container = command[command.index('--name') + 1]
                subprocess.run(['/usr/bin/docker', 'rm', '--force', container], capture_output=True, timeout=15)
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL); process.wait()
            record.update(exit_code=process.returncode, stop_reason=str(exc))
    record.update(finished_at_epoch=time.time(), stdout_sha256=sha(out), stderr_sha256=sha(err))
    write('evidence/' + label + '.json', record)
    return record


def verify(context):
    candidate = HERE / 'candidate'
    expected = json.loads((HERE / 'candidate-hashes.json').read_text())
    if source_hashes(candidate) != expected:
        raise ValueError('Candidate changed after drafting')
    # Owned disposable workspace reused after terminal predecessor; all checks run fresh against corrected source.
    native = SCRATCH / 'native-workspace'
    actual = source_hashes(native)
    if any(actual.get(path) != digest for path, digest in expected.items()):
        raise ValueError('Closed native workspace does not match bound candidate')
    extras = set(actual) - set(expected)
    if any(not path.startswith('.ruff_cache/') for path in extras):
        raise ValueError('Unknown extra source in closed native workspace')
    write('workspace-subject-match.json', {'workspace': str(native),
          'matched_source_count': len(expected), 'known_ruff_cache_files': len(extras),
          'candidate_sha256': sha(HERE / 'candidate-hashes.json'),
          'carried_evidence': False, 'checks': 'All required checks run fresh; owned native build cache retained after terminal predecessor'})
    subprocess.run(['git', '-C', str(native), '-c', 'core.hooksPath=/dev/null', 'rev-parse', '--is-inside-work-tree'], check=True, capture_output=True)
    storage_env = build_environment(SCRATCH)
    env = {**os.environ, **storage_env, 'PYTHONDONTWRITEBYTECODE': '1'}
    image = json.loads((HERE / 'build-environment.json').read_text())['image_id']
    if subprocess.check_output(['/usr/bin/docker', 'image', 'inspect', image, '--format', '{{.Id}}'], text=True).strip() != image:
        raise ValueError('Registered native build image changed')
    # Exact independently measured Bazel 8.7.0, matching the native .bazelversion.
    # New scratch and caches stay bound to this run's SSD; no existing queue is moved.
    tool = SCRATCH / 'tools/bazel-8.7.0'
    if not tool.is_file():
        write('verify-result.json', {'status': 'blocked', 'reason': 'Registered Bazelisk unavailable'})
        return
    write('tools.json', {'bazel_path': str(tool), 'sha256': sha(tool), 'build_image_id': image, 'workspace_reuse': 'Same owned bound workspace and native build action cache; preceding run terminal; forced fresh test results',
          'bazel_version_required': (native / '.bazelversion').read_text().strip()})
    base = [str(tool), '--output_user_root=' + str(SCRATCH / 'bazel-output'), '--batch']
    tasks = [('copyright', ['run', '//:copyright.check']), ('format', ['run', '//:format.check']),
             ('focused', ['test', '//score/mw/com/test/api_idempotency/...', '--nocache_test_results']),
             ('build-all', ['build', '//...']), ('test-all', ['test', '//...', '--nocache_test_results'])]
    records = []
    for label, args in tasks:
        guard()
        container_name = 'score-com1167-' + context['run_id'].lower() + '-' + label
        docker = ['/usr/bin/docker', 'run', '--rm', '--name', container_name, '--read-only',
                  '--network', 'host', '--user', '1000:1000', '--group-add', '999',
                  '--cap-add', 'SYS_ADMIN', '--security-opt', 'seccomp=unconfined',
                  '--security-opt', 'apparmor=unconfined',
                  '--mount', 'type=bind,source=' + str(SCRATCH) + ',target=' + str(SCRATCH),
                  '--mount', 'type=bind,source=' + str(SCRATCH / 'container-tmp') + ',target=/tmp',
                  '--mount', 'type=bind,source=' + str(SCRATCH / 'container-var-tmp') + ',target=/var/tmp',
                  '--mount', 'type=bind,source=' + str(SCRATCH / 'tools/docker-client') + ',target=/usr/bin/docker,readonly',
                  '--mount', 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock',
                  '--workdir', str(native), '--env', 'HOME=' + str(SCRATCH / 'container-home'),
                  '--env', 'PYTHONDONTWRITEBYTECODE=1']
        for key, value in storage_env.items():
            docker.extend(['--env', key + '=' + value])
        docker.extend(['--entrypoint', str(tool), image, *base[1:], *args, '--jobs=' + str(CONFIG['jobs'])])
        record = measure(docker, label, native, env, 1800)
        records.append({'check': label, **record})
        # Do not repeat a dependency failure through the same full target closure.
        if label == 'focused' and record['exit_code'] != 0:
            text = (HERE / 'evidence/focused.stderr').read_text(errors='replace')
            if any(word in text for word in ['Error downloading', 'Failed to fetch', 'no such package', 'Unable to find package', 'MODULE.bazel.lock is no longer up-to-date']):
                records.extend({'check': name, 'status': 'not_run_dependency_failure'} for name in ['build-all', 'test-all'])
                break
    status = 'measured_checks_passed_review_pending' if all(r.get('exit_code') == 0 for r in records) else 'failed_or_missing_checks'
    write('verify-result.json', {'status': status, 'checks': records,
          'engineering_acceptance': 'pending_offline_review', 'fixture_evidence': False})
    logs = native / 'bazel-testlogs'
    if logs.exists():
        for p in logs.rglob('*'):
            if p.is_file() and p.name in {'test.xml', 'test.log'}:
                dest = HERE / 'evidence/native-testlogs' / p.relative_to(logs)
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, dest)
    if status != 'measured_checks_passed_review_pending':
        raise RuntimeError('Native verification failed; measured results preserved for export')


def export(context):
    identifier = context['run_id']
    for suffix, name in [('', 'summary'), ('/state', 'state'), ('/stages?limit=200', 'stages')]:
        try:
            write('native-' + name + '.json', api('/api/v1/runs/' + identifier + suffix))
        except Exception as error:
            write('native-' + name + '-failure.json', {'reason': str(error)})
    guard()
    source = HERE / 'candidate'
    expected = json.loads((HERE / 'candidate-hashes.json').read_text())
    if source_hashes(source) != expected:
        raise ValueError('Corrected candidate changed after measurement')
    patch = subprocess.check_output(['git', '-C', str(source), 'diff', '--binary', '--', 'BUILD', 'score/mw/com/test/api_idempotency'])
    (HERE / 'communication-1167.patch').write_bytes(patch)
    validation = json.loads((HERE / 'verify-result.json').read_text()) if (HERE / 'verify-result.json').exists() else {'status': 'not_run'}
    artifacts = HERE / 'native-artifacts'
    artifacts.mkdir(exist_ok=True)
    native_bin = SCRATCH / 'native-workspace/bazel-bin/score/mw/com/test/api_idempotency'
    products = ['main_api_idempotency', 'libapi_idempotency_datatype.a', 'libapi_idempotency_datatype.so', 'integration_test/_oci_filesystem_api_idempotency_test.tar']
    retained = {}
    missing = []
    for relative in products:
        src = native_bin / relative
        if not src.is_file():
            missing.append(relative)
            continue
        dst = artifacts / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        retained[relative] = {'sha256': sha(dst), 'bytes': dst.stat().st_size, 'source': str(src), 'run_id': identifier}
    oci = native_bin / 'integration_test/_image_api_idempotency_test'
    if oci.is_dir():
        shutil.copytree(oci, artifacts / 'api_idempotency_test.oci', symlinks=False, dirs_exist_ok=True)
        for blob in (artifacts / 'api_idempotency_test.oci/blobs/sha256').iterdir():
            if sha(blob) != blob.name:
                raise ValueError('Exported OCI blob digest mismatch')
    else:
        missing.append('integration_test/api_idempotency_test.oci')
    for f in artifacts.rglob('*'):
        if f.is_file() and f.relative_to(artifacts).as_posix() not in retained:
            retained[f.relative_to(artifacts).as_posix()] = {'sha256': sha(f), 'bytes': f.stat().st_size, 'run_id': identifier}
    write('native-artifacts/manifest.json', {'files': retained, 'missing_products': missing, 'candidate_binding': '../candidate-hashes.json', 'source_sha256': sha(HERE / 'candidate-hashes.json'), 'run_id': identifier, 'native_baseline': CONFIG['native_baseline'], 'license': '../candidate/LICENSE'})
    (HERE / 'README.md').write_text('# Corrected communication #1167 verification\n\nFabro run: `' + identifier + '`. Native checks: **' + validation['status'] + '**. Stable fabric: b2aa9a7a49a054621f38e59f3aef6d6e5daf3cce. Registered ext4 image is bound through `/dev/loop1`; original loop27 records are preserved. All checks run fresh against the isolated corrected candidate. No model calls; original three-attempt supervisor remains exhausted. Engineering acceptance, ECA verification and publication remain pending. See evidence/, candidate-hashes.json, configuration.json, native-artifacts/manifest.json and communication-1167.patch.\n')
    write('export-result.json', {'status': 'portable_artifacts_exported', 'run_id': identifier, 'verification': validation['status'], 'engineering_acceptance': 'pending_offline_review', 'additional_paid_calls': 0, 'missing_native_products': missing})


def main():
    stage = sys.argv[1]
    try:
        guard()
        for name, expected in CONFIG['tools'].items():
            if sha(SCRATCH / 'tools' / name) != expected:
                raise ValueError('Pinned tool changed: ' + name)
        native = SCRATCH / 'native-workspace'
        head = subprocess.check_output(['git', '-C', str(native), 'rev-parse', 'HEAD'], text=True).strip()
        if head != CONFIG['native_baseline']:
            raise ValueError('Native baseline changed')
        identifier = (HERE / 'current-native-run-id').read_text().strip()
        if stage == 'verify':
            verify({'run_id': identifier})
        elif stage == 'export':
            export({'run_id': identifier})
        else:
            raise ValueError('Unsupported deterministic stage')
    except Exception as error:
        write(stage + '-failure.json', {'reason': str(error), 'paid_calls': 0})
        print(json.dumps({'status': 'failed', 'stage': stage, 'reason': str(error)}))
        return 1
    print(json.dumps({'status': 'completed', 'stage': stage, 'run_id': identifier, 'paid_calls': 0}))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
