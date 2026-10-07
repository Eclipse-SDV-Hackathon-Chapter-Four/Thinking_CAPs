# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: End-to-end test without Zenoh: 13 checks and both scenarios through the whole chain.
"""End to end without Zenoh: test vehicle -> stand-in (fed directly) -> console + automatic DTC
-> classic fakes. Runs the 13 checks and both scenarios through the vehicle control API."""
import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class FedPublisher:
    """Stands in for the zenoh publisher: hands each text straight to the stand-in's link."""

    def __init__(self, link):
        self.link = link

    def put(self, text):
        self.link.feed(text.encode())


class SmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib
        cls.tmp = tempfile.mkdtemp()
        standin, cda, sim, console, control = (free_port() for _ in range(5))
        os.environ.update(STANDIN_PORT=str(standin), SOVD_URL=f"http://127.0.0.1:{standin}",
                          CDA_URL=f"http://127.0.0.1:{cda}", SIM_URL=f"http://127.0.0.1:{sim}",
                          STATS_FILE=os.path.join(cls.tmp, "stats.json"), DOCKER_CONTAINERS="",
                          CONSOLE_HOST="127.0.0.1", CONSOLE_PORT=str(console), AUTO_DTC_PERIOD_S="0.2")
        import config
        importlib.reload(config)             # the environment above must win over an earlier import
        import classic_fakes
        import score_app
        import vehicle_sim
        importlib.reload(score_app)
        memory = classic_fakes.DtcMemory()
        cls.fakes = [classic_fakes.serve(cda, classic_fakes.cda_handler(memory, "flxc1000", set()), "127.0.0.1"),
                     classic_fakes.serve(sim, classic_fakes.sim_handler(memory, "FLXC1000", ["Standard"]), "127.0.0.1")]
        cls.app = score_app.ScoreApp()        # no zenoh: the test vehicle feeds the link directly
        cls.app.start()
        cls.standin = score_app.serve(cls.app, "127.0.0.1", standin)
        cls.vehicle = vehicle_sim.VehicleSim(rate_hz=20)
        cls.vehicle.publisher = FedPublisher(cls.app.link)
        cls.vehicle.start()
        from http.server import ThreadingHTTPServer
        cls.control = ThreadingHTTPServer(("127.0.0.1", control), vehicle_sim.control_handler(cls.vehicle))
        threading.Thread(target=cls.control.serve_forever, daemon=True).start()
        cls.sim_url = f"http://127.0.0.1:{control}"
        import server
        importlib.reload(server)              # BACKENDS and AUTO are built at import time from config
        cls.server = server
        server.BACKENDS.cda.fetch_token()
        server.AUTO.start()
        cls.srv = ThreadingHTTPServer(("127.0.0.1", console), server.Handler)
        cls.srv.daemon_threads = True
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{console}"
        time.sleep(1.3)                       # first stats.json, F2 armed

    @classmethod
    def tearDownClass(cls):
        cls.vehicle.stop()
        cls.server.AUTO.stop()
        cls.app.stop()
        for s in [cls.srv, cls.control, cls.standin, *cls.fakes]:
            s.shutdown()

    def get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=5) as r:
            return r.status, json.loads(r.read().decode() or "null")

    def test_1_api_and_proxy(self):
        self.assertEqual(self.get("/api/config")[1]["vehicle"]["key"], "vehicle/status/velocity_status")
        st, h = self.get("/api/health")
        self.assertTrue(h["sovd"]["up"] and h["cda"]["up"] and h["sim"]["up"] and h["cda"]["token"])
        st, speed = self.get("/proxy/sovd/sovd/v1/components/cruise-control/data/vehicle_speed")
        self.assertTrue(80 <= speed["data"]["value"] <= 110)
        st, link = self.get("/proxy/sovd/sovd/v1/components/cruise-diag/data/link_status")
        self.assertEqual(link["data"]["state"], "live")
        st, faults = self.get("/proxy/sovd/sovd/v1/components/cruise-diag/faults")
        self.assertEqual([f["code"] for f in faults["items"]], ["U0104"])
        st, auto = self.get("/api/auto")
        self.assertTrue(auto["running"])
        with urllib.request.urlopen(self.base + "/", timeout=5) as r:
            self.assertIn(b"Demo Console v2", r.read())

    def test_2_runner_all_pass(self):
        import runner
        results = runner.run_all(self.server.BACKENDS, auto=self.server.AUTO)
        failed = [r for r in results if not r["ok"]]
        self.assertEqual(failed, [], msg=json.dumps(failed, indent=1))
        self.assertEqual(len(results), 13)

    def test_3_scenarios_with_automatic_dtc(self):
        import runner
        vehicle = runner.Vehicle(self.sim_url, say=lambda *_: None)
        ctx = {"auto": self.server.AUTO}
        for kind in ("lost-link", "invalid-speed"):
            results = runner.scenario(self.server.BACKENDS, kind, vehicle, ctx)
            failed = [r for r in results if not r["ok"]]
            self.assertEqual(failed, [], msg=json.dumps(results, indent=1))
            self.assertEqual(len(results), 5)
        events = [e for e in self.server.AUTO.status()["events"] if e["change"] != "reset"]
        self.assertEqual([(e["fault"], e["change"]) for e in events],
                         [("U0104", "failing"), ("U0104", "healed"), ("P0500", "failing"), ("P0500", "healed")])
        self.assertTrue(all(e["ok"] for e in events))

    def test_4_reset(self):
        req = urllib.request.Request(self.base + "/api/reset", method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            out = json.loads(r.read().decode())
        self.assertTrue(out["ok"], out)
        st, faults = self.get("/proxy/sovd/sovd/v1/components/cruise-control/faults")
        self.assertEqual(faults["items"][0]["status"], 0)
        st, log = self.get("/api/log?since=0")
        self.assertTrue(all("Authorization" not in json.dumps(e) for e in log["entries"]))
        self.assertTrue(any(e.get("origin") == "auto" for e in log["entries"]))


if __name__ == "__main__":
    unittest.main()
