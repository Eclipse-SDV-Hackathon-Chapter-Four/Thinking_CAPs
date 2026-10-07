# SPDX-License-Identifier: Apache-2.0
"""Integration tests: DoIP entity behaviour, start-up/shutdown and latency (SWE.5)."""

from __future__ import annotations

import re
import socket
import statistics
import struct
import time

import pytest
from doipclient import DoIPClient
from doipclient.messages import RoutingActivationRequest

from conftest import RESULTS, GatewayProcess, gateway_elf
from doip_tester import GATEWAY, GATEWAY_IP, REAR, Tester
from sim_ecu import SimEcu

VIN = b"TCAPSZONALGW00001"
ANNOUNCEMENT = 0x0004


def parse_announcement(datagram: bytes) -> dict | None:
    if len(datagram) < 8:
        return None
    _version, _inverse, payload_type, length = struct.unpack(">BBHI", datagram[:8])
    if payload_type != ANNOUNCEMENT or length < 32:
        return None
    body = datagram[8:8 + length]
    return {"vin": body[:17], "address": struct.unpack(">H", body[17:19])[0], "eid": body[19:25]}


@pytest.fixture(scope="module")
def started(can_log):
    """Starts the gateway while listening for its vehicle announcements."""
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.bind(("", 13400))
    udp.settimeout(0.1)
    mark = can_log.mark()
    proc = GatewayProcess(gateway_elf(), RESULTS / "test_lifecycle-gateway.log").start()
    announcements, deadline = [], time.time() + 3.0
    while time.time() < deadline:
        try:
            data, sender = udp.recvfrom(4096)
        except socket.timeout:
            continue
        parsed = parse_announcement(data)
        if parsed and sender[0] == GATEWAY_IP:
            announcements.append((time.time() - proc.started_at, parsed))
    udp.close()
    yield {"proc": proc, "announcements": announcements, "can_mark": mark}
    if proc.proc.poll() is None:
        proc.stop()


def test_vehicle_announcement(started):
    """SWR-001: three announcements after start-up with VIN and gateway address."""
    announcements = started["announcements"]
    assert len(announcements) == 3, announcements
    for _, parsed in announcements:
        assert parsed["vin"] == VIN and parsed["address"] == GATEWAY
    gaps = [b[0] - a[0] for a, b in zip(announcements, announcements[1:])]
    assert all(0.3 <= gap <= 0.8 for gap in gaps), gaps


def test_vehicle_identification_requests(started):
    """SWR-001: generic, by-VIN and by-EID identification requests are answered."""
    _, entity = DoIPClient.get_entity(ecu_ip_address=GATEWAY_IP, protocol_version=2)
    assert bytes(entity.vin.encode() if isinstance(entity.vin, str) else entity.vin) == VIN
    assert entity.logical_address == GATEWAY
    client = DoIPClient(GATEWAY_IP, GATEWAY, client_logical_address=0x0E80, protocol_version=2)
    try:
        by_vin = client.request_vehicle_identification(vin=VIN.decode())
        assert by_vin.logical_address == GATEWAY
        by_eid = client.request_vehicle_identification(eid=bytes(entity.eid))
        assert by_eid.logical_address == GATEWAY
    finally:
        client.close()


def test_routing_activation_rules(started):
    """SWR-002: tester range accepted; unknown source rejected (0x00); type 0x01 rejected (0x06)."""
    accepted = Tester(0x0EF5)
    accepted.close()
    with pytest.raises(ConnectionRefusedError) as unknown:
        DoIPClient(GATEWAY_IP, GATEWAY, client_logical_address=0x0123, protocol_version=2)
    assert "0" in str(unknown.value) or "Unknown" in str(unknown.value)
    with pytest.raises(ConnectionRefusedError) as wwh_obd:
        DoIPClient(GATEWAY_IP, GATEWAY, client_logical_address=0x0E80, protocol_version=2,
                   activation_type=RoutingActivationRequest.ActivationType.DiagnosticRequiredByRegulation)
    assert "6" in str(wwh_obd.value) or "nsupported" in str(wwh_obd.value)


