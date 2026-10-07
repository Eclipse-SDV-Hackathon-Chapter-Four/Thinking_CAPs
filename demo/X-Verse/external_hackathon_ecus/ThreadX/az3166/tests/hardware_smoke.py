#!/usr/bin/env python3
"""Exercise the ThreadX zonal controller on a physical AZ3166 over SLCAN/UART.

Checks the raw Lawicell dialogue, then uses python-can's "slcan" interface (the
driver the X-Verse Zenoh2CAN bridge loads) for the lighting contract, ThreadX
heartbeat timing, held state and the close fail-safe. With --bridge-source it
also runs the actual, unchanged bridge between an isolated Zenoh peer and the
board. The serial port is exclusive: stop any other user of it first.
"""
import argparse
import hashlib
import json
import queue
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

import can
import serial

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from configure_bridge import profile  # noqa: E402

STATUS_ID, LIGHTS_ID, DIAG_ID = 0x1F1, 0x1F4, 0x1F5
BITRATE = 500000


def wait_for(predicate, timeout=8.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.01)
    raise AssertionError(f"timed out after {timeout}s")


def diag(message):
    data = bytes(message.data)
    return {"reverse": bool(data[0] & 1), "brake": bool(data[0] & 2), "stale": bool(data[0] & 4),
            "losses": bool(data[0] & 8), "oled": bool(data[0] & 16),
            "received": data[1] | data[2] << 8, "rejected": data[3], "line_errors": data[4],
            "uptime_s": data[5] | data[6] << 8 | data[7] << 16}


class Board:
    """python-can slcan bus that sorts lighting commands from diagnostics."""

    def __init__(self, port, log):
        self.bus = can.Bus(interface="slcan", channel=port, bitrate=BITRATE, sleep_after_open=0.5)
        self.log = log

    def recv(self, timeout):
        message = self.bus.recv(timeout=timeout)
        if message is not None:
            self.log.append({"t": round(time.monotonic(), 4), "id": message.arbitration_id,
                             "ext": message.is_extended_id, "data": bytes(message.data).hex()})
        return message

    def next(self, can_id, timeout=2.0):
        deadline = time.monotonic() + timeout
        while (remaining := deadline - time.monotonic()) > 0:
            message = self.recv(remaining)
            if message is not None and message.arbitration_id == can_id and not message.is_extended_id:
                return message
        return None

    def silent(self, can_id, duration):
        deadline = time.monotonic() + duration
        while (remaining := deadline - time.monotonic()) > 0:
            message = self.recv(remaining)
            if message is not None and message.arbitration_id == can_id and not message.is_extended_id:
                return False
        return True

    def send(self, can_id, data, **kwargs):
        self.bus.send(can.Message(arbitration_id=can_id, data=data, is_extended_id=False, **kwargs))

    def drain(self):
        while self.recv(0.05) is not None:
            pass

    def close(self):
        self.bus.shutdown()


def raw_checks(port, checks):
    with serial.Serial(port, 115200, timeout=0.5) as link:
        def ask(line):
            link.reset_input_buffer()
            link.write(line + b"\r")
            reply = b""
            deadline = time.monotonic() + 1
            while time.monotonic() < deadline and not reply.endswith((b"\r", b"\a")):
                reply += link.read(1)
            return reply
        assert ask(b"C") == b"\r"
        assert ask(b"V") == b"V1010\r"
        assert ask(b"N") == b"NAZ31\r"
        assert ask(b"F") == b"\a", "status is only available while open"
        assert ask(b"t1F180600000000000000") == b"\a", "frames are refused while closed"
        assert ask(b"S6") == b"\r" and ask(b"Z0") == b"\r"
        for bad in (b"t1F1806", b"t8001", b"S9", b"Z1", b"x", b"t" + b"0" * 40):
            assert ask(bad) == b"\a", bad
        assert ask(b"O") == b"\r"
        assert ask(b"S6") == b"\a", "bitrate cannot change while open"
        assert ask(b"F") == b"F00\r"
        assert ask(b"C") == b"\r"
    checks.append({"id": "raw-lawicell-dialogue", "status": "passed"})


