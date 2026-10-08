"""Create fresh native inputs from verified public subjects, without old outputs."""
import datetime
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path
from score_sw_fabric.storage import validate_run_root

r = Path(__file__).parent
old = r.parent / 'score-fabric-7r64z_kz'
discovery = Path('/tmp/score-rust-linux-integration-x9apk_vo')
validate_run_root(r)
validate_run_root(old)
assert not (r / 'candidate').exists(), 'Preparation is single-use'

def sha(p, algorithm='sha256'):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()

def write(name, value):
    (r / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

for name in ['authority.json', 'upstream-head.json', 'upstream-issue.json', 'upstream-compare.json']:
    shutil.copy2(discovery / name, r / name)
write('allocation-provenance.json', {'initial_metadata_discovery_root': str(discovery), 'initial_selection': json.loads((discovery / 'storage-selection.json').read_text()), 'initial_scope': 'metadata only; no native cache, source, build or run created', 'selected_new_root': str(r), 'reason': 'A fresh selection succeeded after transient blkid timeout; existing bindings were not changed'})
candidate = r / 'candidate'
candidate.mkdir()
hashes = json.loads((old / 'candidate-hashes.json').read_text())
for name, expected in hashes.items():
    src = old / 'candidate' / name
    assert sha(src) == expected, name
    dst = candidate / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
# Exact baseline internal symlink, not a dereferenced source addition.
link = candidate / 'coding-standards.yaml'
link.unlink()
link.symlink_to('quality/static_analysis/coding-standards.yaml')
assert link.resolve().is_relative_to(candidate.resolve())
baseline = json.loads((old / 'baseline-hashes.json').read_text())
head = json.loads((r / 'upstream-head.json').read_text())['sha']
changes = json.loads((r / 'upstream-compare.json').read_text())
assert changes['status'] == 'ahead'
assert len(changes['files']) == 3
updates = []
for item in changes['files']:
    name = item['filename']
    assert item['status'] == 'modified' and name in baseline
    req = urllib.request.Request(f'https://raw.githubusercontent.com/eclipse-score/communication/{head}/{name}', headers={'User-Agent': 'score-rust-linux-verification'})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == item['sha'], name
    (candidate / name).write_bytes(raw)
    hashes[name] = baseline[name] = hashlib.sha256(raw).hexdigest()
    updates.append({'path': name, 'Git_blob_sha1': blob, 'sha256': hashes[name]})
write('baseline-hashes.json', baseline)
write('candidate-hashes.json', hashes)
write('source-provenance.json', {'selected_baseline': head, 'original_baseline': 'e3d126c2d7569345cf5f790310702eb00cd86b06', 'candidate_files': len(hashes), 'baseline_files': len(baseline), 'updates': updates, 'patch_only_changes': ['score/mw/com/rust/README.md', 'score/mw/com/rust/design/identifier_pasting_assessment.md'], 'symlink': {'coding-standards.yaml': 'quality/static_analysis/coding-standards.yaml'}, 'hooks': 'archive subjects only; no .git or hooks imported', 'imported_old_build_outputs': False})
(r / 'tools').mkdir()
shutil.copy2(old / 'tools/bazel', r / 'tools/bazel')
shutil.copytree(old / 'runtime-libs', r / 'runtime-libs')
shutil.copytree(old / 'runtime-provenance', r / 'runtime-provenance')
overlays = json.loads((old / 'runtime-overlays.json').read_text())
for item in overlays['overlays']:
    item['source'] = str(r / 'runtime-libs' / Path(item['source']).name)
    assert sha(Path(item['source'])) == item['source_sha256']
    assert sha(Path(item['target'])) == item['host_original_sha256']
    assert Path(item['source']).stat().st_mode & 0o7777 == item['mode']
write('runtime-overlays.json', overlays)
cache_rows = json.loads((old / 'cache-import.json').read_text())['inputs']
imported = []
for item in cache_rows:
    algorithm = item['hash_algorithm']
    expected = item['digest']
    relative = Path('content_addressable') / algorithm / expected
    src = old / 'repository-cache' / relative / 'file'
    assert sha(src, algorithm) == expected
    assert src.stat().st_size == item['bytes']
    dest = r / 'repository-cache' / relative
    dest.mkdir(parents=True)
    shutil.copy2(src, dest / 'file')
    for marker in item['markers']:
        assert marker.startswith('id-') and '/' not in marker
        src_marker = src.parent / marker
        assert src_marker.is_file() and src_marker.stat().st_size == 0
        shutil.copy2(src_marker, dest / marker)
    imported.append(item)
write('cache-import.json', {'scope': 'Verified immutable public download payloads and exact empty canonical-ID markers; no queue, credentials, private state or native build outputs', 'inputs': imported})
out = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265/linux-integration') / r.name
out.mkdir(parents=True)
write('contribution.json', {'path': str(out)})
write('correction-ledger.json', {'authority': 'User requests Linux integration tests after exhausted historical recovery', 'max_corrections': 3, 'corrections_used': 0, 'entries': [], 'supervisor': '/root/rust_issue_supervisor', 'status': 'prepared'})
write('preparation-result.json', {'completed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'selected_baseline': head, 'candidate_files': len(hashes), 'public_cache_payloads': len(imported), 'public_cache_bytes': sum(x['bytes'] for x in imported)})
validate_run_root(r)
print(json.dumps({'root': str(r), 'selected_baseline': head, 'candidate_files': len(hashes), 'cache_payloads': len(imported)}))
