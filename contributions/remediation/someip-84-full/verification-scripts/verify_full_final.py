# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Assisted-by: OpenAI Codex (model revision unavailable); human review pending.
from pathlib import Path
import subprocess,sys,shutil,json,os
repo=Path(__file__).resolve().parents[1]
checks=[
 ('final-precommit',['pre-commit','run','--all-files']),
 ('final-format',['bazel','test','--jobs=2','//:format.check']),
 ('final-build',['bazel','build','--jobs=2','//...']),
 ('final-host',['bazel','test','--jobs=2','//...','--build_tests_only','--nocache_test_results']),
 ('final-asan',['bazel','test','--jobs=2','//score/socom/test/unit:socom_test','--features=asan','--features=lsan','--features=ubsan_clang','--nocache_test_results']),
 ('final-tsan',['bazel','test','--jobs=2','//score/socom/test/unit:socom_test','--features=tsan','--nocache_test_results']),
 ('final-quality-tests',['bazel','test','--jobs=2','//:unit_tests','//:component_tests']),
 ('final-docs',['bazel','run','--jobs=2','//:docs']),
 ('final-traceability',['bazel','run','--jobs=2','//:traceability_gate','--','--metrics-json',str(repo/'_build/metrics.json'),'--need-type=comp_req']),
]
for name,argv in checks:
 print('START',name,flush=True)
 result=subprocess.run([sys.executable,str(repo/'.llm_tmp/run_check.py'),name,*argv],cwd=repo)
 if name in ('final-host','final-asan','final-tsan'):
  destination=repo/'.llm_tmp/evidence'/name;destination.mkdir(exist_ok=True)
  for file in (repo/'bazel-testlogs').rglob('*'):
   if file.name in ('test.xml','test.log') and file.is_file():
    target=destination/file.relative_to(repo/'bazel-testlogs');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target)
  if name!='final-host':
   binary=repo/'bazel-bin/score/socom/test/unit/socom_test'
   import hashlib
   r={'sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'instrumentation_symbols':[line for line in subprocess.check_output(['readelf','-Ws',str(binary)],text=True).splitlines() if '__asan_init' in line or '__tsan_init' in line or '__ubsan_handle_' in line]}
   (repo/'.llm_tmp/evidence'/(name+'-binary.json')).write_text(json.dumps(r,indent=2)+'\n')
 if result.returncode:
  print('STOP',name,result.returncode,flush=True);sys.exit(result.returncode)
