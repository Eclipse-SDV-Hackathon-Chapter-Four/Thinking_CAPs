"""Development stand-ins for the three backends, so the console can be built
and rehearsed before the real services run:

  :7690  S-CORE app behind an SOVD gateway (speed, sensor_freeze, debounce,
         faults in the #156 model) and the stats.json writer
  :20002 CDA (token, components, faults in the CDA model)
  :8181  ECU simulator control API (DTC memory, reset)

The CDA and simulator fakes share one DTC memory. Contract details follow the
upstream code as read on 28 Sep 2026; where the real service differs, the
real service wins and this file is corrected.

    python fakes.py [--sovd-port 7690] [--cda-port 20002] [--sim-port 8181] [--stats stats.json]
"""
import argparse
import json
import math
import os
import re
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BIT = {"test_failed": 0, "test_failed_this_operation_cycle": 1, "pending_dtc": 2, "confirmed_dtc": 3,
       "test_not_completed_since_last_clear": 4, "test_failed_since_last_clear": 5,
       "test_not_completed_this_operation_cycle": 6, "warning_indicator_requested": 7}


# ------------------------------------------------------------------ shared state

class ScoreApp:
    """A cruise control app with a speed input, a freeze switch and a
    counter-based debounce. Ticks every 100 ms."""

    PERIOD = 0.1
    THRESHOLD = 5

    def __init__(self, stats_file):
        self.lock = threading.Lock()
        self.stats_file = stats_file
        self.frozen = False
        self.speed = 90.0
        self.ts = time.time()
        self.counter = 0
        self.state = "PASSED"
        self.status = 0x00           # DTC status byte of the one fault
        self.samples = 0             # counters for stats.json
        self.requests = 0
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        t0 = time.time()
        last_stats = 0
        while True:
            time.sleep(self.PERIOD)
            now = time.time()
            with self.lock:
                if not self.frozen:
                    self.speed = round(90 + 8 * math.sin((now - t0) / 6.0) + 1.5 * math.sin((now - t0) * 1.7), 1)
                    self.ts = now
                    self.samples += 1
                # debounce: frozen input = failing sample
                if self.frozen:
                    self.counter = min(self.counter + 1, self.THRESHOLD)
                else:
                    self.counter = max(self.counter - 1, 0)
                if self.counter >= self.THRESHOLD:
                    self.state = "FAILED"
                    self.status |= 0x0D                     # testFailed, pendingDTC, confirmedDTC
                elif self.counter > 0:
                    self.state = "PREFAILED" if self.frozen else "PREPASSED"
                    if not self.frozen:
                        self.status &= ~0x01                # no longer failing; history kept
                else:
                    self.state = "PASSED"
                    self.status &= ~0x01
                if now - last_stats >= 1.0:
                    last_stats = now
                    self._write_stats(now)

    def _write_stats(self, now):
        try:
            tmp = self.stats_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"ts": now, "source": "fake S-CORE app",
                           "counters": {"sensor_samples": self.samples, "sovd_requests": self.requests}}, f)
            os.replace(tmp, self.stats_file)
        except OSError:
            pass


class DtcMemory:
    def __init__(self):
        self.lock = threading.Lock()
        self.dtcs = {}  # id (int) -> {"mask": int, "emissions": bool}

    @staticmethod
    def parse_id(text):
        s = str(text or "").strip()
        if re.fullmatch(r"[0-9a-fA-F]{6}", s):
            return int(s, 16)
        if re.fullmatch(r"[bBcCpPuU][0-9a-fA-F]{6}", s):
            return int(s[1:], 16)
        return None


# ------------------------------------------------------------------ helpers

class JsonHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def body_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        try:
            return json.loads(raw.decode() or "null")
        except ValueError:
            return None

    def reply(self, obj, status=200):
        body = b"" if obj is None else json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        self.handle_any("GET")

    def do_PUT(self):
        self.handle_any("PUT")

    def do_POST(self):
        self.handle_any("POST")

    def do_DELETE(self):
        self.handle_any("DELETE")


# ------------------------------------------------------------------ fake S-CORE app (SOVD)

def score_handler(app, entity):
    base = f"/sovd/v1/{entity}"

    class H(JsonHandler):
        def handle_any(self, method):
            path = self.path.split("?")[0]
            with app.lock:
                app.requests += 1
            if path == "/sovd/version-info":
                return self.reply({"sovd_version": "1.1.0", "base_uri": "http://localhost:7690/sovd",
                                   "vendor_info": {"name": "fake S-CORE app"}})
            if path == "/sovd/v1/components":
                return self.reply({"items": [{"id": entity.split("/")[-1], "name": "Cruise control (fake)"}]})
            if path == base + "/data/vehicle_speed" and method == "GET":
                with app.lock:
                    return self.reply({"id": "vehicle_speed", "data": {"value": app.speed, "unit": "km/h", "ts": app.ts}})
            if path == base + "/data/debounce" and method == "GET":
                with app.lock:
                    return self.reply({"id": "debounce", "data": {"state": app.state, "counter": app.counter,
                                                                 "threshold": app.THRESHOLD, "frozen": app.frozen}})
            if path == base + "/data/sensor_freeze":
                if method == "PUT":
                    body = self.body_json()
                    value = body.get("data") if isinstance(body, dict) else None
                    if not isinstance(value, bool):
                        return self.reply({"error_code": "invalid-parameter", "message": "data must be a boolean"}, 400)
                    with app.lock:
                        app.frozen = value
                    return self.reply(None, 204)
                with app.lock:
                    return self.reply({"id": "sensor_freeze", "data": app.frozen})
            if path == base + "/faults" and method == "GET":
                with app.lock:
                    return self.reply({"items": [{"code": "P0500", "display": "Vehicle speed sensor: input frozen",
                                                  "status": app.status, "severity": 2}]})
            self.reply({"error_code": "resource-not-found", "message": path}, 404)
    return H


