#!/usr/bin/env python3
"""X-COM Serial2CAN bridge: serial (SLCAN) ECUs <-> an X-Verse CAN bus.

Each configured serial port is a CAN node that speaks the Lawicell SLCAN
protocol (for example the ThreadX zonal ECU on the MXChip AZ3166). The bridge
connects all of them to one python-can bus, typically SocketCAN ``vcan0`` or
the rootless ``udp_multicast`` bus, so every other X-Verse component (the
Zenoh2CAN bridge, candump, test tools) sees the ECUs as ordinary CAN nodes.

    serial ECU A --SLCAN--\\                    /-- Zenoh2CAN -- Zenoh -- X-Verse
                           >-- Serial2CAN -- CAN bus
    serial ECU B --SLCAN--/                    \\-- candump, testers, ...

Features: per-port ID filters in both directions, serial-to-serial
forwarding (the ports share one virtual bus), bounded per-port transmit
queues, automatic reconnect and Lawicell handshake on hot-plug, echo
suppression for buses that loop back own frames, and a final close (``C``)
to every ECU on shutdown so it can enter its safe state.

Usage:  python3 src/serial2can_bridge.py config/az3166-udp-multicast.json
"""
import argparse
import glob
import json
import logging
import queue
import signal
import sys
import threading
import time
from collections import deque
from pathlib import Path

import can
import serial

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slcan

logger = logging.getLogger("serial2can")

BITRATE_CODES = {10000: "S0", 20000: "S1", 50000: "S2", 100000: "S3", 125000: "S4",
                 250000: "S5", 500000: "S6", 800000: "S7", 1000000: "S8"}


def _int(value) -> int:
    return int(value, 0) if isinstance(value, str) else int(value)


class IdFilter:
    """Accepts a message if any entry matches ``(id & mask) == (filter_id & mask)``.

    Entries: ``{"id": "0x1F1", "mask": "0x7FF", "extended": false}``; ``mask``
    defaults to an exact match and ``extended`` to either format. A missing or
    empty list accepts everything.
    """

    def __init__(self, entries: list[dict] | None):
        self.entries = []
        for entry in entries or []:
            extended = entry.get("extended")
            mask = _int(entry.get("mask", 0x1FFFFFFF if extended else 0x7FF))
            self.entries.append((_int(entry["id"]) & mask, mask, extended))

    def matches(self, message: can.Message) -> bool:
        if not self.entries:
            return True
        return any((message.arbitration_id & mask) == ident and (extended is None or extended == message.is_extended_id)
                   for ident, mask, extended in self.entries)


class EchoGuard:
    """Drops the echo of frames this bridge sent, on buses that loop them back.

    Each sent frame cancels at most one identical received frame within the
    window, so genuine frames from other nodes are only affected if they are
    byte-identical and arrive while an echo is still outstanding.
    """

    def __init__(self, window_s: float):
        self.window_s = window_s
        self._pending: deque[tuple[tuple, float]] = deque()
        self._lock = threading.Lock()

    @staticmethod
    def _signature(message: can.Message):
        return (message.arbitration_id, message.is_extended_id, message.is_remote_frame,
                message.dlc, bytes(message.data))

    def sent(self, message: can.Message) -> None:
        with self._lock:
            self._pending.append((self._signature(message), time.monotonic() + self.window_s))

    def is_echo(self, message: can.Message) -> bool:
        now, signature = time.monotonic(), self._signature(message)
        with self._lock:
            while self._pending and self._pending[0][1] < now:
                self._pending.popleft()
            for index, (pending, _) in enumerate(self._pending):
                if pending == signature:
                    del self._pending[index]
                    return True
        return False


