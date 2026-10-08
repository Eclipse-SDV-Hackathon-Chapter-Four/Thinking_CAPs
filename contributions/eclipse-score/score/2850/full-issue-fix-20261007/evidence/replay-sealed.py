"""Check patch application at the bound baseline and the observed newer main."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, '/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root

PACKET = Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/score/2850/full-issue-fix-20261007')
ROOT = Path(json.loads((PACKET/'evidence/workspace.json').read_text())['root'])
validate_run_root(ROOT)
expected = json.loads((PACKET/'source/source-hashes.json').read_text())
results = []
for name, baseline in [('bound', '102aad30bd373295d275722c3942b392a8eb7149'), ('current', '36cdc3f7a56e9651ee51ce91fd183bf3d947dd16')]:
    target = ROOT / f'docs-patch-replay-sealed-{name}'
    subprocess.run(['git', 'clone', '--no-hardlinks', str(ROOT/'docs-as-code'), str(target)], check=True)
    subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/eclipse-score/docs-as-code.git'], cwd=target, check=True)
    if name == 'current':
        subprocess.run(['git', 'fetch', '--depth=1', 'origin', baseline], cwd=target, check=True)
    subprocess.run(['git', 'checkout', '--detach', baseline], cwd=target, check=True)
    subprocess.run(['git', 'apply', '--check', str(PACKET/'source/native.patch')], cwd=target, check=True)
    subprocess.run(['git', 'apply', str(PACKET/'source/native.patch')], cwd=target, check=True)
    subprocess.run(['git', 'diff', '--check'], cwd=target, check=True)
    hashes = {path: hashlib.sha256((target/path).read_bytes()).hexdigest() for path in expected}
    changes = [path for path in expected if hashes[path] != expected[path]]
    if name == 'bound' and changes:
        raise ValueError(f'Replayed source differs: {changes}')
    results.append({'baseline': baseline, 'patch_applied_cleanly': True, 'source_matches_bound_export': not changes, 'different_source_files': changes, 'native_verification_carried_to_new_main': False})
(PACKET/'evidence/patch-replay-sealed-result.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results, indent=2))