def direct_checks(port, checks, log, output):
    board = Board(port, log)
    try:
        first = board.next(LIGHTS_ID)
        assert first is not None and bytes(first.data) == bytes(8), first
        checks.append({"id": "open-reports-current-command", "status": "passed"})
        status = board.next(DIAG_ID, 2.5)
        assert status is not None, "no ThreadX heartbeat"
        baseline = diag(status)

        latencies = []
        for value in range(256):
            board.send(STATUS_ID, bytes([value]) + b"\xff" * 7)
            sent = time.monotonic()
            reply = board.next(LIGHTS_ID)
            assert reply is not None, f"no command for status {value:#04x}"
            latencies.append((time.monotonic() - sent) * 1000)
            assert bytes(reply.data) == bytes([(value >> 1) & 3]) + bytes(7), (value, reply)
        checks.append({"id": "all-256-status-bytes", "status": "passed",
                       "round_trip_ms": {"median": round(statistics.median(latencies), 2),
                                         "p95": round(sorted(latencies)[int(len(latencies) * 0.95)], 2),
                                         "max": round(max(latencies), 2)}})

        rejected = [("unrelated-0x1F0", 0x1F0, 8, {}), ("unrelated-0x1F2", 0x1F2, 8, {}),
                    ("own-output-0x1F4", LIGHTS_ID, 8, {})]
        rejected += [(f"dlc-{dlc}", STATUS_ID, dlc, {}) for dlc in range(8)]
        rejected += [("rtr", STATUS_ID, 8, {"is_remote_frame": True})]
        for name, can_id, dlc, kwargs in rejected:
            board.send(can_id, b"\x06" * dlc if not kwargs else None, dlc=dlc, **kwargs)
            assert board.silent(LIGHTS_ID, 0.3), f"{name} caused actuation"
        board.bus.send(can.Message(arbitration_id=STATUS_ID, data=b"\x06" + bytes(7), is_extended_id=True))
        assert board.silent(LIGHTS_ID, 0.3), "extended 0x1F1 caused actuation"
        status = diag(board.next(DIAG_ID, 2.5))
        assert (status["rejected"] - baseline["rejected"]) % 256 == len(rejected) + 1, (baseline, status)
        checks.append({"id": "malformed-and-unrelated-frames-ignored", "status": "passed",
                       "cases": [name for name, *_ in rejected] + ["extended-id"]})

        board.send(STATUS_ID, b"\x06" + bytes(7))
        assert bytes(board.next(LIGHTS_ID).data)[0] == 3
        beats = []
        deadline = time.monotonic() + 5.5
        while time.monotonic() < deadline:
            message = board.recv(deadline - time.monotonic())
            assert message is None or message.arbitration_id != LIGHTS_ID, "held state was re-sent"
            if message is not None and message.arbitration_id == DIAG_ID:
                beats.append((time.monotonic(), diag(message)))
        assert len(beats) >= 4, beats
        intervals = [b[0] - a[0] for a, b in zip(beats, beats[1:])]
        uptimes = [b[1]["uptime_s"] - a[1]["uptime_s"] for a, b in zip(beats, beats[1:])]
        assert all(0.8 <= gap <= 1.2 for gap in intervals), intervals
        assert all(step == 1 for step in uptimes), uptimes
        assert all(beat["brake"] and beat["reverse"] and not beat["stale"] for _, beat in beats)
        checks.append({"id": "threadx-heartbeat-and-held-state", "status": "passed",
                       "intervals_s": [round(gap, 3) for gap in intervals]})
        (output / "diagnostics.json").write_text(json.dumps([b for _, b in beats], indent=2) + "\n")
        checks.append({"id": "oled-status-display", "status": "passed" if beats[-1][1]["oled"] else "failed"})
        checks.append({"id": "no-transport-losses", "status": "failed" if beats[-1][1]["losses"] else "passed"})
    finally:
        board.close()  # python-can sends "C": the board must fail safe

    board = Board(port, log)
    try:
        first = board.next(LIGHTS_ID)
        assert first is not None and bytes(first.data) == bytes(8), "lamps not off after close"
        status = diag(board.next(DIAG_ID, 2.5))
        assert not (status["brake"] or status["reverse"]), status
        checks.append({"id": "close-turns-lamps-off", "status": "passed"})
    finally:
        board.close()