class SerialLink:
    """One SLCAN device: connection management, handshake, receive and transmit."""

    def __init__(self, config: dict, bridge: "Serial2CanBridge"):
        self.name = config["name"]
        self.device = config["device"]
        self.baudrate = int(config.get("baudrate", 115200))
        self.can_bitrate = int(config.get("can_bitrate", 500000))
        if self.can_bitrate not in BITRATE_CODES:
            raise ValueError(f"{self.name}: unsupported can_bitrate {self.can_bitrate}")
        self.to_serial = IdFilter(config.get("to_serial"))
        self.from_serial = IdFilter(config.get("from_serial"))
        self.reconnect_s = float(config.get("reconnect_s", 2.0))
        self.close_on_exit = bool(config.get("close_on_exit", True))
        self.queue: queue.Queue[can.Message] = queue.Queue(maxsize=int(config.get("tx_queue", 256)))
        self.bridge = bridge
        self.connected = threading.Event()
        self.version: str | None = None
        self.stats: dict[str, int] = dict.fromkeys(
            ("serial_to_can", "can_to_serial", "filtered_in", "filtered_out", "dropped_queue_full",
             "dropped_offline", "acks", "nacks", "malformed", "connects", "disconnects"), 0)
        self._serial: serial.Serial | None = None
        self._write_lock = threading.Lock()
        self._splitter = slcan.LineSplitter()
        self._pending: deque = deque()  # tokens read but not yet handled
        self._reader = threading.Thread(target=self._read_loop, name=f"{self.name}-rx", daemon=True)
        self._writer = threading.Thread(target=self._write_loop, name=f"{self.name}-tx", daemon=True)

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> None:
        self._reader.start()
        self._writer.start()

    def close(self) -> None:
        """Close the SLCAN channel (ECU fail-safe) and the serial port."""
        port = self._serial
        if port is not None and self.connected.is_set() and self.close_on_exit:
            try:
                with self._write_lock:
                    port.write(b"C\r")
                    port.flush()
                logger.info("[%s] sent close (C) to ECU", self.name)
            except (serial.SerialException, OSError) as error:
                logger.warning("[%s] close failed: %s", self.name, error)
        self.connected.clear()
        if port is not None:
            port.close()
        self._reader.join(timeout=2)
        self._writer.join(timeout=2)

    def enqueue(self, message: can.Message) -> None:
        """Queue a bus frame for this device; never blocks the caller."""
        if not self.to_serial.matches(message):
            self.stats["filtered_out"] += 1
        elif not self.connected.is_set():
            self.stats["dropped_offline"] += 1
        else:
            try:
                self.queue.put_nowait(message)
            except queue.Full:
                self.stats["dropped_queue_full"] += 1

    # -- connection --------------------------------------------------------
    def _resolve_device(self) -> str | None:
        matches = sorted(glob.glob(self.device)) if any(c in self.device for c in "*?[") else [self.device]
        return matches[0] if matches and Path(matches[0]).exists() else None

    def _command(self, port: serial.Serial, command: str, timeout: float = 1.0) -> bytes | None:
        """Send a command; return its reply token (b'' ok, BELL, or a response)."""
        with self._write_lock:
            port.write(command.encode() + slcan.CR)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not self.bridge.stopping.is_set():
            if not self._pending:
                self._pending.extend(self._splitter.feed(port.read(port.in_waiting or 1)))
                continue
            token = self._pending.popleft()
            if token is not None and token[:1] in (b"t", b"T", b"r", b"R"):
                self._handle(token)  # e.g. the ECU's state report right after "O"
            elif token is not None:
                return token
        return None

    def _handshake(self, port: serial.Serial) -> None:
        port.write(b"\r\r\r")  # terminate any partial line on the device
        time.sleep(0.05)
        port.reset_input_buffer()
        self._splitter = slcan.LineSplitter()
        self._pending.clear()
        self._command(port, "C")  # close if open; BELL from closed devices is fine
        reply = self._command(port, "V")
        self.version = reply.decode(errors="replace") if reply and reply.startswith(b"V") else None
        if self._command(port, BITRATE_CODES[self.can_bitrate]) != b"":
            logger.warning("[%s] device refused nominal bitrate %s", self.name, self.can_bitrate)
        if self._command(port, "O") != b"":
            raise serial.SerialException("device did not acknowledge open (O)")

    def _read_loop(self) -> None:
        """Connection lifecycle: open, handshake, serve until lost, retry."""
        stopping = self.bridge.stopping
        while not stopping.is_set():
            port = self._open()
            if port is not None:
                self._serve(port)
            stopping.wait(self.reconnect_s)

    def _open(self) -> serial.Serial | None:
        path = self._resolve_device()
        if path is None:
            return None
        try:
            port = serial.Serial(path, self.baudrate, timeout=0.1, write_timeout=1.0)
        except (serial.SerialException, OSError) as error:
            logger.warning("[%s] cannot open %s: %s", self.name, path, error)
            return None
        self._serial = port
        return port

    def _serve(self, port: serial.Serial) -> None:
        stopping = self.bridge.stopping
        established = False
        try:
            self._handshake(port)
            self.connected.set()
            established = True
            self.stats["connects"] += 1
            logger.info("[%s] connected on %s (%s), channel open", self.name, port.port, self.version or "no version")
            while self._pending:  # e.g. a state frame that arrived with the "O" reply
                self._handle(self._pending.popleft())
            while not stopping.is_set():
                for token in self._splitter.feed(port.read(port.in_waiting or 1)):
                    self._handle(token)
        except (serial.SerialException, OSError, TypeError) as error:
            if not stopping.is_set():
                logger.warning("[%s] link lost: %s", self.name, error)
        finally:
            self._end_session(port, established)

    def _end_session(self, port: serial.Serial, established: bool) -> None:
        """After a lost link: mark offline and close. On shutdown close() owns the port.

        The writer may already have cleared ``connected``, so the session's own
        ``established`` flag decides whether a disconnect is counted."""
        if not self.bridge.stopping.is_set():
            if established:
                self.stats["disconnects"] += 1
            self.connected.clear()
            port.close()
        self._drain_queue()

    def _drain_queue(self) -> None:
        while True:
            try:
                self.queue.get_nowait()
                self.stats["dropped_offline"] += 1
            except queue.Empty:
                return

    def _handle(self, token: bytes | None) -> None:
        if token is None:
            self.stats["malformed"] += 1
        elif token == slcan.BELL:
            self.stats["nacks"] += 1
        elif token in (b"z", b"Z"):
            self.stats["acks"] += 1
        elif token[:1] in (b"t", b"T", b"r", b"R"):
            try:
                message = slcan.decode(token)
            except slcan.SlcanError:
                self.stats["malformed"] += 1
                return
            if self.from_serial.matches(message):
                self.stats["serial_to_can"] += 1
                self.bridge.from_serial(self, message)
            else:
                self.stats["filtered_in"] += 1

    def _write_loop(self) -> None:
        while not self.bridge.stopping.is_set():
            try:
                message = self.queue.get(timeout=0.2)
            except queue.Empty:
                continue
            port = self._serial
            if port is None or not self.connected.is_set():
                self.stats["dropped_offline"] += 1
                continue
            try:
                line = slcan.encode(message)
                with self._write_lock:
                    port.write(line)
                self.stats["can_to_serial"] += 1
                logger.debug("[%s] CAN→serial %s", self.name, line.strip().decode())
            except slcan.SlcanError:
                self.stats["filtered_out"] += 1
            except (serial.SerialException, OSError) as error:
                logger.warning("[%s] write failed: %s", self.name, error)
                self.connected.clear()
                port.close()  # wakes the reader, which reconnects


