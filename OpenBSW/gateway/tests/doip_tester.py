# SPDX-License-Identifier: Apache-2.0
"""DoIP tester helper: one routing-activated connection, any target address."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

from doipclient import DoIPClient
from doipclient.messages import (
    DiagnosticMessage,
    DiagnosticMessageNegativeAcknowledgement,
    DiagnosticMessagePositiveAcknowledgement,
)

# PC simulation 192.168.0.201; S32K148EVB 192.168.0.200 (ZGW_IP)
GATEWAY_IP = os.environ.get("ZGW_IP", "192.168.0.201")
GATEWAY = 0x1010
REAR = 0x1020
FRONT = 0x1030
ETH = 0x1040
FUNCTIONAL = 0xE400
TESTER = 0x0E80


@dataclass
class Result:
    ack: bool | None = None          # True ACK, False NACK, None nothing
    nack_code: int | None = None
    responses: list[tuple[int, bytes]] = field(default_factory=list)  # (source, payload)

    def payloads(self, source: int | None = None) -> list[bytes]:
        return [p for s, p in self.responses if source is None or s == source]


class Tester:
    def __init__(self, tester_address: int = TESTER, ip: str = GATEWAY_IP):
        self.address = tester_address
        self.client = DoIPClient(ip, GATEWAY, client_logical_address=tester_address, protocol_version=2)
        # doipclient's read_doip() blocks in recv() for the socket timeout (2 s by default),
        # whatever its own timeout argument; a short socket timeout keeps collect() accurate
        self.client._tcp_sock.settimeout(0.02)  # noqa: SLF001 - test helper

    def close(self) -> None:
        self.client.close()

    def send(self, target: int, payload: bytes) -> None:
        self.client.send_doip_message(DiagnosticMessage(self.address, target, bytes(payload)))

    def collect(self, wait: float, until_final: bool = True) -> Result:
        """Read ACK/NACK and diagnostic responses for up to `wait` seconds."""
        result = Result()
        deadline = time.time() + wait
        while time.time() < deadline:
            try:
                msg = self.client.read_doip(timeout=max(0.001, deadline - time.time()))
            except TimeoutError:
                continue
            if msg is None:
                continue
            if isinstance(msg, DiagnosticMessagePositiveAcknowledgement):
                result.ack = True
            elif isinstance(msg, DiagnosticMessageNegativeAcknowledgement):
                result.ack, result.nack_code = False, msg.nack_code
                return result
            elif isinstance(msg, DiagnosticMessage):
                result.responses.append((msg.source_address, bytes(msg.user_data)))
                final = not (len(msg.user_data) >= 3 and msg.user_data[0] == 0x7F and msg.user_data[2] == 0x78)
                if until_final and final:
                    return result
        return result

    def request(self, target: int, payload: bytes, wait: float = 1.0, until_final: bool = True) -> Result:
        self.send(target, payload)
        return self.collect(wait, until_final)

    def read_did(self, target: int, did: int, wait: float = 1.0) -> bytes:
        result = self.request(target, bytes([0x22, did >> 8, did & 0xFF]), wait)
        assert result.ack is True, f"no ACK: {result}"
        assert result.responses, f"no response from {target:#06x}"
        return result.responses[-1][1]
