"""Bound issue collector: deterministic checks; no acceptance or repair loop."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,sys,time
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import build_environment,validate_run_root
ROOT=Path(__file__).parent

def digest(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(name,obj):
 (ROOT/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def bind():
 validate_run_root(ROOT)
 binding=json.loads((ROOT/'run-binding.json').read_text())
 for name,expected in binding['files'].items():
  assert digest(ROOT/name)==expected,'Bound input drift: '+name
 for row in json.loads((ROOT/'runtime-overlays.json').read_text())['overlays']:
  assert (Path(row['source']).stat().st_mode & 0o777)==row['mode'],'Runtime mode drift'
  assert digest(Path(row['source']))==row['source_sha256'],'Runtime bytes drift'
  assert digest(Path(row['target']))==row['host_original_sha256'],'Host library drift'
 for name,expected in json.loads((ROOT/'candidate-hashes.json').read_text()).items():
  assert digest(ROOT/'candidate'/name)==expected,'Candidate drift: '+name
 for path,expected in binding['external_tools'].items():
  assert digest(Path(path))==expected,'External tool drift: '+path
 config=Path(binding['private_docker_config'])
 assert digest(config)==binding['private_docker_config_sha256'],'Docker configuration drift'
 ledger=json.loads(Path(binding['correction_ledger']).read_text())
 assert ledger['corrections_used']<=3 and ledger['max_corrections']==3
 return binding

def execute(name,args,limit):
 bind();log=ROOT/'logs'/f'{name}.log';log.parent.mkdir(exist_ok=True)
 env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8',**build_environment(ROOT)}
 wrapper=['/usr/bin/bwrap','--die-with-parent','--ro-bind','/','/','--bind',str(ROOT),str(ROOT),'--tmpfs','/home/jefferson','--tmpfs','/tmp','--tmpfs','/var/tmp','--proc','/proc','--dev-bind','/dev','/dev','--ro-bind',json.loads((ROOT/'docker-binding.json').read_text())['socket'],'/run/docker.sock',*[part for row in json.loads((ROOT/'runtime-overlays.json').read_text())['overlays'] for part in ('--ro-bind',row['source'],row['target'])],'--chdir',str(ROOT/'candidate'),*args]
 start=time.monotonic();timed_out=False
 with log.open('wb') as stream:
  process=subprocess.Popen(wrapper,env=env,stdout=stream,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
  try:
   while process.poll() is None:
    validate_run_root(ROOT)
    if time.monotonic()-start>limit:timed_out=True;os.killpg(process.pid,signal.SIGKILL);break
    time.sleep(2)
  except BaseException:
   os.killpg(process.pid,signal.SIGKILL);process.wait();raise
  process.wait()
 return {'name':name,'command':wrapper,'environment':env,'timeout_seconds':limit,'elapsed_seconds':round(time.monotonic()-start,3),'exit_code':process.returncode,'timed_out':timed_out,'status':'passed' if process.returncode==0 else 'failed','log':str(log.relative_to(ROOT)),'log_sha256':digest(log)}

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
 args=[str(ROOT/'tools/bazel'),'--batch','--output_user_root='+str(ROOT/'bazel-output'),'test','--repository_cache='+str(ROOT/'repository-cache'),'--jobs=2','--local_test_jobs=1','--color=no','--curses=no','--test_output=errors','--cache_test_results=no',*plan['targets']]
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
