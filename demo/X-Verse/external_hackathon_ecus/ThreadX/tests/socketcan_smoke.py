#!/usr/bin/env python3
"""Exercise real ThreadX, SocketCAN and optionally the existing Zenoh2CAN bridge.

Run in a private Docker network namespace or on an explicitly prepared vcan bus.
This does not start CARLA, openDuT, OpenSOVD or a vehicle supervisor.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

import can

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from configure_bridge import profile


def wait_for(predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.01)
    raise AssertionError("timed out waiting for runtime observation")


def records(path):
    result = []
    for line in path.read_text().splitlines():
        try:
            result.append(json.loads(line))
        except ValueError:
            pass
    return result


def frame(bus, value, timeout=3):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = bus.recv(timeout=min(0.1, max(0, deadline - time.monotonic())))
        if message is not None and message.arbitration_id == 0x1F4:
            assert not message.is_extended_id and not message.is_remote_frame
            assert message.dlc == 8 and bytes(message.data) == bytes([value]) + bytes(7), message
            return message
    raise AssertionError(f"no 0x1F4 frame with light state {value}")


class Runtime:
    def __init__(self, args, name, timeout=0):
        self.log = args.output / (name + ".jsonl")
        self.stream = self.log.open("x")
        self.process = subprocess.Popen([str(args.binary), "--interface", args.interface,
                                         "--timeout-ms", str(timeout)],
                                        stdout=self.stream, stderr=self.stream)
        self.start = time.monotonic()

    def ready(self):
        def check():
            if self.process.poll() is not None:
                raise AssertionError(self.log.read_text())
            return any(row.get("event") == "started" for row in records(self.log))
        wait_for(check)

    def stop(self, signum=signal.SIGTERM):
        if self.process.poll() is None:
            self.process.send_signal(signum)
            try:
                self.process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
                raise AssertionError("ThreadX did not stop cleanly")
        self.stream.close()
        assert self.process.returncode == 0, self.log.read_text()
        assert records(self.log)[-1].get("event") == "stopped", self.log.read_text()


def direct_checks(args, bus, checks):
    runtime = Runtime(args, "direct")
    try:
        runtime.ready()
        frame(bus, 0)
        for status in range(256):
            bus.send(can.Message(arbitration_id=0x1F1, is_extended_id=False,
                                 data=bytes([status]) + bytes([0xFF]) * 7))
            frame(bus, (status >> 1) & 3)
        checks.append({"id": "socketcan-all-256-status-values", "status": "passed"})
        # Receive filter and application validation must not actuate malformed input.
        for message in (
            can.Message(arbitration_id=0x1F1, data=[6], is_extended_id=False),
            can.Message(arbitration_id=0x1F1, data=bytes([6]) + bytes(7), is_extended_id=True),
            can.Message(arbitration_id=0x1F1, dlc=8, is_remote_frame=True, is_extended_id=False),
            can.Message(arbitration_id=0x1F2, data=bytes(8), is_extended_id=False),
        ):
            bus.send(message)
        assert bus.recv(timeout=0.25) is None, "malformed input produced a light frame"
        checks.append({"id": "malformed-and-unrelated-input-ignored", "status": "passed"})
        # Default behavior must hold state for the change-driven Python VCU.
        assert bus.recv(timeout=1.1) is None, "default mode cleared held lights"
        heartbeats = [row for row in records(runtime.log) if row.get("event") == "heartbeat"]
        assert heartbeats and all(not row["stale"] for row in heartbeats)
        assert len(heartbeats) <= time.monotonic() - runtime.start + 2, "timer advances faster than wall clock"
        checks.append({"id": "held-state-and-threadx-heartbeat", "status": "passed"})
        runtime.stop(signal.SIGINT)
        frame(bus, 0)
        checks.append({"id": "sigint-clean-shutdown-lights-off", "status": "passed"})
    finally:
        if runtime.process.poll() is None:
            runtime.stop()

    runtime = Runtime(args, "timeout", timeout=200)
    try:
        runtime.ready()
        frame(bus, 0)
        bus.send(can.Message(arbitration_id=0x1F1, is_extended_id=False, data=bytes([6]) + bytes(7)))
        frame(bus, 3)
        started = time.monotonic()
        frame(bus, 0)
        elapsed = time.monotonic() - started
        assert 0.12 <= elapsed < 2, elapsed
        assert any(row.get("event") == "input_timeout" for row in records(runtime.log))
        checks.append({"id": "optional-input-timeout", "status": "passed", "observed_seconds": elapsed})
        bus.send(can.Message(arbitration_id=0x1F1, is_extended_id=False, data=bytes([6]) + bytes(7)))
        frame(bus, 3)
        checks.append({"id": "input-recovery", "status": "passed"})
        runtime.stop(signal.SIGTERM)
        frame(bus, 0)
        checks.append({"id": "sigterm-clean-shutdown-lights-off", "status": "passed"})
    finally:
        if runtime.process.poll() is None:
            runtime.stop()


def bridge_checks(args, bus, checks):
    import zenoh
    # An isolated local peer provides an actual Zenoh endpoint without using 7447.
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        endpoint = "tcp/127.0.0.1:" + str(7447 if args.carla_host else reservation.getsockname()[1])
    conf = zenoh.Config()
    conf.insert_json5("mode", '"peer"')
    conf.insert_json5("listen/endpoints", json.dumps([endpoint]))
    conf.insert_json5("scouting/multicast/enabled", "false")
    session = zenoh.open(conf)
    import queue
    incoming = queue.Queue()
    latest = {}
    def observed(sample):
        incoming.put((str(sample.key_expr), sample.payload.to_string()))
    subscriber = session.declare_subscriber("vehicle/lights/**", observed)
    config = args.output / "bridge.json"
    config.write_text(json.dumps(profile(args.interface, endpoint), indent=2) + "\n")
    bridge_log = args.output / "bridge.log"
    stream = bridge_log.open("x")
    bridge = subprocess.Popen([sys.executable, str(args.bridge_source), str(config)],
                              stdout=stream, stderr=stream)
    runtime = None
    actor = communicator = controller = world = None
    packets = []
    light_observations = []
    def state(reverse, brake):
        while True:
            try:
                key, value = incoming.get_nowait()
            except queue.Empty:
                break
            latest[key] = value
        return (latest.get("vehicle/lights/reverse_lights_cmd") == str(reverse).lower()
                and latest.get("vehicle/lights/brake_lights_cmd") == str(brake).lower())
    try:
        def ready():
            assert bridge.poll() is None, bridge_log.read_text()
            return "Bridge init complete" in bridge_log.read_text()
        wait_for(ready, 15)
        if args.carla_host:
            import importlib.util
            import carla
            spec = importlib.util.spec_from_file_location("threadx_virtual_vehicle", args.vehicle_module)
            vehicle_module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = vehicle_module
            spec.loader.exec_module(vehicle_module)
            vehicle_module.carla = carla
            assert vehicle_module.SignalDefinitions.load_from_file(str(args.signals))
            client = carla.Client(args.carla_host, args.carla_port)
            client.set_timeout(10)
            assert client.get_server_version().startswith("0.9.15"), client.get_server_version()
            world = client.get_world()
            blueprint = world.get_blueprint_library().find("vehicle.tesla.model3")
            blueprint.set_attribute("role_name", "threadx-zonal-lights-test")
            for transform in world.get_map().get_spawn_points():
                actor = world.try_spawn_actor(blueprint, transform)
                if actor:
                    break
            assert actor is not None, "no free CARLA spawn point"
            communicator = vehicle_module.ZenohCommunicator("127.0.0.1")
            controller = vehicle_module.VehicleController(actor, communicator)
        runtime = Runtime(args, "bridge-threadx")
        runtime.ready()
        frame(bus, 0)
        wait_for(lambda: state(False, False))
        for reverse, brake in ((True, False), (True, True), (False, True), (False, False)):
            wanted = int(reverse) | (int(brake) << 1)
            status = {"vcu_cc_engage_sts": False, "vcu_reverse_sts": reverse, "vcu_brake_sts": brake}
            session.put("vcu/control/status", json.dumps(status))
            request = wait_for(lambda: bus.recv(timeout=0.1))
            assert request.arbitration_id == 0x1F1 and bytes(request.data) == bytes([wanted << 1]) + bytes(7), request
            response = frame(bus, wanted)
            wait_for(lambda: state(reverse, brake))
            if controller:
                wait_for(lambda: (communicator.bcm_reverse_lights_cmd == reverse
                                  and communicator.bcm_brake_lights_cmd == brake))
                controller.update()
                expected = (int(carla.VehicleLightState.Reverse) if reverse else 0) | (
                    int(carla.VehicleLightState.Brake) if brake else 0)
                wait_for(lambda: int(actor.get_light_state()) == expected)
                light_observations.append({"actor_id": actor.id, "reverse": reverse, "brake": brake,
                                           "observed_light_mask": int(actor.get_light_state()),
                                           "expected_light_mask": expected})
            packets.append({"request_id": request.arbitration_id, "request_data": bytes(request.data).hex(),
                            "response_id": response.arbitration_id, "response_data": bytes(response.data).hex(),
                            "reverse": reverse, "brake": brake})
        checks.append({"id": "zenoh-bridge-threadx-roundtrip-four-light-states", "status": "passed"})
        if controller:
            checks.append({"id": "actual-carla-actor-four-light-states", "status": "passed"})
            (args.output / "carla-lights.json").write_text(json.dumps(light_observations, indent=2) + "\n")
        # Existing VCU sends individual text booleans, rather than aggregate JSON.
        session.put("vcu/control/brake_sts", "true")
        request = wait_for(lambda: bus.recv(timeout=0.1))
        assert request.arbitration_id == 0x1F1 and request.data[0] == 4
        frame(bus, 2)
        wait_for(lambda: state(False, True))
        checks.append({"id": "individual-vcu-boolean-topic", "status": "passed"})
        runtime.stop()
        frame(bus, 0)
        wait_for(lambda: state(False, False))
        checks.append({"id": "shutdown-lights-off-through-bridge", "status": "passed"})
        (args.output / "bridge-packets.json").write_text(json.dumps(packets, indent=2) + "\n")
    finally:
        if runtime and runtime.process.poll() is None:
            runtime.stop()
        if bridge.poll() is None:
            bridge.terminate()
            try:
                bridge.wait(timeout=5)
            except subprocess.TimeoutExpired:
                bridge.kill(); bridge.wait()
        stream.close()
        subscriber.undeclare()
        session.close()
        if communicator:
            communicator.close()
        if actor:
            removed = actor.destroy()
            checks.append({"id": "owned-carla-actor-removed", "status": "passed" if removed else "failed"})
            assert removed, "owned CARLA actor cleanup failed"
        assert bridge.returncode == 0, bridge_log.read_text()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=ROOT / "build/threadx-zonal-lights")
    parser.add_argument("--interface", default="vcan0")
    parser.add_argument("--create-interface", action="store_true")
    parser.add_argument("--bridge-source", type=Path)
    parser.add_argument("--carla-host", help="Optional existing CARLA 0.9.15 server; requires the bridge")
    parser.add_argument("--carla-port", type=int, default=2000)
    parser.add_argument("--vehicle-module", type=Path)
    parser.add_argument("--signals", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.carla_host and not (args.bridge_source and args.vehicle_module and args.signals):
        parser.error("CARLA mode requires --bridge-source, --vehicle-module and --signals")
    args.binary = args.binary.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    checks = []
    receipt = {"schema_version": 1, "mode": "ThreadX Linux simulation with real SocketCAN",
               "simulation": True, "physical_can_hardware": False,
               "carla_requested": bool(args.carla_host), "carla_server_owned": False,
               "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(), "checks": checks}
    created = False
    bus = None
    try:
        if args.create_interface:
            subprocess.run(["ip", "link", "add", "dev", args.interface, "type", "vcan"], check=True)
            created = True
            subprocess.run(["ip", "link", "set", "dev", args.interface, "up"], check=True)
        bus = can.Bus(interface="socketcan", channel=args.interface)
        receipt["binary_identity"] = subprocess.check_output([str(args.binary), "--version"], text=True).strip()
        direct_checks(args, bus, checks)
        if args.bridge_source:
            receipt["bridge_source_sha256"] = hashlib.sha256(args.bridge_source.read_bytes()).hexdigest()
            bridge_checks(args, bus, checks)
        receipt["status"] = "passed"
    except Exception as exc:
        receipt["status"] = "failed"
        receipt["error"] = str(exc)
        import traceback
        traceback.print_exc()
    finally:
        if bus:
            bus.shutdown()
        if created:
            result = subprocess.run(["ip", "link", "delete", "dev", args.interface], capture_output=True)
            checks.append({"id": "owned-vcan-interface-removed", "status": "passed" if result.returncode == 0 else "failed"})
            if result.returncode:
                receipt["status"] = "failed"
        (args.output / "results.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "checks": len(checks), "output": str(args.output)}))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
