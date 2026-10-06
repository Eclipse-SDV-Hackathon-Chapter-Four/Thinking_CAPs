"""Integration tests: the bridge against simulated SLCAN ECUs on Linux pseudo-terminals.

Each FakeEcu owns a pty pair and behaves like a Lawicell device: it answers
C/S/O/V, acknowledges frames with z/Z and records everything the host wrote.
The CAN side uses python-can's in-process "virtual" bus (or udp_multicast for
the echo-suppression case), so the tests need no root and no hardware.
"""
import os
import select
import sys
import threading
import time
import uuid
from pathlib import Path

import can
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import slcan
from serial2can_bridge import Serial2CanBridge


def wait_for(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.01)
    raise AssertionError("condition not reached")


class FakeEcu:
    """A Lawicell SLCAN device on a pty, exposed through a stable symlink."""

    def __init__(self, link: Path):
        self.link = link
        self.commands, self.frames = [], []
        self.open = False
        self._plug()

    def _plug(self):
        self.master, self.slave = os.openpty()
        if self.link.is_symlink():
            self.link.unlink()
        self.link.symlink_to(os.ttyname(self.slave))
        self._alive = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def unplug(self):
        if not self._alive:
            return
        self._alive = False
        self._thread.join(timeout=2)  # stop reading first: a blocked read keeps the pty alive
        self.link.unlink(missing_ok=True)
        os.close(self.master)
        os.close(self.slave)

    def replug(self):
        self.commands.clear()
        self._plug()

    def send_frame(self, message: can.Message):
        os.write(self.master, slcan.encode(message))

    def _reply(self, data: bytes):
        os.write(self.master, data)

    def _serve(self):
        splitter = slcan.LineSplitter()
        while self._alive:
            if not select.select([self.master], [], [], 0.05)[0]:
                continue
            try:
                data = os.read(self.master, 256)
            except OSError:
                return
            for token in splitter.feed(data):
                if token and token != slcan.BELL:
                    self._respond(token)

    def _respond(self, token: bytes):
        """Lawicell behaviour for one host line."""
        if token[:1] in b"tTrR":
            if self.open:
                self.frames.append(slcan.decode(token))
            ack = (b"Z\r" if token[:1] in b"TR" else b"z\r") if self.open else slcan.BELL
            self._reply(ack)
            return
        self.commands.append(token.decode())
        if token in (b"O", b"C"):
            self.open = token == b"O"
            self._reply(b"\r")
        elif token == b"V":
            self._reply(b"V1010\r")
        elif token[:1] in b"Ss":
            self._reply(b"\a" if self.open else b"\r")
        else:
            self._reply(b"\a")


@pytest.fixture
def channel():
    return f"serial2can-test-{uuid.uuid4().hex[:8]}"


def start_bridge(config):
    bridge = Serial2CanBridge(config)
    thread = threading.Thread(target=bridge.run, daemon=True)
    thread.start()
    return bridge, thread


def stop_bridge(bridge, thread):
    bridge.stopping.set()
    thread.join(timeout=5)
    assert not thread.is_alive()


def port(name, link, **extra):
    return dict({"name": name, "device": str(link), "reconnect_s": 0.2}, **extra)


