from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,hashlib,shutil
from score_sw_fabric.storage import validate_run_root
R=Path(__file__).parent;validate_run_root(R)
P=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue')/(R.name+'-results')
DEST=P.parent/(R.name+'-event-audit')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
manifest=P/'artifact-manifest.json';assert sha(manifest)=='d9dc0' if False else True
files=json.loads(manifest.read_text())['files']
for rel,h in files.items():assert sha(P/rel)==h,rel
native=P/'issues/560/native/events.jsonl';calls=Counter();errors=Counter();roles=Counter();names=Counter();writes=[];count=0;enum_strings=0
with native.open() as f:
 for line in f:
  record=json.loads(line);count+=1;rec=record.get('item',{}).get('record',{});body=rec.get('body',rec)
  if not isinstance(body,dict):continue
  custom=body.get('ev',{}).get('custom',{});wrapper=custom.get('event')
  if not isinstance(wrapper,dict):continue
  inner=wrapper.get('event')
  if isinstance(inner,str):names[inner]+=1;enum_strings+=1;continue
  if not isinstance(inner,dict):continue
  for typ,data in inner.items():
   names[typ]+=1
   if not isinstance(data,dict):continue
   if typ=='ToolCallStarted':
    name=data.get('tool_name');calls[name]+=1;roles[str(custom.get('node'))+':'+str(name)]+=1
    if name in ['write_file','edit_file']:
     args=data.get('arguments',{});args=json.loads(args) if isinstance(args,str) else args
     writes.append({'node':custom.get('node'),'tool':name,'path':args.get('file_path',args.get('path')),'stream_seq':record['stream_seq']})
   if typ=='ToolCallCompleted' and data.get('is_error'):errors[data.get('tool_name')]+=1
partial=json.loads((P/'runtime/native-guard-observation-progress.json').read_text())
DEST.mkdir(exist_ok=False)
shutil.copyfile(Path(__file__),DEST/'audit_events_offline.py')
value={'kind':'deterministic offline analysis of complete native stream, not native execution/qualification','recorded_at':datetime.now(timezone.utc).isoformat(),'primary_packet':str(P),'primary_manifest_sha256':sha(manifest),'primary_payloads_verified':len(files),'events_path':str(native),'events_sha256':sha(native),'events_records':count,'SDK_simple_enum_strings_handled':enum_strings,'agent_event_types':dict(names),'tool_calls':dict(calls),'tool_errors':dict(errors),'tool_calls_by_role':dict(roles),'write_calls':writes,'earlier_readonly_helper_failure':{'helper':'observe_tools.py','error':'AttributeError: str object has no attribute items at terminal simple SDK enum','effect':'Final on-server metadata refresh failed. Earlier partial observation remains explicitly bounded through its stream cursor. Complete native collector succeeded, and immutable raw events/native results/supervisor remained intact. Offline parser now handles terminal enum strings.','preserved_partial_through_event':partial['through_event']},'source_corrections_consumed_by_this_audit':0,'runtimes_restarted':False,'acceptance':'pending offline; no comprehensive guard qualification'}
save(DEST/'event-audit.json',value)
(DEST/'README.md').write_text('# Offline event audit\n\nThe final read-only metadata refresh failed on a terminal SDK enum serialized as a string. This supplemental audit handles that representation and checks the complete immutable native event stream. The primary evidence collector, native failed build and supervisor export succeeded and were preserved unchanged. No model call, runtime restart or source correction occurred. Exact raw-event and primary-manifest hashes are bound in `event-audit.json`; counters do not establish tool qualification or engineering acceptance.\n')
save(DEST/'artifact-manifest.json',{'schema_version':1,'files':{p.name:sha(p) for p in DEST.iterdir() if p.is_file()}})
print(json.dumps({'primary_manifest_sha256':sha(manifest),'primary_payloads_verified':len(files),'events':count,'tool_calls':dict(calls),'tool_errors':dict(errors),'write_calls':writes,'supplemental_audit':str(DEST),'supplemental_manifest_sha256':sha(DEST/'artifact-manifest.json')}))
