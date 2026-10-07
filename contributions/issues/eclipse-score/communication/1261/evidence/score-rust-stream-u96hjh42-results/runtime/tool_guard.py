"""Bound source editor, report writers and single correction admission."""
import json, sys, hashlib
from pathlib import Path
from storage import validate_run_root
R=Path(__file__).parent
W=R/'workspaces/1261'
T=json.loads((R/'jobs/1261/task.json').read_text())
def source_allowed(rel):
 return rel.name not in T['protected_names'] and (rel.as_posix() in T['allowed_files'] or any(rel.as_posix().startswith(p) for p in T['allowed_prefixes']))
def allowed(c):
 validate_run_root(R)
 w=W.resolve();node=c.get('node_id');event=c.get('event')
 if 'cwd' in c and not Path(c['cwd']).resolve().is_relative_to(w):return False
 if event=='stage_start':
  if not Path(c.get('cwd','/')).resolve().is_relative_to(w):return False
  if node=='implementation':
   p=R/'correction-ledger.json';v=json.loads(p.read_text())
   if v['used']>=v['max'] or node in v['started']:return False
   v['used']+=1;v['started'].append(node);p.write_text(json.dumps(v,indent=2)+'\n')
  return node in ['plan','implementation','supervisor']
 if event!='pre_tool_use':return False
 name=c.get('tool_name');a=c.get('tool_input',{})
 if name not in ['read_file','write_file','edit_file','glob','grep'] or not isinstance(a,dict):return False
 value=a.get('file_path',a.get('path',str(w)))
 if not isinstance(value,str) or '\0' in value:return False
 p=(w/value).resolve() if not value.startswith('/') else Path(value).resolve()
 if not p.is_relative_to(w):return False
 rel=p.relative_to(w)
 if '.git' in rel.parts:return False
 if name in ['write_file','edit_file']:
  reports={'.rust-queue/reports/'+str(node)+'.md'}
  if node=='implementation':reports.add('.rust-queue/reports/regression-plan.json')
  return rel.as_posix() in reports or (node=='implementation' and source_allowed(rel) and json.loads((R/'correction-ledger.json').read_text())['used']==2)
 if name=='read_file':return 0<int(a.get('limit',200))<=200
 if name=='grep':return a.get('output_mode') in ['files_with_matches','count']
 return isinstance(a.get('pattern'),str)
try:ok=allowed(json.load(sys.stdin))
except Exception:ok=False
if not ok:print(json.dumps({'decision':'block','reason':'Bound Flash editor/report scope, original correction cap, bounded reads'}))
raise SystemExit(0 if ok else 2)
