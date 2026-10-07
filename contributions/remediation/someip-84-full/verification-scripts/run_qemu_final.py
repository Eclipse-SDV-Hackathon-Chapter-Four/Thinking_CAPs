# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Assisted-by: OpenAI Codex (model revision unavailable); human review pending.
from pathlib import Path
import subprocess,sys,shutil
repo=Path(__file__).resolve().parents[1];task=repo/'.llm_tmp'
path=str(task/'cloud-tools/usr/bin')+':/usr/bin:/bin'
tmp=str(task/'tmp')
argv=['bazel','test','--jobs=2','--config=qemu-integration','--action_env=PATH='+path,'--test_env=PATH='+path,'--action_env=TMPDIR='+tmp,'--test_env=TMPDIR='+tmp,'//quality/...','//tests/integration_test/...','--nocache_test_results']
r=subprocess.run([sys.executable,str(task/'run_check.py'),'final-qemu',*argv],cwd=repo)
destination=task/'evidence/final-qemu';destination.mkdir(exist_ok=True)
for p in (repo/'bazel-testlogs').rglob('*'):
 if p.name in ('test.xml','test.log') and p.is_file():
  target=destination/p.relative_to(repo/'bazel-testlogs');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
sys.exit(r.returncode)
