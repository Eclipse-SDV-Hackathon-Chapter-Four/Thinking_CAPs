# SPDX-License-Identifier: Apache-2.0
"""Integration tests of DoIP routing to an Ethernet zonal ECU (SWE.5).

The gateway reaches route 0x1040 with its DoIP client (SWR-006, SWR-019): TCP to the
simulated ECU at 192.168.0.30:13400 (sim_doip_ecu.py), routing activation from 0x0E10,
then diagnostic messages. Each test names the software requirement(s) it verifies.
"""

from __future__ import annotations

import struct
import time

from doip_tester import ETH, FUNCTIONAL, GATEWAY, REAR, Tester
from sim_doip_ecu import LARGE_SIZE, SW_VERSION, Message

NODE_TESTER = 0x0E10
U0142 = 0xC14200
# DoIP client delivery budget (DoIpClientSystem::DELIVERY_TIMEOUT_MS) plus margin
DELIVERY_TIMEOUT_S = 1.7


def read_route_stats(tester: Tester) -> dict[int, tuple[int, ...]]:
    """FD01: requests, responses, pending, timeouts, busy, too_large, tx_fail, discarded."""
    data = tester.read_did(GATEWAY, 0xFD01)[3:]
    count, offset, routes = data[8], 9, {}
    for _ in range(count):
        address = struct.unpack_from(">H", data, offset)[0]
        routes[address] = struct.unpack_from(">8H", data, offset + 2)
        offset += 18
    return routes


def read_dtcs(tester: Tester, mask: int = 0xFF) -> dict[int, int]:
    payload = tester.request(GATEWAY, bytes([0x19, 0x02, mask])).responses[-1][1]
    records = payload[3:]
    return {int.from_bytes(records[i:i + 3], "big"): records[i + 3] for i in range(0, len(records), 4)}


# --- routing --------------------------------------------------------------------------------

def test_doip_physical_routing(tester, eth_ecu, can_log):
    """SWR-006, SWR-019, SWR-030: routing activation from 0x0E10, request and response
    over DoIP; nothing on CAN."""
    eth_ecu.disconnect()
    time.sleep(0.1)
    mark = can_log.mark()
    result = tester.request(ETH, b"\x22\xF1\x95")
    assert result.ack is True
    assert result.responses == [(ETH, b"\x62\xF1\x95" + SW_VERSION)]
    assert eth_ecu.record.activations == [(NODE_TESTER, 0x00)]
    assert eth_ecu.record.requests == [Message(NODE_TESTER, ETH, b"\x22\xF1\x95")]
    time.sleep(0.1)
    assert can_log.since(mark) == []


def test_doip_connection_reused(tester, eth_ecu):
    """SWR-006: the connection and its routing activation are kept for later requests."""
    for _ in range(5):
        assert tester.request(ETH, b"\x3E\x00").responses == [(ETH, b"\x7E\x00")]
    assert eth_ecu.record.connections <= 1 and len(eth_ecu.record.activations) <= 1


def test_doip_large_messages(tester, eth_ecu):
    """SWR-014, SWR-017: a 3000-byte response and a 4000-byte request pass unchanged."""
    result = tester.request(ETH, b"\x22\xF1\xA0", wait=2.0)
    assert result.responses == [(ETH, b"\x62\xF1\xA0" + bytes(i & 0xFF for i in range(LARGE_SIZE)))]
    request = b"\x22\xF1\xB0" + bytes(range(256)) * 15 + bytes(157)
    assert len(request) == 4000
    result = tester.request(ETH, request, wait=2.0)
    assert result.responses == [(ETH, b"\x62\xF1\xB0\x0F\xA0")]
    assert eth_ecu.record.requests[-1].payload == request


def test_doip_response_pending(tester, eth_ecu):
    """SWR-016: response pending (NRC 0x78) is passed through, then the final response."""
    result = tester.request(ETH, b"\x22\xF1\xA1", wait=2.0)
    assert result.payloads(ETH) == [b"\x7F\x22\x78", b"\x62\xF1\xA1\x01"]


