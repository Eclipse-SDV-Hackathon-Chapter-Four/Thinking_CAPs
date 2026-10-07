"""Bind terminal native results, failures and read-only review; no native actions."""
from pathlib import Path
import hashlib
import json
from collections import Counter
from score_sw_fabric.storage import validate_run_root

R = Path(__file__).parent
validate_run_root(R)
def read(p):
    return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def save(p, value):
    assert not p.exists(), 'Preserve prior reconciliation'
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

rid = read(R / 'queue.json')['jobs'][0]['run_id']
N = R / 'native-runtime' / rid
state = read(N / 'final-state.json')
projection = read(N / 'final-projection.json')
assert state['conclusion'] is not None
assert projection['lifecycle']['status']['kind'] in ['succeeded','failed','dead','cancelled']
events = read(N / 'event-collection.json')
assert events['terminal_lifecycle_present'] and not events['has_more']
subjects = read(R / 'final-source-subjects.json')
assert subjects == read(R / 'check-source-subjects.json')
assert all((R/'workspaces/1261'/p).is_file() and sha(R/'workspaces/1261'/p) == s for p,s in subjects.items())
assert (R/'supervisor-final.md').exists()
stages = {k: {'handler':v.get('handler'), 'completion':v.get('completion'), 'model':v.get('model')} for k,v in state['stages'].items()}
agents = [v for v in stages.values() if v['handler'] == 'agent']
assert len(agents) == 2
assert all(v['model']['provider']=='deepseek' and v['model']['model_id']=='deepseek-v4-flash' for v in agents)
assert state['conclusion']['total_retries']==0
native = read(R/'execution/native-result.json')
checks = [{'kind':v['kind'],'targets':v['targets'],'exit_code':v['exit_code'],'timed_out':v['timed_out'],'elapsed_seconds':v['elapsed_seconds'],'log_sha256':v['log_sha256']} for v in native['checks']]
analyzer = read(R/'analyzer-summary.json')
export = read(R/'export/review-summary.json')
counts = Counter()
for line in (N/'events.jsonl').open():
    row = json.loads(line)
    rec = row.get('item',{}).get('record',{})
    if rec.get('kind') in ['run.control_requested','run.control_completed']:
        counts[rec['kind']] += 1
ledger = read(R/'correction-ledger.json')
assert ledger['used']==ledger['max']==3
v = {'run_id':rid,'native_lifecycle':projection['lifecycle']['status'],
     'native_models':projection['models'],'native_usage':projection['usage'],
     'native_retries':state['conclusion']['total_retries'],'stages':stages,
     'failed_stages':{k:v['completion'] for k,v in stages.items() if v['completion'] and v['completion']['outcome']!='succeeded'},
     'events':events,'events_sha256':sha(N/'events.jsonl'),'control_events':dict(counts),
     'source_subjects':len(subjects),'source_vector_sha256':sha(R/'final-source-subjects.json'),
     'source_unchanged_since_measurement':True,'baseline_patch_files':export['changed_files'],
     'changed_this_correction':export['changed_files_this_correction'],
     'native_passed':native['passed'],'executed_checks':checks,
     'planned_groups':len(read(R/'effective-check-plan.json')['checks']),
     'required_regression_plan_present':export['required_regression_plan_present'],
     'library_clippy':{'reports':len(analyzer['reports']),'gaps':analyzer['gaps'],'findings':sum(len(x['findings']) for x in analyzer['reports']),'clean':analyzer['clean']},
     'codex_source_review_sha256':sha(R/'supervisor-source-review.md'),
     'codex_final_review_sha256':sha(R/'supervisor-final.md'),
     'source_allowance':{'used':3,'max':3,'remaining':0,'disposition':'STOP further issue1261 source work'},
     'original_queue_budget':{'used':35,'max':36,'remaining':1,'remaining_issue':173},
     'engineering_acceptance':'pending_offline','publication':False,
     'transport_controls':'Fresh initial context, no runtime steer/followup; previous replay bug remains unpatched; no output-limit causality claimed.',
     'semantic_disposition':'Independent Codex final review required; lifecycle success and native_passed do not establish issue completion.'}
save(R/'terminal-reconciliation.json',v)
(R/'terminal-reconciliation.md').write_text(
    '# Final #1261 terminal reconciliation\n\n'
    f"Native run `{rid}` is terminal: `{projection['lifecycle']['status']['kind']}`. Complete {events['records']} events retained and hash-bound. "
    f"Two native agent stages use only DeepSeek Flash; zero native retries. Native measured checks passed: `{native['passed']}`; "
    f"executed {len(checks)}/{v['planned_groups']} groups. Required regression plan present: `{v['required_regression_plan_present']}`. "
    'Read actual failed stages and complete native logs in the JSON; the lifecycle is an execution result, not issue completion.\n\n'
    f"All {len(subjects)} final source subjects match the measured vector and actual workspace. Complete baseline patch changes {len(export['changed_files'])} files. "
    'Codex source and final review hashes bind independent findings and limits. No Codex target source fixes, extra native test reruns or new model stages were performed.\n\n'
    'Issue1261 source allowance3/3 exhausted: STOP further source changes. Issue250 also3/3 stopped. Originalqueue35/36, remaining slot belongs only to173; separate560 Codex exception1/3 used remains560-only. "Succeeded" cannot erase compilation, behavior, evidence, applicability, trace, qualification or acceptance gaps. Engineering acceptance is pending offline. No publication, issue closure, merge, release or deployment.\n')
print(json.dumps({'run_id':rid,'native_passed':native['passed'],'failed_stages':list(v['failed_stages']),'source_subjects':len(subjects),'stop_source_work':True}))
