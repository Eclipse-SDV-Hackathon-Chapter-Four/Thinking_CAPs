"""Allow bounded reads and one report per Flash node; deny source mutation."""
import json
import sys
from pathlib import Path
from storage import validate_run_root
R=Path(__file__).parent
def allowed(c):
    validate_run_root(R)
    w=(R/'workspaces/173').resolve()
    if 'cwd' in c and not Path(c['cwd']).resolve().is_relative_to(w):return False
    if c.get('event')=='stage_start':return Path(c.get('cwd','/')).resolve().is_relative_to(w)
    if c.get('event')!='pre_tool_use':return False
    name=c.get('tool_name');a=c.get('tool_input',{})
    if name not in ['read_file','write_file','edit_file','glob','grep'] or not isinstance(a,dict):return False
    value=a.get('file_path',a.get('path',str(w)))
    if not isinstance(value,str) or '\0' in value:return False
    p=(w/value).resolve() if not value.startswith('/') else Path(value).resolve()
    if not p.is_relative_to(w):return False
    rel=p.relative_to(w)
    if '.git' in rel.parts:return False
    if name in ['write_file','edit_file']:return rel.as_posix()=='.rust-queue/reports/'+c.get('node_id','')+'.md' and c.get('node_id') in ['assessment','supervisor']
    if name=='read_file':return 0<int(a.get('limit',200))<=200 and (p.suffix not in ['.json','.log','.xml','.gz','.crate'] or rel.as_posix().startswith('.rust-queue/context/') or rel.as_posix()=='.rust-queue/reports/native-check-summary.json')
    if name=='grep':return a.get('output_mode') in ['files_with_matches','count']
    return isinstance(a.get('pattern'),str)
try:ok=allowed(json.load(sys.stdin))
except Exception:ok=False
if not ok:print(json.dumps({'decision':'block','reason':'Source-read-only assessment file boundary; 200-line reads'}))
raise SystemExit(0 if ok else 2)
