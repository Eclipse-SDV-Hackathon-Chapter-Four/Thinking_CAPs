from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request

SOURCE = Path('/home/jefferson/s-core_bot')
ROOT = Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/score/2850')
EVIDENCE = ROOT / 'evidence'
def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + '\n')
def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args], text=True).strip()
commit = git('rev-parse', 'HEAD')
assert not git('status', '--porcelain'), 'Source must remain clean'
archive = EVIDENCE / 'source' / 's-core-bot-source.tar.gz'
archive.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(['git', '-C', str(SOURCE), 'archive', '--format=tar.gz', '--output', str(archive), commit], check=True)
scratch = Path(tempfile.mkdtemp(prefix='score-chatbot-2850-'))
with tarfile.open(archive) as tf:
    tf.extractall(scratch, filter='data')
source_files = {p.relative_to(scratch).as_posix(): sha(p) for p in sorted(scratch.rglob('*')) if p.is_file()}
write(EVIDENCE / 'source' / 'source-manifest.json', {'commit': commit, 'archive_sha256': sha(archive), 'files': source_files})
for relative in source_files:
    if relative.startswith(('docs/', 'specs/')) or relative in ('README.md', 'LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md', 'AGENTS.md', 'CLAUDE.md', '.specify/memory/constitution.md', 'config/sources.yaml', 'config/local.yaml', 'pyproject.toml', 'uv.lock', 'frontend/package.json', 'frontend/package-lock.json', '.github/workflows/ci.yml'):
        target = EVIDENCE / 'project' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(scratch / relative, target)
historical = SOURCE / 'data/releases/1.0.0-20260930T051024Z'
release_manifest = json.loads((historical / 'release-manifest.json').read_text())
for item in release_manifest['items']:
    assert sha(historical / item['path']) == item['sha256'], item['path']
for p in historical.rglob('*'):
    if p.is_file():
        target = EVIDENCE / 'historical/local-release-1.0.0' / p.relative_to(historical)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert sha(target) == sha(p)
        else:
            shutil.copy2(p, target)
report = json.loads((SOURCE / 'data/reports/release-20260930T051004Z/report.json').read_text())
selected = {'release-20260930T051004Z/report.json'}
for gate in report['gates']:
    for p in (gate.get('evidence_file') or '').split(', '):
        if p and (SOURCE / 'data/reports' / p).is_file():
            selected.add(p)
selected.update({'suite-heldout-20260929T170034Z-run1.json', 'suite-heldout-20260929T170034Z-run2.json', 'suite-heldout-20260929T170034Z-run3.json', 'suite-heldout-20260929T170034Z-review.yaml', 'sbom-20260930T050619Z.cdx.json', 'contract-native-20260929T172133Z.json', 'contract-container-20260929T172133Z.json', 'browser-20260929T171545Z.json', 'license-generation-d18a5cc71b84.txt', 'license-embedding-c71d239df917.txt'})
carried = []
for relative in sorted(selected):
    p = SOURCE / 'data/reports' / relative
    if p.is_file():
        target = EVIDENCE / 'historical/reports' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        carried.append({'source': str(p), 'destination': target.relative_to(ROOT).as_posix(), 'sha256': sha(target), 'size_bytes': target.stat().st_size})
