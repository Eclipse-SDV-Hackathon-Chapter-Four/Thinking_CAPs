"""Bind the Linux integration check without changing native targets or policy."""
import hashlib
import json
import shutil
from pathlib import Path
from score_sw_fabric.storage import validate_run_root

r = Path(__file__).parent
old = r.parent / 'score-fabric-7r64z_kz'
validate_run_root(r)
validate_run_root(old)
head = json.loads((r / 'upstream-head.json').read_text())['sha']
targets = ['//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync', '//score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test:test_com_api_async']
expected = {'test_com_api_sync': ['test_bigdata_exchange', 'test_mixed_primitives_exchange', 'test_complex_struct_exchange'], 'test_com_api_async': ['test_bigdata_async_with_cancellation', 'test_bigdata_async_without_cancellation', 'test_bigdata_async_stream']}
(r / 'check-plan.json').write_text(json.dumps({'baseline': head, 'platform': 'native default Linux x86_64 GCC15 and pinned Ferrocene', 'targets': targets, 'expected_pytest_cases': expected, 'runtime': 'native Ubuntu24.04 OCI packages in owned rootless Docker; exact native DOCKER_HOST empty attribute retained; private endpoint mounted at /run/docker.sock in namespace', 'omissions': {'QNX': 'User requested Linux only', 'full_repository_CI': 'Focused Rust COM integration request; other suites are not run', 'sanitizers_and_coverage': 'No sanitizer/coverage configuration requested or measured', 'payload_layout_completeness': 'Native BigData opaque placeholders and sample-count checks do not validate every C++ layout or payload field'}, 'acceptance': 'pending offline'}, indent=2) + '\n')
original = (old / 'collector.py').read_text()
helper = original[:original.index('\ndef verify():')]
helper = helper.replace("assert (Path(row['source']).stat().st_mode & 0o777)==row['mode'],'Runtime mode drift'", "assert (Path(row['source']).stat().st_mode & 0o777)==row['mode'],'Runtime mode drift'\n  assert digest(Path(row['source']))==row['source_sha256'],'Runtime bytes drift'")
helper = helper.replace("ledger=json.loads(Path(binding['correction_ledger']).read_text())", "for path,expected in binding['external_tools'].items():\n  assert digest(Path(path))==expected,'External tool drift: '+path\n config=Path(binding['private_docker_config'])\n assert digest(config)==binding['private_docker_config_sha256'],'Docker configuration drift'\n ledger=json.loads(Path(binding['correction_ledger']).read_text())")
helper = helper.replace("'--dev-bind','/dev','/dev',", "'--dev-bind','/dev','/dev','--ro-bind',json.loads((ROOT/'docker-binding.json').read_text())['socket'],'/run/docker.sock',")
rest = '''
def preflight():
 bind()
 import runpy
 runtime=runpy.run_path(str(ROOT/'runtime_manager.py'))['status']()
 assert runtime['exit_code']==0,runtime
 docker=execute('private-docker-in-native-namespace',['/usr/bin/docker','info','--format','{{json .}}'],30)
 assert docker['exit_code']==0
 info=json.loads((ROOT/docker['log']).read_text())
 assert info['DockerRootDir']==str(ROOT/'docker-data')
 assert any('rootless' in value for value in info['SecurityOptions'])
 plan=json.loads((ROOT/'check-plan.json').read_text())
 query=execute('native-target-query',[str(ROOT/'tools/bazel'),'--batch','--output_user_root='+str(ROOT/'bazel-output'),'query','--repository_cache='+str(ROOT/'repository-cache'),'--color=no','--curses=no','--output=label_kind','set('+ ' '.join(plan['targets']) +')'],300)
 assert query['exit_code']==0
 raw=(ROOT/query['log']).read_text()
 assert all(target in raw for target in plan['targets'])
 write('native-worker-preflight.json',{'storage_binding_validated':True,'candidate_hashes_validated':True,'private_runtime':runtime,'socket_mapping':docker,'native_target_query':query,'actual_native_baseline':plan['baseline'],'provider_calls':0})
 print('Native Linux targets and private Docker endpoint verified.');return 0

def verify():
 binding=bind();plan=json.loads((ROOT/'check-plan.json').read_text())
 args=[str(ROOT/'tools/bazel'),'--batch','--output_user_root='+str(ROOT/'bazel-output'),'test','--repository_cache='+str(ROOT/'repository-cache'),'--jobs=2','--local_test_jobs=1','--color=no','--curses=no','--test_output=errors',*plan['targets']]
 check=execute('linux-rust-com-integration',args,3500);check['targets']=plan['targets']
 import xml.etree.ElementTree as ET
 measured=[]
 for target in plan['targets']:
  package,name=target[2:].split(':')
  folder=ROOT/'candidate/bazel-testlogs'/package/name
  xml=folder/'test.xml';log=folder/'test.log'
  record={'target':target,'expected_cases':plan['expected_pytest_cases'][name],'xml_present':xml.is_file(),'raw_test_log_present':log.is_file()}
  if xml.is_file():
   record['xml_sha256']=digest(xml);parsed=ET.parse(xml)
   suites=list(parsed.getroot().iter('testsuite'))
   record['suite_counts']=[{k:s.attrib.get(k) for k in ['name','tests','failures','errors','skipped','time']} for s in suites]
   record['cases']=[{'name':c.attrib.get('name'),'classname':c.attrib.get('classname'),'failure':c.find('failure') is not None,'error':c.find('error') is not None,'skipped':c.find('skipped') is not None} for c in parsed.getroot().iter('testcase')]
  if log.is_file():record['test_log_sha256']=digest(log)
  measured.append(record)
 bind()
 write('verification-results.json',{'schema_version':1,'issue':'eclipse-score/communication#1265','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[check],'native_test_records':measured,'baseline':plan['baseline'],'expected_cases':6,'patch_sha256':binding['patch_sha256'],'candidate_source_count':2879,'engineering_acceptance':'pending_offline','provider_calls':0,'supervisor':'/root/rust_issue_supervisor','max_corrections':3,'corrections_used':json.loads((ROOT/'correction-ledger.json').read_text())['corrections_used'],'omissions':plan['omissions']})
 print(json.dumps({'native_command':check['status'],'exit_code':check['exit_code'],'targets':2,'xml_records':[{'target':m['target'],'counts':m.get('suite_counts')} for m in measured]}))
 return check['exit_code']

def export():
 bind()
 p=ROOT/'verification-results.json'
 if not p.exists():write('execution-export.json',{'verification_results_present':False,'status':'failed_missing_measurements','engineering_acceptance':'pending_offline'});return 1
 report=json.loads(p.read_text());passed=all(c['status']=='passed' for c in report['checks'])
 write('execution-export.json',{'verification_results_sha256':digest(p),'run_binding_sha256':digest(ROOT/'run-binding.json'),'all_selected_native_checks_passed':passed,'failed_or_missing_checks_preserved':True,'engineering_acceptance':'pending_offline'})
 print('Native integration evidence exported; offline acceptance pending.');return 0 if passed else 1

if __name__=='__main__':sys.exit({'preflight':preflight,'verify':verify,'export':export}[sys.argv[1]]())
'''
(r / 'collector.py').write_text(helper + rest)
runner = (old / 'run-copyright3.py').read_text()
runner = runner.replace("attempt=r/'copyright3-recovery'", 'attempt=r')
runner = runner.replace("'communication1265_copyright3'", "'communication1265_linux_integration'")
runner = runner.replace('Communication #1265: copyright pathspec normalization', 'Communication #1265: Linux Rust COM integration')
runner = runner.replace("'1300'", "'3900'")
runner += "\n shutdown=subprocess.run([sys.executable,str(r/'runtime_manager.py'),'stop'],env=env,cwd=r,capture_output=True)\n save('runtime-shutdown-result.json',{'exit_code':shutdown.returncode,'stdout':shutdown.stdout.decode(errors='replace'),'stderr':shutdown.stderr.decode(errors='replace')})\n"
(r / 'run.py').write_text(runner)
graph = (old / 'workflow.fabro').read_text().replace(str(old), str(r)).replace('Measure documentation assessment against pinned native baseline', 'Measure native Rust COM integration on Linux')
graph = graph.replace('timeout="1m"', 'timeout="6m"', 1).replace('timeout="21m"', 'timeout="60m"')
(r / 'workflow.fabro').write_text(graph)
config = (old / 'workflow.toml').read_text().replace(str(old), str(r)).replace('Export scoped communication issue 1265 assessment with measured checks and preserved gaps', 'Export native Linux Rust COM integration measurements and pending offline acceptance')
(r / 'workflow.toml').write_text(config)
(r / 'workflow-version.json').write_text(json.dumps({'entrypoint':'workflow.fabro','files':{'workflow.fabro':graph,'workflow.toml':config},'workflow_dependencies':{}},indent=2)+'\n')
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
files = {p.relative_to(r).as_posix():sha(p) for p in sorted(r.iterdir()) if p.is_file() and p.name not in {'run-binding.json','correction-ledger.json'}}
for folder in ['runtime-libs','runtime-provenance','tools']:
    files.update({p.relative_to(r).as_posix():sha(p) for p in sorted((r/folder).rglob('*')) if p.is_file()})
