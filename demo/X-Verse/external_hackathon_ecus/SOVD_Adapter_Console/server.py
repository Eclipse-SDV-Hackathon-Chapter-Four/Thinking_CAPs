# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: hosts the Zenoh link, the observer, the fault model and the bridge)
# Goal: The console (tester): Zenoh input, F1/F2 observer, fault model + bridge to the gateway, automatic DTC, page and checks.
"""Demo Console server (the tester).

    virtual vehicle --Zenoh--> [ VehicleLink -> Observer (F1, F2) -> FaultModel ] <--SOVD--> opensovd-gateway (PR #40)
                                                        |                 |  bridge: PUT speed_sensor_stuck
                                                        v                 v
                                                  automatic DTC -> ECU simulator <-- CDA (read back)

    python server.py                # http://localhost:8080, Zenoh as configured
    python server.py --no-zenoh     # no subscription (tests feed the link directly)

Routes
  GET  /                        the page
  GET  /static/<file>
  GET  /api/config              names and paths the page needs
  GET  /api/health              the three backends, cached 1 s
  GET  /api/docker              docker ps, cached 5 s
  GET  /api/stats               in-process counters with rates
  GET  /api/vehicle             Zenoh link, speed, F1 monitor (the console's observer)
  GET  /api/sovd                the gateway as last read: four items, contract probe, bridge state
  GET  /api/faults              the two faults of the tester's fault model
  GET  /api/log?since=<seq>     traffic log entries after <seq>
  GET  /api/auto                automatic classic DTC: mapping, state, last events
  POST /api/switch {"stuck":b}  test only: write the gateway's injection switch directly
  POST /api/reset               forget the fault memory, switch back, clear the ECU memory, re-arm the automation
  GET  /api/run  POST /api/run  runner status / start the checks
  ANY  /proxy/sovd/<path>       forwarded to the SOVD gateway (stand-in or Rust build)
  ANY  /proxy/cda/<path>        forwarded to the CDA with the bearer token
  ANY  /proxy/sim/<path>        forwarded to the ECU simulator
"""
import argparse
import json
import mimetypes
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import config
import discover
import runner
from auto_dtc import AutoDtc
from backends import Backends
from faults import FaultModel
from observer import Observer
from vehicle_link import VehicleLink

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
CONSOLE = None   # set by build()


def observer_settings():
    return {"f1_threshold": config.F1_THRESHOLD, "speed_min": config.SPEED_MIN_KMH, "speed_max": config.SPEED_MAX_KMH,
            "link_timeout_s": config.LINK_TIMEOUT_MS / 1000.0, "f1_code": config.F1_CODE, "f2_code": config.F2_CODE}


