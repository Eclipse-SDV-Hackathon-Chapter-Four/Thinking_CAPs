# Copyright (c) 2026 Contributors to the Eclipse Foundation
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Human review pending.
# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();baseline='f8a196c3b16d5172d898394ab99b0ed81346d63d'
files=subprocess.check_output(['git','ls-files'],text=True).splitlines()
changed=set(subprocess.check_output(['git','diff','--name-only',baseline],text=True).splitlines())
code_suffixes={'.h','.hpp','.c','.cc','.cpp','.cxx','.rs','.py','.sh','.bzl','.proto','.fbs','.lds','.build','.BUILD'}
records=[]
for name in files:
 p=r/name
 if p.suffix not in code_suffixes and p.name not in {'BUILD','BUILD.bazel','MODULE.bazel'}:continue
 data=p.read_bytes();h=data.decode(errors='replace')[:3000]
 records.append({'path':name,'sha256':hashlib.sha256(data).hexdigest(),'changed_by_contribution':name in changed,'copyright_header':('Copyright' in h),'project_license_notice':('Apache' in h and 'www.apache.org/licenses/LICENSE-2.0' in h),'spdx_apache':('SPDX-License-Identifier: Apache-2.0' in h),'ai_disclosure':('AI Disclosure:' in h),'cc0_expression':('Apache-2.0 AND CC0-1.0' in h)})
failed=[x['path'] for x in records if not all(x[k] for k in ['copyright_header','project_license_notice','spdx_apache'])]
changed_records=[x for x in records if x['changed_by_contribution']]
missing_ai=[x['path'] for x in changed_records if Path(x['path']).suffix in {'.h','.hpp','.cc','.cpp','.cxx','.rs','.py'} and not(x['ai_disclosure'] and x['cc0_expression'])]
out={'scope':'All tracked native code and Bazel source/build files; vendors, generated build outputs and ephemeral .llm_tmp files excluded','baseline':baseline,'total_code_files':len(records),'changed_code_files':len(changed_records),'missing_project_headers':failed,'changed_code_missing_ai_disclosure':missing_ai,'criteria_source':['AGENTS.md','.github/instructions/code-style.md','https://www.eclipse.org/projects/handbook/'],'method':'Direct header presence/hash audit plus separately executed native copyright/REUSE hooks; not IP acceptance','files':records}
(r/'.llm_tmp/evidence/mapping-license-headers.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='files'})
assert not failed and not missing_ai
