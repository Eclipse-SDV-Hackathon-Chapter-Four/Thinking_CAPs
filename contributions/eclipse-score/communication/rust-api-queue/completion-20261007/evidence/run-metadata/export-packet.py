# Copyright (c) 2026 Eclipse SDV Hackathon Team
#
# Licensed under the Apache License, Version 2.0.
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import json,subprocess,hashlib,shutil,datetime,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from storage import validate_run_root
validate_run_root(ROOT)
WORK=ROOT/'workspaces/integrated'
DEST=Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/rust-api-queue/completion-20261007')
def sha(p):
 with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def cp(p,q): q.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,q)
assert (ROOT/'auxiliary-evidence/completed.json').is_file(), 'Remaining verification has not completed'
subjects=json.loads((ROOT/'resolved-subjects.json').read_text())
for x in subjects['files']: assert sha(WORK/x['path'])==x['sha256'],x['path']
patch=subprocess.check_output(['git','diff',subjects['baseline'],'--binary'],cwd=WORK)
assert hashlib.sha256(patch).hexdigest()==subjects['patch_sha256'],'Source changed after verification'
for name in ['ownership-regression','cfg-test-clippy','format-check','notice-changed','serial-integrations']:
 assert json.loads((ROOT/('resolved-'+name)/'native-result.json').read_text())['passed'],name
# A local unsigned commit records a review subject, not human approval or a rights attestation.
subprocess.run(['git','add','--',*[x['path'] for x in subjects['files']]],cwd=WORK,check=True)
message=ROOT/'candidate-commit-message.txt'
message.write_text('Add configured LoLa discovery, typed Any and subscription state APIs\n\nIntegrate Communication #1261 (configured scope), #250 and #560 on the\nrecorded current-main baseline. Preserve IRuntime and Runtime layout,\ncorrect callback transfer and strict diagnostic findings, and document\nthe public behavior and internal bridge migration.\n\nHuman engineering and IP review remain pending.\n\nAssisted-by: OpenAI GPT-6 through Codex\n')
subprocess.run(['git','-c','commit.gpgsign=false','commit','--file',str(message)],cwd=WORK,check=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WORK,text=True).strip()
subjects.update(candidate_commit=commit,branch='feature/rust-discovery-subscription-complete',engineering_acceptance='pending_offline',merge_ready=False)
save(DEST/'source-identity.json',subjects)
cp(ROOT/'resolved-candidate.patch',DEST/'communication-integrated.patch')
for x in subjects['files']: cp(WORK/x['path'],DEST/'source'/x['path'])
for name in ['LICENSE','NOTICE','CODEOWNERS']:
 p=WORK/name if name!='CODEOWNERS' else WORK/'.github/CODEOWNERS'
 if p.exists(): cp(p,DEST/'native-project'/name)
# Preserve the native submission instructions and gate definitions from the subject.
for name in ['CONTRIBUTING.md','.github/review_checklists.yml', '.github/workflows/_gcc.yml', '.github/workflows/_qcc.yml', '.github/workflows/_address_sanitizer.yml', '.github/workflows/_thread_sanitizer.yml']:
 p=WORK/name
 if p.is_file(): cp(p,DEST/'native-project'/name)
for p in (WORK/'.github/workflows').glob('*.yml'):
 cp(p,DEST/'native-project/.github/workflows'/p.name)
for name in ['.bazelrc','.bazelversion','MODULE.bazel','MODULE.bazel.lock','quality/sanitizer/sanitizer.bazelrc']:
 cp(WORK/name,DEST/'native-project'/name)
subprocess.run(['git','bundle','create',str(DEST/'communication-integrated.bundle'),subjects['branch'],'HEAD'],cwd=WORK,check=True)
p=subprocess.run(['git','bundle','verify',str(DEST/'communication-integrated.bundle')],cwd=WORK,capture_output=True,text=True)
(DEST/'bundle-verify.log').write_text(p.stdout+p.stderr); assert p.returncode==0
subprocess.run(['git','archive','--format=tar.gz','--prefix=communication/','--output='+str(DEST/'communication-source.tar.gz'),'HEAD'],cwd=WORK,check=True)
# All prior attempts remain history. Do not include mutable caches or daemon private state.
for p in ROOT.iterdir():
 if p.is_file() and (p.suffix in ['.json','.py','.patch'] or p.name=='candidate-commit-message.txt'):
  cp(p,DEST/'evidence/run-metadata'/p.name)
 elif p.is_dir() and ((p/'native-result.json').is_file() or p.name in ['planning','auxiliary-evidence']):
  shutil.copytree(p,DEST/'evidence'/p.name,dirs_exist_ok=True)
