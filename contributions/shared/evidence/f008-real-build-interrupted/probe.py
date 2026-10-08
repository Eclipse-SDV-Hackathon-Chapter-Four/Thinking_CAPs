from pathlib import Path
import json,os,signal,subprocess,time
root=Path.cwd();state=root/'.local/reproduction-build-signal';out=root/'evidence/f008-real-build-interrupted';proc=None;owned=None
cmd=['/usr/bin/python3',str(root/'scripts/reproduce_core.py'),'--config',str(root/'evidence/f009-reproduction-current/reproduction-inputs.json'),'--state',str(state),'--output',str(out),'--operator','implementation agent native-build cancellation probe','--shared-host']
log=root/'.local/probes/native_build_signal_output.txt'
with log.open('wb') as stream:
 try:
  proc=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
  deadline=time.monotonic()+50
  while owned is None:
   if proc.poll() is not None:raise RuntimeError('Reproducer exited before actual build started')
   if time.monotonic()>deadline:raise RuntimeError('Native build did not start within probe bound')
   ids=subprocess.check_output(['docker','ps','--filter','label=sdv.reproduction.run','--no-trunc','--format','{{.ID}}']).decode().splitlines()
   for identifier in ids:
    info=json.loads(subprocess.check_output(['docker','inspect',identifier]))[0]
    if any(m.get('Source')==str(state/'score') and m.get('Destination')=='/home/source' for m in info.get('Mounts',[])):
     owned={'container_id':identifier,'name':info['Name'],'run_id':info['Config']['Labels']['sdv.reproduction.run'],'running':info['State']['Running']};break
   if owned is None:time.sleep(.2)
  # The process is inside the actual native build container, not a simulated compiler.
  os.kill(proc.pid,signal.SIGTERM);proc.wait(timeout=60)
  manifest=json.loads((out/'manifest.json').read_text())
  remaining=subprocess.check_output(['docker','ps','-a','--filter','label=sdv.reproduction.run='+owned['run_id'],'--format','{{.Names}}']).decode().strip().splitlines()
  passed=proc.returncode==143 and manifest['status']=='failed' and manifest['interrupted_signal']=='SIGTERM' and manifest['build_container_cleanup']['status']=='passed' and manifest['ownership_container_cleanup']['status']=='passed' and not remaining
  record={'status':'passed' if passed else 'failed','scope':'Actual native build started and deliberately cancelled; failed build verdict retained, ownership-checked finalization verified. No completed native build claim.','command':cmd,'exit_code':proc.returncode,'observed_owned_build':owned,'build_container_cleanup':manifest['build_container_cleanup'],'ownership_container_cleanup':manifest['ownership_container_cleanup'],'owned_containers_remaining':remaining}
  (out/'verification.json').write_text(json.dumps(record,indent=2)+'\n');(out/'probe.py').write_bytes(Path(__file__).read_bytes());(out/'driver-output.txt').write_bytes(log.read_bytes());print(json.dumps(record,indent=2));assert passed
 finally:
  if proc and proc.poll() is None:
   os.kill(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=45)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
  if owned:
   found=subprocess.run(['docker','inspect','--format','{{index .Config.Labels "sdv.reproduction.run"}}',owned['container_id']],capture_output=True,text=True)
   if found.returncode==0:
    assert found.stdout.strip()==owned['run_id'],'Refuse deleting any different owner'
    subprocess.run(['docker','rm','-f',owned['container_id']],check=True,stdout=subprocess.PIPE)
