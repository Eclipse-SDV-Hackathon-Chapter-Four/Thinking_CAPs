"""Deterministic source boundaries, native Linux checks, complete patch export."""
import hashlib,json,subprocess,sys,re,shutil
from pathlib import Path
from storage import validate_run_root
R=Path(__file__).parent;W=R/'workspaces/250';B='381d43dec900ab6a9076f3f30e7bfbdee019e26e'
T=json.loads((R/'jobs/250/task.json').read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed(n):return Path(n).name not in T['protected_names'] and (n in T['allowed_files'] or any(n.startswith(p) for p in T['allowed_prefixes']))
def verify(unchanged=False):
 validate_run_root(R);subjects=json.loads((R/'source-subjects.json').read_text());changed=[]
 for n,s in subjects.items():
  if not (W/n).is_file() or digest(W/n)!=s:
   assert not unchanged and allowed(n),'Protected source changed: '+n
   changed.append(n)
 names=subprocess.check_output(['git','-C',str(W),'ls-files','-z','--cached','--others','--exclude-standard']).decode().split('\0')
 for n in names:
  if not n or n in subjects or n.startswith('.rust-queue/'):continue
  assert allowed(n),'Unapproved extra source: '+n
  changed.append(n)
 return subjects,sorted(set(changed))
action=sys.argv[1];subjects,changed=verify(action=='preflight')
if action=='preflight':
 result=subprocess.run([sys.executable,str(R/'runtime_manager.py'),'status'],capture_output=True,text=True)
 save(R/'preflight.json',{'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'verified_source_subjects':len(subjects)})
 assert result.returncode==0 and json.loads(result.stdout)['exit_code']==0
elif action=='check':
 assert not (R/'execution').exists(),'Single measured check invocation'
 plan=json.loads((R/'check-plan.json').read_text());extra=W/'.rust-queue/reports/regression-plan.json';gap=None
 if extra.exists():
  additions=json.loads(extra.read_text());assert set(additions)=={'checks'} and 0<len(additions['checks'])<=4
  for c in additions['checks']:
   assert c['kind']=='test' and c.get('config','linux_x64') in ['linux_x64','linux_x64_gcc_15']
   assert 0<len(c['targets'])<=6 and all(re.fullmatch(r'//score/mw/com/test/basic_rust_api/[A-Za-z0-9_/.-]+:[A-Za-z0-9_.+-]+',t) for t in c['targets'])
   c['native_obligation']='Issue250 actual positive Rust Any regression; applicability pending independent review'
  plan['checks']=additions['checks']+plan['checks']
 else:gap='Required dedicated positive Rust Any regression plan absent; compatibility tests cannot establish completion.'
 save(R/'effective-check-plan.json',plan)
 before={n:digest(W/n) for n in subjects if (W/n).is_file()};before.update({n:digest(W/n) for n in changed if (W/n).is_file()})
 save(R/'check-source-subjects.json',before)
 result=subprocess.run([sys.executable,str(R/'linux_launcher.py'),'--workspace',str(W),'--plan',str(R/'effective-check-plan.json'),'--output',str(R/'execution')],capture_output=True,text=True)
 verify();assert all((W/n).is_file() and digest(W/n)==s for n,s in before.items()),'Sources changed during checks'
 native=json.loads((R/'execution/native-result.json').read_text());ledger=json.loads((R/'correction-ledger.json').read_text())
 summary={'passed':native['passed'],'exit_code':result.returncode,'checks':native['checks'],'infrastructure_error':native.get('infrastructure_error'),'positive_regression_gap':gap,'planned_checks':plan['checks'],'changed_files':changed,'source_subject_vector_sha256':digest(R/'check-source-subjects.json'),'source_corrections_used':ledger['used'],'source_corrections_max':3,'acceptance':'pending_offline','note':'Dedicated positive regression is required; preserved raw output is authoritative, XML wrappers differ from Rust child cases.'}
 save(W/'.rust-queue/reports/native-check-summary.json',summary);save(R/'check-invocation.json',{'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
 print(json.dumps({'native_passed':native['passed'],'checks':len(native['checks']),'positive_regression_gap':gap,'changed_files':len(changed)}));raise SystemExit(result.returncode)
elif action=='export':
 d=R/'export';d.mkdir(exist_ok=False);shutil.copytree(W/'.rust-queue/reports',d/'reports')
 for n in changed:
  if (W/n).is_file():subprocess.run(['git','-C',str(W),'add','-N','--',n],check=True,capture_output=True)
 (d/'communication-250.patch').write_bytes(subprocess.check_output(['git','-C',str(W),'diff',B,'--','.',':(exclude).rust-queue']))
 final={n:digest(W/n) for n in subjects if (W/n).is_file()};final.update({n:digest(W/n) for n in changed if (W/n).is_file()});save(R/'final-source-subjects.json',final)
 save(d/'review-summary.json',{'issue':250,'mode':'proposed_implementation','changed_files':changed,'correction_ledger':json.loads((R/'correction-ledger.json').read_text()),'native_passed':json.loads((R/'execution/native-result.json').read_text())['passed'] if (R/'execution/native-result.json').exists() else False,'acceptance':'pending_offline','issue_closure_authorized':False});print(json.dumps({'exported':str(d),'changed_files':len(changed)}))
else:raise SystemExit('Unknown command stage')
