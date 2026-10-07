# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: The console (tester): serves the page, proxies the backends with the CDA token, runs the automatic DTC and the checks.
"""Demo Console server (the tester): serves the page, proxies the three backends (adding
the CDA token), runs the automatic classic DTC, keeps the traffic log and runs the checks.

    python server.py            # http://localhost:8080

Routes
  GET  /                        the page
  GET  /static/<file>
  GET  /api/config              names and paths the page needs
  GET  /api/health              the three backends, cached 1 s
  GET  /api/docker              docker ps, cached 5 s
  GET  /api/stats               stats.json with rates
  GET  /api/log?since=<seq>     traffic log entries after <seq>
  GET  /api/auto                automatic classic DTC: mapping, state, last events
  POST /api/reset               clear S-CORE faults (both entities) + ECU memory, re-arm the automation
  GET  /api/run  POST /api/run  runner status / start the checks
  ANY  /proxy/sovd/<path>       forwarded to the SOVD side (stand-in or real gateway)
  ANY  /proxy/cda/<path>        forwarded to the CDA with the bearer token
  ANY  /proxy/sim/<path>        forwarded to the ECU simulator
"""
import json
import mimetypes
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import config
import runner
from auto_dtc import AutoDtc
from backends import Backends

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
BACKENDS = Backends()
AUTO = AutoDtc(BACKENDS, config.dtc_map(), [config.SOVD_ENTITY, config.SOVD_DIAG_ENTITY],
               config.AUTO_DTC_MASK_ACTIVE, config.AUTO_DTC_MASK_HEALED,
               config.AUTO_DTC_PERIOD_S, config.AUTO_DTC_READBACK_S, config.AUTO_DTC)
RUN = {"running": False, "started": None, "finished": None, "results": [], "lock": threading.Lock()}


def start_run():
    with RUN["lock"]:
        if RUN["running"]:
            return False
        RUN.update(running=True, started=time.time(), finished=None, results=[])

    def work():
        try:
            runner.run_all(BACKENDS, lambda r: RUN["results"].append(r), auto=AUTO)
        finally:
            RUN.update(running=False, finished=time.time())
    threading.Thread(target=work, daemon=True).start()
    return True


def run_status():
    return {k: RUN[k] for k in ("running", "started", "finished", "results")}


def reset_all():
    """Test-only reset between dry runs: both SOVD fault lists, the ECU memory, the automation."""
    out = {}
    for entity in (config.SOVD_ENTITY, config.SOVD_DIAG_ENTITY):
        r = BACKENDS.sovd_clear_faults(entity, origin="reset")
        out[entity] = r.status or r.error
    r = BACKENDS.sim_clear(origin="reset")
    out["ecu_memory"] = r.status or r.error
    AUTO.reset()
    out["ok"] = all(isinstance(v, int) and 200 <= v < 300 for k, v in out.items() if k != "ok")
    return out


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
        b = BACKENDS
        if name == "config" and method == "GET":
            return self.send_json(config.public())
        if name == "health" and method == "GET":
            return self.send_json(b.health())
        if name == "docker" and method == "GET":
            return self.send_json(b.docker())
        if name == "stats" and method == "GET":
            return self.send_json(b.stats())
        if name == "log" and method == "GET":
            since = int((query.get("since") or ["0"])[0])
            return self.send_json({"entries": b.log.since(since), "seq": b.log.seq})
        if name == "auto" and method == "GET":
            return self.send_json(AUTO.status())
        if name == "reset" and method == "POST":
            out = reset_all()
            return self.send_json(out, 200 if out["ok"] else 502)
        if name == "run":
            if method == "POST":
                started = start_run()
                return self.send_json({"started": started, **run_status()}, 202 if started else 409)
            return self.send_json(run_status())
        self.send_json({"error": "not found"}, 404)

    def proxy(self, method, rest, query):
        name, _, path = rest.partition("/")
        backend = {"sovd": BACKENDS.sovd, "cda": BACKENDS.cda, "sim": BACKENDS.sim}.get(name)
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
    if not BACKENDS.cda.token:
        BACKENDS.cda.fetch_token()
    AUTO.start()
    try:
        srv = Server((config.CONSOLE_HOST, config.CONSOLE_PORT), Handler)
    except OSError as e:
        AUTO.stop()
        print(f"cannot listen on port {config.CONSOLE_PORT}: {e.strerror or e}. Another console or program uses it "
              f"(see: ss -ltnp 'sport = :{config.CONSOLE_PORT}'). Stop it or set CONSOLE_PORT.", flush=True)
        raise SystemExit(1)
    print(f"Demo Console v{config.VERSION} on http://localhost:{config.CONSOLE_PORT}  "
          f"(sovd {config.SOVD_URL}, cda {config.CDA_URL} token={'ok' if BACKENDS.cda.token else 'none'}, "
          f"sim {config.SIM_URL}, auto DTC {'on' if config.AUTO_DTC else 'off'})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        AUTO.stop()


if __name__ == "__main__":
    main()
