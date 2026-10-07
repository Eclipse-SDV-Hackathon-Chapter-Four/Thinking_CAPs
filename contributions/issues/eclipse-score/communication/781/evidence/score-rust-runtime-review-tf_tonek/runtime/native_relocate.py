"""Apply explicit, hash-bound native file moves in a disposable workspace."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from storage import validate_run_root

ROOT = Path(__file__).parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_path(workspace: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or '.git' in path.parts:
        raise ValueError('Unsafe native path')
    if not path.is_relative_to('score/mw/com') or path == Path('score/mw/com'):
        raise ValueError('Outside registered native source scope')
    absolute = workspace / path
    for candidate in [absolute, *absolute.parents]:
        if candidate == workspace:
            break
        if candidate.is_symlink():
            raise ValueError('Symlink native path rejected')
    if not absolute.resolve().is_relative_to(workspace / 'score/mw/com'):
        raise ValueError('Native path escaped workspace')
    return absolute


def apply(issue: str, plan: dict, dry_run: bool = False) -> dict:
    validate_run_root(ROOT)
    control = json.loads((ROOT / 'jobs' / issue / 'task.json').read_text())
    workspace = Path(control['workspace'])
    if control['mode'] != 'implementation' or not workspace.resolve().is_relative_to(ROOT / 'workspaces'):
        raise ValueError('Relocation requires an implementation workspace')
    if workspace.is_symlink():
        raise ValueError('Workspace symlink rejected')
    if set(plan) != {'moves'} or not isinstance(plan['moves'], list) or not plan['moves']:
        raise ValueError('Explicit nonempty move plan required')
    moves = []
    touched = set()
    for item in plan['moves']:
        if set(item) != {'source', 'destination', 'source_sha256'}:
            raise ValueError('Unsupported move fields')
        src = source_path(workspace, item['source'])
        dst = source_path(workspace, item['destination'])
        if src in touched or dst in touched or src == dst:
            raise ValueError('Repeated/overlapping move path')
        touched.update([src, dst])
        if not src.is_file() or dst.exists():
            raise ValueError('Source must be a file and destination must be absent')
        if digest(src) != item['source_sha256']:
            raise ValueError('Source hash drift')
        moves.append((src, dst, item['source_sha256']))
    completed = []
    if not dry_run:
        try:
            for src, dst, expected in moves:
                validate_run_root(ROOT)
                if digest(src) != expected or dst.exists():
                    raise ValueError('Move subjects changed during application')
                # Recheck parents before mutation; source and destination share the
                # selected volume, so rename retains bytes and native permissions.
                source_path(workspace, str(src.relative_to(workspace)))
                source_path(workspace, str(dst.relative_to(workspace)))
                dst.parent.mkdir(parents=True, exist_ok=True)
                src.rename(dst)
                completed.append((src, dst))
                assert digest(dst) == expected
        except Exception:
            validate_run_root(ROOT)
            for src, dst in reversed(completed):
                dst.rename(src)
            raise
    return {'operation': 'dry_run' if dry_run else 'relocate', 'moves': len(moves),
            'source_hashes_verified': True, 'acceptance': 'not supplied',
            'records': plan['moves']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--issue', required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not args.issue.isdigit():
        raise SystemExit('Numeric issue control required')
    validate_run_root(ROOT)
    control = json.loads((ROOT / 'jobs' / args.issue / 'task.json').read_text())
    expected = Path(control['workspace']) / '.rust-queue/reports/relocation-plan.json'
    if args.plan.absolute() != expected or args.plan.is_symlink():
        raise SystemExit('Only the registered relocation plan is allowed')
    if args.plan.stat().st_size > 16384:
        raise SystemExit('Relocation plan exceeds the operator payload ceiling')
    print(json.dumps(apply(args.issue, json.loads(args.plan.read_text()), args.dry_run)))