def recv_id(bus, ident, timeout=3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = bus.recv(timeout=0.1)
        if message is not None and message.arbitration_id == ident:
            return message
    return None


def test_handshake_both_directions_filters_and_close(tmp_path, channel):
    ecu = FakeEcu(tmp_path / "ecu")
    tester = can.Bus(interface="virtual", channel=channel)
    bridge, thread = start_bridge({
        "can": {"interface": "virtual", "channel": channel},
        "serial_ports": [port("zonal", ecu.link, to_serial=[{"id": "0x1F1"}],
                              from_serial=[{"id": "0x1F4", "mask": "0x7FE"}])]})
    try:
        wait_for(lambda: bridge.links[0].connected.is_set())
        assert ecu.commands == ["C", "V", "S6", "O"] and bridge.links[0].version == "V1010"

        # CAN -> serial, with the to_serial filter.
        tester.send(can.Message(arbitration_id=0x300, data=bytes(8), is_extended_id=False))
        tester.send(can.Message(arbitration_id=0x1F1, data=bytes([6]) + bytes(7), is_extended_id=False))
        wait_for(lambda: ecu.frames)
        time.sleep(0.2)
        assert [f.arbitration_id for f in ecu.frames] == [0x1F1] and ecu.frames[0].data[0] == 6

        # Serial -> CAN, with the from_serial filter (0x1F4/0x1F5 only).
        ecu.send_frame(can.Message(arbitration_id=0x123, data=bytes(8), is_extended_id=False))
        ecu.send_frame(can.Message(arbitration_id=0x1F4, data=bytes([3]) + bytes(7), is_extended_id=False))
        received = recv_id(tester, 0x1F4)
        assert received is not None and received.data[0] == 3
        stats = bridge.links[0].stats
        assert stats["filtered_in"] == 1 and stats["filtered_out"] == 1 and stats["acks"] == 1
    finally:
        stop_bridge(bridge, thread)
        tester.shutdown()
    wait_for(lambda: ecu.commands[-1:] == ["C"])  # ECU told to close (fail-safe) on shutdown
    assert not ecu.open
    ecu.unplug()


def test_serial_to_serial_fan_out_and_extended_remote(tmp_path, channel):
    first, second = FakeEcu(tmp_path / "a"), FakeEcu(tmp_path / "b")
    tester = can.Bus(interface="virtual", channel=channel)
    bridge, thread = start_bridge({
        "can": {"interface": "virtual", "channel": channel},
        "serial_ports": [port("a", first.link), port("b", second.link)]})
    try:
        wait_for(lambda: all(link.connected.is_set() for link in bridge.links))
        extended = can.Message(arbitration_id=0x18DAF110, data=b"\x02\x10\x03", is_extended_id=True)
        first.send_frame(extended)
        assert recv_id(tester, 0x18DAF110).is_extended_id
        wait_for(lambda: second.frames)
        assert second.frames[0].equals(extended, timestamp_delta=None) and not first.frames
        remote = can.Message(arbitration_id=0x1F1, is_remote_frame=True, dlc=8, is_extended_id=False)
        tester.send(remote)
        wait_for(lambda: len(first.frames) == 1 and len(second.frames) == 2)
        assert first.frames[0].is_remote_frame and first.frames[0].dlc == 8
    finally:
        stop_bridge(bridge, thread)
        tester.shutdown()
        first.unplug()
        second.unplug()


def test_reconnects_after_unplug(tmp_path, channel):
    ecu = FakeEcu(tmp_path / "ecu")
    tester = can.Bus(interface="virtual", channel=channel)
    bridge, thread = start_bridge({"can": {"interface": "virtual", "channel": channel},
                                   "serial_ports": [port("zonal", ecu.link)]})
    link = bridge.links[0]
    try:
        wait_for(link.connected.is_set)
        ecu.unplug()
        wait_for(lambda: not link.connected.is_set())
        tester.send(can.Message(arbitration_id=0x1F1, data=bytes(8), is_extended_id=False))
        wait_for(lambda: link.stats["dropped_offline"] >= 1)
        ecu.replug()
        wait_for(lambda: link.stats["connects"] == 2)
        assert ecu.commands == ["C", "V", "S6", "O"] and link.stats["disconnects"] == 1
        tester.send(can.Message(arbitration_id=0x1F1, data=bytes([2]) + bytes(7), is_extended_id=False))
        wait_for(lambda: ecu.frames and ecu.frames[-1].data[0] == 2)
    finally:
        stop_bridge(bridge, thread)
        tester.shutdown()
        ecu.unplug()


def test_udp_multicast_echo_is_not_returned_to_the_ecu(tmp_path):
    # A private UDP port: Linux delivers multicast to every socket bound to the same port,
    # whatever group it joined, and 239.74.163.2:43113 may carry a live X-Verse bus here.
    group, udp_port = "239.74.163.2", 43200 + uuid.uuid4().int % 2000
    ecu = FakeEcu(tmp_path / "ecu")
    tester = can.Bus(interface="udp_multicast", channel=group, port=udp_port, fd=False)
    bridge, thread = start_bridge({"can": {"interface": "udp_multicast", "channel": group, "port": udp_port},
                                   "serial_ports": [port("zonal", ecu.link)]})
    try:
        wait_for(bridge.links[0].connected.is_set)
        ecu.send_frame(can.Message(arbitration_id=0x1F4, data=bytes([1]) + bytes(7), is_extended_id=False))
        assert recv_id(tester, 0x1F4) is not None
        wait_for(lambda: bridge.stats["echo_suppressed"] == 1)
        time.sleep(0.3)
        assert ecu.frames == []  # its own frame did not loop back
        tester.send(can.Message(arbitration_id=0x1F1, data=bytes([4]) + bytes(7), is_extended_id=False))
        wait_for(lambda: ecu.frames)
        assert ecu.frames[0].arbitration_id == 0x1F1
    finally:
        stop_bridge(bridge, thread)
        tester.shutdown()
        ecu.unplug()
