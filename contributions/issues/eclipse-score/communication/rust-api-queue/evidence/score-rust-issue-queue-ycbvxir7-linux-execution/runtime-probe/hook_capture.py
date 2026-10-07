import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).parent
context=json.load(sys.stdin)
with (ROOT/'contexts.jsonl').open('a') as output:output.write(json.dumps(context)+'\n')
result=subprocess.run([sys.executable,str(ROOT.parent/'tool_guard.py'),'0'],input=json.dumps(context),text=True,capture_output=True)
with (ROOT/'guard-results.jsonl').open('a') as output:output.write(json.dumps({'event':context.get('event'),'node_id':context.get('node_id'),'cwd':context.get('cwd'),'tool':context.get('tool_name'),'exit_code':result.returncode})+'\n')
sys.stdout.write(result.stdout)
raise SystemExit(result.returncode)
