"""Register/start a pinned native phase, with explicit title and parent link."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from native_measure import P, R, guard, write

SERVER='http://127.0.0.1:43916'
AUTH=Path('/home/jefferson/.local/state/s-core/fabro/someip84-server/cli-auth.json')
B='/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro'
def api(route,body):
    token=json.loads(AUTH.read_text())['servers'][SERVER]['token']
    req=urllib.request.Request(SERVER+route,data=json.dumps(body,ensure_ascii=False,separators=(',',':')).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=45) as response:return json.load(response)
def main():
    phase=sys.argv[1];folder=P/'phases'/phase;guard()
    if (folder/'run-intent.json').exists():raise ValueError('Already attempted registration; inspect receipt instead of duplicating')
    env={**os.environ,'HOME':'/home/jefferson/.local/state/s-core/fabro/someip84-server/home','FABRO_AUTH_FILE':str(AUTH),'FABRO_SERVER':SERVER,'FABRO_NO_UPGRADE_CHECK':'true'}
    for label,args in [('validate',['--json','validate',str(folder/'workflow/workflow.toml')]),('preflight',['--json','preflight',str(folder/'workflow/workflow.toml'),'--environment','local','--model','deepseek-flash','--provider','deepseek'])]:
        result=subprocess.run([B,*args],env=env,cwd=folder,capture_output=True,text=True,timeout=45)
        (folder/(label+'.stdout')).write_text(result.stdout);(folder/(label+'.stderr')).write_text(result.stderr)
        if result.returncode:raise RuntimeError(label+' failed: '+result.stderr[:500])
    version={'entrypoint':'workflow.fabro','files':{str(f.relative_to(folder/'workflow')):f.read_text() for f in sorted((folder/'workflow').rglob('*')) if f.is_file()},'workflow_dependencies':{}}
    raw=json.dumps(version,ensure_ascii=False,separators=(',',':')).encode();expected=hashlib.sha256(raw).hexdigest()
    (folder/'native-workflow-version.json').write_bytes(raw)
    registered=api('/api/v1/workflow-versions',version);write(folder/'workflow-registration.json',registered)
    if registered['workflow_version_id']!=expected:raise ValueError('Native canonical workflow ID mismatch')
    parent=(P.parent/'native-run-id').read_text().strip()
    intent={'workflow_version_id':expected,'target':{'kind':'folder','path':str(R/'runtime-target')},'environment_id':'local','parent_id':parent,
       'title':'Communication bug queue recovery: '+phase+'; '+('zero model calls' if phase=='evidence' else 'one combined Flash correction'),
       'args':{'model':'deepseek-flash','provider':'deepseek','auto_approve':False,'labels':{'project':'s-core_sw_fabric','task':'communication-bug-queue-recovery-'+phase,'model_policy':'flash-only','total_budget_usd':'10'}}}
    write(folder/'run-intent.json',intent);created=api('/api/v1/runs',intent);write(folder/'native-created-run.json',created)
    identifier=created['id'];(folder/'native-run-id').write_text(identifier+'\n')
    state=json.loads((P.parent/'state.json').read_text());write(folder/'prior-queue-state.json',state)
    state.update(status='recovering_'+phase,active_run_id=identifier,runs=list(dict.fromkeys(state.get('runs',[])+[parent,identifier])),
          notes='User authorized recovery. Original failures retained. '+('Native evidence refresh; zero paid calls.' if phase=='evidence' else 'One combined Flash correction; all calls together bounded below $10, including possible unreported retries.'))
    write(P.parent/'state.json',state)
    result=subprocess.run([B,'--json','start',identifier],env=env,cwd=folder,capture_output=True,text=True,timeout=30)
    (folder/'start.stdout').write_text(result.stdout);(folder/'start.stderr').write_text(result.stderr)
    if result.returncode:raise RuntimeError('Native start failed')
    print(json.dumps({'phase':phase,'run_id':identifier,'paid_stages_max':0 if phase=='evidence' else 1}))
if __name__=='__main__':main()
