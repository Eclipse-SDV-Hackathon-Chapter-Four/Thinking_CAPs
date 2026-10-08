"""Bounded integration harness reusing existing X-Verse vehicle and VCU classes.

Only the dedicated server process group and spawned actor are owned. Existing CARLA
servers/world settings are not modified. Operator pedal/engage requests are generated
by this harness; speed, frames, VCU decisions and return actuation are real.
"""
import importlib.util
import json
import logging
import math
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def wait_for_world(client_factory, server_running, timeout_seconds, record_attempt):
    """Retry fresh clients: a pre-bind connection failure can persist in a client."""
    deadline = time.monotonic() + timeout_seconds
    while True:
        if not server_running():
            raise RuntimeError('owned CARLA exited before readiness; see carla-server.log')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('owned CARLA readiness timeout')
        client = client_factory()
        client.set_timeout(min(2, remaining))
        try:
            return client.get_world(), client
        except RuntimeError as error:
            record_attempt({'monotonic_ns': time.monotonic_ns(), 'error': str(error)})
        time.sleep(min(.2, max(0, deadline - time.monotonic())))


def correlate_return_actuation(samples, damping, limits):
    """Correlate native VCU input with a subsequent applied actor control."""
    matches = []
    for index, sample in enumerate(samples):
        native = sample['score_throttle_received_by_vcu']
        if not sample['cc_engaged'] or sample['operator_acc_pedal'] != 0 or native <= .01:
            continue
        expected = max(limits[0], min(limits[1], native)) / damping
        if abs(sample['vcu_throttle_command'] - expected) > 1e-5:
            continue
        for applied in samples[index + 1:index + 4]:
            if applied['cc_engaged'] and applied['operator_acc_pedal'] == 0 and abs(applied['applied_throttle'] - expected) <= 1e-5:
                matches.append({'received_frame': sample['frame'], 'applied_frame': applied['frame'],
                    'native_request': native, 'vehicle_command': expected,
                    'observation_delta_ns': applied['observed_at_monotonic_ns'] - sample['observed_at_monotonic_ns']})
                break
    return {'matches': matches, 'match_count': len(matches), 'required_matches': 20,
            'comparison_tolerance': 1e-5, 'sample_window': 3, 'damping': damping,
            'limits': list(limits), 'claim': 'sampled native-to-VCU-to-actor correlation; no E2E sample identifier or latency guarantee'}