write(EVIDENCE / 'historical/provenance.json', {'captured_at': now(), 'category': 'carried historical evidence, not rerun', 'source_release_tag_commit': git('rev-parse', 'v1.0.0^{}'), 'subject_binding_limit': 'Reports identify corpus/model/snapshot; no independently complete source-commit binding for every old run. Never attribute these results to current HEAD.', 'original_release_manifest_verified': True, 'files': carried})
write(EVIDENCE / 'source/provenance.json', {'captured_at': now(), 'source_repository': 'https://github.com/jnsagai/s-core_bot', 'source_path': str(SOURCE), 'commit': commit, 'status_porcelain': git('status', '--porcelain'), 'tag_v1_0_0_commit': git('rev-parse', 'v1.0.0^{}'), 'thinking_caps_base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'scratch_copy': str(scratch), 'storage': 'Temporary internal filesystem; documentation assessment, no upstream native build', 'archive_sha256': sha(archive), 'archive_bytes': archive.stat().st_size, 'excluded': ['untracked/runtime data', 'model weights', 'corpus source files/bundles', 'credentials', 'virtual environments', 'node_modules', 'unrelated user files'], 'linux': platform.platform()})
for filename in ['CONTRIBUTION.md', '.github/PULL_REQUEST_TEMPLATE/improvement.md', '.github/ISSUE_TEMPLATE/improvement.md', '.github/CODEOWNERS', 'LICENSE', 'NOTICE']:
    try:
        req = urllib.request.Request('https://raw.githubusercontent.com/eclipse-score/score/main/' + filename, headers={'User-Agent': 'Thinking-CAPs-evidence'})
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
        target = EVIDENCE / 'upstream/guidance' / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    except Exception as exc:
        write(EVIDENCE / 'upstream/guidance' / (Path(filename).name + '.unavailable.json'), {'url': req.full_url, 'error': str(exc), 'retrieved_at': now()})
(scratch / 'frontend/node_modules').symlink_to(SOURCE / 'frontend/node_modules', target_is_directory=True)
env = dict(os.environ)
env['PYTHONPATH'] = str(scratch / 'src')
env['PATH'] = str(SOURCE / '.venv/bin') + os.pathsep + env['PATH']
env.pop('SCORE_ASSISTANT_REAL_RUNTIME', None)
env.pop('SCORE_ASSISTANT_REAL_NETWORK', None)
for key in list(env):
    if key.startswith('SCORE_ASSISTANT_'):
        env.pop(key)
checks = EVIDENCE / 'checks'
checks.mkdir(parents=True, exist_ok=True)
records = []
def run(name, args, cwd=scratch):
    start = now()
    t = time.monotonic()
    log = checks / (name + '.log')
    with log.open('w') as stream:
        proc = subprocess.run(args, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
    records.append({'name': name, 'argv': args, 'cwd': str(cwd), 'started_at': start, 'completed_at': now(), 'elapsed_seconds': round(time.monotonic() - t, 3), 'exit_code': proc.returncode, 'log': log.relative_to(ROOT).as_posix(), 'log_sha256': sha(log), 'source_commit': commit, 'archive_sha256': sha(archive)})
    write(checks / 'commands.json', {'category': 'fresh local execution on isolated source archive', 'environment_overrides': {'PYTHONPATH': str(scratch / 'src'), 'PATH_prefix': str(SOURCE / '.venv/bin'), 'SCORE_ASSISTANT_*': 'removed; real runtime/network opt-in disabled'}, 'dependency_environment': 'Existing project virtualenv and frontend node_modules reused; no install/update. Source imports forced to archive copy.', 'checks': records})
    print(name, proc.returncode, log.read_text()[-600:], flush=True)
run('python-version', ['python', '--version'])
run('tool-versions', ['python', '-c', 'from importlib.metadata import version; import json; print(json.dumps({p:version(p) for p in ["pytest","ruff","mypy","fastapi","numpy","httpx","docutils"]},indent=2))'])
run('python-environment', ['uv', 'pip', 'freeze', '--python', str(SOURCE / '.venv/bin/python')])
run('ruff-format', ['ruff', 'format', '--check', '.'])
run('ruff-lint', ['ruff', 'check', '.'])
run('mypy', ['mypy', 'src'])
run('traceability', ['python', 'scripts/check_traceability.py'])
run('licenses', ['python', 'scripts/check_licenses.py'])
run('node-version', ['node', '--version'])
run('npm-version', ['npm', '--version'])
for name, args in [('frontend-lint', ['npm','run','lint']), ('frontend-typecheck', ['npm','run','typecheck']), ('frontend-tests', ['npm','test','--','--reporter=junit','--outputFile='+str(checks/'vitest.xml')]), ('frontend-build', ['npm','run','build']), ('frontend-assets', ['npm','run','check-no-third-party-assets']), ('frontend-telemetry', ['npm','run','check-no-telemetry'])]:
    run(name, args, scratch / 'frontend')
run('pytest', ['python', '-m', 'pytest', '-q', '-ra', '--junitxml='+str(checks/'pytest.xml')])
write(checks / 'source-after.json', {'original_status_porcelain': git('status','--porcelain'), 'checked_files': len(source_files), 'changed_tracked_inputs_in_scratch': [p for p,h in source_files.items() if sha(scratch/p) != h]})
print('FINISHED', str(scratch), flush=True)
