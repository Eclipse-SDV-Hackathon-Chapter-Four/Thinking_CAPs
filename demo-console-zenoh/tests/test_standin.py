# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-07 · Latest version: 2026-10-07
# Goal: Tests of the gateway stand-in: cruise.rs semantics with a fake clock, and the opensovd-core HTTP contract over a socket.
"""The stand-in must behave like the opensovd-gateway of PR #40: same debounce semantics
(fake clock) and the same HTTP contract (routes, JSON shapes, status codes, error bodies)."""
import json
import os
import socket
import sys
import time
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import score_app  # noqa: E402
from score_app import CruiseGateway, DataInternal, DataNotFound, DataReadOnly, Monitor, Sensor, TimeBased  # noqa: E402


class FakeClock:
    def __init__(self, t=100.0):
        self.t = t

    def __call__(self):
        return self.t


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class DebounceTests(unittest.TestCase):
    """Port of the Rust unit tests of cruise.rs (failed_only_after_failed_duration,
    recovery_needs_passed_duration, short_glitch_never_qualifies)."""

    # same numbers as the Rust tests: failed_duration 100 ms, passed_duration 50 ms
    def test_failed_only_after_failed_duration(self):
        t0 = 0.0
        m = Monitor(TimeBased(0.100, 0.050), t0)
        m.report(True, t0)
        self.assertEqual(m.stage(t0 + 0.099), "prefailed")
        self.assertEqual(m.stage(t0 + 0.100), "failed")

    def test_short_glitch_never_qualifies(self):
        t0 = 0.0
        m = Monitor(TimeBased(0.100, 0.050), t0)
        m.report(True, t0)
        m.report(False, t0 + 0.060)
        self.assertEqual(m.stage(t0 + 0.500), "passed")

    def test_recovery_needs_passed_duration(self):
        t0 = 0.0
        m = Monitor(TimeBased(0.100, 0.050), t0)
        m.report(True, t0)
        self.assertEqual(m.stage(t0 + 0.100), "failed")
        m.report(False, t0 + 0.200)
        self.assertEqual(m.stage(t0 + 0.249), "prepassed")
        self.assertEqual(m.stage(t0 + 0.250), "passed")

    def test_sensor_speed_and_state(self):
        clock = FakeClock(0.0)
        s = Sensor(TimeBased(0.1, 0.2), clock())
        v1 = s.speed_kmh(0.0)
        self.assertAlmostEqual(v1, 100.0)
        self.assertTrue(94.9 <= s.speed_kmh(4.7) <= 105.1)
        s.stuck_at = 97.3
        s.refresh(0.0)
        self.assertEqual(s.speed_kmh(5.0), 97.3)                          # frozen
        self.assertEqual(s.state, "active")                               # prefailed keeps the state
        s.refresh(0.1)
        self.assertEqual(s.state, "unavailable")                          # failed
        s.stuck_at = None
        s.refresh(0.1)
        self.assertEqual(s.state, "unavailable")                          # prepassed keeps unavailable
        s.refresh(0.3)
        self.assertEqual(s.state, "standby")                              # passed again: standby, not active


class GatewayObjectTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.gw = CruiseGateway(TimeBased(0.3, 0.2), self.clock)

    def test_list_and_metadata(self):
        items = self.gw.list()
        self.assertEqual([i["id"] for i in items], ["vehicle_speed", "cruise_state", "speed_sensor_fault_status", "speed_sensor_stuck"])
        self.assertEqual([i["category"] for i in items], ["currentData"] * 3 + ["storedData"])
        self.assertTrue(all(i["groups"] == ["cruise"] for i in items))
        self.assertEqual([i["id"] for i in self.gw.list(categories=["storedData"])], ["speed_sensor_stuck"])
        self.assertEqual(len(self.gw.list(groups=["cruise"], categories=["storedData"])), 4)   # groups win
        self.assertEqual(self.gw.list(groups=["hvac"]), [])
        self.assertEqual(self.gw.list(tags=["x"]), [])

    def test_read_write_and_errors(self):
        self.assertEqual(self.gw.read("vehicle_speed")["unit"], "km/h")
        self.assertEqual(self.gw.read("cruise_state"), {"state": "active", "set_speed": 100.0})
        self.assertEqual(self.gw.read("speed_sensor_fault_status"),
                         {"fault": "VehicleSpeedSensorStuck", "status": "passed", "test_failed": False, "confirmed": False})
        self.assertEqual(self.gw.read("speed_sensor_stuck"), {"stuck": False})
        with self.assertRaises(DataNotFound):
            self.gw.read("nope")
        with self.assertRaises(DataReadOnly):
            self.gw.write("vehicle_speed", {"value": 1})
        with self.assertRaises(DataInternal):
            self.gw.write("speed_sensor_stuck", {"stuck": "yes"})
        self.gw.write("speed_sensor_stuck", {"stuck": True})
        self.assertEqual(self.gw.read("speed_sensor_fault_status")["status"], "prefailed")
        self.clock.t += 0.3
        fs = self.gw.read("speed_sensor_fault_status")
        self.assertEqual((fs["status"], fs["test_failed"], fs["confirmed"]), ("failed", True, True))
        self.assertEqual(self.gw.read("cruise_state")["state"], "unavailable")
        self.gw.write("speed_sensor_stuck", {"stuck": False})
        self.assertEqual(self.gw.read("speed_sensor_fault_status")["status"], "prepassed")
        self.clock.t += 0.2
        self.assertEqual(self.gw.read("speed_sensor_fault_status")["status"], "passed")
        self.assertEqual(self.gw.read("cruise_state")["state"], "standby")


