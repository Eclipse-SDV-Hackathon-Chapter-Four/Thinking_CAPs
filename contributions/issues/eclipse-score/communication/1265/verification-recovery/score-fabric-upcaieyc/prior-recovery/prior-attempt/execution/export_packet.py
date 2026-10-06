from pathlib import Path
import datetime,hashlib,json,shutil,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r)
c=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265')
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def copy(source,dest):dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
for name in ['run-binding.json','workflow.fabro','workflow.toml','workflow-version.json','workflow-registration.json','server-binding.json','server-shutdown.json','run-intent.json','run-start-intent.json','run-created.json','run-started.json','run-final.json','run-stages.json','run-events.json','fabro-wait.log','fabro-wait-result.json','collector.py','run_native.py','storage-selection.json','fabro-source-bindings.json','prepare_packet.py','prepare_run.py','export_packet.py','final_correction.py']:
 copy(r/name,c/'execution'/name)
logs=Path('/home/jefferson/.local/state/s-core/fabro/score-fabric-3t71eiin/communication1265/storage/scratch/20261006-01M475MP83BBNK7VHZ3231Z657/petri/executions/0000000000000000/logs')
for p in logs.glob('*.log'):copy(p,c/'execution'/'logs'/p.name)
for name in ['communication-e3d126c2d7569345cf5f790310702eb00cd86b06.tar.gz','score-crates-4656dda8f04a3d88c8089f63111195840cfbd9e3.tar.gz','crate_index__pastey-0.2.3.crate','crate_index__paste-1.0.15.crate','issue.json','as1100k-pastey-metadata.json','dtolnay-paste-metadata.json']:
 copy(r/name,c/'sources'/name)
# Retain failed registration's server response log, whose source contains no token values.
serverlog=Path('/home/jefferson/.local/state/s-core/fabro/score-fabric-3t71eiin/communication1265/server.log')
copy(serverlog,c/'execution'/'server.log')
# Never export server secrets/private database or CLI authentication stores.
private=Path(json.loads((r/'server-binding.json').read_text())['private_state'])
secrets=json.loads((private/'secrets.json').read_text())
for p in c.rglob('*'):
 if p.is_file():assert secrets['token'].encode() not in p.read_bytes(),'Secret found: '+str(p)
checks=[]
for name in ['score_com_concept-test','score_com_concept-macros-unit-tests','score_com_concept-macros-tests']:
 checks.append({'name':name,'target':'//score/mw/com/rust/score_com_concept:'+name,'status':'not_run','reason':'Fabro verify stage failed during storage validation before launching Bazel.'})
for name,reason in [('native-copyright','Dependent planned stage never reached.'),('score-crates-pastey-tests','Upstream crate tests were not part of this consumer run; published assessment sources are not fresh test evidence.'),('qnx','No licensed QNX environment supplied.'),('full-native-ci','Full upstream CI remains pending; no native tests ran.'),('compiler-qualification','Certified compiler/version/target/use-case evidence and adoption require offline engineering review.'),('dependency-advisories','No advisory sweep performed; dated repository metadata does not establish security clearance.'),('native-format','Native formatter inputs are C++/Rust/Python/Starlark; this patch modifies Markdown only.')]:
 checks.append({'name':name,'status':'not_applicable' if name=='native-format' else 'not_run','reason':reason})
final=json.loads((r/'run-final.json').read_text());stages=json.loads((r/'run-stages.json').read_text())['data']
report={'schema_version':1,'kind':'offline_export_of_failed_fabro_run','issue':'eclipse-score/communication#1265','exported_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_id':final['id'],'workflow_version_id':json.loads((r/'workflow-registration.json').read_text())['workflow_version_id'],'native_lifecycle':final['lifecycle']['status'],'stage_statuses':{s['name']:s['status'] for s in stages},'verification_status':'failed_before_native_execution','failure':{'type':'FileNotFoundError','tool':'losetup','cause':'Fabro server/worker PATH=/usr/bin:/bin omits /usr/sbin; shared storage validation cannot launch losetup. No mount-disconnection evidence observed.','raw_logs':['execution/logs/verify-2.log','execution/logs/export-3.log']},'checks':checks,'executed_native_tests':0,'provider_usage':final['usage'],'models':final['models'],'supervisor':'/root/rust_issue_supervisor','corrections_used':3,'max_corrections':3,'retry_disposition':'No further repair, native retry or bypass authorized. Preserve failures and terminate.','binding_discrepancy':'Frozen run-binding.corrections_used_before_execution says2; ledger and actual launch had3. Field is descriptive; collector enforcement reads actual ledger. Retained original binding bytes.','patch_sha256':json.loads((r/'controls.json').read_text())['patch_sha256'],'production_rust_and_locks_unchanged':True,'engineering_acceptance':'pending_offline','upstream_submission':'not_published'}
save(c/'verification-report.json',report)
ledger=json.loads((c/'correction-ledger.json').read_text());ledger['native_run_failures']=1;ledger['failed_native_stages']=['verify','export'];ledger['retry_disposition']='Limit exhausted; stopped without repair/relaunch';save(c/'correction-ledger.json',ledger)
# Local static evidence is measured outside the failed native run; do not represent it as native results.
expected=json.loads((r/'candidate-hashes.json').read_text());actual={n:h(r/'candidate'/n) for n in expected}
assert actual==expected
save(c/'static-verification.json',{'kind':'direct_local_static_measurement','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_subjects':2878,'candidate_subjects':2879,'all_bound_candidate_hashes_match':True,'patch_apply_check':'passed; exact command and result in patch-apply-check.json','production_and_locks_unchanged':True,'native_tests_run':False,'candidate_source_hashes':expected})
workflow=Path('/home/jefferson/s-core_sw_fabric/.agents/skills/score-rust-workflow');shutil.copytree(workflow,c/'workflow'/'score-rust-workflow',dirs_exist_ok=True)
workflow_evidence=Path('/home/jefferson/s-core_sw_fabric/specs/011-change-impact-and-freshness/rust-workflow')
shutil.copytree(workflow_evidence,c/'workflow'/'fabric-validation',dirs_exist_ok=True)
save(c/'provenance.json',{'issue_authority':'authority.json','native_baseline':'e3d126c2d7569345cf5f790310702eb00cd86b06','score_crates_baseline':'4656dda8f04a3d88c8089f63111195840cfbd9e3','source_acquisition':'source-acquisition.json','source_license_retention':'licenses/ and original archives','generic_workflow':'workflow/score-rust-workflow/SKILL.md','generic_workflow_manifest_sha256':'89d006500fb6b2583f682a18c1cd801a98822801839f352e71a7af59cd5010f0','local_artifact_destination':str(c),'storage_binding':'execution/storage-selection.json','verification':'verification-report.json','supervision':'supervisor-review.md','native_test_claims':'none; storage validation prevented execution','omitted_sensitive_artifacts':'private server database, token/CLI auth files and server environment secrets remain internal','external_scratch':str(r),'publishing':'not authorized/not performed'})
print(json.dumps({'native_status':report['native_lifecycle'],'verification_status':report['verification_status'],'corrections_used':3,'candidate_hashes_verified':len(actual),'secret_scan':'passed'}))