def bridge_checks(args, checks, output):
    import zenoh
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        endpoint = "tcp/127.0.0.1:" + str(reservation.getsockname()[1])
    conf = zenoh.Config()
    conf.insert_json5("mode", '"peer"')
    conf.insert_json5("listen/endpoints", json.dumps([endpoint]))
    conf.insert_json5("scouting/multicast/enabled", "false")
    session = zenoh.open(conf)
    incoming, latest, samples = queue.Queue(), {}, []
    subscriber = session.declare_subscriber(
        "vehicle/lights/**", lambda sample: incoming.put((str(sample.key_expr), sample.payload.to_string())))

    def state(reverse, brake):
        while not incoming.empty():
            key, value = incoming.get_nowait()
            latest[key] = value
            samples.append({"t": round(time.monotonic(), 4), "key": key, "value": value})
        return (latest.get("vehicle/lights/reverse_lights_cmd") == str(reverse).lower()
                and latest.get("vehicle/lights/brake_lights_cmd") == str(brake).lower())

    config = output / "bridge.json"
    config.write_text(json.dumps(profile(args.port, endpoint, "slcan", BITRATE), indent=2) + "\n")
    bridge_log = output / "bridge.log"
    stream = bridge_log.open("x")
    bridge = subprocess.Popen([sys.executable, str(args.bridge_source), str(config)], stdout=stream, stderr=stream)
    timings = []
    try:
        def ready():
            assert bridge.poll() is None, bridge_log.read_text()
            return "Bridge init complete" in bridge_log.read_text()
        wait_for(ready, 20)
        wait_for(lambda: state(False, False))  # board reports its command when the bridge opens it
        for reverse, brake in ((True, False), (True, True), (False, True), (False, False)):
            status = {"vcu_cc_engage_sts": False, "vcu_reverse_sts": reverse, "vcu_brake_sts": brake}
            start = time.monotonic()
            session.put("vcu/control/status", json.dumps(status))
            wait_for(lambda: state(reverse, brake))
            timings.append({"reverse": reverse, "brake": brake,
                            "zenoh_round_trip_ms": round((time.monotonic() - start) * 1000, 1)})
        checks.append({"id": "zenoh-bridge-az3166-roundtrip-four-light-states", "status": "passed",
                       "timings": timings})
        session.put("vcu/control/brake_sts", "true")  # existing VCU's individual boolean topic
        wait_for(lambda: state(False, True))
        checks.append({"id": "individual-vcu-boolean-topic", "status": "passed"})
    finally:
        if bridge.poll() is None:
            bridge.terminate()
            try:
                bridge.wait(timeout=10)
            except subprocess.TimeoutExpired:
                bridge.kill()
                bridge.wait()
        stream.close()
        subscriber.undeclare()
        session.close()
        (output / "zenoh-samples.json").write_text(json.dumps(samples, indent=2) + "\n")
    assert bridge.returncode == 0, bridge_log.read_text()
    checks.append({"id": "bridge-clean-shutdown", "status": "passed"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/ttyACM1", help="AZ3166 ST-LINK virtual COM port")
    parser.add_argument("--firmware", type=Path, help="flashed .bin, hashed into the results")
    parser.add_argument("--bridge-source", type=Path, help="Zenoh2CAN bridge.py for the Zenoh round trip")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    checks, log = [], []
    receipt = {"component": "threadx-zonal-lights-az3166", "port": args.port, "python_can": can.__version__,
               "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "checks": checks}
    if args.firmware:
        receipt["firmware_sha256"] = hashlib.sha256(args.firmware.read_bytes()).hexdigest()
    if args.bridge_source:
        receipt["bridge_source_sha256"] = hashlib.sha256(args.bridge_source.read_bytes()).hexdigest()
    try:
        raw_checks(args.port, checks)
        direct_checks(args.port, checks, log, args.output)
        if args.bridge_source:
            bridge_checks(args, checks, args.output)
        failed = [check["id"] for check in checks if check["status"] != "passed"]
        receipt["status"] = "failed" if failed else "passed"
        if failed:
            receipt["failed"] = failed
    except BaseException as error:
        receipt["status"] = "failed"
        receipt["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        (args.output / "slcan-frames.json").write_text(json.dumps(log) + "\n")
        (args.output / "results.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"status": receipt.get("status"), "checks": len(checks), "output": str(args.output)}))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
