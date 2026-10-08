"""Bounded host collector. Fabro alone schedules this sequential bug queue."""
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

P = Path(__file__).resolve().parent
C = json.loads((P / 'configuration.json').read_text())
R = Path(C['scratch_root'])
SERVER = 'http://127.0.0.1:43916'
AUTH = Path('/home/jefferson/.local/state/s-core/fabro/someip84-server/cli-auth.json')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    temporary = p.with_name(p.name + '.tmp')
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    temporary.replace(p)

def api(route, raw=False):
    token = json.loads(AUTH.read_text())['servers'][SERVER]['token']
    req = urllib.request.Request(SERVER + route, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read(20_000_001)
    if len(body) > 20_000_000:
        raise ValueError('Native response exceeds bound')
    return body if raw else json.loads(body)

def hashes(tree):
    return {str(p.relative_to(tree)): sha(p) for p in tree.rglob('*')
            if p.is_file() and not p.is_symlink() and '.git' not in p.relative_to(tree).parts
            and not any(part.startswith('bazel-') for part in p.relative_to(tree).parts)
            and '.ruff_cache' not in p.relative_to(tree).parts}

def guard():
    validate_run_root(R)
    mount = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(R), '-o', 'SOURCE,UUID'], text=True))['filesystems'][0]
    if mount['source'] != '/dev/loop1' or mount['uuid'] != C['volume_uuid']:
        raise ValueError('Storage identity changed; stop without relocating')
    for name, expected in json.loads((P / 'frozen-inputs.json').read_text()).items():
        if sha(P / name) != expected:
            raise ValueError('Frozen input changed: ' + name)
    for name, expected in C['tools'].items():
        if sha(R / 'tools' / name) != expected:
            raise ValueError('Pinned native tool changed: ' + name)

def state_update(number, status, **fields):
    path = P / 'state.json'
    state = json.loads(path.read_text())
    for item in state['items']:
        if item['issue_number'] == number:
            item.update(status=status, **fields)
    state.update(active_run_id=(P / 'native-run-id').read_text().strip(), updated_at_epoch=time.time())
    state['status'] = 'running'
    write(path, state)

def measure(d, tree, label, args, timeout=1200):
    guard()
    storage = build_environment(R)
    storage.pop('TEST_TMPDIR', None)
    env = {**os.environ, **storage, 'PYTHONDONTWRITEBYTECODE': '1'}
    image = C['image_id']
    if subprocess.check_output(['/usr/bin/docker', 'image', 'inspect', image, '--format', '{{.Id}}'], text=True).strip() != image:
        raise ValueError('Pinned build image missing or changed')
    name = 'score-bug-' + d.name + '-' + label
    command = ['/usr/bin/docker', 'run', '--rm', '--name', name, '--read-only', '--network', 'host',
               '--user', '1000:1000', '--group-add', '999', '--cap-add', 'SYS_ADMIN',
               '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
               '--mount', f'type=bind,source={R},target={R}',
               '--mount', f'type=bind,source={R / "container-tmp"},target=/tmp',
               '--mount', f'type=bind,source={R / "container-var-tmp"},target=/var/tmp',
               '--mount', f'type=bind,source={R / "tools/docker-client"},target=/usr/bin/docker,readonly',
               '--mount', 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock',
               '--workdir', str(tree), '--env', 'HOME=' + str(R / 'container-home'),
               '--env', 'PATH=' + str(R / 'tools') + ':/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
               '--env', 'PYTHONDONTWRITEBYTECODE=1']
    for key, value in storage.items():
        command += ['--env', key + '=' + value]
    bazel_args = list(args)
    if args[0] == 'test':
        bazel_args += ['--test_env=' + k + '=' + v for k, v in sorted({**storage, 'HOME': str(R / 'container-home')}.items())]
    # Bazel options must precede the native binary's -- argument separator.
    insert = bazel_args.index('--') if '--' in bazel_args else len(bazel_args)
    if args[0] in {'run', 'build', 'test'}:
        bazel_args[insert:insert] = ['--jobs=8']
    command += ['--entrypoint', str(R / 'tools/bazel-8.7.0'), image,
                '--output_user_root=' + str(R / 'bazel-output'), '--batch', *bazel_args]
    evidence = d / 'evidence'
    evidence.mkdir(exist_ok=True)
    out, err = evidence / (label + '.stdout'), evidence / (label + '.stderr')
    record = {'command': command, 'cwd': str(tree), 'subject_hashes': hashes(tree),
              'started_at_epoch': time.time(), 'timeout_seconds': timeout, 'carried_evidence': False}
    with out.open('wb') as stdout, err.open('wb') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        try:
            while process.poll() is None:
                guard()
                if time.time() - record['started_at_epoch'] > timeout:
                    raise TimeoutError('Native command exceeded time bound')
                time.sleep(1)
            record['exit_code'] = process.returncode
        except BaseException as error:
            subprocess.run(['/usr/bin/docker', 'rm', '--force', name], capture_output=True, timeout=15)
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            record.update(exit_code=process.returncode, stop_reason=str(error))
    record.update(finished_at_epoch=time.time(), stdout_sha256=sha(out), stderr_sha256=sha(err))
    write(evidence / (label + '.json'), record)
    guard()
    return {'check': label, 'exit_code': record['exit_code'], 'record': str((evidence / (label + '.json')).relative_to(P))}

