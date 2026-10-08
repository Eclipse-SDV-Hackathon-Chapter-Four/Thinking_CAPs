"""Submit one native start request per existing run; Fabro owns scheduling."""
import json
import urllib.request
from pathlib import Path
from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).parent
validate_run_root(ROOT)
queue = json.loads((ROOT / 'queue.json').read_text())
assert queue['status'] in ['ready_to_start_linux_revision', 'linux_execution_requested']
binding = json.loads((ROOT / 'server-binding.json').read_text())
token = json.loads((Path(binding['private_state']) / 'operator-secret.json').read_text())['token']


def request(method, path, body=None):
    req = urllib.request.Request(binding['url'] + path,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 method=method,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


for job in sorted(queue['jobs'], key=lambda j: j['submission_order']):
    validate_run_root(ROOT)
    folder = Path(job['job_root'])
    observed = request('GET', '/api/v1/runs/' + job['run_id'])
    save(folder / 'native-run-projection.json', observed)
    if (folder / 'start-response.json').exists():
        assert observed['lifecycle']['status']['kind'] != 'submitted'
        continue
    assert not (folder / 'start-intent.json').exists(), 'Reconcile any ambiguous prior request before retry'
    assert observed['lifecycle']['status']['kind'] == 'submitted'
    save(folder / 'start-intent.json', {'run_id': job['run_id'], 'request_sent_once': True,
                                      'authority': 'user go', 'resume': False})
    response = request('POST', '/api/v1/runs/' + job['run_id'] + '/start', {})
    save(folder / 'start-response.json', response)
    job.update(start_requested=True, status=response['lifecycle']['status']['kind'])
    queue.update(status='linux_execution_requested', issue_start_requests=sum(bool(j.get('start_requested')) for j in queue['jobs']))
    save(ROOT / 'queue.json', queue)
    print(json.dumps({'issue': job['issue'], 'run_id': job['run_id'], 'native_state': job['status']}), flush=True)

save(ROOT / 'native-runs-after-start.json', request('GET', '/api/v1/runs'))
