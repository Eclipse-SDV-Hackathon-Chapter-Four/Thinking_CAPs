"""Single admission/start; native Fabro owns run state and wait lifecycle."""
from pathlib import Path
import hashlib,json,os,secrets,socket,subprocess,sys,time,urllib.request
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,private_server_root,build_environment
r=Path(__file__).parent;validate_run_root(r)
attempt=r
private=private_server_root(r,'communication1265_linux_integration');fabro='/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro'
def save(name,obj):
 (attempt/name).write_text(json.dumps(obj,indent=2)+'\n')
assert not (attempt/'run-intent.json').exists(),'Do not duplicate native admission'
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
url=f'http://127.0.0.1:{port}'
token='fabro_dev_'+secrets.token_hex(32)
secret=private/'secrets.json';secret.write_text(json.dumps({'token':token}));secret.chmod(0o600)
config=private/'settings.toml'
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
env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','HOME':'/home/jefferson','USER':'jefferson','LANG':'C.UTF-8','FABRO_HOME':str(private),'FABRO_DEV_TOKEN':token,'SESSION_SECRET':secrets.token_hex(32),'FABRO_HTTP_PROXY_POLICY':'disabled','FABRO_NO_UPGRADE_CHECK':'true',**build_environment(r)}
log=(private/'server.log').open('wb')
server=subprocess.Popen([fabro,'--no-upgrade-check','server','start','--foreground','--no-web','--bind',f'127.0.0.1:{port}','--storage-dir',str(private/'storage'),'--config',str(config),'--max-concurrent-runs','1'],env=env,cwd=r,stdout=log,stderr=subprocess.STDOUT)
save('server-binding.json',{'url':url,'pid':server.pid,'private_state':str(private),'config_sha256':hashlib.sha256(config.read_bytes()).hexdigest(),'fabro_binary':fabro,'fabro_sha256':hashlib.sha256(Path(fabro).read_bytes()).hexdigest(),'provider_credentials_inherited':False,'supervisor':'/root/rust_issue_supervisor','max_corrections':3})
def request(method,path,body=None):
 payload=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request(url+path,data=payload,method=method,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
 except urllib.error.HTTPError as exc:
  save('http-error-'+str(exc.code)+'.json',{'method':method,'path':path,'status':exc.code,'body':exc.read().decode('utf-8',errors='replace')});raise
try:
 deadline=time.monotonic()+20
 while True:
  try:request('GET','/api/v1/runs');break
  except Exception:
   if server.poll() is not None or time.monotonic()>deadline:raise
   time.sleep(.25)
 validate_run_root(r)
 version=request('POST','/api/v1/workflow-versions',json.loads((attempt/'workflow-version.json').read_text()));save('workflow-registration.json',version)
 intent={'workflow_version_id':version['workflow_version_id'],'target':{'kind':'folder','path':str(r/'candidate')},'environment_id':'default','title':'Communication #1265: Linux Rust COM integration','goal':'Measure pinned native checks and export complete results; offline acceptance remains pending','args':{'labels':{'score_issue':'communication1265','supervisor':'rust_issue_supervisor','max_corrections':'3'},'auto_approve':False,'dry_run':False}}
 save('run-intent.json',{'state':'create_sent_once','intent':intent})
 created=request('POST','/api/v1/runs',intent);save('run-created.json',created)
 run_id=created['id'];save('run-start-intent.json',{'state':'start_sent_once','run_id':run_id})
 started=request('POST',f'/api/v1/runs/{run_id}/start',{});save('run-started.json',started)
 # CLI auth store is confined to private FABRO_HOME; no credential enters exported artifacts.
 login=subprocess.run([fabro,'--no-upgrade-check','auth','login','--server',url,'--dev-token',token],env=env,cwd=r,capture_output=True)
 (private/'login.log').write_bytes(login.stdout+login.stderr);assert login.returncode==0,'Private CLI authentication failed'
 print(json.dumps({'run_id':run_id,'workflow_version_id':version['workflow_version_id'],'supervisor':'/root/rust_issue_supervisor'}),flush=True)
 with (attempt/'fabro-wait.log').open('wb') as stream:
  wait=subprocess.run([fabro,'--no-upgrade-check','wait',run_id,'--server',url,'--timeout','3900','--json'],env=env,cwd=r,stdout=stream,stderr=subprocess.STDOUT)
 save('fabro-wait-result.json',{'exit_code':wait.returncode})
 for endpoint,name in [('', 'run-final.json'),('/stages','run-stages.json')]:
  try:save(name,request('GET',f'/api/v1/runs/{run_id}'+endpoint))
  except Exception as exc:save(name,{'export_error':type(exc).__name__,'message':str(exc)})
 cursor=0;pages=[];all_events=[]
 while True:
  page=request('GET',f'/api/v1/runs/{run_id}/events?limit=1000&after={cursor}')
  pages.append(page);all_events.extend(page['data'])
  if not page['meta']['has_more']:break
  next_cursor=page['data'][-1]['stream_seq'];assert next_cursor>cursor,'Event cursor made no progress';cursor=next_cursor
 save('run-events.json',{'data':all_events,'meta':{'has_more':False},'pages':len(pages),'event_contract_version':pages[0]['event_contract_version']})
 save('run-event-pages.json',{'pages':pages})
 print(json.dumps({'run_id':run_id,'wait_exit_code':wait.returncode,'report_exists':(attempt/'verification-results.json').exists()}),flush=True)
finally:
 server.terminate()
 try:server.wait(timeout=15)
 except subprocess.TimeoutExpired:server.kill();server.wait()
 log.close()
 save('server-shutdown.json',{'pid':server.pid,'exit_code':server.returncode,'owned_server_stopped':True})

 shutdown=subprocess.run([sys.executable,str(r/'runtime_manager.py'),'stop'],env=env,cwd=r,capture_output=True)
 save('runtime-shutdown-result.json',{'exit_code':shutdown.returncode,'stdout':shutdown.stdout.decode(errors='replace'),'stderr':shutdown.stderr.decode(errors='replace')})
