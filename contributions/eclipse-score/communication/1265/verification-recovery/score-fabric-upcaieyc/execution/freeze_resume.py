from pathlib import Path
import ast,hashlib,json,shutil,subprocess,sys,tarfile
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,build_environment
r=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-upcaieyc');validate_run_root(r)
out=Path(json.loads((r/'contribution.json').read_text())['path'])
ledger=json.loads((out/'correction-ledger.json').read_text());assert ledger['corrections_used']==2
receipt=json.loads((r/'locked-download-utils-cache-receipt.json').read_text())
ledger['corrections_used']=3;ledger['status']='ready_for_final_bounded_native_run';ledger.pop('pending_correction',None)
ledger['entries'].append({'correction':3,'phase':'native_dependency_materialization','failure':'Native HTTP502 fetching exact locked download_utils1.2.2; previous preparation refused SHA512 canonical marker due to64hex assumption.','fix':'Source-verified SHA512 payload and128hex canonical-ID marker copied to owned cache; digest field labels explicit; source/locks unchanged.','receipt_sha256':hashlib.sha256((r/'locked-download-utils-cache-receipt.json').read_bytes()).hexdigest(),'remaining_corrections':0})
(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
p=r/'run_native.py';s=p.read_text().replace("'communication1265_recovery'","'communication1265_remount_final'").replace('Communication #1265: supervised verification recovery','Communication #1265: final supervised native verification');p.write_text(s)
for name in ['collector.py','run_native.py','prepare_run.py']:
 ast.parse((r/name).read_text())
env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8',**build_environment(r)}
resolved={n:shutil.which(n,path=env['PATH']) for n in ['losetup','lsblk','findmnt','git','bwrap']};assert all(resolved.values())
def h(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
(r/'worker-preflight.json').write_text(json.dumps({'kind':'direct_local_worker_environment_measurement','environment':env,'resolved_tools':resolved,'storage_binding_validated':True,'candidate_hashes_validated':True,'native_build_or_tests':False},indent=2)+'\n')
(r/'tooling-bindings.json').write_text(json.dumps({'host_tools':{n:{'path':p,'sha256':h(p)} for n,p in resolved.items()},'python':{'path':sys.executable,'version':sys.version},'fabric_storage_source_sha256':h('/home/jefferson/s-core_sw_fabric/src/score_sw_fabric/storage.py'),'fabro_binary_sha256':h('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro'),'bazel_binary_sha256':h(r/'tools/bazel')},indent=2)+'\n')
proc=subprocess.run([sys.executable,str(r/'prepare_run.py')],env=env,capture_output=True,text=True);assert proc.returncode==0,proc.stderr
binding=json.loads((r/'run-binding.json').read_text())
for name in ['storage-selection.json','resume-import.json','locked-download-utils-cache-receipt.json','seed_locked_download_utils.py','Bazel-8.7.0-DownloadCache.java','download-utils-source.json','download-utils-1.2.2.tar.gz']:
 binding['files'][name]=h(r/name)
binding['prior_run']='01M47SYF7DSPAQDMTYWVD31Q40';binding['carried_candidate_hashes']=True;binding['fresh_root_after_remount']=True;binding['no_further_corrections']=True
(r/'run-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
validate_run_root(r)
for name,expected in binding['files'].items():assert h(r/name)==expected,name
for name,expected in json.loads((r/'candidate-hashes.json').read_text()).items():assert h(r/'candidate'/name)==expected,name
proc=subprocess.run([sys.executable,str(r/'collector.py'),'preflight'],env=env,capture_output=True,text=True);assert proc.returncode==0,proc.stderr
(r/'direct-preflight-result.json').write_text(json.dumps({'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'kind':'direct_check_before_Fabro'},indent=2)+'\n')
native=['/usr/bin/bwrap','--die-with-parent','--ro-bind','/','/','--bind',str(r),str(r),'--tmpfs','/home/jefferson','--tmpfs','/tmp','--tmpfs','/var/tmp','--proc','/proc','--dev-bind','/dev','/dev','--chdir',str(r/'candidate'),str(r/'tools/bazel'),'--version']
proc=subprocess.run(native,env=env,capture_output=True,text=True);assert proc.returncode==0 and '8.7.0' in proc.stdout,proc.stderr
(r/'native-tool-preflight.json').write_text(json.dumps({'command':native,'environment':env,'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'native_tests':False},indent=2)+'\n')
with tarfile.open(r/'download-utils-1.2.2.tar.gz','r:gz') as archive:
 for member in archive:
  assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
  if member.isfile() and member.name.rsplit('/',1)[-1].upper() in {'LICENSE','LICENSE.TXT','COPYING','NOTICE'}:
   p=out/'sources/download_utils'/member.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(member).read())
for name in ['import_resume.py','import-resume-symlink-refusal.py','import-resume-tools-exists-refusal.py','freeze_resume.py']:
 shutil.copyfile(Path('/tmp/rust-resume-xndyh_w9')/name,r/name)
print(json.dumps({'frozen_files':len(binding['files']),'candidate_hashes_verified':2879,'direct_preflight':'passed','bwrap_Bazel_version':'passed8.7.0','corrections_used':3,'remaining':0,'binding_sha256':h(r/'run-binding.json')}))
