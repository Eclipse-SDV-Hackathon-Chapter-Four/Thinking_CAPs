import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backends import decode_status, bit_set  # noqa: E402


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

    def test_cda_object_with_mask(self):
        d = decode_status({"test_failed": True, "mask": "29"})
        self.assertEqual(d["raw"], 0x29)

    def test_cda_object_without_mask(self):
        d = decode_status({"test_failed": True, "confirmed_dtc": True, "pending_dtc": False})
        self.assertEqual(d["raw"], 0x09)
        self.assertTrue(bit_set({"confirmed_dtc": True}, 3))
        self.assertFalse(bit_set({"confirmed_dtc": True}, 0))

    def test_all_bytes_roundtrip(self):
        for v in range(256):
            d = decode_status(v)
            self.assertEqual(sum(b["set"] << b["bit"] for b in d["bits"]), v)

    def test_none(self):
        d = decode_status(None)
        self.assertIsNone(d["raw"])
        self.assertEqual(d["summary"], "no bits set")


if __name__ == "__main__":
    unittest.main()
