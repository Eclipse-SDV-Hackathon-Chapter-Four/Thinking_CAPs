#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate config/routing.yaml and generate the gateway routing configuration.

Outputs (SWR-010, SWR-052):
  <out>/gateway/RoutingConfig.h   C++ constexpr configuration for the gateway
  <out>/routing-table.json        address table to check the CDA MDD and ECU CAN profiles

  gen_routing.py config/routing.yaml --out <dir>
  gen_routing.py config/routing.yaml --check-profile <serial2can.json>   # consistency check
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import sys
from pathlib import Path

import yaml

DIAG_CAN_MIN, DIAG_CAN_MAX = 0x7DF, 0x7EF
TRANSPORTS = ("docan", "doip")


class ConfigError(Exception):
    """Raised for an invalid routing configuration; the message names the entry."""


def _int(entry: dict, key: str, where: str) -> int:
    value = entry.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError(f"{where}: '{key}' must be an integer, got {value!r}")
    return value


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or "gateway" not in data or "routes" not in data:
        raise ConfigError(f"{path}: needs 'gateway' and 'routes'")
    return data


def _ipv4(entry: dict, where: str) -> str:
    value = entry.get("ip_address")
    try:
        address = ipaddress.IPv4Address(str(value))
    except ValueError:
        raise ConfigError(f"{where}: 'ip_address' must be an IPv4 address, got {value!r}") from None
    if (address.is_unspecified or address.is_multicast or address.is_loopback
            or address == ipaddress.IPv4Address("255.255.255.255")):
        raise ConfigError(f"{where}: ip_address {address} is not a unicast node address")
    return str(address)


def _transport_fields(entry: dict, route: dict, where: str, can_ids: dict, ip_addresses: dict) -> None:
    """Add and check the transport-specific fields of a route (CAN identifiers or IPv4 address)."""
    if route["transport"] == "docan":
        if "ip_address" in entry:
            raise ConfigError(f"{where}: ip_address is only for doip routes")
        for key in ("request_can_id", "response_can_id"):
            can_id = route[key] = _int(entry, key, where)
            if not DIAG_CAN_MIN <= can_id <= DIAG_CAN_MAX:
                raise ConfigError(f"{where}: {key} {can_id:#x} outside {DIAG_CAN_MIN:#x}-{DIAG_CAN_MAX:#x}")
            if can_id in can_ids:
                raise ConfigError(f"{where}: {key} {can_id:#x} duplicates {can_ids[can_id]}")
            can_ids[can_id] = f"{route['name']}.{key}"
        return
    if "request_can_id" in entry or "response_can_id" in entry:
        raise ConfigError(f"{where}: CAN identifiers are only for docan routes")
    route["ip_address"] = _ipv4(entry, where)
    if route["ip_address"] in ip_addresses:
        raise ConfigError(f"{where}: ip_address {route['ip_address']} duplicates {ip_addresses[route['ip_address']]}")
    ip_addresses[route["ip_address"]] = route["name"]


