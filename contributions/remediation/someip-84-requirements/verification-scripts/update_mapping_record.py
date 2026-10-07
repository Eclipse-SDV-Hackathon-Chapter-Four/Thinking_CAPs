# Copyright (c) 2026 Contributors to the Eclipse Foundation
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
import copy,json
from pathlib import Path
for root in [Path('/home/jefferson/Thinking_CAPs'),Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/worktrees/thinking-caps-compliance')]:
 packet=root/'contributions/remediation/someip-84-requirements';v=json.loads((packet/'verification.json').read_text())
 p=root/'contributions/registry.json';old=p.read_bytes();data=json.loads(old);before=copy.deepcopy(data)
 a=next(i for i in data['issues'] if i['id']=='eclipse-score/inc_someip_gateway#84')
 current=a.get('current_preparation',{})
 assert current.get('native_commit') in {'f9d46949e40e18637f4c51fcc878339552aa7409',v['native_commit']}
 if current.get('native_commit')!=v['native_commit']:
  histories=a.setdefault('historical_preparations',[])
  if not any(h.get('native_commit')==current['native_commit'] for h in histories):histories.append(copy.deepcopy(current))
 stem='remediation/someip-84-requirements/'
 a.update({'record':stem+'README.md','local_status':'full_implementation_requirements_mapped_locally_reviews_and_integration_pending','compliance_status':stem+'status.json','prepared_pr_draft':stem+'PR-body.md','engineering_review':'proposed_native_requirements_linked_exact_revision_human_ai_committer_ip_and_remaining_ci_pending','submission_candidate':False})
 a['current_preparation']={'record':stem+'README.md','native_results':stem+'native-results.json','baseline':'f8a196c3b16d5172d898394ab99b0ed81346d63d','patch':stem+'submission.patch','patch_sha256':v['plain_patch_sha256'],'native_pr_created':False,'native_commit':v['native_commit'],'mail_patch_with_dco':stem+'submission-with-dco.patch','mail_patch_sha256':v['mail_patch_sha256'],'dco':'Both local commits signed off under continuing user authorization; unpublished; exact-revision human AI review pending','human_disposition':stem+'HUMAN-DISPOSITION.md','requirement_mapping':stem+'requirement-mapping.json','proposed_component_requirements':8,'source_and_partial_test_links':8,'linked_passing_socom_cases':177,'license_header_audit':stem+'evidence/mapping-license-headers.json','integration':'Previous full implementation has two targets passed and four capture permission failures; current re-run pending'}
 assert [i for i in data['issues'] if i['id']!=a['id']]==[i for i in before['issues'] if i['id']!=a['id']]
 assert p.read_bytes()==old,'Concurrent registry edit; rerun before writing'
 p.write_text(json.dumps(data,indent=2)+'\n')
 p=root/'contributions/README.md';old=p.read_bytes();s=old.decode();lines=s.splitlines()
 for i,line in enumerate(lines):
  if line.startswith('| [SOME/IP #84]'):
   lines[i]='| [SOME/IP #84](remediation/someip-84-requirements/README.md) | Full identity/discovery implementation with eight proposed native component requirements | Full build and 722 SOCom cases pass; 177 linked cases; all 243 code/build headers checked | Requirement acceptance, human/IP/committer review, QEMU failures and remaining CI pending; no PR published |'
 s='\n'.join(lines)+'\n'
 s=s.replace('The current full #84 implementation is selected in [the sealed review packet]', 'The preceding full #84 implementation is preserved in [its sealed historical review packet]')
 if 'Native #84 requirement mapping revision' not in s:
  s+='\nNative #84 requirement mapping revision: [current packet](remediation/someip-84-requirements/README.md). Eight proposed SOCom component requirements have native implementation and partial-test links (177 passing cases); all 243 tracked native code/build files have license headers. Requirement acceptance, human/IP review, remaining CI and integration disposition remain pending. The preceding full implementation packet is retained as history; no PR was published.\n'
 assert p.read_bytes()==old,'Concurrent README edit; rerun before writing'
 p.write_text(s)
 print('Updated #84 selection only:',root)
