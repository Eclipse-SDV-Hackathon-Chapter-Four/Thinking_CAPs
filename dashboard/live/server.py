#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Live demo console: serves dashboard/live/index.html and forwards its calls to the
running services, so the browser needs no CORS and the CDA token stays here.

    /api/gw/<path>    -> OpenSOVD gateway   http://127.0.0.1:7690/sovd/v1/<path>
    /api/cda/<path>   -> CDA SOVD API       http://127.0.0.1:20002/vehicle/v15/<path>  (bearer token added)
    /api/sim/<path>   -> ECU simulator      http://127.0.0.1:8181/<path>
    /api/health       -> reachability of all three
    /api/topology     -> live state of the whole architecture: SOVD gateway, the S-CORE
                         containers (processes), cruise_bridge and cruise ECU counters
    /api/run          -> POST starts dashboard/run-demo.sh, GET returns its output

Every forwarded call except the page's background polls is printed to stdout,
so a terminal next to the browser shows the real traffic.

    dashboard/live/server.py            # http://127.0.0.1:8080
    LIVE_PORT=9000 dashboard/live/server.py
"""

import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GATEWAY = os.environ.get("GATEWAY", "http://127.0.0.1:7690/sovd/v1")
CDA = os.environ.get("CDA", "http://127.0.0.1:20002/vehicle/v15")
SIM = os.environ.get("SIM", "http://127.0.0.1:8181")
UPSTREAMS = {"gw": GATEWAY, "cda": CDA, "sim": SIM}
HEALTH = {
    "gateway": GATEWAY + "/components",
    "cda": CDA.split("/vehicle/")[0] + "/health/ready",
    "sim": SIM + "/",
}

_token = {"value": None}
_token_lock = threading.Lock()
_run = {"proc": None, "lines": [], "exit": None, "started": None}
_run_lock = threading.Lock()
SCORE_RUN = ROOT / "dashboard" / "score" / "run"
_counts = {"gw": 0, "cda": 0, "sim": 0}  # forwarded calls per upstream, polls included
_topo = {"at": 0.0, "value": None}
_topo_lock = threading.Lock()


def read_stats(name):
    """A stats file the S-CORE nodes rewrite every 500 ms, with its age."""
    path = SCORE_RUN / name
    try:
        age = time.time() - path.stat().st_mtime
        return {**json.loads(path.read_text()), "file_age_s": round(age, 1)}
    except (OSError, ValueError):
        return None


def container_procs(name):
    """Process names in a container, or None if it is not running."""
    try:
        out = subprocess.run(["docker", "top", name, "-eo", "pid,comm"], capture_output=True, text=True, timeout=3)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return sorted({line.split(None, 1)[1].strip() for line in out.stdout.splitlines()[1:] if len(line.split()) > 1})


def topology():
    with _topo_lock:
        if _topo["value"] is not None and time.time() - _topo["at"] < 0.8:
            return _topo["value"]
        status, data, _, _ = call("GET", GATEWAY + "/components", timeout=2)
        try:
            components = [c["id"] for c in json.loads(data).get("items", [])] if status == 200 else []
        except ValueError:
            components = []
        value = {
            "at": time.time(),
            "gateway": {"status": status, "components": components},
            "counts": dict(_counts),
            "vehicle": {"procs": container_procs("sdv-vehicle")},
            "ecu_node": {"procs": container_procs("sdv-cruise-ecu")},
            "bridge": read_stats("bridge.json"),
            "ecu": read_stats("cruise_ecu.json"),
            "cda": call("GET", HEALTH["cda"], timeout=2)[0],
            "sim": call("GET", HEALTH["sim"], timeout=2)[0],
        }
        _topo.update(at=time.time(), value=value)
        return value


def call(method, url, body=None, headers=None, timeout=5):
    """One upstream request -> (status, body bytes, content type, elapsed ms)."""
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, data, ctype = r.status, r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        status, data, ctype = e.code, e.read(), e.headers.get("Content-Type", "")
    except (urllib.error.URLError, OSError) as e:
        status, data, ctype = 502, json.dumps({"error": f"{url} unreachable: {e}"}).encode(), "application/json"
    return status, data, ctype, (time.perf_counter() - t0) * 1000


def cda_token(refresh=False):
    with _token_lock:
        if refresh or not _token["value"]:
            body = json.dumps({"client_id": "test", "client_secret": "secret"}).encode()
            status, data, _, _ = call("POST", CDA + "/authorize", body, {"Content-Type": "application/json"})
            _token["value"] = json.loads(data).get("access_token") if status == 200 else None
        return _token["value"]


def pump(proc):
    for line in proc.stdout:
        with _run_lock:
            _run["lines"].append(line.rstrip("\n"))
    proc.wait()
    with _run_lock:
        _run["exit"] = proc.returncode


class Handler(BaseHTTPRequestHandler):
    server_version = "sovd-live"

    def log_message(self, *args):  # our own log lines only
        pass

    def reply(self, status, data=b"", ctype="application/json", extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if data:
            self.wfile.write(data)

    def reply_json(self, obj, status=200):
        self.reply(status, json.dumps(obj).encode())

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else None

    def route(self, method):
        path = self.path.split("?")[0]
        if method == "GET" and path in ("/", "/index.html"):
            return self.reply(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/health":
            return self.reply_json({k: call("GET", u, timeout=2)[0] for k, u in HEALTH.items()})
        if path == "/api/run":
            return self.run_demo(method)
        if path == "/api/topology":
            return self.reply_json(topology())
        parts = path.split("/", 3)  # ['', 'api', 'gw', 'rest']
        if len(parts) >= 3 and parts[1] == "api" and parts[2] in UPSTREAMS:
            return self.forward(method, parts[2], parts[3] if len(parts) > 3 else "")
        self.reply_json({"error": f"no route for {method} {path}"}, 404)

    def forward(self, method, target, rest):
        url = UPSTREAMS[target].rstrip("/") + "/" + rest
        _counts[target] += 1
        body = self.body()
        headers = {"Content-Type": "application/json"} if body else {}
        if target == "cda":
            headers["Authorization"] = f"Bearer {cda_token()}"
        status, data, ctype, ms = call(method, url, body, headers)
        if target == "cda" and status == 401:
            headers["Authorization"] = f"Bearer {cda_token(refresh=True)}"
            status, data, ctype, ms = call(method, url, body, headers)
        if not self.headers.get("X-Poll"):
            sent = f"  {body.decode()}" if body else ""
            print(f"[{time.strftime('%H:%M:%S')}] {method:6} {url}{sent}  ->  {status}  ({ms:.0f} ms)", flush=True)
        self.reply(status, data, ctype, {"X-Upstream": f"{method} {url}", "X-Elapsed-Ms": f"{ms:.1f}"})

    def run_demo(self, method):
        with _run_lock:
            running = _run["proc"] is not None and _run["exit"] is None
            if method == "POST" and not running:
                print(f"[{time.strftime('%H:%M:%S')}] starting dashboard/run-demo.sh", flush=True)
                proc = subprocess.Popen([str(ROOT / "dashboard" / "run-demo.sh")], cwd=ROOT, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                _run.update(proc=proc, lines=[], exit=None, started=time.time())
                threading.Thread(target=pump, args=(proc,), daemon=True).start()
                running = True
            return self.reply_json({"running": running, "exit": _run["exit"], "lines": _run["lines"]})

    def do_GET(self):
        self.route("GET")

    def do_PUT(self):
        self.route("PUT")

    def do_POST(self):
        self.route("POST")

    def do_DELETE(self):
        self.route("DELETE")


def main():
    host = os.environ.get("LIVE_HOST", "127.0.0.1")
    port = int(os.environ.get("LIVE_PORT", "8080"))
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"live demo console: http://{host}:{port}/", flush=True)
    for name, url in HEALTH.items():
        print(f"  {name:8} {url}  ->  {call('GET', url, timeout=2)[0]}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