def validate(data: dict) -> dict:
    """Return a normalised configuration or raise ConfigError (SWR-010)."""
    gw = data["gateway"]
    where = "gateway"
    cfg = {
        "name": str(gw.get("name", "zonal_gateway")),
        "logical_address": _int(gw, "logical_address", where),
        "functional_address": _int(gw, "functional_address", where),
        "functional_can_id": _int(gw, "functional_can_id", where),
        "node_tester_address": _int(gw, "node_tester_address", where),
        "functional_window_ms": _int(gw, "functional_window_ms", where),
        "vin": str(gw.get("vin", "")),
        "ecu_serial": str(gw.get("ecu_serial", "")),
    }
    tester_range = gw.get("tester_range")
    if (not isinstance(tester_range, list) or len(tester_range) != 2
            or not all(isinstance(v, int) for v in tester_range) or tester_range[0] > tester_range[1]):
        raise ConfigError("gateway: 'tester_range' must be [min, max]")
    cfg["tester_min"], cfg["tester_max"] = tester_range
    if len(cfg["vin"]) != 17 or not cfg["vin"].isascii():
        raise ConfigError("gateway: 'vin' must be 17 ASCII characters")
    if not DIAG_CAN_MIN <= cfg["functional_can_id"] <= DIAG_CAN_MAX:
        raise ConfigError(f"gateway: functional_can_id {cfg['functional_can_id']:#x} outside "
                          f"{DIAG_CAN_MIN:#x}-{DIAG_CAN_MAX:#x}")
    for key in ("logical_address", "functional_address", "node_tester_address"):
        if not 0 < cfg[key] <= 0xFFFF:
            raise ConfigError(f"gateway: {key} out of range")
    if cfg["tester_min"] <= cfg["logical_address"] <= cfg["tester_max"]:
        raise ConfigError("gateway: logical_address inside tester_range")

    addresses = {cfg["logical_address"]: "gateway", cfg["functional_address"]: "functional"}
    can_ids = {cfg["functional_can_id"]: "functional_can_id"}
    ip_addresses: dict[str, str] = {}
    routes = []
    for i, entry in enumerate(data["routes"] or []):
        where = f"routes[{i}] ({entry.get('name', '?')})"
        transport = entry.get("transport")
        if transport not in TRANSPORTS:
            raise ConfigError(f"{where}: transport must be one of {TRANSPORTS}")
        route = {
            "name": str(entry.get("name", f"route{i}")),
            "logical_address": _int(entry, "logical_address", where),
            "transport": transport,
            "p2_ms": _int(entry, "p2_ms", where),
            "p2_star_ms": _int(entry, "p2_star_ms", where),
            "max_length": _int(entry, "max_length", where),
            "lost_comm_dtc": _int(entry, "lost_comm_dtc", where),
        }
        _transport_fields(entry, route, where, can_ids, ip_addresses)
        if route["logical_address"] in addresses:
            raise ConfigError(f"{where}: logical_address {route['logical_address']:#06x} duplicates "
                              f"{addresses[route['logical_address']]}")
        if cfg["tester_min"] <= route["logical_address"] <= cfg["tester_max"]:
            raise ConfigError(f"{where}: logical_address inside tester_range")
        addresses[route["logical_address"]] = route["name"]
        if not 0 < route["p2_ms"] <= route["p2_star_ms"]:
            raise ConfigError(f"{where}: need 0 < p2_ms <= p2_star_ms")
        if not 1 <= route["max_length"] <= 4095:
            raise ConfigError(f"{where}: max_length must be 1..4095")
        if not 0 <= route["lost_comm_dtc"] <= 0xFFFFFF:
            raise ConfigError(f"{where}: lost_comm_dtc must be a 3-byte DTC")
        routes.append(route)
    if not routes:
        raise ConfigError("routes: at least one route is required")
    cfg["routes"] = routes
    canonical = json.dumps(cfg, sort_keys=True).encode()
    cfg["hash"] = hashlib.sha256(canonical).hexdigest()[:8]
    return cfg


