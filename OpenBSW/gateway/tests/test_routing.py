# SPDX-License-Identifier: Apache-2.0
"""Integration tests: routing, gateway UDS server, robustness, non-interference (SWE.5).

Each test names the software requirement(s) it verifies.
"""

from __future__ import annotations

import socket
import struct
import time

from doip_tester import FRONT, FUNCTIONAL, GATEWAY, REAR, TESTER, Tester
from sim_ecu import LARGE_SIZE, SW_VERSION

GATEWAY_COUNTERS = ("local", "functional", "unknown_target", "no_buffer")
ROUTE_COUNTERS = ("requests", "responses", "pending", "timeouts", "busy", "too_large", "tx_fail", "discarded")


def read_stats(tester: Tester) -> dict:
    data = tester.read_did(GATEWAY, 0xFD01)[3:]
    stats = dict(zip(GATEWAY_COUNTERS, struct.unpack_from(">4H", data, 0)))
    count, offset = data[8], 9
    for _ in range(count):
        addr = struct.unpack_from(">H", data, offset)[0]
        stats[addr] = dict(zip(ROUTE_COUNTERS, struct.unpack_from(">8H", data, offset + 2)))
        offset += 18
    return stats


def read_dtcs(tester: Tester, mask: int = 0xFF) -> dict[int, int]:
    result = tester.request(GATEWAY, bytes([0x19, 0x02, mask]))
    payload = result.responses[-1][1]
    assert payload[:2] == b"\x59\x02", payload.hex()
    records = payload[3:]
    return {int.from_bytes(records[i:i + 3], "big"): records[i + 3] for i in range(0, len(records), 4)}


# --- gateway UDS server -------------------------------------------------------------------

def test_local_identification(tester):
    """SWR-011, SWR-021: identification DIDs answered by 0x1010 from source 0x1010."""
    result = tester.request(GATEWAY, b"\x22\xF1\x90")
    assert result.ack is True
    assert result.responses == [(GATEWAY, b"\x62\xF1\x90" + b"TCAPSZONALGW00001")]
    version = tester.read_did(GATEWAY, 0xF195)[3:].decode()
    assert version.startswith("zgw ") and " obsw " in version and " rt " in version, version
    assert tester.read_did(GATEWAY, 0xF18C)[3:] == b"ZGW-POSIX-0001"


def test_routing_table_did(tester):
    """SWR-022: FD00 equals the routing configuration."""
    data = tester.read_did(GATEWAY, 0xFD00)[3:]
    count, gw, func = data[0], *struct.unpack_from(">HH", data, 1)
    assert (count, gw, func) == (2, GATEWAY, FUNCTIONAL)
    routes = [struct.unpack_from(">HBHHHH", data, 5 + 11 * i) for i in range(count)]
    assert routes == [(REAR, 0, 0x7E1, 0x7E9, 150, 5100), (FRONT, 0, 0x7E2, 0x7EA, 150, 5100)]


def test_local_services_and_nrcs(tester):
    """SWR-020, SWR-027: sessions, TesterPresent and negative response codes."""
    assert tester.request(GATEWAY, b"\x10\x03").responses[-1][1][:2] == b"\x50\x03"
    assert tester.request(GATEWAY, b"\x3E\x00").responses[-1][1] == b"\x7E\x00"
    suppressed = tester.request(GATEWAY, b"\x3E\x80", wait=0.4)
    assert suppressed.ack is True and suppressed.responses == []
    assert tester.request(GATEWAY, b"\x10\x01").responses[-1][1][:2] == b"\x50\x01"
    assert tester.request(GATEWAY, b"\x23\x00").responses[-1][1] == b"\x7F\x23\x11"   # SID not supported
    assert tester.request(GATEWAY, b"\x22\x12\x34").responses[-1][1] == b"\x7F\x22\x31"  # DID unknown


# --- physical routing --------------------------------------------------------------------

def test_physical_routing_to_can_ecu(tester, rear_ecu, can_log):
    """SWR-012: request on 0x7E1, ECU response returned to the tester from 0x1020."""
    mark = can_log.mark()
    result = tester.request(REAR, b"\x22\xF1\x95")
    assert result.ack is True
    assert result.responses == [(REAR, b"\x62\xF1\x95" + SW_VERSION)]
    assert rear_ecu.requests == [b"\x22\xF1\x95"]
    frames = can_log.since(mark)
    request_frames = [f for f in frames if f.arbitration_id == 0x7E1]
    assert request_frames and all(len(f.data) == 8 for f in request_frames), "SWR-018 padding"
    assert request_frames[0].data[4:] == b"\xCC\xCC\xCC\xCC"


