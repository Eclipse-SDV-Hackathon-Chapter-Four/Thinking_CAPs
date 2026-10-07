# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Tests of the automatic classic DTC: edges, read-back, retry after a simulator outage, reset.
"""Automatic classic DTC: edges, read-back, retry after a simulator outage, reset (stub backends)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from auto_dtc import AutoDtc  # noqa: E402
from backends import Response  # noqa: E402

E1, E2 = "components/cruise-control", "components/cruise-diag"


class StubBackends:
    """S-CORE faults per entity, an ECU memory behind a 'CDA', and a switch to break the simulator."""

    def __init__(self):
        self.score = {E1: [{"code": "P0500", "display": "speed implausible", "status": 0}],
                      E2: [{"code": "U0104", "display": "lost communication", "status": 0}]}
        self.ecu = {}           # dtc -> mask (int)
        self.sim_up = True
        self.puts = []

    def sovd_faults(self, entity=None, origin=None):
        return Response(200), self.score[entity]

    def set_score(self, code, status):
        for items in self.score.values():
            for f in items:
                if f["code"] == code:
                    f["status"] = status

    def sim_set(self, code, mask, origin=None):
        self.puts.append((code, mask))
        if not self.sim_up:
            return Response(0, error="ConnectionRefusedError")
        self.ecu[code] = int(mask, 16)
        return Response(201)

    def cda_faults(self, origin=None):
        return Response(200), [{"code": c, "status": {"mask": f"{m:02X}"}} for c, m in self.ecu.items()]


class AutoDtcTests(unittest.TestCase):
    def setUp(self):
        self.b = StubBackends()
        self.auto = AutoDtc(self.b, {"P0500": "01E241", "U0104": "01E242"}, [E1, E2], "2F", "28",
                            period_s=0.01, readback_s=0.5)

    def events(self):
        return [e for e in self.auto.status()["events"] if e["change"] != "reset"]

    def test_quiet_when_nothing_fails(self):
        self.auto.poll_once()
        self.auto.poll_once()
        self.assertEqual(self.b.puts, [])

    def test_failing_then_healed(self):
        self.b.set_score("U0104", 0x0D)
        self.auto.poll_once()
        self.assertEqual(self.b.ecu, {"01E242": 0x2F})
        ev = self.events()[-1]
        self.assertTrue(ev["ok"])
        self.assertEqual((ev["fault"], ev["change"], ev["readback"]), ("U0104", "failing", "0x2F"))
        self.auto.poll_once()                                   # still failing: no second PUT
        self.assertEqual(len(self.b.puts), 1)
        self.b.set_score("U0104", 0x0C)
        self.auto.poll_once()
        self.assertEqual(self.b.ecu["01E242"], 0x28)
        self.assertEqual(self.events()[-1]["change"], "healed")
        self.assertEqual(self.auto.status()["state"]["U0104"]["ecu_mask"], "28")

    def test_both_faults_independent(self):
        self.b.set_score("P0500", 0x0D)
        self.b.set_score("U0104", 0x0D)
        self.auto.poll_once()
        self.assertEqual(self.b.ecu, {"01E241": 0x2F, "01E242": 0x2F})

    def test_simulator_outage_keeps_the_edge_for_a_retry(self):
        self.b.sim_up = False
        self.b.set_score("P0500", 0x0D)
        self.auto.poll_once()
        self.assertFalse(self.events()[-1]["ok"])
        self.b.sim_up = True
        self.auto.state["P0500"]["retry_at"] = 0                # skip the 5 s back-off in the test
        self.auto.poll_once()
        self.assertEqual(self.b.ecu, {"01E241": 0x2F})
        self.assertTrue(self.events()[-1]["ok"])

    def test_readback_mismatch_is_reported(self):
        original = self.b.cda_faults
        self.b.cda_faults = lambda origin=None: (Response(200), [])   # CDA never shows it
        self.b.set_score("P0500", 0x0D)
        self.auto.poll_once()
        ev = self.events()[-1]
        self.assertFalse(ev["ok"])
        self.assertIn("expected 0x2F", ev["error"])
        self.b.cda_faults = original

    def test_reset_rearms(self):
        self.b.set_score("U0104", 0x0D)
        self.auto.poll_once()
        self.auto.reset()
        self.auto.poll_once()                                   # failing again after a reset: re-applied
        self.assertEqual(len(self.b.puts), 2)


if __name__ == "__main__":
    unittest.main()
