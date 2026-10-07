# SPDX-License-Identifier: Apache-2.0
"""Integration tests of the gateway on the NXP S32K148EVB (SWE.5, target integration).

The board talks DoIP over its 100BASE-T1 Ethernet (192.168.0.200). No CAN node is
attached to its CAN connector, so routed requests are transmitted without an
acknowledgement: they must fail cleanly, free the route and, after three failures,
set the route's lost-communication DTC. Run through scripts/board-it.sh, which
flashes the image and sets ZGW_IP=192.168.0.200 and ZGW_ELF.

Each test names the software requirement(s) it verifies.
"""

from __future__ import annotations

import os
import socket
import statistics
import struct
import subprocess
import time
from pathlib import Path

import pytest
from doipclient import DoIPClient
from doipclient.messages import RoutingActivationRequest

from doip_tester import FRONT, FUNCTIONAL, GATEWAY, GATEWAY_IP, REAR, Tester

pytestmark = pytest.mark.skipif(GATEWAY_IP != "192.168.0.200", reason="board tests need ZGW_IP=192.168.0.200")

BOARD = Path(__file__).resolve().parents[2] / "scripts" / "board.sh"
RESULTS = Path(os.environ.get("ZGW_RESULTS", "results"))
VIN = b"TCAPSZONALGW00001"
# no CAN peer: the DoCAN transmission is confirmed as failed after its 1 s callback
# timeout, at the latest after the router's 2 s transfer budget
CAN_FAILURE_S = 2.5


def wait_for_doip(timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((GATEWAY_IP, 13400), timeout=0.5):
                return
        except OSError:
            time.sleep(0.2)
    raise TimeoutError("gateway DoIP port not reachable")


@pytest.fixture(scope="module")
def board():
    """Resets the board while listening for its vehicle announcements."""
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.bind(("", 13400))
    udp.settimeout(0.1)
    subprocess.run([str(BOARD), "reset", os.environ["ZGW_ELF"]], check=True, capture_output=True, timeout=60)
    reset_at = time.time()
    announcements, deadline = [], time.time() + 8.0
    while time.time() < deadline:
        try:
            data, sender = udp.recvfrom(4096)
        except socket.timeout:
            continue
        if sender[0] == GATEWAY_IP and len(data) >= 8 + 32 and struct.unpack(">H", data[2:4])[0] == 0x0004:
            body = data[8:]
            announcements.append((time.time() - reset_at, body[:17], struct.unpack(">H", body[17:19])[0]))
    udp.close()
    wait_for_doip()
    return {"announcements": announcements}


@pytest.fixture
def tester(board):
    t = Tester()
    yield t
    t.close()


def read_dtcs(tester: Tester, mask: int = 0xFF) -> dict[int, int]:
    payload = tester.request(GATEWAY, bytes([0x19, 0x02, mask])).responses[-1][1]
    records = payload[3:]
    return {int.from_bytes(records[i:i + 3], "big"): records[i + 3] for i in range(0, len(records), 4)}


def read_route_stats(tester: Tester) -> dict[int, tuple[int, ...]]:
    data = tester.read_did(GATEWAY, 0xFD01)[3:]
    count, offset, routes = data[8], 9, {}
    for _ in range(count):
        address = struct.unpack_from(">H", data, offset)[0]
        routes[address] = struct.unpack_from(">8H", data, offset + 2)
        offset += 18
    return routes


# --- DoIP entity ---------------------------------------------------------------------------

def test_board_vehicle_announcement(board):
    """SWR-001: the board announces itself after reset with the configured VIN and 0x1010."""
    announcements = board["announcements"]
    # the host address comes back only after the link restarts, so early announcements may be missed
    assert announcements, "no vehicle announcement received"
    for _, vin, address in announcements:
        assert (vin, address) == (VIN, GATEWAY)


def test_board_vehicle_identification(board):
    """SWR-001: generic and by-VIN identification answered with VIN, 0x1010 and EID."""
    _, entity = DoIPClient.get_entity(ecu_ip_address=GATEWAY_IP, protocol_version=2)
    assert (entity.vin.encode() if isinstance(entity.vin, str) else bytes(entity.vin)) == VIN
    assert entity.logical_address == GATEWAY
    client = DoIPClient(GATEWAY_IP, GATEWAY, client_logical_address=0x0E80, protocol_version=2)
    try:
        assert client.request_vehicle_identification(vin=VIN.decode()).logical_address == GATEWAY
    finally:
        client.close()


def test_board_routing_activation_rules(board):
    """SWR-002: tester range accepted; unknown source and activation type 0x01 rejected."""
    Tester(0x0EF5).close()
    with pytest.raises(ConnectionRefusedError):
        DoIPClient(GATEWAY_IP, GATEWAY, client_logical_address=0x0123, protocol_version=2)
    with pytest.raises(ConnectionRefusedError):
        DoIPClient(GATEWAY_IP, GATEWAY, client_logical_address=0x0E80, protocol_version=2,
                   activation_type=RoutingActivationRequest.ActivationType.DiagnosticRequiredByRegulation)


def test_board_entity_status(tester):
    """SWR-005: node type gateway, socket limits and open sockets; power mode ready."""
    status = tester.client.request_entity_status()
    assert status.node_type == 0x00
    assert status.max_concurrent_sockets >= 2 and status.currently_open_sockets >= 1
    assert tester.client.request_diagnostic_power_mode().diagnostic_power_mode == 0x01


# --- gateway UDS server --------------------------------------------------------------------

def test_board_local_uds(tester):
    """SWR-011, SWR-020, SWR-021, SWR-022: identification, routing table, sessions and NRCs."""
    assert tester.read_did(GATEWAY, 0xF190)[3:] == VIN
    assert tester.read_did(GATEWAY, 0xF18C)[3:] == b"ZGW-POSIX-0001"
    version = tester.read_did(GATEWAY, 0xF195)[3:].decode()
    assert version.startswith("zgw ") and " rt b4bdeccc" in version, version
    table = tester.read_did(GATEWAY, 0xFD00)[3:]
    assert table[0] == 2 and struct.unpack_from(">HH", table, 1) == (GATEWAY, FUNCTIONAL)
    assert tester.request(GATEWAY, b"\x10\x03").responses[-1][1][:2] == b"\x50\x03"
    suppressed = tester.request(GATEWAY, b"\x3E\x80", wait=0.4)
    assert suppressed.ack is True and suppressed.responses == []
    assert tester.request(GATEWAY, b"\x10\x01").responses[-1][1][:2] == b"\x50\x01"
    assert tester.request(GATEWAY, b"\x23\x00").responses[-1][1] == b"\x7F\x23\x11"
    assert tester.request(GATEWAY, b"\x22\x12\x34").responses[-1][1] == b"\x7F\x22\x31"


def test_board_rejections(tester):
    """SWR-003, SWR-013: unknown target -> NACK 0x03; 8-byte functional request -> NACK 0x04."""
    unknown = tester.request(0x1099, b"\x3E\x00")
    assert (unknown.ack, unknown.nack_code) == (False, 0x03)
    too_long = tester.request(FUNCTIONAL, bytes(8), wait=0.4)
    assert (too_long.ack, too_long.nack_code) == (False, 0x04)


def test_board_functional_tester_present(tester):
    """SWR-013: functional TesterPresent answered by the gateway; no CAN node answers."""
    result = tester.request(FUNCTIONAL, b"\x3E\x00", wait=0.5, until_final=False)
    assert result.ack is True
    assert result.responses == [(GATEWAY, b"\x7E\x00")]


def test_board_local_latency(tester):
    """SWR-060 (target): gateway-local UDS round trip over the board's Ethernet, 200 samples."""
    samples = []
    for _ in range(200):
        start = time.perf_counter()
        assert tester.request(GATEWAY, b"\x3E\x00").responses == [(GATEWAY, b"\x7E\x00")]
        samples.append((time.perf_counter() - start) * 1000)
    p95 = statistics.quantiles(samples, n=20)[18]
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "board-latency.txt").write_text(
        f"samples={len(samples)}\nlocal_p50_ms={statistics.median(samples):.2f}\nlocal_p95_ms={p95:.2f}\n")
    assert p95 <= 20.0, f"local round trip p95 {p95:.2f} ms"


