# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions are offered under CC0.
# Copyrightable curation retains Apache-2.0. Human review pending.
# Assisted-by: OpenAI Codex (model revision unavailable)
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import sys

sys.path.insert(0, '/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / 'native'
TASK = NATIVE / '.llm_tmp'
PROJECT = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/worktrees/thinking-caps-compliance')
PACKET = PROJECT / 'contributions/remediation/someip-84'
validate_run_root(ROOT)
stamp = datetime.now(timezone.utc).isoformat()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def put(name, data):
    path = PACKET / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')
def copy(source, destination):
    path = PACKET / destination
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, path)

preparation = json.loads((TASK / 'preparation.json').read_text())
changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=NATIVE, text=True).splitlines()
assert len(changed) == 7
assert all(sha(NATIVE / p) == h for p, h in preparation['policy_hashes'].items())
candidate = {p: sha(NATIVE / p) for p in changed}
positive = ['gcc-tests', 'clang-recorded-profile-tests', 'bazel-format', 'bazel-socom-unit', 'precommit-all-files']
for name in positive:
    record = json.loads((TASK / 'evidence' / (name + '.command.json')).read_text())
    assert record['exit_code'] == 0
    assert record['source_hashes'] == candidate
for name in ['gcc-tests', 'clang-recorded-profile-tests']:
    result = json.loads((TASK / 'evidence' / (name + '.json')).read_text())
    assert (result['tests'], result['failures'], result['disabled'], result['errors']) == (91, 0, 0, 0)
control = json.loads((TASK / 'evidence/baseline-control-tests.json').read_text())
assert (control['tests'], control['failures']) == (1, 1)
xml_path = NATIVE / 'bazel-testlogs/score/socom/test/unit/socom_test/test.xml'
xml = ET.parse(xml_path).getroot().attrib
assert (xml['tests'], xml['failures'], xml['errors'], xml['disabled']) == ('689', '0', '0', '0')
subprocess.run(['git', 'diff', '--check'], cwd=NATIVE, check=True)
patch = subprocess.check_output(['git', 'diff', '--binary', '--full-index', '--no-ext-diff', '--no-textconv', 'HEAD'], cwd=NATIVE)
(PACKET / 'submission.patch').write_bytes(patch)
put('candidate-files.json', candidate)
for p in changed:
    copy(NATIVE / p, 'source/' + p)
for p in preparation['policy_hashes']:
    copy(NATIVE / p, 'native-policy/' + p)
for p in ['.github/PULL_REQUEST_TEMPLATE/bug_fix.md', '.github/ISSUE_TEMPLATE/bug_fix.md', '.github/CODEOWNERS', 'NOTICE', 'LICENSES/Apache-2.0.txt']:
    copy(NATIVE / p, 'native-policy/' + p)
for p in sorted((TASK / 'evidence').iterdir()):
    if p.is_file():
        copy(p, 'evidence/' + p.name)
copy(xml_path, 'evidence/native-socom-test.xml')
copy(xml_path.with_name('test.log'), 'evidence/native-socom-test.log')
for p in ['prepare.py', 'checks.py', 'seal.py', 'preparation.json', 'environment.json', 'bin/bazel']:
    copy(TASK / p, 'verification-scripts/' + p)
copy(ROOT / 'storage-selection.json', 'environment/storage-selection.json')
original_root = PROJECT / 'contributions/issues/eclipse-score/inc_someip_gateway/84/imported'
original_candidates = json.loads((original_root / 'pr-preparation/candidate-files.json').read_text())
for p, identity in original_candidates.items():
    if p != 'score/socom/test/unit/service_identifier_tests.cpp':
        assert candidate[p] == identity['sha256']