docker = json.loads((r/'docker-binding.json').read_text())
private_config = docker['command'][2]
external = ['/usr/bin/bwrap','/usr/bin/docker','/usr/bin/dockerd','/usr/bin/dockerd-rootless.sh','/usr/bin/rootlesskit','/usr/bin/slirp4netns','/bin/bash']
binding={'files':files,'external_tools':{name:sha(Path(name)) for name in external},'private_docker_config':private_config,'private_docker_config_sha256':sha(Path(private_config)),'correction_ledger':str(r/'correction-ledger.json'),'patch_sha256':'eb687c1a36b054315970fdbb2a4833cbb5e9470fb30eb06e67a446ca87951c19','max_corrections':3,'baseline':head,'supervisor':'/root/rust_issue_supervisor','no_human_nodes':True,'automatic_retries':0,'paid_calls_authorized':False,'native_configuration':'unchanged default Linux x86_64 GCC15 and pinned Ferrocene','native_test_scope':targets,'Docker_endpoint_scope':'owned private rootless daemon mounted at default endpoint only inside child namespace','global_daemon_reconfigured':False}
(r/'run-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
validate_run_root(r)
print(json.dumps({'bound_files':len(files),'external_tools':len(external),'baseline':head,'targets':targets,'remaining_corrections':1}))
