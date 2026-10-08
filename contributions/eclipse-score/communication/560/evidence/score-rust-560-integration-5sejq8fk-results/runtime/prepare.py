from pathlib import Path
import json,hashlib,shutil,subprocess,os
from datetime import datetime,timezone
from score_sw_fabric.storage import validate_run_root
R=Path(__file__).parent
OLD=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-rust-560-resume-wm0jdkb8')
PLAN=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue/score-rust-560-integration-plan-bqfe04r8-v2')
W=R/'workspaces/560'; J=R/'jobs/560'; D=R/'definitions-linux/560'
B=Path('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro'); PYTHON='/home/jefferson/s-core_sw_fabric/.venv/bin/python'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
validate_run_root(R);validate_run_root(OLD)
sources=json.loads((PLAN/'context/final-source-hashes.json').read_text())
for rel,h in sources.items():assert sha(OLD/'workspaces/560'/rel)==h,rel
W.parent.mkdir(exist_ok=True);J.mkdir(parents=True);D.mkdir(parents=True)
cmd=['git','-c','core.hooksPath=/dev/null','clone','--no-hardlinks','--no-local',str(OLD/'workspaces/560'),str(W)]
p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
subprocess.run(['git','-C',str(W),'config','core.hooksPath','/dev/null'],check=True)
subprocess.run(['git','-C',str(W),'config','user.name','Rust workflow draft'],check=True)
subprocess.run(['git','-C',str(W),'config','user.email','rust-workflow-draft@invalid.local'],check=True)
for rel,h in sources.items():assert sha(W/rel)==h,rel
incoming=subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip()
# No build links or caches are cloned. Preserve the entire previous source/check history as carried context.
context=W/'.rust-queue/context';reports=W/'.rust-queue/reports';context.mkdir(parents=True,exist_ok=True);reports.mkdir(parents=True,exist_ok=True)
shutil.copytree(PLAN,context/'integration-plan',ignore=shutil.ignore_patterns('context'),dirs_exist_ok=False)
for name in ['supervisor.md','correction-2.md','native-check-summary.json']:
 shutil.copyfile(PLAN/'context'/name,reports/('carried-'+name))
(reports/'supervisor.md').unlink(missing_ok=True)
(reports/'correction-3.md').unlink(missing_ok=True)
save(reports/'native-check-summary.json',{'kind':'carried_previous_run','fresh_execution':False,'passed':True,'production_callback_coverage':'missing','source_subjects':2186,'source_vector_sha256':sha(PLAN/'context/final-source-hashes.json'),'prior_run_id':'01M4927N232FTNWEFCRTJQG7PE','acceptance':'pending offline','details':'carried-native-check-summary.json'})
for name in ['issue.json','comments.json']:
 src=OLD/'workspaces/560/.rust-queue/context'/name
 shutil.copyfile(src,context/name)
for name in ['driver_linux.py','tool_guard.py','linux_launcher.py','runtime_manager.py','storage.py','submit_queue.py','collect_terminal.py','finish_review.py','linux-tools.json','runtime-overlays.json']:
 shutil.copyfile(OLD/name,R/name)