def test_unknown_target_nack(tester):
    """SWR-003: unknown target address -> NACK 0x03."""
    result = tester.request(0x1099, b"\x3E\x00")
    assert (result.ack, result.nack_code) == (False, 0x03)


def test_multiframe_response_and_transparency(tester, rear_ecu):
    """SWR-014, SWR-018: multi-frame response forwarded byte for byte."""
    result = tester.request(REAR, b"\x22\xF1\xA0", wait=3.0)
    assert result.ack is True
    assert result.responses == [(REAR, b"\x62\xF1\xA0" + bytes(i & 0xFF for i in range(LARGE_SIZE)))]


def test_negative_response_passthrough(tester, rear_ecu):
    """SWR-014: negative responses forwarded unchanged."""
    assert tester.request(REAR, b"\x22\x12\x34").responses == [(REAR, b"\x7F\x22\x31")]


def test_response_pending_passthrough(tester, rear_ecu):
    """SWR-014, SWR-016: NRC 0x78 forwarded, then the final response within P2*."""
    result = tester.request(REAR, b"\x22\xF1\xA1", wait=2.0)
    assert result.responses == [(REAR, b"\x7F\x22\x78"), (REAR, b"\x62\xF1\xA1\x01")]


def test_large_request(tester, rear_ecu):
    """SWR-017: 4095-byte request routed; 4096 rejected with NACK 0x04."""
    payload = b"\x22\xF1\xB0" + bytes(4092)
    result = tester.request(REAR, payload, wait=5.0)
    assert result.ack is True, result
    assert result.responses == [(REAR, b"\x62\xF1\xB0\x0F\xFF")]
    assert rear_ecu.requests[-1] == payload
    too_large = tester.request(REAR, payload + b"\x00", wait=1.0)
    assert (too_large.ack, too_large.nack_code) == (False, 0x04), too_large


# --- concurrency and timeouts -------------------------------------------------------------

def test_busy_route_nack_and_timeout(tester, rear_ecu):
    """SWR-015, SWR-016: one outstanding request per route; P2 releases it."""
    before = read_stats(tester)[REAR]
    rear_ecu.mode = "silent"
    first = tester.request(REAR, b"\x22\xF1\x95", wait=0.05)
    assert first.ack is True and first.responses == []
    second = tester.request(REAR, b"\x22\xF1\x95", wait=0.05)
    assert (second.ack, second.nack_code) == (False, 0x05)
    time.sleep(0.3)  # P2 = 150 ms
    rear_ecu.mode = "normal"
    assert tester.request(REAR, b"\x22\xF1\x95").responses[-1][1][:3] == b"\x62\xF1\x95"
    after = read_stats(tester)[REAR]
    assert after["busy"] == before["busy"] + 1
    assert after["timeouts"] == before["timeouts"] + 1


def test_parallel_routes(tester, rear_ecu, front_ecu):
    """SWR-015: requests to two routes outstanding at the same time both complete."""
    tester.send(REAR, b"\x22\xF1\xA1")    # rear answers after 0.4 s (pending)
    tester.send(FRONT, b"\x22\xF1\x95")
    result = tester.collect(2.0, until_final=False)
    finals = {s: p for s, p in result.responses if p[:1] != b"\x7F"}
    assert finals.get(FRONT, b"")[:3] == b"\x62\xF1\x95"
    assert finals.get(REAR) == b"\x62\xF1\xA1\x01"


def test_tester_disconnect_releases_route(gateway, rear_ecu):
    """SWR-041: a disconnect frees the route at once; the late response is discarded."""
    rear_ecu.mode = "silent"
    first = Tester()
    first.request(REAR, b"\x22\xF1\x95", wait=0.05)
    first.close()
    time.sleep(0.05)
    second = Tester(0x0E81)
    try:
        result = second.request(REAR, b"\x3E\x00", wait=0.1)
        assert result.ack is True, "route still busy after disconnect"
    finally:
        rear_ecu.mode = "normal"
        time.sleep(0.3)
        second.close()


def test_unsolicited_response_discarded(tester, rear_ecu):
    """SWR-042: CAN response without a pending request reaches no tester and is counted."""
    before = read_stats(tester)[REAR]["discarded"]
    rear_ecu.send_raw(bytes([0x03, 0x7E, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC]))
    stray = tester.collect(0.3)
    assert stray.responses == []
    assert read_stats(tester)[REAR]["discarded"] == before + 1


