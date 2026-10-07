from pathlib import Path
import json,urllib.request
from datetime import datetime,timezone
from score_sw_fabric.storage import validate_run_root
R=Path(__file__).parent;validate_run_root(R)
b=json.loads((R/'server-binding.json').read_text());t=json.loads((Path(b['private_state'])/'operator-secret.json').read_text())['token'];rid=json.loads((R/'queue.json').read_text())['jobs'][0]['run_id']
def api(path):
 req=urllib.request.Request(b['url']+'/api/v1'+path,headers={'Authorization':'Bearer '+t})
 with urllib.request.urlopen(req,timeout=15) as f:return json.load(f)
p=api('/runs/'+rid);s=api('/runs/'+rid+'/state')
stages={k:{kk:v for kk,v in x.items() if kk in ['state','started_at','live_inference_ms','live_tool_ms','termination']} for k,x in s['stages'].items()}
folder=R/'workspaces/560/score/mw/com/test/basic_rust_api/subscription_state_apis';files={str(f.relative_to(folder)):f.stat().st_size for f in folder.rglob('*') if f.is_file() and not f.is_symlink()} if folder.exists() else {}
checks=[]
for f in (R/'jobs/560/execution').glob('check-*/native-result.json'):
 x=json.loads(f.read_text());checks.append({'folder':f.parent.name,'passed':x['passed'],'checks':[{k:c[k] for k in ['kind','targets','exit_code','elapsed_seconds']} for c in x['checks']]})
print(json.dumps({'time':datetime.now(timezone.utc).isoformat(),'lifecycle':p['lifecycle'],'models':p['models'],'stages':stages,'new_package_files':files,'native_checks':checks,'conclusion':s['conclusion']},indent=2))