class OwnedCarla:
    def __init__(self, config, output):
        self.config, self.output = config, Path(output)
        self.process = self.actor = self.communicator = self.vcu = self.log = None
        self.runtime = None
        self.samples, self.identity = [], {'status': 'initializing'}

    def start(self):
        import carla
        root = Path(self.config['root'])
        port = int(self.config.get('port', 2100))
        for candidate in range(port, port + 3):
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', candidate))
        binary = root / 'CarlaUE4/Binaries/Linux/CarlaUE4-Linux-Shipping'
        self.runtime = tempfile.TemporaryDirectory(prefix='sdv-owned-carla-')
        runtime = Path(self.runtime.name)
        environment = os.environ.copy()
        environment['XDG_CONFIG_HOME'] = str(runtime / 'config')
        if self.config.get('vulkan_icd'):
            icd = Path(self.config['vulkan_icd'])
            if not icd.is_file():
                raise RuntimeError('selected Vulkan ICD is unavailable: ' + str(icd))
            environment['VK_ICD_FILENAMES'] = str(icd)
            probe = subprocess.run(['vulkaninfo', '--summary'], env=environment, capture_output=True, text=True, timeout=10)
            (self.output / 'vulkan-probe.txt').write_text(probe.stdout + probe.stderr)
            if probe.returncode:
                raise RuntimeError('selected Vulkan ICD probe failed')
        self.log = (self.output / 'carla-server.log').open('w')
        self.process = subprocess.Popen([str(binary), 'CarlaUE4', '/Game/Carla/Maps/Town01',
            '-prefernvidia', '-RenderOffScreen', '-quality-level=Low', '-nosound', '-fps=20',
            '-carla-rpc-port=' + str(port), '-UserDir=' + str(runtime / 'user'),
            '-abslog=' + str((self.output / 'carla-engine.log').resolve())],
            cwd=root, env=environment, stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        readiness = []
        def record_attempt(attempt):
            readiness.append(attempt)
            (self.output / 'carla-readiness.json').write_text(json.dumps(readiness, indent=2) + '\n')
        world, client = wait_for_world(lambda: carla.Client('127.0.0.1', port, 2),
            lambda: self.process.poll() is None, float(self.config.get('startup_timeout_seconds', 120)), record_attempt)
        client.set_timeout(3)
        self.world = world
        self.vehicle_module = load(self.config['vehicle_module'], 'sdv_existing_virtual_vehicle')
        self.vehicle_module.carla = carla
        if not self.vehicle_module.SignalDefinitions.load_from_file(self.config['signals']):
            raise RuntimeError('existing vehicle signals could not be loaded')
        blueprint = world.get_blueprint_library().find('vehicle.tesla.model3')
        role = 'sdv-campaign-' + uuid.uuid4().hex
        blueprint.set_attribute('role_name', role)
        # Select a deterministic long straight lane on the dedicated world.
        points = world.get_map().get_spawn_points()
        chosen = None
        for point in points:
            waypoint = world.get_map().get_waypoint(point.location)
            following = waypoint.next(180)
            if following and abs((following[0].transform.rotation.yaw - waypoint.transform.rotation.yaw + 180) % 360 - 180) < 5:
                chosen = point
                break
        self.actor = world.try_spawn_actor(blueprint, chosen or points[0])
        if self.actor is None:
            raise RuntimeError('dedicated CARLA actor spawn failed')
        vcu_path = Path(self.config['vcu_module'])
        sys.path.insert(0, str(vcu_path.parent))
        vcu_module = load(vcu_path, 'sdv_existing_vcu')
        logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger('sdv_existing_vcu').setLevel(logging.WARNING)
        vcu_config = self.output / 'vcu-zenoh.json'
        vcu_config.write_text(json.dumps({'mode': 'peer', 'connect': {'endpoints': ['tcp/172.30.77.1:7447']},
                                          'scouting': {'multicast': {'enabled': False}}}) + '\n')
        self.vcu = vcu_module.VCUController(str(vcu_config))
        self.throttle_limits = (vcu_module.MIN_THROTTLE, vcu_module.MAX_THROTTLE)
        self.throttle_damping = self.vehicle_module.THROTTLE_DAMPING_FACTOR
        self.communicator = self.vehicle_module.ZenohCommunicator('172.30.77.1')
        self.publisher = self.vehicle_module.StatusPublisher(self.actor, self.communicator)
        self.controller = self.vehicle_module.VehicleController(self.actor, self.communicator)
        self.map = world.get_map()
        self.identity = {'status': 'real', 'server_version': client.get_server_version(),
                         'client_version': client.get_client_version(), 'map': world.get_map().name,
                         'actor_id': self.actor.id, 'actor_type': self.actor.type_id, 'role_name': role,
                         'rpc_port': port, 'pid': self.process.pid, 'world_settings_changed': False,
                         'vulkan_icd': self.config.get('vulkan_icd', 'system default'),
                         'operator_inputs': 'harness pedal/engage and waypoint steering requests; existing VCU decides engagement; existing vehicle controller applies commands',
                         'plant_clock': 'CARLA snapshot elapsed_seconds; watchdog uses Linux monotonic'}

    def step(self, engage):
        snapshot = self.world.wait_for_tick(2)
        if snapshot is None:
            raise RuntimeError('owned CARLA frame timeout')
        self.publisher.update(snapshot.timestamp)
        self.vcu.session.put('vehicle/command/acc_pedal_sts', '0.7' if not engage else '0')
        self.vcu.session.put('vehicle/command/brake_pedal_sts', '0')
        self.vcu.session.put('vehicle/control/cc_engage_req', str(engage).lower())
        # Test-driver steering uses the existing manual-control topic. Throttle
        # still follows the unchanged VCU/native Cruise Control return path.
        transform = self.actor.get_transform()
        waypoint = self.map.get_waypoint(transform.location)
        lookahead = max(8, self.speed() / 3.6 * .8)
        following = waypoint.next(lookahead)
        steer = 0
        if following:
            target = min(following, key=lambda point: abs((point.transform.rotation.yaw - waypoint.transform.rotation.yaw + 180) % 360 - 180))
            delta = target.transform.location - transform.location
            angle = math.atan2(delta.y, delta.x) - math.radians(transform.rotation.yaw)
            steer = max(-.8, min(.8, math.atan2(2 * 2.9 * math.sin(angle), lookahead) / .7))
        self.vcu.session.put(self.vehicle_module.SignalDefinitions.get_topic('ego_steer_sts'), str(steer))
        self.controller.update()
        control = self.actor.get_control()
        self.samples.append({'frame': snapshot.frame, 'simulation_elapsed_seconds': snapshot.timestamp.elapsed_seconds,
            'observed_at_monotonic_ns': time.monotonic_ns(), 'speed_kmh': self.speed(),
            'cc_engaged': self.vcu.cc_engage_sts, 'score_throttle_received_by_vcu': self.vcu.adas_throttle,
            'vcu_throttle_command': self.communicator.vcu_throttle_cmd, 'applied_throttle': control.throttle,
            'applied_brake': control.brake, 'operator_acc_pedal': 0 if engage else .7,
            'operator_steering_request': steer, 'applied_steer': control.steer,
            'location': {'x': transform.location.x, 'y': transform.location.y, 'z': transform.location.z}})

    def speed(self):
        return self.publisher.get_current_speed_kmh()

    def close(self):
        errors = []
        for identifier, action in (('actor', lambda: self.actor.destroy() if self.actor else None),
                                   ('vehicle-session', lambda: self.communicator.close() if self.communicator else None),
                                   ('vcu-session', lambda: self.vcu.session.close() if self.vcu else None)):
            try:
                action()
            except Exception as error:
                errors.append(identifier + ': ' + str(error))
        if self.process is not None and self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGTERM)
            try:
                self.process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait(timeout=3)
        if self.log:
            self.log.close()
        if self.runtime:
            try:
                self.runtime.cleanup()
            except OSError as error:
                errors.append('private-runtime: ' + str(error))
        (self.output / 'carla-samples.json').write_text(json.dumps(self.samples, indent=2) + '\n')
        (self.output / 'carla-identity.json').write_text(json.dumps(self.identity, indent=2) + '\n')
        if errors:
            raise RuntimeError('; '.join(errors))
