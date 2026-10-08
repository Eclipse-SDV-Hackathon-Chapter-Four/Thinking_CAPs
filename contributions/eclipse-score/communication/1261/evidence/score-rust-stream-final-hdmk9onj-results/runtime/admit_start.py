"""Single native admission/start; no loop, scheduler or model request."""
from pathlib import Path
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).parent
validate_run_root(ROOT)
binding = json.loads((ROOT / 'server-binding.json').read_bytes())
private = Path(binding['private_state'])
token = json.loads((private / 'operator-secret.json').read_bytes())['token']
queue = json.loads((ROOT / 'queue.json').read_bytes())
job = queue['jobs'][0]
job_root = Path(job['job_root'])
rid = job['run_id']
def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
def request(method, path, body=None):
    req = urllib.request.Request(binding['url'] + '/api/v1' + path, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as stream:
        return json.load(stream)
observed = request('GET', '/runs/' + rid)
assert observed['lifecycle']['status']['kind'] == 'submitted'
assert not (job_root / 'start-intent.json').exists()
date = observed['timestamps']['created_at'][:10].replace('-', '')
scope = private / 'storage/scratch' / (date + '-' + rid) / 'petri'
work = scope / 'scopes/invocation-0-scope-0/work'
work.parent.mkdir(parents=True, exist_ok=True)
assert not work.exists() and not work.is_symlink()
work.symlink_to(ROOT / 'workspaces/1261', target_is_directory=True)
snapshot = scope / 'snapshots/invocation-0-scope-0.git'
snapshot.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'init', '--bare', str(snapshot)], check=True, capture_output=True)
for key,value in [('receive.shallowUpdate', 'true'), ('core.hooksPath', '/dev/null')]:
    subprocess.run(['git', '--git-dir', str(snapshot), 'config', key, value], check=True)
save(job_root / 'native-workspace-binding.json', {'run_id': rid, 'native_path': str(work),
     'workspace': str(ROOT / 'workspaces/1261'), 'snapshot_repository': str(snapshot),
     'running_queue_migrated': False, 'clone_enabled': False})
save(job_root / 'start-intent.json', {'authority': 'User resumes supervised DeepSeek Flash issue queue; discovery implementation with original issue1261 source-correction budget 2/3 before this final source attempt',
     'run_id': rid, 'request_sent_once': True, 'recorded_at': datetime.now(timezone.utc).isoformat()})
save(job_root / 'start-response.json', request('POST', '/runs/' + rid + '/start', {}))
queue.update(status='native_verification_requested', start_requests=1, model_calls_requested=2)
save(ROOT / 'queue.json', queue)
print(json.dumps({'run_id': rid, 'start_requested_once': True, 'agent_nodes': 2}))