checks=[]
for prefix,progress in [('resolved-','resolved-progress.json'),('resolved-extended-','resolved-extended-progress.json')]:
 for entry in json.loads((ROOT/progress).read_text()):
  stage=prefix+entry['check']; result=json.loads((ROOT/stage/'native-result.json').read_text())
  item={'check':entry['check'],'stage':stage,'exit_code':entry['exit_code'],'passed':result['passed'],'source_patch_sha256':subjects['patch_sha256'],'result':'evidence/'+stage+'/native-result.json','executed_test_targets':[],'analyzer_findings':{},'analyzer_reports':{'sarif':0,'empty':0,'other':0},'infrastructure_error':result.get('infrastructure_error')}
  labels={}
  for events in (ROOT/stage).glob('*-events.jsonl'):
   for line in events.read_text().splitlines():
    event=json.loads(line)
    if 'testSummary' in event:
     identity=event.get('id',{}).get('testSummary',{})
     labels[identity.get('label','unknown')]=event['testSummary']
  for label,summary in sorted(labels.items()):
   test={'label':label,'status':summary.get('overallStatus'),'runs':summary.get('totalRunCount'),'cached':summary.get('totalNumCached')}
   if label.startswith('//') and ':' in label:
    directory,target=label[2:].split(':',1)
    log=ROOT/stage/'native-testlogs'/directory/target/'test.log'
    if log.exists():
     import re
     test['rust_test_result_lines']=re.findall(r'test result: [^\n]*',log.read_text(errors='replace'))
    xml=ROOT/stage/'native-testlogs'/directory/target/'test.xml'
    if xml.exists(): test['native_xml_suites']=[dict(n.attrib) for n in ET.parse(xml).getroot().iter('testsuite')]
   item['executed_test_targets'].append(test)
  import re
  stage_logs='\n'.join(log.read_text(errors='replace') for log in (ROOT/stage).glob('check-*.log'))
  item['skipped_test_targets']=sorted(set(re.findall(r'^(//\S+)\s+SKIPPED',stage_logs,re.M)))
  item['native_test_totals']=[{'executed':int(a),'selected':int(b)} for a,b in re.findall(r'Executed (\d+) out of (\d+) tests:',stage_logs)]
  for report in (ROOT/stage/'analyzer-artifacts').rglob('*.report'):

   try: data=json.loads(report.read_text())
   except (ValueError,OSError):
    item['analyzer_reports']['empty' if report.stat().st_size==0 else 'other']+=1
    continue
   item['analyzer_reports']['sarif']+=1
   for run in data.get('runs',[]):
    for finding in run.get('results',[]):
     level=finding.get('level','warning'); item['analyzer_findings'][level]=item['analyzer_findings'].get(level,0)+1
  checks.append(item)
aux=json.loads((ROOT/'auxiliary-evidence/results.json').read_text())
for x in aux: checks.append({'check':x['name'],'exit_code':x['exit_code'],'passed':x['exit_code']==0,'result':'evidence/auxiliary-evidence/results.json','source_patch_sha256':subjects['patch_sha256']})
import re
native_document_findings=[]
for p in (ROOT/'resolved-host-build/native-document-artifacts').rglob('validation.log'):
 match=re.search(r'FAILED \((\d+) error',p.read_text())
 if match: native_document_findings.append({'artifact':'evidence/resolved-host-build/native-document-artifacts/'+str(p.relative_to(ROOT/'resolved-host-build/native-document-artifacts')),'reported_errors':int(match.group(1))})
if native_document_findings:
 checks.append({'check':'Native semantic document validation','passed':False,'status':'reported_findings','result':'DOCUMENT-VALIDATION.md','findings':native_document_findings,'reason':'Semantic findings remain for native owner review despite nonfatal build actions'})
