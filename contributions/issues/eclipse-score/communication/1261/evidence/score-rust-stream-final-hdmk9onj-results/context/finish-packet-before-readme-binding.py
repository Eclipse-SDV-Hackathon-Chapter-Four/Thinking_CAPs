"""Seal terminal source-read-only results and shut down only owned runtimes."""
import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import time
from pathlib import Path
import xml.etree.ElementTree as ET
from storage import validate_run_root

R=Path(__file__).parent
W=R/'workspaces/1261'
DEST=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue')/(R.name+'-results')
PY='/home/jefferson/s-core_sw_fabric/.venv/bin/python'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
validate_run_root(R)
assert not DEST.exists(),'Never replace a sealed packet'
q=json.loads((R/'queue.json').read_text());rid=q['jobs'][0]['run_id']
for folder in (R/'native-runtime').iterdir():
    assert json.loads((folder/'final-projection.json').read_text())['lifecycle']['status']['kind'] in ['succeeded','failed','dead','cancelled']
    assert json.loads((folder/'event-collection.json').read_text())['terminal_lifecycle_present']
assert (R/'supervisor-final.md').is_file(),'Independent Codex final review must exist'
subjects=json.loads((R/'final-source-subjects.json').read_text())
assert all(sha(W/p)==s for p,s in subjects.items()),'Final native source changed after export'
assert (R/'export/communication-1261.patch').exists()
native=json.loads((R/'execution/native-result.json').read_text())
groups=[]
for index,row in enumerate(native['checks']):
    group={k:row[k] for k in ['kind','operation','targets','config','exit_code','timed_out','elapsed_seconds','log_sha256']}
    group['target_summaries']=[];group['xml_cases']=[]
    bep=R/f'execution/check-{index}-events.jsonl'
    if bep.exists():
        for line in bep.open():
            e=json.loads(line)
            if 'testSummary' in e:group['target_summaries'].append({'label':e['id']['testSummary']['label'],**e['testSummary']})
    for rec in row.get('test_records',[]):
        p=Path(rec['path']);assert sha(p)==rec['sha256']
        relevant=[t for t in row['targets'] if str(p).endswith('/'+t[2:].replace(':','/')+'/test.xml')]
        if relevant:group['xml_cases'].append({'label':relevant[0],'path':str(p.relative_to(R)),'sha256':rec['sha256'],'suites':rec['suites'],'case_names':[a.attrib.get('name') for a in ET.parse(p).getroot().iter('testcase')]})
    group['unrelated_previous_xml_records_ignored']=len(row.get('test_records',[]))-len(group['xml_cases'])
    groups.append(group)
save(R/'verification-summary.json',{'passed':native['passed'],'executed_groups':groups,'planned_groups':len(json.loads((R/'effective-check-plan.json').read_text())['checks']),'source_subjects':len(subjects),'source_vector_sha256':sha(R/'final-source-subjects.json'),'source_unchanged':False,'source_corrections_this_run':1,'original_source_corrections':json.loads((R/'correction-ledger.json').read_text()),'acceptance':'pending_offline','note':'Only XML belonging to explicit targets is counted; prior copied test logs are not new cases.'})
b=json.loads((R/'server-binding.json').read_text());private=Path(b['private_state']);token=json.loads((private/'operator-secret.json').read_text())['token']
secrets=[token.encode()]
for line in Path('/home/jefferson/.config/sesn/deepseek.env').read_text().splitlines():
    for part in shlex.split(line,comments=True):
        if part.startswith('DEEPSEEK_API_KEY='):secrets.append(part.partition('=')[2].encode())
pid=b['pid'];proc=Path('/proc')/str(pid)
assert sha(proc/'exe')==b['fabro_sha256'] and os.getpgid(pid)==pid
environ=(proc/'environ').read_bytes().split(b'\0');assert ('FABRO_HOME='+str(private)).encode() in environ
for entry in environ:
    if entry.startswith(b'SESSION_SECRET='):secrets.append(entry.partition(b'=')[2])
os.killpg(pid,signal.SIGTERM)
deadline=time.monotonic()+8
while time.monotonic()<deadline:
    try:
        if (proc/'stat').read_text().split(') ',1)[1].split()[0]=='Z':break
    except FileNotFoundError:break
    time.sleep(.2)
members=[]
for p in Path('/proc').iterdir():
    if p.name.isdigit():
        try:
            if os.getpgid(int(p.name))==pid and (p/'stat').read_text().split(') ',1)[1].split()[0]!='Z':members.append(int(p.name))
        except (FileNotFoundError,ProcessLookupError,PermissionError):pass
assert not members,'Do not signal unrelated PIDs; inspect owned group'
save(R/'server-shutdown.json',{'owned_server_stopped':True,'pid':pid,'owned_group_running_members':members,'global_servers_modified':False})
subprocess.run([PY,str(R/'runtime_manager.py'),'stop'],check=True,capture_output=True)
def copy(p,d):
    assert not p.is_symlink()
    carry=b''
    with p.open('rb') as f:
        while chunk:=f.read(1024*1024):
            data=carry+chunk;assert not any(x and x in data for x in secrets),'Credential in export; refuse sealing'
            carry=data[-max(map(len,secrets)):]
    d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
