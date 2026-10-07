# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Tests of the Zenoh scouting parser, the endpoint selection and the reconnect after a vehicle restart.
"""Zenoh scouting replies and endpoint selection; the console following a restarted vehicle."""
import os
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import server  # noqa: E402
from discover import parse_hello, tcp_endpoints  # noqa: E402

VEHICLE = "10.169.127.81"


def hello(locators, whatami=0b01, version=0x09, zid=bytes(range(1, 17))):
    """A HELLO as a Zenoh 1.x node sends it."""
    out = bytes([0x02 | (0x20 if locators else 0), version, ((len(zid) - 1) << 4) | whatami]) + zid
    if locators:
        out += bytes([len(locators)])
        for loc in locators:
            out += bytes([len(loc)]) + loc.encode()
    return out


class HelloTests(unittest.TestCase):
    def test_peer_with_locators(self):
        node = parse_hello(hello([f"tcp/{VEHICLE}:36025", "tcp/[fe80::1]:36025", "tcp/192.168.98.1:36025"]), VEHICLE)
        self.assertEqual((node["whatami"], node["version"]), ("peer", "1.x"))
        self.assertEqual(len(node["locators"]), 3)
        self.assertEqual(node["zid"], bytes(range(1, 17))[::-1].hex().lstrip("0"))

    def test_not_a_hello_or_truncated(self):
        self.assertIsNone(parse_hello(bytes([0x01, 0x09, 0x03]), VEHICLE))      # a SCOUT
        self.assertIsNone(parse_hello(hello([f"tcp/{VEHICLE}:7447"])[:-3], VEHICLE))
        self.assertIsNone(parse_hello(b"", VEHICLE))

    def test_only_ipv4_tcp_on_the_vehicle_host(self):
        nodes = [parse_hello(hello([f"tcp/{VEHICLE}:36025", "tcp/[fe80::1]:36025", "tcp/192.168.98.1:36025",
                                    f"udp/{VEHICLE}:7447", f"tcp/{VEHICLE}:7447?iface=wlan0"]), VEHICLE),
                 parse_hello(hello(["tcp/10.169.127.50:7447"], whatami=0b00), "10.169.127.50")]
        self.assertEqual(tcp_endpoints(nodes, VEHICLE), [f"tcp/{VEHICLE}:36025", f"tcp/{VEHICLE}:7447"])
        self.assertEqual(tcp_endpoints(nodes, "10.0.0.9"), [])


class FakeLink:
    def __init__(self):
        self.endpoints, self.state, self.reconnects = [f"tcp/{VEHICLE}:7447"], "connecting", []

    def status(self, timeout_s):
        return {"state": self.state}

    def reconnect(self, endpoints):
        self.reconnects.append(endpoints)
        self.endpoints = endpoints
        return True

    def stop(self):
        pass


class FollowVehicleTests(unittest.TestCase):
    def test_reconnects_once_when_the_vehicle_moved(self):
        link, asked = FakeLink(), []
        console = server.Console(link=link)   # not started: only the vehicle finder runs here

        def find(host):
            asked.append(host)
            return [f"tcp/{VEHICLE}:40235"]
        threading.Thread(target=console._follow_vehicle, args=(VEHICLE, 0.01, find), daemon=True).start()
        deadline = time.monotonic() + 2
        while len(asked) < 5 and time.monotonic() < deadline:
            time.sleep(0.01)
        link.state = "live"                # samples again: no more scouting
        time.sleep(0.05)
        n = len(asked)
        time.sleep(0.1)
        console.stop()
        self.assertEqual(link.reconnects, [[f"tcp/{VEHICLE}:40235"]])   # same endpoints afterwards: no new reconnect
        self.assertEqual(asked[0], VEHICLE)
        self.assertEqual(len(asked), n)


if __name__ == "__main__":
    unittest.main()
