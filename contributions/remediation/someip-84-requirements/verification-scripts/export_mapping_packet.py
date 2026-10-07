# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Human review pending.
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path.cwd();validate_run_root(r.parent)
workspace=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/worktrees/thinking-caps-compliance')
old=workspace/'contributions/remediation/someip-84-full'
p=workspace/'contributions/remediation/someip-84-requirements'
assert not p.exists(),'Do not overwrite a sealed revision'
p.mkdir()
def git(*args):return subprocess.check_output(['git',*args],cwd=r)
def sha(x):return hashlib.sha256(x).hexdigest()
def save(name,obj):
 target=p/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(obj,indent=2)+'\n')
def cp(src,name):
 target=p/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
def md(name,body):
 (p/name).write_text(body+'\n')
 cp(old/'README.md.license',name+'.license')
baseline='f8a196c3b16d5172d898394ab99b0ed81346d63d';prior='f9d46949e40e18637f4c51fcc878339552aa7409'
head=git('rev-parse','HEAD').decode().strip();assert not git('status','--porcelain').strip()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
files=git('ls-files').decode().splitlines();hashes={f:sha((r/f).read_bytes()) for f in files}
changed=git('diff','--name-only',baseline,'HEAD').decode().splitlines()
plain=git('diff','--binary','--full-index',baseline,'HEAD');mail=git('format-patch','--stdout','--no-signature',baseline+'..HEAD')
(p/'submission.patch').write_bytes(plain);(p/'submission-with-dco.patch').write_bytes(mail)
(p/'requirement-mapping.patch').write_bytes(git('diff','--binary','--full-index',prior,'HEAD'))
cp(r/'.llm_tmp/evidence/mapping-patch-verification.json','evidence/patch-verification.json')
for f in changed+['NOTICE','LICENSE','LICENSES/Apache-2.0.txt']:
 cp(r/f,'source/'+f)
save('candidate-files.json',changed);save('candidate-source-hashes.json',hashes)
for f in ['baseline.json','native-policy-hashes.json','eca-lookup.json']:
 cp(old/f,f)
shutil.copytree(old/'native-policy',p/'native-policy')
for f,expected in json.loads((old/'native-policy-hashes.json').read_text())['files'].items():
 assert hashes[f]==expected,('Native policy changed',f)
cp(old/'artifact-manifest.json','history/implementation-manifest.json');cp(old/'verification.json','history/implementation-verification.json');cp(old/'native-results.json','history/implementation-results.json')
for f in (r/'.llm_tmp/evidence').glob('mapping-*'):
 if f.is_dir():shutil.copytree(f,p/'evidence'/f.name)
 else:cp(f,'evidence/'+f.name)
for f in ['run_check.py','verify_mapping.py','final_mapping_stage.py','audit_headers.py','export_mapping_packet.py','verify_mapping_patch.py','update_mapping_record.py']:
 cp(r/'.llm_tmp'/f,'verification-scripts/'+f)
 helper=p/'verification-scripts'/f
 body=helper.read_text()
 if 'https://www.apache.org/licenses/LICENSE-2.0' not in body[:3000]:
  header='''# Copyright (c) 2026 Contributors to the Eclipse Foundation
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Human review pending.
'''
  helper.write_text(header+body)
checks=[]
for name in ['mapping-source-precommit','mapping-verified-format','mapping-verified-build','mapping-verified-host','mapping-verified-docs','mapping-verified-traceability']:
 a=json.loads((r/'.llm_tmp/evidence'/f'{name}.json').read_text());assert a['exit_code']==0,name
 assert a['source_hashes_before']==hashes==a['source_hashes_after'],name
 checks.append({'name':name,'evidence':f'evidence/{name}.json','exit_code':a['exit_code'],'elapsed_seconds':a['elapsed_seconds'],'command':a['command'],'exact_final_source':True})
