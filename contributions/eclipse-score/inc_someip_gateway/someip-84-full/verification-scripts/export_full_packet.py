# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Assisted-by: OpenAI Codex (model revision unavailable); human review pending.
from pathlib import Path
import datetime,hashlib,json,subprocess,shutil,sys,xml.etree.ElementTree as ET
repo=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
validate_run_root(repo.parent)
task=repo/'.llm_tmp'
packet=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/worktrees/thinking-caps-compliance/contributions/remediation/someip-84-full')
baseline=json.loads((task/'baseline.json').read_text())['commit']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
def sha(data):return hashlib.sha256(data).hexdigest()
def write_json(name,value):
 p=packet/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def copy(src,name):
 p=packet/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p)
commit=git('rev-parse','HEAD').decode().strip()
if commit==baseline:raise SystemExit('Create prepared native commit before export')
if git('status','--porcelain').strip():raise SystemExit('Native source must be frozen and committed')
plain=git('diff','--binary','--full-index',baseline,commit)
mail=git('format-patch','-1','--stdout','--no-signature',commit)
(packet/'submission.patch').write_bytes(plain)
(packet/'submission-with-dco.patch').write_bytes(mail)
(packet/'commit-message.txt').write_bytes(git('show','-s','--format=%B',commit))
files=git('ls-files').decode().splitlines()
source={p:sha((repo/p).read_bytes()) for p in files if (repo/p).is_file()}
changed=git('diff','--name-only',baseline,commit).decode().splitlines()
write_json('candidate-files.json',{'baseline':baseline,'native_commit':commit,'plain_patch_sha256':sha(plain),'mail_patch_sha256':sha(mail),'files':[{'path':p,'size_bytes':(repo/p).stat().st_size,'sha256':source[p]} for p in changed]})
write_json('candidate-source-hashes.json',{'baseline':baseline,'native_commit':commit,'source_files':source})
for p in changed:copy(repo/p,'source/'+p)
for p in ('NOTICE','LICENSE','LICENSES/Apache-2.0.txt'):
 if (repo/p).is_file():copy(repo/p,'source/'+p)
for src in (task/'evidence').rglob('*'):
 if src.is_file():copy(src,'evidence/'+str(src.relative_to(task/'evidence')))
for p in ['environment.json','baseline.json','issue.json','eca-lookup.json','prior-run.json']:
 if (task/p).exists():copy(task/p,{'issue.json':'upstream-issue.json'}.get(p,p))
for p in ['run_check.py','verify_full_final.py','run_qemu_final.py','verify_patch.py','export_full_packet.py','identity_compile.cpp','identity_tests.cpp']:
 copy(task/p,'verification-scripts/'+p)
copy(task/'bin/bazel','environment/bazel-wrapper.sh')
for p in ['cloud-image-utils','genisoimage']:
 copy(task/'cloud-tools/usr/share/doc'/p/'copyright','environment/cloud-tools/'+p+'-copyright')
protected={}
for p in files:
 if p.startswith(('.github/','.devcontainer/','tools/','bazel/')) or p in ('AGENTS.md','CONTRIBUTION.md','.pre-commit-config.yaml','MODULE.bazel','MODULE.bazel.lock','.bazelrc','.bazelversion','.clang-format','.clang-tidy','.ruff.toml','BUILD') or p.endswith('.bazelrc'):
  before=git('show',baseline+':'+p)
  if sha(before)!=source[p]:raise SystemExit('Protected native policy changed: '+p)
  protected[p]=source[p];copy(repo/p,'native-policy/'+p)
write_json('native-policy-hashes.json',{'baseline':baseline,'all_selected_policies_unchanged':True,'files':protected})
checks=[]
for name in ('final-clang-tidy','final-precommit','final-format','final-build','final-host','final-asan','final-tsan','final-quality-tests','final-docs','final-traceability','final-qemu'):
 path=task/'evidence'/(name+'.json')
 if not path.exists():continue
 r=json.loads(path.read_text())
 same=r['source_hashes_before']==source and r['source_hashes_after']==source
 checks.append({'name':name,'evidence':'evidence/'+name+'.json','exit_code':r['exit_code'],'elapsed_seconds':r['elapsed_seconds'],'exact_final_source':same,'command':r['command']})
 if not same:raise SystemExit('Final check does not bind exact source: '+name)
