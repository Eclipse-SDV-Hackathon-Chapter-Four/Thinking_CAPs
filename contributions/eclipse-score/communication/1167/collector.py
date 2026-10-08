"""Frozen host collectors for one Fabro run; no approvals or model calls."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request

from score_sw_fabric.storage import build_environment, validate_run_root

HERE = Path(__file__).resolve().parent
SCRATCH = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha')
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

def guard():
    validate_run_root(SCRATCH)
    source = subprocess.check_output(['findmnt', '-n', '-o', 'SOURCE', '-T', str(SCRATCH)], text=True).strip()
    if source != '/dev/loop27':
        raise ValueError('Bound loop27 is disconnected or substituted')
    if (HERE / 'control-hashes.json').exists():
        for path, expected in json.loads((HERE / 'control-hashes.json').read_text()).items():
            if sha(HERE / path) != expected:
                raise ValueError('Frozen control changed: ' + path)

def source_hashes(tree):
    return {str(p.relative_to(tree)): sha(p) for p in tree.rglob('*')
            if p.is_file() and not p.is_symlink() and '.git' not in p.relative_to(tree).parts}

def admit(context):
    authority = json.loads((HERE / 'authority.json').read_text())
    budget = json.loads((HERE / 'budget.json').read_text())
    if authority['max_total_cost_usd'] != 10 or budget['reserved_upper_cost_usd'] > 10:
        raise ValueError('Spending envelope differs from user authority')
    native_sha = subprocess.check_output(['git', '-C', str(HERE / 'candidate'), 'rev-parse', 'HEAD'], text=True).strip()
    if native_sha != authority['target_commit']:
        raise ValueError('Native baseline differs')
    for unit in json.loads((HERE / 'context-manifest.json').read_text())['files']:
        if sha(HERE / 'candidate' / unit['path']) != unit['sha256']:
            raise ValueError('Draft context is stale')
    write('admit-result.json', {'status': 'admitted_for_draft_execution', 'run_id': context['run_id'],
          'storage': '/dev/loop27', 'cost_upper_bound_usd': budget['reserved_upper_cost_usd'],
          'engineering_acceptance': 'pending_offline_review'})

def response_values(value, key):
    found = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key:
                found.append(v)
            found.extend(response_values(v, key))
    elif isinstance(value, list):
        for v in value:
            found.extend(response_values(v, key))
    return found

def apply(context):
    identifier = (HERE / 'draft-source-run-id').read_text().strip()
    state = api('/api/v1/runs/' + identifier + '/state')
    write('draft-state.json', state)
    node = json.loads((HERE / 'node-ids.json').read_text())['draft']
    values = response_values(state, 'response.' + node)
    if not values:
        values = [stage['response'] for key, stage in state.get('stages', {}).items()
                  if key.startswith(node + '@') and stage.get('response') is not None]
    if not values:
        raise ValueError('Native draft output unavailable in bound run state')
    raw = values[-1]
    if isinstance(raw, str) and re.fullmatch(r'blob://sha256/[a-f0-9]{64}', raw):
        digest = raw.rsplit('/', 1)[-1]
        payload = api('/api/v1/runs/' + identifier + '/blobs/' + digest, raw=True)
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError('Native draft blob digest differs')
        raw = json.loads(payload)
    if not isinstance(raw, str):
        raise ValueError('Native draft output has an unsupported representation')
    (HERE / 'draft-output.txt').write_text(raw)
    text = raw.strip()
    if text.startswith('```json') and text.endswith('```'):
        text = text[7:-3].strip()
    try:
        draft = json.loads(text)
    except json.JSONDecodeError:
        # Preserve the original response. Recover only completely decoded source
        # files and rationale when the sole incomplete suffix is assumptions.
        decoder = json.JSONDecoder()
        prefix = re.match(r'^\{\s*"files"\s*:\s*', text)
        if prefix is None:
            raise ValueError('Truncated source payload cannot be recovered')
        files, end = decoder.raw_decode(text, prefix.end())
        tail = text[end:]
        match = re.match(r'\s*,\s*"rationale"\s*:\s*', tail)
        if match is None:
            raise ValueError('Draft rationale is unavailable')
        rationale, end = decoder.raw_decode(tail, match.end())
        tail = tail[end:]
        match = re.match(r'\s*,\s*"assumptions"\s*:\s*\[\s*', tail)
        if match is None:
            raise ValueError('Draft suffix is not the supported metadata truncation')
        tail = tail[match.end():]
        assumptions = []
        while tail.strip():
            value, end = decoder.raw_decode(tail.lstrip())
            if not isinstance(value, str):
                raise ValueError('Unsupported assumption representation')
            assumptions.append(value)
            tail = tail.lstrip()[end:].lstrip()
            if not tail.startswith(','):
                raise ValueError('Unsupported metadata truncation boundary')
            tail = tail[1:].lstrip()
        draft = {'files': files, 'rationale': rationale, 'assumptions': assumptions}
        write('draft-recovery.json', {'status': 'complete_source_values_recovered',
              'original_response_sha256': sha(HERE / 'draft-output.txt'),
              'source_file_count': len(files), 'metadata_status': 'assumptions_suffix_missing',
              'missing_assumptions': 'unknown', 'engineering_acceptance': 'pending',
              'new_paid_calls': 0})
    if set(draft) != {'files', 'rationale', 'assumptions'} or not isinstance(draft['files'], list):
        raise ValueError('Draft output contract differs')
    if not 1 <= len(draft['files']) <= 30:
        raise ValueError('Draft file count exceeds scope')
    planned = {}
    candidate = HERE / 'candidate'
    for unit in draft['files']:
        if not isinstance(unit, dict) or set(unit) != {'path', 'content'}:
            raise ValueError('Malformed draft file')
        path = PurePosixPath(unit['path'])
        if path.is_absolute() or '..' in path.parts or '\\' in unit['path'] or not str(path).startswith('score/mw/com/test/api_idempotency/'):
            raise ValueError('Draft write escapes authorized test directory')
        if path.name != 'BUILD' and path.suffix not in {'.cpp', '.h', '.json', '.py', '.md'}:
            raise ValueError('Unsupported draft file type')
        if str(path) in planned or (candidate / str(path)).exists():
            raise ValueError('Draft cannot overwrite existing paths')
        if not isinstance(unit['content'], str) or len(unit['content'].encode()) > 150000:
            raise ValueError('Draft content exceeds scope')
        planned[str(path)] = unit['content']
    if not any(p.endswith('.cpp') for p in planned) or not any(p.endswith('.py') for p in planned):
        raise ValueError('Missing native application or integration harness')
    for path, content in planned.items():
        dest = candidate / path
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(content)
    write('draft-result.json', draft)
    write('candidate-hashes.json', source_hashes(candidate))
    write('apply-result.json', {'status': 'draft_applied', 'paths': sorted(planned), 'origin': 'native_fabro_deepseek_prompt'})

def measure(command, label, cwd, env, timeout):
    record = {'command': command, 'cwd': str(cwd), 'started_at_epoch': time.time(),
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
    native = SCRATCH / ('native-workspace-' + context['run_id'])
    shutil.copytree(candidate, native, symlinks=True)
    subprocess.run(['git', '-C', str(native), '-c', 'core.hooksPath=/dev/null', 'rev-parse', '--is-inside-work-tree'], check=True, capture_output=True)
    storage_env = build_environment(SCRATCH)
    env = {**os.environ, **storage_env, 'PYTHONDONTWRITEBYTECODE': '1'}
    image = json.loads((HERE / 'build-environment.json').read_text())['image_id']
    if subprocess.check_output(['/usr/bin/docker', 'image', 'inspect', image, '--format', '{{.Id}}'], text=True).strip() != image:
        raise ValueError('Registered native build image changed')
    # Exact independently measured Bazel 8.7.0, matching the native .bazelversion.
    # New scratch and caches stay bound to this run's SSD; no existing queue is moved.
    tool = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha/tools/bazel-8.7.0')
    if not tool.is_file():
        write('verify-result.json', {'status': 'blocked', 'reason': 'Registered Bazelisk unavailable'})
        return
    write('tools.json', {'bazel_path': str(tool), 'sha256': sha(tool), 'build_image_id': image,
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
                  '--mount', 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock',
                  '--workdir', str(native), '--env', 'HOME=' + str(SCRATCH / 'container-home'),
                  '--env', 'PYTHONDONTWRITEBYTECODE=1']
        for key, value in storage_env.items():
            docker.extend(['--env', key + '=' + value])
        docker.extend(['--entrypoint', str(tool), image, *base[1:], *args])
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
    for suffix in ['', '/state', '/stages?limit=200']:
        name = 'summary' if not suffix else 'state' if suffix == '/state' else 'stages'
        try:
            write('native-' + name + '.json', api('/api/v1/runs/' + identifier + suffix))
        except Exception as exc:
            write('native-' + name + '-failure.json', {'error': str(exc)})
    source = HERE / 'candidate'
    files = json.loads((HERE / 'apply-result.json').read_text()).get('paths', []) if (HERE / 'apply-result.json').exists() else []
    # Include untracked contribution files in a portable Git patch without a commit.
    if files:
        subprocess.run(['git', '-C', str(source), '-c', 'core.hooksPath=/dev/null', 'add', '-N', '--', *files], check=True)
        patch = subprocess.check_output(['git', '-C', str(source), 'diff', '--binary', '--', 'score/mw/com/test/api_idempotency'])
        (HERE / 'communication-1167.patch').write_bytes(patch)
    validation = json.loads((HERE / 'verify-result.json').read_text()) if (HERE / 'verify-result.json').exists() else {'status': 'not_run'}
    report = '# Communication #1167 contribution run\n\n'
    report += 'Native Fabro run: `' + identifier + '`.\n\n'
    report += 'Verification: **' + validation['status'] + '**. Engineering acceptance and ECA verification remain pending.\n\n'
    report += 'The pre-optimization fabric is frozen at b2aa9a7. Native builds use the registered ext4 image on loop27. '
    report += 'The authorized model is the configured DeepSeek Flash, maximum $10; the workflow contains one tool-free prompt stage. '
    report += 'No human decision, upstream submission or issue closure is recorded.\n\n'
    report += 'See authority.json, budget.json, workflow/, upstream/, draft-result.json, candidate/, evidence/ and the patch for the complete local record.\n'
    (HERE / 'README.md').write_text(report)
    write('export-result.json', {'status': 'portable_artifacts_exported', 'run_id': identifier,
          'verification': validation['status'], 'engineering_acceptance': 'pending_offline_review'})
    hashes = {str(p.relative_to(HERE)): sha(p) for p in HERE.rglob('*') if p.is_file()
              and not p.is_symlink() and '.git' not in p.relative_to(HERE).parts and p.name != 'artifact-manifest.json'}
    write('artifact-manifest.json', {'schema_version': 1, 'run_id': identifier, 'files': hashes})

def main():
    label = sys.argv[1]
    context = json.load(sys.stdin)
    context['native_hook_run_id'] = context.get('run_id')
    binding = HERE / 'current-native-run-id'
    context['run_id'] = binding.read_text().strip() if binding.exists() else (HERE / 'native-run-id').read_text().strip()
    try:
        guard()
        if context.get('event') != 'stage_start':
            raise ValueError('Unsupported hook event')
        expected = json.loads((HERE / 'node-ids.json').read_text())[label]
        if context.get('node_id') != expected:
            raise ValueError('Collector node binding differs')
        globals()[label](context)
        print(json.dumps({'decision': 'proceed'}))
        return 0
    except Exception as exc:
        write(label + '-failure.json', {'status': 'blocked', 'reason': str(exc), 'run_id': context.get('run_id')})
        print(json.dumps({'decision': 'block', 'reason': str(exc)}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