a=json.loads((r/'.llm_tmp/evidence/mapping-verified-clang-tidy.json').read_text());assert a['exit_code']==0
assert a['source_hashes_before']==hashes==a['source_hashes_after']
checks.append({'name':'mapping-verified-clang-tidy','evidence':'evidence/mapping-verified-clang-tidy.json','exit_code':0,'exact_final_source':True,'elapsed_seconds':a['elapsed_seconds'],'command':a['command']})
xml=ET.parse(r/'.llm_tmp/evidence/mapping-verified-host/score/socom/test/unit/socom_test/test.xml')
assert xml.getroot().get('tests')=='722' and xml.getroot().get('failures')=='0'
needsraw=json.loads((r/'.llm_tmp/evidence/mapping-verified-needs.json').read_text());needs=next(iter(needsraw['versions'].values()))['needs']
ids=sorted(k for k in needs if k.startswith('comp_req__socom__'))
assert len(ids)==8
matrix=[]
for identifier in ids:
 n=needs[identifier];assert n['status']=='invalid' and n['source_code_link'] and n['testlink'],identifier
 sources=[]
 for f in files:
  if Path(f).suffix not in {'.cpp','.hpp','.h'}:continue
  for line,text in enumerate((r/f).read_text().splitlines(),1):
   if '// req-Id:' in text and identifier in text.split('// req-Id:',1)[1].replace(',',' ').split():sources.append({'path':f,'line':line,'sha256':hashes[f]})
 tests=[]
 for t in xml.findall('.//testcase'):
  props={v.get('name'):v.get('value') for v in t.findall('./properties/property')}
  if identifier in (props.get('PartiallyVerifies','').replace(',',' ').split()):
   tests.append({'suite':t.get('classname'),'name':t.get('name'),'path':t.get('file'),'line':int(t.get('line')),'link_type':'PartiallyVerifies','result':'passed'})
 assert sources and tests
 matrix.append({'requirement_id':identifier,'title':n['title'],'status':'invalid','acceptance':'proposal, pending committer review','parent':n['derived_from'],'component':n['satisfied_by'],'design':'score/socom/docs/version_handling.rst','source':sources,'tests':tests,'verification_limits':'Partial case links; complete requirement adequacy and implementation review remain human decisions. Synchronization also needs inspection of lock, no allocation/callbacks and caller lifetime obligations.'})
save('requirement-mapping.json',{'baseline':baseline,'native_commit':head,'scope':'Issue 84 native SOCom proposals; unrelated TC8 requirements unchanged','feature':'feat_req__socom__version_selection','stakeholder':'stkh_req__someip_gw__local_version_selection','requirements':matrix,'native_metamodel':'score_docs_as_code 8.2.0; derived_from/satisfied_by; invalid status required until accepted, because draft is unsupported','source_revision_bound':True})
metrics=json.loads((r/'.llm_tmp/evidence/mapping-verified-metrics.json').read_text())
linked=sum(bool(t.findall('./properties/property[@name="PartiallyVerifies"]')) for t in xml.findall('.//testcase'))
assert linked==177
license_report=json.loads((r/'.llm_tmp/evidence/mapping-license-headers.json').read_text());assert not license_report['missing_project_headers'] and not license_report['changed_code_missing_ai_disclosure']
save('native-results.json',{'captured_at_utc':now,'native_commit':head,'baseline':baseline,'patch_sha256':sha(plain),'native_policy_unchanged':True,'checks':checks,'socom_cases':722,'linked_socom_cases':linked,'new_component_requirements_fully_linked':8,'native_metrics':metrics,'historical_results':{'native_commit':prior,'path':'../someip-84-full/native-results.json','manifest':'history/implementation-manifest.json','scope':'Original full build/host/sanitizer/QEMU measurements; not fresh evidence for this revision. Runtime implementation unchanged apart from trace comments; tests now add metadata. QEMU remains two targets passed, four capture permission failures.'},'remaining_ci':'Full sanitizer/cross/platform/coverage/integration and other applicable upstream gates remain pending; selected SOCom checks do not replace them'})
save('preparation.json',{'prepared_at_utc':now,'baseline':baseline,'native_commit':head,'previous_full_commit':prior,'native_pr_created':False,'formal_native_requirement_ids':ids,'requirement_acceptance':'proposed, invalid until committer disposition','dependency_changes':False,'native_policy_changes':False,'disposable_native_directory':str(r)})
# Existing review obligations carry forward; no human or IP decision is inferred.
status=json.loads((old/'status.json').read_text());status.update({'observed_at':now,'technical_status':'full_implementation_with_native_requirement_mapping_prepared_locally','requirement_mapping':'8 proposed component requirements linked to source and partial verification cases; not accepted','native_commit':head})
status['artifacts']={k:v.replace('someip-84-full/','someip-84-requirements/') if isinstance(v,str) else v for k,v in status['artifacts'].items()}
status['artifacts']['requirement_mapping']='remediation/someip-84-requirements/REQUIREMENT-MAPPING.md'
status['patch_provenance']={'original_path':'remediation/someip-84-full/submission.patch','original_sha256':sha((old/'submission.patch').read_bytes()),'prepared_sha256':sha(plain),'source_diff_unchanged':False,'note':'Native requirement hierarchy, trace/test metadata and standard schema license header added to original full implementation'}
save('status.json',status)
for name in ['HUMAN-DISPOSITION.md','IP-review-request.md','bugfix-issue-draft.md','DCO.md']:
 md(name,(old/name).read_text()+'\n\nCurrent revision: `'+head+'`. Requirement mapping and header audit are in this packet. Proposed requirement status remains invalid until committer acceptance. Earlier full implementation checks remain historical in `../someip-84-full/`; current checks are listed in native-results.json.')