class HttpContractTests(unittest.TestCase):
    """The wire format of opensovd-core (pin 29e806f) as the console and curl see it."""

    @classmethod
    def setUpClass(cls):
        cls.port = free_port()
        cls.gw = CruiseGateway(TimeBased(0.3, 0.2))
        cls.srv = score_app.serve(cls.gw, "127.0.0.1", cls.port, "/sovd")
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def req(self, method, path, body=None, content_type="application/json", raw=None):
        data = raw if raw is not None else (None if body is None else json.dumps(body).encode())
        headers = {"Content-Type": content_type} if data is not None else {}
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(r, timeout=3) as resp:
                return resp.status, resp.headers.get("Content-Type", ""), resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Content-Type", ""), e.read()

    def get_json(self, path):
        status, ctype, body = self.req("GET", path)
        return status, json.loads(body.decode() or "null")

    def test_version_components_capabilities(self):
        st, j = self.get_json("/sovd/version-info")
        self.assertEqual(st, 200)
        self.assertEqual(j["sovd_info"][0]["version"], "1.1.0")
        self.assertEqual(j["sovd_info"][0]["base_uri"], f"{self.base}/sovd/v1")
        self.assertEqual(j["sovd_info"][0]["vendor_info"], {"version": "0.1.1", "name": "OpenSOVD"})   # as the Rust binary answers
        self.assertNotIn("schema", j)
        st, j = self.get_json("/sovd/version-info?include-schema=true")
        self.assertIn("schema", j)
        st, j = self.get_json("/sovd/v1/components")
        self.assertEqual(st, 200)
        self.assertEqual(j, {"items": [{"id": "cruise", "name": "Cruise Control", "href": f"{self.base}/sovd/v1/components/cruise"}]})
        st, j = self.get_json("/sovd/v1/components/cruise")
        self.assertEqual((st, j["id"], j["data"]), (200, "cruise", f"{self.base}/sovd/v1/components/cruise/data"))
        st, j = self.get_json("/sovd/v1/components/hvac")
        self.assertEqual(st, 404)
        self.assertEqual(j, {"error_code": "vendor-specific", "vendor_code": "entity-not-found", "message": "Entity not found: hvac"})
        self.assertEqual(self.get_json("/sovd/v1/apps"), (200, {"items": []}))           # empty collections, like the Rust gateway

    def test_data_list_and_filters(self):
        st, j = self.get_json("/sovd/v1/components/cruise/data")
        self.assertEqual(st, 200)
        self.assertEqual([i["id"] for i in j["items"]], ["vehicle_speed", "cruise_state", "speed_sensor_fault_status", "speed_sensor_stuck"])
        self.assertEqual(j["items"][3], {"id": "speed_sensor_stuck", "name": "Fault injection: vehicle speed sensor stuck",
                                         "category": "storedData", "groups": ["cruise"]})
        self.assertNotIn("tags", j["items"][0])
        st, j = self.get_json("/sovd/v1/components/cruise/data?categories=storedData")
        self.assertEqual([i["id"] for i in j["items"]], ["speed_sensor_stuck"])
        st, j = self.get_json("/sovd/v1/components/cruise/data?groups=cruise&categories=storedData")
        self.assertEqual(len(j["items"]), 4)                                # groups take precedence
        st, j = self.get_json("/sovd/v1/components/cruise/data?include-schema=true")
        self.assertIn("schema", j)
        st, j = self.get_json("/sovd/v1/components/cruise/data-categories")
        self.assertEqual(j, {"items": [{"item": "currentData"}, {"item": "storedData"}]})
        st, j = self.get_json("/sovd/v1/components/cruise/data-groups?category=storedData")
        self.assertEqual(j, {"items": [{"id": "cruise", "category": "storedData"}]})

    def test_read_write_round_trip(self):
        st, j = self.get_json("/sovd/v1/components/cruise/data/vehicle_speed")
        self.assertEqual(st, 200)
        self.assertEqual(j["id"], "vehicle_speed")
        self.assertTrue(94.9 <= j["data"]["value"] <= 105.1)
        self.assertEqual(j["data"]["unit"], "km/h")
        self.assertEqual(set(j), {"id", "data"})
        st, ctype, body = self.req("PUT", "/sovd/v1/components/cruise/data/speed_sensor_stuck", {"data": {"stuck": True}})
        self.assertEqual((st, body), (204, b""))
        self.assertEqual(self.get_json("/sovd/v1/components/cruise/data/speed_sensor_stuck")[1]["data"], {"stuck": True})
        self.assertEqual(self.get_json("/sovd/v1/components/cruise/data/speed_sensor_fault_status")[1]["data"]["status"], "prefailed")
        time.sleep(0.35)
        fs = self.get_json("/sovd/v1/components/cruise/data/speed_sensor_fault_status")[1]["data"]
        self.assertEqual(fs, {"fault": "VehicleSpeedSensorStuck", "status": "failed", "test_failed": True, "confirmed": True})
        self.assertEqual(self.get_json("/sovd/v1/components/cruise/data/cruise_state")[1]["data"]["state"], "unavailable")
        st, _, _ = self.req("PUT", "/sovd/v1/components/cruise/data/speed_sensor_stuck", {"data": {"stuck": False}})
        self.assertEqual(st, 204)
        time.sleep(0.25)
        self.assertEqual(self.get_json("/sovd/v1/components/cruise/data/speed_sensor_fault_status")[1]["data"]["status"], "passed")
        self.assertEqual(self.get_json("/sovd/v1/components/cruise/data/cruise_state")[1]["data"]["state"], "standby")

    def test_error_answers(self):
        st, j = self.get_json("/sovd/v1/components/cruise/data/nope")
        self.assertEqual((st, j), (404, {"error_code": "error-response", "message": "not found: nope"}))
        st, _, body = self.req("PUT", "/sovd/v1/components/cruise/data/vehicle_speed", {"data": {"value": 1}})
        self.assertEqual((st, json.loads(body)), (400, {"error_code": "error-response", "message": "read only"}))
        st, _, body = self.req("PUT", "/sovd/v1/components/cruise/data/speed_sensor_stuck", {"data": {"stuck": "yes"}})
        self.assertEqual((st, json.loads(body)), (500, {"error_code": "error-response", "message": "An internal error occurred"}))  # CR-04
        st, ctype, body = self.req("PUT", "/sovd/v1/components/cruise/data/speed_sensor_stuck", {"stuck": True})
        self.assertEqual(st, 422)
        self.assertTrue(ctype.startswith("text/plain"))
        st, ctype, body = self.req("PUT", "/sovd/v1/components/cruise/data/speed_sensor_stuck", raw=b"{not json")
        self.assertEqual(st, 400)
        st, ctype, body = self.req("PUT", "/sovd/v1/components/cruise/data/speed_sensor_stuck", raw=b'{"data":{"stuck":true}}', content_type="text/plain")
        self.assertEqual(st, 415)
        st, ctype, body = self.req("GET", "/sovd/v1/nope")
        self.assertEqual((st, body), (404, b""))
        st, ctype, body = self.req("DELETE", "/sovd/v1/components/cruise/data/speed_sensor_stuck")
        self.assertEqual(st, 405)
        st, ctype, body = self.req("GET", "/sovd/v1/components/cruise/faults")
        self.assertEqual(st, 404)                                           # no faults resource (#156) in PR #40


if __name__ == "__main__":
    unittest.main()
