"""Seal public evidence and update only the authorized contribution record."""
import datetime
import hashlib
import json
import re
import shutil
from pathlib import Path

from score_sw_fabric.storage import validate_run_root

r = Path(__file__).parent
validate_run_root(r)
out = Path(json.loads((r / 'contribution.json').read_text())['path'])
contributions = out.parents[5]
assert contributions.name == 'contributions'

def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def check(root, files):
    for relative, expected in files.items():
        p = root / relative
        assert p.resolve().is_relative_to(root.resolve()), relative
        assert sha(p) == expected, relative
    return len(files)

bindings = {}
for name in ['run-binding.json', 'run-binding-copyright.json', 'run-binding-copyright3.json']:
    d = json.loads((r / name).read_text())
    bindings[name] = check(r, d['files'])
    if d.get('git_metadata_files'):
        check(r / 'candidate', d['git_metadata_files'])
    for path, expected in d.get('external_tools', {}).items():
        assert sha(Path(path)) == expected
sources = check(r / 'candidate', json.loads((r / 'candidate-hashes.json').read_text()))
overlays = json.loads((r / 'runtime-overlays.json').read_text())['overlays']
for lib in overlays:
    assert sha(Path(lib['source'])) == lib['source_sha256']
    assert sha(Path(lib['target'])) == lib['host_original_sha256']
    assert Path(lib['source']).stat().st_mode & 0o7777 == lib['mode']
assert (r / 'copyright-label-wrapper.sh').stat().st_mode & 0o7777 == 0o755
ledger = json.loads((out / 'correction-ledger.json').read_text())
assert ledger['corrections_used'] == ledger['max_corrections'] == 3
assert ledger['status'] == 'stopped_budget_exhausted'
historical = {}
for p in sorted(out.rglob('artifact-manifest.json')):
    if p != out / 'artifact-manifest.json':
        historical[p.relative_to(out).as_posix()] = {'sha256': sha(p), 'subjects': check(p.parent, json.loads(p.read_text())['files'])}
for relative in re.findall(r'\]\(([^)]+)\)', (out / 'README.md').read_text()):
    assert (out / relative).exists(), relative
write(out / 'execution/final-subject-verification.json', {
    'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'bindings': bindings, 'candidate_sources': sources,
    'runtime_and_original_host_libraries': len(overlays),
    'historical_manifests': historical,
    'scope': 'byte integrity and storage binding; native checks not repeated; no engineering acceptance',
})
shutil.copy2(__file__, out / 'execution/seal_contribution.py')
manifest = out / 'artifact-manifest.json'
sizes = out / 'artifact-sizes.json'
write(sizes, {'scope': 'All retained regular files except this size inventory and the root manifest; nested historical manifests included', 'files': {p.relative_to(out).as_posix(): p.stat().st_size for p in sorted(out.rglob('*')) if p.is_file() and p not in (manifest, sizes)}})
files = {p.relative_to(out).as_posix(): sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p != manifest}
write(manifest, {'schema_version': 1, 'kind': 'portable_subject_hash_manifest', 'files': files})
assert check(out, files) == len(files)
receipt = {'path': str(out), 'subjects': len(files), 'manifest_sha256': sha(manifest), 'sealed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
write(r / 'final-packet-receipt.json', receipt)

registry_path = contributions / 'registry.json'
readme_path = contributions / 'README.md'
before = json.loads(registry_path.read_text())
shutil.copy2(registry_path, r / 'registry-before-compatible-promotion.json')
shutil.copy2(readme_path, r / 'contributions-README-before-compatible-promotion.md')
prefix = out.relative_to(contributions).as_posix()
item = next(i for i in before['issues'] if i['id'] == 'eclipse-score/communication#1265')
item.update({
    'record': prefix + '/README.md',
    'local_status': 'assessment_prepared_rust_verified_copyright_failed',
    'scope': 'Documentation assessment of existing pastey 0.2.3; three native Rust targets passed, 33 cases passed and two ignored. Copyright failed with 204 baseline-identical findings. Newer upstream native verification, qualification/adoption and human acceptance pending.',
    'evidence_manifest': prefix + '/artifact-manifest.json',
    'evidence_manifest_sha256': receipt['manifest_sha256'],
    'upstream_snapshot': prefix + '/upstream-snapshot.json',
    'pr_draft': prefix + '/pr-description.md',
    'implementation_execution': 'native_fabro_command_only;Rust_passed;copyright_failed;failure_export_retained',
    'run_id': '01M4863C6JY8WNMY9T44H47XV8',
    'workflow_version_id': '2eca92a572d50dc850930335de77ed159f93bf4cb8fa87f41aeb4d4949a283fe',
    'Rust_execution_run_id': '01M484ZS5EGJ8E5KH83XXN7PCB',
    'native_tests_executed': 3,
    'Rust_cases_passed': 33,
    'Rust_doctest_cases_ignored': 2,
    'copyright_findings': 204,
    'copyright_all_reported_bytes_match_baseline': True,
    'observed_upstream_HEAD': '81a540e196421d7613350d77068e9a886eccbac6',
    'current_HEAD_native_verification': 'pending',
    'stop_reason': 'compatible_userspace_recovery_budget_exhausted',
    'operational_storage_gap': prefix + '/execution/auxiliary-help-storage-deviation.json',
})
assert item['submission_candidate'] is False
before['updated_on'] = '2026-10-06'
write(registry_path, before)
after = json.loads(registry_path.read_text())
original = json.loads((r / 'registry-before-compatible-promotion.json').read_text())
assert after['competition_submission'] == original['competition_submission']
assert [i for i in after['issues'] if i['issue_number'] != 1265] == [i for i in original['issues'] if i['issue_number'] != 1265]
lines = readme_path.read_text().splitlines()
rows = [n for n, line in enumerate(lines) if line.startswith('| [Communication #1265]')]
assert len(rows) == 1
lines[rows[0]] = f'| [Communication #1265]({prefix}/README.md) | Assess Rust COM identifier-pasting dependency; generic Rust workflow retained | Documentation patch prepared; three native Rust targets passed: 33 cases passed, two ignored; copyright failed with 204 baseline-identical findings; recovery 3/3 fixes used | Issue open; offline engineering review, qualification/adoption and current-baseline verification pending |'
readme_path.write_text('\n'.join(lines) + '\n')
validate_run_root(r)
print(json.dumps(receipt))
