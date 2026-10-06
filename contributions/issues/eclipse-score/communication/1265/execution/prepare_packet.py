from pathlib import Path
import hashlib,json,difflib,shutil,subprocess,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
root=Path(__file__).parent; validate_run_root(root)
out=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265')
changed=json.loads((root/'controls.json').read_text())['changed_paths']
parts=[]
for name in changed:
 old=root/'communication-source'/name; new=root/'candidate'/name
 for line in difflib.unified_diff(old.read_text().splitlines(keepends=True) if old.exists() else [],new.read_text().splitlines(keepends=True),fromfile='a/'+name if old.exists() else '/dev/null',tofile='b/'+name):
  parts.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
 dest=out/'candidate'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(new,dest)
patch=out/'communication-1265.patch';patch.write_text(''.join(parts))
check=subprocess.run(['git','apply','--check',str(patch)],cwd=root/'communication-source',capture_output=True,text=True)
(root/'patch-apply-check.json').write_text(json.dumps({'command':['git','apply','--check',str(patch)],'cwd':str(root/'communication-source'),'exit_code':check.returncode,'stdout':check.stdout,'stderr':check.stderr},indent=2)+'\n');check.check_returncode()
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((root/'baseline-hashes.json').read_text())
candidate={str(p.relative_to(root/'candidate')):h(p) for p in (root/'candidate').rglob('*') if p.is_file()}
delta=sorted(n for n in base.keys()|candidate.keys() if base.get(n)!=candidate.get(n))
assert delta==sorted(changed),delta
(root/'candidate-hashes.json').write_text(json.dumps(candidate,sort_keys=True,indent=2)+'\n')
(out/'candidate-hashes.json').write_text(json.dumps({n:{'sha256':candidate[n],'bytes':(root/'candidate'/n).stat().st_size} for n in changed},indent=2)+'\n')
controls={'target_commit':'e3d126c2d7569345cf5f790310702eb00cd86b06','changed_paths':changed,'source_count':len(base),'candidate_source_count':len(candidate),'patch_sha256':h(patch),'production_rust_and_locks_unchanged':True}
(root/'controls.json').write_text(json.dumps(controls,indent=2)+'\n')
for name in ['controls.json','baseline-hashes.json','patch-apply-check.json','fabro-source-bindings.json']:
 shutil.copyfile(root/name,out/name)
for source,name in [(root/'communication-source'/'LICENSE','communication-LICENSE'),(root/'communication-source'/'NOTICE','communication-NOTICE'),(root/'crate-sources'/'pastey-0.2.3'/'LICENSE-MIT','pastey-LICENSE-MIT'),(root/'crate-sources'/'pastey-0.2.3'/'LICENSE-APACHE','pastey-LICENSE-APACHE')]:
 dest=out/'licenses'/name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(source,dest)
shutil.copytree(root/'score-crates-source'/'docs'/'pastey',out/'sources'/'score-crates'/'docs'/'pastey',dirs_exist_ok=True)
for name in ['interface_macros.rs','BUILD','lib.rs']:
 dest=out/'sources'/'communication'/'score/mw/com/rust/score_com_concept'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/'communication-source'/'score/mw/com/rust/score_com_concept'/name,dest)
for name in ['pastey-0.2.3','paste-1.0.15']:
 shutil.copytree(root/'crate-sources'/name,out/'sources'/'crates'/name,dirs_exist_ok=True)
print(json.dumps(controls))
