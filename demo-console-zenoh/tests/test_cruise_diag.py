# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Tests of the F1 plausibility debounce, the F2 lost-communication monitor and the fault store.
"""F1 plausibility debounce, F2 lost communication and the fault store, with a fake clock."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cruise_diag import CruiseDiag  # noqa: E402
from vehicle_link import VehicleLink  # noqa: E402

SETTINGS = {"f1_threshold": 5, "speed_min": 0.0, "speed_max": 300.0, "link_timeout_s": 0.5,
            "f1_code": "P0500", "f2_code": "U0104",
            "entity": "components/cruise-control", "diag_entity": "components/cruise-diag"}


class FakeClock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class DiagTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.link = VehicleLink("vehicle/status/velocity_status", clock=self.clock, wall=self.clock)
        self.diag = CruiseDiag(self.link, SETTINGS, self.clock, self.clock)

    def feed(self, payload, n=1, dt=0.05):
        for _ in range(n):
            self.link.feed(payload)
            self.clock.t += dt
            self.diag.tick()

    def status(self, code):
        entity = SETTINGS["entity"] if code == "P0500" else SETTINGS["diag_entity"]
        return next(f["status"] for f in self.diag.faults_view(entity) if f["code"] == code)

    # ------------------------------------------------------------ F1
    def test_f1_debounce_to_failed_and_back(self):
        self.feed(b"95.0", 3)
        self.assertEqual(self.diag.debounce_view()["state"], "PASSED")
        self.feed(b"nan", 4)
        self.assertEqual(self.diag.debounce_view()["state"], "PREFAILED")
        self.assertEqual(self.status("P0500"), 0x00)                 # not qualified yet
        self.feed(b"-5", 1)
        self.assertEqual(self.diag.debounce_view()["state"], "FAILED")
        self.assertEqual(self.status("P0500"), 0x0D)                 # failing, pending, confirmed
        self.feed(b"95.0", 2)
        self.assertEqual(self.diag.debounce_view()["state"], "PREPASSED")
        self.assertEqual(self.status("P0500"), 0x0D)                 # still the last qualified result
        self.feed(b"95.0", 3)
        self.assertEqual(self.diag.debounce_view()["state"], "PASSED")
        self.assertEqual(self.status("P0500"), 0x0C)                 # healed, stays stored

    def test_f1_reasons(self):
        self.feed(b"999.9")
        self.assertIn("outside", self.diag.debounce_view()["last_reason"])
        self.feed(b"abc")
        self.assertEqual(self.diag.debounce_view()["last_reason"], "not a number")
        self.feed(b"inf")
        self.assertEqual(self.diag.debounce_view()["last_reason"], "not a finite number")

    def test_speed_view_keeps_last_valid_value(self):
        self.feed(b"88.0")
        self.feed(b"nan")
        v = self.diag.speed_view()
        self.assertEqual(v["value"], 88.0)
        self.assertFalse(v["last_sample_valid"])

    # ------------------------------------------------------------ F2
    def test_f2_not_armed_before_first_valid_sample(self):
        self.clock.t += 5
        self.diag.tick()
        self.assertEqual(self.status("U0104"), 0x00)
        self.feed(b"abc", 2)                                         # traffic, but never valid
        self.clock.t += 5
        self.diag.tick()
        self.assertEqual(self.status("U0104"), 0x00)
        self.assertFalse(self.diag.link_view()["monitor_armed"])

    def test_f2_timeout_and_recovery(self):
        self.feed(b"90.0", 3)                                        # last sample 0.05 s before "now"
        self.clock.t += 0.35
        self.diag.tick()
        self.assertEqual(self.status("U0104"), 0x00)                 # 0.4 s of silence: within the timeout
        self.clock.t += 0.2
        self.diag.tick()
        self.assertEqual(self.status("U0104"), 0x0D)                 # > 500 ms of silence
        self.assertTrue(self.diag.speed_view()["stale"])
        self.assertEqual(self.diag.debounce_view()["state"], "PASSED")  # silence is not F1's business
        self.feed(b"91.0")
        self.assertEqual(self.status("U0104"), 0x0C)
        self.assertFalse(self.diag.speed_view()["stale"])

    def test_invalid_samples_keep_the_link_alive(self):
        self.feed(b"90.0")
        self.feed(b"nan", 20, dt=0.1)                                # 2 s of implausible but present data
        self.assertEqual(self.status("U0104"), 0x00)
        self.assertEqual(self.status("P0500"), 0x0D)

    # ------------------------------------------------------------ clear
    def test_clear(self):
        self.feed(b"90.0")
        self.clock.t += 1
        self.diag.tick()
        self.assertEqual(self.status("U0104"), 0x0D)
        self.diag.clear_faults(SETTINGS["diag_entity"])
        self.assertEqual(self.status("U0104"), 0x0D)                 # still failing: stays failing
        self.feed(b"90.0")
        self.diag.clear_faults(SETTINGS["diag_entity"])
        self.assertEqual(self.status("U0104"), 0x00)                 # healed: history gone


if __name__ == "__main__":
    unittest.main()
