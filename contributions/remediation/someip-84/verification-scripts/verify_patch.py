# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions CC0, curation Apache-2.0.
# Human review pending. Assisted-by: OpenAI Codex (model revision unavailable)
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys

sys.path.insert(0, '/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / 'native'
TASK = NATIVE / '.llm_tmp'
PROJECT = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/worktrees/thinking-caps-compliance')
PACKET = PROJECT / 'contributions/remediation/someip-84'
validate_run_root(ROOT)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
original = PROJECT / 'contributions/issues/eclipse-score/inc_someip_gateway/84/imported/pr-preparation/someip-84-verified.patch'
test_path = 'score/socom/test/unit/service_identifier_tests.cpp'
diff = next(d for d in original.read_bytes().split(b'diff --git ') if d.startswith(('a/' + test_path + ' ').encode()))
body = b''.join(line[1:] for line in diff[diff.index(b'@@'):].splitlines(keepends=True) if line.startswith(b'+'))
preparation = json.loads((PACKET / 'preparation.json').read_text())
assert hashlib.sha256(body).hexdigest() == preparation['test_old_sha256']
assert body.split(b'*/', 1)[1] == (PACKET / 'source' / test_path).read_bytes().split(b'*/', 1)[1]
candidate = json.loads((PACKET / 'candidate-files.json').read_text())
check = TASK / 'patch-check'
records = []
def run(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    records.append({'argv': argv, 'cwd': str(cwd), 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    assert result.returncode == 0, result.stderr
run(['git', 'worktree', 'add', '--detach', str(check), preparation['baseline']], NATIVE)
run(['git', 'apply', '--check', '--whitespace=error-all', str(PACKET / 'submission.patch')], check)
run(['git', 'apply', '--whitespace=error-all', str(PACKET / 'submission.patch')], check)
assert all(sha(check / p) == h == sha(PACKET / 'source' / p) for p, h in candidate.items())
run(['git', 'diff', '--check'], check)
sources = json.loads((PACKET / 'candidate-source-hashes.json').read_text())
assert all(sha(check / p) == h for p, h in sources.items())
(PACKET / 'patch-verification.json').write_text(json.dumps({'captured_at_utc': datetime.now(timezone.utc).isoformat(), 'patch_sha256': sha(PACKET / 'submission.patch'), 'commands': records, 'fresh_baseline_application': True, 'all_270_candidate_source_hashes_match': True, 'all_seven_packet_source_files_match': True, 'old_new_test_executable_body_byte_identical': True}, indent=2) + '\n')
shutil.copyfile(__file__, PACKET / 'verification-scripts/verify_patch.py')
for name in ['README.md', 'PR-body.md', 'CI-applicability.md', 'IP-review-request.md', 'HUMAN-DISPOSITION.md', 'bugfix-issue-draft.md', 'commit-message.txt']:
    (PACKET / (name + '.license')).write_text('SPDX-FileCopyrightText: 2026 Eclipse SDV Hackathon Team\nSPDX-License-Identifier: Apache-2.0 AND CC0-1.0\n\nAI Disclosure: Prepared with OpenAI Codex. AI-generated portions are offered\nunder CC0-1.0; copyrightable human modifications/curation retain Apache-2.0.\nHuman review pending. Assisted-by: OpenAI Codex (model revision unavailable)\n')
(PACKET / 'artifact-manifest.json').write_text(json.dumps({'schema_version': 1, 'captured_at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Current SOME/IP preparation and exact captured evidence; no human approval or native execution by the offline verifier', 'excluded': ['artifact-manifest.json', 'verification.json'], 'files': {p.relative_to(PACKET).as_posix(): sha(p) for p in sorted(PACKET.rglob('*')) if p.is_file() and p.name not in ['artifact-manifest.json', 'verification.json']}}, indent=2) + '\n')
print('Prepared patch applies cleanly; 270 candidate hashes match; executable test body unchanged.')
