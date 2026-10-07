# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Assisted-by: OpenAI Codex (model revision unavailable); human review pending.
from pathlib import Path
import datetime,hashlib,json,sys,xml.etree.ElementTree as E
root=Path(sys.argv[1]).resolve()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((root/p).read_text())
source=load('candidate-source-hashes.json')['source_files'];candidate=load('candidate-files.json');results=load('native-results.json');proof=load('evidence/patch-verification.json')
assert candidate['native_commit']=='f9d46949e40e18637f4c51fcc878339552aa7409'
assert digest(root/'submission.patch')==candidate['plain_patch_sha256']==proof['plain_patch_sha256']==results['patch_sha256']
assert digest(root/'submission-with-dco.patch')==candidate['mail_patch_sha256']==proof['mail_patch_sha256']
assert proof['source_hashes']==source and proof['source_file_count']==395
for p in (root/'source').rglob('*'):
 if p.is_file():assert digest(p)==source[str(p.relative_to(root/'source'))]
for check in results['checks']:
 r=load(check['evidence']);assert r['source_hashes_before']==r['source_hashes_after']==source and check['exact_final_source']
 assert check['exit_code']==(3 if check['name']=='final-qemu' else 0)
for profile,count in results['socom_case_counts'].items():
 r=E.parse(root/count['xml']).getroot();assert len(r.findall('.//testcase'))==722 and not r.findall('.//failure') and not r.findall('.//error')
for p,h in load('native-policy-hashes.json')['files'].items():assert digest(root/'native-policy'/p)==h==source[p]
assert len(candidate['files'])==46
assert not load('status.json')['ready_for_official_merge'] and load('status.json')['remaining_gates']
assert (root/'commit-message.txt').read_text().count('Signed-off-by: Jefferson Nascimento <jnsagai@gmail.com>')==1
files={str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name not in ('artifact-manifest.json','verification.json')}
manifest={'schema_version':1,'captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Full issue #84 local implementation and evidence; not native acceptance','excluded':['artifact-manifest.json','verification.json'],'files':files,'sizes_bytes':{p:(root/p).stat().st_size for p in files}}
(root/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for p,h in files.items():assert digest(root/p)==h
record={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_commit':candidate['native_commit'],'plain_patch_sha256':candidate['plain_patch_sha256'],'mail_patch_sha256':candidate['mail_patch_sha256'],'manifest_sha256':digest(root/'artifact-manifest.json'),'manifest_files':len(files),'candidate_source_files':395,'changed_native_files':46,'all_final_commands_bind_same_source':True,'fresh_baseline_patch_application_verified':True,'socom_cases_per_profile':722,'final_qemu_exit_code':3,'native_policy_unchanged':True,'ready_for_official_merge':False,'classification':'Deterministic artifact/hash consistency only; no human review or IP/engineering approval'}
(root/'verification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