dco=json.loads((old/'DCO-preparation.json').read_text());dco.update({'native_commit':head,'mail_patch_sha256':sha(mail),'patch_sha256':sha(plain),'prepared_under_continuing_user_authorization':True,'native_pr_created':False,'note':'Two native commits retain contributor DCO sign-off; human AI review remains pending'});save('DCO-preparation.json',dco)
md('README.md',f'''# SOME/IP #84: requirement mapping revision

The complete implementation now has a native proposal hierarchy: one stakeholder
need, one feature requirement and eight SOCom component requirements. Each
component requirement links to implementation, the native design guide and
specific passing test cases. [Requirement mapping](REQUIREMENT-MAPPING.md) lists
all links and verification limits. [License audit](LICENSE-HEADERS.md) covers all
tracked native code/build files and preserves existing attribution.

Native revision: `{head}`; baseline `{baseline}`. Both commits in
[the prepared DCO mail series](submission-with-dco.patch) are signed off under
the user's continuing #84 authorization. [Full patch](submission.patch),
[incremental mapping patch](requirement-mapping.patch), changed source snapshots,
native policies and raw measurements are included. Earlier implementation
measurements and their original seal remain in `../someip-84-full/`.

Current checks: all 722 SOCom cases pass; 177 carry targeted partial requirement
links. All eight new component requirements have source and test links, with no
broken test references. The repository-wide graph still includes the eight
unrelated TC8 requirements; local SOCom tests do not verify them. Native full
build, formatting, copyright/REUSE/pre-commit and docs/trace checks pass.
SOCom Clang-Tidy passed for this exact revision.

Requirements are tagged `proposal` and marked `invalid` because the pinned
metamodel has no draft requirement status. This is an explicit unaccepted state,
not a declaration that tests failed. Link presence does not establish complete
verification. Committer requirement/API acceptance, exact-revision human AI and
IP review, remaining CI and the previous four QEMU capture permission failures
still prevent a merge-ready claim. No PR was created or published.
''')
rows=['| Proposed requirement | Implementation | Passing partial cases |','|---|---|---|']
for m in matrix:
 rows.append('| `'+m['requirement_id']+'` | '+', '.join('`'+x['path']+':'+str(x['line'])+'`' for x in m['source'])+' | '+str(len(m['tests']))+' |')
