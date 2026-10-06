import importlib.util,json,socket,time
from pathlib import Path
import zenoh
root=Path.cwd(); out=root/'evidence/f009-physical-plant'; out.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('owned_carla',root/'scripts/owned_carla.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
config=json.loads((root/'.local/campaign.json').read_text())['carla']; plant=module.OwnedCarla(config,out); runtime=None; error=None; cleanup=None
session=zenoh.open(zenoh.Config.from_json5(json.dumps({'mode':'peer','listen':{'endpoints':['tcp/172.30.77.1:7447']},'scouting':{'multicast':{'enabled':False}}})))
try:
 plant.start(); runtime=Path(plant.runtime.name); deadline=time.monotonic()+8
 while time.monotonic()<deadline: plant.step(False); time.sleep(.05)
except Exception as exc: error=str(exc)
finally:
 try: plant.close(); cleanup='passed'
 except Exception as exc: cleanup=str(exc)
 session.close()
checks={'actual_world':plant.identity.get('status')=='real','advancing_frames':len(plant.samples)>20 and plant.samples[-1]['frame']>plant.samples[0]['frame'],'physical_movement':bool(plant.samples) and max(s['speed_kmh'] for s in plant.samples)>10,'private_runtime_removed':runtime is not None and not runtime.exists(),'owned_server_stopped':plant.process is not None and plant.process.poll() is not None,'cleanup':cleanup=='passed'}
result={'scope':'real CARLA world/actor/physical speed using existing VCU/vehicle classes; no native Score return in this probe','status':'passed' if all(checks.values()) and error is None else 'failed','error':error,'checks':checks,'samples':len(plant.samples),'max_speed_kmh':max((s['speed_kmh'] for s in plant.samples),default=0)}
(out/'verification.json').write_text(json.dumps(result,indent=2)+'\n'); (out/'probe.py').write_bytes(Path(__file__).read_bytes()); print(json.dumps(result)); raise SystemExit(0 if result['status']=='passed' else 1)