# --- routing without a CAN peer -------------------------------------------------------------

def test_board_route_without_can_peer(tester):
    """SWR-015, SWR-016, SWR-018: unacknowledged CAN request -> route busy, then freed and counted."""
    before = read_route_stats(tester)[REAR]
    first = tester.request(REAR, b"\x22\xF1\x95", wait=0.1)
    assert first.ack is True and first.responses == []
    busy = tester.request(REAR, b"\x22\xF1\x95", wait=0.1)
    assert (busy.ack, busy.nack_code) == (False, 0x05)
    time.sleep(CAN_FAILURE_S)
    again = tester.request(REAR, b"\x3E\x00", wait=0.1)
    assert again.ack is True, "route not freed after the failed transmission"
    time.sleep(CAN_FAILURE_S)
    after = read_route_stats(tester)[REAR]
    # counters: requests, responses, pending, timeouts, busy, too_large, tx_fail, discarded
    assert after[0] == before[0] + 2 and after[4] == before[4] + 1
    assert after[3] + after[6] == before[3] + before[6] + 2, (before, after)


def test_board_lost_communication_dtc(tester):
    """SWR-024, SWR-025: three failed requests to 0x1030 set U0141; ClearDTC resets it."""
    u0141 = 0xC14100
    tester.request(GATEWAY, b"\x14\xFF\xFF\xFF")
    assert read_dtcs(tester).get(u0141, 0) & 0x01 == 0
    for _ in range(3):
        assert tester.request(FRONT, b"\x3E\x00", wait=0.1).ack is True
        time.sleep(CAN_FAILURE_S)
    status = read_dtcs(tester)[u0141]
    assert status & 0x09 == 0x09, f"testFailed + confirmedDTC expected, got {status:#04x}"
    assert tester.request(GATEWAY, b"\x14\xFF\xFF\xFF").responses[-1][1] == b"\x54"
    assert read_dtcs(tester, 0x09).get(u0141) is None
