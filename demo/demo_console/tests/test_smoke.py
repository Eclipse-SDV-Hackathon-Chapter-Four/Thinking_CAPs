"""Smoke test: fakes on free ports, the console server, the 13 checks."""
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


class SmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        sovd, cda, sim, console = (free_port() for _ in range(4))
        stats = os.path.join(cls.tmp, "stats.json")
        os.environ.update(SOVD_URL=f"http://127.0.0.1:{sovd}", CDA_URL=f"http://127.0.0.1:{cda}",
                          SIM_URL=f"http://127.0.0.1:{sim}", STATS_FILE=stats, DOCKER_CONTAINERS="",
                          CONSOLE_HOST="127.0.0.1", CONSOLE_PORT=str(console))
        import importlib
        import config
        importlib.reload(config)  # the environment above must win over an earlier import
        import fakes
        app = fakes.ScoreApp(stats)
        app.THRESHOLD = 3
        memory = fakes.DtcMemory()
        fakes.serve(sovd, fakes.score_handler(app, "components/cruise-control"))
        fakes.serve(cda, fakes.cda_handler(memory, "flxc1000", set()))
        fakes.serve(sim, fakes.sim_handler(memory, "FLXC1000", ["Standard", "Development"]))
        import server
        importlib.reload(server)  # BACKENDS is built at import time from config
        from http.server import ThreadingHTTPServer
        server.BACKENDS.cda.fetch_token()
        cls.srv = ThreadingHTTPServer(("127.0.0.1", console), server.Handler)
        cls.srv.daemon_threads = True
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{console}"
        time.sleep(1.2)  # first stats.json

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=5) as r:
            return r.status, json.loads(r.read().decode() or "null")

    def test_api_and_proxy(self):
        self.assertEqual(self.get("/api/config")[1]["cda"]["ecu"], "flxc1000")
        st, h = self.get("/api/health")
        self.assertTrue(h["sovd"]["up"] and h["cda"]["up"] and h["sim"]["up"] and h["cda"]["token"])
        st, speed = self.get("/proxy/sovd/sovd/v1/components/cruise-control/data/vehicle_speed")
        self.assertEqual(speed["id"], "vehicle_speed")
        st, faults = self.get("/proxy/cda/vehicle/v15/components/flxc1000/faults")
        self.assertEqual(faults["items"], [])
        st, page = self.get("/api/stats")
        self.assertTrue(page["ok"])
        with urllib.request.urlopen(self.base + "/", timeout=5) as r:
            self.assertIn(b"Demo Console", r.read())

    def test_runner_all_pass(self):
        import runner
        import server
        results = runner.run_all(server.BACKENDS)
        failed = [r for r in results if not r["ok"]]
        self.assertEqual(failed, [], msg=json.dumps(failed, indent=1))
        self.assertEqual(len(results), 13)
        st, log = self.get("/api/log?since=0")
        self.assertTrue(all("Authorization" not in json.dumps(e) for e in log["entries"]))


if __name__ == "__main__":
    unittest.main()