# Third attempt is explicitly authorized to implement the bound production integration plan,
# rather than the old graph's conditional compiler-error recovery.
p=R/'driver_linux.py';s=p.read_text();start=s.index('    if n == 3:\n');end=s.index("    value['used'] = n",start)
s=s[:start]+"    assert n == 3 and control['historical_corrections_used'] == 2\n    assert control['integration_plan_sha256'] == sha(Path(control['integration_plan']))\n"+s[end:]
# Preserve all incoming native subjects; source writes are restricted to the new test package.
needle="    plan = json.loads(plan_file.read_text())\n"
s=s.replace(needle,"    for relative, expected in json.loads((job / 'baseline-hashes.json').read_text()).items():\n        assert sha(workspace / relative) == expected, ('Existing native source changed outside test scope', relative)\n"+needle)
p.write_text(s)
p=R/'tool_guard.py';s=p.read_text().replace("source = relative.startswith('score/mw/com/')","source = relative.startswith('score/mw/com/test/basic_rust_api/subscription_state_apis/')")
s=s.replace("if relative == '.rust-queue/reports/native-check-summary.json':","if relative == '.rust-queue/reports/native-check-summary.json' or relative.startswith('.rust-queue/reports/carried-'):")
p.write_text(s)
# New scripts self-bind their root, and the historical scripts remain unchanged.
(R/'linux_launcher.py').chmod(0o755)
shutil.copytree(OLD/'repository-cache',R/'repository-cache',symlinks=False)
validate_run_root(R);validate_run_root(OLD)
save(J/'baseline-hashes.json',sources)
ledger=json.loads((OLD/'jobs/560/correction-ledger.json').read_text());assert ledger['used']==2 and ledger['remaining']==1;save(J/'correction-ledger.json',ledger)
control=json.loads((OLD/'jobs/560/task.json').read_text());control.update(workspace=str(W),incoming_head=incoming,historical_corrections_used=2,integration_plan=str(PLAN/'integration-plan.md'),integration_plan_sha256=sha(PLAN/'integration-plan.md'),control_hashes={})
authority={'user_request':'go using fabro and deepseek-flash run','recorded_at':datetime.now(timezone.utc).isoformat(),'issue':560,'activity':'Implement and verify bound production callback integration plan using final lifetime source correction','historical_corrections_used':2,'max':3,'remaining_before_run':1,'no_correction_loop':True,'provider':'deepseek','model':'deepseek-flash','fallbacks':False,'supervisor':'read-only DeepSeek Flash','publication':False,'acceptance':'offline pending','source_scope':'score/mw/com/test/basic_rust_api/subscription_state_apis/','plan_manifest_sha256':sha(PLAN/'artifact-manifest.json')}
save(R/'execution-authority.json',authority)
save(R/'linux-measurement-binding.json',{'launcher':str(R/'linux_launcher.py'),'sha256':sha(R/'linux_launcher.py')})
for f in ['driver_linux.py','tool_guard.py','storage.py','linux_launcher.py','execution-authority.json','linux-measurement-binding.json']:
 control['control_hashes'][str(R/f)]=sha(R/f)
