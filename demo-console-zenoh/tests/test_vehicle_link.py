# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Tests of the payload decoding and the link statistics.
"""Payload decoding and link statistics (no zenoh needed)."""
import math
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from vehicle_link import VehicleLink, decode_speed  # noqa: E402


class FakeClock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class DecodeTests(unittest.TestCase):
    def test_text_floats(self):
        self.assertEqual(decode_speed(b"96.4")[0], 96.4)
        self.assertEqual(decode_speed(b"  96.4\n")[0], 96.4)
        self.assertEqual(decode_speed(b"9.64e1")[0], 96.4)
        self.assertEqual(decode_speed(b"96.4\x00")[0], 96.4)        # C string with its terminator
        self.assertEqual(decode_speed(b"0")[0], 0.0)

    def test_unit_factor(self):
        self.assertAlmostEqual(decode_speed(b"10", factor=3.6)[0], 36.0)

    def test_nan_and_inf_decode_but_are_not_finite(self):
        self.assertTrue(math.isnan(decode_speed(b"nan")[0]))
        self.assertTrue(math.isinf(decode_speed(b"inf")[0]))
        self.assertIsNone(decode_speed(b"nan")[2])                  # rejected later by the plausibility check

    def test_garbage_is_an_error_not_an_exception(self):
        value, raw, err = decode_speed(b"abc")
        self.assertIsNone(value)
        self.assertEqual(raw, "abc")
        self.assertEqual(err, "not a number")
        self.assertEqual(decode_speed(b"")[2], "empty payload")
        self.assertEqual(decode_speed(b"\xff\xfe")[2], "not a float32 string")

    def test_binary_float32_fallback(self):
        value, raw, err = decode_speed(struct.pack("<f", 88.5))
        self.assertAlmostEqual(value, 88.5, places=4)
        self.assertTrue(raw.startswith("float32 "))
        self.assertIsNone(err)

    def test_four_char_text_is_text_not_binary(self):
        self.assertEqual(decode_speed(b"12.5")[0], 12.5)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.link = VehicleLink("vehicle/status/velocity_status", clock=self.clock, wall=self.clock)

    def test_states_and_rate(self):
        self.assertEqual(self.link.status(0.5)["state"], "no-session")
        for i in range(10):                       # 10 samples in 1 s
            self.link.feed(b"90.0")
            self.clock.t += 0.1
        st = self.link.status(0.5)
        self.assertEqual(st["state"], "live")
        self.assertEqual(st["samples"], 10)
        self.assertEqual(st["rate_hz"], 5.0)      # 10 samples over the 2 s window
        self.assertEqual(st["last_value_kmh"], 90.0)
        self.clock.t += 0.6
        self.assertEqual(self.link.status(0.5)["state"], "lost")

    def test_drain_returns_each_sample_once(self):
        self.link.feed(b"1")
        self.link.feed(b"x")
        out = self.link.drain()
        self.assertEqual([s.raw for s in out], ["1", "x"])
        self.assertEqual(self.link.invalid, 1)
        self.assertEqual(self.link.drain(), [])

    def test_missing_zenoh_is_reported(self):
        link = VehicleLink("k")
        try:
            import zenoh  # noqa: F401
            self.skipTest("zenoh is installed here")
        except ImportError:
            self.assertFalse(link.start())
            self.assertIn("eclipse-zenoh", link.status(0.5)["error"])
            self.assertEqual(link.status(0.5)["state"], "error")


if __name__ == "__main__":
    unittest.main()
