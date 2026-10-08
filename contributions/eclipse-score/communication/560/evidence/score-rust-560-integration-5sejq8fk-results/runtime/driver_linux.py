"""Deterministic workspace/check/export commands for the submitted Rust queue."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from storage import build_environment, validate_run_root


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def paths(number: str):
    validate_run_root(ROOT)
    assert number.isdigit()
    job = ROOT / 'jobs' / number
    control = json.loads((job / 'task.json').read_text())
    return job, Path(control['workspace']), control


def preflight(number: str) -> int:
    job, workspace, control = paths(number)
    for path, expected in control['control_hashes'].items():
        assert sha(Path(path)) == expected, ('Queue control drift', path)
    head = subprocess.check_output(['git', '-C', str(workspace), 'rev-parse', 'HEAD'], text=True).strip()
    if head not in [control['baseline'], control['incoming_head']]:
        binding = json.loads((job / 'native-workspace-binding.json').read_text())
        snapshot = Path(binding['snapshot_repository'])
        refs = subprocess.check_output(['git', '--git-dir', str(snapshot), 'for-each-ref', '--format=%(objectname)', 'refs/checkpoints/'], text=True).splitlines()
        assert head in refs, ('HEAD is not a published native checkpoint', head)
        assert subprocess.run(['git', '-C', str(workspace), 'merge-base', '--is-ancestor', control['baseline'], head], capture_output=True).returncode == 0, 'Checkpoint lost baseline ancestry' 
    for relative, expected in json.loads((job / 'baseline-hashes.json').read_text()).items():
        assert sha(workspace / relative) == expected, ('Source drift', relative)
    save(job / 'execution/preflight.json', {'status': 'verified', 'source_subjects': len(json.loads((job / 'baseline-hashes.json').read_text())), 'baseline': control['baseline'], 'native_checkpoint_head': head, 'storage': 'bound_volume_valid', 'native_checks': 'not_executed', 'human_acceptance': 'pending'})
    return 0


def checks(number: str, attempt: str) -> int:
    job, workspace, control = paths(number)
    output = job / 'execution' / ('check-' + attempt)
    output.mkdir(parents=True, exist_ok=False)
    plan_file = workspace / '.rust-queue/reports/check-plan.json'
    result = {'issue': int(number), 'attempt': int(attempt), 'baseline': control['baseline'], 'kind': 'infrastructure_unavailable', 'passed': False, 'checks': [], 'engineering_acceptance': 'pending'}
    def retain():
        save(output / 'result.json', result)
        save(workspace / '.rust-queue/reports/native-check-summary.json', result)
        print(json.dumps(result))
    # The operator supplies a hash-bound Linux measurement launcher after admission.
    # An agent-authored plan never grants shell execution or declares a check passed.
    runtime_file = ROOT / 'linux-measurement-binding.json'
    if not runtime_file.is_file():
        result['reason'] = 'Linux measurement runner is not bound; no native checks executed'
        result['collection_status'] = 'retained_missing_evidence; no source correction warranted'
        retain()
        # Successful collection is distinct from a passing native check. Missing
        # infrastructure routes to review/export instead of consuming source repairs.
        return 0
    if not plan_file.is_file():
        result.update(kind='missing_check_plan', reason='No native check plan supplied')
        retain()
        return 1
    binding = json.loads(runtime_file.read_text())
    launcher = Path(binding['launcher'])
    assert sha(launcher) == binding['sha256']
    for relative, expected in json.loads((job / 'baseline-hashes.json').read_text()).items():
        assert sha(workspace / relative) == expected, ('Existing native source changed outside test scope', relative)
    plan = json.loads(plan_file.read_text())
    assert isinstance(plan.get('checks'), list) and plan['checks'], 'Checks must be explicit'
    for item in plan['checks']:
        assert set(item) <= {'kind', 'targets', 'reason', 'native_obligation', 'config'}
        assert item['kind'] in ['test', 'doctest', 'build', 'query', 'docs', 'lint']
        assert all(isinstance(t, str) and t.startswith('//') and not any(c in t for c in '\n\r;`$') for t in item.get('targets', []))
    with (output / 'stdout.log').open('wb') as out, (output / 'stderr.log').open('wb') as err:
        completed = subprocess.run([str(launcher), '--workspace', str(workspace), '--plan', str(plan_file), '--output', str(output)], cwd=workspace, env={**os.environ, **build_environment(ROOT)}, stdout=out, stderr=err)
    measured = output / 'native-result.json'
    if measured.is_file():
        result['native_result'] = {'path': str(measured), 'sha256': sha(measured)}
        native = json.loads(measured.read_text())
        result['bounded_native_summary'] = {'passed': native.get('passed', False), 'infrastructure_error': native.get('infrastructure_error'), 'checks': [{'kind': item['kind'], 'targets': item['targets'], 'exit_code': item['exit_code'], 'timed_out': item['timed_out'], 'bounded_tail': item.get('bounded_tail', '')[-4000:]} for item in native.get('checks', [])]}
        save(output / 'measured-subject-hashes.json', {str(p.relative_to(workspace)): sha(p) for p in (workspace / 'score/mw/com').rglob('*') if p.is_file() and not p.is_symlink()})
        result['measured_subject_hashes_sha256'] = sha(output / 'measured-subject-hashes.json')
    result.update(kind='measured_native_command', exit_code=completed.returncode, passed=completed.returncode == 0 and measured.is_file() and native.get('passed') is True)
    retain()
    return 0 if result['passed'] else 1


def export(number: str) -> int:
    job, workspace, control = paths(number)
    out = job / 'export'
    out.mkdir(parents=True, exist_ok=True)
    # Include newly created regression/design files without mutating the native
    # working index or forgetting files that git diff normally omits.
    index = job / 'execution/export-index'
    index.parent.mkdir(parents=True, exist_ok=True)
    if index.exists():
        index.unlink()
    git_env = {**os.environ, 'GIT_INDEX_FILE': str(index)}
    subprocess.run(['git', '-C', str(workspace), 'read-tree', control['baseline']], env=git_env, check=True)
    subprocess.run(['git', '-C', str(workspace), 'add', '--', 'score/mw/com'], env=git_env, check=True)
    diff = subprocess.check_output(['git', '-C', str(workspace), 'diff', '--cached', '--binary', control['baseline'], '--', 'score/mw/com'], env=git_env)
    (out / ('communication-' + number + '.patch')).write_bytes(diff)
    reports = workspace / '.rust-queue/reports'
    if reports.exists():
        import shutil
        shutil.copytree(reports, out / 'reports', dirs_exist_ok=True)
    results = [json.loads(f.read_text()) for f in sorted((job / 'execution').glob('check-*/result.json'))]
    save(out / 'review-summary.json', {'issue': int(number), 'baseline': control['baseline'], 'prepared_at': datetime.now(timezone.utc).isoformat(), 'mode': control['mode'], 'native_results': results, 'claim': 'Export completed; failed/missing evidence retained, no acceptance or automatic issue closure', 'historical_reuse': control.get('historical_reuse'), 'max_source_corrections': control['max_source_corrections'], 'authorized_human_acceptance': 'pending'})
    save(out / 'artifact-manifest.json', {'schema_version': 1, 'files': {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file() and p.name != 'artifact-manifest.json'}})
    return 0



def reserve(number: str, attempt: str) -> int:
    job, workspace, control = paths(number)
    ledger = job / 'correction-ledger.json'
    value = json.loads(ledger.read_text())
    n = int(attempt)
    assert n == value['used'] + 1 and n <= value['max'], 'No reset or repeat correction'
    assert n == 3 and control['historical_corrections_used'] == 2
    assert control['integration_plan_sha256'] == sha(Path(control['integration_plan']))
    value['used'] = n
    value['remaining'] = value['max'] - n
    value['attempts'].append({'attempt': n, 'reservation': 'counts even if agent or transport fails', 'reserved_at': datetime.now(timezone.utc).isoformat()})
    save(ledger, value)
    return 0

if __name__ == '__main__':
    action, number = sys.argv[1:3]
    if action == 'reserve':
        raise SystemExit(reserve(number, sys.argv[3]))
    if action == 'preflight':
        raise SystemExit(preflight(number))
    if action == 'check':
        raise SystemExit(checks(number, sys.argv[3]))
    if action == 'export':
        raise SystemExit(export(number))
    raise SystemExit('Unknown action')
