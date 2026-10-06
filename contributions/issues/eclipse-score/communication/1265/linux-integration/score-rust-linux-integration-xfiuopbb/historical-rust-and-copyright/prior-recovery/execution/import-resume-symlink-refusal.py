from pathlib import Path
import hashlib,json,shutil,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-upcaieyc')
old=r.parent/'score-fabric-pste_44o'
packet=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265/verification-recovery/score-fabric-pste_44o')
out=packet.parent/r.name
validate_run_root(r);out.mkdir()
def h(p,alg='sha256'):
 with p.open('rb') as f:return hashlib.file_digest(f,alg).hexdigest()
manifest=json.loads((packet/'artifact-manifest.json').read_text())['files']
names=['candidate-hashes.json','baseline-hashes.json','controls.json','fabro-source-bindings.json','collector.py','run_native.py','prepare_run.py','tooling-bindings.json','download-utils-source.json','download-utils-1.2.2.tar.gz']
receipts=[]
for name in names:
 source=packet/'execution'/name
 if not source.exists():source=packet/'resume-inputs'/name
 assert source.exists(),name
 assert h(source)==manifest[str(source.relative_to(packet))]
 shutil.copyfile(source,r/name)
 receipts.append({'path':name,'sha256':h(r/name),'carried_evidence':True,'source':str(source)})
(r/'tools').mkdir();source=old/'tools/bazel';expected=json.loads((packet/'execution/run-binding.json').read_text())['files']['tools/bazel'];assert h(source)==expected;shutil.copyfile(source,r/'tools/bazel');(r/'tools/bazel').chmod(0o755)
candidate=json.loads((r/'candidate-hashes.json').read_text())
for name,expected in candidate.items():
 source=old/'candidate'/name;assert source.is_file() and not source.is_symlink() and h(source)==expected,name
 dest=r/'candidate'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);assert h(dest)==expected
assert len(candidate)==2879
cache=[]
base=old/'repository-cache/content_addressable'
for algorithm,width in [('sha256',64),('sha512',128)]:
 for source in (base/algorithm).glob('*/file'):
  validate_run_root(r)
  digest=source.parent.name;assert len(digest)==width and all(x in '0123456789abcdef' for x in digest)
  assert source.is_file() and not source.is_symlink() and h(source,algorithm)==digest
  dest=r/'repository-cache/content_addressable'/algorithm/digest/'file';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert h(dest,algorithm)==digest
  markers=[]
  for marker in source.parent.glob('id-*'):
   assert marker.is_file() and not marker.is_symlink() and marker.stat().st_size==0
   assert len(marker.name)==3+width and all(x in '0123456789abcdef' for x in marker.name[3:])
   shutil.copyfile(marker,dest.parent/marker.name);markers.append(marker.name)
  cache.append({'algorithm':algorithm,'digest':digest,'bytes':source.stat().st_size,'source':str(source),'markers':markers,'carried_evidence':True})
for name in ['seed_locked_download_utils.py','Bazel-8.7.0-DownloadCache.java','cache-marker-source-review.json']:
 shutil.copyfile(Path('/tmp/rust-resume-xndyh_w9')/name,r/name)
ledger=json.loads((packet/'correction-ledger.json').read_text());ledger['status']='resumed';(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
(r/'contribution.json').write_text(json.dumps({'path':str(out)},indent=2)+'\n')
record={'kind':'fresh_workspace_import_after_remount','historical_guard_preserved':True,'old_mount_device':1819,'current_mount_device':1793,'carried_inputs':receipts,'candidate_subjects_verified':len(candidate),'public_cache_payloads':cache,'cache_bytes':sum(x['bytes'] for x in cache),'queues_private_state_or_build_outputs_imported':False,'source_and_lock_unchanged':True}
(r/'resume-import.json').write_text(json.dumps(record,indent=2)+'\n');validate_run_root(r)
print(json.dumps({'root':str(r),'out':str(out),'verified_candidate':len(candidate),'verified_public_cache_payloads':len(cache),'cache_bytes':record['cache_bytes']}))
