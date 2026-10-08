#!/usr/bin/env python3
"""Attach an AutoSD guest NIC to an explicitly selected owned openDuT bench."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / 'OpenDut/scripts'))
from opendut_testbench import Bench, run

LABEL = 'sdv.autosd.vm'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['up', 'configure', 'local', 'status', 'down'])
    p.add_argument('--bench-state', type=Path, required=True)
    p.add_argument('--vm-state', type=Path, default=ROOT / '.local/lighting-vm')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error('Choose a new receipt output')
    bench = Bench(a.bench_state)
    state = json.loads((a.vm_state / 'state.json').read_text())
    identity = state['id']
    relay = 'sdv-autosd-relay-' + identity[:8]
    router = 'sdv-autosd-router-' + identity[:8]
    names = [relay, router]
    peer_a, peer_b = bench.management_address(11), bench.management_address(12)
    receipt = {'schema_version': 1, 'vm_id': identity, 'bench_run_id': bench.state['run_id'],
               'profile': 'openDuT 0.10.2 local managed Ethernet/GRE; guest end station attached to peer B',
               'qemu_endpoint': peer_b + ':19092', 'host_zenoh_endpoint': 'tcp/' + peer_a + ':7447',
               'guest_zenoh_endpoint': 'tcp/192.168.123.101:7447'}
    if a.action == 'up':
        if bench.state['phase'] != 'deployed':
            raise RuntimeError('Deploy the owned openDuT bench first')
        for peer in ['a', 'b']:
            bench.ownership('container', bench.name(peer))
        run(['docker', 'run', '-d', '--name', relay, '--label', LABEL + '=' + identity,
             '--network', 'container:' + bench.name('b'), '--cap-add', 'NET_ADMIN', '--device', '/dev/net/tun',
             '-v', str(ROOT / 'scripts/ethernet_relay.py') + ':/relay.py:ro',
             'threadx-zonal-lights:autosd-build', 'python3', '/relay.py', '--listen', peer_b])
        run(['docker', 'run', '-d', '--name', router, '--label', LABEL + '=' + identity,
             '--network', 'container:' + bench.name('a'), 'eclipse/zenoh:1.3.4', '--listen', 'tcp/0.0.0.0:7447'])
        deadline = time.monotonic() + 10
        while '"event": "ready"' not in run(['docker', 'logs', relay]):
            if time.monotonic() > deadline:
                raise RuntimeError('Ethernet relay unavailable; inspect owned container logs')
            time.sleep(.1)
        receipt['status'] = 'attached'
    elif a.action == 'configure':
        # SSH stays on the separate QEMU management interface.
        sys.path.insert(0, str(ROOT / 'scripts'))
        from vm import VM
        vm = VM(argparse.Namespace(state=a.vm_state))
        script = '''set -eu
nic=$(python3 -c 'import json,subprocess; print(next(i["ifname"] for i in json.loads(subprocess.check_output(["ip","-j","link"])) if i.get("address")=="52:54:00:77:00:03"))')
if ! nmcli connection show sdv-opendut >/dev/null 2>&1; then
    nmcli connection add type ethernet ifname "$nic" con-name sdv-opendut ipv4.method manual ipv4.addresses 192.168.123.103/24 ipv4.never-default yes ipv6.method disabled
fi
nmcli connection up sdv-opendut
systemctl stop sdv-threadx sdv-zenoh-can
python3 -c 'import json; p="/var/lib/sdv-lighting/bridge.json"; j=json.load(open(p)); j["zenoh"]["connect"]=["tcp/192.168.123.101:7447"]; open(p,"w").write(json.dumps(j))'
systemctl start sdv-zenoh-can
sleep 2
systemctl start sdv-threadx
ip route get 192.168.123.101
ping -c 3 -W 2 192.168.123.101
'''
        receipt['guest_network'] = vm.ssh('sh -s', input=script, capture_output=True, text=True).stdout
        receipt['status'] = 'configured'
    elif a.action == 'local':
        sys.path.insert(0, str(ROOT / 'scripts'))
        from vm import VM
        vm = VM(argparse.Namespace(state=a.vm_state))
        script = '''set -eu
systemctl stop sdv-threadx sdv-zenoh-can
python3 -c 'import json; p="/var/lib/sdv-lighting/bridge.json"; j=json.load(open(p)); j["zenoh"]["connect"]=["tcp/10.0.2.2:7447"]; open(p,"w").write(json.dumps(j))'
nmcli connection delete sdv-opendut
systemctl start sdv-zenoh-can
sleep 2
systemctl start sdv-threadx
'''
        vm.ssh('sh -s', input=script, text=True)
        vm.state.pop('dut_endpoint', None)
        vm.save()
        receipt['status'] = 'local-profile-restored'
    elif a.action == 'status':
        receipt['containers'] = json.loads(run(['docker', 'inspect', *names]))
        receipt['guest_bridge'] = run(['docker', 'exec', bench.name('b'), 'ip', '-d', '-j', 'link'])
    else:
        receipt['cleanup'] = []
        for name in names:
            inspected = subprocess.run(['docker', 'inspect', '--format', '{{json .Config.Labels}}', name],
                                       capture_output=True, text=True)
            if inspected.returncode:
                receipt['cleanup'].append({'name': name, 'status': 'absent'})
                continue
            if json.loads(inspected.stdout).get(LABEL) != identity:
                raise RuntimeError('Refusing to remove unrelated container ' + name)
            if name == relay:
                run(['docker', 'stop', '--time', '3', name])
                receipt['relay_log'] = run(['docker', 'logs', name])
            run(['docker', 'rm', '-f', name])
            receipt['cleanup'].append({'name': name, 'status': 'removed'})
        receipt['status'] = 'removed'
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ['containers', 'guest_bridge']}, indent=2))


if __name__ == '__main__':
    main()
