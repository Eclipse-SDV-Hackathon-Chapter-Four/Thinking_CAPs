#!/usr/bin/env python3
"""Hardware check: Serial2CAN bridge with a physical SLCAN ECU (AZ3166 ThreadX).

Starts the bridge as a separate process with the given configuration and
acts as another CAN node on the same bus. It checks:

- the ECU's state report after the bridge opens the channel
- all 256 VCU status bytes (0x1F1) against the light command (0x1F4), with latency
- that the 1 s diagnostic heartbeat (0x1F5) crosses the bridge
- that filtered IDs are not forwarded
- that stopping the bridge (SIGTERM) closes the ECU channel, so the ECU
  reports lamps off when reopened

The serial port must be free: stop other users first.
"""
import argparse
import itertools
import json
import signal
import statistics
import subprocess
import sys
import time
from pathlib import Path

import can

HERE = Path(__file__).resolve().parents[1]


def recv(bus, ident, timeout):
    deadline = time.monotonic() + timeout
    while (left := deadline - time.monotonic()) > 0:
        message = bus.recv(timeout=left)
        if message is not None and message.arbitration_id == ident:
            return message
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=HERE / "config" / "az3166-udp-multicast.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    config = json.loads(args.config.read_text())
    can_config = dict(config["can"])
    interface, channel = can_config.pop("interface"), can_config.pop("channel")
    tester = can.Bus(interface=interface, channel=channel, **({"fd": False} if interface == "udp_multicast" else {}))
    log = (args.output / "bridge.log").open("w")
    bridge = subprocess.Popen([sys.executable, "-W", "ignore", str(HERE / "src" / "serial2can_bridge.py"),
                               str(args.config), "--log-level", "INFO"], stdout=log, stderr=log)
    checks, receipt = [], {"config": str(args.config), "bus": f"{interface}:{channel}",
                           "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    receipt["checks"] = checks
    try:
        first = recv(tester, 0x1F4, 15)
        assert first is not None and bytes(first.data) == bytes(8), f"no all-off state report: {first}"
        checks.append({"id": "ecu-state-report-on-open", "status": "passed"})

        latencies = []
        for status in range(256):
            tester.send(can.Message(arbitration_id=0x1F1, data=bytes([status]) + b"\xff" * 7, is_extended_id=False))
            start = time.monotonic()
            reply = recv(tester, 0x1F4, 2)
            assert reply is not None, f"no 0x1F4 for status {status:#04x}"
            latencies.append((time.monotonic() - start) * 1000)
            assert bytes(reply.data) == bytes([(status >> 1) & 3]) + bytes(7), (status, reply)
        checks.append({"id": "all-256-status-bytes-through-bridge", "status": "passed",
                       "round_trip_ms": {"median": round(statistics.median(latencies), 2),
                                         "p95": round(sorted(latencies)[242], 2), "max": round(max(latencies), 2)}})

        beats = []
        deadline = time.monotonic() + 3.5
        while time.monotonic() < deadline:
            beat = recv(tester, 0x1F5, deadline - time.monotonic())
            if beat is not None:
                beats.append(time.monotonic())
        gaps = [round(b - a, 3) for a, b in itertools.pairwise(beats)]
        assert len(beats) >= 3 and all(0.8 <= gap <= 1.2 for gap in gaps), gaps
        checks.append({"id": "diagnostic-heartbeat-forwarded", "status": "passed", "intervals_s": gaps})

        tester.send(can.Message(arbitration_id=0x1F0, data=bytes([6]) + bytes(7), is_extended_id=False))
        assert recv(tester, 0x1F4, 0.5) is None, "a filtered ID reached the ECU"
        checks.append({"id": "to-serial-filter", "status": "passed"})

        bridge.send_signal(signal.SIGTERM)
        assert bridge.wait(timeout=10) == 0
        log.flush()
        assert "sent close (C) to ECU" in (args.output / "bridge.log").read_text()
        checks.append({"id": "clean-shutdown-closes-ecu", "status": "passed"})

        # Reopen directly: the ECU must report lamps off after the bridge's close.
        port = config["serial_ports"][0]["device"]
        from glob import glob
        direct = can.Bus(interface="slcan", channel=sorted(glob(port))[0], bitrate=500000, sleep_after_open=0.5)
        try:
            state = recv(direct, 0x1F4, 3)
            assert state is not None and bytes(state.data) == bytes(8), state
        finally:
            direct.shutdown()
        checks.append({"id": "ecu-fail-safe-after-bridge-stop", "status": "passed"})
        receipt["status"] = "passed"
    except BaseException as error:
        receipt["status"] = "failed"
        receipt["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        if bridge.poll() is None:
            bridge.terminate()
            bridge.wait(timeout=10)
        log.close()
        tester.shutdown()
        (args.output / "results.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"status": receipt.get("status"), "checks": [c["id"] for c in checks],
                          "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
