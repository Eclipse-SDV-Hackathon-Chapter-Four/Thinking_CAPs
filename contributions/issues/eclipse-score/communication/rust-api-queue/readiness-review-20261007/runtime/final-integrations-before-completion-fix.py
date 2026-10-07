import hashlib
import json
from pathlib import Path
import subprocess
import time

root = Path(Path('/tmp/thinking-caps-communication-review-root').read_text().strip())
packet = Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/rust-api-queue/readiness-review-20261007')

def wait_for(name):
    path = root / name / 'native-result.json'
    while not path.exists():
        time.sleep(1)
    return json.loads(path.read_text())

for issue in ['1261', '560']:
    wait_for(f'execution-{issue}-final-selected')
    workspace = root / 'workspaces' / issue
    build = workspace / 'BUILD'
    original = build.read_bytes()
    modified = original.replace(b'"//:BUILD",', b'"BUILD",').replace(b'"//:MODULE.bazel",', b'"MODULE.bazel",')
    assert original != modified
    binding = {'issue': issue, 'scope': 'candidate plus separate diagnostic checker-path correction; not candidate-only native validation',
               'candidate_source_manifest': f'subjects-{issue}.json',
               'candidate_source_manifest_sha256': hashlib.sha256((packet / f'subjects-{issue}.json').read_bytes()).hexdigest(),
               'original_BUILD_sha256': hashlib.sha256(original).hexdigest(),
               'diagnostic_BUILD_sha256': hashlib.sha256(modified).hexdigest(),
               'companion_patch_sha256': hashlib.sha256((packet / 'copyright-checker-path-companion.patch').read_bytes()).hexdigest()}
    (packet / f'copyright-diagnostic-{issue}-binding.json').write_text(json.dumps(binding, indent=2) + '\n')
    plan = root / f'plan-{issue}-copyright-diagnostic.json'
    plan.write_text((root / 'plan-1261-copyright.json').read_text())
    build.write_bytes(modified)
    try:
        result = subprocess.run(['python3', str(root / 'supplementary_launcher.py'), '--workspace', str(workspace),
                                 '--plan', str(plan), '--output', str(root / f'execution-{issue}-copyright-diagnostic')])
        print('copyright diagnostic', issue, result.returncode, flush=True)
    finally:
        build.write_bytes(original)
        assert hashlib.sha256(build.read_bytes()).hexdigest() == binding['original_BUILD_sha256']

outcomes = []
for issue in ['1261', '560']:
    result = subprocess.run(['python3', str(root / 'linux_launcher.py'), '--workspace', str(root / 'workspaces' / issue),
                             '--plan', str(root / f'plan-{issue}-serial-itf.json'),
                             '--output', str(root / f'execution-{issue}-final-serial-itf')])
    outcomes.append({'issue': issue, 'exit_code': result.returncode})
    print('final sequential integration', issue, result.returncode, flush=True)
(root / 'final-integration-sequence.json').write_text(json.dumps(outcomes, indent=2) + '\n')
raise SystemExit(int(any(x['exit_code'] for x in outcomes)))
