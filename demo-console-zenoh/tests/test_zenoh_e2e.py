# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: End-to-end test with real Zenoh pub/sub on localhost, including link loss.
"""Real Zenoh pub/sub on localhost: test vehicle publishes, VehicleLink receives, link loss detected.
Skipped when eclipse-zenoh is not installed."""
import os
import socket
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import zenoh  # noqa: F401
    HAVE_ZENOH = True
except ImportError:
    HAVE_ZENOH = False


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@unittest.skipUnless(HAVE_ZENOH, "eclipse-zenoh not installed")
class ZenohEndToEnd(unittest.TestCase):
    def test_publish_receive_and_loss(self):
        from vehicle_link import VehicleLink
        from vehicle_sim import VehicleSim
        endpoint = f"tcp/127.0.0.1:{free_port()}"
        key = "vehicle/status/velocity_status"
        sim = VehicleSim(key=key, rate_hz=20, mode="fixed", value=77.7)
        sim.open(listen=[endpoint])                       # like the virtual vehicle on 127.0.0.1
        link = VehicleLink(key, endpoints=[endpoint])
        try:
            self.assertTrue(link.start("peer", [endpoint], [], False), link.error)
            sim.start()
            deadline = time.time() + 10
            while time.time() < deadline and link.samples < 10:
                time.sleep(0.1)
            st = link.status(0.5)
            self.assertGreaterEqual(link.samples, 10, st)
            self.assertEqual(st["state"], "live")
            self.assertTrue(st["connected"])
            self.assertEqual(st["last_raw"], "77.7")
            self.assertAlmostEqual(st["last_value_kmh"], 77.7)
            sim.set_mode("stop")
            time.sleep(0.8)
            self.assertEqual(link.status(0.5)["state"], "lost")
        finally:
            sim.stop()
            link.stop()


if __name__ == "__main__":
    unittest.main()
