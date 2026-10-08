"""Seal terminal native evidence and stop only the owned verification runtimes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import time
import urllib.request

from storage import validate_run_root

ROOT = Path(__file__).parent
DEST = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue') / (ROOT.name + '-results')


def digest(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def main():
    validate_run_root(ROOT)
    assert not (DEST / 'artifact-manifest.json').exists(), 'Already sealed; preserve packet'
    binding = json.loads((ROOT / 'server-binding.json').read_text())
    private = Path(binding['private_state'])
    token = json.loads((private / 'operator-secret.json').read_text())['token']
    run_id = json.loads((ROOT / 'queue.json').read_text())['jobs'][0]['run_id']
    req = urllib.request.Request(binding['url'] + '/api/v1/runs/' + run_id,
                                 headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=15) as response:
        projection = json.load(response)
    assert projection['lifecycle']['status']['kind'] in ['succeeded', 'failed', 'dead', 'cancelled']
    assert (DEST / 'issues/560/artifact-manifest.json').exists(), 'Complete collector first'
    issue_manifest = json.loads((DEST / 'issues/560/artifact-manifest.json').read_text())
    for name, expected in issue_manifest['files'].items():
        assert digest(DEST / 'issues/560' / name) == expected, name
    secrets = [token.encode()]
    for line in Path('/home/jefferson/.config/sesn/deepseek.env').read_text().splitlines():
        for part in shlex.split(line, comments=True):
            if part.startswith('DEEPSEEK_API_KEY='):
                secrets.append(part.partition('=')[2].encode())
    pid = binding['pid']
    proc = Path('/proc') / str(pid)
    environ = proc.joinpath('environ').read_bytes().split(b'\0')
    assert ('FABRO_HOME=' + str(private)).encode() in environ, 'PID ownership drift'
    for item in environ:
        if item.startswith(b'SESSION_SECRET='):
            secrets.append(item.partition(b'=')[2])
    assert os.getpgid(pid) == pid
    # Fabro rewrites its process title. Executable identity, private HOME and
    # owned process group are stronger evidence than mutable argv contents.
    assert digest(proc.joinpath('exe')) == binding['fabro_sha256'], 'Executable identity drift'
    # Stop only the dedicated private server process group after terminal collection.
    os.killpg(pid, signal.SIGTERM)
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        try:
            if proc.joinpath('stat').read_text().split(') ', 1)[1].split()[0] == 'Z':
                break
        except FileNotFoundError:
            break
        time.sleep(.2)
    members = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            if os.getpgid(int(p.name)) == pid and p.joinpath('stat').read_text().split(') ', 1)[1].split()[0] != 'Z':
                members.append(int(p.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    if members:
        os.killpg(pid, signal.SIGKILL)
        raise RuntimeError('Owned server group required forced stop; verify before sealing')
    save(ROOT / 'server-shutdown.json', {'owned_server_stopped': True, 'pid': pid,
                                        'owned_group_running_members': members,
                                        'global_servers_modified': False})
    stop = subprocess.run(['/home/jefferson/s-core_sw_fabric/.venv/bin/python',
                           str(ROOT / 'runtime_manager.py'), 'stop'], capture_output=True)
    assert stop.returncode == 0, 'Verify owned Docker shutdown'
    native = DEST / 'issues/560'
    summary = json.loads((native / 'collection-summary.json').read_text())
    ledger = json.loads((ROOT / 'jobs/560/correction-ledger.json').read_text())
    assert ledger['used'] == summary['corrections_used'] and ledger['used'] <= 3
    checks = []
    execution_inventory = []
    for folder in sorted((ROOT / 'jobs/560/execution').glob('check-*')):
        result = folder / 'native-result.json'
        if result.exists():
            obj = json.loads(result.read_text())
            checks.append({'attempt': folder.name, 'passed': obj['passed'],
                           'infrastructure_error': obj.get('infrastructure_error'),
                           'commands': [{k: row[k] for k in ['kind', 'operation', 'config', 'targets', 'exit_code', 'timed_out']}
                                        for row in obj['checks']]})
            for index, row in enumerate(obj['checks']):
                if row['kind'] not in ['test', 'doctest']:
                    continue
                bep = folder / f'check-{index}-events.jsonl'
                if not bep.exists():
                    execution_inventory.append({'attempt': folder.name, 'command': index,
                                                 'gap': 'No command-specific BEP'})
                    continue
                target_summaries = []
                for line in bep.open():
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if 'testSummary' not in event:
                        continue
                    label = event['id']['testSummary']['label']
                    detail = {'label': label, 'overallStatus': event['testSummary'].get('overallStatus'),
                              'totalRunCount': event['testSummary'].get('totalRunCount')}
                    log = folder / 'native-testlogs' / label[2:].replace(':', '/') / 'test.log'
                    if log.exists():
                        text = log.read_text(errors='replace')
                        detail['log_sha256'] = digest(log)
                        detail['harness_summary_lines'] = [line.strip() for line in text.splitlines()
                            if re.search(r'test result:|=+ .*\d+ passed|\[  PASSED  \]', line)]
                    target_summaries.append(detail)
                execution_inventory.append({'attempt': folder.name, 'command': index,
                                             'kind': row['kind'], 'bep_sha256': digest(bep),
                                             'target_summaries': target_summaries,
                                             'claim': 'This uncached command only; no aggregation across attempts'})
    runtime = DEST / 'runtime'
    runtime.mkdir()
    for name in ['execution-authority.json', 'incoming-source-binding.json', 'storage-selection.json',
                 'plan-normalization.json', 'guard-host-checks.json', 'linux-tools.json', 'runtime-overlays.json',
                 'server-binding.json', 'docker-binding.json', 'server-shutdown.json', 'docker-shutdown.json',
                 'storage.py', 'tool_guard.py', 'driver_linux.py', 'linux_launcher.py', 'runtime_manager.py',
                 'linux-measurement-binding.json', 'collect_terminal.py', 'finish_review.py',
                 'issue-current.json', 'issue-comments-current.json', 'analyzer-observation.json',
                 'prepare.py', 'admit_start.py', 'submit_queue.py', 'observe_progress.py',
                 'observe_tools.py', 'static-scope-verification.json', 'operator-check-disposition.json']:
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, runtime / name)
    observation = ROOT / 'native-guard-observation-progress.json'
    if observation.exists():
        shutil.copy2(observation, runtime / observation.name)
    observed = ROOT / 'llvm-fetch-observation.json'
    if observed.exists():
        shutil.copy2(observed, runtime / observed.name)
    # Bind native configuration and the actual downloaded compiler/lint binaries.
    workspace = ROOT / 'workspaces/560'
    native_inputs = {name: digest(workspace / name) for name in
                     ['.bazelversion', '.bazelrc', '.clang-tidy', 'MODULE.bazel', 'MODULE.bazel.lock',
                      'quality/static_analysis/static_analysis.bazelrc', 'tools/lint/linters.bzl']}
    binaries = {}
    for external in (ROOT / 'bazel-output').glob('*/external'):
        for pattern in ['toolchains_llvm++llvm+llvm_toolchain_llvm/bin/clang-tidy',
                        'toolchains_llvm++llvm+llvm_toolchain_llvm/bin/clang',
                        'score_toolchains_rust++*/bin/rustc',
                        'score_toolchains_rust++*/bin/clippy-driver']:
            for binary in external.glob(pattern):
                if binary.is_file():
                    binaries[str(binary)] = digest(binary)
    save(DEST / 'native-input-binding.json', {
        'configuration_sha256': native_inputs, 'observed_binary_sha256': binaries,
        'selection_evidence': 'Full native command logs and baseline-resolved MODULE lock',
        'qualification': 'Not supplied by binary presence or passing commands',
    })
    # Keep actual analyzer outputs in addition to command logs; cached files are
    # artifacts only. Command logs determine which aspects were freshly executed.
    analyzer_files = {}
    analyzer_root = ROOT / 'workspaces/560/bazel-bin/score/mw/com'
    if analyzer_root.exists():
        for src in analyzer_root.rglob('*'):
            if src.is_file() and '.AspectRulesLint' in src.name:
                target = DEST / 'analyzer-artifacts' / src.relative_to(analyzer_root)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, target)
                analyzer_files[str(target.relative_to(DEST))] = digest(target)
    save(DEST / 'analyzer-artifact-binding.json', {
        'files': analyzer_files,
        'freshness': 'Inspect native command logs; artifacts alone do not prove execution',
    })
    for name in ['correction-ledger.json', 'prior-check-plan.json', 'carried-prior-check-summary.json',
                 'native-validation-initial-refusal.json']:
        if (ROOT / 'jobs/560' / name).exists():
            shutil.copy2(ROOT / 'jobs/560' / name, runtime / name)
    licenses = DEST / 'licenses/communication'
    licenses.mkdir(parents=True)
    for name in ['LICENSE', 'NOTICE']:
        shutil.copy2(ROOT / 'workspaces/560' / name, licenses / name)
    save(DEST / 'verification-summary.json', {'run_id': run_id, 'issue': 560,
                                             'native_status': projection['lifecycle']['status']['kind'],
                                             'correction_budget': ledger, 'checks': checks,
                                             'supervisor_present': summary['supervisor_present'],
                                             'acceptance': 'pending offline',
                                             'other_issue_budgets': 'Unchanged; never reset exhausted attempts',
                                             'test_evidence': 'Command-specific BEP determines actual executions; copied XML may include prior commands'})
    save(DEST / 'test-execution-inventory.json', {'commands': execution_inventory,
                                                'acceptance': 'pending offline'})
    README = f'''# Rust production subscription-state integration — issue #560

**Measured outcome: native build FAILED** with two E0283 runtime-builder type-inference
errors at `subscription_state_app.rs:118` and `:125`. The five new production integration
cases, existing integration regressions, Clippy and label query were not reached in this run.
All three lifetime source corrections are used; no fourth correction was performed.

Native Fabro run `{run_id}` attempted the five production callback/lifecycle cases on Linux using only DeepSeek
Flash (`deepseek-v4-flash`), with an independent Flash supervisor stage. Native run
status: {projection['lifecycle']['status']['kind']}; this does not establish issue resolution
or engineering acceptance. Written supervisor present: {summary['supervisor_present']}.

Lifetime source corrections used: {ledger['used']}/3; remaining: {ledger['remaining']}.
Historical corrections1/2 and any failed final request remain counted. Other issue budgets
were not changed. The incoming source map matched all 2186 sealed #560 subjects.
The original source baseline, incoming checkpoint, final source map, full patch,
changed native files, workflow/control hashes, events, failed results and raw Linux
logs are retained. Old reports are historical; inspect current corrections/supervisor.

Read `verification-summary.json` and `issues/560/collection-summary.json` for measured
command outcomes and whether subjects match the final patch. Native build, Rust/FFI
unit tests, existing C++ state-machine tests, existing consumer integration and actual
new callback integration are distinct coverage claims. The current expected target
inventory is in `issues/560/export/reports/check-plan.json`; unexecuted checks remain gaps.
Explicit doctest uses Bazel test; inspect the runnable Rust-example denominator.
Explicit-label query does not establish reverse-dependency completeness. The revised
launcher supports the native clang-tidy configuration for the changed C++ wrapper.

Offline engineering review remains pending, including callback ownership/disposal,
reentrancy/thread guarantees, trace and qualification obligations identified in source
and supervisor output. No issue closure, human acceptance, commit or publishing occurred.
Only the new owned Fabro and rootless Docker runtimes were stopped; proofs are exported.
Credentials/private state stayed internal, source/build work used the bound registered
Linux build image on the external SSD, and reference repositories were read-only.
No QNX execution or model fallback was admitted.
'''
    (DEST / 'README.md').write_text(README)
    secrets = [s for s in secrets if s]
    files = {}
    for p in DEST.rglob('*'):
        assert not p.is_symlink(), str(p)
        if p.is_file():
            body = p.read_bytes()
            assert all(s not in body for s in secrets), 'Private secret found; refuse sealing'
            files[str(p.relative_to(DEST))] = hashlib.sha256(body).hexdigest()
    save(DEST / 'artifact-manifest.json', {'schema_version': 1,
                                         'created_at': datetime.now(timezone.utc).isoformat(),
                                         'files': files})
    for name, expected in files.items():
        assert digest(DEST / name) == expected, name
    save(ROOT / 'results-contribution-binding.json', {'path': str(DEST), 'subjects': len(files),
                                                     'manifest_sha256': digest(DEST / 'artifact-manifest.json')})
    print(json.dumps({'packet': str(DEST), 'payloads_verified': len(files),
                      'used': ledger['used'], 'remaining': ledger['remaining'],
                      'native_checks': [(c['attempt'], c['passed']) for c in checks],
                      'supervisor_present': summary['supervisor_present'],
                      'owned_runtimes_stopped': True}))


if __name__ == '__main__':
    main()
