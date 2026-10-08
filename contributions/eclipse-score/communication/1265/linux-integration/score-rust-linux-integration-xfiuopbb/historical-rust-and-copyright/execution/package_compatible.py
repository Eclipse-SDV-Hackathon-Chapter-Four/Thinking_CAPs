"""Offline complete packet, preserving every native refusal and carried result."""
from pathlib import Path
import hashlib,json,shutil,sys,re,datetime
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r);out=Path(json.loads((r/'contribution.json').read_text())['path'])
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
first=json.loads((out/'verification-report.json').read_text());save(out/'first-compatible-verification-report.json',first)
for p in r.iterdir():
 if p.is_file() and p.suffix in {'.json','.py','.sh','.fabro','.toml','.log','.txt','.stderr','.stdout','.nul'}:copy(p,out/'execution'/p.name)
for p in (r/'logs').glob('*.log'):copy(p,out/'execution/logs'/p.name)
secrets=[]
for folder,label in [(r,'initial-compatible-run'),(r/'copyright-recovery','copyright-git-run'),(r/'copyright3-recovery','copyright-normalized-run')]:
 for p in folder.iterdir():
  if p.is_file() and p.suffix in {'.json','.fabro','.toml','.log'}:copy(p,out/'execution'/label/p.name)
 b=json.loads((folder/'server-binding.json').read_text());private=Path(b['private_state']);secrets.append(json.loads((private/'secrets.json').read_text())['token'].encode())
 copy(private/'server.log',out/'execution'/label/'server.log')
 for p in (private/'storage/scratch').glob('*/petri/executions/*/logs/*.log'):
  copy(p,out/'execution'/label/'native-stage-logs'/p.name)
 for p in ['run-final.json','server-shutdown.json']:assert (folder/p).exists()
for directory in ['runtime-libs','runtime-provenance','runtime-notices']:
 for p in (r/directory).rglob('*'):
  if p.is_file():copy(p,out/'sources'/directory/p.relative_to(r/directory))
source_code=next((r/'bazel-output').glob('*/external/score_tooling+/cr_checker/tool/cr_checker.py'))
copy(source_code,out/'sources/native-copyright/cr_checker.py');copy(source_code.parent.parent/'cr_checker.bzl',out/'sources/native-copyright/cr_checker.bzl')
for name in ['BUILD','third_party/cr_checker/templates.ini','third_party/cr_checker/config.json']:
 copy(r/'candidate'/name,out/'sources/native-copyright'/name)