def admit(number, d, item):
    if hashes(R / 'baseline') != json.loads((P / 'baseline-hashes.json').read_text()):
        raise ValueError('Native baseline changed')
    tree = R / ('issue-' + str(number))
    if hashes(tree) != json.loads((P / 'baseline-hashes.json').read_text()):
        raise ValueError('Issue workspace is not a fresh pinned baseline')
    ledger = json.loads((P / 'budget-ledger.json').read_text())
    if str(number) in ledger['reservations']:
        raise ValueError('Duplicate draft admission refused; reservation is never reset')
    reserve = 2_359_296
    if sum(ledger['reservations'].values()) + reserve > 10_000_000:
        raise ValueError('Queue-wide $10 envelope exhausted')
    ledger['reservations'][str(number)] = reserve
    write(P / 'budget-ledger.json', ledger)
    state_update(number, 'running', stage='admit', reserved_upper_cost_usd_micros=reserve)
    write(d / 'admit-result.json', {'status': 'admitted', 'source_commit': C['native_commit'],
          'reserved_upper_cost_usd_micros': reserve, 'actual_cost_usd_micros': None,
          'engineering_acceptance': 'pending_offline_review'})

def apply(number, d, item):
    identifier = (P / 'native-run-id').read_text().strip()
    state = api('/api/v1/runs/' + identifier + '/state')
    write(d / 'draft-native-state.json', state)
    node = json.loads((P / 'node-ids.json').read_text())[f'{number}_draft']
    values = [v['response'] for k, v in state.get('stages', {}).items()
              if k.startswith(node + '@') and v.get('response') is not None]
    if len(values) != 1:
        raise ValueError('Expected exactly one bound draft response')
    raw = values[0]
    if isinstance(raw, str) and re.fullmatch(r'blob://sha256/[a-f0-9]{64}', raw):
        digest = raw.rsplit('/', 1)[-1]
        payload = api('/api/v1/runs/' + identifier + '/blobs/' + digest, raw=True)
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError('Response blob hash differs')
        raw = json.loads(payload)
    if not isinstance(raw, str):
        raise ValueError('Unsupported native response representation')
    (d / 'draft-output.txt').write_text(raw)
    text = raw.strip()
    if text.startswith('```json') and text.endswith('```'):
        text = text[7:-3].strip()
    draft = json.loads(text)
    if set(draft) != {'files', 'rationale'} or not isinstance(draft['rationale'], str):
        raise ValueError('Draft response contract differs')
    files = draft['files']
    if not isinstance(files, list) or not 1 <= len(files) <= 16:
        raise ValueError('No supported scoped patch or file count exceeds bound')
    tree = R / ('issue-' + str(number))
    planned = {}
    for unit in files:
        if not isinstance(unit, dict) or set(unit) != {'path', 'content'}:
            raise ValueError('Invalid file entry')
        path = PurePosixPath(unit['path'])
        if path.is_absolute() or '..' in path.parts or '\\' in str(path) or '.git' in path.parts:
            raise ValueError('Draft path escapes scope')
        if str(path) not in item['allowed_files'] and not any(str(path).startswith(prefix) for prefix in item['allowed_prefixes']):
            raise ValueError('Draft path not authorized: ' + str(path))
        content = unit['content']
        if not isinstance(content, str) or len(content.encode()) > 150_000 or str(path) in planned:
            raise ValueError('Invalid or duplicate source payload')
        target = tree / path
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if parent != tree.parent):
            raise ValueError('Symlink source write refused')
        planned[str(path)] = content
    for path, content in planned.items():
        target = tree / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    write(d / 'draft.json', draft)
    write(d / 'candidate-hashes.json', hashes(tree))
    state_update(number, 'running', stage='apply', changed_files=sorted(planned))

