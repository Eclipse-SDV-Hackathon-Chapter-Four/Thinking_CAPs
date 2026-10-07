"""Create submitted native runs on an isolated Fabro instance. Never start runs."""
from __future__ import annotations

import hashlib
import json
import secrets
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from score_sw_fabric.storage import build_environment, private_server_root, validate_run_root

ROOT = Path(__file__).parent
BINARY = Path('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro')
EXPECTED_BINARY = '8d7ef1e66f19a4da4b806ea64944d58ee33652e959f46c142645c4feb7468fbe'
validate_run_root(ROOT)
assert hashlib.sha256(BINARY.read_bytes()).hexdigest() == EXPECTED_BINARY
queue = json.loads((ROOT / 'queue.json').read_text())
assert queue['status'] == 'prepared_not_submitted', 'Inspect native state rather than duplicate queue admission'
assert not (ROOT / 'server-binding.json').exists(), 'Do not replace a prepared/running queue server'
private = private_server_root(ROOT, 'rust_api_queue')
with socket.socket() as listener:
    listener.bind(('127.0.0.1',0))
    port = listener.getsockname()[1]
url = 'http://127.0.0.1:' + str(port)
token = 'fabro_dev_' + secrets.token_hex(32)
secret = private / 'operator-secret.json'
secret.write_text(json.dumps({'token':token})+'\n');secret.chmod(0o600)
config = private / 'settings.toml'
config.write_text('''_version = 1
[server.auth]
methods = ["dev-token"]
[server.sandbox.providers.local]
enabled = true
[server.sandbox.providers.docker]
enabled = false
[server.sandbox.providers.daytona]
enabled = false
[environments.default]
provider = "local"
[environments.default.env]
PATH = "/usr/sbin:/usr/bin:/sbin:/bin"
''');config.chmod(0o600)
env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','HOME':'/home/jefferson','USER':'jefferson','LANG':'C.UTF-8','FABRO_HOME':str(private),'FABRO_DEV_TOKEN':token,'SESSION_SECRET':secrets.token_hex(32),'FABRO_HTTP_PROXY_POLICY':'disabled','FABRO_NO_UPGRADE_CHECK':'true',**build_environment(ROOT)}
log=(private/'server.log').open('ab')
server=subprocess.Popen([str(BINARY),'--no-upgrade-check','server','start','--foreground','--no-web','--bind','127.0.0.1:'+str(port),'--storage-dir',str(private/'storage'),'--config',str(config),'--max-concurrent-runs','1','--model','deepseek-flash','--provider','deepseek'],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
log.close()


def save(path: Path, value: object):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def request(method,path,body=None):
    payload=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url+path,data=payload,method=method,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        save(ROOT/'last-http-refusal.json',{'method':method,'path':path,'status':error.code,'body':error.read().decode(errors='replace')})
        raise


save(ROOT/'server-binding.json',{'url':url,'pid':server.pid,'private_state':str(private),'config_sha256':hashlib.sha256(config.read_bytes()).hexdigest(),'fabro_binary':str(BINARY),'fabro_sha256':EXPECTED_BINARY,'max_concurrent_runs':1,'provider':'deepseek','model':'deepseek-flash','provider_credentials_inherited':False,'existing_servers_and_queues_modified':False,'lifecycle':'keep metadata server available for submitted queue; no run starts issued'})
deadline=time.monotonic()+20
while True:
    try:
        request('GET','/api/v1/runs')
        break
    except Exception:
        if server.poll() is not None or time.monotonic()>deadline:
            raise RuntimeError('Queue server failed; inspect private server.log without printing credentials')
        time.sleep(.25)

# Store CLI login only in this instance's private FABRO_HOME.
login=subprocess.run([str(BINARY),'--no-upgrade-check','auth','login','--server',url,'--dev-token',token],env=env,cwd=ROOT,capture_output=True)
(private/'operator-login.log').write_bytes(login.stdout+login.stderr)
assert login.returncode==0,'Private CLI login refused; no global auth state was changed'

import shlex
key = None
for line in (Path('/home/jefferson/.config/sesn/deepseek.env')).read_text().splitlines():
    for part in shlex.split(line, comments=True):
        if part.startswith('DEEPSEEK_API_KEY='):
            key = part.partition('=')[2]
assert key
credential = subprocess.run([str(BINARY),'--no-upgrade-check','secret','set','DEEPSEEK_API_KEY','--value-stdin','--json'], input=key.encode(), env=env,cwd=ROOT,capture_output=True)
assert credential.returncode == 0, 'Native private vault import failed'
(private/'credential-import-status.json').write_text(json.dumps({'key_name':'DEEPSEEK_API_KEY','exit_code':0,'mechanism':'native secret set --value-stdin','live_model_request':False})+'\n')
del key

catalogue=subprocess.run([str(BINARY),'--no-upgrade-check','model','list','--provider','deepseek','--server',url,'--json'],env=env,cwd=ROOT,capture_output=True,text=True)
save(ROOT/'native-model-catalogue.json',{'exit_code':catalogue.returncode,'stdout':catalogue.stdout,'stderr':catalogue.stderr,'claim':'Native catalogue observation; no live model request or qualification claim'})

# Stable topological submission order for declared prerequisites. Fabro owns the
# actual execution queue; this is one-time preparation, not a runtime scheduler.
pending=list(queue['jobs']);ordered=[]
while pending:
    ready=[job for job in pending if all(dep in [x['issue'] for x in ordered] for dep in job['prerequisites_to_verify'])]
    assert ready,'Issue prerequisite cycle; refuse submission'
    selected=ready[0];pending.remove(selected);ordered.append(selected)

for ordinal, job in enumerate(ordered,1):
    validate_run_root(ROOT)
    folder=Path(job['job_root'])
    assert not (folder/'create-intent.json').exists(),'A create may have been sent; reconcile native state instead of retrying'
    package=json.loads((folder/'workflow-version.json').read_text())
    registered=request('POST','/api/v1/workflow-versions',package)
    save(folder/'workflow-registration.json',registered)
    intent={'workflow_version_id':registered['workflow_version_id'],'target':{'kind':'folder','path':job['workspace']},'environment_id':'default','title':'Rust API #'+str(job['issue'])+': '+job['title'],'goal':job['title']+'; current baseline '+queue['baseline']+'; Linux only; DeepSeek Flash only; preserve missing evidence and pending offline acceptance','args':{'model':'deepseek-flash','provider':'deepseek','auto_approve':False,'dry_run':False,'preserve_sandbox':True,'labels':{'queue_id':queue['queue_id'],'issue':str(job['issue']),'queue_order':str(ordinal),'model_policy':'deepseek_flash_only','supervisor':'deepseek-flash','max_source_corrections':str(job['max_source_corrections']),'mode':job['mode']}}}
    save(folder/'create-intent.json',{'state':'create_sent_once','intent':intent,'start':False})
    created=request('POST','/api/v1/runs',intent)
    save(folder/'run-created.json',created)
    identifier=created['id']
    observed=request('GET','/api/v1/runs/'+identifier)
    save(folder/'native-run-projection.json',observed)
    job.update(run_id=identifier,workflow_version_id=registered['workflow_version_id'],submission_order=ordinal,status='submitted_not_started')
    save(ROOT/'queue.json',queue)
    print(json.dumps({'issue':job['issue'],'run_id':identifier,'state':'submitted_not_started','model':'deepseek-flash'}),flush=True)
queue.update(status='submitted_not_started',server_url=url,submitted_count=len(ordered),start_requests=0,model_calls_requested=0,provider_credential_status='No provider credentials inherited; configure/probe DeepSeek transport before execution',native_execution_ready=False)
save(ROOT/'queue.json',queue)
save(ROOT/'native-runs-page.json',request('GET','/api/v1/runs'))
print(json.dumps({'queue':queue['queue_id'],'submitted':len(ordered),'started':0,'server':url,'model':'deepseek-flash','fallbacks':[]},indent=2),flush=True)
