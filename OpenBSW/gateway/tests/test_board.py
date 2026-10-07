# SPDX-License-Identifier: Apache-2.0
"""Integration tests of the gateway on the NXP S32K148EVB (SWE.5, target integration).

The board talks DoIP over its 100BASE-T1 Ethernet (192.168.0.200). No CAN node is
attached to its CAN connector, so routed CAN requests are transmitted without an
acknowledgement: they must fail cleanly, free the route and, after three failures,
set the route's lost-communication DTC. The DoIP route 0x1040 reaches the simulated
Ethernet zonal ECU on the host (192.168.0.30, sim_doip_ecu.py) over the same link, so
routing is verified end to end on the target. Run through scripts/board-it.sh, which
flashes the image and sets ZGW_IP=192.168.0.200 and ZGW_ELF.

Each test names the software requirement(s) it verifies.
"""

from __future__ import annotations

import os
import socket
import statistics
import struct
import subprocess
import sys
import time
from pathlib import Path

import pytest
from doipclient import DoIPClient
from doipclient.messages import RoutingActivationRequest

from doip_tester import ETH, FRONT, FUNCTIONAL, GATEWAY, GATEWAY_IP, REAR, Tester
from sim_doip_ecu import LARGE_SIZE, NODE_IP, SW_VERSION, Message, SimDoipEcu

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gen_routing  # noqa: E402

ROUTING = gen_routing.validate(gen_routing.load(Path(__file__).resolve().parents[1] / "config" / "routing.yaml"))

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


@pytest.fixture(scope="module")
def eth_ecu(board):
    """Simulated Ethernet zonal ECU at 192.168.0.30, reached by the board over 100BASE-T1."""
    try:
        ecu = SimDoipEcu().start()
    except OSError as exc:
        pytest.fail(f"cannot listen on {NODE_IP}:13400 ({exc}); add the address with "
                    f"sudo OpenBSW/scripts/net-up.sh")
    yield ecu
    ecu.stop()


@pytest.fixture(autouse=True)
def _reset_eth(request):
    if "eth_ecu" in request.fixturenames:
        ecu = request.getfixturevalue("eth_ecu")
        ecu.resume()
        ecu.reset()
    yield


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
    assert version.startswith("zgw ") and f" rt {ROUTING['hash']}" in version, version
    table = tester.read_did(GATEWAY, 0xFD00)[3:]
    assert table[0] == len(ROUTING["routes"])
    assert struct.unpack_from(">HH", table, 1) == (GATEWAY, FUNCTIONAL)
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


# --- routing to the Ethernet zonal ECU over DoIP --------------------------------------------

def test_board_doip_routing(tester, eth_ecu):
    """SWR-006, SWR-019, SWR-051: the board's DoIP client activates routing from 0x0E10 and
    routes the request; the node's response reaches the tester from 0x1040."""
    eth_ecu.disconnect()
    time.sleep(0.2)
    result = tester.request(ETH, b"\x22\xF1\x95")
    assert result.ack is True
    assert result.responses == [(ETH, b"\x62\xF1\x95" + SW_VERSION)]
    assert eth_ecu.record.activations == [(0x0E10, 0x00)]
    assert eth_ecu.record.requests == [Message(0x0E10, ETH, b"\x22\xF1\x95")]


def test_board_doip_large_and_pending(tester, eth_ecu):
    """SWR-014, SWR-016, SWR-017: 3000-byte response, 4000-byte request and response pending."""
    result = tester.request(ETH, b"\x22\xF1\xA0", wait=2.0)
    assert result.responses == [(ETH, b"\x62\xF1\xA0" + bytes(i & 0xFF for i in range(LARGE_SIZE)))]
    request = b"\x22\xF1\xB0" + bytes(range(256)) * 15 + bytes(157)
    assert tester.request(ETH, request, wait=2.0).responses == [(ETH, b"\x62\xF1\xB0\x0F\xA0")]
    assert eth_ecu.record.requests[-1].payload == request
    pending = tester.request(ETH, b"\x22\xF1\xA1", wait=2.0)
    assert pending.payloads(ETH) == [b"\x7F\x22\x78", b"\x62\xF1\xA1\x01"]


def test_board_doip_functional(tester, eth_ecu):
    """SWR-013, SWR-019: functional TesterPresent answered by the gateway and the DoIP ECU."""
    assert tester.request(ETH, b"\x3E\x00").ack is True
    result = tester.request(FUNCTIONAL, b"\x3E\x00", wait=0.5, until_final=False)
    assert result.ack is True
    assert sorted(result.responses) == sorted([(GATEWAY, b"\x7E\x00"), (ETH, b"\x7E\x00")])


def test_board_doip_latency(tester, eth_ecu):
    """SWR-060 (target): routed round trip tester -> board -> DoIP ECU -> tester, 200 samples."""
    assert tester.request(ETH, b"\x3E\x00").ack is True
    samples = []
    for _ in range(200):
        start = time.perf_counter()
        assert tester.request(ETH, b"\x3E\x00").responses == [(ETH, b"\x7E\x00")]
        samples.append((time.perf_counter() - start) * 1000)
    p95 = statistics.quantiles(samples, n=20)[18]
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "board-latency.txt").open("a") as f:
        f.write(f"routed_doip_p50_ms={statistics.median(samples):.2f}\nrouted_doip_p95_ms={p95:.2f}\n")
    assert p95 <= 20.0, f"routed round trip p95 {p95:.2f} ms"


def test_board_doip_node_failures(tester, eth_ecu):
    """SWR-006, SWR-024, SWR-025: unreachable and silent node: requests fail, the route is
    freed, three failures set U0142; after recovery ClearDTC resets it."""
    u0142 = 0xC14200
    tester.request(GATEWAY, b"\x14\xFF\xFF\xFF")
    eth_ecu.suspend()
    time.sleep(0.2)
    unreachable = tester.request(ETH, b"\x22\xF1\x95", wait=0.5)
    assert unreachable.ack is True and unreachable.responses == []
    eth_ecu.resume()
    eth_ecu.mode = "silent"
    for _ in range(2):
        assert tester.request(ETH, b"\x3E\x00", wait=0.3).ack is True
    status = read_dtcs(tester)[u0142]
    assert status & 0x09 == 0x09, f"testFailed + confirmedDTC expected, got {status:#04x}"
    eth_ecu.mode = "normal"
    assert tester.request(ETH, b"\x3E\x00").responses == [(ETH, b"\x7E\x00")]
    assert tester.request(GATEWAY, b"\x14\xFF\xFF\xFF").responses[-1][1] == b"\x54"
    assert read_dtcs(tester, 0x09).get(u0142) is None
