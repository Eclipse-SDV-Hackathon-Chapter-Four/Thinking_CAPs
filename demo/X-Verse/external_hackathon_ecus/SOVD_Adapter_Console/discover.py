# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Finds the vehicle's Zenoh endpoints by multicast scouting (through Windows Python when run from WSL).
"""Find the vehicle's Zenoh endpoints by multicast scouting (standard library only).

A Zenoh peer listens on a random TCP port unless configured otherwise, and announces
it only to multicast scouting (UDP 224.0.0.224:7446). WSL2 with NAT networking cannot
reach the LAN by multicast, so under WSL the scout runs in Windows Python (interop).

    python discover.py                  every Zenoh node that answers, with its endpoints
    python discover.py 10.169.127.81    the endpoints of that host, for ZENOH_CONNECT
"""
import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time

MCAST = ("224.0.0.224", 7446)
SCOUT = bytes([0x01, 0x09, 0x03])              # SCOUT, protocol 0x09 (Zenoh 1.x), wants routers and peers
VERSIONS = {0x09: "1.x", 0x08: "0.10/0.11"}    # nodes answer whatever version the scout carries


def _zint(buf, i):
    value = shift = 0
    while True:
        b = buf[i]
        i += 1
        value |= (b & 0x7F) << shift
        shift += 7
        if not b & 0x80:
            return value, i


def parse_hello(data, host):
    """HELLO bytes -> {"host", "whatami", "version", "zid", "locators"}, or None."""
    try:
        if data[0] & 0x1F != 0x02:
            return None
        version, flags = data[1], data[2]
        zid_len = (flags >> 4) + 1
        node = {"host": host, "whatami": ("router", "peer", "client", "?")[flags & 0b11],
                "version": VERSIONS.get(version, f"0x{version:02x}"),
                "zid": data[3:3 + zid_len][::-1].hex().lstrip("0"), "locators": []}
        i = 3 + zid_len
        if data[0] & 0x20:                     # L flag: locators follow
            count, i = _zint(data, i)
            for _ in range(count):
                size, i = _zint(data, i)
                if i + size > len(data):
                    return None
                node["locators"].append(data[i:i + size].decode("utf-8", "replace"))
                i += size
        return node
    except IndexError:
        return None


def tcp_endpoints(nodes, host):
    """'tcp/<ip>:<port>' for each IPv4 TCP locator that the nodes on `host` announce on `host`."""
    out = []
    for node in nodes:
        if node["host"] != host:
            continue
        for loc in node["locators"]:
            addr = loc.split("#")[0].split("?")[0]
            ip, _, port = addr[len("tcp/"):].rpartition(":")
            ep = f"tcp/{ip}:{port}"
            if addr.startswith("tcp/") and ip == host and port.isdigit() and ep not in out:
                out.append(ep)
    return out


def _local_ip(toward):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((toward, 7447))              # only picks the interface, sends nothing
        return s.getsockname()[0]
    except OSError:
        return "0.0.0.0"
    finally:
        s.close()


def scout(seconds=2.0, toward="1.1.1.1"):
    """Every node that answers a multicast scout on the interface that routes to `toward`."""
    ip = _local_ip(toward)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    nodes, next_send, end = {}, 0.0, time.monotonic() + seconds
    try:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        if ip != "0.0.0.0":
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
        s.bind((ip, 0))
        s.settimeout(0.2)
        while time.monotonic() < end:
            if time.monotonic() >= next_send:
                s.sendto(SCOUT, MCAST)
                next_send = time.monotonic() + 0.5
            try:
                data, addr = s.recvfrom(65535)
            except (socket.timeout, ConnectionResetError):
                continue
            node = parse_hello(data, addr[0])
            if node:
                nodes.setdefault(node["zid"] or addr[0], node)
    finally:
        s.close()
    return list(nodes.values())


def in_wsl():
    return "microsoft" in platform.uname().release.lower()


def nodes(seconds=2.0, toward="1.1.1.1"):
    """scout(), run in Windows Python when this is WSL (its NAT network drops multicast)."""
    exe = (shutil.which("python.exe") or shutil.which("py.exe")) if in_wsl() else None
    if not exe:
        return scout(seconds, toward)
    me = subprocess.run(["wslpath", "-w", os.path.abspath(__file__)],
                        capture_output=True, text=True, check=True).stdout.strip()
    out = subprocess.run([exe, me, "--json", "--toward", toward, "--seconds", str(seconds)],
                         capture_output=True, text=True, timeout=seconds + 20, check=True).stdout
    return json.loads(out)


def find(host, seconds=2.0):
    """Endpoints of the Zenoh nodes on `host`, [] when none answer. Never raises."""
    try:
        ip = socket.gethostbyname(host)
        return tcp_endpoints(nodes(seconds, ip), ip)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print(f"vehicle finder: {type(e).__name__}: {e}"[:300], file=sys.stderr, flush=True)
        return []


def main():
    ap = argparse.ArgumentParser(description="Find Zenoh routers and peers on the network (multicast scouting)")
    ap.add_argument("host", nargs="?", help="only this host: print its endpoints, comma-separated")
    ap.add_argument("--seconds", type=float, default=2.0)
    ap.add_argument("--toward", default="1.1.1.1", help=argparse.SUPPRESS)
    ap.add_argument("--json", action="store_true", help=argparse.SUPPRESS)  # what the WSL side asks Windows for
    a = ap.parse_args()
    if a.json:
        print(json.dumps(scout(a.seconds, a.toward)))
        return
    if a.host:
        eps = find(a.host, a.seconds)
        print(",".join(eps) or f"no Zenoh node answered on {a.host}")
        raise SystemExit(0 if eps else 1)
    found = sorted(nodes(a.seconds), key=lambda n: (n["host"], n["zid"]))
    if not found:
        print("No Zenoh node answered. Is the vehicle running, in peer or router mode, on this network?")
        raise SystemExit(1)
    for n in found:
        eps = ", ".join(tcp_endpoints([n], n["host"])) or "(no IPv4 TCP endpoint)"
        print(f"{n['host']:<16} {n['whatami']:<6} Zenoh {n['version']:<10} {eps}")
    hosts = sorted({n["host"] for n in found})
    print(f"\nStart the console with:  VEHICLE_HOST={hosts[0] if len(hosts) == 1 else '<vehicle IP>'} ./run.sh")


if __name__ == "__main__":
    main()