save(J/'task.json',control);save(context/'task.json',control)
save(R/'incoming-source-binding.json',{'source_vector_sha256':sha(PLAN/'context/final-source-hashes.json'),'source_subjects':len(sources),'incoming_head':incoming,'previous_workspace':str(OLD/'workspaces/560'),'incoming_native_configuration_sha256':json.loads((PLAN/'context/native-input-binding.json').read_text())['configuration_sha256'],'clone_command':cmd,'hooks':'inspected no active hook files, inherited core.hooksPath=/dev/null; disabled on clone','prior_packet':str(PLAN),'existing_queue_changed':False})
new='//score/mw/com/test/basic_rust_api/subscription_state_apis'
checks=[
 {'kind':'build','config':'linux_x64','targets':[new+':subscription-state-apis'],'reason':'Build dedicated production LoLa two-process integration binary','native_obligation':'Issue560, native production callback contract; integration-plan.md'},
 {'kind':'test','config':'linux_x64','targets':[new+'/integration_test:test_subscription_state_apis','//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync','//score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test:test_com_api_async'],'reason':'Five new callback/lifecycle cases plus six existing sample regressions; uncached Linux Docker execution','native_obligation':'Supervisor O12/G8 and G6/G7; production path rather than mock substitution'},
 {'kind':'lint','config':'clippy','targets':[new+':subscription-state-apis'],'reason':'Native Clippy on newly written executable/test harness; measure actual aspect execution','native_obligation':'Native quality/static_analysis/static_analysis.bazelrc clippy_strict'},
 {'kind':'query','config':'linux_x64','targets':[new+':subscription-state-apis',new+'/integration_test:test_subscription_state_apis'],'reason':'Explicit label discovery, not reverse-dependency completeness','native_obligation':'Resolve newly implemented BUILD labels; complete downstream set stays unknown'},
]
save(reports/'check-plan.json',{'checks':checks});save(J/'prior-check-plan.json',json.loads((OLD/'jobs/560/prior-check-plan.json').read_text()))
save(J/'carried-prior-check-summary.json',json.loads((PLAN/'context/native-check-summary.json').read_text()))
save(R/'plan-normalization.json',{'status':'new production targets proposed before implementation; driver resolves via real Bazel execution after draft','old_obligations':'carried only through verified unchanged source/control hashes','new_case_names':[c['name'] for c in json.loads((PLAN/'case-specifications.json').read_text())['cases']],'checks':checks})
base_prompt='Use DeepSeek Flash only with no fallback. File tools only; no shell, delegation, credentials or publication. Human engineering acceptance stays offline and pending. read_file limit <=200; grep output_mode files_with_matches or count. Read .rust-queue/context/task.json and score-rust-workflow/SKILL.md plus native verification guidance. Preserve native pins, policy, source IDs and notices. Existing source writes are forbidden; only score/mw/com/test/basic_rust_api/subscription_state_apis/ and .rust-queue/reports/ are writable. Protected/native/carried summaries must not be edited. No QNX. '
fix=base_prompt+'This is source correction3, the FINAL lifetime attempt (historical1 failed,2 passed; failures still count). Read .rust-queue/context/integration-plan/integration-plan.md in full bounded sections and the bound case specifications. Implement all five Linux production callback cases following that plan. Write BUILD, controller/provider Rust source and integration_test/BUILD plus pytest wrapper under the dedicated test package. EXACT target labels: '+new+':subscription-state-apis and '+new+'/integration_test:test_subscription_state_apis. Use real score_com LoLa runtime, existing MixedPrimitivesInterface and generated C++ registration, native config/package rule and Linux Docker integration_test. Inspect and follow actual native APIs/macros/BUILD and existing Rust binaries for valid imports, linker features/flags and initialization. No dependency/policy changes, mock bridge, direct trampoline calls or simulated notifications. Controller owns native handles; separate provider child with acknowledged withdrawal/reoffer, deadlines, flushed prefixed protocol, drained diagnostics and owned process cleanup. No initial callback is promised by registration. Callback only records nonblocking observations and returns bool; never calls the same subscription. Capture DropProbe resources and assert once-only disposal; callback receipt is not disposal fence. Include all five named cases and positive controls exactly as planned. Keep check-plan.json explicit native schema already supplied; do not remove checks to pass. You have one implementation stage then deterministic verification; no post-verification correction is authorized. Review your own source for compile/ownership/trait inference issues before ending this stage. Write .rust-queue/reports/correction-3.md with actual paths, rationale, source-derived decisions, unmeasured limits and structured status. Do not claim executed checks. If blocked, write a concrete blocker and preserve failures.'
review=base_prompt+'Read-only supervisor: write ONLY .rust-queue/reports/supervisor.md. Read integration plan, correction-3.md, actual new sources/BUILD/pytest, native-check-summary.json and carried supervisor. Review all five cases independently: actual real LoLa Rust->C++->Rust callback invocation; coordination and deadlines; replacement; explicit unset; false then drop; active drop; captured resource disposal; process cleanup; trait imports/lifetimes; compiler/test/lint measured results. Separate carried unit/docs/C++ evidence from freshly executed cases and omitted/failed checks. Verify case-count denominator and no mocked notification substitute. Retain unresolved concurrency/ownership-on-failure/trace/qualification/example/downstream obligations and pending offline acceptance. No source fixes even if checks fail: final correction budget is exhausted.'
def node(name,typ,script=None,prompt=None,timeout='60s'):
 attrs={'type':typ,'max_retries':0,'on_failure':'route','timeout':timeout}
 if script:attrs['script']=script
 if prompt:attrs.update(prompt=prompt,model='deepseek-flash',provider='deepseek',reasoning_effort='high',max_tokens=32000,output_retries=0,max_visits=1,project_memory=False)
 return '  '+name+' ['+', '.join(k+'='+ (str(v).lower() if isinstance(v,(bool,int)) else json.dumps(v)) for k,v in attrs.items())+'];\n'
