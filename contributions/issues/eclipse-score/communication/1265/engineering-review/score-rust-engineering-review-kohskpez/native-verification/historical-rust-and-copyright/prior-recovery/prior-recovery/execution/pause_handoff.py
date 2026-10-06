from pathlib import Path
import json,hashlib,datetime,shutil,base64,os,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r);fabric=Path('/home/jefferson/s-core_sw_fabric');c=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265');out=Path(json.loads((r/'contribution.json').read_text())['path'])
def h(p,algorithm='sha256'):
 with p.open('rb') as f:return hashlib.file_digest(f,algorithm).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
oldman=json.loads((c/'artifact-manifest.json').read_text())
for name,sha in oldman['files'].items():assert h(c/name)==sha,name
for name,sha in json.loads((r/'candidate-hashes.json').read_text()).items():assert h(r/'candidate'/name)==sha,name
for name,sha in json.loads((r/'run-binding.json').read_text())['files'].items():assert h(r/name)==sha,name
assert json.loads((r/'server-shutdown.json').read_text())['owned_server_stopped']
ledger=json.loads((out/'correction-ledger.json').read_text());assert ledger['corrections_used']==1
ledger['status']='paused_by_user';ledger['pending_correction']={'number':2,'state':'preparation_failed_before_new_binding_or_launch','failure':'prepare_correction2.py refused a public native cache id marker: it assumed64hex but observed128hex under SHA512.','next_action':'Inspect pinned Bazel8.7.0 DownloadCache.java; preserve refusal, repair guard for source-verified SHA512 canonical-ID shape, correct acquisition labels, then complete cache preparation and record correction2.','remaining_total_corrections':2};save(out/'correction-ledger.json',ledger)
metadata=json.loads((r/'download-utils-source.json').read_text());algorithm,b64=metadata['integrity'].split('-',1);expected=base64.b64decode(b64).hex();archive=r/'download-utils-1.2.2.tar.gz';assert h(archive,algorithm)==expected
lock=json.loads((r/'candidate'/'MODULE.bazel.lock').read_text());url='https://bcr.bazel.build/modules/download_utils/1.2.2/source.json';assert lock['registryFileHashes'][url]==h(r/'download-utils-source.json')
identity={'kind':'corrected_digest_labels_supplement_original_acquisition_retained','registry_source_url':url,'registry_source_sha256':h(r/'download-utils-source.json'),'registry_source_matches_native_root_lock':True,'archive_sha512':h(archive,'sha512'),'archive_sha256':h(archive),'archive_bytes':archive.stat().st_size,'source_declared_SRI':metadata['integrity'],'strip_prefix':metadata['strip_prefix'],'original_record_gap':'download-utils-acquisition.json incorrectly labels some128hex SHA512 values as sha256; original retained. This supplement provides actual algorithm identities.','source_bazel_module_version':'download_utils1.2.2'}
save(out/'archive-identity.json',identity)
# Preserve latest partial scripts and refusals without scheduling or repairing a run.
for p in r.iterdir():
 if p.is_file() and p.suffix in {'.json','.py','.java','.fabro','.toml','.log'}:copy(p,out/'execution'/p.name)
for name in ['download-utils-1.2.2.tar.gz','download-utils-source.json','download-utils-acquisition.json','Bazel-8.7.0-RepositoryCache.java','acquire_download_utils.py','acquire-download-utils-sha256-refusal.py','prepare_correction2.py']:
 copy(r/name,out/'resume-inputs'/name)
# Check only owned native/server processes; never stop unrelated runs or user applications.
owned=[]
needle=[str(r).encode(),b'01M47SYF7DSPAQDMTYWVD31Q40']
for entry in Path('/proc').iterdir():
 if not entry.name.isdigit():continue
 try:
  exe=Path(os.readlink(entry/'exe')).name
  if exe not in {'fabro','java','bwrap','bazel'}:continue
  argv=(entry/'cmdline').read_bytes()
  if any(n in argv for n in needle):owned.append({'pid':int(entry.name),'executable':exe})
 except (OSError,PermissionError):pass
