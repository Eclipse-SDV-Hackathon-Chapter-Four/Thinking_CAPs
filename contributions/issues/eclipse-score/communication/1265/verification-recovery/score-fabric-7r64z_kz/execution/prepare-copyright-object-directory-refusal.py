from pathlib import Path
import ast,hashlib,json,os,shutil,subprocess,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r);out=Path(json.loads((r/'contribution.json').read_text())['path'])
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
original=json.loads((r/'run-binding.json').read_text())
for n,want in original['files'].items():assert h(r/n)==want,n
for n,want in json.loads((r/'candidate-hashes.json').read_text()).items():assert h(r/'candidate'/n)==want,n
ledger=json.loads((out/'correction-ledger.json').read_text());assert ledger['corrections_used']==1
assert not (r/'candidate/.git').exists();empty=r/'empty-git-template';empty.mkdir()
env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null'}
commands=[['/usr/bin/git','-c','core.hooksPath=/dev/null','init','--template='+str(empty),str(r/'candidate')],['/usr/bin/git','-C',str(r/'candidate'),'config','--local','core.hooksPath','/dev/null']]
records=[]
for cmd in commands:
 p=subprocess.run(cmd,env=env,capture_output=True,text=True);records.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,p.stderr
assert not list((r/'candidate/.git/hooks').glob('*'))
metadata={str(p.relative_to(r/'candidate')):h(p) for p in (r/'candidate/.git').rglob('*') if p.is_file()}
assert not(r/'candidate/.git/index').exists() and not list((r/'candidate/.git/objects').rglob('*'))
(r/'git-prerequisite-correction.json').write_text(json.dumps({'correction':2,'reason':'Native copyright checker requires gitls-files; archivehadno.git','commands':records,'environment':env,'hooks_disabled':True,'index_or_commit_created':False,'source_subjects_verified_unchanged':2879,'git_metadata_files':metadata,'native_Markdown_header_coverage':False},indent=2)+'\n')
ledger['corrections_used']=2;ledger['entries'].append({'correction':2,'failure':'Nativecopyright failedcollect_inputs gitls-files exit128 because archive lacked.git metadata.','fix':'Initialize empty-template disposable Git repository, hooksPath/dev/null, noindex/commit; execute copyright-only run, carryRust evidence byunchanged source/runtime/config/log hashes.','remaining_corrections':1});ledger['status']='ready_copyright_only_recovery';(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
trial=r/'copyright-recovery';trial.mkdir()
s=(r/'run_native.py').read_text().replace("private=private_server_root(r,'communication1265_compatible')","attempt=r/'copyright-recovery'\nprivate=private_server_root(r,'communication1265_copyright2')").replace('(r/name).write_text','(attempt/name).write_text')
for name in ['run-intent.json','workflow-version.json','fabro-wait.log','verification-results.json']:s=s.replace("r/'"+name+"'","attempt/'"+name+"'")
s=s.replace('Communication #1265: compatible userspace verification','Communication #1265: copyright prerequisite recovery');(r/'run-copyright.py').write_text(s);ast.parse(s)
graph=(r/'workflow.fabro').read_text().replace('/collector.py ', '/collector-copyright.py ');(trial/'workflow.fabro').write_text(graph);(trial/'workflow.toml').write_text((r/'workflow.toml').read_text())
(trial/'workflow-version.json').write_text(json.dumps({'entrypoint':'workflow.fabro','files':{'workflow.fabro':graph,'workflow.toml':(trial/'workflow.toml').read_text()},'workflow_dependencies':{}},indent=2)+'\n')
b={**original,'files':dict(original['files']),'git_metadata_files':metadata,'corrections_used_before_execution':2,'carried_rust_run_id':'01M484ZS5EGJ8E5KH83XXN7PCB','fresh_check_scope':'native copyright only'}
for name in ['collector-copyright.py','run-copyright.py','copyright-recovery/workflow.fabro','copyright-recovery/workflow.toml','copyright-recovery/workflow-version.json','verification-results.json','logs/communication-macro-tests.log','git-prerequisite-correction.json','current-doc-patch-check.json']:
 b['files'][name]=h(r/name)
for p in (r/'candidate/bazel-testlogs/score/mw/com/rust/score_com_concept').glob('*/test.*'):
 b['files'][str(p.relative_to(r))]=h(p)
(r/'run-binding-copyright.json').write_text(json.dumps(b,indent=2)+'\n')
validate_run_root(r)
print(json.dumps({'new_bound_files':len(b['files']),'git_metadata_files':len(metadata),'corrections_used':2,'remaining':1,'binding_sha256':h(r/'run-binding-copyright.json')}))
