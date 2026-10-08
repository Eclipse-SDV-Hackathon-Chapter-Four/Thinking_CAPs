from pathlib import Path
import hashlib,json,shutil,subprocess,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-upcaieyc');validate_run_root(r)
out=Path(json.loads((r/'contribution.json').read_text())['path']);c=out.parent.parent
old=c/'verification-recovery/score-fabric-pste_44o'
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for source,folder,want in [(c,'prior-attempt','d455bbafc5b5a79df6f1786b0a7aa9a7b76558521ebc308a4c21a414c9600d92'),(old,'prior-recovery','2f60752a659f364ec7e0cafbeaa39dc99c16677a3aaac8b6155ddf9f4282df4a')]:
 manifest=source/'artifact-manifest.json';assert h(manifest)==want
 for name,expected in json.loads(manifest.read_text())['files'].items():
  p=source/name;assert h(p)==expected,name
  q=out/folder/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);assert h(q)==expected
 q=out/folder/'artifact-manifest.json';q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(manifest,q)
(r/'recovery-allocation.json').write_text(json.dumps({'prior_packet_manifest_sha256':'d455bbafc5b5a79df6f1786b0a7aa9a7b76558521ebc308a4c21a414c9600d92','paused_recovery_manifest_sha256':'2f60752a659f364ec7e0cafbeaa39dc99c16677a3aaac8b6155ddf9f4282df4a','fresh_root_after_remount':True,'private_state_and_queues_imported':False},indent=2)+'\n')
source=old/'execution/export_recovery.py';assert h(source)==json.loads((old/'artifact-manifest.json').read_text())['files']['execution/export_recovery.py']
s=source.read_text().replace('(PASSED|FAILED|TIMEOUT|NO STATUS|SKIPPED)(.*)$','(FAILED TO BUILD|PASSED|FAILED|TIMEOUT|NO STATUS|SKIPPED)(.*)$')
(r/'export_final.py').write_text(s)
proc=subprocess.run([sys.executable,str(r/'export_final.py')],capture_output=True,text=True)
(r/'offline-packaging-result.json').write_text(json.dumps({'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr},indent=2)+'\n');assert proc.returncode==0,proc.stderr
report=json.loads((out/'verification-report.json').read_text());report['native_tests_executed']=0;report['native_tests_selected']=3;report['native_build_failure']='Pinned Ferrocene compiler/librustc_driver requires unavailable GLIBC2.36/2.38/2.39 symbols; hostgetconf reports2.35.';report['public_dependency_cache_remedy_verified']=True;report['remaining_corrections']=0;report['stop_reason']='max_corrections_exhausted_after_terminal_native_failure';report['human_acceptance']='pending_offline';report['prior_recovery_preserved']='prior-recovery/';report['carried_evidence_note']='Historical175/253 packets and candidate inputs verified by subject hashes; their native results are historical, not fresh measurements.'
(out/'verification-report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
p=out/'sources/dependency-correction';p.mkdir(parents=True,exist_ok=True)
for name in ['download-utils-1.2.2.tar.gz','download-utils-source.json','Bazel-8.7.0-DownloadCache.java','locked-download-utils-cache-receipt.json']:
 shutil.copyfile(r/name,p/name)
for name in ['issue-1265-current.json','communication-head-current.json']:
 shutil.copyfile(Path('/tmp/rust-resume-xndyh_w9')/name,out/name)
proc=subprocess.run(['/usr/bin/getconf','GNU_LIBC_VERSION'],capture_output=True,text=True);(out/'host-glibc-measurement.json').write_text(json.dumps({'command':['/usr/bin/getconf','GNU_LIBC_VERSION'],'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'measurement_kind':'direct_host_diagnostic_after_failed_native_run'},indent=2)+'\n')
ledger=json.loads((out/'correction-ledger.json').read_text());ledger['status']='stopped_budget_exhausted';ledger['stop_reason']='Native compiler build failure; no correction4 or new run authorized.';(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
shutil.copyfile(out/'correction-ledger.json',out/'execution/final-correction-ledger.json')
(out/'README.md').write_text('''# Communication #1265 — assessment retained; native verification failed

The generic S-CORE Rust workflow is implemented and installed. The contribution
contains a documentation patch assessing the existing pastey0.2.3 dependency;
no Rust implementation, dependency version, API, lock or native policy changed.

Final supervised Fabro run `01M482VTQYK6T74SS0SVTPGCX4` completed with failed
lifecycle. Worker preflight passed. The exact locked download_utils1.2.2 cache
remedy passed source/SRI/payload/canonical-ID checks. Native analysis progressed
to compilation, where the pinned Ferrocene compiler required GLIBC2.36/2.38/2.39
symbols unavailable on the measured GLIBC2.35 host. **Zero of three selected
tests executed**: one failed to build, two were skipped. Copyright did not run.
Verification and export stages report failure; export retains the failure evidence.

Recovery fixes are exhausted at **3/3**. The supervisor audited bound inputs and
terminal evidence. No fourth fix or further native run was attempted. The private
server stopped; native provider usage is zero and its model list is empty.

See [verification report](verification-report.json), [correction ledger](correction-ledger.json),
[raw native log](execution/logs/communication-macro-tests.log),
[patch](communication-1265.patch), and [supervisor review](supervisor-review.md).
All original175 and paused253 subjects remain byte-exact under `prior-attempt/`
and `prior-recovery/`, including their manifests. These are explicitly carried
historical evidence, not fresh tests. The new workspace was allocated after the
reboot changed the mount device; immutable sources/public caches were hash-verified,
with no queues, private state or previous build outputs imported.

Offline engineering acceptance, compiler qualification/use-case evidence,
communication adoption, unavailable QNX and full CI remain pending as recorded.
The issue is open. No publication or accepted fix is claimed. Further native work
needs a compatible build environment and a newly authorized correction budget.
''')
description=(out/'prior-attempt/pr-description.md').read_text()
(out/'pr-description.md').write_text(description+'\n\nLatest native verification: supervised run01M482VTQYK6T74SS0SVTPGCX4 failed loading the pinned compiler because required GLIBC symbols through2.39 are absent on the2.35 host. Zero of three selected tests executed; copyright not run. Recovery3/3 fixes exhausted; retained full failure evidence and offline review obligations.\n')
secret=json.loads((Path(json.loads((r/'server-binding.json').read_text())['private_state'])/'secrets.json').read_text())['token'].encode()
for p in out.rglob('*'):
 if p.is_file():assert secret not in p.read_bytes(),str(p)
validate_run_root(r)
print(json.dumps({'packet':str(out),'run_id':report['run_id'],'native_tests_executed':0,'corrections_used':3,'historical_subjects_retained':428,'exporter':proc.returncode}))
