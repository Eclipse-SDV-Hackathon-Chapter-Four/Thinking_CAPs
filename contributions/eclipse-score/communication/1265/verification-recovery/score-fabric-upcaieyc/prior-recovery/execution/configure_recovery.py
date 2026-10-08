from pathlib import Path
import json,subprocess,os,shutil,hashlib,urllib.request,datetime,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,build_environment
r=Path(__file__).parent;validate_run_root(r);out=Path(json.loads((r/'contribution.json').read_text())['path'])
path='/usr/sbin:/usr/bin:/sbin:/bin'
for name in ['collector.py','run_native.py']:
 p=r/name;p.write_text(p.read_text().replace("'PATH':'/usr/bin:/bin'",f"'PATH':'{path}'"))
p=r/'run_native.py';s=p.read_text().replace("'communication1265');fabro=","'communication1265_recovery');fabro=")
s=s.replace('Communication #1265: supervised pastey assessment verification','Communication #1265: supervised verification recovery')
s=s.replace('provider = "local"\n\'\'\'','provider = "local"\n[environments.default.env]\nPATH = "'+path+'"\n\'\'\'')
s=s.replace("try:save(name,request('GET',f'/api/v1/runs/{run_id}'+endpoint))","try:save(name,request('GET',f'/api/v1/runs/{run_id}'+endpoint))")
# HTTP errors must retain the native response body, rather than losing the useful diagnostic.
s=s.replace('with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)',"try:\n  with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)\n except urllib.error.HTTPError as exc:\n  save('http-error-'+str(exc.code)+'.json',{'method':method,'path':path,'status':exc.code,'body':exc.read().decode('utf-8',errors='replace')});raise")
p.write_text(s)
p=r/'prepare_run.py';s=p.read_text().replace("on_failure=\"route\"","on_failure=\"exit\"")
s=s.replace('start -> verify;','start -> preflight;\\n preflight -> verify;\\n preflight -> export [condition="outcome=failed"];')
s=s.replace('start [type="start"];\\n verify', 'start [type="start"];\\n preflight [type="command", script=\'+q(f\'{python} {r}/collector.py preflight\')+\', max_retries=0, timeout="1m"];\\n verify')
s=s.replace("'correction_ledger':'/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265/correction-ledger.json'","'correction_ledger':str(Path(json.loads((r/'contribution.json').read_text())['path'])/'correction-ledger.json')")
s=s.replace("'corrections_used_before_execution':2","'corrections_used_before_execution':json.loads((Path(json.loads((r/'contribution.json').read_text())['path'])/'correction-ledger.json').read_text())['corrections_used']")
s=s.replace("'fabro-source-bindings.json']","'fabro-source-bindings.json','run_native.py','worker-preflight.json','tooling-bindings.json']")
p.write_text(s)
p=r/'collector.py';s=p.read_text()
s=s.replace("print('Bound verification export complete; offline engineering acceptance pending.')\n return 0", "print('Bound verification export complete; offline engineering acceptance pending.')\n return 0 if all(c['status']=='passed' for c in report['checks'] if 'exit_code' in c) else 1")
s=s.replace("bind();report=json.loads((ROOT/'verification-results.json').read_text())", "bind()\n if not (ROOT/'verification-results.json').exists():\n  write('execution-export.json',{'verification_results_present':False,'verification_status':'missing_after_preflight_or_collector_failure','all_executed_checks_passed':False,'engineering_acceptance':'pending_offline'});return 1\n report=json.loads((ROOT/'verification-results.json').read_text())")
s=s.replace("if __name__=='__main__':sys.exit(verify() if sys.argv[1]=='verify' else export())", "def preflight():\n bind()\n import shutil\n required=['losetup','lsblk','findmnt','git','bwrap']\n resolved={name:shutil.which(name) for name in required}\n assert all(resolved.values()),resolved\n write('native-worker-preflight.json',{'PATH':os.environ.get('PATH'),'resolved_tools':resolved,'storage_binding_validated':True,'candidate_hashes_validated':True,'provider_calls':0})\n print('Native worker storage/tool/source preflight passed.');return 0\n\nif __name__=='__main__':sys.exit({'verify':verify,'export':export,'preflight':preflight}[sys.argv[1]]())")
p.write_text(s)
# The actual sanitized worker environment is exercised before native admission.
env={'PATH':path,'LANG':'C.UTF-8',**build_environment(r)}
code="import sys,shutil,json;from pathlib import Path;sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src');from score_sw_fabric.storage import validate_run_root;validate_run_root(Path(sys.argv[1]));print(json.dumps({n:shutil.which(n) for n in ['losetup','lsblk','findmnt','git','bwrap']}))"
proc=subprocess.run(['/home/jefferson/s-core_sw_fabric/.venv/bin/python','-c',code,str(r)],env=env,capture_output=True,text=True)
assert proc.returncode==0,proc.stderr
resolved=json.loads(proc.stdout);assert all(resolved.values())
def h(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
record={'kind':'direct_local_worker_environment_measurement','environment':env,'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'storage_binding_validated':True,'resolved_tools':resolved,'changed_PATH_from_prior_run':'/usr/sbin:/usr/bin:/sbin:/bin','native_build_or_tests':False}
(r/'worker-preflight.json').write_text(json.dumps(record,indent=2)+'\n')
(r/'tooling-bindings.json').write_text(json.dumps({'host_tools':{n:{'path':p,'sha256':h(p)} for n,p in resolved.items()},'python':{'path':sys.executable,'version':sys.version},'fabric_storage_source_sha256':h('/home/jefferson/s-core_sw_fabric/src/score_sw_fabric/storage.py'),'fabro_binary_sha256':h('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro'),'bazel_binary_sha256':h(r/'tools/bazel')},indent=2)+'\n')
for endpoint,name in [('https://api.github.com/repos/eclipse-score/communication/issues/1265','issue-current.json'),('https://api.github.com/repos/eclipse-score/communication/commits/HEAD','head-current.json')]:
 req=urllib.request.Request(endpoint,headers={'User-Agent':'score-rust-workflow-verification','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=30) as response:data=json.load(response)
 (r/name).write_text(json.dumps(data,indent=2)+'\n')
issue=json.loads((r/'issue-current.json').read_text());head=json.loads((r/'head-current.json').read_text())
(r/'upstream-observation.json').write_text(json.dumps({'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'issue_state':issue['state'],'issue_updated_at':issue['updated_at'],'current_HEAD':head['sha'],'selected_verification_baseline':'e3d126c2d7569345cf5f790310702eb00cd86b06','baseline_changed_upstream':head['sha']!='e3d126c2d7569345cf5f790310702eb00cd86b06'},indent=2)+'\n')
print(json.dumps({'worker_preflight':'passed','resolved_tools':resolved,'current_HEAD':head['sha'],'issue_state':issue['state'],'root':str(r),'contribution':str(out)}))
