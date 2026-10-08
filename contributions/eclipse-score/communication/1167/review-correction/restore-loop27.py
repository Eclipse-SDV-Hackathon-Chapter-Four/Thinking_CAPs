#!/usr/bin/python3
"""Restore the existing build image's exact loop binding; never create an image."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

IMAGE = Path('/media/jefferson/Lexar/.s-core-build/build-volume-v1.ext4')
MOUNT = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0')
SSD = Path('/media/jefferson/Lexar')
OLD = '/dev/loop1'
NEW = '/dev/loop27'
VOLUME_UUID = '11c42dee-73a3-4c2b-ab42-a0440011d9e0'
SSD_UUID = '002B-CE31'
OPTIONS = 'rw,nosuid,nodev,relatime,errors=remount-ro'
ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}


def run(*args, allowed=(0,)):
    result = subprocess.run(args, env=ENV, text=True, capture_output=True, timeout=30)
    if result.returncode not in allowed:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}): {result.stderr.strip()}')
    return result


def loops():
    return json.loads(run('losetup', '--list', '--json', '--output',
                          'NAME,BACK-FILE,OFFSET,SIZELIMIT,RO').stdout)['loopdevices']


def mounts(device):
    result = run('findmnt', '-J', '--source', device,
                 '-o', 'TARGET,SOURCE,FSTYPE,FSROOT', allowed=(0, 1))
    return json.loads(result.stdout)['filesystems'] if result.returncode == 0 else []


def preflight():
    if IMAGE.is_symlink() or not IMAGE.is_file() or not SSD.is_mount():
        raise RuntimeError('Original mounted SSD and regular backing image are required')
    ssd = json.loads(run('findmnt', '-J', '-T', str(SSD),
                         '-o', 'TARGET,UUID').stdout)['filesystems'][0]
    if ssd['target'] != str(SSD) or ssd['uuid'] != SSD_UUID:
        raise RuntimeError('SSD mount/UUID changed')
    rows = loops()
    matching = [r for r in rows if r['back-file'] == str(IMAGE)]
    if len(matching) != 1:
        raise RuntimeError('Backing image must have exactly one loop attachment')
    row = matching[0]
    device = row['name']
    if device not in (OLD, NEW) or row['offset'] or row['sizelimit'] or row['ro']:
        raise RuntimeError('Unexpected image device or loop parameters')
    if device != NEW and any(r['name'] == NEW for r in rows):
        raise RuntimeError('loop27 is occupied; it must not be detached')
    mounted = mounts(device)
    if len(mounted) != 1 or mounted[0] != {
            'target': str(MOUNT), 'source': device, 'fstype': 'ext4', 'fsroot': '/'}:
        raise RuntimeError('Expected exactly the original ext4 root mount, without other binds')
    if os.geteuid() == 0:
        uuid = run('blkid', '-p', '-s', 'UUID', '-o', 'value', str(IMAGE)).stdout.strip()
        if uuid != VOLUME_UUID:
            raise RuntimeError('Backing image UUID changed')
    return device


def restore():
    if os.geteuid() != 0:
        raise RuntimeError('Administrator authentication is required; run with sudo')
    flags = os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW
    fd = os.open('/run/lock/score-communication1167-loop27.lock', flags, 0o600)
    with os.fdopen(fd, 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        device = preflight()
        if device == NEW:
            return {'status': 'already_restored', 'source': NEW, 'mount': str(MOUNT)}
        users = run('fuser', '-m', str(MOUNT), allowed=(0, 1))
        if users.returncode == 0 or users.stderr.strip():
            raise RuntimeError('Filesystem is in use; stop its owning work before retrying')
        if run('docker', 'ps', '--quiet').stdout.strip():
            raise RuntimeError('Running containers exist; leave them untouched and investigate')
        if Path.cwd().is_relative_to(MOUNT):
            raise RuntimeError('Run from an internal directory outside this filesystem')
        run('sync', '-f', str(MOUNT))
        run('umount', str(MOUNT))  # Normal unmount refuses new users; never force/lazy unmount.
        try:
            run('losetup', '--detach', OLD)
            if any(r['name'] in (OLD, NEW) for r in loops()):
                raise RuntimeError('Loop device became occupied; refusing substitution')
            run('losetup', NEW, str(IMAGE))
            run('mount', '-t', 'ext4', '-o', OPTIONS, NEW, str(MOUNT))
            if preflight() != NEW or MOUNT.stat().st_dev != os.makedev(7, 27):
                raise RuntimeError('Restored binding did not verify')
        except Exception:
            # Restore the prior mapping only when the image remains unmounted.
            matching = [r for r in loops() if r['back-file'] == str(IMAGE)]
            if any(mounts(r['name']) for r in matching):
                print('A mount remains present; no automatic detach was attempted.', file=sys.stderr)
            elif len(matching) <= 1:
                if matching and matching[0]['name'] == NEW:
                    run('losetup', '--detach', NEW)
                    matching = []
                if not matching and not any(r['name'] == OLD for r in loops()):
                    run('losetup', OLD, str(IMAGE))
                    matching = [r for r in loops() if r['back-file'] == str(IMAGE)]
                if len(matching) == 1 and matching[0]['name'] == OLD:
                    run('mount', '-t', 'ext4', '-o', OPTIONS, OLD, str(MOUNT))
                    print('Original loop1 mount restored after failure.', file=sys.stderr)
            raise
        return {'status': 'restored', 'source': NEW, 'mount': str(MOUNT),
                'volume_uuid': VOLUME_UUID, 'mount_device': MOUNT.stat().st_dev}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true', help='Read-only preliminary checks')
    mode.add_argument('--restore', action='store_true', help='Restore loop27; requires root')
    args = parser.parse_args()
    try:
        result = ({'status': 'preliminary_check_passed', 'source': preflight(),
                   'mutation': False, 'root_busy_and_image_uuid_checks': os.geteuid() == 0}
                  if args.check else restore())
        print(json.dumps(result, indent=2))
    except Exception as error:
        print(f'Refused: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
