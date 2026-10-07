from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime, timezone

from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).resolve().parent
PRIOR_ROOT = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-rust-560-resume-wm0jdkb8')
WORKSPACE = PRIOR_ROOT / 'workspaces/560'
PRIOR = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue/score-rust-560-resume-wm0jdkb8-results')
DEST = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue') / (ROOT.name + '-v2')
STAMP = datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def copy(source, relative):
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


validate_run_root(ROOT)
validate_run_root(PRIOR_ROOT)
prior_manifest_hash = digest(PRIOR / 'artifact-manifest.json')
assert prior_manifest_hash == '3b3fdbd56f5b7bfac38d3f93ae2834fdee3613d01406db907160d7a2907eb216'
prior_files = json.loads((PRIOR / 'artifact-manifest.json').read_text())['files']
for relative, sha in prior_files.items():
    assert digest(PRIOR / relative) == sha, relative
vector = PRIOR / 'issues/560/provenance/final-source-hashes.json'
assert digest(vector) == '003291e718b3c937af1b0b28d7ae91c4d1b602f942ed37fbd55b8cd9acfc98e6'
source_hashes = json.loads(vector.read_text())
for relative, sha in source_hashes.items():
    assert digest(WORKSPACE / relative) == sha, relative
controls = json.loads((PRIOR / 'native-input-binding.json').read_text())['configuration_sha256']
for relative, sha in controls.items():
    assert digest(WORKSPACE / relative) == sha, relative

# Never edit an existing sealed contribution.
DEST.mkdir(exist_ok=False)
copy(ROOT / 'integration-plan.md', 'integration-plan.md')
copy(ROOT / 'export_plan.py', 'provenance/export_plan.py')
copy(ROOT / 'storage-selection.json', 'storage-selection.json')
copy(vector, 'context/final-source-hashes.json')
copies = {
    'issues/560/export/reports/supervisor.md': 'context/supervisor.md',
    'issues/560/export/reports/correction-2.md': 'context/correction-2.md',
    'issues/560/export/reports/native-check-summary.json': 'context/native-check-summary.json',
    'native-input-binding.json': 'context/native-input-binding.json',
    'test-execution-inventory.json': 'context/test-execution-inventory.json',
    'runtime/issue-current.json': 'context/issue-current.json',
    'runtime/issue-comments-current.json': 'context/issue-comments-current.json',
}
for source, target in copies.items():
    assert source in prior_files, source
    copy(PRIOR / source, target)
base = 'score/mw/com/'
selected = [
    'impl/subscription_state.h', 'impl/subscription_state_change_handler.h',
    'impl/proxy_event_base.h', 'impl/proxy_event_base.cpp',
    'impl/bindings/lola/proxy_event.cpp', 'impl/bindings/lola/subscription_state_machine.cpp',
    'rust/score_com.rs', 'rust/score_com_concept/concept.rs',
    'rust/score_com_concept/interface_macros.rs',
    'impl/rust/com-api/com-api-runtime-lola/consumer.rs',
    'impl/rust/com-api/com-api-runtime-lola/producer.rs',
    'impl/rust/com-api/com-api-runtime-lola/BUILD',
    'impl/rust/com-api/com-api-ffi-lola/bridge_ffi_lola.rs',
    'impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h',
    'impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.cpp',
    'test/basic_rust_api/BUILD', 'test/basic_rust_api/bigdata_com_api_gen.rs',
    'test/basic_rust_api/consumer_sync_apis/BUILD',
    'test/basic_rust_api/consumer_sync_apis/consumer_app.rs',
    'test/basic_rust_api/consumer_sync_apis/integration_test/BUILD',
    'test/basic_rust_api/consumer_sync_apis/integration_test/com_api_sync_api_test.py',
    'test/basic_rust_api/consumer_async_apis/consumer_app.rs',
    'test/basic_rust_api/consumer_async_apis/integration_test/BUILD',
    'test/basic_rust_api/producer_app/producer_app.rs',
    'test/basic_rust_api/etc/config.json',
    'test/partial_restart/provider_restart/consumer.cpp', 'test/testing_guidelines.md',
    'test/pkg_application.bzl', 'test/bigdata/logging.json',
]
paths = sorted(set([base + name for name in selected] + list(controls) + ['quality/integration_testing/integration_testing.bzl']))
for name in ['LICENSE', 'NOTICE', 'NOTICE.md']:
    if (WORKSPACE / name).is_file():
        paths.append(name)
for relative in paths:
    copy(WORKSPACE / relative, 'context/native/' + relative)
