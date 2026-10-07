"""Verify terminal packets, stop only owned runtimes, and seal offline results."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('terminal_collection', Path(__file__).with_name('collect_terminal.py'))
assert SPEC and SPEC.loader
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


def main():
    C.validate_run_root(C.ROOT)
    destination = C.DEST
    assert not (destination / 'artifact-manifest.json').exists(), 'Final packet already sealed'
    result = json.loads((destination / 'queue-results.json').read_text())
    assert {i['issue'] for i in result['issues']} == {j['issue'] for j in C.JOBS}
    audit = []
    current = []
    for job in sorted(C.JOBS, key=lambda j: j['submission_order']):
        root = destination / 'issues' / str(job['issue'])
        C.verify_manifest(root)
        projection = C.api('/runs/' + job['run_id'])
        assert projection['lifecycle']['status']['kind'] in ['succeeded', 'failed', 'dead', 'cancelled']
        current.append(projection)
        state = json.loads((root / 'native/final-state.json').read_text())
        summary = json.loads((root / 'collection-summary.json').read_text())
        page = C.api('/runs/' + job['run_id'] + '/events?limit=1')
        first_retained = json.loads((root / 'native/events.jsonl').open().readline())
        assert page['data'][0] == first_retained, 'Native event history identity changed'
        control = json.loads((root / 'provenance/task.json').read_text())
        for path, expected in control['control_hashes'].items():
            assert C.digest(Path(path)) == expected, ('Control drift', path)
        agent_stages = []
        for name, stage in state['stages'].items():
            if stage.get('handler') != 'agent' or not stage.get('started_at'):
                continue
            used = stage.get('provider_used')
            model = stage.get('model')
            assert not used or (used['model'] == 'deepseek-v4-flash' and used['provider'] == 'deepseek')
            assert not model or (model['model_id'] == 'deepseek-v4-flash' and model['provider'] == 'deepseek')
            assert stage['graph_visit'] == 1, ('Repeated agent visit', name)
            agent_stages.append({'stage': name, 'state': stage['state'], 'provider_used': used, 'model': model})
        assert summary['corrections_used'] <= job['max_source_corrections']
        if not summary['supervisor_present']:
            supervisor = state['stages'].get('supervisor@1', {})
            C.save(destination / f'gaps/{job["issue"]}/supervisor-output.json', {
                'gap': 'supervisor.md missing; successful native stage is not a completed written review',
                'source': f'issues/{job["issue"]}/native/final-state.json',
                'source_sha256': C.digest(root / 'native/final-state.json'),
                'stage': 'supervisor@1', 'actual_response': supervisor.get('response'),
                'actual_state': supervisor.get('state'), 'fabricated_review': False})
        executed_tests = []
        failed_commands = []
        for native in sorted((root / 'execution').glob('check-*/native-result.json')):
            data = json.loads(native.read_text())
            for index, command in enumerate(data['checks']):
                log = Path(command['log'])
                copy = native.parent / log.name
                assert copy.exists() and C.digest(copy) == command['log_sha256']
                if command['exit_code'] != 0:
                    failed_commands.append({'attempt': native.parent.name, 'command': index,
                                            'kind': command['kind'], 'targets': command['targets'],
                                            'exit_code': command['exit_code'], 'timed_out': command['timed_out'],
                                            'log': str(copy.relative_to(destination))})
                if command['kind'] != 'test':
                    continue
                bep = native.parent / f'check-{index}-events.jsonl'
                if not bep.exists():
                    executed_tests.append({'attempt': native.parent.name, 'command': index,
                                           'gap': 'No command-specific Bazel events; execution unproven'})
                    continue
                no_cache = '--cache_test_results=no' in command['command']
                for line in bep.open():
                    event = json.loads(line)
                    if 'testResult' in event:
                        measurement = event['testResult']
                        label = event['id']['testResult']['label']
                        test_log = native.parent / 'native-testlogs' / label.removeprefix('//').replace(':', '/') / 'test.log'
                        harness = []
                        if label.startswith('//') and test_log.exists():
                            for match in re.finditer(r'^test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;', test_log.read_text(errors='replace'), re.M):
                                harness.append({'result': match[1], 'passed': int(match[2]), 'failed': int(match[3]),
                                                'ignored': int(match[4]), 'measured': int(match[5]), 'filtered_out': int(match[6]),
                                                'source': str(test_log.relative_to(destination)), 'sha256': C.digest(test_log),
                                                'basis': 'Direct Rust harness log, not XML wrapper inference'})
                        executed_tests.append({'attempt': native.parent.name, 'command': index,
                                               'label': label, 'rust_harness_summaries': harness,
                                               'status': measurement['status'],
                                               'cache_disabled_command': no_cache,
                                               'cached_locally': measurement.get('cachedLocally', False),
                                               'cached_remotely': measurement.get('cachedRemotely', False),
                                               'bep': str(bep.relative_to(destination))})
        checks = summary['attempts']
        latest = checks[-1] if checks else None
        patch = (root / f'export/communication-{job["issue"]}.patch').read_bytes()
        artifact_class = ('boundary-probe artifact; not an issue fix' if b'boundary-probe artifact' in patch
                          else 'draft patch' if patch else 'report/assessment')
        audit.append({'issue': job['issue'], 'run_id': job['run_id'], 'mode': job['mode'],
                      'native_status': summary['native_status'], 'patch_bytes': summary['patch_bytes'],
                      'corrections_used': summary['corrections_used'], 'max_corrections': summary['max_corrections'],
                      'latest_check': latest, 'agent_stages': agent_stages,
                      'operator_artifact_class': artifact_class,
                      'failed_commands': failed_commands, 'native_test_results': executed_tests,
                      'supervisor_present': summary['supervisor_present'],
                      'event_contract_version': page['event_contract_version'],
                      'acceptance': 'pending offline; no issue automatically closed'})
    C.save(destination / 'verification-audit.json', {'audited_at': C.now(), 'issues': audit,
                                                    'scope': 'Selected Linux commands; no QNX, no aggregate acceptance claim',
                                                    'docs': 'docs kind invokes build; rust_doc_test execution is not measured'})
    C.save(destination / 'native/final-runs.json', current)
    settings = C.api('/settings')
    C.save(destination / 'native/final-scheduler-settings.json', {'scheduler': settings['server']['scheduler']})
    common = ['queue.json', 'authority.json', 'execution-authority.json', 'storage-selection.json',
              'source-provenance.json', 'github-search.json', 'upstream-head.json',
              'linux-measurement-binding.json', 'linux-tools.json', 'runtime-overlays.json',
              'definition-revision.json', 'launch-verification.json', 'execution-readiness.json',
              'native-scheduler-observation.json', 'server-binding.json', 'docker-binding.json',
              'contribution-binding.json', 'execution-contribution-binding.json',
              'driver_linux.py', 'linux_launcher.py', 'tool_guard.py', 'storage.py',
              'runtime_manager.py', 'collect_terminal.py', 'collector-revision.json', 'finalize_results.py']
    for name in common:
        source = C.ROOT / name
        if source.exists():
            out = destination / 'provenance' / name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(C.safe(source.read_bytes()))
    launch = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue') / (C.ROOT.name + '-linux-execution')
    C.verify_manifest(launch)
    C.copy_tree(launch / 'runtime-notices', destination / 'licenses/runtime-notices')
    creation = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue') / C.ROOT.name
    C.verify_manifest(creation)
    C.save(destination / 'provenance/previous-packets.json', {
        'creation': {'path': str(creation), 'manifest_sha256': C.digest(creation / 'artifact-manifest.json')},
        'linux_launch': {'path': str(launch), 'manifest_sha256': C.digest(launch / 'artifact-manifest.json')},
        'reuse': 'Verified bound historical packets; previous contents unchanged'})
    baseline = json.loads((C.ROOT / 'queue.json').read_text())['baseline']
    for name in ['.bazelrc', 'quality/static_analysis/static_analysis.bazelrc']:
        data = subprocess.check_output(['git', '-C', str(C.ROOT / 'target'), 'show', baseline + ':' + name])
        out = destination / 'provenance/native-configs' / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(C.safe(data))
    for name in ['LICENSE', 'NOTICE']:
        data = subprocess.check_output(['git', '-C', str(C.ROOT / 'target'), 'show', baseline + ':' + name])
        out = destination / 'licenses/communication' / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(C.safe(data))
    # Final API observation above confirms all selected IDs terminal before lifecycle cleanup.
    C.validate_run_root(C.ROOT)
    shutdown = subprocess.run(['uv', 'run', '--frozen', 'python', str(C.ROOT / 'runtime_manager.py'), 'stop'],
                              capture_output=True, timeout=50)
    C.save(destination / 'lifecycle/docker-stop-command.json', {'exit_code': shutdown.returncode,
            'stdout': shutdown.stdout.decode(errors='replace'), 'stderr': shutdown.stderr.decode(errors='replace')})
    assert shutdown.returncode == 0, 'Owned Docker cleanup incomplete'
    for name in ['docker-shutdown.json', 'docker-binding.json']:
        p = C.ROOT / name
        if p.exists():
            C.save(destination / 'lifecycle' / name, json.loads(p.read_text()))
    pid = C.BINDING['pid']
    proc = Path(f'/proc/{pid}')
    binary = Path('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro')
    assert C.digest(binary) == '8d7ef1e66f19a4da4b806ea64944d58ee33652e959f46c142645c4feb7468fbe', 'Owned Fabro binary changed'
    assert proc.exists() and (proc / 'exe').resolve() == binary.resolve(), 'Owned Fabro identity mismatch'
    env = dict(f.partition(b'=')[::2] for f in (proc / 'environ').read_bytes().split(b'\0') if b'=' in f)
    assert env.get(b'FABRO_HOME') == str(C.PRIVATE).encode(), 'Private Fabro root mismatch'
    start_identity = (proc / 'stat').read_text().split(') ', 1)[1].split()[19]
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + 12
    while proc.exists() and time.monotonic() < deadline:
        time.sleep(0.2)
    exited = not proc.exists()
    if proc.exists():
        fields = (proc / 'stat').read_text().split(') ', 1)[1].split()
        exited = fields[0] == 'Z' or fields[19] != start_identity
    assert exited, 'Fabro still active; preserve state and inspect, do not force kill'
    C.save(destination / 'lifecycle/fabro-shutdown.json', {'pid': pid, 'binary': str(binary),
            'binary_sha256': C.digest(binary), 'private_state': str(C.PRIVATE),
            'signal': 'SIGTERM', 'owned_process_exited': exited, 'completed_at': C.now(),
            'selected_runs_terminal_before_stop': len(current)})
    rows = []
    for item in audit:
        latest = item['latest_check']
        check = ('passed selected checks' if latest and latest['passed'] else
                 'failed/missing selected checks' if latest else 'historical reuse; no new checks')
        artifact = item['operator_artifact_class']
        review = 'written review present' if item['supervisor_present'] else '**written review missing**'
        rows.append(f"| [#{item['issue']}](issues/{item['issue']}/collection-summary.json) | {artifact} | {item['native_status']} | {check} | {review} | {item['corrections_used']}/{item['max_corrections']} |")
    readme = f'''# S-CORE Rust API queue results

All {len(audit)} selected native Fabro runs are terminal and their complete available
patches, reports, native events and Linux measurement evidence are exported. This is a
results packet, not a declaration that all issues are solved. Engineering acceptance
and adoption remain pending offline; no issue was closed and no new results were pushed.

| Issue | Artifact | Fabro status | Verification disposition | Supervisor artifact | Corrections |
|---|---|---|---|---|---|
''' + '\n'.join(rows) + '''

Every observed agent, correction and supervisor call used `deepseek-v4-flash` from
DeepSeek (configured alias `deepseek-flash`), with no fallback. New issue runs used at
most three correction stages. #1265 reused historical evidence with zero new fixes;
its prior exhausted budgets were preserved. QNX #1278 was excluded.

All workspaces started from communication baseline `''' + baseline + '''`.
The native scheduler ran up to five jobs; its startup concurrency flag of one was not
applied. Prerequisite hints affected submission order only. Workspaces remained
independent; no predecessor patch or backend contract was silently integrated.

Each issue directory contains a bound exported binary-capable patch (including new
files), its final changed source, reports, captured issue/context, exact workflow,
initial/final source hashes, raw protected check outputs, complete paginated native
events, final run/state records and a terminal collection summary. Per-issue manifests
and the packet manifest bind every payload. Native checkpoint commits were retained;
the collector's separate index verified each patch against final source without
changing a native index or creating another correction.

`verification-audit.json` records actual agent identities, all failed commands and
command-specific Bazel test-result events. Consult each supervisor and raw logs for
the issue-specific blocker and applicability findings. A successful Fabro export can
retain failed checks; it is not a passing native verification result.
If a supervisor stage completed without writing its required report, the missing
review remains explicit in the table and `gaps/`; native stage output is preserved
without inventing a replacement review or resetting the correction budget.

Known measurement limits: `docs` checks built their selected targets and did not execute
`rust_doc_test`. Test XML copied during an attempt may also include earlier runs;
command-specific Bazel events identify actual executed test targets. Inner Rust case
totals are not inferred from wrapper XML. Checks remain tied to their measured subject
hashes; a mismatch is stale evidence, not current verification. Native requirement,
safety, qualification and acceptance gaps remain explicit in the reports.

`provenance/` preserves source/tool/config/storage/authority bindings and verified
links to the unchanged creation and Linux launch packets. Original issue text and
license notices are preserved. Runtime binaries are identified by hash; raw tool
caches are retained on the bound SSD rather than copied here. Credentials and private
Fabro/vault/server state remain internal and are excluded from exports.

The selected SSD binding was validated before collection and cleanup. After all
selected runs became terminal and their evidence was retained, only this queue's owned
rootless Docker and private Fabro server were stopped. `lifecycle/` retains cleanup
evidence. No active queue was relocated, no disk reformatted, and no budgets reset.

Next step: review the issue packets offline and decide which proposals to adopt or
which unresolved checks need a separately authorized follow-up run.
Recommended model: deepseek-flash — the user-required model for any subsequent Fabro run.
'''
    (destination / 'README.md').write_bytes(C.safe(readme.encode()))
    findings = '''# Operator observations on the execution boundary

These are collected source/command observations, not engineering acceptance or a
replacement for a missing Flash supervisor review. No current queue controls, source
corrections, budgets or run IDs were changed to resolve these findings.

## Clippy configuration failure

The pinned native `.bazelrc` imports `quality/static_analysis/static_analysis.bazelrc`
at line 188. The launcher also passes this same file as an explicit `--bazelrc` startup
argument. The imported config defines `build:clippy --aspects=...%clippy_strict`.
Raw lint commands report both duplicate rc reads and
`aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once`.
The duplicate configuration is an operator launcher problem, not a proven Rust source
defect. Any future launcher revision should load this native configuration once and
measure it against a pinned subject. Existing lint failures remain failures; successful
builds/tests do not provide missing lint evidence. Already exhausted budgets are not
reset by this finding.

Sources: `provenance/linux_launcher.py`, `provenance/native-configs/.bazelrc`,
`provenance/native-configs/quality/static_analysis/static_analysis.bazelrc`, and
command log references in `verification-audit.json`.

## Relocation capability and source configuration reads

The registered file-tool guard allows `read_file`, `write_file`, `edit_file`, `glob`
and bounded search, but has no delete/rename capability. It also rejects native source
`.json` reads under the same suffix rule used for raw evidence. Issue #741 needs a file
relocation and native example configuration reads; this boundary was too restrictive
for that operation. Its exported patch is a comment-only boundary-probe BUILD file,
not the requested relocation and not a candidate fix to adopt. The supervisor retains
the unapplied move specification and the missing acceptance checks.

A future authorized workflow revision needs scoped relocation support and bounded
reads of native configuration files while continuing to protect credentials and
collector-owned evidence. No current source was moved by the operator to conceal this
failure or bypass the Flash-only constraint.

Sources: `provenance/tool_guard.py`, #741's exact patch, measured command logs,
and `issues/741/export/reports/supervisor.md`.

## Missing written reviews and documentation measurements

A successful supervisor stage does not establish that its required report was written.
Missing `supervisor.md` artifacts remain flagged in `verification-audit.json` and the
README table; `gaps/` preserves their actual native stage outputs. No replacement review
was synthesized. Likewise, `docs` invokes build rather than executing Rust doctests;
its success must not be reported as a passing doctest execution.

Next step: review these runtime findings and issue dispositions before authorizing any
new run or accepting a patch.
Recommended model: deepseek-flash — required for any future Fabro agent work.
'''
    (destination / 'operator-findings.md').write_bytes(C.safe(findings.encode()))
    C.validate_run_root(C.ROOT)
    C.save(destination / 'artifact-manifest.json', {'schema_version': 1, 'prepared_at': C.now(),
            'files': {str(p.relative_to(destination)): C.digest(p) for p in destination.rglob('*')
                      if p.is_file() and p != destination / 'artifact-manifest.json'}})
    C.verify_manifest(destination)
    C.save(C.ROOT / 'results-contribution-binding.json', {'path': str(destination),
             'manifest_sha256': C.digest(destination / 'artifact-manifest.json'),
             'subjects': len(json.loads((destination / 'artifact-manifest.json').read_text())['files']),
             'selected_runs_terminal': len(audit), 'sealed_at': C.now(),
             'engineering_acceptance': 'pending offline'})
    print(json.dumps(json.loads((C.ROOT / 'results-contribution-binding.json').read_text())))


if __name__ == '__main__':
    main()
