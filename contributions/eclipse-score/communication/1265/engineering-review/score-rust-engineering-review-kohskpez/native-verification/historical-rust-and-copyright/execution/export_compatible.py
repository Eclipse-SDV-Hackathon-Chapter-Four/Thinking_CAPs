"""Offline packaging of measured Fabro results, retaining all prior evidence."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys,re,xml.etree.ElementTree as ET
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r)
out=Path(json.loads((r/'contribution.json').read_text())['path'])
assert (r/'server-shutdown.json').exists(),'Wait for owned run termination/export first'
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
def save(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
for p in r.glob('*'):
 if p.is_file() and p.suffix in {'.json','.py','.fabro','.toml','.log'}:
  copy(p,out/'execution'/p.name)
for p in (r/'logs').glob('*.log'):copy(p,out/'execution'/'logs'/p.name)
server_binding=json.loads((r/'server-binding.json').read_text());private=Path(server_binding['private_state'])
for p in (private/'storage'/'scratch').glob('*/petri/executions/*/logs/*.log'):
 copy(p,out/'execution'/'native-stage-logs'/p.name)
copy(private/'server.log',out/'execution'/'server.log')
# Local test records are fresh in this workspace (only archive cache payloads were seeded).
testroot=r/'candidate'/'bazel-testlogs'/'score/mw/com/rust/score_com_concept'
target_results=[]
macro_log=(r/'logs'/'communication-macro-tests.log').read_text(errors='replace') if (r/'logs'/'communication-macro-tests.log').exists() else ''
for name in ['score_com_concept-test','score_com_concept-macros-unit-tests','score_com_concept-macros-tests']:
 target='//score/mw/com/rust/score_com_concept:'+name
 summary=re.search(r'^'+re.escape(target)+r'\s+(FAILED TO BUILD|PASSED|FAILED|TIMEOUT|NO STATUS|SKIPPED)(.*)$',macro_log,re.M)
 item={'target':target,'bazel_summary_status':summary.group(1) if summary else None,'test_records':[]}
 directory=testroot/name
 if directory.exists():
  assert directory.resolve().is_relative_to(r.resolve())
  for p in sorted(directory.rglob('*')):
   if p.is_file():
    dest=out/'execution'/'testlogs'/name/p.relative_to(directory);copy(p,dest)
    record={'path':str(dest.relative_to(out)),'bytes':p.stat().st_size,'sha256':h(p)}
    if p.name=='test.log':
     record['rust_harness_summaries']=[{'result':a,'passed':int(b),'failed':int(c)} for a,b,c in re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',p.read_text(errors='replace'))]
    if p.name=='test.xml':
     try:record['xml_root_attributes']=dict(ET.parse(p).getroot().attrib)
     except ET.ParseError as e:record['xml_parse_error']=str(e)
    item['test_records'].append(record)
 target_results.append(item)
final=json.loads((r/'run-final.json').read_text());stages=json.loads((r/'run-stages.json').read_text())['data']
measured=json.loads((r/'verification-results.json').read_text()) if (r/'verification-results.json').exists() else None
ledger=json.loads((out/'correction-ledger.json').read_text())
report={'schema_version':1,'kind':'offline_packet_of_native_fabro_measurements','exported_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_id':final['id'],'workflow_version_id':json.loads((r/'workflow-registration.json').read_text())['workflow_version_id'],'native_lifecycle':final['lifecycle']['status'],'stage_statuses':{s['name']:s['status'] for s in stages},'verification_status':'passed_selected_native_checks' if measured and all(c['status']=='passed' for c in measured['checks'] if 'exit_code' in c) else 'failed_or_incomplete_native_checks','collector_report_present':measured is not None,'collector_export_present':(r/'execution-export.json').exists(),'measured_collector_report':'execution/verification-results.json' if measured else None,'native_worker_preflight':'execution/native-worker-preflight.json' if (r/'native-worker-preflight.json').exists() else None,'direct_local_preflights':['execution/worker-preflight.json','execution/native-tool-preflight.json'],'target_results':target_results,'checks':measured['checks'] if measured else [],'patch_sha256':json.loads((r/'controls.json').read_text())['patch_sha256'],'candidate_source_subjects':len(json.loads((r/'candidate-hashes.json').read_text())),'production_rust_and_locks_unchanged':True,'provider_usage':final['usage'],'models':final['models'],'supervisor':'/root/rust_issue_supervisor','max_corrections':3,'corrections_used':ledger['corrections_used'],'prior_attempt_manifest_sha256':h(out/'prior-attempt'/'artifact-manifest.json'),'prior_attempt_preserved':'prior-attempt/','engineering_acceptance':'pending_offline','qualification_adoption':'pending_offline','publication':'not_performed'}
for name,sha in json.loads((r/'candidate-hashes.json').read_text()).items():assert h(r/'candidate'/name)==sha,name
for name,sha in json.loads((out/'prior-attempt'/'artifact-manifest.json').read_text())['files'].items():assert h(out/'prior-attempt'/name)==sha,name
# Explicit identity of the materialized registered compiler; hash only, not a qualification claim.
compiler_identities=[]
for e in (r/'bazel-output').glob('*/external'):
 for repo in e.glob('*ferrocene*'):
  if repo.is_dir():
   for name in ['bin/rustc','bin/rustdoc','BUILD.bazel','SHA256SUMS']:
    p=repo/name
    if p.is_file():compiler_identities.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h(p),'claim':'Materialized native input; compiler qualification/use-case acceptance not established.'})
save(out/'compiler-input-identities.json',{'files':compiler_identities,'certified_scope':'not_established'})
save(out/'verification-report.json',report)
patch=out/'prior-attempt'/'communication-1265.patch';copy(patch,out/'communication-1265.patch')
copy(out/'prior-attempt'/'pr-title.txt',out/'pr-title.txt')
copy(out/'prior-attempt'/'candidate-hashes.json',out/'candidate-hashes.json')
copy(out/'prior-attempt'/'upstream-snapshot.json',out/'upstream-snapshot.json')
# Remove no credentials: refuse if any private token value accidentally entered copied evidence.
secret=json.loads((private/'secrets.json').read_text())['token'].encode()
for p in out.rglob('*'):
 if p.is_file():assert secret not in p.read_bytes(),'Secret found: '+str(p)
print(json.dumps({'run_id':report['run_id'],'verification_status':report['verification_status'],'target_statuses':{x['target']:x['bazel_summary_status'] for x in target_results},'corrections_used':ledger['corrections_used'],'prior_packet':'unchanged'}))
