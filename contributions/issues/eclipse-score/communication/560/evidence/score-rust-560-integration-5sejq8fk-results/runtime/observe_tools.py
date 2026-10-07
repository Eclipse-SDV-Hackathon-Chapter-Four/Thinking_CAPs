from pathlib import Path
from collections import Counter
import json,urllib.request
R=Path(__file__).parent
b=json.loads((R/'server-binding.json').read_text());t=json.loads((Path(b['private_state'])/'operator-secret.json').read_text())['token'];rid=json.loads((R/'queue.json').read_text())['jobs'][0]['run_id']
path=R/'native-guard-observation-progress.json';old=json.loads(path.read_text()) if path.exists() else {};after=0;counts=Counter(); shapes={};agent_types=Counter();tool_calls=Counter();tool_errors=Counter()
for _ in range(250):
 req=urllib.request.Request(b['url']+'/api/v1/runs/'+rid+f'/events?limit=1000&after={after}',headers={'Authorization':'Bearer '+t})
 with urllib.request.urlopen(req,timeout=15) as f:x=json.load(f)
 for item in x['data']:
  after=item['stream_seq'];rec=item.get('item',{}).get('record',{});body=rec.get('body',rec);event=body.get('event',body.get('kind','unknown'));counts[event]+=1
  custom=body.get('ev',{}).get('custom',{}); inner=custom.get('event',{}).get('event',{}) if isinstance(custom.get('event'),dict) else {}
  for typ,data in inner.items():
   agent_types[typ]+=1
   if 'tool' in typ.lower() and isinstance(data,dict):
    shapes.setdefault(typ,list(data))
    name=data.get('tool_name',data.get('name'))
    if name and ('start' in typ.lower() or 'called' in typ.lower()):tool_calls[name]+=1
    if name and data.get('is_error'):tool_errors[name]+=1
 if not x['meta']['has_more']:break
value={'through_event':after,'event_types':dict(counts),'tool_event_shapes':shapes,'agent_event_types':dict(agent_types),'tool_calls':dict(tool_calls),'tool_errors':dict(tool_errors),'claim':'Read-only native event metadata; no scheduling or execution; not comprehensive guard qualification'}
path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
print(json.dumps({'through_event':after,'agent_types':agent_types.most_common(12),'tool_calls':dict(tool_calls),'tool_errors':dict(tool_errors),'tool_event_shapes':shapes}))
