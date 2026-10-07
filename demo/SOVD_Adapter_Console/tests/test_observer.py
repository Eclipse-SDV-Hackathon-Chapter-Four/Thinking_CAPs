# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-07 · Latest version: 2026-10-07
# Goal: Tests of the console observer: F1 plausibility debounce, F2 lost-communication monitor, views and verdicts.
"""F1 plausibility debounce, F2 lost communication, views and verdicts, with a fake clock."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from observer import Observer  # noqa: E402
from vehicle_link import VehicleLink  # noqa: E402

SETTINGS = {"f1_threshold": 5, "speed_min": 0.0, "speed_max": 300.0, "link_timeout_s": 0.5,
            "f1_code": "P0500", "f2_code": "U0104"}


class FakeClock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.link = VehicleLink("vehicle/status/velocity_status", clock=self.clock, wall=self.clock)
        self.obs = Observer(self.link, SETTINGS, self.clock, self.clock)

    def feed(self, payload, n=1, dt=0.05):
        for _ in range(n):
            self.link.feed(payload)
            self.clock.t += dt
            self.obs.tick()

    # ------------------------------------------------------------ F1
    def test_f1_debounce_to_failed_and_back(self):
        self.feed(b"95.0", 3)
        self.assertEqual(self.obs.f1_view()["state"], "PASSED")
        self.feed(b"nan", 4)
        self.assertEqual(self.obs.f1_view()["state"], "PREFAILED")
        self.assertFalse(self.obs.verdicts()["f1_failed"])                 # not qualified yet
        self.feed(b"-5", 1)
        self.assertEqual(self.obs.f1_view()["state"], "FAILED")
        self.assertTrue(self.obs.verdicts()["f1_failed"])
        self.feed(b"95.0", 2)
        self.assertEqual(self.obs.f1_view()["state"], "PREPASSED")
        self.assertTrue(self.obs.verdicts()["f1_failed"])                  # still the last qualified result
        self.feed(b"95.0", 3)
        self.assertEqual(self.obs.f1_view()["state"], "PASSED")
        self.assertFalse(self.obs.verdicts()["f1_failed"])

    def test_f1_reasons(self):
        self.feed(b"999.9")
        self.assertIn("outside", self.obs.f1_view()["last_reason"])
        self.feed(b"abc")
        self.assertEqual(self.obs.f1_view()["last_reason"], "not a number")
        self.feed(b"inf")
        self.assertEqual(self.obs.f1_view()["last_reason"], "not a finite number")

    def test_speed_view_keeps_last_valid_value(self):
        self.feed(b"88.0")
        self.feed(b"nan")
        v = self.obs.speed_view()
        self.assertEqual(v["value"], 88.0)
        self.assertFalse(v["last_sample_valid"])
        self.assertEqual(v["source"], "zenoh:vehicle/status/velocity_status")

    # ------------------------------------------------------------ F2
    def test_f2_not_armed_before_first_valid_sample(self):
        self.clock.t += 5
        self.obs.tick()
        self.assertFalse(self.obs.verdicts()["f2_failed"])
        self.feed(b"abc", 2)                                              # traffic, but never valid
        self.clock.t += 5
        self.obs.tick()
        self.assertFalse(self.obs.verdicts()["f2_failed"])
        self.assertFalse(self.obs.link_view()["monitor_armed"])

    def test_f2_timeout_and_recovery(self):
        self.feed(b"90.0", 3)                                             # last sample 0.05 s before "now"
        self.clock.t += 0.35
        self.obs.tick()
        self.assertFalse(self.obs.verdicts()["f2_failed"])               # 0.4 s of silence: within the timeout
        self.clock.t += 0.2
        self.obs.tick()
        self.assertTrue(self.obs.verdicts()["f2_failed"])                # > 500 ms of silence
        self.assertTrue(self.obs.speed_view()["stale"])
        self.assertEqual(self.obs.f1_view()["state"], "PASSED")          # silence is not F1's business
        self.feed(b"91.0")
        self.assertFalse(self.obs.verdicts()["f2_failed"])
        self.assertFalse(self.obs.speed_view()["stale"])

    def test_invalid_samples_keep_the_link_alive(self):
        self.feed(b"90.0")
        self.feed(b"nan", 20, dt=0.1)                                     # 2 s of implausible but present data
        v = self.obs.verdicts()
        self.assertFalse(v["f2_failed"])
        self.assertTrue(v["f1_failed"])

    def test_counters(self):
        self.feed(b"90.0", 4)
        self.assertEqual(self.obs.f1_view()["samples"], 4)
        self.assertEqual(self.obs.ticks, 4)


if __name__ == "__main__":
    unittest.main()
