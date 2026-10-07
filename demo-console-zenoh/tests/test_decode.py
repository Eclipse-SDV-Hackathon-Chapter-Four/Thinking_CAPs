# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Tests of the UDS status byte decoder and the fault lookup helpers.
"""UDS status byte decoder and fault lookup helpers."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backends import active_fault, bit_set, decode_status, find_fault  # noqa: E402


class DecodeTests(unittest.TestCase):
    def test_int(self):
        d = decode_status(0x0D)
        self.assertEqual(d["hex"], "0x0D")
        self.assertEqual([b["set"] for b in d["bits"]], [True, False, True, True, False, False, False, False])
        self.assertEqual(d["summary"], "failing, pending, confirmed")

    def test_hex_string(self):
        self.assertEqual(decode_status("2F")["raw"], 0x2F)
        self.assertEqual(decode_status("0x2f")["raw"], 0x2F)
        self.assertIsNone(decode_status("zz")["raw"])

    def test_cda_object(self):
        self.assertEqual(decode_status({"test_failed": True, "mask": "29"})["raw"], 0x29)
        self.assertEqual(decode_status({"test_failed": True, "confirmed_dtc": True})["raw"], 0x09)
        self.assertTrue(bit_set({"confirmed_dtc": True}, 3))
        self.assertFalse(bit_set({"confirmed_dtc": True}, 0))

    def test_all_bytes_roundtrip(self):
        for v in range(256):
            self.assertEqual(sum(b["set"] << b["bit"] for b in decode_status(v)["bits"]), v)

    def test_find_and_active(self):
        items = [{"code": "01E241", "status": {"mask": "00"}}, {"code": "01E242", "status": {"mask": "28"}}]
        self.assertIsNotNone(find_fault(items, "1e241"))
        self.assertIsNone(active_fault(items, "01E241"))      # listed, but status 00
        self.assertIsNotNone(active_fault(items, "01E242"))


if __name__ == "__main__":
    unittest.main()