assert not owned,owned
state={'status':'paused_by_user','request':'I need to turn off the pc, put on hold with a handoff to resume','paused_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'objective':'Complete supervised native verification for communication1265 assessment using generic score-rust-workflow; retain portable contribution.','scratch_root':str(r),'contribution':str(out),'generic_workflow':str(fabric/'.agents/skills/score-rust-workflow/SKILL.md'),'prior_manifest_sha256':h(c/'artifact-manifest.json'),'prior_files_verified':len(oldman['files']),'native_source_commit':'e3d126c2d7569345cf5f790310702eb00cd86b06','patch_sha256':json.loads((r/'controls.json').read_text())['patch_sha256'],'candidate_hashes_verified':2879,'frozen_config_hashes_verified':12,'fresh_corrections_used':1,'fresh_max_corrections':3,'remaining_corrections':2,'previous_attempt_corrections_used':3,'latest_run_id':'01M47SYF7DSPAQDMTYWVD31Q40','native_run_status':'failed','native_tests_run':0,'native_failure':'GitLabHTTP502 for exact locked download_utils1.2.2; analysis failed after448.085s.','PATH_remediation':'Measured successful inside actual Fabro worker; sbin included.','supervisor':'/root/rust_issue_supervisor','supervisor_state':'completed_read_only_review; reactivate on resume','owned_native_processes':owned,'private_server_stopped':True,'correction2_directory':{'path':str(r/'correction2'),'entries':[p.name for p in (r/'correction2').iterdir()],'bound':False,'launched':False},'archive_identity':'archive-identity.json','storage_binding':json.loads((r/'storage-selection.json').read_text()),'resume_storage_rule':'Validate exact volume/device binding. If reboot/remount changes device and old guard fails, do not rewrite it. Allocate fresh measured root and import only hash-verified immutable inputs with carried-evidence labels; do not migrate queue/private server state.','paid_calls_authorized':False,'publication_authorized':False,'engineering_acceptance':'pending_offline','registry_status':'Previous sealed175-file attempt remains selected; fresh recovery packet paused, not yet promoted as latest completed verification.'}
save(out/'pause-state.json',state);save(r/'pause-state.json',state)
# Paused packet remains independently hash/size verifiable, including nested historic manifests.
(out/'PAUSED.md').write_text('''# Verification paused by user

The user requested a PC shutdown handoff. No owned native/server processes remain.
The original 175-file packet is unchanged. The fresh run cleared the worker PATH
failure but failed in native dependency analysis after GitLab HTTP502; no tests ran.

See `pause-state.json` for complete source/storage/budget/authority bindings and
`archive-identity.json` for the exact locked SHA512 archive identity. Fresh budget:
**1/3 fixes used, 2 remaining**. Correction2 preparation stopped at a canonical-ID
marker-shape refusal; no correction2 binding or run exists. Keep failed inputs/logs.

Resume with the factory handoff `docs/handoff/011-session-20261006-rust-paused.md`.
No model/provider call, publishing or engineering acceptance is authorized. Previous
failed run and original contribution remain intact; recovery registry promotion is pending.
''')
files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.relative_to(out).as_posix() not in {'artifact-manifest.json','artifact-sizes.json'}]
save(out/'artifact-sizes.json',{'scope':'Packet files; main size inventory and main hash manifest excluded. Nested original manifests are included unchanged.','files':{p.relative_to(out).as_posix():p.stat().st_size for p in files}})
files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.relative_to(out).as_posix()!='artifact-manifest.json']
save(out/'artifact-manifest.json',{'schema_version':1,'scope':'User-paused recovery packet; main manifest self excluded; historical manifests included; no engineering acceptance.','files':{p.relative_to(out).as_posix():h(p) for p in files}})
state['paused_packet_files']=len(files);state['paused_packet_manifest_sha256']=h(out/'artifact-manifest.json')
# Outer receipt is stored outside the sealed paused packet to avoid a circular hash.
save(r/'pause-receipt.json',state)
print(json.dumps({'status':'paused','files':len(files),'manifest_sha256':state['paused_packet_manifest_sha256'],'owned_processes':owned,'corrections_used':1,'remaining':2,'contribution':str(out)}))