class Console:
    """Everything the tester runs: link, observer, fault model with bridge, automation, runner."""

    def __init__(self, link=None, clock=time.monotonic, wall=time.time):
        self.clock, self.wall = clock, wall
        self.backends = Backends()
        self.link = link or VehicleLink(config.SPEED_KEY, config.speed_factor(), config.ZENOH_CONNECT, clock, wall)
        self.observer = Observer(self.link, observer_settings(), clock, wall)
        self.faults = FaultModel(self.backends, self.observer, clock=clock, wall=wall)
        self.auto = AutoDtc(self.backends, config.dtc_map(), self.faults.faults_view,
                            config.AUTO_DTC_MASK_ACTIVE, config.AUTO_DTC_MASK_HEALED,
                            config.AUTO_DTC_PERIOD_S, config.AUTO_DTC_READBACK_S, config.AUTO_DTC)
        self.run = {"running": False, "started": None, "finished": None, "results": [], "lock": threading.Lock()}
        self.contract = {"checked": None, "ok": None}
        self.cycle_error = None
        self._stats = (None, None)   # (prev, now) snapshots of (t, counters)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._threads = []
        self.zenoh_state = "not started"

    # ------------------------------------------------------------ lifecycle
    def start(self, zenoh=True):
        if zenoh:
            connect, found = config.ZENOH_CONNECT, ""
            if config.VEHICLE_HOST and not connect:
                connect = discover.find(config.VEHICLE_HOST)
                found = (f" (found on {config.VEHICLE_HOST} by scouting)" if connect
                         else f" (no Zenoh node answers on {config.VEHICLE_HOST} yet - scouting again every 5 s)")
                connect = connect or [f"tcp/{config.VEHICLE_HOST}:7447"]
            self.link.start(config.ZENOH_MODE, connect, config.ZENOH_LISTEN, config.ZENOH_MULTICAST_SCOUTING)
            self.zenoh_state = (f"NO VEHICLE INPUT - {self.link.error}" if self.link.error else
                                f"subscribed to '{config.SPEED_KEY}' via {config.ZENOH_MODE} {','.join(self.link.endpoints)}{found}")
            if config.VEHICLE_HOST:
                self._spawn("vehicle-finder", self._follow_vehicle, config.VEHICLE_HOST)
        else:
            self.zenoh_state = "no Zenoh session (fed directly)"
        self._spawn("observer", self._observer_loop)
        self._spawn("gateway", self._gateway_loop)
        self._spawn("stats", self._stats_loop)
        self.auto.start()

    def _spawn(self, name, target, *args):
        t = threading.Thread(target=target, args=args, name=name, daemon=True)
        t.start()
        self._threads.append(t)

    def stop(self):
        self._stop.set()
        self.auto.stop()
        self.link.stop()

    def _observer_loop(self):
        while not self._stop.wait(config.DIAG_TICK_S):
            try:
                self.observer.tick()
            except Exception as e:  # never stop observing
                self.cycle_error = f"observer: {type(e).__name__}: {e}"[:200]

    def _gateway_loop(self):
        last_probe = 0.0
        while not self._stop.wait(config.SOVD_POLL_S):
            try:
                self.faults.poll()
                if time.time() - last_probe >= 10.0:
                    last_probe = time.time()
                    self.probe_contract()
            except Exception as e:
                self.cycle_error = f"gateway: {type(e).__name__}: {e}"[:200]

    def _stats_loop(self):
        while not self._stop.wait(1.0):
            with self._lock:
                self._stats = (self._stats[1], (time.time(), self.counters()))

    def _follow_vehicle(self, host, every_s=5.0, find=discover.find):
        """While no speed sample arrives, scout `host` again and reconnect when none of our
        endpoints is announced any more (a restarted vehicle listens on new random ports)."""
        while not self._stop.wait(every_s):
            if self.link.status(config.LINK_TIMEOUT_MS / 1000.0)["state"] == "live":
                continue
            endpoints = find(host)
            if endpoints and not set(endpoints) & set(self.link.endpoints):
                print(f"vehicle {host} now on {','.join(endpoints)} - reconnecting", flush=True)
                self.link.reconnect(endpoints)

    # ------------------------------------------------------------ views
    def counters(self):
        g = self.faults.gateway_view()
        return {"vehicle_samples": self.link.samples, "observer_ticks": self.observer.ticks,
                "gateway_polls": g["polls"], "sovd_requests": self.backends.log.counts.get("sovd", 0),
                "bridge_writes": g["bridge"]["writes"], "auto_polls": self.auto.polls}

    def stats(self):
        with self._lock:
            prev, now = self._stats
        counters = self.counters()
        rates = {}
        if prev and now and now[0] > prev[0]:
            dt = now[0] - prev[0]
            rates = {k: round((now[1].get(k, 0) - prev[1].get(k, 0)) / dt, 1) for k in counters}
        return {"ok": True, "source": "console process", "ts": time.time(), "age_s": 0.0, "counters": counters,
                "rates": rates, "cycle_error": self.cycle_error, "error": None}

    def vehicle_view(self):
        return {"link": self.observer.link_view(), "speed": self.observer.speed_view(), "f1": self.observer.f1_view(),
                "zenoh": self.zenoh_state}

    def sovd_view(self):
        out = self.faults.gateway_view()
        out["url"], out["base"] = config.SOVD_URL, config.SOVD_BASE
        out["contract"] = dict(self.contract)
        out["debounce_ms"] = {"failed": config.CRUISE_DEBOUNCE_FAILED_MS, "passed": config.CRUISE_DEBOUNCE_PASSED_MS}
        return out

    def probe_contract(self):
        """Does the gateway serve the PR #40 contract? component present, four items, switch writable."""
        b = self.backends
        r1, comps = b.sovd_components(origin="console")
        r2, items = b.sovd_data_list(origin="console")
        ids = [i.get("id") for i in items if isinstance(i, dict)]
        want = config.sovd_items()
        by_id = {i.get("id"): i for i in items if isinstance(i, dict)}
        switch = by_id.get(want["switch"]) or {}
        out = {"checked": time.time(), "ok": False, "components": [c.get("id") for c in comps if isinstance(c, dict)],
               "component_found": any(c.get("id") == config.SOVD_COMPONENT for c in comps if isinstance(c, dict)),
               "items": ids, "missing": [v for v in want.values() if v not in ids],
               "switch_category": switch.get("category"), "error": r1.problem() or r2.problem()}
        out["ok"] = out["component_found"] and not out["missing"] and r1.ok and r2.ok
        with self._lock:
            self.contract = out
        return out

    # ------------------------------------------------------------ actions
    def reset_all(self):
        """Test-only reset between dry runs: fault memory, the gateway's switch, the ECU memory, the automation."""
        out = {}
        r = self.faults.reset()
        out["switch"] = r.status or r.error
        r = self.backends.sim_clear(origin="reset")
        out["ecu_memory"] = r.status or r.error
        self.auto.reset()
        out["ok"] = all(isinstance(v, int) and 200 <= v < 300 for k, v in out.items() if k != "ok")
        return out

    def start_run(self):
        with self.run["lock"]:
            if self.run["running"]:
                return False
            self.run.update(running=True, started=time.time(), finished=None, results=[])

        def work():
            try:
                runner.run_all(self.backends, lambda r: self.run["results"].append(r), console=self)
            finally:
                self.run.update(running=False, finished=time.time())
        threading.Thread(target=work, daemon=True).start()
        return True

    def run_status(self):
        return {k: self.run[k] for k in ("running", "started", "finished", "results")}


