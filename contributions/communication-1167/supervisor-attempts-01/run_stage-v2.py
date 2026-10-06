"""Host stages of the finite, native Fabro three-attempt supervisor."""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import time

P = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167')
D = P / 'supervisor'
spec = importlib.util.spec_from_file_location('frozen_collectors', D / 'collector.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
AUTH = json.loads((D / 'authority.json').read_text())

def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def run_id():
    return (D / 'native-run-id').read_text().strip()

def bind_subject():
    save(P / 'candidate-hashes.json', base.source_hashes(P / 'candidate'))
    hashes = json.loads((P / 'control-hashes.json').read_text())
    hashes['candidate-hashes.json'] = base.sha(P / 'candidate-hashes.json')
    save(P / 'control-hashes.json', hashes)

def guard():
    base.guard()
    if AUTH['max_fix_attempts'] != 3 or AUTH['maximum_combined_reservation_usd'] > 10:
        raise ValueError('Supervisor limits changed')
    if base.sha(Path(AUTH['docker_client'])) != AUTH['docker_client_sha256']:
        raise ValueError('Docker client changed')
    head = subprocess.check_output(['git', '-C', str(P / 'candidate'), 'rev-parse', 'HEAD'], text=True).strip()
    if head != AUTH['native_baseline']:
        raise ValueError('Native baseline changed')

def await_previous():
    deadline = time.monotonic() + 10800
    old = AUTH['original_current_run']
    while True:
        guard()
        state = base.api('/api/v1/runs/' + old + '/state')
        kind = state.get('status', {}).get('kind')
        if kind in {'succeeded', 'failed', 'cancelled', 'canceled'}:
            save(D / 'previous-terminal-state.json', state)
            (P / 'current-native-run-id').write_text(run_id() + '\n')
            result = json.loads((P / 'verify-result.json').read_text())
            if result.get('status') == 'measured_checks_passed_review_pending':
                save(D / 'result.json', {'status': 'previous_checks_passed_review_pending', 'attempts': 0})
                raise RuntimeError('Previous checks passed; no correction needed')
            print(json.dumps({'previous_run': old, 'terminal_kind': kind, 'next': 'bounded_correction'}))
            return
        if time.monotonic() > deadline:
            raise TimeoutError('Previous run exceeded bounded supervision wait; current run unchanged')
        time.sleep(5)

def prepare(attempt):
    guard()
    if not 1 <= attempt <= 3:
        raise ValueError('Three-attempt limit exceeded')
    a = D / ('attempt-' + str(attempt)); a.mkdir(exist_ok=False)
    for name in ['verify-result.json', 'candidate-hashes.json', 'communication-1167.patch', 'tools.json', 'current-native-run-id']:
        if (P / name).exists(): shutil.copyfile(P / name, a / ('before-' + name))
    shutil.copytree(P / 'evidence', a / 'before-evidence')
    shutil.copytree(P / 'candidate/score/mw/com/test/api_idempotency', a / 'before-api-idempotency')
    shutil.copyfile(P / 'candidate/BUILD', a / 'before-BUILD')
    changes = []
    if attempt == 1:
        root = P / 'candidate/BUILD'; text = root.read_text()
        old = '        "//:BUILD",\n        "//:MODULE.bazel",'
        new = '        "BUILD",\n        "MODULE.bazel",'
        if old not in text:
            raise ValueError('Copyright target differs from measured baseline')
        root.write_text(text.replace(old, new, 1))
        changes.append('Correct copyright_checker source arguments to native filesystem paths')
        changes.append('Expose pinned Docker client in Ubuntu 24.04 build image for the native integration image loader')
        bind_subject()
    save(a / 'preparation.json', {'attempt': attempt, 'known_corrections': changes, 'candidate_hash': base.sha(P / 'candidate-hashes.json')})
    packet = {'attempt': attempt, 'max_fix_attempts': 3, 'known_corrections': changes,
              'instruction': 'Return complete replacement contents only for files that need correction. Empty files means no source correction. Preserve the BUILD path correction. Never claim acceptance or test success.',
              'allowed_source_paths': AUTH['allowed_source_paths'], 'verification': {}, 'files': {}}
    result = json.loads((P / 'verify-result.json').read_text())
    packet['verification']['status'] = result.get('status')
    packet['verification']['checks'] = [{k: item.get(k) for k in ['check', 'exit_code', 'status', 'stop_reason'] if k in item} for item in result.get('checks', [])]
    for name in ['copyright', 'format', 'focused', 'build-all', 'test-all']:
        for ext in ['stdout', 'stderr']:
            f = P / 'evidence' / (name + '.' + ext)
            if not f.exists(): continue
            text = f.read_text(errors='replace')
            errors = [line for line in text.splitlines() if any(t in line for t in ['error:', 'ERROR:', 'E   ', 'Bootstrap stderr:', 'FAILED', 'Segmentation fault'])]
            packet['verification'][f.name] = ('\n'.join(errors[:18]) + '\n' + text[-1800:])[:5500]
    for rel in AUTH['allowed_source_paths']:
        packet['files'][rel] = (P / 'candidate' / rel).read_text()
    native = (P / 'implementation-prompt.txt').read_text().split('Pinned native source context:', 1)[1]
    packet['pinned_native_context'] = native
    body = json.dumps(packet, ensure_ascii=False)
    if len(body.encode()) > 400000:
        raise ValueError('Correction packet exceeds bound')
    (a / 'correction-packet.json').write_text(body + '\n')
    save(D / 'status.json', {'run_id': run_id(), 'status': 'correction_prepared', 'attempt': attempt, 'max_fix_attempts': 3})
    print(body)

def apply(attempt):
    guard(); a = D / ('attempt-' + str(attempt))
    ids = json.loads((D / 'node-ids.json').read_text()); node = ids['draft' + str(attempt)]
    state = base.api('/api/v1/runs/' + run_id() + '/state')
    stages = state.get('stages', {})
    stage = next(v for k, v in stages.items() if k.startswith(node + '@'))
    text = stage.get('response')
    if not isinstance(text, str): raise ValueError('Native correction response absent')
    (a / 'native-response.txt').write_text(text)
    raw = text.strip()
    if raw.startswith('```'): raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    try:
        result = json.loads(raw)
    except ValueError:
        # Recover only a fully closed files array; never invent missing source content.
        if not raw.startswith('{') or '"files"' not in raw: raise
        start = raw.index('"files"') + len('"files"')
        if not raw[start:].lstrip().startswith(':'): raise
        start = raw.index(':', start) + 1
        files, end = json.JSONDecoder().raw_decode(raw[start:].lstrip())
        if not isinstance(files, list): raise
        result = {'files': files, 'rationale_status': 'truncated_unavailable'}
        save(a / 'response-recovery.json', {'status': 'complete_files_array_only', 'unknown_suffix': True})
    files = result.get('files')
    if not isinstance(files, list) or len(files) > len(AUTH['allowed_source_paths']):
        raise ValueError('Correction output shape exceeds allowed scope')
    planned = {}
    for item in files:
        rel = item.get('path'); content = item.get('content')
        if rel not in AUTH['allowed_source_paths'] or rel in planned or not isinstance(content, str) or len(content.encode()) > 150000:
            raise ValueError('Correction path/content violates task scope')
        if rel == 'BUILD' and content != (P / 'candidate/BUILD').read_text():
            raise ValueError('Model may not alter the deterministic copyright-only BUILD correction')
        path = PurePosixPath(rel)
        if path.is_absolute() or '..' in path.parts: raise ValueError('Unsafe correction path')
        planned[rel] = content
    if sum(len(v.encode()) for v in planned.values()) > 400000: raise ValueError('Correction output exceeds aggregate bound')
    changed = [rel for rel, content in planned.items() if (P / 'candidate' / rel).read_text() != content]
    prep = json.loads((a / 'preparation.json').read_text())
    if not changed and not prep['known_corrections']:
        save(D / 'result.json', {'status': 'stopped_no_progress', 'attempts': attempt, 'verification': 'failed_or_missing_checks', 'acceptance': 'pending_offline_review'})
        raise RuntimeError('No source or environment correction; unchanged checks will not be replayed')
    for rel, content in planned.items(): (P / 'candidate' / rel).write_text(content)
    bind_subject(); save(a / 'applied-result.json', {'changed_paths': changed, 'rationale': result.get('rationale'), 'candidate_hash': base.sha(P / 'candidate-hashes.json')})
    paths = set(json.loads((P / 'apply-result.json').read_text()).get('paths', [])); paths.update(planned); paths.add('BUILD')
    base.write('apply-result.json', {'status': 'draft_corrected', 'paths': sorted(paths), 'origin': 'native_fabro_supervisor', 'attempt': attempt})
    print(json.dumps({'changed_paths': changed, 'known_corrections': prep['known_corrections'], 'attempt': attempt}))

def verify(attempt):
    guard(); a = D / ('attempt-' + str(attempt))
    context = {'run_id': run_id() + '-retry' + str(attempt)}
    try:
        base.verify(context)
    finally:
        if (P / 'verify-result.json').exists(): shutil.copyfile(P / 'verify-result.json', a / 'verify-result.json')
        shutil.copytree(P / 'evidence', a / 'evidence', dirs_exist_ok=True)
        result = json.loads((P / 'verify-result.json').read_text())
        save(D / 'status.json', {'run_id': run_id(), 'status': result.get('status'), 'attempt': attempt, 'max_fix_attempts': 3})
    print(json.dumps({'attempt': attempt, 'verification': result['status'], 'checks': [{k: c.get(k) for k in ['check', 'exit_code', 'status'] if k in c} for c in result['checks']]}))

def export():
    guard()
    base.export({'run_id': run_id()})
    old = json.loads((D / 'result.json').read_text()) if (D / 'result.json').exists() else {}
    status = json.loads((D / 'status.json').read_text()) if (D / 'status.json').exists() else {}
    result = json.loads((P / 'verify-result.json').read_text())
    save(D / 'result.json', {**old, 'run_id': run_id(), 'attempts': status.get('attempt', 0), 'max_fix_attempts': 3,
                           'verification': result.get('status'), 'acceptance': 'pending_offline_review',
                           'publication': 'not_authorized', 'billed_cost': 'not_confirmed', 'maximum_reserved_usd': AUTH['maximum_combined_reservation_usd']})
    print(json.dumps(json.loads((D / 'result.json').read_text())))

if __name__ == '__main__':
    label = sys.argv[1]
    try:
        if label == 'await_previous': await_previous()
        elif label == 'export': export()
        else:
            attempt = int(label[-1]); operation = label[:-1]
            if not 1 <= attempt <= 3: raise ValueError('Three-attempt limit exceeded')
            {'prepare': prepare, 'apply': apply, 'verify': verify}[operation](attempt)
    except Exception as exc:
        save(D / (label + '-failure.json'), {'run_id': run_id(), 'stage': label, 'reason': str(exc), 'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})
        print(json.dumps({'stage': label, 'failure': str(exc)}))
        raise SystemExit(1)
