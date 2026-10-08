"""Create isolated local hackathon branch and stage the bound contribution; no publication."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,time
from score_sw_fabric.storage import validate_run_root
ROOT=pathlib.Path('/home/jefferson/eclipse_sdv_hackathon_2026');P=ROOT/'contributions/communication-1167';L=P/'local-commit';R=pathlib.Path((P/'final-review/new-scratch-root').read_text().strip());W=R/'hackathon-communication1167';BASE='7d160cf9d9974db930615a59b7038bbd78b26156';BRANCH='contributions/communication-1167'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def guard():
 validate_run_root(R)
 mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(R),'-o','SOURCE,UUID'],text=True))['filesystems'][0]
 assert mount['source']=='/dev/loop1' and mount['uuid']=='11c42dee-73a3-4c2b-ab42-a0440011d9e0'
def run(cmd,cwd=None):
 guard()
 process=subprocess.Popen(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  while True:
   try:
    out,err=process.communicate(timeout=.25)
    break
   except subprocess.TimeoutExpired:
    guard()
 except BaseException:
  process.terminate();process.wait(timeout=5);raise
 if process.returncode:raise RuntimeError(str(cmd[:5])+' failed: '+err[:1200])
 return out.strip()
def git(root,args):return run(['git','-c','gc.auto=0','-c','maintenance.auto=false','-C',str(root),*args])
guard();assert not W.exists(),'Do not overwrite an existing worktree'
assert not git(ROOT,['branch','--list',BRANCH]),'Do not overwrite an existing branch'
git(ROOT,['worktree','add','-b',BRANCH,str(W),BASE]);print('Created isolated branch/worktree',flush=True)
# Read-only offline issue snapshot derived from preserved upstream bytes.
issue=json.loads((P/'upstream/issue.json').read_text());write(L/'upstream-snapshot.json',{'url':issue['html_url'],'issue_number':issue['number'],'state':issue['state'],'title':issue['title'],'captured_on':'2026-10-06','source':'../upstream/issue.json','source_sha256':sha(P/'upstream/issue.json'),'observation':'carried existing immutable issue capture; not a fresh upstream query'})
plan={'authority':'user: create a new branch for commit that contribution','branch':BRANCH,'worktree':str(W),'base_commit':BASE,'parent_repository':str(ROOT),'artifact_root':str(P),'scope':['contributions/communication-1167/','contributions/README.md (1167 entry only)','contributions/registry.json (1167 entry only)'],'publication_authorized':False,'push_prohibited':True,'git_metadata_in_artifacts':'excluded; source files captured as ordinary files, not submodules','generated_caches':'excluded by existing portable inventory','new_native_tests':0,'additional_paid_calls':0,'human_acceptance':'pending; local commit does not create acceptance','state':'isolated_local_branch_created_preparing_commit','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write(L/'plan.json',plan)
# Preserve pre-local-commit handoff, then describe this branch without self-referential commit hashes.
if not (L/'before-local-commit-handoff.json').exists():shutil.copy2(P/'session-handoff.json',L/'before-local-commit-handoff.json')
h=json.loads((P/'session-handoff.json').read_text());h.update(hackathon_local_branch=BRANCH,hackathon_local_worktree=str(W),hackathon_contribution_git_status='packaged_on_isolated_local_branch; commit identity is in Git history',local_commit_authorized=True,publication_authorized=False,next_obligation='Keep committed contribution local; user has explicitly withheld pushing',task_status='verified_contribution_packaged_on_local_branch',time_utc=plan['time_utc']);write(P/'session-handoff.json',h)
for name in ['CURRENT-STATUS.md','RESUME-HANDOFF.md']:
 f=P/name;f.write_text(f.read_text()+'\nLocal commit was authorized on dedicated branch `'+BRANCH+'`, prepared in the isolated worktree `'+str(W)+'`. Another contribution is being committed separately; its main checkout/index are not touched. Remote pushing remains prohibited. The branch Git history identifies the local commit; no human engineering acceptance is implied.\n')
(P/'README.md').write_text((P/'README.md').read_text()+'\nLocal hackathon contribution branch: `'+BRANCH+'` (isolated worktree recorded in `local-commit/plan.json`). All portable artifacts are packaged as ordinary files; nested Git internals and generated caches stay local. Remote pushing remains prohibited.\n')
# Existing complete inventory generator is reused after intentional metadata additions.
run(['python3',str(P/'final-review/finalize_inventories.py')]);manifest=json.loads((P/'artifact-manifest.json').read_text());relatives=list(manifest['files'])+['artifact-manifest.json','session-artifact-manifest.json'];assert len(relatives)==len(set(relatives))
for index,relative in enumerate(relatives):
 if index%250==0:guard()
 src=P/relative;dest=W/'contributions/communication-1167'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 if relative in manifest['files']:assert sha(dest)==manifest['files'][relative]
print('Copied and hash-verified '+str(len(relatives))+' portable files',flush=True)
# Add only this issue to baseline registry/readme; concurrent registry changes remain in original checkout.
registry=W/'contributions/registry.json';v=json.loads(registry.read_text());assert not any(x['id']=='eclipse-score/communication#1167' for x in v['issues']);prefix='communication-1167/';v['issues'].append({'id':'eclipse-score/communication#1167','repository':'eclipse-score/communication','issue_number':1167,'issue_url':issue['html_url'],'upstream_state':issue['state'],'upstream_observed_on':'2026-10-06','upstream_snapshot':prefix+'local-commit/upstream-snapshot.json','baseline_commit':'e3d126c2d7569345cf5f790310702eb00cd86b06','local_status':'implemented_locally','engineering_review':'agent_technical_review_complete_human_acceptance_pending','evidence_manifest':prefix+'artifact-manifest.json','record':prefix+'README.md','patch':prefix+'final-review/verification-run/communication-1167.patch','patch_sha256':sha(P/'final-review/verification-run/communication-1167.patch'),'pr_draft':prefix+'submission/PR-BODY.md','pr_title':prefix+'submission/PR-TITLE.txt','upstream_pr_url':None,'merge_commit':None,'submission_candidate':False,'scope':'Dedicated QM LoLa idempotency integration test for five public APIs; full native baseline suite passes; 204 inherited copyright findings and 6 skips retained; human acceptance pending.','full_suite':{'passed':503,'failed':0,'skipped':6},'focused_tests_passed':2,'copyright':{'findings':204,'added':0,'status':'failed_baseline_identical'},'eclipse_username':'jnascimento6p0','eca_status':'signed_eca_confirmed_by_official_username_lookup','publication':'withheld_by_user','native_run_id':'01M4878Q65ENC6PJ5AEJ6NMWB3'});v['updated_on']='2026-10-06';write(registry,v)
readme=W/'contributions/README.md';t=readme.read_text();row='| [Communication #1167](communication-1167/README.md) | Dedicated COM API idempotency integration test | Agent review complete; 503 full-suite tests pass, 6 skipped; 204 inherited copyright findings retained | Issue open; ECA confirmed; formal acceptance pending; push withheld |\n';needle='\nThe first two rows are completed local implementations';assert needle in t;t=t.replace(needle,'\n'+row+needle,1);readme.write_text(t)
# Original index/staged work remains untouched: this worktree owns its own index.
git(W,['add','--force','--','contributions/communication-1167','contributions/README.md','contributions/registry.json'])
entries=git(W,['ls-files','--stage','--','contributions/communication-1167']).splitlines();assert len(entries)==len(relatives);assert not any(x.startswith('160000 ') for x in entries)
changes=git(W,['diff','--cached','--name-only']).splitlines();assert all(x.startswith('contributions/communication-1167/') or x in {'contributions/README.md','contributions/registry.json'} for x in changes)
print(json.dumps({'branch':BRANCH,'worktree':str(W),'base':BASE,'staged_files':len(changes),'portable_artifact_files':len(relatives),'scope_verified':True,'submodules_created':0,'pushed':False}),flush=True)
