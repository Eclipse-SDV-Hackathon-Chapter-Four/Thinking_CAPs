"""Prepare exact measured source and check patch applicability, without signing or publishing."""
import hashlib,json,os,pathlib,subprocess,tarfile,datetime
from score_sw_fabric.storage import validate_run_root
P=pathlib.Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167');D=P/'final-review/verification-run';S=P/'submission';R=pathlib.Path((P/'final-review/new-scratch-root').read_text().strip());W=R/'submission-workspace'
BASE='e3d126c2d7569345cf5f790310702eb00cd86b06';MAIN='9fa5a2f6cc78dd3f756df3ec3ea9466d38ee7dfd';BRANCH='test/1167-api-idempotency-reviewed'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def guard():
 validate_run_root(R)
 v=json.loads(subprocess.check_output(['findmnt','-J','-T',str(R),'-o','SOURCE,UUID'],text=True))['filesystems'][0]
 assert v['source']=='/dev/loop1' and v['uuid']=='11c42dee-73a3-4c2b-ab42-a0440011d9e0'
def git(args,env=None):
 guard();r=subprocess.run(['git','-C',str(W),'-c','core.hooksPath=/dev/null',*args],capture_output=True,text=True,env=env,timeout=90)
 if r.returncode:raise RuntimeError('git '+str(args)+': '+r.stderr[:1200])
 return r.stdout.strip()
guard();assert not W.exists(),'Preserve existing disposable preparation rather than overwriting'
subprocess.run(['git','-c','core.hooksPath=/dev/null','clone','--no-hardlinks','--no-local','--no-checkout',str(D/'candidate'),str(W)],check=True,capture_output=True,timeout=90)
git(['config','core.hooksPath','/dev/null']);git(['checkout','-b',BRANCH,BASE]);git(['apply','--index',str(S/'communication-1167.patch')])
binding=json.loads((D/'candidate-hashes.json').read_text());assert all(sha(W/rel)==h for rel,h in binding.items())
assert json.loads(subprocess.check_output(['gh','api','user'],text=True))['login']=='jnsagai'
tree=git(['write-tree']);changed=git(['diff','--cached','--name-only']).splitlines();assert len(changed)==9
# Export exact source tree independent of Git internals or Fabro.
archive=S/'source.tar.gz'
with archive.open('wb') as out:
 subprocess.run(['git','-C',str(W),'-c','core.hooksPath=/dev/null','archive','--format=tar.gz',tree],stdout=out,check=True,timeout=30)
with tarfile.open(archive,'r:gz') as tar:
 for rel,h in binding.items():assert hashlib.sha256(tar.extractfile(rel).read()).hexdigest()==h
# Read-only applicability check using alternate index, leaving measured-baseline tree staged.
git(['fetch','--no-tags','https://github.com/eclipse-score/communication.git',MAIN]);env=dict(os.environ);env['GIT_INDEX_FILE']=str(R/'submission-main-compatibility.index')
git(['read-tree',MAIN],env);compat=git(['apply','--cached','--check',str(S/'communication-1167.patch')],env);assert git(['write-tree'])==tree
record={'status':'exact_measured_source_prepared_eca_identity_resolution_required','branch':BRANCH,'workspace':str(W),'staged_git_tree':tree,'baseline':BASE,'current_upstream_main':MAIN,'current_main_patch_applicability':'passes_against_alternate_index','current_main_execution_verification':'not_performed; baseline native results are not claimed for changed upstream production source','source_file_count':len(binding),'source_binding_sha256':sha(D/'candidate-hashes.json'),'archive':archive.name,'archive_sha256':sha(archive),'changed_paths':changed,'source_commits_created':0,'signed_off_by_added':False,'signed_eca_on_behalf_of_user':False,'human_acceptance_recorded':False,'fork_created':False,'remote_pushed':False,'pull_request_created':False,'new_paid_calls':0,'new_native_runs':0,'storage_guard':'stable admitted loop1 binding revalidated before operations','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
write(S/'preparation-result.json',record);print(json.dumps(record,indent=2))