latest=json.loads((r/'copyright3-recovery/run-final.json').read_text());stages=json.loads((r/'copyright3-recovery/run-stages.json').read_text())['data'];measured=json.loads((r/'copyright3-recovery/verification-results.json').read_text())
findings=json.loads((r/'copyright-findings-normalized.json').read_text());findings['native_summary_counts']={'missing_headers':96,'wrong_format':107,'duplicate_headers':1,'misplaced_correct_headers':0,'license_mismatches':0};save(out/'copyright-findings.json',findings)
report={**first,'exported_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_id':latest['id'],'workflow_version_id':json.loads((r/'copyright3-recovery/workflow-registration.json').read_text())['workflow_version_id'],'native_lifecycle':latest['lifecycle']['status'],'stage_statuses':{s['name']:s['status'] for s in stages},'verification_status':'Rust_scoped_checks_passed_copyright_failed','checks':measured['checks'],'measured_collector_report':'execution/copyright-normalized-run/verification-results.json','native_worker_preflight':'execution/copyright-normalized-run/native-worker-preflight.json','direct_local_preflights':['execution/compatibility-preflight.json','execution/runtime-signature-measurement.json'],'Rust_targets_passed':3,'Rust_cases_passed':33,'Rust_cases_failed':0,'Rust_doctest_cases_ignored':2,'Rust_execution_run_id':'01M484ZS5EGJ8E5KH83XXN7PCB','Rust_evidence_mode':'carried_from_completed_native_run_by_unchanged2879source_and_original45config_runtime_and_raw_test_log_hashes','copyright_native_findings':204,'copyright_unique_reported_files':204,'copyright_counts':findings['native_summary_counts'],'copyright_all_reported_bytes_match_baseline':True,'copyright_scope':'unchanged native checker/templates/config; operator normalizes exactly two root label strings to intended workspace paths; unmodified target failures retained','copyright_Markdown_native_coverage':'excluded_by_native_templates','documentation_license_marker_inspection':'execution/documentation-license-inspection.json; text inspection, not native coverage or human acceptance','selected_baseline':'e3d126c2d7569345cf5f790310702eb00cd86b06','observed_upstream_HEAD':'81a540e196421d7613350d77068e9a886eccbac6','upstream_delta':'two commits change one C++/RustFFIheader; latestHEADnativeverificationnotperformed','documentation_patch_current_HEAD_applicability':'execution/current-doc-patch-check.json','corrections_used':3,'max_corrections':3,'remaining_corrections':0,'stop_reason':'budget_exhausted_after_native_copyright_findings; no unrelated cleanup or further run','prior_recovery_manifest_sha256':'a211f501c0b2c824ddd3172a634d514fa23bf4b692a17371a6f20a3afb000716','prior_recovery_preserved':'prior-recovery/','provider_usage':latest['usage'],'models':latest['models'],'engineering_acceptance':'pending_offline','qualification_adoption':'pending_offline','findings_disposition':'pending_native_offline_review; not accepted/suppressed/declaredfalsepositives','operational_storage_gap':'execution/auxiliary-help-storage-deviation.json; auxiliary help query extracted install in defaultcache; exactdeltaunmeasured; nativebuildsremainSSDbound'}
save(out/'verification-report.json',report)
ledger=json.loads((out/'correction-ledger.json').read_text());ledger['status']='stopped_budget_exhausted';ledger['stop_reason']=report['stop_reason'];save(out/'correction-ledger.json',ledger);copy(out/'correction-ledger.json',out/'execution/final-correction-ledger.json')
snapshot=json.loads((out/'prior-attempt/upstream-snapshot.json').read_text());issue=json.loads((r/'issue-current.json').read_text());snapshot.update({'captured_on':'2026-10-06','state':issue['state'],'title':issue['title'],'updated_at':issue['updated_at'],'observed_HEAD':report['observed_upstream_HEAD'],'native_verification_baseline':report['selected_baseline']});save(out/'upstream-snapshot.json',snapshot)
copy(out/'prior-attempt/communication-1265.patch',out/'communication-1265.patch');copy(out/'prior-attempt/pr-title.txt',out/'pr-title.txt')
(out/'pr-description.md').write_text('''Document the Rust COM API's existing pastey0.2.3 dependency, configured features,
generated identifier patterns, API consumers, provenance, licensing and maintenance.
Compare paste/pastey/internal alternatives and record qualification/adoption evidence
and replacement compatibility obligations. Proposed retain-current disposition
remains pending offline engineering review; production Rust, APIs, dependencies,
locks and native policy are unchanged.

Validation on communication baselinee3d126c2d7569345cf5f790310702eb00cd86b06:
allthree nativeRusttargets passed,33casespassed and2doctestcasesignored, with the
pinnedFerrocene compiler in a verified privateUbuntuNoble library namespace.
Copyrightcheckingfailed: after recordedGitmetadata andtwo-label argument remedies,
the unchanged nativechecker reported96missingheaders,107wrongformats and1duplicate
on204files whosebytesmatchthebaseline. Markdownisexcludedbyitsnative templates;
the newdocument'sApache2SPDXnotice was separately inspected as text.
The patch checks cleanly against the unchangedREADME at observed currentHEAD81a540e
(currentHEADnativeverificationnotperformed; oneC++/RustFFIheader differs).
Fullfailed logs and supervisor review are retained; recovery3/3fixes exhausted.
Qualification/adoption, current-baseline/fullCI/QNX and human acceptance remain pending.
''')
for p in out.rglob('*'):
 if p.is_file():
  data=p.read_bytes();assert not any(secret in data for secret in secrets),str(p)
validate_run_root(r)
print(json.dumps({'packet':str(out),'Rust_cases_passed':33,'Rust_doctests_ignored':2,'copyright_findings':204,'corrections_used':3,'latest_native_status':latest['lifecycle']['status']}))
