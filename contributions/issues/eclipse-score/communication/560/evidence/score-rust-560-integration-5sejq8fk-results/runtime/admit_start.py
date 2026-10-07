from pathlib import Path
import json,subprocess,urllib.request,hashlib,shutil
from datetime import datetime,timezone
from score_sw_fabric.storage import validate_run_root
R=Path(__file__).parent;J=R/'jobs/560';W=R/'workspaces/560'
validate_run_root(R)
b=json.loads((R/'server-binding.json').read_text());priv=Path(b['private_state']);token=json.loads((priv/'operator-secret.json').read_text())['token']
q=json.loads((R/'queue.json').read_text());job=q['jobs'][0];rid=job['run_id']
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def request(method,path,body=None):
 req=urllib.request.Request(b['url']+'/api/v1'+path,method=method,data=None if body is None else json.dumps(body).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as f:return json.load(f)
state=request('GET','/runs/'+rid);assert state['lifecycle']['status']['kind']=='submitted'
assert not (J/'start-intent.json').exists(),'Never resend start without reconciling native state'
date=state['timestamps']['created_at'][:10].replace('-','')
scope=priv/'storage/scratch'/(date+'-'+rid)/'petri'
native=scope/'scopes/invocation-0-scope-0/work';native.parent.mkdir(parents=True,exist_ok=True)
assert not native.exists() and not native.is_symlink();native.symlink_to(W,target_is_directory=True)
snapshot=scope/'snapshots/invocation-0-scope-0.git';snapshot.parent.mkdir(parents=True,exist_ok=True)
p=subprocess.run(['git','-c','core.hooksPath=/dev/null','init','--bare',str(snapshot)],capture_output=True);assert p.returncode==0
subprocess.run(['git','--git-dir',str(snapshot),'config','receive.shallowUpdate','true'],check=True)
subprocess.run(['git','--git-dir',str(snapshot),'config','core.hooksPath','/dev/null'],check=True)
save(J/'native-workspace-binding.json',{'run_id':rid,'native_path':str(native),'workspace':str(W),'snapshot_repository':str(snapshot),'baseline':q['baseline'],'clone_enabled':False,'snapshot_receive_shallow_update':True,'running_queue_migrated':False})
PLAN=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue/score-rust-560-integration-plan-bqfe04r8-v2');shutil.copytree(PLAN,W/'.rust-queue/context/integration-plan',dirs_exist_ok=True)
subprocess.run(['/home/jefferson/s-core_sw_fabric/.venv/bin/python',str(R/'driver_linux.py'),'preflight','560'],check=True)
save(J/'native-state-before-start.json',request('GET','/runs/'+rid+'/state'))
save(J/'start-intent.json',{'authority':'user go using fabro and deepseek-flash run','run_id':rid,'request_sent_once':True,'historical_used':2,'remaining':1,'new_isolated_run':True,'old_run_restarted':False,'recorded_at':datetime.now(timezone.utc).isoformat()})
try:
 response=request('POST','/runs/'+rid+'/start',{})
 save(J/'start-response.json',response)
except Exception as exc:
 save(J/'start-transport-observation.json',{'error_type':type(exc).__name__,'reconcile_before_retry':True});raise
q.update(status='linux_execution_requested',issue_start_requests=1,native_execution_ready=True,provider_credential_status='DeepSeek key in isolated private native vault; model DeepSeek Flash only')
job.update(start_requested=True,status='runnable');save(R/'queue.json',q)
print(json.dumps({'run_id':rid,'status':'start requested once','provider':'deepseek','model':'deepseek-flash','final_correction':3,'server':b['url']}))