def test_two_testers_at_once(started):
    """SWR-002: at least two simultaneous tester connections."""
    first, second = Tester(0x0E80), Tester(0x0E81)
    try:
        assert first.request(GATEWAY, b"\x3E\x00").responses == [(GATEWAY, b"\x7E\x00")]
        assert second.request(GATEWAY, b"\x3E\x00").responses == [(GATEWAY, b"\x7E\x00")]
    finally:
        first.close()
        second.close()


def test_entity_status_and_power_mode(started):
    """SWR-005: node type gateway, socket limits and current count; power mode ready."""
    tester = Tester()
    try:
        status = tester.client.request_entity_status()
        assert status.node_type == 0x00  # gateway
        assert status.max_concurrent_sockets >= 2
        assert status.currently_open_sockets >= 1
        assert tester.client.request_diagnostic_power_mode().diagnostic_power_mode == 0x01
    finally:
        tester.close()


def test_forwarding_latency(started, can_log):
    """SWR-060: gateway-added latency p95 <= 10 ms per direction (single frames, 200 round trips)."""
    ecu = SimEcu("vcan0", 0x7E1, 0x7E9, "rear").start()
    tester = Tester()
    downstream, upstream = [], []
    try:
        for _ in range(200):
            mark = can_log.mark()
            sent = time.time()
            result = tester.request(REAR, b"\x22\xF1\x95", wait=1.0)
            received = time.time()
            assert result.responses, "no response"
            frames = can_log.since(mark)
            request = next(f for f in frames if f.arbitration_id == 0x7E1)
            response = [f for f in frames if f.arbitration_id == 0x7E9][-1]
            downstream.append((request.timestamp - sent) * 1000)
            upstream.append((received - response.timestamp) * 1000)
    finally:
        tester.close()
        ecu.stop()
    p95_down = statistics.quantiles(downstream, n=20)[18]
    p95_up = statistics.quantiles(upstream, n=20)[18]
    (RESULTS / "latency.txt").write_text(
        f"samples={len(downstream)}\ndown_p50_ms={statistics.median(downstream):.2f}\n"
        f"down_p95_ms={p95_down:.2f}\nup_p50_ms={statistics.median(upstream):.2f}\nup_p95_ms={p95_up:.2f}\n")
    assert p95_down <= 10.0, f"DoIP -> CAN p95 {p95_down:.2f} ms"
    assert p95_up <= 10.0, f"CAN -> DoIP p95 {p95_up:.2f} ms"


def test_periodic_statistics_log(started):
    """SWR-054: start-up identity and a statistics line every 30 s, matching FD01."""
    proc = started["proc"]
    assert "routing table " in proc.text() and " routes" in proc.text()
    deadline = proc.started_at + 35.0
    while time.time() < deadline and "stats local=" not in proc.text():
        time.sleep(0.5)
    log = proc.text()
    assert "stats local=" in log, "no statistics line within 35 s"
    tester = Tester()
    try:
        data = tester.read_did(GATEWAY, 0xFD01)[3:]
    finally:
        tester.close()
    local_requests = struct.unpack_from(">H", data, 0)[0]
    logged = int(re.findall(r"stats local=(\d+)", log)[-1])
    assert logged <= local_requests  # the log is a snapshot taken before the FD01 request


def test_shutdown(started, can_log):
    """SWR-044: SIGINT ends the gateway with status 0 within 1 s; no CAN frame afterwards."""
    proc = started["proc"]
    begin = time.time()
    code = proc.stop()
    elapsed = time.time() - begin
    assert code == 0 and elapsed <= 1.0, (code, elapsed)
    mark = can_log.mark()
    time.sleep(0.5)
    assert can_log.since(mark) == []
    # start-up order: announcements only after the CAN and ISO-TP levels ran (SWR-044)
    log = proc.text()
    assert log.find("Run level 5") < log.find("Run level 7") and "DoIp Initialized" in log