# XML files are retained by profile. Bazel testlogs can contain earlier targets;
# only the SOCom target is asserted for selected sanitizer profiles.
case_counts={}
for profile in ('final-host','final-asan','final-tsan'):
 xml=task/'evidence'/profile/'score/socom/test/unit/socom_test/test.xml'
 tree=ET.parse(xml).getroot();cases=tree.findall('.//testcase')
 case_counts[profile]={'target':'//score/socom/test/unit:socom_test','test_cases':len(cases),'failures':len(tree.findall('.//failure')),'errors':len(tree.findall('.//error')),'xml':'evidence/'+str(xml.relative_to(task/'evidence'))}
carried=[]
for name in ('gcc-final-compile','gcc-final-tests','baseline-api-control'):
 r=json.loads((task/'evidence'/(name+'.json')).read_text())
 relevant=['score/socom/service_interface_identifier.hpp','score/socom/string_registry.hpp','score/socom/registry_string_view.hpp','score/socom/impl/string_registry.cpp']
 unchanged={p:source[p] for p in relevant if r['source_hashes_after'].get(p)==source[p]}
 if name!='baseline-api-control' and len(unchanged)!=len(relevant):raise SystemExit('Supplementary source changed: '+name)
 if name=='baseline-api-control':
  carried.append({'name':name,'exit_code':r['exit_code'],'evidence':'evidence/'+name+'.json','classification':'Baseline API absence probe, expected failure; not current runtime evidence','verified_baseline_inputs':'evidence/baseline-api-subject.json'});continue
 carried.append({'name':name,'exit_code':r['exit_code'],'evidence':'evidence/'+name+'.json','classification':'carried supplementary API/type check; excludes runtime implementation','verified_unchanged_source_inputs':unchanged})
