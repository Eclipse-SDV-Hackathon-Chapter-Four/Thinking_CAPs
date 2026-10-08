"""Measure unchanged sources and preserve all outcomes; no source corrections."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from storage import validate_run_root
R=Path(__file__).parent
W=R/'workspaces/173'
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def verify():
    validate_run_root(R)
    subjects=json.loads((R/'source-subjects.json').read_text())
    for p,s in subjects.items():assert hashlib.sha256((W/p).read_bytes()).hexdigest()==s,'Source changed: '+p
    tracked=subprocess.check_output(['git','-C',str(W),'ls-files','-z']).decode().split('\0')
    assert set(x for x in tracked if x and (W/x).is_file() and not x.startswith('.rust-queue/'))==set(subjects)
    return len(subjects)
count=verify()
action=sys.argv[1]
if action=='preflight':
    result=subprocess.run([sys.executable,str(R/'runtime_manager.py'),'status'],capture_output=True,text=True)
    save(R/'preflight.json',{'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'verified_source_subjects':count})
    assert result.returncode==0 and json.loads(result.stdout)['exit_code']==0
elif action=='check':
    assert not (R/'execution').exists(),'One check invocation only; retain failures'
    result=subprocess.run([sys.executable,str(R/'linux_launcher.py'),'--workspace',str(W),'--plan',str(R/'check-plan.json'),'--output',str(R/'execution')],capture_output=True,text=True)
    verify()
    native=json.loads((R/'execution/native-result.json').read_text())
    summary={'passed':native['passed'],'exit_code':result.returncode,'checks':[{'kind':a['kind'],'targets':a['targets'],'config':a['config'],'exit_code':a['exit_code'],'elapsed_seconds':a['elapsed_seconds'],'log_sha256':a['log_sha256'],'bounded_tail':a['bounded_tail'],'test_records':a['test_records']} for a in native['checks']],'infrastructure_error':native.get('infrastructure_error'),'planned_checks':json.loads((R/'check-plan.json').read_text())['checks'],'source_subjects':count,'source_subject_vector_sha256':hashlib.sha256((R/'source-subjects.json').read_bytes()).hexdigest(),'source_unchanged':True,'source_corrections_this_run':0,'original_corrections_used':2,'original_corrections_max':3,'acceptance':'pending_offline','note':'Newly measured tests; no carried test evidence. Unexecuted checks are not passed.'}
    save(W/'.rust-queue/reports/native-check-summary.json',summary)
    save(R/'check-invocation.json',{'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    print(json.dumps({'native_passed':native['passed'],'checks':len(native['checks']),'source_unchanged':True}))
    raise SystemExit(result.returncode)
elif action=='export':
    dest=R/'export';dest.mkdir(exist_ok=False)
    shutil=__import__('shutil');shutil.copytree(W/'.rust-queue/reports',dest/'reports')
    (dest/'communication-173.patch').write_bytes(subprocess.check_output(['git','-C',str(W),'diff','381d43dec900ab6a9076f3f30e7bfbdee019e26e','--','.',':(exclude).rust-queue']))
    save(dest/'review-summary.json',{'issue':173,'mode':'assessment','source_unchanged':True,'verified_subjects':count,'source_corrections_this_run':0,'original_source_corrections_used':2,'original_source_corrections_max':3,'assessment_exists':(dest/'reports/assessment.md').is_file(),'supervisor_exists':(dest/'reports/supervisor.md').is_file(),'native_passed':json.loads((R/'execution/native-result.json').read_text())['passed'] if (R/'execution/native-result.json').exists() else False,'acceptance':'pending_offline','issue_closure_authorized':False})
    print(json.dumps({'exported':str(dest),'source_corrections':0}))
else:raise SystemExit('Unknown stage')
