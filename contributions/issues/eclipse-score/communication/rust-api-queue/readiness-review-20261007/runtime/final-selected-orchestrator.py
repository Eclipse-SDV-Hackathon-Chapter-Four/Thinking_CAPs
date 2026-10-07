import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

root = Path('/tmp/thinking-caps-communication-review-root').read_text().strip()
root = Path(root)
packet = Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/rust-api-queue/readiness-review-20261007')
issue = sys.argv[1]

def wait_for(name):
    path = root / name / 'native-result.json'
    while not path.exists():
        time.sleep(1)
    return json.loads(path.read_text())

def run(plan, output):
    return subprocess.run(['python3', str(root / 'supplementary_launcher.py'),
                           '--workspace', str(root / 'workspaces' / issue),
                           '--plan', str(root / plan), '--output', str(root / output)]).returncode

if issue == '1261':
    applied = wait_for('execution-1261-format-apply')
    if not applied['passed']:
        raise SystemExit('Native formatting apply failed')
else:
    wait_for('execution-560-serial-itf')
    if run('plan-560-format-apply.json', 'execution-560-format-apply'):
        raise SystemExit('Native formatting apply failed')

workspace = root / 'workspaces' / issue
subjects = json.loads((packet / f'subjects-{issue}.json').read_text())
for relative in subjects:
    subjects[relative] = hashlib.sha256((workspace / relative).read_bytes()).hexdigest()
encoded = json.dumps(subjects, indent=2, sort_keys=True) + '\n'
(packet / f'subjects-{issue}.json').write_text(encoded)
(root / f'subjects-{issue}.json').write_text(encoded)
patch = subprocess.check_output(['git', 'diff', '--binary', '381d43dec900ab6a9076f3f30e7bfbdee019e26e'], cwd=workspace)
(packet / f'communication-{issue}-candidate.patch').write_bytes(patch)
print(json.dumps({'issue': issue, 'final_source_manifest_sha256': hashlib.sha256(encoded.encode()).hexdigest(), 'candidate_patch_sha256': hashlib.sha256(patch).hexdigest()}), flush=True)
raise SystemExit(run(f'plan-{issue}-final-selected.json', f'execution-{issue}-final-selected'))
