"""Retain Linux native execution evidence separately from historical checks."""
import datetime
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from score_sw_fabric.storage import validate_run_root

r = Path(__file__).parent
validate_run_root(r)
out = Path(json.loads((r / 'contribution.json').read_text())['path'])
base = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265')
prior = base / 'verification-recovery/score-fabric-7r64z_kz'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def copy_file(source, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    assert sha(source) == sha(dest)

assert (r / 'run-final.json').is_file()
run = json.loads((r / 'run-final.json').read_text())
plan = json.loads((r / 'check-plan.json').read_text())
binding = json.loads((r / 'run-binding.json').read_text())
for name, expected in binding['files'].items():
    assert sha(r / name) == expected, name
for name, expected in json.loads((r / 'candidate-hashes.json').read_text()).items():
    assert sha(r / 'candidate' / name) == expected, name
for name, expected in binding['external_tools'].items():
    assert sha(Path(name)) == expected, name
runtime = json.loads((r / 'runtime-overlays.json').read_text())
for item in runtime['overlays']:
    assert sha(Path(item['source'])) == item['source_sha256']
    assert sha(Path(item['target'])) == item['host_original_sha256']
    assert Path(item['source']).stat().st_mode & 0o7777 == item['mode']
prior_manifest = json.loads((prior / 'artifact-manifest.json').read_text())
assert sha(prior / 'artifact-manifest.json') == '6357dce316bbf9e30bb23accd75fdb553a7a87130f040bc4108a815267c0c600'
for name, expected in prior_manifest['files'].items():
    assert sha(prior / name) == expected
    copy_file(prior / name, out / 'historical-rust-and-copyright' / name)
copy_file(prior / 'artifact-manifest.json', out / 'historical-rust-and-copyright/artifact-manifest.json')

execution = out / 'execution'
execution.mkdir(exist_ok=True)
for p in sorted(r.iterdir()):
    if p.is_file() and p.suffix in {'.json', '.py', '.fabro', '.toml', '.log'}:
        copy_file(p, execution / p.name)
for folder in ['logs', 'attempts']:
    for p in sorted((r / folder).rglob('*')):
        if p.is_file():
            copy_file(p, execution / p.relative_to(r))
private = Path(json.loads((r / 'server-binding.json').read_text())['private_state'])
if (private / 'server.log').exists():
    copy_file(private / 'server.log', execution / 'native-server.log')
for p in sorted((private / 'storage/scratch').glob('*/petri/executions/*/logs/*.log')):
    copy_file(p, execution / 'native-stage-logs' / p.parent.parent.name / p.name)

cases = []
test_roots = list((r / 'bazel-output').glob('*/execroot/_main/bazel-out/*/testlogs'))
for label in plan['targets']:
    package, target = label[2:].split(':')
    matches = [root / package / target for root in test_roots if (root / package / target / 'test.xml').is_file()]
    assert len(matches) <= 1, 'Ambiguous native XML roots'
    folder = matches[0] if matches else r / 'candidate/bazel-testlogs' / package / target
    record = {'target': label, 'expected_cases': plan['expected_pytest_cases'][target], 'xml_present': (folder / 'test.xml').is_file(), 'test_log_present': (folder / 'test.log').is_file(), 'actual_native_output_directory': str(folder), 'collection_scope': 'Offline measured actual native output tree; executed collector convenience-symlink path was unavailable and its raw report is preserved'}
    for p in folder.rglob('*') if folder.exists() else []:
        if p.is_file():
            copy_file(p, execution / 'testlogs' / package / target / p.relative_to(folder))
    if record['xml_present']:
        parsed = ET.parse(folder / 'test.xml')
        actual = [{'name': c.attrib.get('name'), 'classname': c.attrib.get('classname'), 'failure': c.find('failure') is not None, 'error': c.find('error') is not None, 'skipped': c.find('skipped') is not None} for c in parsed.getroot().iter('testcase')]
        record['actual_cases'] = actual
        record['counts'] = {'passed': sum(not any(c[k] for k in ['failure','error','skipped']) for c in actual), 'failed': sum(c['failure'] for c in actual), 'errors': sum(c['error'] for c in actual), 'skipped': sum(c['skipped'] for c in actual)}
        record['exact_expected_names_match'] = sorted(c['name'] for c in actual) == sorted(record['expected_cases'])
        record['all_expected_cases_passed'] = record['exact_expected_names_match'] and record['counts']['passed'] == len(record['expected_cases'])
    else:
        record['all_expected_cases_passed'] = False
    cases.append(record)
passed = all(c['all_expected_cases_passed'] for c in cases)

source_paths = ['MODULE.bazel','MODULE.bazel.lock','.bazelrc','.bazelversion','CI.md','LICENSE','NOTICE','quality/integration_testing/integration_testing.bzl','score/mw/com/rust/BUILD','score/mw/com/rust/README.md','score/mw/com/rust/design/identifier_pasting_assessment.md','score/mw/com/test/basic_rust_api/BUILD','score/mw/com/test/basic_rust_api/bigdata_com_api_gen.rs','score/mw/com/test/basic_rust_api/bigdata_com_api_gen.cpp','score/mw/com/test/basic_rust_api/bigdata_com_api_gen.h']
for name in source_paths:
    if (r / 'candidate' / name).is_file():copy_file(r / 'candidate' / name, out / 'sources/native' / name)
for folder in ['consumer_sync_apis','consumer_async_apis','producer_app','etc']:
    for p in sorted((r / 'candidate/score/mw/com/test/basic_rust_api' / folder).rglob('*')):
        if p.is_file():copy_file(p, out / 'sources/native' / p.relative_to(r / 'candidate'))
for item in json.loads((r / 'source-provenance.json').read_text())['updates']:
    copy_file(r / 'candidate' / item['path'], out / 'sources/native' / item['path'])
for folder in ['runtime-libs','runtime-provenance']:
    for p in sorted((r / folder).rglob('*')):
        if p.is_file():copy_file(p, out / 'sources' / p.relative_to(r))
output = next((r / 'bazel-output').glob('*/external'))
for name in ['defs.bzl','bazel/py_itf_test.bzl','score/itf/plugins/docker.py','score/itf/plugins/core.py','score/itf/plugins/core_dump.py','LICENSE','NOTICE']:
    p = output / 'score_itf+' / name
    if p.is_file():copy_file(p, out / 'sources/native-itf' / name)
artifact_metadata = []
for label in plan['targets']:
    package, name = label[2:].split(':')
    bin_roots = list((r / 'bazel-output').glob('*/execroot/_main/bazel-out/*/bin'))
    for bin_root in bin_roots:
        folder = bin_root / package
        if not folder.exists():continue
        for p in sorted(folder.rglob('*')):
            if p.is_file() and (p.name in {'index.json','oci-layout','manifest.json'} or '/blobs/sha256/' in str(p)):
                # Hash native OCI image metadata/layers and retain small descriptors.
                record = {'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size, 'exported': p.stat().st_size <= 1024 * 1024}
                if record['exported']:copy_file(p, out / 'execution/native-oci' / package / p.relative_to(folder))
                artifact_metadata.append(record)
write(out / 'native-oci-subjects.json', {'scope': 'Native OCI descriptors exported; larger layer bytes retained in bound build workspace and referenced by size/hash, not copied into portable packet', 'files': artifact_metadata})
copy_file(base / 'communication-1265.patch', out / 'communication-1265.patch')
copy_file(base / 'pr-title.txt', out / 'pr-title.txt')
issue = json.loads((r / 'upstream-issue.json').read_text())
write(out / 'upstream-snapshot.json', {'url': issue['html_url'], 'issue_number': issue['number'], 'state': issue['state'], 'captured_on': '2026-10-06', 'updated_at': issue['updated_at'], 'title': issue['title'], 'baseline_commit': plan['baseline'], 'original_issue': 'execution/upstream-issue.json'})
ledger = json.loads((r / 'correction-ledger.json').read_text())
shutdown = json.loads((r / 'docker-shutdown.json').read_text())
report = {'schema_version':1, 'issue':'eclipse-score/communication#1265', 'exported_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'baseline':plan['baseline'], 'run_id':run['id'], 'workflow_version_id':json.loads((r / 'workflow-registration.json').read_text())['workflow_version_id'], 'native_lifecycle':run['lifecycle']['status'], 'models':run['models'], 'provider_usage':run['usage'], 'expected_native_targets':2, 'expected_pytest_cases':6, 'test_records':cases, 'all_six_expected_cases_passed':passed, 'checks':json.loads((r / 'verification-results.json').read_text()).get('checks',[]) if (r / 'verification-results.json').exists() else [], 'bound_files':len(binding['files']), 'bound_candidate_subjects':2879, 'run_binding_sha256':sha(r / 'run-binding.json'), 'Linux_runtime':'native Ubuntu24.04 OCI applications in owned rootless Docker29.8.2; native socket mapped privately inside bwrap', 'storage':json.loads((r / 'storage-selection.json').read_text()), 'owned_Docker_stopped':shutdown['owned_runtime_stopped'], 'owned_Fabro_stopped':json.loads((r / 'server-shutdown.json').read_text())['owned_server_stopped'], 'corrections_used':ledger['corrections_used'], 'max_corrections':3, 'patch_sha256':binding['patch_sha256'], 'historical_evidence':'historical-rust-and-copyright/; Rust33passed2ignored and copyright204findings apply to e3d126c2 baseline, not rerun or promoted to current8368', 'omissions':plan['omissions'], 'qualification_adoption':'pending_offline', 'engineering_acceptance':'pending_offline', 'full_native_CI':'unperformed', 'source_changes':'README and assessment only'}
write(out / 'verification-report.json', report)
write(out / 'correction-ledger.json', ledger)
token = json.loads((private / 'secrets.json').read_text())['token'].encode()
for p in out.rglob('*'):
    if p.is_file():assert token not in p.read_bytes(), 'Refuse credential export: '+str(p)
validate_run_root(r)
print(json.dumps({'packet':str(out),'all_six_expected_cases_passed':passed,'records':[{'target':c['target'],'counts':c.get('counts'),'expected_match':c.get('exact_expected_names_match')} for c in cases],'files':sum(p.is_file() for p in out.rglob('*'))}))
