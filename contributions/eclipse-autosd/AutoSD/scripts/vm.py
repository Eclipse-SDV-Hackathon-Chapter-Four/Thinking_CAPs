#!/usr/bin/env python3
"""Own an AutoSD QEMU/KVM guest, its overlay, SSH key and deployment receipts."""
import argparse
import hashlib
import json
import lzma
import os
from pathlib import Path
import platform
import shlex
import shutil
import socket
import subprocess
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    return subprocess.run([str(x) for x in command], check=True, **kwargs)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


class VM:
    def __init__(self, args):
        self.args = args
        self.path = args.state.resolve()
        self.file = self.path / 'state.json'
        self.state = json.loads(self.file.read_text()) if self.file.exists() else None

    def save(self):
        tmp = self.file.with_suffix('.tmp')
        tmp.write_text(json.dumps(self.state, indent=2) + '\n')
        tmp.chmod(0o600)
        tmp.replace(self.file)

    def prepare(self):
        if self.state or self.path.exists() and any(self.path.iterdir()):
            raise RuntimeError('Choose a new empty state directory; existing state is never overwritten')
        if platform.machine() != 'x86_64' or not os.access('/dev/kvm', os.R_OK | os.W_OK):
            raise RuntimeError('This deployment requires x86_64 Linux with accessible /dev/kvm')
        for tool in ['qemu-system-x86_64', 'qemu-img', 'ssh', 'scp', 'ssh-keygen']:
            if not shutil.which(tool):
                raise RuntimeError(f'Missing prerequisite: {tool}')
        config = json.loads(self.args.config.read_text())
        firmware = next((Path(p) for p in ['/usr/share/OVMF/OVMF_CODE.fd', '/usr/share/edk2/ovmf/OVMF_CODE.fd']
                         if Path(p).is_file()), None)
        if firmware is None or not firmware.with_name('OVMF_VARS.fd').is_file():
            raise RuntimeError('Install OVMF UEFI firmware (Ubuntu: ovmf; Fedora: edk2-ovmf)')
        self.path.mkdir(parents=True, mode=0o700)
        self.path.chmod(0o700)
        cache = self.args.cache.resolve()
        cache.mkdir(parents=True, exist_ok=True)
        image = config['image']
        compressed = cache / (image['sha256'] + '.qcow2.xz')
        if not compressed.exists():
            temporary = compressed.with_suffix('.partial')
            print('Downloading pinned AutoSD image...', flush=True)
            with urllib.request.urlopen(image['url'], timeout=60) as src, temporary.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            temporary.replace(compressed)
        if digest(compressed) != image['sha256']:
            raise RuntimeError('AutoSD download SHA-256 mismatch')
        base = cache / (image['sha256'] + '.qcow2')
        if not base.exists():
            print('Expanding verified AutoSD image...', flush=True)
            temporary = base.with_suffix('.partial')
            with lzma.open(compressed, 'rb') as src, temporary.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            temporary.replace(base)
            base.chmod(0o444)
        identity = str(uuid.uuid4())
        run(['qemu-img', 'create', '-f', 'qcow2', '-F', 'qcow2', '-b', base, self.path / 'disk.qcow2'])
        run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', self.path / 'id_ed25519'])
        shutil.copy2(firmware, self.path / 'OVMF_CODE.fd')
        shutil.copy2(firmware.with_name('OVMF_VARS.fd'), self.path / 'OVMF_VARS.fd')
        self.state = {'schema_version': 1, 'id': identity, 'phase': 'prepared', 'config': config,
                      'base_image_sha256': digest(base), 'base_image': str(base)}
        self.save()
        return {'phase': 'prepared', 'image': image, 'base_image_sha256': self.state['base_image_sha256']}

    def ssh_command(self):
        return ['ssh', '-T', '-p', str(self.state['config']['vm']['ssh_port']),
                '-i', self.path / 'id_ed25519', '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes',
                '-o', 'StrictHostKeyChecking=accept-new', '-o', f'UserKnownHostsFile={self.path}/known_hosts',
                '-o', 'ConnectTimeout=5', 'root@127.0.0.1']

    def ssh(self, command, **kwargs):
        return run([*self.ssh_command(), command], **kwargs)

    def owned_pid(self):
        pidfile = self.path / 'qemu.pid'
        if not pidfile.exists():
            return None
        pid = int(pidfile.read_text())
        try:
            cmdline = Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
        except FileNotFoundError:
            return None
        if self.state['id'].encode() not in cmdline:
            raise RuntimeError('PID no longer belongs to this VM; refusing to control it')
        return pid

    def up(self):
        if self.owned_pid():
            raise RuntimeError('VM is already running')
        cfg = self.state['config']['vm']
        for port in [cfg['ssh_port'], cfg['diagnostics_port']]:
            with socket.socket() as s:
                s.bind(('127.0.0.1', port))
        # An unchanged base image is shared by independent writable overlays.
        if digest(Path(self.state['base_image'])) != self.state['base_image_sha256']:
            raise RuntimeError('Base image changed after preparation')
        command = ['qemu-system-x86_64', '-name', 'sdv-autosd-' + self.state['id'][:8],
                   '-uuid', self.state['id'], '-machine', 'q35,accel=kvm', '-cpu', 'host',
                   '-m', str(cfg['memory_mib']), '-smp', str(cfg['cpus']),
                   '-drive', f'if=pflash,format=raw,readonly=on,file={self.path}/OVMF_CODE.fd',
                   '-drive', f'if=pflash,format=raw,file={self.path}/OVMF_VARS.fd',
                   '-drive', f'file={self.path}/disk.qcow2,format=qcow2,if=none,id=systemdisk',
                   '-device', 'virtio-blk-pci,drive=systemdisk,addr=0x4,bootindex=1',
                   '-netdev', f'user,id=management,hostfwd=tcp:127.0.0.1:{cfg["ssh_port"]}-:22,'
                              f'hostfwd=tcp:127.0.0.1:{cfg["diagnostics_port"]}-:7692',
                   '-device', 'virtio-net-pci,netdev=management,addr=0x2,romfile=', '-display', 'none',
                   '-serial', f'file:{self.path}/console.log', '-monitor', f'unix:{self.path}/monitor.sock,server=on,wait=off',
                   '-pidfile', self.path / 'qemu.pid', '-daemonize']
        if self.args.dut_endpoint:
            self.state['dut_endpoint'] = self.args.dut_endpoint
        if self.state.get('dut_endpoint'):
            command += ['-netdev', 'socket,id=dut,connect=' + self.state['dut_endpoint'],
                        '-device', 'virtio-net-pci,netdev=dut,addr=0x3,romfile=,mac=52:54:00:77:00:03']
        run(command)
        self.state['phase'] = 'booting'
        self.save()
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            if not self.owned_pid():
                raise RuntimeError('QEMU stopped; inspect console.log')
            try:
                self.ssh('true', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            except subprocess.CalledProcessError:
                if not self.state.get('bootstrapped'):
                    try:
                        self.bootstrap()
                        break
                    except subprocess.CalledProcessError:
                        pass
                time.sleep(2)
        else:
            raise RuntimeError('Guest SSH did not become available; inspect console.log')
        self.state['phase'] = 'running'
        self.save()
        return self.status()

    def bootstrap(self):
        # Public sample-image password is used only for first localhost SSH access.
        askpass = self.path / 'askpass'
        askpass.write_text('#!/bin/sh\nprintf "%s\\n" password\n')
        askpass.chmod(0o700)
        key = (self.path / 'id_ed25519.pub').read_text().strip()
        script = f'''set -eu
mkdir -p /root/.ssh /etc/ssh/authorized_keys
chmod 700 /root/.ssh
printf '%s\\n' {shlex.quote(key)} > /root/.ssh/authorized_keys
printf '%s\\n' {shlex.quote(key)} > /etc/ssh/authorized_keys/root
chmod 600 /root/.ssh/authorized_keys /etc/ssh/authorized_keys/root
restorecon -RF /root/.ssh /etc/ssh/authorized_keys
printf '%s\\n' 'PasswordAuthentication no' 'PermitRootLogin prohibit-password' > /etc/ssh/sshd_config.d/00-sdv-key-only.conf
sshd -t
systemctl reload sshd
'''
        command = self.ssh_command()
        command[command.index('BatchMode=yes')] = 'BatchMode=no'
        command[-1:-1] = ['-o', 'PreferredAuthentications=password', '-o', 'NumberOfPasswordPrompts=1']
        try:
            run([*command, 'sh -s'], input=script, text=True, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=20,
                env={**os.environ, 'SSH_ASKPASS': str(askpass), 'SSH_ASKPASS_REQUIRE': 'force', 'DISPLAY': ':0'})
            self.ssh('true', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.state['bootstrapped'] = True
            self.save()
        finally:
            askpass.unlink(missing_ok=True)

    def status(self):
        pid = self.owned_pid()
        result = {'phase': 'running' if pid else 'stopped', 'id': self.state['id'],
                  'image': self.state['config']['image'], 'vm': self.state['config']['vm']}
        if pid:
            out = self.ssh('cat /etc/os-release; uname -r; ip -j address; '
                           'systemctl is-active sdv-threadx sdv-zenoh-can sdv-lighting-diagnostics || true',
                           text=True, capture_output=True).stdout
            result['guest'] = out
        return result

    def deploy(self):
        if not self.owned_pid():
            raise RuntimeError('Start the VM before deployment')
        bundle = self.args.bundle.resolve()
        if not bundle.is_file():
            raise RuntimeError('Build the workload bundle first')
        # scp uses its own port flag; reuse all SSH connection restrictions.
        ssh = self.ssh_command()
        scp = ['scp', '-P', ssh[ssh.index('-p') + 1], *ssh[4:-1], bundle,
               'root@127.0.0.1:/var/tmp/sdv-workload.tar']
        run(scp)
        transferred = self.ssh('sha256sum /var/tmp/sdv-workload.tar', capture_output=True, text=True).stdout.split()[0]
        if transferred != digest(bundle):
            raise RuntimeError('Guest bundle transfer digest mismatch')
        self.ssh('systemctl stop sdv-threadx 2>/dev/null || true; sleep 1; '
                 'systemctl stop sdv-zenoh-can sdv-lighting-diagnostics 2>/dev/null || true')
        self.ssh('mkdir -p /var/lib/sdv-lighting; tar -xf /var/tmp/sdv-workload.tar -C /var/lib/sdv-lighting')
        cfg = self.state['config']['lighting']
        command = ['sh', '/var/lib/sdv-lighting/provision.sh', cfg['zenoh_endpoint'], cfg['interface'], str(cfg['timeout_ms']), cfg['bridge_interface']]
        self.ssh(shlex.join(command))
        self.state['phase'] = 'deployed'
        self.state['bundle_sha256'] = digest(bundle)
        self.save()
        return {**self.status(), 'phase': 'deployed', 'bundle_sha256': self.state['bundle_sha256']}

    def down(self):
        if self.owned_pid():
            # Stop controller before bridge so its OFF frame can reach the vehicle.
            self.ssh('systemctl stop sdv-threadx; sleep 1; systemctl stop sdv-zenoh-can sdv-lighting-diagnostics; '
                     'systemctl poweroff', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 45
            while self.owned_pid() and time.monotonic() < deadline:
                time.sleep(.25)
            if self.owned_pid():
                raise RuntimeError('VM did not shut down; inspect console.log (no forced kill)')
        self.state['phase'] = 'stopped'
        self.save()
        return {'phase': 'stopped', 'qemu_running': False, 'overlay_retained': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['prepare', 'up', 'status', 'deploy', 'ssh', 'down'])
    p.add_argument('--state', type=Path, default=ROOT / '.local/lighting-vm')
    p.add_argument('--cache', type=Path, default=ROOT / '.cache')
    p.add_argument('--config', type=Path, default=ROOT / 'config/deployment.json')
    p.add_argument('--bundle', type=Path, default=ROOT / '.local/workload.tar')
    p.add_argument('--command', default='true', help='Guest shell command for ssh action')
    p.add_argument('--dut-endpoint', help='Optional owned openDuT Ethernet relay IP:port for up')
    p.add_argument('--output', type=Path, help='New JSON receipt path')
    a = p.parse_args()
    if a.output and a.output.exists():
        p.error('Receipt output already exists')
    vm = VM(a)
    if a.action != 'prepare' and not vm.state:
        p.error('Prepare this state first')
    if a.action == 'ssh':
        vm.ssh(a.command)
        return
    receipt = getattr(vm, a.action)()
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
