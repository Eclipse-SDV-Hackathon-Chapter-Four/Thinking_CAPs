#!/usr/bin/env python3
"""Build a portable ThreadX/Zenoh2CAN container and native OpenSOVD bundle."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
# ThreadX comes with the X-Verse branch (external_hackathon_ecus/ThreadX).
THREADX = ROOT.parents[2] / 'demo' / 'X-Verse' / 'external_hackathon_ecus' / 'ThreadX'
sys.path.insert(0, str(ROOT / 'scripts'))
from vm import digest, run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bridge-source', type=Path, required=True, help='Pinned zenoh2can_bridge checkout')
    p.add_argument('--output', type=Path, default=ROOT / '.local/workload.tar')
    p.add_argument('--target-dir', type=Path, default=ROOT / '.cache/rust-target')
    p.add_argument('--engine', choices=['docker', 'podman'], default='docker')
    args = p.parse_args()
    if args.output.exists():
        p.error('Use a new output bundle path')
    bridge = args.bridge_source.resolve()
    cfg = json.loads((ROOT / 'config/deployment.json').read_text())
    revision = subprocess.check_output(['git', '-C', str(bridge), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != cfg['bridge']['revision']:
        p.error('Bridge checkout does not match pinned revision')
    run(['git', '-C', bridge, 'diff', '--exit-code', 'HEAD', '--', 'src/bridge.py'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / '.local').mkdir(exist_ok=True)
    run([args.engine, 'build', '-t', 'threadx-zonal-lights:autosd-build', THREADX])
    with tempfile.TemporaryDirectory(prefix='autosd-bundle-', dir=ROOT / '.local') as temp:
        staging = Path(temp)
        context = staging / 'context'
        context.mkdir()
        shutil.copy2(bridge / 'src/bridge.py', context / 'bridge.py')
        shutil.copy2(ROOT / 'scripts/controller.py', context / 'controller.py')
        shutil.copy2(ROOT / 'tests/can_probe.py', context / 'can_probe.py')
        shutil.copy2(ROOT / 'config/Workload.Dockerfile', context / 'Dockerfile')
        run([args.engine, 'build', '-t', 'sdv-autosd-lighting:1.0', context])
        if args.engine == 'podman':
            save = ['podman', 'save', '--format', 'docker-archive']
        else:
            save = ['docker', 'save']
        run([*save, '-o', staging / 'workload-image.tar', 'sdv-autosd-lighting:1.0'])
        run(['cargo', 'build', '--locked', '--manifest-path', ROOT.parents[2] / 'contributions/eclipse-opensovd/OpenSOVD/integration/lighting-diagnostics/Cargo.toml',
             '--target-dir', args.target_dir.resolve()])
        shutil.copy2(args.target_dir / 'debug/sdv-lighting-diagnostics', staging / 'sdv-lighting-diagnostics')
        for f in (ROOT / 'config').glob('sdv-*.service'):
            shutil.copy2(f, staging / f.name)
        shutil.copy2(ROOT / 'config/provision.sh', staging / 'provision.sh')
        metadata = {'schema_version': 1, 'bridge_revision': revision,
                    'bridge_source_sha256': digest(bridge / 'src/bridge.py'),
                    'opensovd_revision': cfg['opensovd_revision'],
                    'threadx_revision': json.loads((THREADX / 'dependencies.lock.json').read_text()),
                    'rustc': subprocess.check_output(['rustc', '--version'], text=True).strip(),
                    'cargo': subprocess.check_output(['cargo', '--version'], text=True).strip(),
                    'container_id': subprocess.check_output([args.engine, 'image', 'inspect', '--format', '{{.Id}}',
                                                             'sdv-autosd-lighting:1.0'], text=True).strip(),
                    'files': {f.name: digest(f) for f in staging.iterdir() if f.is_file()}}
        (staging / 'build.json').write_text(json.dumps(metadata, indent=2) + '\n')
        with tarfile.open(args.output, 'w') as bundle:
            for f in sorted(staging.iterdir()):
                if f.is_file():
                    bundle.add(f, arcname=f.name)
    print(json.dumps({'bundle': str(args.output), 'sha256': digest(args.output)}))


if __name__ == '__main__':
    main()
