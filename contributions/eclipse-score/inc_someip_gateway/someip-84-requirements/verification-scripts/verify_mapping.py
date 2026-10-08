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
from pathlib import Path
import subprocess,sys,shutil
r=Path.cwd()
checks=[('mapping-precommit-final',['pre-commit','run','--all-files']),('mapping-format-check',['bazel','test','--jobs=2','//:format.check']),('mapping-host',['bazel','test','--jobs=2','//score/socom/test/unit:socom_test','--nocache_test_results']),('mapping-docs',['bazel','run','--jobs=2','//:docs']),('mapping-traceability',['bazel','run','--jobs=2','//:traceability_gate','--','--metrics-json',str(r/'_build/metrics.json'),'--need-type=comp_req']),('mapping-clang-tidy',['bazel','test','--jobs=2','--config=clang-tidy','//score/socom/...','--nocache_test_results'])]
for name,args in checks:
 print('START',name,flush=True)
 p=subprocess.run([sys.executable,'.llm_tmp/run_check.py',name,*args])
 if name=='mapping-host':
  for file in (r/'bazel-testlogs/score/socom/test/unit/socom_test').glob('test.*'):
   if file.name in ('test.xml','test.log'):
    out=r/'.llm_tmp/evidence/mapping-host/score/socom/test/unit/socom_test'/file.name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,out)
 if name=='mapping-docs':
  for file in ['metrics.json','needs.json']:
   shutil.copyfile(r/'_build'/file,r/'.llm_tmp/evidence'/('mapping-'+file))
 if p.returncode:sys.exit(p.returncode)
