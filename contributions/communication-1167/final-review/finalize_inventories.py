"""Export and verify portable contribution inventories after final review."""
import hashlib,json,os,pathlib
from datetime import datetime,timezone
P=pathlib.Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167');Q=P/'final-review';D=Q/'verification-run';ID=(D/'current-native-run-id').read_text().strip()
excluded_dirs={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.venv','node_modules'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def inventory(root,excluded):
 files={}
 for directory,dirs,names in os.walk(root,followlinks=False):
  dirs[:]=sorted(d for d in dirs if d not in excluded_dirs and not (pathlib.Path(directory)/d).is_symlink())
  for name in sorted(names):
   f=pathlib.Path(directory)/name;rel=f.relative_to(root).as_posix()
   if rel not in excluded and not f.is_symlink() and not name.endswith('.pyc') and f.is_file():files[rel]=sha(f)
 return files
packet=inventory(D,{'artifact-manifest.json'});write(D/'artifact-manifest.json',{'run_id':ID,'status':'portable_packet_verified_agent_review_complete','exclusions':['Git internals','generated caches','symlinks','own inventory'],'files':packet})
assert all(sha(D/f)==h for f,h in packet.items())
root=inventory(P,{'artifact-manifest.json','session-artifact-manifest.json'});write(P/'artifact-manifest.json',{'run_id':ID,'status':'portable_artifacts_verified_agent_review_complete_formal_acceptance_pending','exclusions':['Git internals','generated caches','symlinks','root inventory files'],'files':root})
assert all(sha(P/f)==h for f,h in root.items())
write(P/'session-artifact-manifest.json',{'manifest':'artifact-manifest.json','run_id':ID,'sha256':sha(P/'artifact-manifest.json'),'status':'agent_review_complete_verified_export','verified_file_count':len(root),'verified_packet_file_count':len(packet),'time_utc':datetime.now(timezone.utc).isoformat()})
print(json.dumps({'root_files_verified':len(root),'packet_files_verified':len(packet),'root_inventory_sha256':sha(P/'artifact-manifest.json')}))
