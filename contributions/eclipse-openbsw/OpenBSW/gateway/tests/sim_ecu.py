# SPDX-License-Identifier: Apache-2.0
"""Simulated zonal ECU for the gateway integration tests.

A minimal UDS server on ISO-TP (normal 11-bit addressing, padded classic CAN). It
answers physical requests on its request ID and single-frame functional requests on
0x7DF, always on its response ID. Behaviour per DID:

  22 F195   software version
  22 F1A0   LARGE_SIZE bytes (multi-frame)
  22 F1A1   7F 22 78 (response pending), then the final response after PENDING_DELAY_S
  3E 00/80  TesterPresent (80 = suppress positive response)
  10 xx     DiagnosticSessionControl
  19 02     no DTCs
  other     7F <SID> 11

mode = "silent" drops every request (used for timeout and monitoring tests).
"""

from __future__ import annotations

import threading
import time

import can
import isotp

FUNCTIONAL_CAN_ID = 0x7DF
LARGE_SIZE = 1000
PENDING_DELAY_S = 0.4
SW_VERSION = b"THREADX-SIM 1.0"


class SimEcu:
    def __init__(self, channel: str, request_id: int, response_id: int, name: str = "ecu"):
        self.name = name
        self.request_id = request_id
        self.response_id = response_id
        self.mode = "normal"
        self.requests: list[bytes] = []
        self.functional_requests: list[bytes] = []
        self._bus = can.Bus(channel=channel, interface="socketcan")
        self._notifier = can.Notifier(self._bus, [], timeout=0.05)
        address = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=response_id, rxid=request_id)
        params = {
            "stmin": 0,
            "blocksize": 0,
            "tx_padding": 0xCC,
            "tx_data_min_length": 8,
            "rx_flowcontrol_timeout": 1000,
            "rx_consecutive_frame_timeout": 1000,
            "wftmax": 0,
        }
        self._stack = isotp.NotifierBasedCanStack(self._bus, self._notifier, address=address, params=params)
        self._notifier.add_listener(self._on_frame)
        self._running = False
        self._thread: threading.Thread | None = None

    # -- lifecycle -------------------------------------------------------
    def start(self) -> "SimEcu":
        self._running = True
        self._stack.start()
        self._thread = threading.Thread(target=self._loop, name=f"sim-{self.name}", daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self._stack.stop()
        self._notifier.stop()
        self._bus.shutdown()

    def send_raw(self, data: bytes) -> None:
        """Send a raw single CAN frame on the response ID (unsolicited traffic)."""
        self._bus.send(can.Message(arbitration_id=self.response_id, data=data, is_extended_id=False))

    # -- request handling ------------------------------------------------
    def _loop(self) -> None:
        while self._running:
            payload = self._stack.recv(block=True, timeout=0.05)
            if payload is None:
                continue
            self.requests.append(bytes(payload))
            if self.mode == "silent":
                continue
            self._respond(bytes(payload))

    def _on_frame(self, msg: can.Message) -> None:
        if msg.arbitration_id != FUNCTIONAL_CAN_ID or msg.is_extended_id or not msg.data:
            return
        pci = msg.data[0]
        if pci >> 4 != 0:  # functional requests are single frames only
            return
        payload = bytes(msg.data[1:1 + (pci & 0x0F)])
        self.functional_requests.append(payload)
        if self.mode == "silent":
            return
        self._respond(payload)

    def _respond(self, req: bytes) -> None:
        response = self.handle(req)
        if response is not None:
            self._stack.send(response)

    def handle(self, req: bytes) -> bytes | None:
        sid = req[0]
        if sid == 0x3E and len(req) == 2:
            return None if req[1] & 0x80 else bytes([0x7E, req[1]])
        if sid == 0x10 and len(req) == 2:
            return bytes([0x50, req[1], 0x00, 0x32, 0x01, 0xF4])
        if sid == 0x19 and len(req) >= 2 and req[1] == 0x02:
            return bytes([0x59, 0x02, 0xFF])
        if sid == 0x22 and len(req) == 3:
            did = (req[1] << 8) | req[2]
            if did == 0xF195:
                return bytes([0x62, 0xF1, 0x95]) + SW_VERSION
            if did == 0xF1A0:
                return bytes([0x62, 0xF1, 0xA0]) + bytes(i & 0xFF for i in range(LARGE_SIZE))
            if did == 0xF1A1:
                self._stack.send(bytes([0x7F, 0x22, 0x78]))
                threading.Timer(PENDING_DELAY_S, lambda: self._stack.send(bytes([0x62, 0xF1, 0xA1, 0x01]))).start()
                return None
            return bytes([0x7F, 0x22, 0x31])
        if sid == 0x22 and len(req) > 3:
            # echo-length service for large request tests: 22 F1 B0 <data...> -> 62 F1 B0 <len>
            return bytes([0x62, req[1], req[2], (len(req) >> 8) & 0xFF, len(req) & 0xFF])
        return bytes([0x7F, sid, 0x11])

    def wait_for_requests(self, count: int, timeout: float = 2.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if len(self.requests) >= count:
                return True
            time.sleep(0.01)
        return False