def test_doip_negative_response_passthrough(tester, eth_ecu):
    """SWR-014: a negative response of the node reaches the tester unchanged."""
    assert tester.request(ETH, b"\x2E\xF1\x90\x00").responses == [(ETH, b"\x7F\x2E\x11")]


def test_doip_functional(tester, eth_ecu, rear_ecu):
    """SWR-013, SWR-019: a functional request reaches the gateway, the CAN ECU and the
    DoIP ECU; all responses go back to the tester."""
    assert tester.request(ETH, b"\x3E\x00").ack is True  # routing active towards 0x1040
    result = tester.request(FUNCTIONAL, b"\x3E\x00", wait=0.5, until_final=False)
    assert result.ack is True
    assert sorted(result.responses) == sorted(
        [(GATEWAY, b"\x7E\x00"), (REAR, b"\x7E\x00"), (ETH, b"\x7E\x00")])
    assert eth_ecu.record.requests[-1] == Message(NODE_TESTER, FUNCTIONAL, b"\x3E\x00")


def test_doip_alive_check(tester, eth_ecu):
    """SWR-006: the gateway answers the node's alive check with its tester address."""
    assert tester.request(ETH, b"\x3E\x00").ack is True
    eth_ecu.send_alive_check()
    assert eth_ecu.wait_for(lambda: eth_ecu.record.alive_responses == [NODE_TESTER])


def test_doip_unsolicited_response_discarded(tester, eth_ecu):
    """SWR-042: a diagnostic message from the node without a pending request is dropped."""
    assert tester.request(ETH, b"\x3E\x00").ack is True
    before = read_route_stats(tester)[ETH]
    eth_ecu.send_diagnostic(b"\x62\xF1\x95\x00")
    assert tester.collect(0.3).responses == []
    assert read_route_stats(tester)[ETH][7] == before[7] + 1


# --- failures -------------------------------------------------------------------------------

def test_doip_node_nack(tester, eth_ecu):
    """SWR-019: a diagnostic message NACK from the node fails the request at once: no
    response, route free, transmission failure counted."""
    before = read_route_stats(tester)[ETH]
    eth_ecu.mode = "nack"
    result = tester.request(ETH, b"\x22\xF1\x95", wait=0.3)
    assert result.ack is True and result.responses == []
    eth_ecu.mode = "normal"
    assert tester.request(ETH, b"\x22\xF1\x95").responses == [(ETH, b"\x62\xF1\x95" + SW_VERSION)]
    after = read_route_stats(tester)[ETH]
    assert after[6] == before[6] + 1, (before, after)


def test_doip_no_acknowledgement(tester, eth_ecu):
    """SWR-006: no acknowledgement within the delivery budget: the connection is closed, the
    route freed, and the next request opens a new connection."""
    eth_ecu.mode = "no_ack"
    result = tester.request(ETH, b"\x22\xF1\x95", wait=0.3)
    assert result.ack is True and result.responses == []
    busy = tester.request(ETH, b"\x3E\x00", wait=0.2)
    assert (busy.ack, busy.nack_code) == (False, 0x05)
    assert eth_ecu.wait_for(lambda: not eth_ecu.connected, timeout=DELIVERY_TIMEOUT_S)
    eth_ecu.mode = "normal"
    connections = eth_ecu.record.connections
    assert tester.request(ETH, b"\x22\xF1\x95").responses == [(ETH, b"\x62\xF1\x95" + SW_VERSION)]
    assert eth_ecu.record.connections == connections + 1


def test_doip_activation_refused(tester, eth_ecu):
    """SWR-006: a refused routing activation fails the request; the route is free again."""
    eth_ecu.disconnect()
    eth_ecu.mode = "refuse"
    result = tester.request(ETH, b"\x22\xF1\x95", wait=0.5)
    assert result.ack is True and result.responses == []
    assert eth_ecu.record.activations == [(NODE_TESTER, 0x00)]
    eth_ecu.mode = "normal"
    assert tester.request(ETH, b"\x22\xF1\x95").responses == [(ETH, b"\x62\xF1\x95" + SW_VERSION)]