def sarif_summary(output):
    files = sorted(output.rglob('*.sarif')) if output.exists() else []
    result = {'reports': [], 'invalid_file_root_locations': 0, 'named_source_present': False}
    needle = 'score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp'
    def visit(value):
        if isinstance(value, dict):
            if value.get('uri') in {'file:/', 'file:///', ''}:
                result['invalid_file_root_locations'] += 1
            if isinstance(value.get('uri'), str) and needle in value['uri']:
                result['named_source_present'] = True
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    for path in files:
        visit(json.loads(path.read_text()))
        result['reports'].append({'path': str(path), 'sha256': sha(path)})
    return result

def verify(number, d, item):
    tree = R / ('issue-' + str(number))
    expected = json.loads((d / 'candidate-hashes.json').read_text())
    if hashes(tree) != expected:
        raise ValueError('Candidate changed after apply')
    state_update(number, 'running', stage='verify')
    records = []
    # Query discovers actual added targets; it is not treated as execution evidence.
    records.append(measure(d, tree, 'target-discovery', ['query', item['query'], '--output=label_kind'], 600))
    for phase, subject in [('baseline', R / 'baseline'), ('candidate', tree)]:
        for label, args in item['native_checks']:
            records.append(measure(d, subject, phase + '-' + label, args))
        if number in {751, 1104}:
            output = R / 'codeql-output' / str(number) / phase
            output.mkdir(parents=True, exist_ok=True)
            args = ['run', '//quality/static_analysis:codeql_lint', '--', '--output-dir', str(output),
                    '--output-prefix', 'communication-' + str(number), '--target', '//score/mw/com/impl/...']
            records.append(measure(d, subject, phase + '-codeql-native', args, 1800))
            write(d / (phase + '-sarif-summary.json'), sarif_summary(output))
            shutil.copytree(output, d / 'evidence' / (phase + '-codeql'), dirs_exist_ok=True)
    # The contribution guideline requires full build and tests. Preserve failures.
    for label, args in [('copyright', ['run', '//:copyright.check']), ('format', ['run', '//:format.check']),
                        ('build-all', ['build', '//...']), ('test-all', ['test', '//...', '--nocache_test_results'])]:
        records.append(measure(d, tree, 'candidate-' + label, args))
        if label == 'build-all' and records[-1]['exit_code'] != 0:
            error = (d / 'evidence/candidate-build-all.stderr').read_text(errors='replace')
            if any(x in error for x in ['Error downloading', 'Failed to fetch', 'no such package', 'Unable to find package']):
                records.append({'check': 'candidate-test-all', 'status': 'not_run_dependency_failure'})
                break
    pending = ['Offline engineering review and authenticated commit identity remain pending.']
    candidate_records = [r for r in records if r['check'].startswith('candidate-') or r['check'] == 'target-discovery']
    passed = all(r.get('exit_code') == 0 for r in candidate_records)
    if number == 1104:
        s = json.loads((d / 'candidate-sarif-summary.json').read_text())
        if not s['reports'] or s['invalid_file_root_locations']:
            passed = False
            pending.append('Real SARIF locations remain invalid or missing; fixture success cannot close #1104.')
    if number == 751:
        passed = False
        pending.append('Compiler database source-coverage audit requires offline review; SARIF findings alone do not prove every production file was analyzed.')
    if number == 1031:
        passed = False
        pending.append('External Config Management consumption and FMEA/LOBSTER non-duplication require native cross-repository review.')
    write(d / 'verify-result.json', {'status': 'measured_checks_passed_review_pending' if passed else 'failed_or_missing_checks',
          'checks': records, 'pending': pending, 'engineering_acceptance': 'pending_offline_review',
          'candidate_subject_match': hashes(tree) == expected, 'carried_evidence': False})
    logs = tree / 'bazel-testlogs'
    if logs.exists():
        for p in logs.rglob('*'):
            if p.is_file() and p.name in {'test.log', 'test.xml'}:
                dest = d / 'evidence/native-testlogs' / p.relative_to(logs)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, dest)
    if not passed:
        raise RuntimeError('Failed or missing native evidence retained for review')

