"""Read-only measurement validation and additive terminal evidence export."""
import hashlib,json,pathlib,re,subprocess,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timezone
P=pathlib.Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167'); Q=P/'final-review'; D=Q/'verification-run'
R=pathlib.Path((Q/'new-scratch-root').read_text().strip()); ID=(D/'current-native-run-id').read_text().strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def load(p):return json.loads(p.read_text())
server='http://127.0.0.1:43916';auth=load(pathlib.Path('/home/jefferson/.local/state/s-core/fabro/someip84-server/cli-auth.json'))['servers'][server]['token']
def get(url,private=False):
 req=urllib.request.Request(url,headers={'Authorization':'Bearer '+auth} if private else {})
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
for name,route in [('state','/state'),('summary',''),('stages','/stages?page%5Blimit%5D=100')]:
 v=get(server+'/api/v1/runs/'+ID+route,True);write(D/('final-native-'+name+'.json'),v)
assert load(D/'final-native-state.json')['status']['kind']=='succeeded'
from score_sw_fabric.storage import validate_run_root
validate_run_root(R)
mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(R),'-o','SOURCE,UUID'],text=True))['filesystems'][0]
assert mount['source']=='/dev/loop1' and mount['uuid']=='11c42dee-73a3-4c2b-ab42-a0440011d9e0'
bind=load(D/'candidate-hashes.json'); checks={}
for root,binding in [(D/'candidate',bind),(R/'native-workspace',bind),(P/'candidate',load(P/'candidate-hashes.json')),(P/'review-correction/verification-run/candidate',load(P/'review-correction/verification-run/candidate-hashes.json'))]:
 assert all(sha(root/rel)==h for rel,h in binding.items()),str(root)
checks['source_sets']={'current_candidate':len(bind),'native_workspace':len(bind),'original_preserved':len(load(P/'candidate-hashes.json')),'predecessor_preserved':len(load(P/'review-correction/verification-run/candidate-hashes.json'))}
frozen=load(D/'frozen-inputs.json');assert all(sha(D/rel)==h for rel,h in frozen.items());checks['frozen_inputs']=len(frozen)
results={}
for name in ['copyright','format','focused','build-all','test-all']:
 v=load(D/'evidence'/f'{name}.json');assert v['subject_sha256']==bind and v['fabro_run_id']==ID
 for stream in ['stdout','stderr']:assert sha(D/'evidence'/f'{name}.{stream}')==v[stream+'_sha256']
 assert v['exit_code']==(1 if name=='copyright' else 0)
 results[name]={'exit_code':v['exit_code'],'elapsed_seconds':round(v['finished_at_epoch']-v['started_at_epoch'],3)}
manifest=load(D/'native-artifacts/manifest.json');assert manifest['source_sha256']==sha(D/'candidate-hashes.json') and not manifest['missing_products']
for rel,v in manifest['files'].items():
 f=D/'native-artifacts'/rel;assert sha(f)==v['sha256'] and f.stat().st_size==v['bytes'] and v['run_id']==ID
 if '/blobs/sha256/' in rel:assert f.name==v['sha256']
checks['native_products']=len(manifest['files']);checks['oci_files']=sum(x.startswith('api_idempotency_test.oci/') for x in manifest['files'])
log=(D/'evidence/test-all.stdout').read_text();assert 'Executed 503 out of 509 tests: 503 tests pass and 6 were skipped.' in log
skips=re.findall(r'^(//\S+)\s+SKIPPED$',log,re.M);assert skips==load(P/'follow-up/skipped-tests.json')['skipped_targets']
write(D/'skipped-tests.json',{'source':'evidence/test-all.stdout','sha256':sha(D/'evidence/test-all.stdout'),'skipped_targets':skips,'declaration_context':'../../../resume-review/REVIEW.md','acceptance':'pending'})
cases=[]; xml=D/'evidence/native-testlogs/score/mw/com/impl/bindings/lola/service_discovery/client/service_discovery_client_test/test.xml';tree=ET.parse(xml)
for name in [x['name'] for x in load(Q/'prior-native-case-correspondence.json')['cases']]+['CallingStartFindServiceOnOfferedServiceTwiceWithTheSameIdentifierCallsBothHandlers']:
 matches=[x for x in tree.iter('testcase') if x.get('name')==name];assert len(matches)==1,name
 x=matches[0];assert not any(x.find(tag) is not None for tag in ['failure','error','skipped'])
 cases.append({'name':name,'class':x.get('classname'),'record':str(xml.relative_to(Q)),'sha256':sha(xml),'failed':False,'skipped':False})
write(Q/'native-case-correspondence.json',{'status':'fresh_native_full_suite_cases_passed','run_id':ID,'source_binding':'verification-run/candidate-hashes.json','cases':cases})
app=D/'evidence/native-testlogs/score/mw/com/test/api_idempotency/integration_test/api_idempotency_test/test.log'; assert 'Application [main_api_idempotency] exit code: [0]' in app.read_text()
checks['fresh_check_results']=results;checks['full_suite']={'passed':503,'failed':0,'skipped':6};checks['application_exit_code']=0;checks['application_exit_record']={'path':str(app.relative_to(Q)),'sha256':sha(app)}
comparison=load(D/'copyright-comparison.json');assert comparison['identical_normalized_findings'] and comparison['candidate_count']==204 and not comparison['candidate_only_findings']
checks['copyright']={'count':204,'added':0,'measurement':'failed','classification':'pre_existing_baseline_with_checker_path_overlay'}
for name,args in [('issue-1167-tests.patch',['score/mw/com/test/api_idempotency']),('copyright-checker-paths.patch',['BUILD'])]:
 result=subprocess.run(['git','-C',str(D/'candidate'),'-c','core.hooksPath=/dev/null','diff','--binary','--',*args],capture_output=True,check=True);assert result.stdout
 (D/name).write_bytes(result.stdout)
# Frozen/exported metadata retained as measured. Correct nested-packet reference resolution additively.
write(Q/'reference-resolution.json',{'preserve_original_metadata':True,'references':[{'record':'verification-run/configuration.json','field':'device_reconciliation','actual':'../review-correction/storage-reconciliation.json','sha256':sha(P/'review-correction/storage-reconciliation.json')},{'record':'verification-run/copyright-comparison.json','field':'baseline_record','actual':'../follow-up/copyright-comparison.json','sha256':sha(P/'follow-up/copyright-comparison.json')}]})
detail=get('http://127.0.0.1:8787/api/runs/someip/'+ID);graph=get('http://127.0.0.1:8787/api/runs/someip/'+ID+'/graph');assert graph['svg']
with urllib.request.urlopen('http://172.18.17.0:8787',timeout=10) as response:assert response.status==200
write(Q/'dashboard-reverification.json',{'application':'fabro_dashboard','service':'fabro-monitor.service','url':'http://172.18.17.0:8787','http_status':200,'run_id':ID,'run_visible':True,'run_status':detail['run'].get('status'),'graph_available':True,'source':'someip','native_api_url':server,'dashboard_code_or_configuration_changed':False,'credentials_exported':False})
checks['status']='all_bound_source_controls_logs_and_products_verified';checks['run_id']=ID;checks['time_utc']=datetime.now(timezone.utc).isoformat();write(Q/'final-binding-verification.json',checks)
print(json.dumps(checks,indent=2))