write_json(DEST / 'source-binding.json', {
    'schema_version': 1, 'verified_at': STAMP,
    'baseline_commit': '381d43dec900ab6a9076f3f30e7bfbdee019e26e',
    'draft_run_id': '01M4927N232FTNWEFCRTJQG7PE', 'workspace': str(WORKSPACE),
    'source_vector_path': 'context/final-source-hashes.json', 'source_vector_sha256': digest(vector),
    'source_subjects_verified': len(source_hashes), 'drift': False,
    'selected_native_inputs_sha256': {p: digest(WORKSPACE / p) for p in paths},
    'native_configuration_subjects_verified': len(controls),
    'qualification': 'pending; source and input identity are not qualification',
})
write_json(DEST / 'carried-evidence.json', {
    'evidence_class': 'carried, subject-hash-verified; no fresh native executions',
    'prior_packet': str(PRIOR), 'prior_manifest_sha256': prior_manifest_hash,
    'prior_payloads_verified': len(prior_files),
    'copied_prior_artifact_sha256': {target: prior_files[source] for source, target in copies.items()},
    'complete_raw_evidence': 'Retained in the sealed prior packet, bound by its manifest; not duplicated here.',
    'new_production_callback_coverage': 'missing; the proposed tests have not been implemented or executed',
    'acceptance': 'pending offline',
})
cases = [
    ('test_subscription_state_notifications', ['O12', 'G8'], 'real production callback: pending after withdrawal, subscribed after re-offer on the same subscription'),
    ('test_subscription_state_handler_replacement', ['G7', 'G8'], 'A replaced by B; A and B each disposed once; only B observes subsequent transitions'),
    ('test_subscription_state_handler_unset', ['G8'], 'returning unset fences A; confirmed subsequent state transitions produce no A callback'),
    ('test_subscription_state_handler_false_then_drop', ['G6', 'G8'], 'false unregisters and disposes A once; later subscription drop causes no second disposal'),
    ('test_subscription_state_handler_drop_active', ['G8'], 'active registration is disposed once on subscription drop; fresh positive-control subscription verifies transitions'),
]
write_json(DEST / 'case-specifications.json', {
    'status': 'proposed, not implemented or executed',
    'native_requirement_anchor': {'id': 'SWS_CM_00310', 'applicability': 'pending', 'source': base + 'impl/subscription_state.h'},
    'finding_ids': 'supervisor-local IDs, not native requirement/verification IDs; detailed scope is in integration-plan.md',
    'cases': [{'name': name, 'supervisor_findings': findings, 'oracle': oracle, 'status': 'not executed', 'details': 'integration-plan.md, Proposed integration cases'} for name, findings, oracle in cases],
})
new_package = '//' + base + 'test/basic_rust_api/subscription_state_apis'
old_plan = json.loads((PRIOR / 'issues/560/export/reports/check-plan.json').read_text())
checks = [
    {'kind': 'build', 'config': 'linux_x64', 'targets': [new_package + ':subscription-state-apis'], 'target_status': 'proposed, absent from bound source', 'execution_status': 'not executed'},
    {'kind': 'test', 'config': 'linux_x64', 'targets': [new_package + '/integration_test:test_subscription_state_apis'], 'target_status': 'proposed, absent from bound source', 'expected_cases': [x[0] for x in cases], 'cache': 'explicitly disabled', 'execution_status': 'not executed'},
    {'kind': 'lint', 'config': 'clippy', 'targets': [new_package + ':subscription-state-apis'], 'target_status': 'proposed, absent from bound source', 'aspect_execution': 'must be measured, no library-only substitution', 'execution_status': 'not executed'},
]
for item in old_plan['checks']:
    clone = dict(item)
    clone.pop('reason', None)
    clone['target_status'] = 'existing, prior measured labels'
    clone['execution_status'] = 'not executed in planning activity'
    clone['future_execution_rule'] = 'rerun if source/dependency/control subjects change; otherwise explicit verified carried evidence'
    if clone['kind'] == 'test':
        clone['current_callback_unit_names'] = [
            'test_get_subscription_state_maps_raw_values', 'test_handler_observed_mapped_state_and_mutated_capture',
            'test_handler_false_return_signals_cancellation', 'test_set_handler_failure_drops_captured_resource',
            'test_set_and_unset_disposes_captured_resource_exactly_once',
            'test_drop_unregisters_before_unsubscribe_and_disposes_once',
        ]
        clone['new_binary_regression_rule'] = 'execute the two existing sync/async Linux integration labels alongside the new five-case target'
    if clone['kind'] == 'query':
        clone['limitation'] = 'explicit-label query only; reverse-dependency and implementor completeness remain unmeasured'
    if clone['kind'] == 'doctest':
        clone['carried_measurement'] = 'previous explicit native execution: 17 pass, two ignored; no current rerun or Markdown-example coverage'
    checks.append(clone)
