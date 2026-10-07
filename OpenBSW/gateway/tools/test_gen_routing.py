# SPDX-License-Identifier: Apache-2.0
"""Unit tests of the routing configuration generator (SWR-010, SWR-052)."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
import gen_routing  # noqa: E402

CONFIG = Path(__file__).parents[1] / "config" / "routing.yaml"


@pytest.fixture
def data() -> dict:
    return yaml.safe_load(CONFIG.read_text())


def test_shipped_configuration_is_valid(data):
    cfg = gen_routing.validate(data)
    assert cfg["logical_address"] == 0x1010 and len(cfg["routes"]) == 3
    assert [r["transport"] for r in cfg["routes"]] == ["docan", "docan", "doip"]
    assert cfg["routes"][2]["ip_address"] == "192.168.0.30"
    assert len(cfg["hash"]) == 8


def test_hash_changes_with_any_address(data):
    changed = copy.deepcopy(data)
    changed["routes"][0]["request_can_id"] = 0x7E3
    assert gen_routing.validate(changed)["hash"] != gen_routing.validate(data)["hash"]


@pytest.mark.parametrize("mutate, message", [
    (lambda d: d["routes"].append(dict(d["routes"][0])), "duplicates"),
    (lambda d: d["routes"][1].update(logical_address=0x1010), "duplicates gateway"),
    (lambda d: d["routes"][1].update(logical_address=0x0E20), "tester_range"),
    (lambda d: d["routes"][1].update(request_can_id=0x7E9), "duplicates"),
    (lambda d: d["routes"][1].update(response_can_id=0x7DF), "duplicates"),
    (lambda d: d["routes"][0].update(request_can_id=0x1F1), "outside"),
    (lambda d: d["routes"][0].update(p2_ms=6000), "p2_ms"),
    (lambda d: d["routes"][0].update(max_length=4096), "max_length"),
    (lambda d: d["routes"][0].update(lost_comm_dtc=0x1000000), "3-byte"),
    (lambda d: d["routes"][0].update(transport="lin"), "transport"),
    (lambda d: d["routes"][0].update(p2_ms="fast"), "integer"),
    (lambda d: d["gateway"].update(vin="SHORT"), "17 ASCII"),
    (lambda d: d["gateway"].update(functional_can_id=0x700), "outside"),
    (lambda d: d["gateway"].update(tester_range=[0x0EFF, 0x0E00]), "tester_range"),
    (lambda d: d["gateway"].update(logical_address=0x0E05), "inside tester_range"),
    (lambda d: d.update(routes=[]), "at least one route"),
    # DoIP routes
    (lambda d: d["routes"][2].update(ip_address="192.168.0.300"), "IPv4"),
    (lambda d: d["routes"][2].update(ip_address=None), "IPv4"),
    (lambda d: d["routes"][2].update(ip_address="0.0.0.0"), "unicast"),
    (lambda d: d["routes"][2].update(ip_address="127.0.0.1"), "unicast"),
    (lambda d: d["routes"][2].update(ip_address="224.0.0.1"), "unicast"),
    (lambda d: d["routes"][2].update(ip_address="255.255.255.255"), "unicast"),
    (lambda d: d["routes"][2].update(request_can_id=0x7E3), "only for docan"),
    (lambda d: d["routes"][0].update(ip_address="192.168.0.31"), "only for doip"),
    (lambda d: d["routes"].append(dict(d["routes"][2], logical_address=0x1050)), "duplicates eth_zone"),
    # SWR-032: pacing gap and the transfer budget that the pacing needs
    (lambda d: d["gateway"].update(can_tx_min_gap_us=2699), "bus-load budget"),
    (lambda d: d["gateway"].update(transfer_timeout_ms=5687), "paced transfers"),
    (lambda d: d["gateway"].pop("can_tx_min_gap_us"), "integer"),
    # SWR-026: internal tester of the reachability routine
    (lambda d: d["gateway"].update(probe_tester_address=0x0F00), "inside tester_range"),
    (lambda d: d["gateway"].update(probe_tester_address=0x0E10), "equals node_tester_address"),
])


def test_invalid_configurations_name_the_problem(data, mutate, message):
    mutate(data)
    with pytest.raises(gen_routing.ConfigError, match=message):
        gen_routing.validate(data)


def test_generated_header_and_address_table(tmp_path):
    assert gen_routing.main([str(CONFIG), "--out", str(tmp_path)]) == 0
    header = (tmp_path / "gateway" / "RoutingConfig.h").read_text()
    assert "constexpr uint16_t GATEWAY_ADDRESS        = 0x1010U;" in header
    assert 'Route{0x1020U, "rear_lighting", Transport::DOCAN, 0x7E1U, 0x7E9U, 0x00000000U' in header
    assert 'Route{0x1040U, "eth_zone", Transport::DOIP, 0x000U, 0x000U, 0xC0A8001EU' in header
    assert "DOCAN_ROUTE_COUNT = 2U" in header and "DOIP_ROUTE_COUNT  = 1U" in header
    assert "CAN_TX_MIN_GAP_US      = 3000U;" in header and "TRANSFER_TIMEOUT_MS    = 10000U;" in header
    table = json.loads((tmp_path / "routing-table.json").read_text())
    assert [r["logical_address"] for r in table["routes"]] == [0x1020, 0x1030, 0x1040]
    assert table["routes"][2] == {"name": "eth_zone", "logical_address": 0x1040, "transport": "doip",
                                  "ip_address": "192.168.0.30", "lost_comm_dtc": 0xC14200}
    # unchanged output is not rewritten (keeps incremental builds stable)
    before = (tmp_path / "gateway" / "RoutingConfig.h").stat().st_mtime_ns
    assert gen_routing.main([str(CONFIG), "--out", str(tmp_path)]) == 0
    assert (tmp_path / "gateway" / "RoutingConfig.h").stat().st_mtime_ns == before


def test_invalid_file_fails_with_exit_code_2(tmp_path):
    bad = tmp_path / "routing.yaml"
    bad.write_text("gateway: {}\n")
    assert gen_routing.main([str(bad)]) == 2


def test_serial2can_profile_consistency(tmp_path):
    ok = {"serial_ports": [{"name": "az3166", "to_serial": [{"id": "0x7E1"}], "from_serial": [{"id": "0x7E9"}]}]}
    half = {"serial_ports": [{"name": "az3166", "to_serial": [{"id": "0x7E1"}], "from_serial": [{"id": "0x1F4"}]}]}
    (tmp_path / "ok.json").write_text(json.dumps(ok))
    (tmp_path / "half.json").write_text(json.dumps(half))
    assert gen_routing.main([str(CONFIG), "--check-profile", str(tmp_path / "ok.json")]) == 0
    assert gen_routing.main([str(CONFIG), "--check-profile", str(tmp_path / "half.json")]) == 3


def test_existing_az3166_profiles_do_not_forward_diagnostics():
    """The unchanged lighting profiles forward neither request nor response IDs (SWR-033)."""
    profiles = Path(__file__).parents[3] / "X-Verse" / "bridges" / "serial2can" / "config"
    for profile in profiles.glob("az3166-*.json"):
        assert gen_routing.check_profile(gen_routing.validate(gen_routing.load(CONFIG)), profile) == []


def test_bus_load_helpers():
    """SWR-032: frame size, ISO-TP frame count and the derived limits."""
    assert gen_routing.frame_bits(8) == 135
    assert [gen_routing.isotp_frames(n) for n in (1, 7, 8, 13, 14, 4095)] == [1, 1, 2, 2, 3, 586]
    assert gen_routing.min_tx_gap_us() == 2700
    cfg = gen_routing.validate(yaml.safe_load(CONFIG.read_text()))
    # two CAN routes x 586 frames x (3 ms gap rounded to the tick + 1 tick) + 1 s
    assert gen_routing.required_transfer_ms(cfg) == 5688
