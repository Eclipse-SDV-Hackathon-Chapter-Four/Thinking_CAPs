"""Protected native measurement; source corrections are made by Codex outside this graph."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from storage import validate_run_root

ROOT = Path(__file__).parent
WORK = ROOT / 'workspaces/560'
PYTHON = '/home/jefferson/s-core_sw_fabric/.venv/bin/python'
BASELINE = '381d43dec900ab6a9076f3f30e7bfbdee019e26e'
ALLOWED = 'score/mw/com/test/basic_rust_api/subscription_state_apis/'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def sources():
    incoming = json.loads((ROOT / 'incoming-source-hashes.json').read_bytes())
    result = {rel: sha(WORK / rel) for rel in incoming}
    for path in (WORK / ALLOWED).rglob('*'):
        if path.is_file():
            relative = str(path.relative_to(WORK))
            result[relative] = sha(path)
    assert all(result[p] == h for p, h in incoming.items() if not p.startswith(ALLOWED))
    return result

def main():
    action, raw = sys.argv[1:]
    n = int(raw)
    validate_run_root(ROOT)
    ledger = json.loads((ROOT / 'correction-ledger.json').read_bytes())
    assert 1 <= n <= 3 and ledger['codex_used'] == n and ledger['codex_max'] == 3
    for rel, h in json.loads((ROOT / 'control-binding.json').read_bytes()).items():
        assert sha(ROOT / rel) == h, rel
    folder = ROOT / f'attempt-{n}'
    folder.mkdir(exist_ok=True)
    if action == 'check':
        assert not (folder / 'native/native-result.json').exists(), 'Never repeat a measured attempt'
        before = sources()
        save(folder / 'measured-source-hashes.json', before)
        process = subprocess.run([PYTHON, str(ROOT / 'linux_launcher.py'),
                                  '--workspace', str(WORK), '--plan', str(ROOT / 'check-plan.json'),
                                  '--output', str(folder / 'native')], cwd=ROOT,
                                 env={'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'HOME': '/home/jefferson',
                                      'LANG': 'C.UTF-8'})
        validate_run_root(ROOT)
        assert sources() == before, 'Native subject changed during measurement'
        result = json.loads((folder / 'native/native-result.json').read_bytes())
        save(folder / 'measurement-binding.json', {
            'attempt': n, 'editor': 'Codex', 'historical_corrections': 3,
            'source_vector_sha256': sha(folder / 'measured-source-hashes.json'),
            'native_result_sha256': sha(folder / 'native/native-result.json'),
            'subject_unchanged': True, 'passed': result['passed'],
            'native_exit_code': process.returncode, 'acceptance': 'pending_offline'})
        print(json.dumps({'attempt': n, 'passed': result['passed'], 'checks': len(result['checks'])}))
        return process.returncode
    assert action == 'export'
    result_file = folder / 'native/native-result.json'
    result = json.loads(result_file.read_bytes()) if result_file.exists() else {'passed': False, 'checks': [], 'missing': True}
    final = sources()
    save(folder / 'final-source-hashes.json', final)
    incoming = json.loads((ROOT / 'incoming-source-hashes.json').read_bytes())
    changes = []
    for rel, h in final.items():
        if incoming.get(rel) != h:
            destination = folder / 'changed-source' / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((WORK / rel).read_bytes())
            changes.append(rel)
    index = folder / 'export-index'
    env = {'PATH': '/usr/bin:/bin', 'HOME': '/home/jefferson', 'GIT_INDEX_FILE': str(index)}
    def git(*args):
        return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(WORK), *args], env=env)
    git('read-tree', BASELINE)
    git('add', '-A', '--', 'score/mw/com')
    (folder / 'full.patch').write_bytes(git('diff', '--cached', BASELINE, '--binary', '--', 'score/mw/com'))
    index.unlink(missing_ok=True)
    save(folder / 'summary.json', {'attempt': n, 'editor': 'Codex', 'changed_paths_from_incoming': changes,
                                  'passed': result['passed'], 'native_checks_executed': len(result['checks']),
                                  'source_subjects': len(final), 'historical_corrections_used': 3,
                                  'codex_corrections_used': n, 'codex_remaining': 3 - n,
                                  'exported_at': datetime.now(timezone.utc).isoformat(),
                                  'acceptance': 'pending_offline', 'issue_closed': False})
    ledger['attempts'][n - 1]['state'] = 'verified_pass' if result['passed'] else 'verified_fail_or_missing'
    ledger['attempts'][n - 1]['summary_sha256'] = sha(folder / 'summary.json')
    save(ROOT / 'correction-ledger.json', ledger)
    print(json.dumps({'attempt': n, 'exported': True, 'native_passed': result['passed']}))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
