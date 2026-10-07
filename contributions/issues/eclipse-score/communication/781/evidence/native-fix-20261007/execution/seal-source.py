from pathlib import Path
import subprocess,json,hashlib,os,datetime,shutil,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(Path('/tmp/communication-781-490-root.txt').read_text());validate_run_root(r)
base='c77751819b8885a902540dbef7f0fe25cf85d51c';records={}
def git(w,*args,**kwargs):
 p=subprocess.run(['git','-c','core.hooksPath=/dev/null',*args],cwd=w,capture_output=True,**kwargs)
 assert p.returncode==0,(args,p.stdout,p.stderr)
 return p.stdout
for i,label,title in [('781','final','Implement lifetime-bound MethodInArgPtr ABI owner'),('490','final-verified','Implement isolated Rust COM mock runtime')]:
 validate_run_root(r);w=r/'workspaces'/i; out=r/'export'/i;out.mkdir(parents=True,exist_ok=True)
 s=json.loads((r/'evidence'/i/label/'source-hashes.json').read_text())
 for rel,digest in s.items():assert hashlib.sha256((w/rel).read_bytes()).hexdigest()==digest,rel
 assert not json.loads((r/'evidence'/i/label/'result.json').read_text())['source_drift_paths']
 git(w,'diff','--check','HEAD')
 changed=git(w,'diff','--name-only','HEAD').decode().splitlines()+git(w,'ls-files','--others','--exclude-standard').decode().splitlines()
 assert all(x.startswith('score/mw/com/') for x in changed),changed
 git(w,'add','--',*changed)
 git(w,'commit','-m',title,'-m',f'Addresses eclipse-score/communication#{i}.')
 head=git(w,'rev-parse','HEAD').decode().strip();branch=git(w,'branch','--show-current').decode().strip();tree=git(w,'rev-parse','HEAD^{tree}').decode().strip()
 patch=git(w,'format-patch','--stdout',base+'..HEAD');(out/f'communication-{i}.patch').write_bytes(patch)
 git(w,'bundle','create',str(out/f'feature-{i}.bundle'),branch,'^'+base)
 verification=git(w,'bundle','verify',str(out/f'feature-{i}.bundle')).decode()
 idx=r/'context'/f'patch-check-{i}.index';env={**os.environ,'GIT_INDEX_FILE':str(idx)}
 git(w,'read-tree',base,env=env);git(w,'apply','--cached','--check',str(out/f'communication-{i}.patch'),env=env);git(w,'apply','--cached',str(out/f'communication-{i}.patch'),env=env)
 replay_tree=git(w,'write-tree',env=env).decode().strip();assert tree==replay_tree;idx.unlink()
 source={}
 for rel in changed:
  target=out/'changed-source'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(w/rel,target);source[rel]={'sha256':hashlib.sha256((w/rel).read_bytes()).hexdigest(),'size':(w/rel).stat().st_size}
 record={'baseline':base,'commit':head,'tree':tree,'branch':branch,'patch_sha256':hashlib.sha256(patch).hexdigest(),'bundle_sha256':hashlib.sha256((out/f'feature-{i}.bundle').read_bytes()).hexdigest(),'changed_files':source,'patch_application':{'exit_code':0,'replayed_tree':replay_tree,'matches_candidate_tree':True},'bundle_verification':verification,'source_matches_final_native_test_manifest':True,'source_matches_final_clippy_manifest':all(hashlib.sha256((w/x).read_bytes()).hexdigest()==h for x,h in json.loads((r/'evidence'/i/'lint-verified/source-hashes.json').read_text()).items()),'sealed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (out/'source-binding.json').write_text(json.dumps(record,indent=2)+'\n');records[i]=record
 print(i,head,'patch',len(patch),'files',len(changed),'replay matches')
(r/'context/final-source-bindings.json').write_text(json.dumps(records,indent=2)+'\n')