# ------------------------------------------------------------------ fake CDA

def cda_handler(memory, ecu, tokens):
    base = "/vehicle/v15"

    class H(JsonHandler):
        def handle_any(self, method):
            path = self.path.split("?")[0]
            if path == base + "/authorize" and method == "POST":
                body = self.body_json() or {}
                if not body.get("client_id") or not body.get("client_secret"):
                    return self.reply({"error": "client_id and client_secret required"}, 400)
                tok = secrets.token_urlsafe(24)
                tokens.add(tok)
                return self.reply({"access_token": tok, "token_type": "Bearer", "expires_in": 3600})
            auth = self.headers.get("Authorization", "")
            if not (auth.startswith("Bearer ") and auth[7:] in tokens):
                return self.reply({"error": "unauthorized"}, 401)
            if path == base + "/components" and method == "GET":
                return self.reply({"items": [{"id": ecu, "name": ecu.upper()}]})
            if path == f"{base}/components/{ecu}/faults" and method == "GET":
                items = []
                with memory.lock:
                    for did, d in sorted(memory.dtcs.items()):
                        st = {name: bool((d["mask"] >> bit) & 1) for name, bit in BIT.items()}
                        st["mask"] = f"{d['mask']:02X}"
                        items.append({"code": f"{did:06X}", "fault_name": f"DTC {did:06X} (fake)",
                                      "severity": 0, "status": st})
                return self.reply({"items": items})
            self.reply({"error_code": "resource-not-found", "message": path}, 404)
    return H


# ------------------------------------------------------------------ fake ECU simulator

def sim_handler(memory, ecu, fault_memories):
    class H(JsonHandler):
        def handle_any(self, method):
            path = self.path.split("?")[0]
            parts = [p for p in path.split("/") if p]
            if path == "/" and method == "GET":
                return self.reply({"name": "fake ECU simulator", "ecus": [ecu]})
            if path == "/reset" and method == "POST":
                with memory.lock:
                    memory.dtcs.clear()
                return self.reply(None, 204)
            if len(parts) >= 2 and parts[0] == ecu and parts[1] == "dtc":
                if len(parts) == 2 and method == "GET":
                    return self.reply({"items": [{"name": m} for m in fault_memories]})
                if len(parts) >= 3 and parts[2] not in fault_memories:
                    return self.reply({"message": "unknown fault memory"}, 404)
                if len(parts) == 3 and method == "GET":
                    with memory.lock:
                        return self.reply([{"id": f"{did:06X}", "statusMask": f"{d['mask']:02X}",
                                            "emissionsRelated": d["emissions"]} for did, d in sorted(memory.dtcs.items())])
                if len(parts) == 3 and method == "PUT":
                    body = self.body_json() or {}
                    did = memory.parse_id(body.get("id"))
                    if did is None:
                        return self.reply({"message": "Not a valid dtc number"}, 400)
                    mask = body.get("statusMask")
                    try:
                        mask = int(str(mask), 16) & 0xFF if mask is not None else 0x09
                    except ValueError:
                        return self.reply({"message": "invalid statusMask"}, 400)
                    with memory.lock:
                        memory.dtcs[did] = {"mask": mask, "emissions": bool(body.get("emissionsRelated"))}
                    return self.reply({"message": "DTC was created"}, 201)
                if len(parts) == 3 and method == "DELETE":
                    with memory.lock:
                        memory.dtcs.clear()
                    return self.reply({"message": "DTCs were deleted"})
                if len(parts) == 4 and method == "DELETE":
                    did = memory.parse_id(parts[3])
                    with memory.lock:
                        memory.dtcs.pop(did, None)
                    return self.reply({"message": "DTCs were deleted"})
            self.reply({"message": "not found"}, 404)
    return H


# ------------------------------------------------------------------ main

class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != "nt"  # see server.py: no silent double bind on Windows


def serve(port, handler):
    srv = Server(("0.0.0.0", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser(description="Fake backends for the Demo Console")
    ap.add_argument("--sovd-port", type=int, default=7690)
    ap.add_argument("--cda-port", type=int, default=20002)
    ap.add_argument("--sim-port", type=int, default=8181)
    ap.add_argument("--entity", default="components/cruise-control")
    ap.add_argument("--ecu", default="FLXC1000")
    ap.add_argument("--stats", default="stats.json")
    a = ap.parse_args()
    app = ScoreApp(a.stats)
    memory = DtcMemory()
    serve(a.sovd_port, score_handler(app, a.entity))
    serve(a.cda_port, cda_handler(memory, a.ecu.lower(), set()))
    serve(a.sim_port, sim_handler(memory, a.ecu, ["Standard", "Development"]))
    print(f"fakes: S-CORE app :{a.sovd_port}  CDA :{a.cda_port}  ECU simulator :{a.sim_port}  stats -> {a.stats}", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
