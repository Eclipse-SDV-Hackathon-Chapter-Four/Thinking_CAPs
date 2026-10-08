from pathlib import Path
import subprocess,json,datetime,os,time
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT/'workspaces/integrated'
while Path('/proc/1025066').exists(): time.sleep(1)
progress=json.loads((ROOT/'assurance-progress.json').read_text())
result=json.loads((ROOT/'assurance-native-clippy/native-result.json').read_text())
progress.append({'check':'native-clippy','exit_code':0 if result['passed'] else 1,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recovery':'resumed after server restart; surviving collector result'})
(ROOT/'assurance-progress.json').write_text(json.dumps(progress,indent=2)+'\n')
for name in ['native-ruff','host-build']:
 print('START '+name,flush=True)
 status=subprocess.run(['python3',str(ROOT/'supplementary_launcher.py'),'--workspace',str(WORKSPACE),'--plan',str(ROOT/(name+'-plan.json')),'--output',str(ROOT/('assurance-'+name))]).returncode
 progress.append({'check':name,'exit_code':status,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (ROOT/'assurance-progress.json').write_text(json.dumps(progress,indent=2)+'\n')
 print('END '+name+' '+str(status),flush=True)
subprocess.run(['python3',str(ROOT/'extended-pipeline.py')],check=False)
