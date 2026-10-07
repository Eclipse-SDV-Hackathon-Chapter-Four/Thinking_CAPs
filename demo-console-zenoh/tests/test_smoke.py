# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: gateway stand-in + console with bridge, 13 checks, three scenarios)
# Goal: End-to-end test without Zenoh: 13 checks and the three scenarios through the whole chain.
"""End to end without Zenoh: test vehicle (fed directly into the console's link) -> console
(observer, fault model, bridge) <-> gateway stand-in (PR #40 contract) -> automatic DTC ->
classic fakes. Runs the 13 checks and the three scenarios through the vehicle control API."""
import json
import os
import socket
import sys
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
    """Stands in for the zenoh publisher: hands each text straight to the console's link."""

    def __init__(self, link):
        self.link = link

    def put(self, text):
        self.link.feed(text.encode())


class SmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib
        gw, cda, sim, console, control = (free_port() for _ in range(5))
        os.environ.update(SCORE_GATEWAY_ADDRESS=f"127.0.0.1:{gw}", SOVD_URL=f"http://127.0.0.1:{gw}",
                          CDA_URL=f"http://127.0.0.1:{cda}", SIM_URL=f"http://127.0.0.1:{sim}",
                          DOCKER_CONTAINERS="", CONSOLE_HOST="127.0.0.1", CONSOLE_PORT=str(console),
                          AUTO_DTC_PERIOD_S="0.2", SOVD_POLL_S="0.1", DIAG_TICK_S="0.05",
                          CRUISE_DEBOUNCE_FAILED_MS="300", CRUISE_DEBOUNCE_PASSED_MS="200")
        import config
        importlib.reload(config)             # the environment above must win over an earlier import
        import classic_fakes
        import score_app
        import server
        import vehicle_sim
        memory = classic_fakes.DtcMemory()
        cls.fakes = [classic_fakes.serve(cda, classic_fakes.cda_handler(memory, "flxc1000", set()), "127.0.0.1"),
                     classic_fakes.serve(sim, classic_fakes.sim_handler(memory, "FLXC1000", ["Standard"]), "127.0.0.1")]
        cls.gateway = score_app.CruiseGateway()
        cls.standin = score_app.serve(cls.gateway, "127.0.0.1", gw)
        cls.console = server.build()         # no zenoh: the test vehicle feeds the link directly
        cls.vehicle = vehicle_sim.VehicleSim(rate_hz=20)
        cls.vehicle.publisher = FedPublisher(cls.console.link)
        cls.vehicle.start()
        from http.server import ThreadingHTTPServer
        cls.control = ThreadingHTTPServer(("127.0.0.1", control), vehicle_sim.control_handler(cls.vehicle))
        threading.Thread(target=cls.control.serve_forever, daemon=True).start()
        cls.sim_url = f"http://127.0.0.1:{control}"
        cls.console.backends.cda.fetch_token()
        cls.console.start(zenoh=False)
        cls.srv = ThreadingHTTPServer(("127.0.0.1", console), server.Handler)
        cls.srv.daemon_threads = True
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{console}"
        time.sleep(1.5)                      # first polls, F2 armed, contract probed

    @classmethod
    def tearDownClass(cls):
        cls.vehicle.stop()
        cls.console.stop()
        for s in [cls.srv, cls.control, cls.standin, *cls.fakes]:
            s.shutdown()

    def get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=5) as r:
            return r.status, json.loads(r.read().decode() or "null")

    def test_1_api_and_proxy(self):
        self.assertEqual(self.get("/api/config")[1]["sovd"]["component"], "cruise")
        st, h = self.get("/api/health")
        self.assertTrue(h["sovd"]["up"] and h["cda"]["up"] and h["sim"]["up"] and h["cda"]["token"], h)
        self.assertEqual(h["sovd"]["sovd_version"], "1.1.0")
        st, v = self.get("/api/vehicle")
        self.assertEqual(v["link"]["state"], "live")
        self.assertTrue(80 <= v["speed"]["value"] <= 110)
        self.assertEqual(v["f1"]["state"], "PASSED")
        st, g = self.get("/api/sovd")
        self.assertTrue(g["reachable"], g)
        self.assertTrue(g["contract"]["ok"], g["contract"])
        self.assertEqual(g["items"]["fault"]["data"]["status"], "passed")
        self.assertEqual(g["items"]["switch"]["data"], {"stuck": False})
        self.assertTrue(g["bridge"]["enabled"] and g["bridge"]["in_sync"])
        st, f = self.get("/api/faults")
        self.assertEqual([x["code"] for x in f["items"]], ["P0500", "U0104"])
        st, speed = self.get("/proxy/sovd/sovd/v1/components/cruise/data/vehicle_speed")
        self.assertTrue(94 <= speed["data"]["value"] <= 106)
        st, auto = self.get("/api/auto")
        self.assertTrue(auto["running"])
        with urllib.request.urlopen(self.base + "/", timeout=5) as r:
            self.assertIn(b"Demo Console v2", r.read())

    def test_2_runner_all_pass(self):
        import runner
        results = runner.run_all(self.console.backends, console=self.console)
        failed = [r for r in results if not r["ok"]]
        self.assertEqual(failed, [], msg=json.dumps(failed, indent=1))
        self.assertEqual(len(results), 13)

    def test_3_scenarios_with_automatic_dtc(self):
        import runner
        vehicle = runner.Vehicle(self.sim_url, say=lambda *_: None)
        ctx = {"console": self.console}
        for kind in runner.KINDS:
            results = runner.scenario(self.console.backends, kind, vehicle, ctx)
            failed = [r for r in results if not r["ok"]]
            self.assertEqual(failed, [], msg=json.dumps(results, indent=1))
            self.assertEqual(len(results), 5)
        events = [e for e in self.console.auto.status()["events"] if e["change"] != "reset"]
        self.assertEqual([(e["fault"], e["change"]) for e in events],
                         [("U0104", "failing"), ("U0104", "healed"), ("P0500", "failing"), ("P0500", "healed"),
                          ("P0500", "failing"), ("P0500", "healed")])
        self.assertTrue(all(e["ok"] for e in events))
        bridge = [e for e in self.console.sovd_view()["bridge"]["events"] if e["reason"] == "edge"]
        self.assertEqual([e["stuck"] for e in bridge], [True, False])       # one edge each way, from the invalid-speed scenario

    def test_4_reset(self):
        req = urllib.request.Request(self.base + "/api/reset", method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            out = json.loads(r.read().decode())
        self.assertTrue(out["ok"], out)
        time.sleep(0.3)
        st, faults = self.get("/api/faults")
        self.assertEqual([f["status"] for f in faults["items"]], [0, 0])
        st, log = self.get("/api/log?since=0")
        self.assertTrue(all("Authorization" not in json.dumps(e) for e in log["entries"]))
        origins = {e.get("origin") for e in log["entries"]}
        self.assertTrue({"auto", "console", "bridge", "reset"} <= origins, origins)


if __name__ == "__main__":
    unittest.main()