md('REQUIREMENT-MAPPING.md','''# Issue #84 requirement mapping

This is a native proposal, not an accepted requirement baseline. The hierarchy
is `stkh_req__someip_gw__local_version_selection` →
`feat_req__socom__version_selection` → the eight requirements
below → existing `comp__socom` (belongs to `feat__someip_gateway`). New requirement
status is `invalid`, tagged `proposal`, as required by the pinned metamodel's
valid/invalid vocabulary. Existing TC8 requirements and valid architecture IDs
retain their status and meaning.

'''+ '\n'.join(rows)+f'''

All eight requirements have native source and test links. The 177 distinct
linked SOCom cases pass within the 722-case suite; counts overlap when a case
covers several requirements. [Machine-readable matrix](requirement-mapping.json)
provides exact paths, line numbers, hashes and case names. Native [metrics](evidence/mapping-verified-metrics.json)
and [needs graph](evidence/mapping-verified-needs.json) preserve the resolved links.

Optional minor as a minimum, enabled-only local synchronous snapshots, bounded
storage and the new virtual API are explicit design interpretations for
committer review. Individual cases use `PartiallyVerifies`, not a claim of
complete requirement verification. Synchronization/heap allocation/callback
absence and caller/snapshot lifetime obligations need implementation inspection
and human adequacy review as well as concurrency test evidence. Source API
migration is validated by the full native build; IPC layout and network sentinel
translation remain separate unchanged design constraints, not TC8 acceptance.

The proposed stakeholder requirement's `valid_from: v0.1` is a proposed
applicability window required by the metamodel, not approval of a release.
Classification QM/security NO follows the existing component and is still
subject to committer disposition. Committers must decide whether the expanded
scope requires requirements acceptance before a code PR under CONTRIBUTION.md.

Native revision: `{head}`.
''')
md('LICENSE-HEADERS.md',f'''# Native license header audit

Audited {license_report['total_code_files']} tracked code/build files; all have
inline copyright, Apache license notice/link and SPDX identifiers. This covers
{license_report['changed_code_files']} files changed by the full contribution.
All changed C++ files disclose AI assistance and the Apache-2.0 AND CC0-1.0
expression. Original notices are retained, including the Bazel Authors' valid
Apache notice (its HTTP license link and copyright syntax are preserved).

Added the standard project Apache header to `score/config/mw_someip_config.fbs`,
which previously relied on the existing REUSE annotation. The schema body and
license remain unchanged. This conventional header is copied from the project
header template and does not attribute existing schema code to an AI.

[Per-file hashes and findings](evidence/mapping-license-headers.json) record the
scope and criteria. The initial audit's overly narrow copyright/link matching
and genuine missing inline schema header remain recorded as history. Native
copyright and REUSE hooks pass in the final pre-commit run. These checks assess
notices and consistency; project IP acceptance remains pending.

Guidance: [Eclipse Project Handbook](https://www.eclipse.org/projects/handbook/),
native `AGENTS.md` and `.github/instructions/code-style.md` (included in the
policy snapshot). External fetched dependencies, generated build outputs and
ephemeral scratch are outside the authored native source audit.
''')
md('ACCEPTANCE.md','''# Issue acceptance and verification

The issue's service identity, full instance identity, optional filters and exact
major are mapped to the proposed native requirements in REQUIREMENT-MAPPING.md.
Single registration and compatibility preservation are mapped to targeted key,
runtime and connector tests. Runtime snapshot, storage and concurrency obligations
are explicit design refinements with partial verification and review limits.
The complete case matrix and resolved graph accompany the patch. Human/native
requirements, scope/API and IP acceptance remain pending; integration is incomplete.
''')
md('CI-applicability.md','''# Current verification scope

Fresh exact-revision checks: pre-commit (copyright and REUSE included), native
format checks, full build, 722-case SOCom unit suite, docs and traceability gate.
SOCom Clang-Tidy also passed for the exact current source; its native lint
policy, exact command and hashes are preserved.

Original full implementation results are in history/implementation-results.json
and the sealed sibling packet: full host suite, selected ASAN/LSAN/UBSAN and
TSAN checks, quality tests and QEMU. They are historical measurements against
f9d4694, not exact-revision runs for this mapping revision. Four QEMU packet
capture targets still need resolution/re-run on an appropriate host. The full
sanitizer/cross/QNX/performance/coverage/license/common PR/merge CI obligations
remain those of the original full packet; no native gate or policy was changed.

The native trace gate retains zero thresholds. Eight SOCom proposals now have
source and test links; eight unrelated TC8 component requirements remain unlinked.
Presence metrics cannot establish test adequacy or requirement acceptance.
''')
md('SELF-REVIEW.md','''# Agent assessment

Requirement IDs were created as explicitly proposed native work products using
the pinned namespace, link direction and status vocabulary. No existing TC8
network requirement was reused to claim local discovery coverage. Test metadata
uses partial links to the requirements each case exercises, and the native graph
and exact commands are captured. Runtime implementation changes since f9d4694
are trace comments only; test changes record metadata and schema change is the
standard header. Public API semantics and limitations remain documented.

This is an agent assessment, not independent human review, committer acceptance
or IP disposition. All remaining decisions in HUMAN-DISPOSITION.md apply to the
current exact patch. Review the proposed requirement statements, minimum-minor
interpretation, API migration, synchronization and caller obligations before
acceptance. The earlier QEMU capture permission failures remain unresolved.
''')
md('REPRODUCE.md','''# Reproduce

Check out baseline `f8a196c3b16d5172d898394ab99b0ed81346d63d` in a fresh clone.
Apply `submission.patch`, or `git am submission-with-dco.patch` for both signed
off commits. From the existing full f9d4694 revision, `requirement-mapping.patch`
applies only the mapping/header additions. Never apply both plain and mail patches.

Run native `pre-commit run --all-files`, `bazel test //:format.check`,
`bazel build //...`, `bazel test //score/socom/test/unit:socom_test`,
`bazel test --config=clang-tidy //score/socom/...`, `bazel run //:docs`,
then `bazel run //:traceability_gate -- --metrics-json "$PWD/_build/metrics.json"
--need-type=comp_req`. Exact task cache/output arguments, hashes and timings
are retained in evidence. The helper scripts use task-specific managed paths;
standard native commands do not require that local infrastructure.
''')
md('PR-body.md','''# Bug Fix

## Description

SOCom separates canonical service ID + major identity, full offered instance
identity and optional local discovery filters. Bounded snapshots report actual
enabled offer minors, and single-server registration ignores minor versions.
Full contracts retain compatibility versions and all in-repository callers are
migrated. The native design guide documents migration, storage and locking.

Eight proposed SOCom requirements now link the native design, implementation and
177 targeted passing test cases. They are explicitly unaccepted (`invalid` /
`proposal`) under the pinned metamodel. Native requirement/API classification and
acceptance must precede final review as required by the committers' disposition.
A standard inline Apache header is added to the existing licensed config schema.

## Related ticket

Related to https://github.com/eclipse-score/inc_someip_gateway/issues/84.
The actual codeowner_review tracking issue and PR links must be supplied at
submission; no tracking issue or PR has been published for this local packet.

## Validation

Full native build, 722 SOCom cases, formatting, pre-commit copyright/REUSE,
docs and trace checks pass for the current revision. SOCom Clang-Tidy passes for the exact current revision. All eight new component requirements have source
and partial-test links, with no broken test references. Unrelated TC8 requirements
remain outside this verification. Exact commands/raw evidence are in native-results.json.

Original selected sanitizer/full host/quality/QEMU runs belong to the prior
implementation revision and are retained as history. QEMU has two passing targets
and four host tcpdump credential-change EPERM failures; integration and remaining
applicable CI are pending. Trace presence does not establish complete verification.

## AI assistance

OpenAI Codex assisted code, documentation, mapping and verification helpers
(model revision unavailable). AI-generated portions are disclosed and offered
under CC0-1.0; existing Apache notices remain. Exact-revision human AI review is
pending. Both local commits include Jefferson Nascimento's authorized DCO sign-off.

## Review and IP

Committer requirement/API acceptance, human review, required IP disposition and
remaining CI are pending. Prepare as draft under CONTRIBUTION.md until these
gates are met. External users must migrate the source API and Runtime method.
''')
# Manifest binding excludes the summary of that same manifest.
manifest={f.relative_to(p).as_posix():sha(f.read_bytes()) for f in sorted(p.rglob('*')) if f.is_file() and f.name not in {'artifact-manifest.json','verification.json'}}
save('artifact-manifest.json',{'schema_version':1,'captured_at_utc':now,'scope':'Full issue 84 requirement mapping revision; native acceptance pending','excluded':['artifact-manifest.json','verification.json'],'files':manifest})
save('verification.json',{'verified_at_utc':now,'native_commit':head,'plain_patch_sha256':sha(plain),'mail_patch_sha256':sha(mail),'manifest_sha256':sha((p/'artifact-manifest.json').read_bytes()),'manifest_files':len(manifest),'candidate_source_files':len(hashes),'changed_native_files':len(changed),'new_requirements_with_source_and_test_links':8,'linked_socom_cases':177,'socom_cases':722,'fresh_baseline_patch_application_verified':True,'native_policy_unchanged':True,'ready_for_official_merge':False,'classification':'Deterministic artifact/hash consistency only; no human or IP acceptance'})
print('EXPORTED',p,head,len(changed),len(manifest))