# --- functional routing ---------------------------------------------------------------------

def test_functional_tester_present(tester, rear_ecu, front_ecu, can_log):
    """SWR-013: one single frame on 0x7DF; one response per node, own source address."""
    mark = can_log.mark()
    result = tester.request(FUNCTIONAL, b"\x3E\x00", wait=0.5, until_final=False)
    assert result.ack is True
    assert sorted(result.responses) == sorted([(GATEWAY, b"\x7E\x00"), (REAR, b"\x7E\x00"), (FRONT, b"\x7E\x00")])
    functional = [f for f in can_log.since(mark) if f.arbitration_id == 0x7DF]
    assert len(functional) == 1 and functional[0].data[:3] == b"\x02\x3E\x00"


def test_functional_suppressed_and_too_large(tester, rear_ecu):
    """SWR-013: 3E 80 yields only the ACK; functional requests > 7 bytes -> NACK 0x04."""
    suppressed = tester.request(FUNCTIONAL, b"\x3E\x80", wait=0.4, until_final=False)
    assert suppressed.ack is True and suppressed.responses == []
    assert rear_ecu.functional_requests[-1] == b"\x3E\x80"
    too_long = tester.request(FUNCTIONAL, bytes(8), wait=0.4)
    assert (too_long.ack, too_long.nack_code) == (False, 0x04)


# --- node monitoring and fault memory ----------------------------------------------------------

def test_lost_communication_dtc(tester, gateway, can_log):
    """SWR-024, SWR-025: 3 timeouts set U0141; a response passes it; 14 FFFFFF clears."""
    U0141 = 0xC14100
    assert read_dtcs(tester).get(U0141, 0) & 0x01 == 0
    for _ in range(3):
        tester.request(FRONT, b"\x3E\x00", wait=0.3)  # no front ECU on the bus
    status = read_dtcs(tester)[U0141]
    assert status & 0x09 == 0x09, f"testFailed+confirmed expected, got {status:#04x}"
    # supported DTCs (19 0A) include both routes' DTCs
    supported = tester.request(GATEWAY, b"\x19\x0A").responses[-1][1]
    assert b"\xC1\x40\x00" in supported and b"\xC1\x41\x00" in supported


def test_dtc_passes_and_clears(tester, front_ecu):
    """SWR-024, SWR-025: a valid response clears testFailed; ClearDTC resets the status."""
    U0141 = 0xC14100
    assert tester.request(FRONT, b"\x3E\x00").responses == [(FRONT, b"\x7E\x00")]
    status = read_dtcs(tester)[U0141]
    assert status & 0x01 == 0 and status & 0x08, f"{status:#04x}"
    assert tester.request(GATEWAY, b"\x14\xFF\xFF\xFF").responses[-1][1] == b"\x54"
    assert read_dtcs(tester, 0x09).get(U0141) is None


# --- non-interference ----------------------------------------------------------------------------

def test_no_traffic_when_idle(gateway, can_log):
    """SWR-024, SWR-030: the gateway sends nothing on CAN without tester requests."""
    mark = can_log.mark()
    time.sleep(2.0)
    assert can_log.since(mark) == []


def test_lighting_frames_ignored(tester, gateway, can_log):
    """SWR-030: lighting traffic (0x1F1/0x1F4) changes no gateway counter."""
    before = read_stats(tester)
    bus_frames = [(0x1F1, b"\x06" + bytes(7)), (0x1F4, b"\x03" + bytes(7))]
    import can
    with can.Bus(channel="vcan0", interface="socketcan") as bus:
        for _ in range(20):
            for can_id, data in bus_frames:
                bus.send(can.Message(arbitration_id=can_id, data=data, is_extended_id=False))
    time.sleep(0.2)
    after = read_stats(tester)
    for key in (REAR, FRONT):
        assert after[key] == before[key]


def test_can_identifier_discipline(can_log):
    """SWR-030: over this module, only diagnostic IDs (and the injected lighting frames)."""
    ids = {f.arbitration_id for f in can_log.frames}
    allowed = {0x7DF, 0x7E1, 0x7E2, 0x7E9, 0x7EA, 0x1F1, 0x1F4}
    assert ids <= allowed, sorted(hex(i) for i in ids - allowed)
    gateway_tx = {0x7DF, 0x7E1, 0x7E2}
    assert gateway_tx & ids, "gateway traffic expected"
