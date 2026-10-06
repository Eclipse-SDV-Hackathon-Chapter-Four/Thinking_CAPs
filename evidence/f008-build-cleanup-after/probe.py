from pathlib import Path
import hashlib,importlib.util,json,os,signal,subprocess,tempfile,time,uuid
root=Path.cwd();out=root/'evidence/f008-build-cleanup-after';out.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('reproduction',root/'scripts/reproduce_core.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
image='sha256:71efeddcfec43b336a4f4a22b2cc9a73c99b11bd44fe8c657c8c8b210b73e78c';checks=[]
def check(name,valid,details=None):
 row={'id':name,'status':'passed' if valid else 'failed'}
 if details is not None:row['details']=details
 checks.append(row);assert valid,name

def exists(name):
 return subprocess.run(['docker','inspect','--format','{{.State.Running}}',name],capture_output=True,text=True)

def manual_cleanup(name,owner):
 p=subprocess.run(['docker','inspect','--format','{{index .Config.Labels "sdv.reproduction.run"}}',name],capture_output=True,text=True)
 if p.returncode==0:
  assert p.stdout.strip()==owner,'Probe refuses deleting any other container'
  subprocess.run(['docker','rm','-f',name],check=True,stdout=subprocess.PIPE)

identity=uuid.uuid4().hex;name='sdv-repro-cleanup-probe-'+identity[:10]
try:
 try:
  m.run_owned_command(['docker','run','--rm','--sig-proxy=false','--name',name,'--label','sdv.reproduction.run='+identity,'--network','none','--entrypoint','sleep',image,'40'],1,out/'timeout-output.txt')
 except subprocess.TimeoutExpired:timed_out=True
 else:timed_out=False
 p=exists(name);check('actual-timeout-before-container-finalization',timed_out and p.returncode==0 and p.stdout.strip()=='true')
 result=m.cleanup_build_container(name,identity);check('ownership-checked-timeout-removal',result['status']=='passed' and exists(name).returncode!=0,result)
 result=m.cleanup_build_container(name,identity);check('already-absent-is-success',result['status']=='passed',result)
finally:manual_cleanup(name,identity)

identity=uuid.uuid4().hex;name='sdv-repro-other-probe-'+identity[:10];owner='other-'+identity
try:
 subprocess.run(['docker','run','-d','--rm','--name',name,'--label','sdv.reproduction.run='+owner,'--network','none','--entrypoint','sleep',image,'40'],check=True,stdout=subprocess.PIPE)
 result=m.cleanup_build_container(name,identity);p=exists(name)
 check('unowned-container-refused-and-retained',result['status']=='failed' and result['reason']=='refuse removing unowned build container' and p.returncode==0 and p.stdout.strip()=='true',result)
finally:manual_cleanup(name,owner)

source='import subprocess,time;print(subprocess.Popen(["/usr/bin/python3","-c","import time;time.sleep(40)"]).pid,flush=True);time.sleep(40)'
try:m.run_owned_command(['/usr/bin/python3','-c',source],.5,out/'process-tree-output.txt')
except subprocess.TimeoutExpired:timed_out=True
else:timed_out=False
pid=int((out/'process-tree-output.txt').read_text().strip());stat=Path('/proc')/str(pid)/'stat';state=stat.read_text().split()[2] if stat.exists() else 'absent'
check('timeout-terminates-owned-child-process',timed_out and state in ('Z','X','absent'),{'child_pid':pid,'observed_state':state,'limit':'A terminated zombie is not claimed to be reaped by host init'})

with tempfile.TemporaryDirectory(prefix='sdv-reproduction-signal-') as td:
 td=Path(td);binpath=td/'bin';binpath.mkdir();marker=td/'rustc.pid'
 shim=binpath/'rustc';shim.write_text('#!/usr/bin/python3\nfrom pathlib import Path\nimport os,time\nPath('+repr(str(marker))+').write_text(str(os.getpid()))\nprint("owned compiler-wait fixture",flush=True)\ntime.sleep(40)\n');shim.chmod(0o700)
 cfg=td/'config.json';cfg.write_text('{}\n')
 for signum in (signal.SIGINT,signal.SIGTERM):
  marker.unlink(missing_ok=True);evidence=out/signal.Signals(signum).name;proc=None
  try:
   env=dict(os.environ);env['PATH']=str(binpath)+os.pathsep+env['PATH']
   cmd=['/usr/bin/python3',str(root/'scripts/reproduce_core.py'),'--config',str(cfg),'--state',str(td/signal.Signals(signum).name),'--output',str(evidence),'--operator','implementation agent signal-path validation','--shared-host']
   proc=subprocess.Popen(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
   deadline=time.monotonic()+10
   while not marker.exists():
    if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Signal fixture did not reach owned compiler wait')
    time.sleep(.05)
   child=int(marker.read_text());os.kill(proc.pid,signum);output=proc.communicate(timeout=15)[0];record=json.loads((evidence/'manifest.json').read_text());stat=Path('/proc')/str(child)/'stat';state=stat.read_text().split()[2] if stat.exists() else 'absent'
   check(signal.Signals(signum).name+'-explicit-failure-and-child-stop',proc.returncode==128+signum and record['status']=='failed' and record['interrupted_signal']==signal.Signals(signum).name and record['build_container_cleanup']['status']=='skipped' and state in ('Z','X','absent'),{'exit_code':proc.returncode,'child_state':state,'scope':'Actual helper interrupted at controlled compiler-wait fixture before native build'})
   (evidence/'invocation.json').write_text(json.dumps({'command':cmd,'exit_code':proc.returncode,'output':output.decode()},indent=2)+'\n')
  finally:
   if proc and proc.poll() is None:
    os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
   if marker.exists():
    child=int(marker.read_text())
    try:os.killpg(child,signal.SIGKILL)
    except ProcessLookupError:pass

 for name,value in [('malformed','{'),('wrong-root','[]')]:
  cfg.write_text(value);evidence=out/name
  result=subprocess.run(['/usr/bin/python3',str(root/'scripts/reproduce_core.py'),'--config',str(cfg),'--state',str(td/name),'--output',str(evidence)],text=True,capture_output=True,timeout=10)
  record=json.loads((evidence/'manifest.json').read_text())
  check(name+'-config-produces-failed-manifest',result.returncode==1 and record['status']=='failed' and record['build_container_cleanup']['status']=='skipped')

record={'status':'passed','scope':'Actual isolated Docker ownership/timeout, process-group child termination and controlled helper signal/config failure paths; not native build acceptance','producer_sha256':hashlib.sha256((root/'scripts/reproduce_core.py').read_bytes()).hexdigest(),'checks':checks}
(out/'verification.json').write_text(json.dumps(record,indent=2)+'\n');(out/'probe.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(record,indent=2))
