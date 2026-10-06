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
 for name,expected in json.loads((ROOT/'candidate-hashes.json').read_text()).items():
  assert digest(ROOT/'candidate'/name)==expected,'Candidate drift: '+name
 ledger=json.loads(Path(binding['correction_ledger']).read_text())
 assert ledger['corrections_used']<=3 and ledger['max_corrections']==3
 return binding

def execute(name,args,limit):
 bind();log=ROOT/'logs'/f'{name}.log';log.parent.mkdir(exist_ok=True)
 env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8',**build_environment(ROOT)}
 wrapper=['/usr/bin/bwrap','--die-with-parent','--ro-bind','/','/','--bind',str(ROOT),str(ROOT),'--tmpfs','/home/jefferson','--tmpfs','/tmp','--tmpfs','/var/tmp','--proc','/proc','--dev-bind','/dev','/dev','--chdir',str(ROOT/'candidate'),*args]
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

def verify():
 binding=bind();checks=[]
 prefix=[str(ROOT/'tools/bazel'),'--batch','--output_user_root='+str(ROOT/'bazel-output')]
 options=['--repository_cache='+str(ROOT/'repository-cache'),'--jobs=2','--color=no','--curses=no']
 targets=['//score/mw/com/rust/score_com_concept:score_com_concept-test','//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests','//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests']
 result=execute('communication-macro-tests',prefix+['test',*options,*targets],900);result['targets']=targets;checks.append(result)
 if result['exit_code']==0:
  checks.append(execute('native-copyright',prefix+['run',*options,'//:copyright.check'],300))
 else:
  checks.append({'name':'native-copyright','status':'not_run','reason':'Native macro command failed; preserve dependency/environment failure rather than repeat unresolved native closure.'})
 for name,reason in [('score-crates-pastey-tests','Separate upstream component tests not executed; published artifacts are source evidence, not fresh qualification measurements.'),('qnx','QNX toolchain/license unavailable; Linux cannot satisfy platform coverage.'),('full-native-ci','Documentation-only scoped assessment; whole-repository CI remains pending before upstream submission.'),('compiler-qualification','Certified compiler/use-case scope and communication adoption require offline evidence/decision.'),('dependency-advisories','No advisory database scan performed; maintenance metadata is not security clearance.'),('native-format','Native format rules cover Rust/C++/Python/Starlark; changed files are Markdown, checked as documentation inputs.')]:
  checks.append({'name':name,'status':'not_run' if name!='native-format' else 'not_applicable','reason':reason})
 bind()
 report={'schema_version':1,'issue':'eclipse-score/communication#1265','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'patch_sha256':binding['patch_sha256'],'candidate_source_count':2879,'production_rust_and_locks_unchanged':True,'engineering_acceptance':'pending_offline','provider_calls':0,'supervisor':'/root/rust_issue_supervisor','max_corrections':3,'corrections_used':json.loads(Path(binding['correction_ledger']).read_text())['corrections_used']}
 write('verification-results.json',report)
 print(json.dumps({'checks':[{k:c[k] for k in ('name','status','exit_code') if k in c} for c in checks],'engineering_acceptance':'pending_offline'}))
 return 0 if all(c['status']=='passed' for c in checks if 'exit_code' in c) else 1

def export():
 bind()
 if not (ROOT/'verification-results.json').exists():
  write('execution-export.json',{'verification_results_present':False,'verification_status':'missing_after_preflight_or_collector_failure','all_executed_checks_passed':False,'engineering_acceptance':'pending_offline'});return 1
 report=json.loads((ROOT/'verification-results.json').read_text())
 write('execution-export.json',{'verification_results_sha256':digest(ROOT/'verification-results.json'),'run_binding_sha256':digest(ROOT/'run-binding.json'),'check_inventory_export_complete':True,'all_executed_checks_passed':all(c['status']=='passed' for c in report['checks'] if 'exit_code' in c),'engineering_acceptance':'pending_offline','failed_checks_preserved':True})
 print('Bound verification export complete; offline engineering acceptance pending.')
 return 0 if all(c['status']=='passed' for c in report['checks'] if 'exit_code' in c) else 1
def preflight():
 bind()
 import shutil
 required=['losetup','lsblk','findmnt','git','bwrap']
 resolved={name:shutil.which(name) for name in required}
 assert all(resolved.values()),resolved
 write('native-worker-preflight.json',{'PATH':os.environ.get('PATH'),'resolved_tools':resolved,'storage_binding_validated':True,'candidate_hashes_validated':True,'provider_calls':0})
 print('Native worker storage/tool/source preflight passed.');return 0

if __name__=='__main__':sys.exit({'verify':verify,'export':export,'preflight':preflight}[sys.argv[1]]())