def test_doip_node_closes_connection(tester, eth_ecu):
    """SWR-006: after the node closes the connection, the next request reconnects."""
    assert tester.request(ETH, b"\x3E\x00").ack is True
    eth_ecu.disconnect()
    time.sleep(0.2)
    assert tester.request(ETH, b"\x22\xF1\x95").responses == [(ETH, b"\x62\xF1\x95" + SW_VERSION)]
    assert eth_ecu.record.connections == 1


def test_doip_node_unreachable(tester, eth_ecu):
    """SWR-006: a refused TCP connection fails the request well before the delivery budget."""
    eth_ecu.suspend()
    time.sleep(0.1)
    start = time.time()
    result = tester.request(ETH, b"\x22\xF1\x95", wait=0.3)
    assert result.ack is True and result.responses == []
    # the route is free again: a second request is accepted, not NACKed as busy
    second = tester.request(ETH, b"\x3E\x00", wait=0.3)
    assert second.ack is True, second
    assert time.time() - start < DELIVERY_TIMEOUT_S
    eth_ecu.resume()


def test_doip_lost_communication_dtc(tester, eth_ecu):
    """SWR-024, SWR-025: three unanswered requests to 0x1040 set U0142; ClearDTC resets it."""
    tester.request(GATEWAY, b"\x14\xFF\xFF\xFF")
    assert read_dtcs(tester).get(U0142, 0) & 0x01 == 0
    eth_ecu.mode = "silent"
    for _ in range(3):
        assert tester.request(ETH, b"\x3E\x00", wait=0.3).ack is True
    status = read_dtcs(tester)[U0142]
    assert status & 0x09 == 0x09, f"testFailed + confirmedDTC expected, got {status:#04x}"
    eth_ecu.mode = "normal"
    assert tester.request(ETH, b"\x3E\x00").responses == [(ETH, b"\x7E\x00")]
    assert tester.request(GATEWAY, b"\x14\xFF\xFF\xFF").responses[-1][1] == b"\x54"
    assert read_dtcs(tester, 0x09).get(U0142) is None


# --- node reachability routine F000 ---------------------------------------------------------

def test_reachability_routine(tester, eth_ecu, rear_ecu):
    """SWR-026: 31 01 F000 probes every route; 31 03 F000 reports one byte per route in
    routing-table order: CAN 0x1020 answers, CAN 0x1030 has no ECU, DoIP 0x1040 answers;
    with 0x1020 silent only the DoIP route is reached."""
    start = tester.request(GATEWAY, b"\x31\x01\xF0\x00")
    assert start.responses == [(GATEWAY, b"\x71\x01\xF0\x00")]
    running = tester.request(GATEWAY, b"\x31\x03\xF0\x00").responses[-1][1]
    assert running[:5] == b"\x71\x03\xF0\x00\x01"
    time.sleep(2.2)
    assert tester.request(GATEWAY, b"\x31\x03\xF0\x00").responses == [
        (GATEWAY, b"\x71\x03\xF0\x00\x00\x03\x01\x00\x01")]
    assert rear_ecu.requests[-1] == b"\x3E\x00"
    assert eth_ecu.record.requests[-1] == Message(NODE_TESTER, ETH, b"\x3E\x00")

    rear_ecu.mode = "silent"
    assert tester.request(GATEWAY, b"\x31\x01\xF0\x00").responses == [(GATEWAY, b"\x71\x01\xF0\x00")]
    time.sleep(2.2)
    assert tester.request(GATEWAY, b"\x31\x03\xF0\x00").responses == [
        (GATEWAY, b"\x71\x03\xF0\x00\x00\x03\x00\x00\x01")]