def build(link=None, clock=time.monotonic, wall=time.time):
    """Create the console object the handler serves (tests call this with a fed link)."""
    global CONSOLE
    CONSOLE = Console(link, clock, wall)
    return CONSOLE


class Handler(BaseHTTPRequestHandler):
    server_version = "DemoConsole/" + config.VERSION
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):  # quiet: the traffic log is the record
        pass

    # helpers
    def send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else None

    # routing
    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_PUT(self):
        self.route("PUT")

    def do_DELETE(self):
        self.route("DELETE")

    def route(self, method):
        url = urlsplit(self.path)
        path, query = url.path, parse_qs(url.query)
        try:
            if path.startswith("/proxy/"):
                return self.proxy(method, path[len("/proxy/"):], url.query)
            if path.startswith("/api/"):
                return self.api(method, path[5:], query)
            if method != "GET":
                return self.send_json({"error": "method not allowed"}, 405)
            if path == "/":
                path = "/static/index.html"
            if path.startswith("/static/"):
                return self.static(path[len("/static/"):])
            self.send_json({"error": "not found"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:  # never take the server down
            self.send_json({"error": f"{type(e).__name__}: {e}"}, 500)

    def static(self, name):
        full = os.path.normpath(os.path.join(STATIC, name))
        if not full.startswith(STATIC) or not os.path.isfile(full):
            return self.send_json({"error": "not found"}, 404)
        with open(full, "rb") as f:
            self.send_bytes(f.read(), mimetypes.guess_type(full)[0] or "text/plain")

    def api(self, method, name, query):
        c = CONSOLE
        if c is None:
            return self.send_json({"error": "console not built"}, 503)
        b = c.backends
        if name == "config" and method == "GET":
            return self.send_json(config.public())
        if name == "health" and method == "GET":
            return self.send_json(b.health())
        if name == "docker" and method == "GET":
            return self.send_json(b.docker())
        if name == "stats" and method == "GET":
            return self.send_json(c.stats())
        if name == "vehicle" and method == "GET":
            return self.send_json(c.vehicle_view())
        if name == "sovd" and method == "GET":
            return self.send_json(c.sovd_view())
        if name == "faults" and method == "GET":
            return self.send_json({"items": c.faults.faults_view()})
        if name == "log" and method == "GET":
            since = int((query.get("since") or ["0"])[0])
            return self.send_json({"entries": b.log.since(since), "seq": b.log.seq})
        if name == "auto" and method == "GET":
            return self.send_json(c.auto.status())
        if name == "switch" and method == "POST":
            try:
                body = json.loads((self.read_body() or b"{}").decode() or "{}")
                stuck = body.get("stuck")
            except (ValueError, AttributeError):
                stuck = None
            if not isinstance(stuck, bool):
                return self.send_json({"error": 'body must be {"stuck": true|false}'}, 400)
            r = c.faults.set_switch(stuck, origin="page")
            return self.send_json({"ok": r.ok, "status": r.status, "error": r.problem()}, 200 if r.ok else 502)
        if name == "reset" and method == "POST":
            out = c.reset_all()
            return self.send_json(out, 200 if out["ok"] else 502)
        if name == "run":
            if method == "POST":
                started = c.start_run()
                return self.send_json({"started": started, **c.run_status()}, 202 if started else 409)
            return self.send_json(c.run_status())
        self.send_json({"error": "not found"}, 404)

    def proxy(self, method, rest, query):
        name, _, path = rest.partition("/")
        b = CONSOLE.backends
        backend = {"sovd": b.sovd, "cda": b.cda, "sim": b.sim}.get(name)
        if backend is None:
            return self.send_json({"error": "unknown backend"}, 404)
        path = "/" + path + ("?" + query if query else "")
        body = self.read_body() if method in ("POST", "PUT") else None
        headers = {}
        if body is not None and self.headers.get("Content-Type"):
            headers["Content-Type"] = self.headers["Content-Type"]
        r = backend.request(method, path, body, headers, origin="page")
        if r.status == 0:
            return self.send_json({"error": r.error, "backend": name}, 502)
        self.send_bytes(r.body, r.content_type or "application/json", r.status)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    # On Windows SO_REUSEADDR lets a second process bind the same port silently,
    # and requests then split between an old and a new console. Fail loudly instead.
    allow_reuse_address = os.name != "nt"


def main():
    ap = argparse.ArgumentParser(description="Demo Console v2 (tester)")
    ap.add_argument("--no-zenoh", action="store_true", help="do not subscribe (tests and offline use)")
    a = ap.parse_args()
    c = build()
    if not c.backends.cda.token:
        c.backends.cda.fetch_token()
    c.start(zenoh=not a.no_zenoh)
    try:
        srv = Server((config.CONSOLE_HOST, config.CONSOLE_PORT), Handler)
    except OSError as e:
        c.stop()
        print(f"cannot listen on port {config.CONSOLE_PORT}: {e.strerror or e}. Another console or program uses it "
              f"(see: ss -ltnp 'sport = :{config.CONSOLE_PORT}'). Stop it or set CONSOLE_PORT.", flush=True)
        raise SystemExit(1)
    print(f"Demo Console v{config.VERSION} on http://localhost:{config.CONSOLE_PORT}  "
          f"(sovd {config.SOVD_URL} component '{config.SOVD_COMPONENT}' bridge {'on' if config.FAULT_BRIDGE else 'off'}, "
          f"cda {config.CDA_URL} token={'ok' if c.backends.cda.token else 'none'}, sim {config.SIM_URL}, "
          f"auto DTC {'on' if config.AUTO_DTC else 'off'}) - vehicle: {c.zenoh_state}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        c.stop()


if __name__ == "__main__":
    main()