checks.append({'check':'QCC - Build & Test','passed':False,'status':'unavailable','reason':'Licensed QNX environment not available; no license contents read','result':'evidence/run-metadata/qnx-availability.json'})
save(DEST/'expected-checks.json',{'source':subjects,'checks':checks,'manual_and_excluded_inventory':'evidence/auxiliary-evidence/manual-inventory.log','full_test_inventory':'evidence/auxiliary-evidence/test-inventory.log','scope':'Direct local execution; no hosted statuses or human acceptance'})
rows=['| Check | Local result | Evidence |','| --- | --- | --- |']
for x in checks:
 result='pass' if x['passed'] else x.get('status','fail')
 executed=x.get('executed_test_targets',[])
 if executed: result+='; '+str(len(executed))+' executed targets'
 if x.get('skipped_test_targets'): result+='; '+str(len(x['skipped_test_targets']))+' skipped'
 findings=x.get('analyzer_findings',{})
 if findings: result+='; '+', '.join(str(v)+' '+k for k,v in findings.items())
 rows.append('| '+x['check']+' | '+result+' | ['+x['result']+']('+x['result']+') |')
(DEST/'CHECKS.md').write_text('# Measured checks\n\nBaseline: `'+subjects['baseline']+'`. Candidate: `'+commit+'`. Patch SHA-256: `'+subjects['patch_sha256']+'`.\n\n'+'\n'.join(rows)+'\n\nThe emitted build events identify executed test targets. Captured XML outside that executed set may be earlier test output and is not counted as a fresh execution. Manual targets, ignored cases and unavailable platform checks are recorded explicitly. Analyzer execution and report severity are separate facts. The native hosted analyzer job also uses Aspect CLI hold-the-line strategy and uploads reports; this collector does not assert that hosted status. Older attempts and source epochs are retained as history and are not substituted for these results.\n')
(DEST/'README.md').write_text('# Communication contribution completion packet\n\nIntegrated candidate for #1261 (configured LoLa deployments), #250 and #560 on current-main baseline `'+subjects['baseline']+'`. Discovery uses one selected configured instance deployment and quality level per LoLa type; type-only declarations without an instance deployment and entirely unconfigured interface types remain outside this contribution. The broader #1261 request remains open.\n\nCandidate: `'+commit+'`; patch SHA-256: `'+subjects['patch_sha256']+'`. The candidate is a local unsigned review commit; no PR has been published or merged.\n\nThe implementation resolves the competing bridge names, preserves IRuntime and Runtime layout, corrects callback ownership on new registrations, replaces unit errors and resolves strict diagnostics in changed code. Tests, detailed design and user examples accompany the changes.\n\n- [Measured checks](CHECKS.md) and [machine-readable inventory](expected-checks.json)\n- [Acceptance and design trace](ACCEPTANCE-TRACE.md)\n- [API/ABI and migration review](API-ABI-REVIEW.md)\n- [License-header audit](LICENSE-HEADERS.md)\n- [Diagnostic disposition](WARNING-DISPOSITION.md)\n- [Sanitizer coverage and exclusions](SANITIZER-COVERAGE.md)\n- [Human/IP review subjects](HUMAN-IP-REVIEW.md) and [IP submission draft](IP-SUBMISSION.md)\n- [Merge requirements](MERGE-ARTIFACTS.md)\n- [PR title](PR-TITLE.txt) and [description](PR-BODY.md)\n- [Reproduction and offline review](REPRODUCE.md)\n- [Integrated patch](communication-integrated.patch), [full Git bundle](communication-integrated.bundle), [complete source archive](communication-source.tar.gz) and [source identity](source-identity.json)\n\nRun `python3 verify.py` to verify the sealed inventory. Human engineering/rights/IP acceptance, official ECA status, QCC execution and protected PR/merge-group checks remain pending. Local evidence does not establish merge readiness. See the check inventory for every failed or unavailable local check.\n')

pr=DEST/'PR-BODY.md'
body=pr.read_text()
bt=chr(96)
summary='Candidate '+bt+commit+bt+' on baseline '+bt+subjects['baseline']+bt+'. '
summary+='Focused regressions (4 targets, 56 native cases), strict cfg(test) checks for two Rust targets (macro-forwarder Clippy coverage remains incomplete), formatting, all changed-file copyright categories and four serial production integrations pass. '
summary+='The accompanying CHECKS.md records every broader pass, failure and unavailable check on this exact source; it includes the full host build/test, manual targets, analyzer and sanitizer results and nested module checks. '
summary+='All 40 changed code files carry the native Apache-2.0 license header. '
summary+='Local execution does not supply hosted protected statuses; QCC requires the licensed project environment.'
paragraph=next(line for line in body.splitlines() if line.startswith('Validation, exact source identity'))
body=body.replace(paragraph,summary)
pr.write_text(body)

print('EXPORTED',commit,len(checks))
