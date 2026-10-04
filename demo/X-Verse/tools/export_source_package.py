#!/usr/bin/env python3
"""Export unpublished working sources as portable Git bundles without changing them."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def git(source, *arguments):
    return subprocess.check_output(['git', '-C', str(source), *arguments], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integration', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sources = [('autoverse', workspace, 'autoverse', git(workspace, 'remote', 'get-url', 'origin')),
               ('integration', args.integration.resolve(), 'eclipse_sdv_hackathon_2026',
                git(args.integration, 'remote', 'get-url', 'origin'))]
    # vcstool supplies PyYAML during workstation setup.
    import yaml
    manifest = yaml.safe_load((workspace / 'autoverse.repos').read_text())['repositories']
    sources += [('component-' + str(index), workspace / relative, 'autoverse/' + relative, entry['url'])
                for index, (relative, entry) in enumerate(manifest.items())]
    records = []
    for name, source, relative, origin in sources:
        snapshot = output / 'snapshots' / name
        snapshot.parent.mkdir(exist_ok=True)
        env = dict(os.environ, GIT_LFS_SKIP_SMUDGE='1')
        subprocess.run(['git', 'clone', '--no-hardlinks', str(source), str(snapshot)], env=env, check=True)
        files = subprocess.check_output(['git', '-C', str(source), 'ls-files', '--cached', '--others',
                                         '--exclude-standard', '-z']).decode().split('\0')
        for item in sorted(set(filter(None, files)), key=lambda p: (len(Path(p).parts), p)):
            src, dst = source / item, snapshot / item
            if any(p.is_symlink() for p in src.parents if p != source and p.is_relative_to(source)):
                continue
            if not src.exists() and not src.is_symlink():
                if dst.is_file() or dst.is_symlink(): dst.unlink()
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_symlink():
                if dst.is_dir() and not dst.is_symlink(): shutil.rmtree(dst)
                elif dst.exists() or dst.is_symlink(): dst.unlink()
                dst.symlink_to(src.readlink(), target_is_directory=src.is_dir())
            elif src.is_file():
                if dst.is_symlink(): dst.unlink()
                shutil.copy2(src, dst)
        subprocess.run(['git', '-C', str(snapshot), 'switch', '-C', 'readme-validated'], check=True)
        subprocess.run(['git', '-C', str(snapshot), 'add', '-A'], check=True)
        subprocess.run(['git', '-C', str(snapshot), '-c', 'user.name=README source export',
                        '-c', 'user.email=readme-export@localhost', 'commit', '--allow-empty',
                        '-m', 'Local source package for README reproduction'], check=True)
        bundle = output / (name + '.bundle')
        subprocess.run(['git', '-C', str(snapshot), 'bundle', 'create', str(bundle), 'readme-validated'], check=True)
        records.append({'path': relative, 'origin': origin, 'bundle': bundle.name,
                        'revision': git(snapshot, 'rev-parse', 'HEAD'),
                        'source_head': git(source, 'rev-parse', 'HEAD'),
                        'sha256': hashlib.sha256(bundle.read_bytes()).hexdigest()})
    (output / 'manifest.json').write_text(json.dumps({'schema_version': 1, 'published': False,
        'includes_working_tree_changes': True, 'sources': records}, indent=2) + '\n')
    print('Source package:', output)


if __name__ == '__main__':
    main()
