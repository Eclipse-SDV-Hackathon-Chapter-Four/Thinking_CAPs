# SPDX-License-Identifier: Apache-2.0
"""Simulated Ethernet zonal ECU: a DoIP entity (ISO 13400-2:2012) with a UDS server.

It listens on TCP 13400 at NODE_IP (default 192.168.0.30, set by ZGW_DOIP_NODE_IP); the
host must own that address (scripts/net-up.sh adds it to lo). The gateway reaches it as
route 0x1040. Routing activation is accepted for any source in 0x0E00-0x0EFF with
activation type 0x00. UDS behaviour, also for the functional address 0xE400:

  22 F195   software version
  22 F1A0   LARGE_SIZE bytes
  22 F1A1   7F 22 78 (response pending), then the final response after PENDING_DELAY_S
  22 <DID> <data...>  62 <DID> <request length> (large request test)
  3E 00/80  TesterPresent (80 = suppress positive response)
  10 xx     DiagnosticSessionControl
  other     7F <SID> 11

mode:
  normal    ACK and respond
  silent    ACK, never respond (P2 timeout)
  no_ack    neither ACK nor respond (delivery timeout of the DoIP client)
  nack      diagnostic message NACK 0x06 (target unreachable)
  refuse    routing activation refused (code 0x00)
  close     close the connection when a diagnostic message arrives
"""

from __future__ import annotations

import os
import socket
import struct
import threading
import time
from dataclasses import dataclass, field

NODE_IP = os.environ.get("ZGW_DOIP_NODE_IP", "192.168.0.30")
NODE = 0x1040
FUNCTIONAL = 0xE400
PORT = 13400
VERSION = 0x02
LARGE_SIZE = 3000
PENDING_DELAY_S = 0.4
SW_VERSION = b"ETH-ZONE-SIM 1.0"

ROUTING_ACTIVATION_REQUEST = 0x0005
ROUTING_ACTIVATION_RESPONSE = 0x0006
ALIVE_CHECK_REQUEST = 0x0007
ALIVE_CHECK_RESPONSE = 0x0008
DIAGNOSTIC_MESSAGE = 0x8001
DIAGNOSTIC_ACK = 0x8002
DIAGNOSTIC_NACK = 0x8003


def frame(payload_type: int, payload: bytes) -> bytes:
    return struct.pack(">BBHI", VERSION, VERSION ^ 0xFF, payload_type, len(payload)) + payload


@dataclass
class Message:
    source: int
    target: int
    payload: bytes


@dataclass
class Record:
    connections: int = 0
    activations: list[tuple[int, int]] = field(default_factory=list)  # (source, type)
    requests: list[Message] = field(default_factory=list)
    alive_responses: list[int] = field(default_factory=list)


