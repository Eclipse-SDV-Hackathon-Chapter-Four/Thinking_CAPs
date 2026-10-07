"""Host pre-tool guard: file-only source drafting inside each disposable target."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from storage import validate_run_root


def allowed(context: dict, number: str) -> bool:
    validate_run_root(ROOT)
    control = json.loads((ROOT / 'jobs' / number / 'task.json').read_text())
    workspace = Path(control['workspace']).resolve()
    if context.get('event') == 'stage_start':
        return Path(context.get('cwd', '/')).resolve().is_relative_to(workspace)
    if context.get('event') != 'pre_tool_use':
        return False
    if 'cwd' in context and not Path(context['cwd']).resolve().is_relative_to(workspace):
        return False
    name, args = context.get('tool_name'), context.get('tool_input', {})
    if not isinstance(args, dict):
        return False
    if name not in ['read_file', 'write_file', 'edit_file', 'glob', 'grep']:
        return False
    value = args.get('file_path', args.get('path', str(workspace)))
    if not isinstance(value, str) or '\x00' in value:
        return False
    path = (workspace / value).resolve() if not value.startswith('/') else Path(value).resolve()
    if not path.is_relative_to(workspace) or '.git' in path.relative_to(workspace).parts:
        return False
    relative = path.relative_to(workspace).as_posix()
    if name in ['write_file', 'edit_file']:
        if context.get('node_id') == 'supervisor':
            return relative == '.rust-queue/reports/supervisor.md'
        if context.get('node_id') == 'scope' and not relative.startswith('.rust-queue/reports/'):
            return False
        if relative == '.rust-queue/reports/native-check-summary.json':
            return False
        reports = relative.startswith('.rust-queue/reports/')
        source = relative.startswith('score/mw/com/')
        if control['mode'] in ['assessment', 'reuse', 'design']:
            source = source and (path.suffix in ['.md', '.rst', '.trlc', '.puml'] or 'doc/' in relative or 'design/' in relative)
        return reports or source
    if name == 'read_file':
        registration = control.get('native_json_reads', {}).get(relative)
        native_json = (path.suffix == '.json' and relative.startswith('score/mw/com/')
                       and registration is not None and path.is_file()
                       and path.stat().st_size <= registration['max_bytes'])
        if path.suffix in ['.json', '.log', '.xml', '.crate', '.gz'] and not (native_json or relative.startswith('.rust-queue/context/') or relative in ['.rust-queue/reports/check-plan.json', '.rust-queue/reports/native-check-summary.json']):
            return False
        return 0 < int(args.get('limit', 200)) <= 200
    if name == 'grep':
        return args.get('output_mode') in ['files_with_matches', 'count']
    return isinstance(args.get('pattern'), str)


if __name__ == '__main__':
    try:
        permitted = allowed(json.load(sys.stdin), sys.argv[1])
    except Exception:
        permitted = False
    if not permitted:
        print(json.dumps({'decision': 'block', 'reason': 'Bound Rust workspace/file-tool boundary'}))
    raise SystemExit(0 if permitted else 2)
