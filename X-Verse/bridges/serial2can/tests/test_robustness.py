"""Integration tests of error handling: unusable devices, late devices, CAN and serial
failures, unencodable frames and the command-line process lifecycle."""
import json
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

import can
import serial

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_bridge import FakeEcu, port, start_bridge, stop_bridge, wait_for

ROOT = Path(__file__).resolve().parents[1]


def channel():
    return f"serial2can-robust-{uuid.uuid4().hex[:8]}"


def test_unusable_device_is_retried_and_late_glob_device_connects(tmp_path):
    not_a_tty = tmp_path / "plain-file"
    not_a_tty.write_text("")
    late = tmp_path / "late-ecu"
    bridge, thread = start_bridge({"can": {"interface": "virtual", "channel": channel()},
                                   "serial_ports": [port("bad", not_a_tty),
                                                    port("late", tmp_path / "late-*")]})
    try:
        time.sleep(0.6)
        assert not any(link.connected.is_set() for link in bridge.links)
        ecu = FakeEcu(late)  # appears after start; found through the glob
        wait_for(bridge.links[1].connected.is_set)
        assert not bridge.links[0].connected.is_set()
    finally:
        stop_bridge(bridge, thread)
        ecu.unplug()


def test_can_send_error_is_counted_and_fan_out_continues(tmp_path):
    first, second = FakeEcu(tmp_path / "a"), FakeEcu(tmp_path / "b")
    bridge, thread = start_bridge({"can": {"interface": "virtual", "channel": channel()},
                                   "serial_ports": [port("a", first.link), port("b", second.link)]})

    def failing_send(message, timeout=None):
        raise can.CanOperationError("bus off")

    try:
        wait_for(lambda: all(link.connected.is_set() for link in bridge.links))
        bridge.bus.send = failing_send
        first.send_frame(can.Message(arbitration_id=0x1F4, data=bytes(8), is_extended_id=False))
        wait_for(lambda: bridge.stats["can_tx_errors"] == 1)
        wait_for(lambda: second.frames)
    finally:
        stop_bridge(bridge, thread)
        first.unplug()
        second.unplug()


def test_serial_write_failure_triggers_reconnect(tmp_path):
    ecu = FakeEcu(tmp_path / "ecu")
    tester_channel = channel()
    tester = can.Bus(interface="virtual", channel=tester_channel)
    bridge, thread = start_bridge({"can": {"interface": "virtual", "channel": tester_channel},
                                   "serial_ports": [port("zonal", ecu.link)]})
    link = bridge.links[0]

    def broken_write(data):
        raise serial.SerialException("write failed")

    try:
        wait_for(link.connected.is_set)
        link._serial.write = broken_write
        tester.send(can.Message(arbitration_id=0x1F1, data=bytes(8), is_extended_id=False))
        wait_for(lambda: link.stats["disconnects"] == 1)
        wait_for(lambda: link.stats["connects"] == 2)  # fresh port object, handshake repeated
        tester.send(can.Message(arbitration_id=0x1F1, data=bytes([4]) + bytes(7), is_extended_id=False))
        wait_for(lambda: ecu.frames and ecu.frames[-1].data[0] == 4)
    finally:
        stop_bridge(bridge, thread)
        tester.shutdown()
        ecu.unplug()


def test_unencodable_frames_are_not_written(tmp_path):
    ecu = FakeEcu(tmp_path / "ecu")
    bridge, thread = start_bridge({"can": {"interface": "virtual", "channel": channel()},
                                   "serial_ports": [port("zonal", ecu.link)]})
    link = bridge.links[0]
    try:
        wait_for(link.connected.is_set)
        link.enqueue(can.Message(arbitration_id=0x1F1, is_fd=True, data=bytes(12), is_extended_id=False))
        wait_for(lambda: link.stats["filtered_out"] == 1)
        bridge._dispatch(can.Message(arbitration_id=0x1F1, is_error_frame=True))
        time.sleep(0.2)
        assert ecu.frames == [] and bridge.stats["can_rx"] == 0
    finally:
        stop_bridge(bridge, thread)
        ecu.unplug()


def test_cli_process_runs_and_stops_cleanly_on_sigterm(tmp_path):
    ecu = FakeEcu(tmp_path / "ecu")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"can": {"interface": "virtual", "channel": channel()},
                                  "serial_ports": [{"name": "zonal", "device": "/dev/null-not-used"}],
                                  "stats_interval_s": 0.3}))
    # The report generator sets SERIAL2CAN_COVERAGE so the child process is measured too.
    coverage = ["-m", "coverage", "run", "--parallel-mode", "--branch", f"--source={ROOT / 'src'}"]
    runner = coverage if os.environ.get("SERIAL2CAN_COVERAGE") else []
    process = subprocess.Popen([sys.executable, "-W", "ignore", *runner, str(ROOT / "src" / "serial2can_bridge.py"),
                                str(config), "--device", f"zonal={ecu.link}"],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        wait_for(lambda: ecu.open, 10)
        time.sleep(0.5)
        process.send_signal(signal.SIGTERM)
        output = process.communicate(timeout=10)[0]
        assert process.returncode == 0
        assert "channel open" in output and '"connected":true' in output
        assert "sent close (C) to ECU" in output and "Serial2CAN bridge stopped" in output
        wait_for(lambda: not ecu.open)
    finally:
        if process.poll() is None:
            process.kill()
        ecu.unplug()

