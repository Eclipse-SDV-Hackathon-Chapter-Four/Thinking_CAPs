"""Observe native Fabro events and retain terminal evidence; never dispatch/fix runs."""
from __future__ import annotations

import hashlib
import json
import os
import queue
import shlex
import shutil
import subprocess
import threading
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).parent
DEST = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue') / (ROOT.name + '-results')
validate_run_root(ROOT)
BINDING = json.loads((ROOT / 'server-binding.json').read_text())
PRIVATE = Path(BINDING['private_state'])
TOKEN = json.loads((PRIVATE / 'operator-secret.json').read_text())['token']
JOBS = json.loads((ROOT / 'queue.json').read_text())['jobs']
BY_ID = {j['run_id']: j for j in JOBS}
SECRETS = [TOKEN.encode()]
for line in (Path.home() / '.config/sesn/deepseek.env').read_text().splitlines():
    parts = shlex.split(line, comments=True)
    for part in parts:
        if part.startswith('DEEPSEEK_API_KEY='):
            SECRETS.append(part.partition('=')[2].encode())
pid = BINDING.get('pid')
if pid and Path(f'/proc/{pid}/environ').exists():
    for field in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0'):
        if field.startswith(b'SESSION_SECRET='):
            SECRETS.append(field.partition(b'=')[2])
SECRETS = [s for s in SECRETS if s]


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def safe(data):
    assert all(s not in data for s in SECRETS), 'Private credential found; refusing export'
    return data


def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(safe((json.dumps(obj, indent=2, sort_keys=True) + '\n').encode()))


def api(path):
    validate_run_root(ROOT)
    req = urllib.request.Request(BINDING['url'] + '/api/v1' + path,
                                 headers={'Authorization': 'Bearer ' + TOKEN})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def copy_tree(source, dest):
    validate_run_root(ROOT)
    for p in source.rglob('*'):
        assert not p.is_symlink(), ('Unexpected export symlink', str(p))
        if p.is_file():
            out = dest / p.relative_to(source)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(safe(p.read_bytes()))


def verify_manifest(root):
    m = json.loads((root / 'artifact-manifest.json').read_text())
    for relative, sha in m['files'].items():
        assert digest(root / relative) == sha, ('Export changed', relative)


