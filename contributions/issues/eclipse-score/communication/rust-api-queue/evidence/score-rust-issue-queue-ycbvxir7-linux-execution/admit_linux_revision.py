"""One-time native queue revision admission; preserves every original record."""
import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).parent
validate_run_root(ROOT)
binding = json.loads((ROOT / 'server-binding.json').read_text())
private = Path(binding['private_state'])
token = json.loads((private / 'operator-secret.json').read_text())['token']


def request(method, path, body=None):
    req = urllib.request.Request(binding['url'] + path,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 method=method,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


queue = json.loads((ROOT / 'queue.json').read_text())
assert queue['status'] == 'submitted_not_started' and not (ROOT / 'queue-before-linux-revision.json').exists()
save(ROOT / 'queue-before-linux-revision.json', queue)

# Finish and retain all concrete packages before replacing any native run.
for job in queue['jobs']:
    validate_run_root(ROOT)
    folder = ROOT / 'definitions-linux' / str(job['issue'])
    package = json.loads((folder / 'workflow-version.json').read_text())
    registered = request('POST', '/api/v1/workflow-versions', package)
    save(folder / 'workflow-registration.json', registered)

for job in sorted(queue['jobs'], key=lambda j: j['submission_order']):
    validate_run_root(ROOT)
    folder = Path(job['job_root'])
    revision = ROOT / 'definitions-linux' / str(job['issue'])
    original_id = job['run_id']
    original = request('GET', '/api/v1/runs/' + original_id)
    assert original['lifecycle']['status']['kind'] == 'submitted' and original['timestamps']['started_at'] is None
    original_folder = ROOT / 'original-jobs' / str(job['issue'])
    original_folder.parent.mkdir(exist_ok=True)
    shutil.copytree(folder, original_folder)
    save(original_folder / 'native-cancel-response.json', request('POST', '/api/v1/runs/' + original_id + '/cancel', {}))
    save(original_folder / 'native-archive-response.json', request('POST', '/api/v1/runs/' + original_id + '/archive', {}))
    for name in ['workflow-version.json', 'workflow.fabro', 'workflow.toml', 'workflow-registration.json', 'task.json', 'native-validation.json']:
        shutil.copy2(revision / name, folder / name)
    shutil.copy2(revision / 'task.json', Path(job['workspace']) / '.rust-queue/context/task.json')
    original_intent = json.loads((original_folder / 'create-intent.json').read_text())['intent']
    original_intent['workflow_version_id'] = json.loads((revision / 'workflow-registration.json').read_text())['workflow_version_id']
    original_intent['args']['labels'].update(runtime_revision='linux_native', supersedes_unstarted_run=original_id)
    save(folder / 'create-intent.json', {'state': 'linux_revision_create_sent_once', 'intent': original_intent, 'start': False})
    created = request('POST', '/api/v1/runs', original_intent)
    save(folder / 'run-created.json', created)
    run_id = created['id']
    state = request('GET', '/api/v1/runs/' + run_id + '/state')
    save(folder / 'native-state.json', state)
    assert state['spec']['settings']['run']['clone']['enabled'] is False
    model = state['spec']['settings']['run']['model']
    assert model['name'] == 'deepseek-flash' and model['provider'] == 'deepseek' and model['fallbacks'] == {}
    # The native host driver canonicalizes this prospective managed path.
    # Its private registry and records remain internal; source/build work is SSD-bound.
    scratch = private / 'storage/scratch' / ('20261006-' + run_id) / 'petri'
    work = scratch / 'scopes/invocation-0-scope-0/work'
    assert not work.exists()
    work.parent.mkdir(parents=True)
    work.symlink_to(job['workspace'], target_is_directory=True)
    repository = scratch / 'snapshots/invocation-0-scope-0.git'
    repository.parent.mkdir()
    subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'init', '--bare', str(repository)], capture_output=True, check=True)
    subprocess.run(['git', '--git-dir', str(repository), 'config', 'receive.shallowUpdate', 'true'], check=True)
    save(folder / 'native-workspace-binding.json', {'run_id': run_id, 'baseline': queue['baseline'], 'native_path': str(work), 'workspace': job['workspace'], 'snapshot_repository': str(repository), 'snapshot_receive_shallow_update': True, 'clone_enabled': False, 'running_queue_migrated': False})
    job.update(run_id=run_id, original_unstarted_run_id=original_id,
               workflow_version_id=original_intent['workflow_version_id'], runtime_revision='linux_native')
    save(folder / 'native-run-projection.json', request('GET', '/api/v1/runs/' + run_id))
    save(ROOT / 'queue.json', queue)
    print(json.dumps({'issue': job['issue'], 'active_run_id': run_id, 'original_preserved_cancelled_archived': original_id}), flush=True)

queue.update(status='linux_revision_submitted_not_started', original_unstarted_runs_preserved=13,
             native_execution_ready=False, issue_start_requests=0,
             model_calls_requested=None, qualification_agent_stage='Flash native hook probe succeeded; exact request count not aggregated',
             launch_prerequisites=['Wait for fresh native Linux launcher readiness checks'])
save(ROOT / 'queue.json', queue)
