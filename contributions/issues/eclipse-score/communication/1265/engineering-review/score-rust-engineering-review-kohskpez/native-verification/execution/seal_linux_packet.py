"""Seal the Linux evidence and select its truthful contribution status."""
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
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def verify_manifest(path):
    d = json.loads(path.read_text())['files']
    for name, expected in d.items():
        subject = path.parent / name
        assert subject.resolve().is_relative_to(path.parent.resolve()), name
        assert sha(subject) == expected, str(subject)
    return {'sha256':sha(path),'subjects':len(d)}

report = json.loads((out / 'verification-report.json').read_text())
assert report['all_six_expected_cases_passed']
assert report['native_lifecycle']['kind'] == 'succeeded'
assert report['owned_Docker_stopped'] and report['owned_Fabro_stopped']
assert report['corrections_used'] == report['max_corrections'] == 3
binding = json.loads((r / 'run-binding.json').read_text())
for name, expected in binding['files'].items():assert sha(r / name) == expected, name
for name, expected in json.loads((r / 'candidate-hashes.json').read_text()).items():assert sha(r / 'candidate' / name) == expected, name
for name, expected in binding['external_tools'].items():assert sha(Path(name)) == expected, name
historical = {p.relative_to(out).as_posix():verify_manifest(p) for p in sorted(out.rglob('artifact-manifest.json')) if p != out / 'artifact-manifest.json'}
for name in re.findall(r'\]\(([^)]+)\)', (out / 'README.md').read_text()):assert (out / name).exists(), name
write(out / 'execution/final-integrity-verification.json', {'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bound_files':len(binding['files']),'bound_candidate_sources':2879,'historical_manifests':historical,'scope':'Artifact and subject integrity; tests not repeated; engineering acceptance not evaluated'})
shutil.copy2(__file__, out / 'execution/seal_linux_packet.py')
sizes = out / 'artifact-sizes.json'
manifest = out / 'artifact-manifest.json'
write(sizes, {'scope':'All packet regular files except this inventory and root manifest; nested historical manifests included','files':{p.relative_to(out).as_posix():p.stat().st_size for p in sorted(out.rglob('*')) if p.is_file() and p not in (sizes,manifest)}})
write(manifest, {'schema_version':1,'kind':'portable_subject_hash_manifest','files':{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p != manifest}})
receipt = {'path':str(out),**verify_manifest(manifest),'sealed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
write(r / 'final-linux-packet-receipt.json',receipt)

registry = contributions / 'registry.json'
inventory = contributions / 'README.md'
shutil.copy2(registry, r / 'registry-before-linux-integration.json')
shutil.copy2(inventory, r / 'inventory-before-linux-integration.md')
original = json.loads(registry.read_text())
current = json.loads(registry.read_text())
item = next(i for i in current['issues'] if i['id'] == 'eclipse-score/communication#1265')
prefix = out.relative_to(contributions).as_posix()
for key in ['record','evidence_manifest','upstream_snapshot','pr_draft']:
    filename = {'record':'README.md','evidence_manifest':'artifact-manifest.json','upstream_snapshot':'upstream-snapshot.json','pr_draft':'pr-description.md'}[key]
    item[key] = prefix + '/' + filename
item.update({'local_status':'assessment_prepared_linux_integration_verified','scope':'Documentation assessment of existing pastey 0.2.3. Fresh native Linux production Rust/C++ COM integration passed both targets and all six cases, zero failures/errors/skips, on baseline8368bfb5. Earlier unit/doctest/copyright results remain historical e3d126c2 evidence. Qualification/adoption and human acceptance pending.', 'baseline_commit':report['baseline'],'observed_upstream_HEAD':report['baseline'],'current_HEAD_native_verification':'focused_Linux_integration_measured; full_CI_unperformed','evidence_manifest_sha256':receipt['sha256'],'implementation_execution':'native_fabro_command_only;fresh_Linux_integration_passed;complete_failed_and_successful_measurements_retained','run_id':report['run_id'],'workflow_version_id':report['workflow_version_id'],'native_tests_executed':2,'native_integration_targets_executed':2,'integration_pytest_cases_passed':6,'integration_pytest_cases_failed':0,'integration_pytest_cases_errors':0,'integration_pytest_cases_skipped':0,'corrections_used':3,'max_corrections':3,'remaining_corrections':0,'stop_reason':'all_six_expected_native_Linux_integration_cases_passed;bounded_run_terminated','historical_Rust_unit_and_doctest_evidence':{'baseline':'e3d126c2d7569345cf5f790310702eb00cd86b06','cases_passed':33,'doctest_cases_ignored':2,'manifest':prefix+'/historical-rust-and-copyright/artifact-manifest.json','promoted_to_current_baseline':False},'historical_copyright_evidence':{'baseline':'e3d126c2d7569345cf5f790310702eb00cd86b06','findings':204,'all_reported_bytes_match_that_baseline':True,'current_baseline_checker_rerun':False,'review':'pending_offline'},'owned_Docker_runtime':'stopped; measured private_API_absence_and_owned_group_zero','owned_Fabro_server':'stopped','operational_storage_gap':prefix+'/historical-rust-and-copyright/execution/auxiliary-help-storage-deviation.json','packaging_draft_refusal':prefix+'/execution/packaging-draft-refusal.json'})
for key in ['Rust_cases_passed','Rust_doctest_cases_ignored','Rust_execution_run_id','copyright_findings','copyright_all_reported_bytes_match_baseline']:
    item.pop(key,None)
assert item['submission_candidate'] is False
assert current['competition_submission'] == original['competition_submission']
assert [i for i in current['issues'] if i['id'] != item['id']] == [i for i in original['issues'] if i['id'] != item['id']]
write(registry,current)
lines = inventory.read_text().splitlines()
rows = [i for i,line in enumerate(lines) if line.startswith('| [Communication #1265]')]
assert len(rows) == 1
lines[rows[0]] = f'| [Communication #1265]({prefix}/README.md) | Assess Rust COM identifier-pasting dependency; generic Rust workflow retained | Documentation patch prepared; fresh native Linux integration: six cases passed, zero failures/errors/skips; three runtime fixes used | Issue open; offline review and qualification/adoption pending; older unit/copyright results preserved separately |'
inventory.write_text('\n'.join(lines)+'\n')
validate_run_root(r)
print(json.dumps(receipt))