def collect(job, projection):
    validate_run_root(ROOT)
    issue = str(job['issue'])
    dest = DEST / 'issues' / issue
    if (dest / 'artifact-manifest.json').exists():
        verify_manifest(dest)
        return json.loads((dest / 'collection-summary.json').read_text())
    assert not dest.exists(), ('Incomplete collection requires inspection', issue)
    stage = ROOT / 'collection-staging' / issue
    assert not stage.exists(), ('Incomplete staging requires inspection', issue)
    stage.mkdir(parents=True)
    work = Path(job['workspace'])
    src = ROOT / 'jobs' / issue
    state = api('/runs/' + job['run_id'] + '/state')
    assert state['conclusion'] is not None, 'Run projection terminal before conclusion'
    fixes = sorted(k for k, v in state['stages'].items()
                   if k.startswith('fix') and v.get('started_at'))
    assert len(fixes) <= job['max_source_corrections'], 'Native correction budget exceeded'
    models = projection.get('models', [])
    assert all(m['provider'] == 'deepseek' and m['name'] == 'deepseek-v4-flash'
               for m in models), 'Unexpected native model'
    save(stage / 'native/final-projection.json', projection)
    save(stage / 'native/final-state.json', state)
    events_path = stage / 'native/events.jsonl'
    after = 0
    count = 0
    terminal_record = False
    with events_path.open('wb') as output:
        while True:
            page = api('/runs/' + job['run_id'] + f'/events?limit=1000&after={after}')
            for item in page['data']:
                assert item['stream_seq'] > after
                after = item['stream_seq']
                count += 1
                record = item.get('item', {}).get('record', {})
                terminal_record |= (record.get('kind') == 'run.lifecycle'
                                    and record.get('transition') in ['succeeded', 'failed', 'dead'])
                output.write(safe((json.dumps(item, sort_keys=True) + '\n').encode()))
            if not page['meta']['has_more']:
                break
    save(stage / 'native/events-pagination.json', {'records': count, 'last_stream_seq': after,
                                                  'has_more': False, 'terminal_lifecycle_present': terminal_record})
    if not (src / 'export/artifact-manifest.json').exists():
        completed = subprocess.run(['uv', 'run', '--frozen', 'python', str(ROOT / 'driver_linux.py'),
                                    'export', issue], capture_output=True)
        save(stage / 'native/operator-export.json', {'reason': 'Terminal run had no native export',
                                                     'exit_code': completed.returncode,
                                                     'stdout': completed.stdout.decode(errors='replace'),
                                                     'stderr': completed.stderr.decode(errors='replace')})
        assert completed.returncode == 0, 'Terminal evidence export failed'
    verify_manifest(src / 'export')
    copy_tree(src / 'export', stage / 'export')
    copy_tree(ROOT / 'definitions-linux' / issue, stage / 'workflow')
    copy_tree(work / '.rust-queue/context', stage / 'context')
    for p in (src / 'execution').iterdir():
        if p.is_dir():
            copy_tree(p, stage / 'execution' / p.name)
        elif p.name != 'export-index':
            out = stage / 'execution' / p.name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(safe(p.read_bytes()))
    for name in ['native-workspace-binding.json', 'baseline-hashes.json', 'task.json']:
        save(stage / 'provenance' / name, json.loads((src / name).read_text()))
    # A private alternate index verifies the exported diff without touching native index/HEAD.
    index = ROOT / 'collection-staging' / (issue + '.index')
    env = {**os.environ, 'GIT_INDEX_FILE': str(index)}
    def git(*args):
        return subprocess.check_output(['git', '-C', str(work), *args], env=env)
    git('read-tree', job.get('baseline', json.loads((ROOT / 'queue.json').read_text())['baseline']))
    git('add', '--', 'score/mw/com')
    baseline = json.loads((src / 'task.json').read_text())['baseline']
    patch = git('diff', '--cached', '--binary', baseline, '--', 'score/mw/com')
    patch_equal = patch == (src / f'export/communication-{issue}.patch').read_bytes()
    assert patch_equal, 'Export patch differs from terminal workspace'
    changed = git('diff', '--cached', '--name-only', '-z', baseline, '--', 'score/mw/com').decode().split('\0')
    changed = [p for p in changed if p]
    for relative in changed:
        p = work / relative
        if p.exists():
            assert p.is_file() and not p.is_symlink()
            out = stage / 'changed-source' / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(safe(p.read_bytes()))
    final_hashes = {str(p.relative_to(work)): digest(p) for p in (work / 'score/mw/com').rglob('*')
                    if p.is_file() and not p.is_symlink()}
    save(stage / 'provenance/final-source-hashes.json', final_hashes)
    attempts = []
    for attempt in sorted((src / 'execution').glob('check-*')):
        result_path = attempt / 'result.json'
        if not result_path.exists():
            attempts.append({'attempt': attempt.name, 'measured': False, 'passed': False,
                             'gap': 'No result; inspect native stage failure in final-state/events'})
            continue
        result = json.loads(result_path.read_text())
        subjects = attempt / 'measured-subject-hashes.json'
        commands = result.get('bounded_native_summary', {}).get('checks', [])
        attempts.append({'attempt': attempt.name, 'measured': subjects.exists(),
                         'passed': result['passed'], 'kind': result['kind'],
                         'final_subjects_match': subjects.exists() and json.loads(subjects.read_text()) == final_hashes,
                         'command_exits': [{k: c[k] for k in ['kind', 'targets', 'exit_code', 'timed_out']}
                                           for c in commands]})
    summary = {'issue': job['issue'], 'run_id': job['run_id'], 'mode': job['mode'], 'url': job['url'],
               'native_status': projection['lifecycle']['status']['kind'], 'baseline': baseline,
               'models': models, 'corrections_used': len(fixes), 'max_corrections': job['max_source_corrections'],
               'attempts': attempts, 'patch_bytes': len(patch), 'changed_files': changed,
               'patch_matches_terminal_source': patch_equal, 'events_complete_through': after,
               'terminal_lifecycle_present': terminal_record,
               'supervisor_present': (stage / 'export/reports/supervisor.md').exists(),
               'acceptance': 'pending offline; native success is not issue resolution',
               'docs_limitation': 'kind docs builds selected targets; does not execute rust_doc_test',
               'test_evidence_limitation': 'Use command-specific BEP for fresh executions; copied XML alone may include prior attempts',
               'collected_at': now()}
    save(stage / 'collection-summary.json', summary)
    save(stage / 'artifact-manifest.json', {'schema_version': 1,
          'files': {str(p.relative_to(stage)): digest(p) for p in stage.rglob('*')
                    if p.is_file() and p != stage / 'artifact-manifest.json'}})
    verify_manifest(stage)
    validate_run_root(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(stage, dest)
    verify_manifest(dest)
    print(json.dumps({'collected': job['issue'], 'status': summary['native_status'],
                      'fixes': len(fixes), 'patch_bytes': len(patch),
                      'checks_passed': [a['passed'] for a in attempts]}), flush=True)
    return summary


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    notifications = queue.Queue()
    connected = threading.Event()
    stopped = threading.Event()
    def observe(run_id):
        cursor = None
        while not stopped.is_set():
            try:
                validate_run_root(ROOT)
                suffix = '' if cursor is None else f'?after={cursor}'
                req = urllib.request.Request(BINDING['url'] + '/api/v1/runs/' + run_id + '/attach' + suffix,
                                              headers={'Authorization': 'Bearer ' + TOKEN})
                with urllib.request.urlopen(req, timeout=60) as stream:
                    connected.set()
                    notifications.put(('transition', run_id))
                    for line in stream:
                        if stopped.is_set():
                            return
                        if not line.startswith(b'data: '):
                            continue
                        item = json.loads(line[6:])
                        cursor = item['stream_seq']
                        record = item.get('item', {}).get('record', {})
                        if record.get('kind') == 'run.lifecycle':
                            notifications.put(('transition', run_id))
                # Native per-run attach ends after terminal lifecycle/grace. Reconcile
                # even if attachment started after the terminal record was committed.
                notifications.put(('transition', run_id))
                return
            except Exception as exc:
                notifications.put(('stream_interruption', type(exc).__name__))
                if stopped.wait(3):
                    return
    for run_id in BY_ID:
        threading.Thread(target=observe, args=(run_id,), daemon=True).start()
    assert connected.wait(20), 'Could not attach native event stream'
    summaries = {}
    statuses = {}
    while len(summaries) < len(JOBS):
        try:
            kind, value = notifications.get(timeout=45)
        except queue.Empty:
            print(json.dumps({'observing_native_events': True, 'collected': len(summaries),
                              'statuses': dict(Counter(statuses.values())), 'time': now()}), flush=True)
            continue
        if kind == 'stream_interruption':
            print(json.dumps({'native_stream_reconnecting': value}), flush=True)
            continue
        candidates = JOBS if kind == 'reconcile' else [BY_ID[value]]
        for job in candidates:
            if job['issue'] in summaries:
                continue
            p = api('/runs/' + job['run_id'])
            status = p['lifecycle']['status']['kind']
            if statuses.get(job['issue']) != status:
                print(json.dumps({'issue': job['issue'], 'native_transition': status}), flush=True)
            statuses[job['issue']] = status
            if status in ['succeeded', 'failed', 'dead', 'cancelled']:
                summaries[job['issue']] = collect(job, p)
        save(ROOT / 'collector-status.json', {'updated_at': now(), 'statuses': statuses,
                                             'collected': sorted(summaries), 'destination': str(DEST)})
    stopped.set()
    save(DEST / 'queue-results.json', {'collected_at': now(), 'issues': list(summaries.values()),
                                      'qnx_excluded': [1278], 'acceptance': 'pending offline'})
    print(json.dumps({'all_terminal_collected': len(summaries), 'destination': str(DEST)}), flush=True)


if __name__ == '__main__':
    main()