def export(number, d, item):
    tree = R / ('issue-' + str(number))
    identifier = (P / 'native-run-id').read_text().strip()
    for suffix, label in [('', 'summary'), ('/state', 'state'), ('/stages?page%5Blimit%5D=100', 'stages')]:
        try:
            write(d / ('native-' + label + '.json'), api('/api/v1/runs/' + identifier + suffix))
        except Exception as error:
            write(d / ('native-' + label + '-failure.json'), {'reason': str(error)})
    guard()
    planned = json.loads((d / 'draft.json').read_text())['files'] if (d / 'draft.json').exists() else []
    if (d / 'candidate-hashes.json').exists() and hashes(tree) != json.loads((d / 'candidate-hashes.json').read_text()):
        raise ValueError('Candidate changed during measurement; export cannot bind it')
    if planned:
        subprocess.run(['git', '-C', str(tree), '-c', 'core.hooksPath=/dev/null', 'add', '--intent-to-add', '--',
                        *[f['path'] for f in planned]], check=True, capture_output=True)
        (d / ('communication-' + str(number) + '.patch')).write_bytes(subprocess.check_output([
            'git', '-C', str(tree), 'diff', '--binary', '--', *[f['path'] for f in planned]]))
        for unit in planned:
            dest = d / 'changed-source' / unit['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tree / unit['path'], dest)
    verification = json.loads((d / 'verify-result.json').read_text()) if (d / 'verify-result.json').exists() else {'status': 'not_run'}
    status = 'draft_checks_passed_review_pending' if verification['status'] == 'measured_checks_passed_review_pending' else 'needs_review_or_fix'
    write(d / 'export-result.json', {'status': status, 'issue': item['url'], 'run_id': identifier,
          'verification': verification, 'engineering_acceptance': 'pending_offline_review',
          'actual_provider_cost_usd': None, 'budget_accounting': 'full conservative reservation retained'})
    state_update(number, status, stage='export', run_id=identifier)
    if number == C['order'][-1]:
        state = json.loads((P / 'state.json').read_text())
        state.update(status='finished_review_pending', active_run_id=identifier,
                     notes='Queue execution ended. Review each native result; no issue closure or human acceptance implied. Provider billing unknown; $9.437184 conservatively reserved.')
        write(P / 'state.json', state)
    write(d / 'artifact-manifest.json', {'files': {str(p.relative_to(d)): sha(p) for p in d.rglob('*')
          if p.is_file() and p.name != 'artifact-manifest.json'}})

def main():
    def interrupted(signum, frame):
        raise RuntimeError('Collector interrupted by signal ' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    number, stage = int(sys.argv[1]), sys.argv[2]
    item = next(x for x in json.loads((P / 'queue-record.json').read_text())['items'] if x['issue_number'] == number)
    d = P / 'items' / str(number)
    d.mkdir(parents=True, exist_ok=True)
    try:
        guard()
        globals()[stage](number, d, item)
        print(json.dumps({'issue': number, 'stage': stage, 'status': 'completed', 'engineering_acceptance': 'pending_offline_review'}))
        return 0
    except Exception as error:
        write(d / (stage + '-failure.json'), {'reason': str(error), 'time_epoch': time.time()})
        state_update(number, 'failed', stage=stage, reason=str(error))
        if stage in {'admit', 'export'}:
            state = json.loads((P / 'state.json').read_text())
            state.update(status='blocked', last_error=str(error))
            write(P / 'state.json', state)
        print(json.dumps({'issue': number, 'stage': stage, 'status': 'failed', 'reason': str(error)}))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
