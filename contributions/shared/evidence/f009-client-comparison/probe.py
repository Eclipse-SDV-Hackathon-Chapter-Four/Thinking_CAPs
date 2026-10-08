import json,os,signal,socket,subprocess,tempfile,time
from pathlib import Path
import carla
out=Path('evidence/f009-client-comparison'); out.mkdir(exist_ok=False)
for port in [2100,2101,2102]:
 with socket.socket() as sock: sock.bind(('127.0.0.1',port))
record={'schema_version':1,'work_classification':'prepared','mode':'controlled early/late client comparison with actual NVIDIA offscreen CARLA world','client_version':carla.Client('127.0.0.1',2100,2).get_client_version(),'observations':[]}; process=None
early=carla.Client('127.0.0.1',2100,2); early.set_timeout(1)
try: record['early_before_launch']=early.get_server_version()
except RuntimeError as error: record['early_before_launch_error']=str(error)
with tempfile.TemporaryDirectory(prefix='sdv-carla-compare-') as runtime:
 environment=os.environ.copy(); environment['XDG_CONFIG_HOME']=runtime+'/config'; environment['VK_ICD_FILENAMES']='/usr/share/vulkan/icd.d/nvidia_icd.json'
 command=['/home/jefferson/carla-simulator/CarlaUE4/Binaries/Linux/CarlaUE4-Linux-Shipping','CarlaUE4','/Game/Carla/Maps/Town01','-prefernvidia','-RenderOffScreen','-quality-level=Low','-nosound','-fps=20','-carla-rpc-port=2100','-UserDir='+runtime+'/user']; record['command']=command
 with (out/'server.log').open('wb') as log:
  try:
   process=subprocess.Popen(command,cwd='/home/jefferson/carla-simulator',env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   deadline=time.monotonic()+45
   while time.monotonic()<deadline:
    try:
     late=carla.Client('127.0.0.1',2100,2); late.set_timeout(2); version=late.get_server_version(); world=late.get_world(); record['late']={'server_version':version,'world_id':world.id,'map':world.get_map().name}; break
    except RuntimeError as error: record['observations'].append({'error':str(error),'monotonic_ns':time.monotonic_ns()}); time.sleep(.2)
   if 'late' in record:
    try: record['early_after_world_ready']=early.get_server_version()
    except RuntimeError as error: record['early_after_world_ready_error']=str(error)
    frames=[]
    for _ in range(5):
     snap=world.wait_for_tick(2); frames.append({'frame':snap.frame,'simulation_elapsed_seconds':snap.timestamp.elapsed_seconds})
    record['frames']=frames; record['status']='passed' if frames[-1]['frame']>frames[0]['frame'] else 'failed'
   else: record['status']='blocked'
  except Exception as error: record.update({'status':'failed','error':str(error)})
  finally:
   if process:
    try: os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError: pass
    try: process.wait(timeout=5)
    except subprocess.TimeoutExpired: os.killpg(process.pid,signal.SIGKILL); process.wait(timeout=3)
record['owned_server_exit']=process.returncode if process else None
(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n'); (out/'probe.py').write_bytes(Path(__file__).read_bytes()); print(json.dumps(record))
