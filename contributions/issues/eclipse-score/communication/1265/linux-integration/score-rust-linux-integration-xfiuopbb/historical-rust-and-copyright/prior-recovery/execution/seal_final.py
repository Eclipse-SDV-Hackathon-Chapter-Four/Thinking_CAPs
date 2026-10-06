from pathlib import Path
import datetime,hashlib,json,shutil,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-upcaieyc');validate_run_root(r)
out=Path(json.loads((r/'contribution.json').read_text())['path']);c=out.parent.parent
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report=json.loads((out/'verification-report.json').read_text());report['native_build_failure']='Pinned Ferrocene rustc/librustc_driver needs missing GLIBCXX_3.4.32 and GLIBC_2.36/2.38/2.39 while compiling the rules_rust tinyjson host-tool dependency; measured host glibc2.35.'
(out/'verification-report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
readme=(out/'README.md').read_text().replace('where the pinned Ferrocene compiler required GLIBC2.36/2.38/2.39','where the pinned Ferrocene compiler required GLIBCXX_3.4.32 and GLIBC2.36/2.38/2.39');(out/'README.md').write_text(readme)
(out/'supervisor-review.md').write_text('''# Read-only agent supervisor review

Reviewer: `/root/rust_issue_supervisor`; task explicitly requested by user.
This is agent supervision, not authorized human engineering acceptance.

Pre-launch audit found no blocker: all19 frozen configuration bindings and2879
candidate hashes matched; source-backed SHA512 payload and exact128hex canonical
marker verified. The internal coding-standards.yaml symlink was preserved exactly.
Fresh storage bound to device1793 after the historical device1819 guard refused.
Original175 and paused253 manifests remained unchanged. No private state, queues
or previous build outputs were imported. Graph command-only, no LLM/human nodes,
no automatic retries, with explicit title, private server state and sbin PATH.

Terminal review confirmed run01M482VTQYK6T74SS0SVTPGCX4 completed analysis then
failed loading the pinned compiler while compiling rules_rust tinyjson host-tool
dependency. Missing symbols: GLIBCXX_3.4.32 and GLIBC_2.36/2.38/2.39. This is a
build/environment failure, not test assertions or demonstrated API incompatibility.
Zero of three tests executed: concept-test FAILED TO BUILD, both macro targets
NO STATUS/skipped. Copyright was not reached. Bazel32.545s; collector34.181s,
exit1. Worker preflight succeeded; verify/export failed. Export nevertheless retained
the failure evidence and reported failure truthfully. Models empty; tokens zero.
Owned private server shutdown recorded. All bound inputs and source hashes remained
unchanged and storage validation passed at terminal review.

Recovery correction budget3/3 exhausted, zero remaining. Import preparation's
strict symlink refusal and tools-directory restart refusal are retained as part of
the same incomplete import correction2. Cache remedy used correction3. No further
fix, automatic retry or relaunch. Human acceptance stays pending offline. A future
compatible-userspace run requires a separately authorized budget and exact pins.
''')
(out/'pr-description.md').write_text('''Document the Rust COM API's existing pastey0.2.3 dependency, configured features,
generated identifier patterns and API consumers. Add a source-bound assessment of
provenance, licensing, maintenance, safety artifacts and qualification obligations,
with paste/pastey/internal alternatives and replacement compatibility checks. The
proposed disposition retains the current dependency pending offline engineering
review; production Rust, dependencies, APIs, locks and policies are unchanged.

Validation: the documentation patch applies cleanly to communication commit
e3d126c2d7569345cf5f790310702eb00cd86b06. Supervised native run
01M482VTQYK6T74SS0SVTPGCX4 completed analysis but failed loading the pinned
compiler because GLIBCXX_3.4.32 and GLIBC symbols through2.39 are unavailable on
the measured GLIBC2.35 host. Zero of three selected tests executed; copyright
was not reached. Full failed evidence is retained; recovery3/3 fixes exhausted.
Compiler qualification/use-case scope, communication adoption, QNX, full CI and
human engineering acceptance remain pending. The issue remains open.
''')
x=json.loads((c/'upstream-snapshot.json').read_text());issue=json.loads((out/'issue-1265-current.json').read_text())
x.update({'captured_on':'2026-10-06','state':issue['state'],'updated_at':issue['updated_at'],'title':issue['title']});(out/'upstream-snapshot.json').write_text(json.dumps(x,indent=2)+'\n')
observation=c/'verification-recovery/resume-20261006T073841Z'
(observation/'resolution.json').write_text(json.dumps({'status':'superseded_by_completed_bounded_run','SSD_reconnected':True,'old_guard_refused_device_change':True,'new_root':str(r),'latest_record':'../score-fabric-upcaieyc/README.md','budget_final':3,'native_tests_executed':0,'failure':'Pinned compiler userspace incompatible; GLIBC and GLIBCXX symbols missing.'},indent=2)+'\n')
validation={'cache_helper_AST':'passed','cache_helper_Ruff_F':'passed','helper_executed_later_in_fresh_external_root':True,'final_native_run_status':'failed','no_further_native_fix':True}
(observation/'preparation-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
def seal(folder):
 files={str(p.relative_to(folder)):h(p) for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'artifact-manifest.json' and p!=folder/'artifact-sizes.json'}
 sizes={name:(folder/name).stat().st_size for name in files}
 (folder/'artifact-sizes.json').write_text(json.dumps({'files':sizes,'total_bytes':sum(sizes.values()),'excludes':'This size inventory and root manifest; nested manifests included.'},indent=2)+'\n')
 files['artifact-sizes.json']=h(folder/'artifact-sizes.json')
 (folder/'artifact-manifest.json').write_text(json.dumps({'schema_version':1,'kind':'portable_subject_hash_manifest','files':files},indent=2)+'\n')
 for name,expected in files.items():assert h(folder/name)==expected,name
 return {'manifest_sha256':h(folder/'artifact-manifest.json'),'subjects':len(files)}
initial=seal(observation)
for p in observation.iterdir():
 if p.is_file():q=out/'initial-resume-observation'/p.name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q)
shutil.copyfile(Path('/tmp/rust-resume-xndyh_w9/package_final.py'),out/'execution/package_final.py')
shutil.copyfile(Path('/tmp/rust-resume-xndyh_w9/seal_final.py'),out/'execution/seal_final.py')
for name in ['offline-packaging-result.json','recovery-allocation.json']:
 shutil.copyfile(r/name,out/'execution'/name)
secret=json.loads((Path(json.loads((r/'server-binding.json').read_text())['private_state'])/'secrets.json').read_text())['token'].encode()
for p in out.rglob('*'):
 if p.is_file():assert secret not in p.read_bytes(),str(p)
sealed=seal(out)
(r/'final-packet-receipt.json').write_text(json.dumps({'path':str(out),**sealed,'initial_resume_packet':initial},indent=2)+'\n')
print(json.dumps({'packet':str(out),**sealed,'initial_resume_packet':initial}))
