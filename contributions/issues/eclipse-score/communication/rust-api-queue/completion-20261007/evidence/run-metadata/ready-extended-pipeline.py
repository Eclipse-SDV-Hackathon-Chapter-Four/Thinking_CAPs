from pathlib import Path
import subprocess,json,datetime
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT/'workspaces/integrated'
results=[]
for name in ['host-tests','macro-and-doc-tests','notice-full','clang-tidy-full','asan-full','tsan-full']:
 print('START '+name,flush=True)
 status=subprocess.run(['python3',str(ROOT/'supplementary_launcher.py'),'--workspace',str(WORKSPACE),'--plan',str(ROOT/(name+'-plan.json')),'--output',str(ROOT/('ready-extended-'+name))]).returncode
 results.append({'check':name,'exit_code':status,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (ROOT/'ready-extended-progress.json').write_text(json.dumps(results,indent=2)+'\n')
 print('END '+name+' '+str(status),flush=True)

subprocess.run(["python3",str(ROOT/"auxiliary-checks.py")],check=False)
