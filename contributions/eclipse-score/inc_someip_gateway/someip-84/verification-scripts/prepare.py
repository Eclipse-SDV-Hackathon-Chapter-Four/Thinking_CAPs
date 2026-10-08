# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: This scratch preparation helper was generated with OpenAI Codex.
# AI portions are offered under CC0-1.0; copyrightable curation retains Apache-2.0.
# Human review pending. Assisted-by: OpenAI Codex (model revision unavailable)
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

sys.path.insert(0, '/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root, build_environment

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / 'native'
TASK = NATIVE / '.llm_tmp'
PROJECT = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/worktrees/thinking-caps-compliance')
validate_run_root(ROOT)
patch = PROJECT / 'contributions/issues/eclipse-score/inc_someip_gateway/84/imported/pr-preparation/someip-84-verified.patch'
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=NATIVE, text=True).strip()
assert base == 'f8a196c3b16d5172d898394ab99b0ed81346d63d'
subprocess.run(['git', 'apply', '--check', '--whitespace=error-all', str(patch)], cwd=NATIVE, check=True)
subprocess.run(['git', 'apply', '--whitespace=error-all', str(patch)], cwd=NATIVE, check=True)
original = json.loads((PROJECT / 'contributions/issues/eclipse-score/inc_someip_gateway/84/imported/pr-preparation/candidate-files.json').read_text())
for name, identity in original.items():
    assert hashlib.sha256((NATIVE / name).read_bytes()).hexdigest() == identity['sha256'], name
file = NATIVE / 'score/socom/test/unit/service_identifier_tests.cpp'
old = file.read_text()
notice = ''' * AI Disclosure: This new regression file was largely generated with OpenAI
 * Codex. AI-generated portions are offered under CC0-1.0; copyrightable human
 * modifications and curation retain Apache-2.0. Human review of this amended
 * revision is required before merge. The prior approval covers the old revision.
 * Assisted-by: OpenAI Codex (historical model revision not retained)
 *
 * SPDX-License-Identifier: Apache-2.0 AND CC0-1.0'''
assert ' * SPDX-License-Identifier: Apache-2.0' in old
new = old.replace(' * SPDX-License-Identifier: Apache-2.0', notice, 1)
assert old.split('*/', 1)[1] == new.split('*/', 1)[1]
file.write_text(new)
shutil.copyfile(PROJECT / 'LICENSES/CC0-1.0.txt', NATIVE / 'LICENSES/CC0-1.0.txt')
subprocess.run(['git', 'add', '--intent-to-add', 'score/socom/test/unit/service_identifier_tests.cpp', 'LICENSES/CC0-1.0.txt'], cwd=NATIVE, check=True)
subprocess.run(['git', 'diff', '--check'], cwd=NATIVE, check=True)
environment = build_environment(ROOT)
environment['TMPDIR'] = str(TASK / 'tmp')
Path(environment['TMPDIR']).mkdir(exist_ok=True)
tools = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-someip84-tools-0ptca_j_/bin')
bin_dir = TASK / 'bin'
bin_dir.mkdir(exist_ok=True)
(bin_dir / 'bazel').write_text('#!/bin/sh\nexec "' + str(tools / 'bazel') + '" --output_user_root="' + str(ROOT / 'bazel-output') + '" "$@"\n')
(bin_dir / 'bazel').chmod(0o700)
environment['PATH_PREFIX'] = str(bin_dir) + ':' + str(tools)
environment['LD_LIBRARY_PATH'] = '/home/jefferson/.local/share/s-core-tools/llvm-19.1.7/usr/lib/x86_64-linux-gnu'
(TASK / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n')
policy_paths = ['AGENTS.md', 'CONTRIBUTION.md', '.pre-commit-config.yaml', 'MODULE.bazel', 'MODULE.bazel.lock', '.bazelrc', '.bazelversion', 'BUILD', 'static_analysis.bazelrc']
policy_paths += [p.relative_to(NATIVE).as_posix() for p in sorted((NATIVE / '.github/instructions').glob('*.md'))]
policy_paths += [p.relative_to(NATIVE).as_posix() for p in sorted((NATIVE / '.github/workflows').glob('*'))]
policy = {name: hashlib.sha256((NATIVE / name).read_bytes()).hexdigest() for name in policy_paths if (NATIVE / name).is_file()}
(TASK / 'preparation.json').write_text(json.dumps({'baseline': base, 'historical_patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'original_candidate_file_hashes_match': True, 'new_test_executable_body_unchanged': True, 'test_old_sha256': hashlib.sha256(old.encode()).hexdigest(), 'test_new_sha256': hashlib.sha256(new.encode()).hexdigest(), 'policy_hashes': policy, 'human_review': 'Pending for amended revision', 'DCO': 'Actual author certification pending'}, indent=2) + '\n')
print(subprocess.check_output(['git', 'diff', '--stat'], cwd=NATIVE, text=True))
