"""Fresh authorized userspace preparation; no private-state/build-output migration."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,sys,tarfile
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,build_environment
r=Path(__file__).parent;validate_run_root(r)
old=r.parent/'score-fabric-upcaieyc'
validate_run_root(old)
packet=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265/verification-recovery/score-fabric-upcaieyc')
out=packet.parent/r.name;assert not out.exists();out.mkdir()
def h(p,alg='sha256'):
 with p.open('rb') as f:return hashlib.file_digest(f,alg).hexdigest()
assert h(packet/'artifact-manifest.json')=='a211f501c0b2c824ddd3172a634d514fa23bf4b692a17371a6f20a3afb000716'
manifest=json.loads((packet/'artifact-manifest.json').read_text())['files']
for name,expected in manifest.items():assert h(packet/name)==expected,name
for name in ['collector.py','run_native.py','prepare_run.py','controls.json','candidate-hashes.json','baseline-hashes.json','fabro-source-bindings.json']:
 source=packet/'execution'/name;assert h(source)==manifest[str(source.relative_to(packet))];shutil.copyfile(source,r/name)
original_binding=json.loads((packet/'execution/run-binding.json').read_text())
(r/'tools').mkdir();assert h(old/'tools/bazel')==original_binding['files']['tools/bazel'];shutil.copyfile(old/'tools/bazel',r/'tools/bazel');(r/'tools/bazel').chmod(0o755)
subjects=json.loads((r/'candidate-hashes.json').read_text())
for name,expected in subjects.items():
 source=old/'candidate'/name;assert source.is_file() and h(source)==expected
 dest=r/'candidate'/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if source.is_symlink():
  assert name=='coding-standards.yaml' and str(source.readlink())=='quality/static_analysis/coding-standards.yaml';assert source.resolve().is_relative_to((old/'candidate').resolve());dest.symlink_to(source.readlink())
 else:shutil.copy2(source,dest)
for name,expected in subjects.items():assert h(r/'candidate'/name)==expected
cache=[]
for alg,width in [('sha256',64),('sha512',128)]:
 for source in (old/'repository-cache/content_addressable'/alg).glob('*/file'):
  validate_run_root(r);digest=source.parent.name;assert len(digest)==width and h(source,alg)==digest and not source.is_symlink()
  dest=r/'repository-cache/content_addressable'/alg/digest/'file';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert h(dest,alg)==digest
  markers=[]
  for marker in source.parent.glob('id-*'):
   assert marker.is_file() and not marker.is_symlink() and marker.stat().st_size==0 and len(marker.name)==width+3 and all(c in '0123456789abcdef' for c in marker.name[3:]);shutil.copyfile(marker,dest.parent/marker.name);markers.append(marker.name)
  cache.append({'hash_algorithm':alg,'digest':digest,'bytes':source.stat().st_size,'markers':markers,'carried_immutable_public_payload':True})
(r/'cache-import.json').write_text(json.dumps({'inputs':cache,'queues_private_state_build_outputs_imported':False},indent=2)+'\n')
# Retain exact image/checksum evidence, and extract regular libraries only (no links).
runtime_packet=Path('/home/jefferson/s-core_sw_fabric/specs/011-change-impact-and-freshness/evidence/t033-linux-runtime')
assert h(runtime_packet/'manifest.json')=='485b2f0cc3dbd6cf7522d79ad47924f892538c57a486b9ceb4d29bead7871bed'
runtime_manifest=json.loads((runtime_packet/'manifest.json').read_text())['files']
for name in ['runtime-acquisition.json','runtime-provenance.json','runtime-overlays.json','runtime-ABI.json','checksum-signature.txt']:
 assert h(runtime_packet/name)==runtime_manifest[name];dest=r/'runtime-provenance'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(runtime_packet/name,dest)
archive_root=r.parent/'score-011-runtime-p0y6xo39/public-runtime'
for record in json.loads((runtime_packet/'runtime-acquisition.json').read_text())['requests']:
 source=archive_root/record['url'].rsplit('/',1)[-1];assert h(source)==record['sha256'] and source.stat().st_size==record['bytes'];shutil.copyfile(source,r/'runtime-provenance'/source.name)
rows=json.loads((runtime_packet/'runtime-overlays.json').read_text())['overlays'];mapped={Path(x['source']).name:x for x in rows};assert len(mapped)==13
overlays=[];notices=[]
with tarfile.open(r/'runtime-provenance/ubuntu-noble-oci-amd64-root.tar.gz') as archive:
 for member in archive:
  name=Path(member.name);assert not name.is_absolute() and '..' not in name.parts
  if member.isfile() and member.name.startswith('usr/lib/x86_64-linux-gnu/') and name.name in mapped:
   row=mapped[name.name];assert h(Path(row['target']))==row['host_original_sha256'];data=archive.extractfile(member).read();assert hashlib.sha256(data).hexdigest()==row['source_sha256']
   dest=r/'runtime-libs'/name.name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(data);overlays.append({'source':str(dest),'target':row['target'],'source_sha256':row['source_sha256'],'host_original_sha256':row['host_original_sha256'],'archive_member':member.name})
  if member.isfile() and ('/copyright' in member.name or 'common-licenses/' in member.name):
   data=archive.extractfile(member).read();dest=r/'runtime-notices'/member.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);notices.append({'path':str(dest.relative_to(r)),'sha256':h(dest),'bytes':len(data)})
assert len(overlays)==13
(r/'runtime-overlays.json').write_text(json.dumps({'scope':'private UbuntuNoble library namespace over readonly host tools; scoped compatibility, not fullCI or qualification','overlays':overlays,'image_archive_sha256':'6fb36aacf06bfa77b8b624c63f07c04b85d76ad66d3bd3d9f101462537e770e3','notices':notices,'carried_origin_manifest_sha256':'485b2f0cc3dbd6cf7522d79ad47924f892538c57a486b9ceb4d29bead7871bed'},indent=2)+'\n')
sig=subprocess.run(['/usr/bin/gpgv','--keyring','/usr/share/keyrings/ubuntu-cloudimage-keyring.gpg',str(r/'runtime-provenance/SHA256SUMS.gpg'),str(r/'runtime-provenance/SHA256SUMS')],capture_output=True,text=True)
(r/'runtime-signature-measurement.json').write_text(json.dumps({'exit_code':sig.returncode,'stdout':sig.stdout,'stderr':sig.stderr,'keyring_sha256':h(Path('/usr/share/keyrings/ubuntu-cloudimage-keyring.gpg')),'fresh_local_check_of_carried_checksum_files':True},indent=2)+'\n');assert sig.returncode==0,sig.stderr
ledger={'max_corrections':3,'corrections_used':0,'entries':[],'status':'preparing_compatible_userspace','authority':'User go on2026-10-06 following request for new bounded compatible-userspace run','previous_recovery_corrections_used':3,'supervisor':'/root/rust_issue_supervisor'}
(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');(r/'contribution.json').write_text(json.dumps({'path':str(out)},indent=2)+'\n')
(r/'recovery-allocation.json').write_text(json.dumps({'prior_packet_manifest_sha256':h(packet/'artifact-manifest.json'),'carried_candidate_subjects_verified':len(subjects),'public_cache_payloads':len(cache),'runtime_archive_verified':True,'runtime_library_inputs':13,'private_queues_or_build_outputs_migrated':False},indent=2)+'\n')
p=r/'collector.py';s=p.read_text();needle="'--chdir',str(ROOT/'candidate'),*args]";assert s.count(needle)==1
s=s.replace(needle,"*[part for row in json.loads((ROOT/'runtime-overlays.json').read_text())['overlays'] for part in ('--ro-bind',row['source'],row['target'])],'--chdir',str(ROOT/'candidate'),*args]")
p.write_text(s);ast.parse(s)
p=r/'run_native.py';s=p.read_text().replace("'communication1265_remount_final'","'communication1265_compatible'").replace('Communication #1265: final supervised native verification','Communication #1265: compatible userspace verification');p.write_text(s);ast.parse(s)
env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8',**build_environment(r)}
resolved={n:shutil.which(n,path=env['PATH']) for n in ['losetup','lsblk','findmnt','git','bwrap']};assert all(resolved.values())
(r/'worker-preflight.json').write_text(json.dumps({'kind':'direct_local_environment_inspection','environment':env,'resolved_tools':resolved,'storage_binding_validated':True,'candidate_hashes_validated':True,'no_tests_yet':True},indent=2)+'\n')
(r/'tooling-bindings.json').write_text(json.dumps({'host_tools':{n:{'path':p,'sha256':h(Path(p))} for n,p in resolved.items()},'python':{'path':sys.executable,'version':sys.version},'fabric_storage_source_sha256':h(Path('/home/jefferson/s-core_sw_fabric/src/score_sw_fabric/storage.py')),'fabro_binary_sha256':h(Path('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro')),'bazel_binary_sha256':h(r/'tools/bazel')},indent=2)+'\n')
proc=subprocess.run([sys.executable,str(r/'prepare_run.py')],env=env,capture_output=True,text=True);assert proc.returncode==0,proc.stderr
binding=json.loads((r/'run-binding.json').read_text())
for name in ['runtime-overlays.json','cache-import.json','runtime-signature-measurement.json','storage-selection.json','recovery-allocation.json']:
 binding['files'][name]=h(r/name)
for p in list((r/'runtime-libs').iterdir())+list((r/'runtime-provenance').iterdir()):binding['files'][str(p.relative_to(r))]=h(p)
binding['prior_run']='01M482VTQYK6T74SS0SVTPGCX4';binding['runtime_scope']='private hash-bound Noble shared libraries; exact native compiler/source/toolchain pins'
(r/'run-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
validate_run_root(r)
print(json.dumps({'root':str(r),'out':str(out),'candidate_subjects':len(subjects),'cache_payloads':len(cache),'runtime_libraries':len(overlays),'runtime_notices':len(notices),'fresh_signature_check':sig.returncode,'bound_files':len(binding['files']),'corrections_used':0}))
