"""Seal all completed Codex attempts and shut down only the owned runtimes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import time
import xml.etree.ElementTree as ET
from storage import validate_run_root

ROOT = Path(__file__).parent
DEST = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue') / (ROOT.name + '-results')
PYTHON = '/home/jefferson/s-core_sw_fabric/.venv/bin/python'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')

def main():
    validate_run_root(ROOT)
    assert not DEST.exists(), 'Never overwrite an exported packet'
    ledger = json.loads((ROOT / 'correction-ledger.json').read_bytes())
    n = ledger['codex_used']
    assert 1 <= n <= 3
    summary = json.loads((ROOT / f'attempt-{n}/summary.json').read_bytes())
    assert summary['passed'] or n == 3, 'Do not silently stop a failed attempt with corrections available'
    assert (ROOT / f'reports/codex-supervisor-final.md').is_file()
    binding = json.loads((ROOT / 'server-binding.json').read_bytes())
    private = Path(binding['private_state'])
    secrets = [json.loads((private / 'operator-secret.json').read_bytes())['token'].encode()]
    for line in Path('/home/jefferson/.config/sesn/deepseek.env').read_text().splitlines():
        for part in shlex.split(line, comments=True):
            if part.startswith('DEEPSEEK_API_KEY='):
                secrets.append(part.partition('=')[2].encode())
    pid = binding['pid']; proc = Path('/proc') / str(pid)
    environ = (proc / 'environ').read_bytes().split(b'\0')
    assert ('FABRO_HOME=' + str(private)).encode() in environ
    assert sha(proc / 'exe') == binding['fabro_sha256'] and os.getpgid(pid) == pid
    for entry in environ:
        if entry.startswith(b'SESSION_SECRET='):
            secrets.append(entry.partition(b'=')[2])
    runtimes = list((ROOT / 'native-runtime').iterdir())
    for runtime in runtimes:
        projection = json.loads((runtime / 'final-projection.json').read_bytes())
        assert projection['lifecycle']['status']['kind'] in ['succeeded', 'failed', 'dead', 'cancelled']
        assert json.loads((runtime / 'event-collection.json').read_bytes())['terminal_lifecycle_present']
    os.killpg(pid, signal.SIGTERM)
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        try:
            if (proc / 'stat').read_text().split(') ', 1)[1].split()[0] == 'Z':
                break
        except FileNotFoundError:
            break
        time.sleep(.2)
    members = []
    for process in Path('/proc').iterdir():
        if not process.name.isdigit():
            continue
        try:
            if os.getpgid(int(process.name)) == pid and (process / 'stat').read_text().split(') ', 1)[1].split()[0] != 'Z':
                members.append(int(process.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    assert not members, 'Owned Fabro group did not stop; inspect, do not signal unrelated PIDs'
    save(ROOT / 'server-shutdown.json', {'owned_server_stopped': True, 'pid': pid,
                                       'owned_group_running_members': members, 'global_servers_modified': False})
    subprocess.run([PYTHON, str(ROOT / 'runtime_manager.py'), 'stop'], check=True, capture_output=True)
    DEST.mkdir()
    def copy_file(source, dest):
        assert not source.is_symlink(), str(source)
        # Stream secret scanning keeps large raw evidence outside model context/memory.
        carry = b''
        with source.open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                data = carry + chunk
                assert not any(s and s in data for s in secrets), 'Credential in export; refuse sealing'
                carry = data[-max(map(len, secrets)):]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in ['.py', '.json']:
            copy_file(path, DEST / 'runtime' / path.name)
    for name in ['definitions', 'jobs', 'reports', 'native-runtime', 'analyzer-evidence']:
        for path in (ROOT / name).rglob('*'):
            if path.is_file():
                copy_file(path, DEST / name / path.relative_to(ROOT / name))
    for attempt in range(1, n + 1):
        source = ROOT / f'attempt-{attempt}'
        for path in source.rglob('*'):
            if path.is_file():
                copy_file(path, DEST / source.name / path.relative_to(source))
    original = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/rust-api-queue/score-rust-560-integration-5sejq8fk-results')
    original_manifest = original / 'artifact-manifest.json'
    assert sha(original_manifest) == '479e54a9ca827336018a207ade8c7673fea6ff9beb0c3e81b6b994a03c018f85'
    old_files = json.loads(original_manifest.read_bytes())['files']
    for rel, digest in old_files.items():
        assert sha(original / rel) == digest, rel
        prefix = 'issues/560/changed-source/'
        if rel.startswith(prefix):
            copy_file(ROOT / 'workspaces/560' / rel[len(prefix):], DEST / 'changed-source' / rel[len(prefix):])
    copy_file(original_manifest, DEST / 'carried/primary-artifact-manifest.json')
    work = ROOT / 'workspaces/560'
    for rel, digest in json.loads((ROOT / 'native-config-binding.json').read_bytes())['files'].items():
        assert sha(work / rel) == digest, rel
        copy_file(work / rel, DEST / 'native-context' / rel)
    tool_rows = []
    for folder in (ROOT / 'bazel-output').glob('*/external/score_toolchains_rust++*'):
        for name in ['rustc', 'clippy-driver']:
            for path in folder.glob('bin/' + name):
                tool_rows.append({'path': str(path), 'sha256': sha(path), 'qualification': 'pending'})
    save(DEST / 'compiler-identities.json', tool_rows)
    checks = []
    for attempt in range(1, n + 1):
        native = ROOT / f'attempt-{attempt}/native'
        result = json.loads((native / 'native-result.json').read_bytes())
        groups = []
        for idx,row in enumerate(result['checks']):
            group = {k: row[k] for k in ['kind', 'operation', 'targets', 'config', 'exit_code', 'timed_out', 'elapsed_seconds']}
            group['target_summaries'] = []
            bep = native / f'check-{idx}-events.jsonl'
            if bep.exists():
                for line in bep.open():
                    event = json.loads(line)
                    if 'testSummary' in event:
                        group['target_summaries'].append({'label': event['id']['testSummary']['label'], **event['testSummary']})
            group['xml_cases'] = []
            for rec in row.get('test_records', []):
                xml = Path(rec['path'])
                assert sha(xml) == rec['sha256']
                group['xml_cases'].append({'path': str(xml.relative_to(ROOT)), 'suites': rec['suites'],
                    'listed_command_target': any(str(xml).endswith('/' + label[2:].replace(':', '/') + '/test.xml')
                                                 for label in row['targets']),
                    'case_names': [node.attrib.get('name') for node in ET.parse(xml).getroot().iter('testcase')]})
            groups.append(group)
        checks.append({'codex_attempt': attempt, 'passed': result['passed'], 'checks': groups})
    save(DEST / 'verification-summary.json', {'attempts': checks, 'latest_passed': summary['passed'],
         'historical_corrections_used': 3, 'codex_corrections_used': n, 'codex_remaining': 3 - n,
         'native_agent_nodes': 0, 'source_editor': 'Codex', 'binary_clippy_warnings': ['dead_code', 'clippy::manual_is_multiple_of'],
         'test_code_clippy': 'not measured', 'qualification': 'pending', 'acceptance': 'pending_offline'})
    status = 'PASSED' if summary['passed'] else 'FAILED — correction limit reached'
    (DEST / 'README.md').write_text('# #560 Codex corrections and native Linux verification\n\n'
        '**Latest measured outcome: ' + status + '.** Inspect verification-summary.json for actual target and case results. '
        'Fabro lifecycle success means execution/export ended, not engineering acceptance.\n\n'
        f'Codex used {n}/3 newly authorized source correction attempts ({3+n} lifetime attempts including three historical attempts). '
        'The original queue budgets and immutable contributions remain unchanged.\n\n'
        'Codex corrected the explicit runtime builder types and provider termination ownership/status handling. '
        'Three scripted subprocess tests cover helper cleanup separately from the five real LoLa integration scenarios. '
        'Fabro executed command-only verification/export graphs; no runtime LLM agent stage or DeepSeek model call was requested. '
        'An independent Codex supervisor report is under reports/codex-supervisor-final.md.\n\n'
        'Clippy executed the actual native binary aspect and returned success with two retained warnings '
        '(unread Observation.invocation and manual_is_multiple_of). Test-code Clippy was not executed. '
        'Analyzer success is not a warning-free or qualification claim.\n\n'
        'Full native commands, environments, raw logs, BEP, XML, all attempt failures, source vectors, full patch, source files, '
        'control/storage/tool identities and native events are preserved. Prior library/test measurements remain carried evidence, '
        'not fresh tests of this correction. Qualification, applicability, downstream/concurrency coverage and offline human '
        'engineering acceptance remain pending. No publishing, issue closure or safety qualification occurred.\n\n'
        'Owned private Fabro and rootless Docker services stopped; shutdown proofs are under runtime/. '
        'Original services/reference repositories/global caches and user work were preserved.\n')
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'files': {
        str(path.relative_to(DEST)): sha(path) for path in sorted(DEST.rglob('*')) if path.is_file()}}
    save(DEST / 'artifact-manifest.json', manifest)
    for rel, digest in manifest['files'].items():
        assert sha(DEST / rel) == digest, rel
    print(json.dumps({'contribution': str(DEST), 'payloads_verified': len(manifest['files']),
                     'manifest_sha256': sha(DEST / 'artifact-manifest.json'), 'native_passed': summary['passed'],
                     'codex_used': n, 'owned_runtimes_stopped': True}))

if __name__ == '__main__':
    main()
