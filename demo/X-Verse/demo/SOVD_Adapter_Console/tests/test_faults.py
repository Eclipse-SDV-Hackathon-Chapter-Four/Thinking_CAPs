# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-07 · Latest version: 2026-10-07
# Goal: Tests of the tester's fault model: status mapping and memory, F1 from the gateway, F2 from the observer, the bridge, reset.
"""Fault model with a stub gateway and a stub observer: status byte mapping, memory since
reset, F1 read from the gateway, F2 from the observer, the bridge edges, reset."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backends import Response  # noqa: E402
from faults import FaultModel, TesterFault, status_byte  # noqa: E402

SETTINGS = {"f1_code": "P0500", "f2_code": "U0104", "component": "cruise", "bridge": True, "retry_s": 2.0,
            "items": {"speed": "vehicle_speed", "state": "cruise_state", "fault": "speed_sensor_fault_status",
                      "switch": "speed_sensor_stuck"}}


class FakeClock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class StubGateway:
    """What the console reads and writes on the gateway, as a dict of data items."""

    def __init__(self):
        self.up = True
        self.write_ok = True
        self.writes = []
        self.data = {"vehicle_speed": {"value": 101.3, "unit": "km/h"},
                     "cruise_state": {"state": "active", "set_speed": 100.0},
                     "speed_sensor_fault_status": {"fault": "VehicleSpeedSensorStuck", "status": "passed", "test_failed": False, "confirmed": False},
                     "speed_sensor_stuck": {"stuck": False}}

    def set_stage(self, stage):
        self.data["speed_sensor_fault_status"].update(status=stage, test_failed=stage in ("prefailed", "failed"), confirmed=stage == "failed")
        if stage == "failed":
            self.data["cruise_state"]["state"] = "unavailable"

    def sovd_read(self, item, component=None, origin=None):
        if not self.up:
            return Response(0, error="URLError: connection refused"), None
        if item not in self.data:
            return Response(404, b'{"error_code":"error-response","message":"not found"}', "application/json"), None
        return Response(200), dict(self.data[item])

    def sovd_write(self, item, value, component=None, origin=None):
        self.writes.append((item, value, origin))
        if not self.up:
            return Response(0, error="URLError: connection refused")
        if not self.write_ok:
            return Response(500, b'{"error_code":"error-response","message":"An internal error occurred"}', "application/json")
        self.data["speed_sensor_stuck"]["stuck"] = value["stuck"]
        return Response(204)


class StubObserver:
    def __init__(self):
        self.v = {"f1_failed": False, "f1_state": "PASSED", "f1_reason": None, "f2_failed": False, "f2_armed": True}

    def verdicts(self):
        return dict(self.v)


class StatusByteTests(unittest.TestCase):
    def test_mapping(self):
        self.assertEqual(status_byte(False, False, False), 0x00)
        self.assertEqual(status_byte(True, False, False), 0x01)       # prefailed, never failed
        self.assertEqual(status_byte(True, True, True), 0x0D)         # failed
        self.assertEqual(status_byte(False, True, True), 0x0C)        # prepassed
        self.assertEqual(status_byte(False, False, True), 0x0C)       # passed, stored
        self.assertEqual(status_byte(True, False, True), 0x0D)        # prefailed again after a failure

    def test_memory_and_clear(self):
        f = TesterFault("P0500", "x", "s", "m")
        f.update("prefailed", True, 1.0)
        self.assertEqual((f.status(), f.occurrences, f.stored), (0x01, 0, False))
        f.update("failed", True, 2.0)
        self.assertEqual((f.status(), f.occurrences, f.first_failed), (0x0D, 1, 2.0))
        f.update("prepassed", False, 3.0)
        self.assertEqual((f.status(), f.qualified_failed), (0x0C, True))
        f.update("passed", False, 4.0)
        self.assertEqual((f.status(), f.qualified_failed, f.stored), (0x0C, False, True))
        f.update("failed", True, 5.0)
        self.assertEqual(f.occurrences, 2)
        f.clear(6.0)
        self.assertEqual((f.occurrences, f.stored, f.status()), (1, True, 0x0D))   # still failing: stays failing
        f.update("passed", False, 7.0)
        f.clear(8.0)
        self.assertEqual((f.occurrences, f.stored, f.status()), (0, False, 0x00))
        self.assertEqual(f.view()["code"], "P0500")


class FaultModelTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.gw = StubGateway()
        self.obs = StubObserver()
        self.m = FaultModel(self.gw, self.obs, SETTINGS, self.clock, self.clock)

    def fault(self, code):
        return next(f for f in self.m.faults_view() if f["code"] == code)

    def test_f1_from_gateway_and_f2_from_observer(self):
        self.m.poll()
        f1, f2 = self.fault("P0500"), self.fault("U0104")
        self.assertEqual((f1["stage"], f1["status"], f1["available"], f1["cruise_state"]), ("passed", 0, True, "active"))
        self.assertEqual((f2["stage"], f2["armed"]), ("passed", True))
        self.gw.set_stage("failed")
        self.obs.v["f2_failed"] = True
        self.m.poll()
        f1, f2 = self.fault("P0500"), self.fault("U0104")
        self.assertEqual((f1["stage"], f1["status"], f1["qualified_failed"], f1["cruise_state"]), ("failed", 0x0D, True, "unavailable"))
        self.assertEqual((f2["stage"], f2["status"], f2["qualified_failed"]), ("failed", 0x0D, True))
        self.assertEqual(self.m.gateway_view()["items"]["speed"]["data"]["value"], 101.3)

    def test_gateway_down_keeps_last_state_unavailable(self):
        self.gw.set_stage("failed")
        self.m.poll()
        self.gw.up = False
        self.m.poll()
        f1 = self.fault("P0500")
        self.assertEqual((f1["stage"], f1["available"]), ("failed", False))
        self.assertFalse(self.m.gateway_view()["reachable"])
        self.assertIn("connection refused", self.m.gateway_view()["error"])

    def test_bridge_edges(self):
        self.m.poll()                                       # verdict ok at start: nothing written
        self.assertEqual(self.gw.writes, [])
        self.obs.v["f1_failed"] = True
        self.m.poll()
        self.assertEqual(self.gw.writes, [("speed_sensor_stuck", {"stuck": True}, "bridge")])
        self.m.poll()                                       # still faulty: no second write
        self.assertEqual(len(self.gw.writes), 1)
        self.assertTrue(self.m.gateway_view()["bridge"]["in_sync"])
        self.gw.data["speed_sensor_stuck"]["stuck"] = False  # the gateway restarted: lost the switch
        self.m.poll()
        self.assertEqual(len(self.gw.writes), 2)
        self.assertEqual(self.m.gateway_view()["bridge"]["events"][-1]["reason"], "re-assert")
        self.obs.v["f1_failed"] = False
        self.m.poll()
        self.assertEqual(self.gw.writes[-1], ("speed_sensor_stuck", {"stuck": False}, "bridge"))
        self.assertEqual(len(self.gw.writes), 3)

    def test_bridge_does_not_undo_a_manual_injection(self):
        self.m.poll()
        self.m.set_switch(True, origin="scenario")        # like the stuck-switch scenario or curl
        self.assertTrue(self.gw.data["speed_sensor_stuck"]["stuck"])
        self.m.poll()
        self.m.poll()
        self.assertEqual([w[2] for w in self.gw.writes], ["scenario"])   # the bridge did not write false
        self.assertFalse(self.m.gateway_view()["bridge"]["in_sync"])     # but reports the difference

    def test_bridge_retries_after_a_failed_write(self):
        self.gw.write_ok = False
        self.obs.v["f1_failed"] = True
        self.m.poll()
        self.assertEqual(len(self.gw.writes), 1)
        self.assertEqual(self.m.gateway_view()["bridge"]["failures"], 1)
        self.m.poll()                                       # inside the retry back-off: no write
        self.assertEqual(len(self.gw.writes), 1)
        self.clock.t += 2.5
        self.gw.write_ok = True
        self.m.poll()
        self.assertEqual(len(self.gw.writes), 2)
        self.assertTrue(self.gw.data["speed_sensor_stuck"]["stuck"])
        self.assertIsNone(self.m.gateway_view()["bridge"]["last_error"])

    def test_bridge_disabled(self):
        m = FaultModel(self.gw, self.obs, {**SETTINGS, "bridge": False}, self.clock, self.clock)
        self.obs.v["f1_failed"] = True
        m.poll()
        self.assertEqual(self.gw.writes, [])
        self.assertTrue(m.gateway_view()["bridge"]["wanted"])

    def test_reset(self):
        self.gw.set_stage("failed")
        self.m.poll()
        self.gw.set_stage("passed")
        self.m.poll()
        self.assertEqual(self.fault("P0500")["status"], 0x0C)              # stored
        r = self.m.reset()
        self.assertTrue(r.ok)
        self.assertEqual(self.gw.writes[-1], ("speed_sensor_stuck", {"stuck": False}, "reset"))
        self.m.poll()
        f1 = self.fault("P0500")
        self.assertEqual((f1["status"], f1["occurrences"], f1["stored"]), (0x00, 0, False))


if __name__ == "__main__":
    unittest.main()
