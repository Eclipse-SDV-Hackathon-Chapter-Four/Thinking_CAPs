import hashlib,json,os,signal,socket,subprocess,tempfile,time
from pathlib import Path
root=Path.cwd(); out=root/'evidence/f008-carla-rpc-wire'; out.mkdir(exist_ok=False)
for port in [2100,2101,2102]:
 with socket.socket() as sock: sock.bind(('127.0.0.1',port))
observations=[]; process=None; result={'mode':'owned CARLA null-RHI RPC wire diagnostic; no vehicle acceptance','work_classification':'prepared','observations':observations}
with tempfile.TemporaryDirectory(prefix='sdv-carla-wire-') as runtime:
 environment=os.environ.copy(); environment['XDG_CONFIG_HOME']=runtime+'/config'
 binary='/home/jefferson/carla-simulator/CarlaUE4/Binaries/Linux/CarlaUE4-Linux-Shipping'; command=[binary,'CarlaUE4','-nullrhi','-nosound','-carla-rpc-port=2100','-UserDir='+runtime+'/user']; result['command']=command
 with (out/'server.log').open('wb') as log:
  try:
   process=subprocess.Popen(command,cwd='/home/jefferson/carla-simulator',env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   deadline=time.monotonic()+25
   request=b'\x94\x00\x01\xa7version\x91\x91\xc2'
   while time.monotonic()<deadline:
    record={'monotonic_ns':time.monotonic_ns(),'request_hex':request.hex()}
    try:
     with socket.create_connection(('127.0.0.1',2100),timeout=1) as sock:
      sock.settimeout(1); sock.sendall(request); response=sock.recv(4096); record.update({'status':'received' if response else 'closed','response_hex':response.hex()})
    except OSError as error: record.update({'status':'unavailable','error':str(error)})
    observations.append(record); time.sleep(.3)
   code='import carla; c=carla.Client("127.0.0.1",2100,2); c.set_timeout(2); print(c.get_server_version())'
   trace=subprocess.run(['strace','-f','-s','256','-e','trace=network,read,write','-o',str(out/'client-strace.txt'),'/usr/bin/python3','-c',code],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=10)
   (out/'client-output.txt').write_bytes(trace.stdout); result['client_exit']=trace.returncode
   result['tcp_sockets']=subprocess.check_output(['ss','-H','-tnp','sport = :2100 or dport = :2100']).decode()
   result['status']='response-observed' if any(o['status']=='received' for o in observations) else 'blocked'
  except Exception as error: result.update({'status':'failed','error':str(error)})
  finally:
   if process:
    try: os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError: pass
    try: process.wait(timeout=5)
    except subprocess.TimeoutExpired: os.killpg(process.pid,signal.SIGKILL); process.wait(timeout=3)
result['owned_server_exit']=process.returncode if process else None
result['binary_sha256']=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n'); (out/'probe.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':result['status'],'responses':[o for o in observations if o['status']=='received']}))
