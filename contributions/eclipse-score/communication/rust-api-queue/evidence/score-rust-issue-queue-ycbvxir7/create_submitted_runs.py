"""Submit prepared runs to the already-owned queue server; never start them."""
import json
import urllib.request
import urllib.error
from pathlib import Path
from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).parent
validate_run_root(ROOT)
binding=json.loads((ROOT/'server-binding.json').read_text())
private=Path(binding['private_state'])
token=json.loads((private/'operator-secret.json').read_text())['token']
url=binding['url']


def save(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def request(method,path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url+path,data=data,method=method,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
    except urllib.error.HTTPError as error:
        save(ROOT/'last-http-refusal.json',{'method':method,'path':path,'status':error.code,'body':error.read().decode(errors='replace')})
        raise


queue=json.loads((ROOT/'queue.json').read_text())
pending=list(queue['jobs']);ordered=[]
while pending:
    candidates=[j for j in pending if all(d in [x['issue'] for x in ordered] for d in j['prerequisites_to_verify'])]
    assert candidates,'Issue prerequisite cycle'
    job=candidates[0];pending.remove(job);ordered.append(job)

for order,job in enumerate(ordered,1):
    validate_run_root(ROOT)
    folder=Path(job['job_root'])
    if (folder/'run-created.json').exists():
        created=json.loads((folder/'run-created.json').read_text())
        observed=request('GET','/api/v1/runs/'+created['id'])
        save(folder/'native-run-projection.json',observed)
        continue
    assert not (folder/'create-intent.json').exists(),'Create may have been sent; reconcile native state before any duplicate attempt'
    if (folder/'workflow-registration.json').exists():
        version=json.loads((folder/'workflow-registration.json').read_text())
    else:
        version=request('POST','/api/v1/workflow-versions',json.loads((folder/'workflow-version.json').read_text()))
        save(folder/'workflow-registration.json',version)
    intent={'workflow_version_id':version['workflow_version_id'],'target':{'kind':'folder','path':job['workspace']},'environment_id':'default','title':'Rust API #'+str(job['issue'])+': '+job['title'],'goal':job['title']+'; baseline '+queue['baseline']+'; Linux only; DeepSeek Flash only; preserve failed/missing evidence and pending offline acceptance','args':{'model':'deepseek-flash','provider':'deepseek','auto_approve':False,'dry_run':False,'preserve_sandbox':True,'labels':{'queue_id':queue['queue_id'],'issue':str(job['issue']),'queue_order':str(order),'model_policy':'deepseek_flash_only','supervisor':'deepseek-flash','max_source_corrections':str(job['max_source_corrections']),'mode':job['mode']}}}
    save(folder/'create-intent.json',{'state':'create_sent_once','intent':intent,'start':False})
    created=request('POST','/api/v1/runs',intent)
    save(folder/'run-created.json',created)
    observed=request('GET','/api/v1/runs/'+created['id'])
    save(folder/'native-run-projection.json',observed)
    job.update(run_id=created['id'],workflow_version_id=version['workflow_version_id'],submission_order=order,status='submitted_not_started')
    save(ROOT/'queue.json',queue)
    print(json.dumps({'issue':job['issue'],'run_id':created['id'],'state':'submitted_not_started','model':'deepseek-flash'}),flush=True)
queue.update(status='submitted_not_started',server_url=url,submitted_count=len(ordered),start_requests=0,model_calls_requested=0,provider_credential_status='DeepSeek credential configured in isolated internal vault; native catalogue configured=true; no live provider request',native_execution_ready=False)
save(ROOT/'queue.json',queue)
save(ROOT/'native-runs-page.json',request('GET','/api/v1/runs'))
print(json.dumps({'submitted':len(ordered),'started':0,'server':url,'provider':'deepseek','model':'deepseek-flash','fallbacks':[]},indent=2),flush=True)
