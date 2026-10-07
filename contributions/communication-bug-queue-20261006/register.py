"""Native immutable registration with an explicit title (no paid title call)."""
from pathlib import Path
import hashlib
import json
import urllib.request
from collector import guard

P = Path(__file__).resolve().parent
SERVER = 'http://127.0.0.1:43916'
AUTH = Path('/home/jefferson/.local/state/s-core/fabro/someip84-server/cli-auth.json')

def write(name, value):
    (P / name).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')

def api(route, body=None):
    token = json.loads(AUTH.read_text())['servers'][SERVER]['token']
    headers = {'Authorization': 'Bearer ' + token}
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode()
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(SERVER + route, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)

def main():
    guard()
    if (P / 'native-run-id').exists() or (P / 'run-intent.json').exists():
        raise ValueError('Already registered or attempted; inspect native state before any retry')
    # Wire shape and canonical field order checked against pinned native Rust
    # WorkflowVersion. Files are sorted like its BTreeMap; the server verifies ID.
    version = {'entrypoint': 'workflow.fabro', 'files': {
        str(f.relative_to(P / 'workflow')): f.read_text()
        for f in sorted((P / 'workflow').rglob('*')) if f.is_file()
    }, 'workflow_dependencies': {}}
    canonical = json.dumps(version, ensure_ascii=False, separators=(',', ':')).encode()
    expected_id = hashlib.sha256(canonical).hexdigest()
    (P / 'native-workflow-version.json').write_bytes(canonical)
    registered = api('/api/v1/workflow-versions', version)
    write('workflow-registration.json', registered)
    if registered['workflow_version_id'] != expected_id:
        raise ValueError('Native workflow version ID differs from canonical content hash')
    config = json.loads((P / 'configuration.json').read_text())
    intent = {'workflow_version_id': expected_id, 'target': {'kind': 'folder', 'path': config['scratch_root'] + '/runtime-target'},
              'args': {'model': 'deepseek-flash', 'provider': 'deepseek', 'auto_approve': False,
                       'labels': {'project': 's-core_sw_fabric', 'task': 'communication-bug-queue-20261006', 'budget_usd': '10', 'model_policy': 'flash-only'}},
              'environment_id': 'local', 'title': 'Communication bug queue: 1236, 1031, 751, 1104; Flash only; $10 total'}
    # Persist intent before POST so a lost response cannot silently duplicate it.
    write('run-intent.json', intent)
    created = api('/api/v1/runs', intent)
    write('native-created-run.json', created)
    identifier = created['id']
    (P / 'native-run-id').write_text(identifier + '\n')
    state = json.loads((P / 'state.json').read_text())
    state.update(status='submitted', active_run_id=identifier)
    for item in state['items']:
        item['run_id'] = identifier
    write('state.json', state)
    print(json.dumps({'run_id': identifier, 'workflow_version_id': expected_id, 'status': 'submitted', 'implicit_model_title_call': False}))

if __name__ == '__main__':
    main()