old_test = original_candidates['score/socom/test/unit/service_identifier_tests.cpp']['sha256']
assert old_test == preparation['test_old_sha256']
assert candidate['score/socom/test/unit/service_identifier_tests.cpp'] == preparation['test_new_sha256']
review = json.loads((original_root / 'factory/runs/score-someip84-repair-b4ard87e/review-packet.json').read_text())
source_hashes = {p: sha(NATIVE / p) for p in sorted(set(review['source_hashes']) | set(changed))}
differences = {p: {'historical': h, 'current': source_hashes[p]} for p, h in review['source_hashes'].items() if source_hashes[p] != h}
assert list(differences) == ['score/socom/test/unit/service_identifier_tests.cpp']
put('candidate-source-hashes.json', source_hashes)
copy(original_root / 'factory/runs/score-someip84-repair-b4ard87e/external-user-approval.json', 'historical-owner-approval.json')
snapshot = json.loads(Path('/tmp/thinking-caps-someip-current.json').read_text())
put('upstream-observation.json', {'captured_on': '2026-10-07', 'api_source': 'https://api.github.com/repos/eclipse-score/inc_someip_gateway', 'default_branch': snapshot['repository']['default_branch'], 'head': snapshot['head']['sha'], 'issue': {k: snapshot['issue'][k] for k in ['html_url', 'number', 'title', 'state', 'updated_at', 'comments', 'body']}, 'open_prs_observed': [{k: pr[k] for k in ['html_url', 'number', 'title', 'state', 'draft', 'body']} for pr in snapshot['pulls']], 'scope': 'Observed open PR listing, not an exhaustive history or maintainer scope acceptance'})
request = urllib.request.Request('https://api.eclipse.org/git/eca/lookup?q=jnascimento6p0', headers={'User-Agent': 'Thinking-CAPs-contribution-compliance'})
with urllib.request.urlopen(request, timeout=45) as response:
    put('eca-lookup.json', {'captured_at_utc': stamp, 'url': request.full_url, 'user': 'jnascimento6p0', 'http_status': response.status, 'body': response.read().decode(), 'meaning': 'Lookup succeeds; eventual native commit author/committer checks remain required'})
request = urllib.request.Request('https://www.eclipse.org/projects/handbook/', headers={'User-Agent': 'Thinking-CAPs-contribution-compliance'})
with urllib.request.urlopen(request, timeout=45) as response:
    handbook = PACKET / 'native-policy/eclipse-project-handbook.html'
    handbook.write_bytes(response.read())