class SimDoipEcu:
    def __init__(self, ip: str = NODE_IP, address: int = NODE):
        self.ip, self.address = ip, address
        self.mode = "normal"
        self.record = Record()
        self._server: socket.socket | None = None
        self._listen()  # OSError if the host does not own the address
        self._client: socket.socket | None = None
        self._tester: int | None = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    # -- lifecycle -----------------------------------------------------------------------
    def _listen(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.ip, PORT))
        server.listen(4)
        server.settimeout(0.05)
        self._server = server

    def suspend(self) -> None:
        """Stop listening and drop the connection: connection attempts are refused."""
        server, self._server = self._server, None
        if server:
            server.close()
        self.disconnect()

    def resume(self) -> None:
        if self._server is None:
            self._listen()

    def start(self) -> "SimDoipEcu":
        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, name="sim-doip", daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self.suspend()

    def reset(self) -> None:
        self.mode = "normal"
        self.record = Record()

    def disconnect(self) -> None:
        with self._lock:
            client, self._client, self._tester = self._client, None, None
        if client:
            try:
                client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            client.close()

    @property
    def connected(self) -> bool:
        return self._client is not None

    # -- node-initiated messages ---------------------------------------------------------
    def send(self, payload_type: int, payload: bytes) -> None:
        with self._lock:
            if self._client:
                self._client.sendall(frame(payload_type, payload))

    def send_alive_check(self) -> None:
        self.send(ALIVE_CHECK_REQUEST, b"")

    def send_diagnostic(self, payload: bytes, source: int | None = None) -> None:
        tester = self._tester if self._tester is not None else 0x0E10
        self.send(DIAGNOSTIC_MESSAGE, struct.pack(">HH", source or self.address, tester) + payload)

    # -- connection handling -------------------------------------------------------------
    def _accept_loop(self) -> None:
        while self._running:
            server = self._server
            if server is None:
                time.sleep(0.05)
                continue
            try:
                client, _ = server.accept()
            except (TimeoutError, socket.timeout):
                continue
            except OSError:
                continue
            self.disconnect()  # one tester connection at a time
            # ACK and response leave at once, as from a DoIP stack (no Nagle delay)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client.settimeout(0.05)
            with self._lock:
                self._client = client
            self.record.connections += 1
            threading.Thread(target=self._serve, args=(client,), daemon=True).start()

    def _recv_exact(self, client: socket.socket, n: int) -> bytes | None:
        data = b""
        while len(data) < n:
            if not self._running or self._client is not client:
                return None
            try:
                chunk = client.recv(n - len(data))
            except (TimeoutError, socket.timeout):
                continue
            except OSError:
                return None
            if not chunk:
                return None
            data += chunk
        return data

    def _serve(self, client: socket.socket) -> None:
        while True:
            header = self._recv_exact(client, 8)
            if header is None:
                break
            _, _, payload_type, length = struct.unpack(">BBHI", header)
            payload = self._recv_exact(client, length) if length else b""
            if payload is None:
                break
            if not self._handle(client, payload_type, payload):
                break
        if self._client is client:
            self.disconnect()

    def _handle(self, client: socket.socket, payload_type: int, payload: bytes) -> bool:
        if payload_type == ROUTING_ACTIVATION_REQUEST:
            source, activation_type = struct.unpack_from(">HB", payload)
            self.record.activations.append((source, activation_type))
            ok = self.mode != "refuse" and 0x0E00 <= source <= 0x0EFF and activation_type == 0x00
            code = 0x10 if ok else 0x00
            self.send(ROUTING_ACTIVATION_RESPONSE, struct.pack(">HHB4x", source, self.address, code))
            if ok:
                self._tester = source
                return True
            return False
        if payload_type == ALIVE_CHECK_RESPONSE:
            self.record.alive_responses.append(struct.unpack_from(">H", payload)[0])
            return True
        if payload_type != DIAGNOSTIC_MESSAGE:
            return True
        source, target = struct.unpack_from(">HH", payload)
        request = payload[4:]
        self.record.requests.append(Message(source, target, request))
        if self.mode == "close":
            return False
        if self.mode == "no_ack":
            return True
        if self.mode == "nack":
            self.send(DIAGNOSTIC_NACK, struct.pack(">HHB", self.address, source, 0x06))
            return True
        self.send(DIAGNOSTIC_ACK, struct.pack(">HHB", self.address, source, 0x00))
        if self.mode == "silent" or source != self._tester:
            return True
        response = self.handle(request)
        if response is not None:
            self.send_diagnostic(response)
        return True

    def handle(self, req: bytes) -> bytes | None:
        sid = req[0]
        if sid == 0x3E and len(req) == 2:
            return None if req[1] & 0x80 else bytes([0x7E, req[1]])
        if sid == 0x10 and len(req) == 2:
            return bytes([0x50, req[1], 0x00, 0x32, 0x01, 0xF4])
        if sid == 0x22 and len(req) == 3:
            did = (req[1] << 8) | req[2]
            if did == 0xF195:
                return bytes([0x62, 0xF1, 0x95]) + SW_VERSION
            if did == 0xF1A0:
                return bytes([0x62, 0xF1, 0xA0]) + bytes(i & 0xFF for i in range(LARGE_SIZE))
            if did == 0xF1A1:
                self.send_diagnostic(bytes([0x7F, 0x22, 0x78]))
                threading.Timer(PENDING_DELAY_S,
                                lambda: self.send_diagnostic(bytes([0x62, 0xF1, 0xA1, 0x01]))).start()
                return None
            return bytes([0x7F, 0x22, 0x31])
        if sid == 0x22 and len(req) > 3:
            return bytes([0x62, req[1], req[2], (len(req) >> 8) & 0xFF, len(req) & 0xFF])
        return bytes([0x7F, sid, 0x11])

    def wait_for(self, condition, timeout: float = 2.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if condition():
                return True
            time.sleep(0.01)
        return False