graph='digraph Rust560ProductionIntegration {\n  graph [goal="Implement and verify real Linux Rust subscription-state callback integration within last correction", default_max_retries=0, max_node_visits=1, on_failure="route"];\n  start [type="start"];\n  exit [type="exit"];\n'
for name,action in [('preflight','preflight 560'),('reserve3','reserve 560 3'),('check3','check 560 3'),('export','export 560')]:graph+=node(name,'command',script=PYTHON+' '+str(R/'driver_linux.py')+' '+action,timeout='3600s' if name=='check3' else '60s')
graph+=node('fix3','agent',prompt=fix,timeout='900s')+node('supervisor','agent',prompt=review,timeout='900s')
graph+='''  start -> preflight;
  preflight -> reserve3;
  preflight -> export [condition="outcome=failed"];
  reserve3 -> fix3;
  reserve3 -> export [condition="outcome=failed"];
  fix3 -> check3;
  fix3 -> supervisor [condition="outcome=failed"];
  check3 -> supervisor;
  supervisor -> export;
  export -> exit;
}
'''
(D/'workflow.fabro').write_text(graph)
toml=(OLD/'definitions-linux/560/workflow.toml').read_text().replace(str(OLD),str(R));(D/'workflow.toml').write_text(toml)
package=json.loads((OLD/'jobs/560/workflow-version.json').read_text());package['files']['workflow.fabro']=graph;package['files']['workflow.toml']=toml
for name in ['driver_linux.py','linux_launcher.py','storage.py','tool_guard.py']:package['files']['support/'+name]=(R/name).read_text()
for directory in [D,J]:
 save(directory/'workflow-version.json',package);(directory/'workflow.fabro').write_text(graph);(directory/'workflow.toml').write_text(toml);save(directory/'task.json',control)
validation=subprocess.run([str(B),'--no-upgrade-check','validate',str(D/'workflow.fabro'),'--json'],capture_output=True,text=True)
save(D/'native-validation.json',{'exit_code':validation.returncode,'stdout':validation.stdout,'stderr':validation.stderr});save(J/'native-validation.json',{'exit_code':validation.returncode,'stdout':validation.stdout,'stderr':validation.stderr});assert validation.returncode==0,validation.stderr
save(R/'queue.json',{'queue_id':R.name,'status':'prepared_not_submitted','baseline':control['baseline'],'ownership':'Fabro owns execution; one-time isolated admission, no scheduler','jobs':[{'issue':560,'title':'Production Rust subscription-state callback Linux integration','url':'https://github.com/eclipse-score/communication/issues/560','job_root':str(J),'workspace':str(W),'mode':'implementation','max_source_corrections':3,'historical_corrections_used':2,'prerequisites_to_verify':[]}]})
# Direct host boundary checks verify restrictions, not native test readiness.
import importlib.util
spec=importlib.util.spec_from_file_location('integration_guard',R/'tool_guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
cases=[({'event':'pre_tool_use','cwd':str(W),'node_id':'fix3','tool_name':'write_file','tool_input':{'file_path':'score/mw/com/test/basic_rust_api/subscription_state_apis/app.rs'}},True),({'event':'pre_tool_use','cwd':str(W),'node_id':'fix3','tool_name':'write_file','tool_input':{'file_path':'score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs'}},False),({'event':'pre_tool_use','cwd':str(W),'node_id':'supervisor','tool_name':'write_file','tool_input':{'file_path':'.rust-queue/reports/supervisor.md'}},True),({'event':'pre_tool_use','cwd':str(W),'node_id':'supervisor','tool_name':'write_file','tool_input':{'file_path':'score/mw/com/test/basic_rust_api/subscription_state_apis/app.rs'}},False),({'event':'pre_tool_use','cwd':str(W),'node_id':'fix3','tool_name':'shell','tool_input':{'command':'true'}},False)]
for c,expected in cases:assert guard.allowed(c,'560') is expected
save(R/'guard-host-checks.json',{'checks':len(cases),'passed':True,'kind':'direct host boundary check; not native qualification'})
print(json.dumps({'root':str(R),'source_subjects_verified':len(sources),'graph_valid':True,'implementation_stages':1,'corrections_before':ledger['used'],'model':'deepseek-flash','prepared_only':True}))
