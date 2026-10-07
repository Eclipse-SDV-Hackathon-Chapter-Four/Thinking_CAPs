from pathlib import Path
import subprocess,json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT/'workspaces/integrated'
checks=['ownership-regression','cfg-test-clippy','format-check','notice-changed','serial-integrations','native-clippy','native-ruff','host-build']
results=[]
for name in checks:
 print('START '+name,flush=True)
 status=subprocess.run(['python3',str(ROOT/'supplementary_launcher.py'),'--workspace',str(WORKSPACE),'--plan',str(ROOT/('resolved-format-check-plan.json' if name=='format-check' else 'resolved-serial-integrations-plan.json' if name=='serial-integrations' else name+'-plan.json')),'--output',str(ROOT/('resolved-'+name))]).returncode
 results.append({'check':name,'exit_code':status,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (ROOT/'resolved-progress.json').write_text(json.dumps(results,indent=2)+'\n')
 print('END '+name+' '+str(status),flush=True)
 # Regression/format/owned notices must pass before broader or costly checks.
 if status and name in ['ownership-regression','cfg-test-clippy','format-check','notice-changed']:
  break

subprocess.run(["python3",str(ROOT/"resolved-extended-pipeline.py")],check=False)
