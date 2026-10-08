#!/usr/bin/env python3
"""Test the deployed AutoSD guest over actual host/guest Zenoh and OpenSOVD."""
import argparse
import importlib.util
import json
from pathlib import Path
import queue
import signal
import subprocess
import sys
import time
import urllib.request

import zenoh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from vm import VM


def wait(predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.025)
    raise AssertionError('Timed out waiting for observed state')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state', type=Path, default=ROOT / '.local/lighting-vm')
    p.add_argument('--endpoint', default='tcp/127.0.0.1:7447')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--carla-host')
    p.add_argument('--carla-port', type=int, default=2000)
    p.add_argument('--vehicle-module', type=Path)
    p.add_argument('--signals', type=Path)
    p.add_argument('--bench-state', type=Path, help='Also disturb the actual selected openDuT GRE path')
    args = p.parse_args()
    if args.carla_host and not (args.vehicle_module and args.signals):
        p.error('CARLA mode needs --vehicle-module and --signals')
    args.output.mkdir(parents=True, exist_ok=False)
    vm = VM(args)
    cfg = vm.state['config']
    base = f'http://127.0.0.1:{cfg["vm"]["diagnostics_port"]}/sovd/v1'
    checks, requests, packets, carla_rows = [], [], [], []
    actor = communicator = controller = tunnel = bench = None
    conf = zenoh.Config()
    conf.insert_json5('mode', '"client"')
    conf.insert_json5('connect/endpoints', json.dumps([args.endpoint]))
    conf.insert_json5('scouting/multicast/enabled', 'false')
    session = zenoh.open(conf)
    incoming = queue.Queue()
    sub = session.declare_subscriber('vehicle/lights/**', lambda s: incoming.put((str(s.key_expr), s.payload.to_string())))
    latest = {}
    uri = history_uri = None

    def check(name, condition=True):
        checks.append({'id': name, 'status': 'passed' if condition else 'failed'})
        if not condition:
            raise AssertionError(name)

    def request(url):
        with urllib.request.urlopen(url, timeout=5) as r:
            value = json.load(r)
        requests.append({'url': url, 'response': value})
        return value

    def observed(reverse, brake):
        while True:
            try:
                k, v = incoming.get_nowait()
                latest[k] = v
                if k == 'vehicle/lights/frame':
                    aggregate = json.loads(v)
                    for name, key in [('bcm_reverse_lights_cmd', 'vehicle/lights/reverse_lights_cmd'),
                                      ('bcm_brake_lights_cmd', 'vehicle/lights/brake_lights_cmd')]:
                        latest[key] = str(bool(aggregate[name])).lower()
            except queue.Empty:
                break
        return latest.get('vehicle/lights/reverse_lights_cmd') == str(reverse).lower() and latest.get(
            'vehicle/lights/brake_lights_cmd') == str(brake).lower()

    def send(reverse, brake):
        status = {'vcu_cc_engage_sts': False, 'vcu_reverse_sts': reverse, 'vcu_brake_sts': brake}
        session.put('vcu/control/status', json.dumps(status))
        wait(lambda: observed(reverse, brake))
        view = wait(lambda: (v if (v := request(uri)['data']['value']).get('lights') == {
            'reverse': reverse, 'brake': brake, 'stale': False} else None))
        packets.append({'input': status, 'feedback': dict(latest), 'native_observation': view})
        if controller:
            wait(lambda: communicator.bcm_reverse_lights_cmd == reverse and communicator.bcm_brake_lights_cmd == brake)
            controller.update()
            expected = (64 if reverse else 0) | (8 if brake else 0)
            wait(lambda: int(actor.get_light_state()) == expected)
            carla_rows.append({'actor_id': actor.id, 'reverse': reverse, 'brake': brake,
                               'expected_light_mask': expected, 'observed_light_mask': int(actor.get_light_state())})

    result = {'schema_version': 1, 'mode': 'real AutoSD QEMU/KVM guest; host Zenoh fixtures',
              'physical_can_hardware': False, 'carla_requested': bool(args.carla_host),
              'native_opensovd': True, 'native_dfm_faults': False, 'openDuT_path': bool(args.bench_state),
              'image': cfg['image'], 'checks': checks}
    try:
        services = vm.ssh('systemctl is-active sdv-threadx sdv-zenoh-can sdv-lighting-diagnostics',
                          capture_output=True, text=True).stdout.splitlines()
        check('three-guest-services-active', services == ['active'] * 3)
        root = request(base)
        apps = request(root['apps'])
        app = request(next(x['href'] for x in apps['items'] if x['id'] == 'zonal-lighting'))
        resources = request(app['data'])
        check('native-opensovd-lighting-discovery', {x['id'] for x in resources['items']} == {
            'lighting.observation', 'lighting.fault-history'})
        uri = app['data'] + '/lighting.observation'
        history_uri = app['data'] + '/lighting.fault-history'
        if args.carla_host:
            import carla
            spec = importlib.util.spec_from_file_location('autosd_virtual_vehicle', args.vehicle_module)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            module.carla = carla
            assert module.SignalDefinitions.load_from_file(str(args.signals))
            client = carla.Client(args.carla_host, args.carla_port)
            client.set_timeout(10)
            assert client.get_server_version().startswith('0.9.15')
            world = client.get_world()
            blueprint = world.get_blueprint_library().find('vehicle.tesla.model3')
            blueprint.set_attribute('role_name', 'autosd-threadx-lighting-test')
            for transform in world.get_map().get_spawn_points():
                actor = world.try_spawn_actor(blueprint, transform)
                if actor:
                    break
            assert actor is not None
            communicator = module.ZenohCommunicator(args.endpoint.split('/')[-1].rsplit(':', 1)[0])
            controller = module.VehicleController(actor, communicator)
        time.sleep(1)
        # Begin with a changed state so the existing bridge's dedupe is respected.
        for reverse, brake in [(True, False), (True, True), (False, True), (False, False)]:
            send(reverse, brake)
        check('host-guest-zenoh-can-threadx-four-states')
        check('native-opensovd-actual-threadx-light-states')
        if actor:
            check('actual-carla-actor-four-light-masks')
        session.put('vcu/control/brake_sts', 'true')
        wait(lambda: observed(False, True))
        wait(lambda: request(uri)['data']['value']['lights'] == {'reverse': False, 'brake': True, 'stale': False})
        check('existing-vcu-individual-text-boolean-topic')
        # A stopped controller must send OFF and retain a fault record.
        send(True, True)
        vm.ssh('systemctl stop sdv-threadx', stdout=subprocess.DEVNULL)
        wait(lambda: observed(False, False))
        view = request(history_uri)['data']['value']
        check('graceful-controller-stop-off-and-diagnostic-fault', 'controller_unavailable' in view['active_faults'])
        time.sleep(3.1)
        view = request(uri)['data']['value']
        check('old-controller-observation-expires', view['controller_state'] == 'unavailable' and view['lights'] is None)
        vm.ssh('systemctl start sdv-threadx', stdout=subprocess.DEVNULL)
        wait(lambda: request(uri)['data']['value']['controller_state'] == 'running')
        view = request(history_uri)['data']['value']
        check('controller-restart-retains-and-clears-fault', 'controller_unavailable' not in view['active_faults']
              and any(x['code'] == 'controller_unavailable' and x['active'] for x in view['history'])
              and any(x['code'] == 'controller_unavailable' and not x['active'] for x in view['history']))
        send(False, True)
        check('controller-restart-command-recovery')
        # Isolate only the workload's Zenoh service; management diagnostics stay up.
        vm.ssh('systemctl stop sdv-zenoh-can', stdout=subprocess.DEVNULL)
        session.put('vcu/control/status', json.dumps({'vcu_reverse_sts': True, 'vcu_brake_sts': False}))
        time.sleep(.5)
        view = request(uri)['data']['value']
        check('gateway-interruption-holds-last-can-state', view['lights']['brake'] and not view['lights']['reverse'])
        vm.ssh('systemctl start sdv-zenoh-can', stdout=subprocess.DEVNULL)
        time.sleep(2)
        send(True, False)
        check('gateway-restart-and-explicit-state-republish')
        if args.bench_state:
            sys.path.insert(0, str(ROOT.parents[2] / 'contributions/eclipse-opendut/OpenDut/scripts'))
            from opendut_testbench import Bench, run
            bench = Bench(args.bench_state)
            bench.ownership('container', bench.name('a'))
            links = json.loads(run(['docker', 'exec', bench.name('a'), 'ip', '-d', '-j', 'link']))
            tunnel = next(l['ifname'] for l in links if l['ifname'].startswith('gre-') and l.get('master') == 'br-opendut')
            result['bench_run_id'] = bench.state['run_id']
            result['managed_tunnel'] = tunnel
            send(False, True)
            run(['docker', 'exec', bench.name('a'), 'ip', 'link', 'set', tunnel, 'down'])
            session.put('vcu/control/status', json.dumps({'vcu_reverse_sts': True, 'vcu_brake_sts': False}))
            time.sleep(1)
            view = request(uri)['data']['value']
            check('actual-opendut-gre-interruption-holds-lights', view['lights']['brake'] and not view['lights']['reverse'])
            check('management-diagnostics-reachable-during-gre-interruption', view['controller_state'] == 'running')
            run(['docker', 'exec', bench.name('a'), 'ip', 'link', 'set', tunnel, 'up'])
            time.sleep(2)
            send(True, True)
            check('actual-opendut-gre-recovery-lighting-roundtrip')
        send(False, False)
        result['status'] = 'passed'
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)
        import traceback
        traceback.print_exc()
    finally:
        if tunnel:
            run(['docker', 'exec', bench.name('a'), 'ip', 'link', 'set', tunnel, 'up'])
        try:
            vm.ssh('systemctl start sdv-zenoh-can sdv-threadx', stdout=subprocess.DEVNULL)
            # This is an isolated fixture test; leave its last command at OFF.
            session.put('vcu/control/status', json.dumps({'vcu_reverse_sts': False, 'vcu_brake_sts': False}))
            log = vm.ssh('journalctl -u sdv-threadx -u sdv-zenoh-can -u sdv-lighting-diagnostics --no-pager -o cat',
                         capture_output=True, text=True).stdout
            (args.output / 'guest-services.log').write_text(log)
        except Exception as e:
            result['cleanup_error'] = str(e)
            result['status'] = 'failed'
        if communicator:
            communicator.close()
        if actor:
            removed = actor.destroy()
            check('owned-carla-actor-removed', removed)
        sub.undeclare()
        session.close()
        for name, value in [('results', result), ('requests', requests), ('packets', packets), ('carla-lights', carla_rows)]:
            (args.output / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'output': str(args.output)}))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