put('policy-observation.json', {'captured_at_utc': stamp, 'handbook_url': request.full_url, 'sha256': sha(handbook), 'scope': 'AI disclosure, human review and IP policy; native contribution instructions copied from exact baseline'})
environment = json.loads((TASK / 'environment.json').read_text())
tool_paths = {
    'bazel-8.6.0': Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-someip84-tools-0ptca_j_/bin/bazel'),
    'gcc-12': Path('/usr/bin/x86_64-linux-gnu-g++-12'),
    'clang-19': Path('/home/jefferson/.local/share/s-core-tools/llvm-19.1.7/usr/lib/llvm-19/bin/clang++'),
    'bazel-output-wrapper': TASK / 'bin/bazel',
}
put('tool-identities.json', {'captured_at_utc': stamp, 'tools': {name: {'path': str(p), 'resolved_path': str(p.resolve()), 'sha256': sha(p)} for name, p in tool_paths.items()}, 'environment': environment, 'native_dependencies': 'Unchanged MODULE.bazel, MODULE.bazel.lock and .bazelrc; fresh Bazel output/cache under this run; pre-commit revisions pinned by unchanged native configuration'})
preparation.update({'captured_at_utc': stamp, 'prepared_patch_sha256': sha(PACKET / 'submission.patch'), 'changed_files': candidate, 'candidate_source_files': len(source_hashes), 'candidate_source_differences_from_historical_packet': differences, 'policy_files_unchanged_after_precommit': True, 'native_commit': None, 'patch_format': 'Plain binary Git diff against baseline; no human DCO added', 'native_pr_created': False, 'historical_evidence_reuse': 'Original integration/profiling measurements retained as history; no claim those commands ran on the amended file header and added CC0 text'})
put('preparation.json', preparation)
put('native-results.json', {'captured_at_utc': stamp, 'baseline': preparation['baseline'], 'patch_sha256': preparation['prepared_patch_sha256'], 'candidate_files': candidate, 'GCC_12_focused': {'tests': 91, 'failures': 0}, 'Clang_19_focused': {'tests': 91, 'failures': 0, 'external_google_test_flags': 'Historical profile: -Wall -Wextra, without -Werror for third-party GoogleTest; project sources retain -Werror'}, 'baseline_negative_control': {'tests': 1, 'failures': 1, 'expected': True}, 'native_format': {'targets': 4, 'passed': 4}, 'native_socom_unit': {'tests': 689, 'failures': 0, 'disabled': 0, 'errors': 0, 'cached_test_results': False}, 'precommit_all_files': {'exit_code': 0, 'all_hooks_passed': True}, 'retained_failed_attempts': ['Clang GoogleTest compile with harness -Werror rejected upstream libstdc++ deprecation; retried using retained historical third-party profile', 'Negative control relocation lacked local include path; corrected harness include path; original failed logs retained'], 'warning_disposition': 'Native build reports Java option deprecation and third-party GoogleTest/libstdc++ deprecation. No native warning policy changed. See exact stderr.'})
prefix = 'remediation/someip-84/'
status = {'id': 'eclipse-score/inc_someip_gateway#84', 'observed_at': stamp, 'ready_for_official_merge': False, 'ai_assistance': ['OpenAI Codex (historical model revision not retained)', 'OpenAI Codex (compliance preparation; model revision unavailable)'], 'human_review': 'Earlier scoped approval retained; amended patch awaits actual human review', 'remaining_gates': ['Actual author DCO certification on eventual native commit', 'Human review of this exact amended patch, AI provenance extent and project scope acceptance', 'Project committer determination of net new IP and required Eclipse IP Team review/disposition', 'Remaining applicable upstream CI and omitted-platform disposition; no full CI pass claimed', 'Publication remains restricted by prior explicit user instruction; no native PR created'], 'artifacts': {'patch': prefix + 'submission.patch', 'pr_body': prefix + 'PR-body.md', 'commit_message_guidance': prefix + 'commit-message.txt', 'native_results': prefix + 'native-results.json', 'human_disposition': prefix + 'HUMAN-DISPOSITION.md', 'ip_review_request': prefix + 'IP-review-request.md', 'ci_matrix': prefix + 'CI-applicability.md', 'evidence_manifest': prefix + 'artifact-manifest.json'}, 'patch_provenance': {'original_path': 'issues/eclipse-score/inc_someip_gateway/84/imported/pr-preparation/someip-84-verified.patch', 'original_sha256': preparation['historical_patch_sha256'], 'prepared_sha256': preparation['prepared_patch_sha256'], 'source_diff_unchanged': False, 'note': 'New test file AI/licence comment and complete CC0 terms added; five other source/build files exact-hash unchanged from original candidate, test executable body unchanged'}, 'native_policy_unchanged': True, 'eca_lookup_http_status': 200}
put('status.json', status)
registry_path = PROJECT / 'contributions/registry.json'
registry = json.loads(registry_path.read_text())
entry = next(i for i in registry['issues'] if i['id'] == status['id'])
entry['compliance_status'] = prefix + 'status.json'
entry['prepared_pr_draft'] = prefix + 'PR-body.md'
entry['engineering_review'] = 'historical_scoped_approval_retained_amended_revision_review_pending'
entry['current_preparation'] = {'record': prefix + 'README.md', 'native_results': prefix + 'native-results.json', 'baseline': preparation['baseline'], 'patch_sha256': preparation['prepared_patch_sha256'], 'native_pr_created': False}
registry_path.write_text(json.dumps(registry, indent=2) + '\n')
print(json.dumps({'patch_sha256': preparation['prepared_patch_sha256'], 'changed_files': len(candidate), 'candidate_sources': len(source_hashes), 'tests': xml['tests'], 'native_checks': 'passed'}, indent=2))