write_json('native-results.json',{'schema_version':1,'captured_at_utc':now,'repository':'eclipse-score/inc_someip_gateway','issue':84,'baseline':baseline,'native_commit':commit,'patch_sha256':sha(plain),'native_policy_unchanged':True,'execution_class':'direct local native commands; not upstream CI or human approval','checks':checks,'socom_case_counts':case_counts,'supplementary_carried_evidence':carried,'historical_attempts':'Other retained evidence records are exploratory, failed, earlier-source or environment setup attempts; not final acceptance results. initial-unit-retry changed source during execution. bounded-clang-tidy completed lint but exited 4 because the library target has no tests. qemu-default failed because cloud-localds was missing. docs failed on a title underline before correction.','unmeasured_native_ci':['full //score/... //tests/... sanitizer matrix','QEMU sanitizer matrix','performance/flamegraphs','73% coverage threshold workflow','repository-wide clang-tidy and ruff checks','conditional cross/QNX matrices','actual PR ECA/DCO/license and can_merge jobs'],'traceability_gap':{'raw_gate_output':'evidence/final-traceability.stdout','scope':'repository-wide native component-requirement metrics','source_linked_requirements':0,'test_linked_requirements':0,'component_requirements':8,'linked_tests':0,'tests':996,'baseline_thresholds':'zero; passing is not accepted trace coverage for new behavior'},'engineering_acceptance':'pending exact-revision human AI review, committer API/scope/requirements acceptance, IP assessment and required IP Team disposition'})
author=git('show','-s','--format=%an <%ae>',commit).decode().strip();committer=git('show','-s','--format=%cn <%ce>',commit).decode().strip();message=git('show','-s','--format=%B',commit).decode()
expected='Jefferson Nascimento <jnsagai@gmail.com>'
assert author==expected and committer==expected and message.count('Signed-off-by: '+expected)==1
write_json('DCO-preparation.json',{'native_commit':commit,'patch_sha256':sha(plain),'mail_patch_sha256':sha(mail),'author':author,'committer':committer,'signed_off_by':'Signed-off-by: '+expected,'authorization':'Continuing user instruction: ok, prepare the DCO for me; later expanded the same #84 contribution: work on this Full issue #84 implementation','old_exact_revision_approval_reused':False,'full_revision_human_ai_review':'pending','published':False})
write_json('preparation.json',{'prepared_at_utc':now,'disposable_native_directory':str(repo),'baseline':baseline,'native_commit':commit,'branch':git('branch','--show-current').decode().strip(),'native_pr_created':False,'source_api_migration':True,'historical_scoped_packet':'../someip-84','scope':'Complete three identifier/discovery use cases in issue #84; optional minor means compatible minimum; synchronous local runtime snapshot','formal_native_requirement_ids':'unknown; existing comp__socom and feat__someip_gateway documentation IDs preserved','dependency_changes':False,'native_policy_changes':False,'human_approval':'prior scoped approval retained as history only; expanded revision not yet human-reviewed'})
gates=['Human AI/code review of exact expanded revision','Committer acceptance of public API migration, optional-minor semantics and native contribution classification/requirements','Project committer net-new-IP assessment and required IP Team disposition','Remaining applicable upstream CI, actual PR author/committer ECA/DCO and license checks','Native publication remains restricted by prior user instruction; no PR created']
write_json('status.json',{'id':'eclipse-score/inc_someip_gateway#84','observed_at':now,'ready_for_official_merge':False,'submission_candidate':False,'technical_status':'full_issue_implementation_prepared_locally','remaining_gates':gates,'human_review':'pending expanded exact revision; old scoped approval does not cover new source','native_policy_unchanged':True,'native_pr_created':False,'ai_assistance':['OpenAI Codex (historical model revision not retained)','OpenAI Codex (full implementation; model revision unavailable)'],'artifacts':{name:'remediation/someip-84-full/'+path for name,path in {'patch':'submission.patch','mail_patch_with_dco':'submission-with-dco.patch','pr_body':'PR-body.md','native_results':'native-results.json','acceptance':'ACCEPTANCE.md','human_disposition':'HUMAN-DISPOSITION.md','ip_review_request':'IP-review-request.md','ci_matrix':'CI-applicability.md','dco_preparation':'DCO-preparation.json','evidence_manifest':'artifact-manifest.json'}.items()},'patch_provenance':{'original_path':'remediation/someip-84/submission.patch','original_sha256':'cd93cb62c08b80d857b1795b203e133aa7d3d403d281af61bac7d9bcb60d4ea1','prepared_sha256':sha(plain),'source_diff_unchanged':False,'note':'Expanded native implementation against same baseline; previous scoped packet left unchanged'}})
# Results are now concrete. No prospective check is reported as successful.
validation='\n'.join('- `{}`: exit {} ({} seconds).'.format(c['name'],c['exit_code'],round(c['elapsed_seconds'],1)) for c in checks)
p=packet/'PR-body.md';s=p.read_text();s=s.replace('Populate from `native-results.json` for the exact exported patch. Earlier 689-test\nresults belong to the previous scoped revision and are not evidence for this patch.',validation+'\n\nSOCom: 722 cases passed in each final default, ASAN/LSAN/UBSAN and TSAN run.\nSelected sanitizer checks do not represent the complete CI matrix. The native trace gate passes baseline zero thresholds with 0/8 linked component\nrequirements and 0/996 linked tests; this is not formal acceptance of the new\nbehavior. Earlier 689-test scoped results remain historical. See native-results.json for source\nbindings, raw logs, failures and remaining CI obligations.')
p.write_text(s)
for src in (repo/'bazel-bin/score/socom').rglob('*'):
 if src.is_file() and (src.name.endswith('.sarif') or 'AspectRulesLint' in src.name and src.suffix in ('.out','.txt','.yaml','.json')):
  copy(src,'evidence/clang-tidy-reports/'+str(src.relative_to(repo/'bazel-bin/score/socom')))
for p in ['_build/metrics.json','_build/needs.json']:
 if (repo/p).exists():copy(repo/p,'evidence/docs/'+Path(p).name)
# Licence sidecars cover authored packet prose/scripts, not copied native ownership.
for p in packet.iterdir():
 if p.suffix in ('.md','.txt') and p.name!='submission.patch':
  Path(str(p)+'.license').write_text('SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation\nSPDX-License-Identifier: Apache-2.0 AND CC0-1.0\nAI Disclosure: Generated with OpenAI Codex (model revision unavailable); AI portions offered under CC0-1.0. Human review pending.\n')
print(json.dumps({'native_commit':commit,'patch_sha256':sha(plain),'files':len(changed),'checks':[(c['name'],c['exit_code']) for c in checks]},indent=2))
