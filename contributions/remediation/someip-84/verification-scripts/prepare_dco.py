# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex. AI portions CC0; curation Apache-2.0.
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
CHECK = TASK / 'patch-check'
PROJECT = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/worktrees/thinking-caps-compliance')
PACKET = PROJECT / 'contributions/remediation/someip-84'
validate_run_root(ROOT)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = datetime.now(timezone.utc).isoformat()
baseline = 'f8a196c3b16d5172d898394ab99b0ed81346d63d'
patch_hash = 'cd93cb62c08b80d857b1795b203e133aa7d3d403d281af61bac7d9bcb60d4ea1'
assert sha(PACKET / 'submission.patch') == patch_hash
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=CHECK, text=True).strip() == baseline
sources = json.loads((PACKET / 'candidate-source-hashes.json').read_text())
changed = json.loads((PACKET / 'candidate-files.json').read_text())
assert all(sha(CHECK / p) == h == sha(NATIVE / p) for p, h in sources.items())
message = (PACKET / 'commit-message.txt').read_text().split('\nPREPARATION NOTE:', 1)[0].rstrip()
trailer = 'Signed-off-by: Jefferson Nascimento <jnsagai@gmail.com>'
assert 'Signed-off-by:' not in message
message += '\n' + trailer + '\n'
message_path = TASK / 'native-dco-commit-message.txt'
message_path.write_text(message)
records = []
def run(argv, cwd=CHECK):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    records.append({'argv': argv, 'cwd': str(cwd), 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout
run(['git', 'add', '--', *changed])
run(['git', 'diff', '--cached', '--check'])
config = ['git', '-c', 'user.name=Jefferson Nascimento', '-c', 'user.email=jnsagai@gmail.com']
run([*config, 'commit', '--file=' + str(message_path)])
commit = run(['git', 'rev-parse', 'HEAD']).strip()
assert run(['git', 'rev-parse', 'HEAD^']).strip() == baseline
assert run(['git', 'status', '--porcelain']) == ''
assert run(['git', 'show', '-s', '--format=%an <%ae>%n%cn <%ce>']).splitlines() == ['Jefferson Nascimento <jnsagai@gmail.com>'] * 2
assert run(['git', 'show', '-s', '--format=%B']).count(trailer) == 1
assert set(run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD']).splitlines()) == set(changed)
assert all(sha(CHECK / p) == h for p, h in sources.items())
mail = subprocess.check_output(['git', 'format-patch', '-1', '--stdout', '--binary', '--full-index', '--no-signature', 'HEAD'], cwd=CHECK)
mail_path = PACKET / 'submission-with-dco.patch'
mail_path.write_bytes(mail)
plain = (PACKET / 'submission.patch').read_bytes()
assert mail[mail.index(b'diff --git '):].rstrip(b'\n') == plain.rstrip(b'\n')
fresh = TASK / 'dco-patch-check'
run(['git', 'worktree', 'add', '--detach', str(fresh), baseline], NATIVE)
run(['git', 'apply', '--check', '--whitespace=error-all', str(mail_path)], fresh)
run(['git', 'apply', '--whitespace=error-all', str(mail_path)], fresh)
assert all(sha(fresh / p) == h for p, h in sources.items())
run(['git', 'diff', '--check'], fresh)
(PACKET / 'commit-message.txt').write_text(message)
confirmation = {'id': 'eclipse-score/inc_someip_gateway#84', 'captured_at_utc': stamp, 'origin': 'Explicit user instruction in this conversation after explanation of the DCO and request for personal sign-off confirmation', 'user_statement': 'ok, prepare the DCO for me', 'action_authorized': 'Prepare the named contributor DCO sign-off for this SOME/IP patch', 'human_author': {'legal_name': 'Jefferson Nascimento', 'email': 'jnsagai@gmail.com', 'eclipse_username': 'jnascimento6p0'}, 'signed_off_by': trailer, 'subject': {'baseline': baseline, 'verified_plain_patch_sha256': patch_hash, 'native_commit': commit, 'mail_patch_sha256': sha(mail_path)}, 'prior_review_packet_commit': '795df6c5', 'publication_authorized': False, 'technical_review_or_ip_approval_supplied': False, 'scope': 'SOME/IP #84 only; no certification for Puru or other contributions; records the user instruction and prepared sign-off, not a digital signature or an agent-created personal declaration'}
(PACKET / 'DCO-confirmation.json').write_text(json.dumps(confirmation, indent=2) + '\n')
verification = {'captured_at_utc': stamp, 'native_commit': commit, 'base': baseline, 'mail_patch_sha256': sha(mail_path), 'verified_plain_patch_sha256': patch_hash, 'native_author_and_committer': 'Jefferson Nascimento <jnsagai@gmail.com>', 'signed_off_by_occurrences': 1, 'seven_changed_files_match': True, 'all_270_candidate_source_hashes_match': True, 'code_diff_identical_except_trailing_mail_separator_newlines': True, 'fresh_baseline_mail_patch_application': True, 'native_tests_rerun': False, 'native_test_evidence': 'Prior native results retained with exact same candidate hashes; change is commit/mail metadata only', 'commands': records}
(PACKET / 'dco-verification.json').write_text(json.dumps(verification, indent=2) + '\n')
shutil.copyfile(__file__, PACKET / 'verification-scripts/prepare_dco.py')
status_path = PACKET / 'status.json'
status = json.loads(status_path.read_text())
status['observed_at'] = stamp
status['remaining_gates'].remove('Actual author DCO certification on eventual native commit')
status['artifacts'].update({'dco_confirmation': 'remediation/someip-84/DCO-confirmation.json', 'mail_patch_with_dco': 'remediation/someip-84/submission-with-dco.patch', 'dco_verification': 'remediation/someip-84/dco-verification.json'})
status['dco'] = {'status': 'User-authorized sign-off prepared on local native commit', 'signed_off_by': trailer, 'native_commit': commit, 'mail_patch_sha256': sha(mail_path), 'published': False, 'human_review_and_ip_approval': 'Remain pending'}
status_path.write_text(json.dumps(status, indent=2) + '\n')
registry_path = PROJECT / 'contributions/registry.json'
registry = json.loads(registry_path.read_text())
entry = next(i for i in registry['issues'] if i['id'] == status['id'])
entry['current_preparation'].update({'native_commit': commit, 'mail_patch_with_dco': 'remediation/someip-84/submission-with-dco.patch', 'mail_patch_sha256': sha(mail_path), 'dco': 'User-authorized sign-off prepared; unpublished'})
registry_path.write_text(json.dumps(registry, indent=2) + '\n')
print(json.dumps({'native_commit': commit, 'mail_patch_sha256': sha(mail_path), 'signed_off_by': trailer, 'source_hashes_unchanged': True, 'published': False}, indent=2))
