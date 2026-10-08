# Copyright (c) 2026 Eclipse SDV Hackathon Team
#
# Licensed under the Apache License, Version 2.0.
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import json,hashlib,datetime,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from storage import validate_run_root
validate_run_root(ROOT)
WORKSPACE=Path('/home/jefferson/Thinking_CAPs')
CONTRIB=WORKSPACE/'contributions'
DEST=CONTRIB/'issues/eclipse-score/communication/rust-api-queue/completion-20261007'
def sha(p):
 with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
identity=json.loads((DEST/'source-identity.json').read_text())
assert not (DEST/'artifact-manifest.json').exists(),'Do not overwrite a sealed packet'
entries=[{'path':str(p.relative_to(DEST)),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in sorted(DEST.rglob('*')) if p.is_file() and p.name not in ['artifact-manifest.sha256']]
manifest={'schema_version':1,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':identity['baseline'],'candidate_commit':identity['candidate_commit'],'patch_sha256':identity['patch_sha256'],'engineering_acceptance':'pending_offline','merge_ready':False,'files':entries}
(DEST/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
manifest_sha=sha(DEST/'artifact-manifest.json')
(DEST/'artifact-manifest.sha256').write_text(manifest_sha+'  artifact-manifest.json\n')
subprocess.run(['python3',str(DEST/'verify.py')],check=True)
path=CONTRIB/'registry.json'; raw=path.read_bytes(); registry=json.loads(raw)
previous=[]; base=str(DEST.relative_to(CONTRIB))
for issue in registry['issues']:
 if issue['id'] not in [f'eclipse-score/communication#{n}' for n in [1261,250,560]]: continue
 previous.append(json.loads(json.dumps(issue)))
 issue['original_manifest']=issue.get('original_manifest',issue['evidence_manifest'])
 issue.update(record=base+'/README.md',local_status='integrated_scoped_candidate_local_verification_recorded',baseline_commit=identity['baseline'],candidate_commit=identity['candidate_commit'],evidence_manifest=base+'/artifact-manifest.json',submission_candidate=True,engineering_review='Integrated local source correction and verification recorded; see applicable check matrix; human/IP and hosted acceptance pending',patch=base+'/communication-integrated.patch',patch_sha256=identity['patch_sha256'],pr_draft=base+'/PR-BODY.md',branch=identity['branch'],branch_clone=str(ROOT/'workspaces/integrated'),queue_record=base+'/README.md')
 if issue['issue_number']==1261: issue['scope']='Scoped heterogeneous discovery across configured LoLa deployments; provider instances may be absent from the consumer manifest; entirely unconfigured interface types remain outside this contribution.'
 issue['readiness_review']={'record':base+'/README.md','manifest':base+'/artifact-manifest.json','manifest_sha256':manifest_sha,'candidate_patch':base+'/communication-integrated.patch','candidate_patch_sha256':identity['patch_sha256'],'pr_draft':base+'/PR-BODY.md','merge_requirements':base+'/MERGE-ARTIFACTS.md','engineering_acceptance':'pending_offline','merge_ready':False}
assert len(previous)==3
assert path.read_bytes()==raw,'Registry changed concurrently; reread before linking'
path.write_text(json.dumps(registry,indent=2)+'\n')
audit=CONTRIB/'audits/2026-10-07-communication-completion-link.json'
audit.write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'Link the three Communication records to the integrated current-main review subject while retaining original evidence and preceding packet','registry_before_sha256':hashlib.sha256(raw).hexdigest(),'registry_after_sha256':sha(path),'previous_records':previous,'candidate_commit':identity['candidate_commit'],'manifest_sha256':manifest_sha},indent=2)+'\n')
command=['python3',str(WORKSPACE/'scripts/verify_contributions.py'),'--json']
for n in [1261,250,560,781,490]: command+=['--issue',f'eclipse-score/communication#{n}']
result=subprocess.run(command,capture_output=True,text=True,cwd=WORKSPACE)
(CONTRIB/'audits/2026-10-07-communication-final-integrity.json').write_text(result.stdout)
assert result.returncode==0,result.stdout+result.stderr
print('SEALED',identity['candidate_commit'],len(entries),manifest_sha)
