"""Host boundary checks; fixture moves are not native issue readiness evidence."""
import copy
import json
from pathlib import Path

from storage import validate_run_root
import native_relocate
import tool_guard

ROOT = Path(__file__).parent


def main():
    validate_run_root(ROOT)
    control = json.loads((ROOT / 'jobs/781/task.json').read_text())
    workspace = Path(control['workspace'])
    registered = next(k for k in control['native_json_reads'] if k.endswith('/logging.json'))
    base = {'event': 'pre_tool_use', 'node_id': 'draft', 'cwd': str(workspace),
            'tool_name': 'read_file', 'tool_input': {'file_path': registered, 'limit': 200}}
    checks = []
    def guard(name, context, expected):
        actual = tool_guard.allowed(context, '781')
        assert actual is expected, name
        checks.append({'name': name, 'passed': True, 'classification': 'host guard invocation, no live agent'})
    guard('real native registered JSON allowed', base, True)
    for name, path in [('credential escape', '/home/jefferson/.config/sesn/deepseek.env'),
                       ('native git escape', '.git/config'),
                       ('unregistered report JSON', '.rust-queue/reports/raw.json')]:
        context = copy.deepcopy(base); context['tool_input']['file_path'] = path
        guard(name, context, False)
    context = copy.deepcopy(base);context['tool_input']['limit'] = 201
    guard('read ceiling retained', context, False)
    context = copy.deepcopy(base);context['tool_name'] = 'shell';context['tool_input'] = {'command': 'true'}
    guard('general shell still denied', context, False)
    context = copy.deepcopy(base);context['node_id'] = 'supervisor';context['tool_name'] = 'write_file'
    context['tool_input'] = {'file_path': 'score/mw/com/changed.rs', 'content': 'probe'}
    guard('supervisor source write denied', context, False)
    probe = ROOT / 'workspaces/relocation-capability-probe'
    source = probe / 'score/mw/com/a/source.rs'
    source.parent.mkdir(parents=True, exist_ok=False)
    source.write_text('fixture only; no issue source correction\n')
    source.chmod(0o640)
    task = ROOT / 'jobs/0/task.json';task.parent.mkdir(parents=True)
    task.write_text(json.dumps({'workspace': str(probe), 'mode': 'implementation'}))
    sha = native_relocate.digest(source)
    move = {'source': 'score/mw/com/a/source.rs', 'destination': 'score/mw/com/b/source.rs', 'source_sha256': sha}
    def rejected(name, plan):
        try:
            native_relocate.apply('0', plan)
        except ValueError:
            assert source.exists() and native_relocate.digest(source) == sha
            assert not (probe / 'score/mw/com/b/source.rs').exists()
            checks.append({'name': name, 'passed': True, 'classification': 'synthetic boundary fixture'})
        else:
            raise AssertionError(name)
    for name, field, value in [('traversal rejected', 'destination', '../outside.rs'),
                               ('protected git rejected', 'destination', '.git/config'),
                               ('source drift rejected', 'source_sha256', '0' * 64)]:
        item = dict(move);item[field] = value
        rejected(name, {'moves': [item]})
    second = dict(move);second['source'] = 'score/mw/com/missing.rs';second['destination'] = 'score/mw/com/b/second.rs'
    rejected('whole plan validated before first mutation', {'moves': [move, second]})
    (probe / 'score/mw/com/link').symlink_to(ROOT, target_is_directory=True)
    item = dict(move);item['destination'] = 'score/mw/com/link/stolen.rs'
    rejected('symlink escape rejected', {'moves': [item]})
    dry = native_relocate.apply('0', {'moves': [move]}, dry_run=True)
    assert dry['moves'] == 1 and source.exists()
    result = native_relocate.apply('0', {'moves': [move]})
    dest = probe / move['destination']
    assert not source.exists() and native_relocate.digest(dest) == sha and dest.stat().st_mode & 0o777 == 0o640
    checks.append({'name': 'move retains bytes and file permissions', 'passed': True, 'classification': 'synthetic boundary fixture'})
    data = {'passed': True, 'checks': checks, 'relocation': result,
            'limits': 'No paid agent, Fabro relocation stage, real issue move or engineering acceptance tested'}
    (ROOT / 'boundary-checks.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'passed': True, 'checks': len(checks), 'classification': 'host boundary checks; not issue readiness'}))


if __name__ == '__main__':
    main()
