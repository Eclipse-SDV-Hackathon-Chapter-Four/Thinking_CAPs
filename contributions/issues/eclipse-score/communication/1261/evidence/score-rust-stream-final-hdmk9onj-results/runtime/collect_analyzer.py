"""Collect existing measured lint outputs; never run an analyzer or count cached old reports."""
from pathlib import Path
import hashlib, json, shutil
from storage import validate_run_root
R=Path(__file__).parent
validate_run_root(R)
native=json.loads((R/'execution/native-result.json').read_text())
W=R/'workspaces/1261'
rows=[];gaps=[]
for check in native['checks']:
    if check['kind']!='lint':continue
    for target in check['targets']:
        path,name=target[2:].split(':')
        p=(W/'bazel-bin'/path/(name+'.AspectRulesLintClippy.report')).resolve()
        if not p.is_file():
            gaps.append({'target':target,'reason':'No actual report; executed lint command exit'+str(check['exit_code'])});continue
        assert p.is_relative_to(R/'bazel-output')
        dest=R/'analyzer-evidence'/path/(name+'.sarif.json')
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,dest)
        report=json.loads(dest.read_text())
        findings=[v for run in report.get('runs',[]) for v in run.get('results',[])]
        rows.append({'target':target,'source':str(p),'path':str(dest.relative_to(R)),
            'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
            'findings':[{'ruleId':v.get('ruleId'),'level':v.get('level'),'message':v.get('message')} for v in findings]})
if not rows and not gaps:gaps.append({'reason':'Lint group did not execute; no analyzer-cleanliness evidence'})
v={'reports':rows,'gaps':gaps,'clean':bool(rows) and not gaps and all(not x['findings'] for x in rows),
    'source_vector_sha256':hashlib.sha256((R/'check-source-subjects.json').read_bytes()).hexdigest(),
    'test_code_clippy':'unmeasured','cpp_static_analysis':'unmeasured','acceptance':'pending_offline'}
(R/'analyzer-summary.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps({'reports':len(rows),'gaps':gaps,'findings':sum(len(x['findings']) for x in rows)}))