write_json(DEST / 'planned-checks.json', {'status': 'planning only, not admitted for execution', 'admission': 'resolve newly implemented labels and applicable native check capabilities first', 'checks': checks, 'unresolved': ['test-code Clippy applicability', 'native Python/format checks', 'full downstream denominator', 'mock-runtime test target', 'Markdown examples', 'qualification and human acceptance']})
write_json(DEST / 'task-envelope.json', {
    'issue': 'https://github.com/eclipse-score/communication/issues/560',
    'activity': 'production callback integration planning, completed',
    'native_source_modified': False, 'native_tests_executed': False,
    'paid_model_calls': 0, 'runtimes_started': False,
    'future_agent_model': {'alias': 'deepseek-flash', 'provider': 'deepseek', 'model': 'deepseek-v4-flash', 'fallbacks': False},
    'correction_budget': {'max': 3, 'used': 2, 'remaining': 1, 'reset': False, 'reserve_before_future_implementation': True},
    'queue_budget': {'used': 30, 'max': 36, 'remaining': 6},
    'future_proposed_write_scope': [base + 'test/basic_rust_api/subscription_state_apis/', base + 'rust/design/high_level_design_detail.md', '.rust-queue/reports/'],
    'artifact_destination': str(DEST), 'planning_scratch_root': str(ROOT),
    'offline_human_acceptance': 'pending', 'publication_authorized_by_this_plan': False,
    'exclusions': ['QNX #1278', 'new #1265 work', 'budget resets', 'fourth source correction', 'changes to references or sealed packets', 'publishing or acceptance'],
})
write_json(DEST / 'revision-history.json', {
    'supersedes': str(DEST.parent / ROOT.name),
    'superseded_manifest_sha256': 'adaa096f22cd227cc119b188ba3603df1890ad63b03e1bfbcd0dda97e3651632',
    'reason': 'Corrected local finding mappings: G7 replacement, G6 false-return teardown, G8 production gap; removed misleading historical O5/O6 references. Test oracles and budgets unchanged.',
    'superseded_packet_preserved_unchanged': True,
})
(DEST / 'README.md').write_text('''# Rust #560 production integration plan

This contribution is a source-bound operator draft for five Linux production callback/lifecycle cases. Start with [integration-plan.md](integration-plan.md); see [case specifications](case-specifications.json) and [planned native checks](planned-checks.json). Proposed targets are absent from the bound source and are not admitted runnable checks.

All 2186 prior source subjects, seven native configuration subjects and 149 prior packet payloads were verified. [Source binding](source-binding.json) and [carried evidence](carried-evidence.json) distinguish historical measurements from this unexecuted plan. Selected native sources, original notices, the current Flash supervisor and original issue retrieval are included under `context/`.

No native source edit, native test, paid model call, runtime start, publishing or acceptance occurred. #560 remains at two of three lifetime corrections used, one remaining. All other issue budgets remain unchanged. Implementation must use DeepSeek Flash only and reserve the final correction before any source change/call; a failed attempt still counts. Human engineering review remains offline and pending.

The top-level artifact manifest binds every packet payload. Complete prior raw evidence remains in the sealed results packet referenced by `carried-evidence.json`; it is not promoted to production callback coverage. This plan is understandable without Fabro, and does not claim target qualification or readiness.
''')
validate_run_root(ROOT)
validate_run_root(PRIOR_ROOT)
for relative, sha in source_hashes.items():
    assert digest(WORKSPACE / relative) == sha, relative
for relative, sha in controls.items():
    assert digest(WORKSPACE / relative) == sha, relative
write_json(DEST / 'planning-verification.json', {
    'checked_at': datetime.now(timezone.utc).isoformat(),
    'storage_bindings_validated': [str(ROOT), str(PRIOR_ROOT)],
    'prior_payloads_verified': len(prior_files), 'source_subjects_verified_before_and_after': len(source_hashes),
    'configuration_subjects_verified_before_and_after': len(controls),
    'new_native_target_directory_absent': not (WORKSPACE / (new_package[2:] )).exists(),
    'native_source_drift': False, 'native_checks_executed': False,
    'cases_specified': len(cases), 'cases_executed': 0, 'planning_assertions_are_not_native_test_results': True,
})
files = {str(p.relative_to(DEST)): digest(p) for p in sorted(DEST.rglob('*')) if p.is_file()}
write_json(DEST / 'artifact-manifest.json', {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(), 'files': files})
for relative, sha in files.items():
    assert digest(DEST / relative) == sha, relative
print(json.dumps({'packet': str(DEST), 'payloads': len(files), 'manifest_sha256': digest(DEST / 'artifact-manifest.json'), 'source_subjects_verified': len(source_hashes), 'configuration_subjects_verified': len(controls), 'corrections_used': 2, 'remaining': 1, 'native_tests_executed': 0}))