DEST.mkdir()
for p in R.iterdir():
    if p.is_file() and p.suffix in ['.py','.json','.md']:copy(p,DEST/'runtime'/p.name)
for name in ['export','execution','context','native-runtime','jobs','analyzer-evidence']:
    for p in (R/name).rglob('*'):
        if p.is_file():copy(p,DEST/name/p.relative_to(R/name))
for p in (W/'.rust-queue/context').rglob('*'):
    if p.is_file():copy(p,DEST/'agent-context'/p.relative_to(W/'.rust-queue/context'))
for n in ['LICENSE','NOTICE','.bazelrc','.bazelversion','MODULE.bazel','MODULE.bazel.lock','CI.md','score/mw/com/rust/score_com_concept/BUILD','score/mw/com/rust/score_com_concept/interface_macros.rs','score/mw/com/rust/score_com_concept/lib.rs','score/mw/com/rust/score_com.rs','quality/static_analysis/static_analysis.bazelrc','score/mw/com/impl/instance_identifier.h','score/mw/com/impl/handle_type.cpp','score/mw/com/impl/handle_type.h','score/mw/com/impl/bindings/lola/service_discovery/known_instances_container.cpp','score/mw/com/impl/bindings/lola/service_discovery/flag_file_crawler.cpp','score/mw/com/impl/configuration/configuration.h','score/mw/com/impl/runtime.h','score/mw/com/impl/runtime.cpp','score/mw/com/impl/i_runtime.h','score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h','score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.cpp','score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs','score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs','score/mw/com/design/service_discovery/README.md']:
    copy(W/n,DEST/'native-context'/n)
tools=[]
for folder in (R/'bazel-output').glob('*/external/score_toolchains_rust++*'):
    for name in ['rustc','clippy-driver']:
        for p in folder.glob('bin/'+name):tools.append({'path':str(p),'sha256':sha(p),'qualification':'not established'})
save(DEST/'compiler-identities.json',tools)
state=json.loads((R/'native-runtime'/rid/'final-state.json').read_text())
projection=json.loads((R/'native-runtime'/rid/'final-projection.json').read_text())
save(DEST/'resume-outcome.json',{'issue':1261,'native_run_id':rid,'native_lifecycle':projection['lifecycle']['status'],'native_models':projection['models'],'usage':projection['usage'],'source_read_only':False,'source_corrections_this_run':1,'original_queue_budget':{'used':35,'max':36,'remaining':1},'remaining_by_issue':{'250':0,'1261':0,'173':1},'codex_560_exception':{'used':1,'max':3,'scope':'560 only'},'native_passed':native['passed'],'issue_implementation_complete':False,'measured_tests_executed':0,'required_regression_plan_present':(W/'.rust-queue/reports/regression-plan.json').exists(),'terminal_reconciliation_sha256':sha(R/'terminal-reconciliation.json'),'source_work_stopped_budget_exhausted':True,'engineering_acceptance':'pending_offline','issue_closed':False,'publication_performed':False,'owned_runtimes_stopped':True})
changed=json.loads((R/'export/review-summary.json').read_text())['changed_files']
for n in changed:
    if (W/n).is_file():copy(W/n,DEST/'changed-source'/n)
(DEST/'README.md').write_text('# Final bounded Rust discovery stream #1261\n\nBaseline381d43dec900ab6a9076f3f30e7bfbdee019e26e. NativeFabro uses onlyDeepSeekFlash in implementation andsupervisor stages, nofallback/retry. Codex read-only reports and terminalreconciliation are authoritative source/evidence dispositions; lifecycle success alone doesnotestablishbackendbehavior. Fullpatch/changedsource, allselectedrawchecks/SARIFs/nativeevents, provenance andownedshutdown remainunderstandablewithoutFabro.\n\nThisfinalsourceattempt charges original1261 correction2→3(max3); STOPfurther1261sourcework afterit eveniffailed/incomplete. #250alsoSTOP3/3; #173hasoneleft. Originalqueue35/36,oneleft;extraCodex5601/3ofseparatethree remains560only. NoCodex targetsourcefixes here. Previousfailed1261attempt isretained; freshinitialcontextwithallreviewguidanceandnoruntimefollowup removesobservedmalformedhistoryreplaytrigger, doesnotpatchcodecorguaranteeprovidercompletion.\n\nReadactualnative/sourceresults andmissing/unexecutedevidence. Configurednativeuniverse/unknowninterface/FFIownership/allocation/ABI/qualification/trace gaps cannotbeconvertedintoengineeringacceptance. Humanacceptanceremainsoffline;noissueclosure/publication/merge/release/deploymentauthorizedorperformed.\n')
manifest={'schema_version':1,'source_baseline':'381d43dec900ab6a9076f3f30e7bfbdee019e26e','acceptance':'pending_offline','files':{}}
for p in sorted(DEST.rglob('*')):
    if p.is_file():manifest['files'][str(p.relative_to(DEST))]=sha(p)
save(DEST/'artifact-manifest.json',manifest)
save(R/'packet-location.json',{'path':str(DEST),'payloads':len(manifest['files']),'manifest_sha256':sha(DEST/'artifact-manifest.json'),'native_passed':native['passed'],'source_corrections':1,'owned_runtimes_stopped':True})
print(json.dumps(json.loads((R/'packet-location.json').read_text())))