def render_header(cfg: dict) -> str:
    rows = []
    for r in cfg["routes"]:
        ip = int(ipaddress.IPv4Address(r["ip_address"])) if r["transport"] == "doip" else 0
        rows.append(
            f"    Route{{0x{r['logical_address']:04X}U, \"{r['name']}\", "
            f"Transport::{r['transport'].upper()}, 0x{r.get('request_can_id', 0):03X}U, "
            f"0x{r.get('response_can_id', 0):03X}U, 0x{ip:08X}U, {r['p2_ms']}U, "
            f"{r['p2_star_ms']}U, {r['max_length']}U, 0x{r['lost_comm_dtc']:06X}U}},")
    counts = {t: sum(r["transport"] == t for r in cfg["routes"]) for t in TRANSPORTS}
    return f"""// Generated by tools/gen_routing.py from config/routing.yaml. Do not edit.
// SPDX-License-Identifier: Apache-2.0
#pragma once

#include "gateway/Route.h"

#include <etl/array.h>

namespace gateway
{{
namespace config
{{
constexpr char const* ROUTING_TABLE_HASH = "{cfg['hash']}";
constexpr uint16_t GATEWAY_ADDRESS        = 0x{cfg['logical_address']:04X}U;
constexpr uint16_t FUNCTIONAL_ADDRESS     = 0x{cfg['functional_address']:04X}U;
constexpr uint32_t FUNCTIONAL_CAN_ID      = 0x{cfg['functional_can_id']:03X}U;
constexpr uint16_t NODE_TESTER_ADDRESS    = 0x{cfg['node_tester_address']:04X}U;
constexpr uint16_t TESTER_ADDRESS_MIN     = 0x{cfg['tester_min']:04X}U;
constexpr uint16_t TESTER_ADDRESS_MAX     = 0x{cfg['tester_max']:04X}U;
constexpr uint32_t FUNCTIONAL_WINDOW_MS   = {cfg['functional_window_ms']}U;
constexpr char const VIN[]                = "{cfg['vin']}";
constexpr char const ECU_SERIAL[]         = "{cfg['ecu_serial']}";

constexpr size_t ROUTE_COUNT       = {len(cfg['routes'])}U;
constexpr size_t DOCAN_ROUTE_COUNT = {counts['docan']}U;
constexpr size_t DOIP_ROUTE_COUNT  = {counts['doip']}U;
constexpr ::etl::array<Route, ROUTE_COUNT> ROUTES = {{{{
{chr(10).join(rows)}
}}}};
}} // namespace config
}} // namespace gateway
"""


def address_table(cfg: dict) -> dict:
    return {
        "hash": cfg["hash"],
        "gateway": {k: cfg[k] for k in ("logical_address", "functional_address",
                                         "functional_can_id", "node_tester_address")},
        "routes": [{k: r[k] for k in ("name", "logical_address", "transport", "request_can_id",
                                      "response_can_id", "ip_address", "lost_comm_dtc") if k in r}
                   for r in cfg["routes"]],
    }


def check_profile(cfg: dict, profile_path: Path) -> list[str]:
    """Check a Serial2CAN profile forwards each route's diagnostic IDs (SWR-052)."""
    profile = json.loads(profile_path.read_text())
    problems = []
    ports = profile.get("serial_ports", [])

    def matches(filters: list, can_id: int) -> bool:
        if not filters:
            return True
        for f in filters:
            fid, mask = int(str(f["id"]), 0), int(str(f.get("mask", "0x7FF")), 0)
            if (can_id & mask) == (fid & mask):
                return True
        return False

    for route in (r for r in cfg["routes"] if r["transport"] == "docan"):
        for port in ports:
            to_ok = matches(port.get("to_serial", []), route["request_can_id"])
            from_ok = matches(port.get("from_serial", []), route["response_can_id"])
            if to_ok != from_ok:
                problems.append(
                    f"{profile_path.name}:{port.get('name')}: route {route['name']} forwards "
                    f"request {route['request_can_id']:#x}={to_ok} but response "
                    f"{route['response_can_id']:#x}={from_ok}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("config", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check-profile", type=Path, action="append", default=[])
    args = parser.parse_args(argv)
    try:
        cfg = validate(load(args.config))
    except ConfigError as exc:
        print(f"routing config error: {exc}", file=sys.stderr)
        return 2
    if args.out:
        header = args.out / "gateway" / "RoutingConfig.h"
        header.parent.mkdir(parents=True, exist_ok=True)
        text = render_header(cfg)
        if not header.exists() or header.read_text() != text:
            header.write_text(text)
        (args.out / "routing-table.json").write_text(json.dumps(address_table(cfg), indent=2) + "\n")
    problems = [p for prof in args.check_profile for p in check_profile(cfg, prof)]
    for p in problems:
        print(f"consistency error: {p}", file=sys.stderr)
    return 3 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