class Serial2CanBridge:
    def __init__(self, config: dict):
        self.config = config
        self.stopping = threading.Event()
        can_config = dict(config["can"])
        interface = can_config.pop("interface")
        channel = can_config.pop("channel")
        suppress = can_config.pop("suppress_own_echo", interface == "udp_multicast")
        if interface in ("socketcan", "socketcan_native"):
            can_config.pop("bitrate", None)  # configured by the OS
        if interface == "udp_multicast":
            can_config.setdefault("fd", False)
        self.bus = can.Bus(interface=interface, channel=channel, **can_config)
        self.bus_name = f"{interface}:{channel}"
        self.echo = EchoGuard(float(config.get("echo_window_s", 1.0))) if suppress else None
        self._send_lock = threading.Lock()
        self.stats = {"can_rx": 0, "can_tx": 0, "echo_suppressed": 0, "can_tx_errors": 0}
        names = [port["name"] for port in config["serial_ports"]]
        if len(set(names)) != len(names):
            raise ValueError("serial port names must be unique")
        self.links = [SerialLink(port, self) for port in config["serial_ports"]]

    def from_serial(self, source: SerialLink, message: can.Message) -> None:
        """A frame from one ECU: put it on the CAN bus and on the other serial ports."""
        # Leave message.channel unset: SocketCAN would treat it as an interface name.
        try:
            with self._send_lock:
                if self.echo:
                    self.echo.sent(message)
                self.bus.send(message)
            self.stats["can_tx"] += 1
            logger.debug("[%s] serial→CAN %s", source.name, slcan.encode(message).strip().decode())
        except can.CanError as error:
            self.stats["can_tx_errors"] += 1
            logger.warning("[%s] CAN send failed: %s", source.name, error)
        for link in self.links:
            if link is not source:
                link.enqueue(message)

    def run(self) -> None:
        interval = float(self.config.get("stats_interval_s", 10))
        logger.info("Serial2CAN bridge on %s with %d serial port(s)", self.bus_name, len(self.links))
        for link in self.links:
            link.start()
        next_stats = time.monotonic() + interval
        try:
            while not self.stopping.is_set():
                message = self.bus.recv(timeout=0.2)
                if message is not None:
                    self._dispatch(message)
                if interval > 0 and time.monotonic() >= next_stats:
                    next_stats += interval
                    self.log_stats()
        finally:
            self.shutdown()

    def _dispatch(self, message: can.Message) -> None:
        """A frame from the CAN bus: to every serial port whose filter accepts it."""
        if message.is_error_frame:
            return
        if self.echo and self.echo.is_echo(message):
            self.stats["echo_suppressed"] += 1
            return
        self.stats["can_rx"] += 1
        for link in self.links:
            link.enqueue(message)

    def log_stats(self) -> None:
        ports = {link.name: dict(link.stats, connected=link.connected.is_set()) for link in self.links}
        logger.info("stats %s", json.dumps({"bus": self.stats, "ports": ports}, separators=(",", ":")))

    def shutdown(self) -> None:
        self.stopping.set()
        for link in self.links:
            link.close()
        self.bus.shutdown()
        self.log_stats()
        logger.info("Serial2CAN bridge stopped")


def load_config(path: Path, overrides: list[str]) -> dict:
    config = json.loads(path.read_text())
    ports = {port["name"]: port for port in config.get("serial_ports", [])}
    for override in overrides:
        name, _, device = override.partition("=")
        if name not in ports or not device:
            raise SystemExit(f"--device expects NAME=PATH with a configured port name, got {override!r}")
        ports[name]["device"] = device
    if not ports:
        raise SystemExit("configuration has no serial_ports")
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", type=Path, help="bridge configuration JSON")
    parser.add_argument("--device", action="append", default=[], metavar="NAME=PATH",
                        help="override the serial device of a configured port")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    args = parser.parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    bridge = Serial2CanBridge(load_config(args.config, args.device))

    def request_stop(signum, frame):
        logger.info("Shutdown requested")
        bridge.stopping.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    bridge.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
