# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: faithful stand-in of the opensovd-gateway of PR #40)
# Goal: Stand-in of the Rust opensovd-gateway (feature/16-sovd-adapter-dataprovider): same URLs, JSON, debounce and env variables.
"""Stand-in of the opensovd-gateway binary of PR #40 (inc_diagnostics, branch
feature/16-sovd-adapter-dataprovider, head d388985), for laptops where the Rust build is
not available. It is a contract double, not a different design:

  * the same HTTP surface as opensovd-core (pin 29e806f) mounted at SOVD_BASE:
      GET  /sovd/version-info
      GET  /sovd/v1/components                        -> [cruise]
      GET  /sovd/v1/components/cruise                 -> capabilities
      GET  /sovd/v1/components/cruise/data            -> the four data items (sovd_adapter #16)
      GET  /sovd/v1/components/cruise/data/{id}       -> {"id": id, "data": {...}}
      PUT  /sovd/v1/components/cruise/data/{id}       -> body {"data": {...}}, 204
      GET  /sovd/v1/components/cruise/data-categories, data-groups
  * the same four resources as score/opensovd-gateway/src/cruise.rs, with the same JSON
    bodies, the same simulated sensor (100 ± 5 km/h) and the same time-based debounce
    (Passed -> PreFailed -> Failed -> PrePassed), driven by the same environment variables
    CRUISE_DEBOUNCE_FAILED_MS, CRUISE_DEBOUNCE_PASSED_MS and SCORE_GATEWAY_ADDRESS;
  * the same error answers, including the one the review flagged as CR-04 (every
    resource error is reported as HTTP 500 "An internal error occurred").

When the Rust binary runs, point the console's SOVD_URL at it and do not start this.

    python score_app.py                 # http://127.0.0.1:7690/sovd
    SCORE_GATEWAY_ADDRESS=0.0.0.0:7690 CRUISE_DEBOUNCE_FAILED_MS=1500 python score_app.py
"""
import argparse
import json
import math
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import config

SOVD_VERSION = "1.1.0"
STAGES = ("passed", "prefailed", "failed", "prepassed")
CRUISE_STATES = ("standby", "active", "unavailable")


# ---------------------------------------------------------------- cruise.rs, ported line by line
class TimeBased:
    """score::mw::diag::dtc::Debounce::TimeBased: a monitor result must hold continuously
    for the given duration before the qualified status changes."""

    def __init__(self, failed_s, passed_s):
        self.failed_s, self.passed_s = float(failed_s), float(passed_s)


class Monitor:
    def __init__(self, debounce, now):
        self.debounce = debounce
        self.qualified_failed = False
        self.raw_failed = False
        self.raw_since = now

    def report(self, failed, now):
        self.settle(now)
        if failed != self.raw_failed:
            self.raw_failed = failed
            self.raw_since = now

    def settle(self, now):
        if self.raw_failed == self.qualified_failed:
            return
        needed = self.debounce.failed_s if self.raw_failed else self.debounce.passed_s
        # Rust compares exact Durations; float seconds need a tolerance (0.3 - 0.1 < 0.2 in binary).
        if now - self.raw_since >= needed - 1e-6:
            self.qualified_failed = self.raw_failed

    def stage(self, now):
        self.settle(now)
        return {(False, False): "passed", (False, True): "prefailed",
                (True, True): "failed", (True, False): "prepassed"}[(self.qualified_failed, self.raw_failed)]


class Sensor:
    """Simulated speed drifts around 100 km/h; a stuck sensor repeats one value."""

    def __init__(self, debounce, now):
        self.started = now
        self.stuck_at = None
        self.monitor = Monitor(debounce, now)
        self.state = "active"
        self.set_speed_kmh = 100.0

    def speed_kmh(self, now):
        if self.stuck_at is not None:
            return self.stuck_at
        t = now - self.started
        return round((100.0 + 5.0 * math.sin(t / 3.0)) * 10.0) / 10.0

    def refresh(self, now):
        """Report the fault condition, settle the debounce, derive cruise_state (called on every access)."""
        self.monitor.report(self.stuck_at is not None, now)
        stage = self.monitor.stage(now)
        if stage == "failed":
            self.state = "unavailable"
        elif stage == "passed" and self.state == "unavailable":
            self.state = "standby"


class DataNotFound(Exception):
    pass


class DataReadOnly(Exception):
    pass


class DataInternal(Exception):
    pass


class CruiseGateway:
    """The component `cruise` exactly as CruiseDiag::register() builds it: four DataResources
    behind one mutex, served through the DataProvider adapter."""

    COMPONENT_ID, COMPONENT_NAME = "cruise", "Cruise Control"

    def __init__(self, debounce=None, clock=time.monotonic):
        self.clock = clock
        self.sensor = Sensor(debounce or TimeBased(config.CRUISE_DEBOUNCE_FAILED_MS / 1000.0,
                                                    config.CRUISE_DEBOUNCE_PASSED_MS / 1000.0), clock())
        self.lock = threading.Lock()
        s = config.sovd_items()
        # registration order, name, category, read_only — as in cruise.rs
        self.items = [
            {"id": s["speed"], "name": "Vehicle speed", "category": "currentData", "read_only": True},
            {"id": s["state"], "name": "Cruise control state", "category": "currentData", "read_only": True},
            {"id": s["fault"], "name": "Vehicle speed sensor fault status", "category": "currentData", "read_only": True},
            {"id": s["switch"], "name": "Fault injection: vehicle speed sensor stuck", "category": "storedData", "read_only": False},
        ]
        self.groups = ["cruise"]
        self._readers = {s["speed"]: self._read_speed, s["state"]: self._read_state,
                         s["fault"]: self._read_fault, s["switch"]: self._read_switch}
        self._writers = {s["switch"]: self._write_switch}

    def _with(self, fn):
        with self.lock:
            now = self.clock()
            self.sensor.refresh(now)
            return fn(self.sensor, now)

    # resources (JSON bodies as in cruise.rs)
    def _read_speed(self):
        return self._with(lambda s, now: {"value": s.speed_kmh(now), "unit": "km/h"})

    def _read_state(self):
        return self._with(lambda s, now: {"state": s.state, "set_speed": s.set_speed_kmh})

    def _read_fault(self):
        def view(s, now):
            stage = s.monitor.stage(now)
            return {"fault": "VehicleSpeedSensorStuck", "status": stage,
                    "test_failed": s.monitor.raw_failed, "confirmed": stage == "failed"}
        return self._with(view)

    def _read_switch(self):
        return self._with(lambda s, now: {"stuck": s.stuck_at is not None})

    def _write_switch(self, value):
        stuck = value.get("stuck") if isinstance(value, dict) else None
        if not isinstance(stuck, bool):
            # cruise.rs answers GenericError IncompleteRequest; sovd_adapter maps every resource
            # error to DataError::Internal, which the server reports as HTTP 500 (review CR-04).
            raise DataInternal('expected a JSON body {"stuck": true|false}')

        def apply(s, now):
            s.stuck_at = s.speed_kmh(now) if stuck else None
            s.monitor.report(stuck, now)
        self._with(apply)

    # DataProvider surface (sovd_adapter/provider.rs)
    def metadata(self, item):
        return {"id": item["id"], "name": item["name"], "category": item["category"], "groups": list(self.groups)}

    def list(self, categories=None, groups=None, tags=None):
        out = []
        for it in self.items:
            if groups:                      # groups win over categories (routes/data.rs data_filter)
                if not set(groups) & set(self.groups):
                    continue
            elif categories and it["category"] not in categories:
                continue
            if tags:                        # the cruise items carry no tags
                continue
            out.append(self.metadata(it))
        return out

    def read(self, item_id):
        reader = self._readers.get(item_id)
        if reader is None:
            raise DataNotFound(item_id)
        return reader()

    def write(self, item_id, value):
        item = next((i for i in self.items if i["id"] == item_id), None)
        if item is None:
            raise DataNotFound(item_id)
        if item["read_only"]:
            raise DataReadOnly()
        self._writers[item_id](value)


# ---------------------------------------------------------------- opensovd-core server routes (pin 29e806f)
def handler_for(gateway, base=None):
    base = base if base is not None else config.SOVD_BASE
    v1 = base + "/v1"

    def error_json(code, message, vendor_code=None):
        out = {"error_code": code}
        if vendor_code:
            out["vendor_code"] = vendor_code
        out["message"] = message
        return out

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "opensovd-gateway-standin/" + config.VERSION

        def log_message(self, *args):
            pass

        def send(self, status, body=None, content_type="application/json"):
            data = b"" if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
            self.send_response(status)
            if data:
                self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if data:
                self.wfile.write(data)

        def text(self, status, message):          # axum rejections are text/plain
            self.send(status, message.encode(), "text/plain; charset=utf-8")

        def base_uri(self):
            return f"http://{self.headers.get('Host', 'localhost')}{base}"

        def do_GET(self):
            self.route("GET")

        def do_PUT(self):
            self.route("PUT")

        def do_POST(self):
            self.route("POST")

        def do_DELETE(self):
            self.route("DELETE")

        def route(self, method):
            url = urlsplit(self.path)
            path, query = url.path.rstrip("/") or "/", parse_qs(url.query)
            if path == base + "/version-info":
                if method != "GET":
                    return self.send(405)
                # vendor_info as the Rust binary answers it (opensovd-server default, checked with curl on d388985)
                out = {"sovd_info": [{"version": SOVD_VERSION, "base_uri": self.base_uri() + "/v1",
                                      "vendor_info": {"version": "0.1.1", "name": "OpenSOVD"}}]}
                if query.get("include-schema", [""])[0] == "true":
                    out["schema"] = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "VersionInfo", "type": "object"}
                return self.send(200, out)
            if not path.startswith(v1 + "/"):
                return self.send(404)
            parts = path[len(v1) + 1:].split("/")
            if parts == ["apps"] or parts == ["areas"]:          # the server has these collections; the gateway fills none
                return self.send(200, {"items": []}) if method == "GET" else self.send(405)
            if parts[0] != "components":
                return self.send(404)
            vb = self.base_uri() + "/v1"
            if len(parts) == 1:
                if method != "GET":
                    return self.send(405)
                return self.send(200, {"items": [{"id": gateway.COMPONENT_ID, "name": gateway.COMPONENT_NAME,
                                                  "href": f"{vb}/components/{gateway.COMPONENT_ID}"}]})
            cid = parts[1]
            if cid != gateway.COMPONENT_ID:
                return self.send(404, error_json("vendor-specific", f"Entity not found: {cid}", "entity-not-found"))
            sub = parts[2:]
            if not sub:
                if method != "GET":
                    return self.send(405)
                return self.send(200, {"id": cid, "name": gateway.COMPONENT_NAME,
                                       "hosts": f"{vb}/components/{cid}/hosts", "data": f"{vb}/components/{cid}/data"})
            if sub == ["data-categories"]:
                if method != "GET":
                    return self.send(405)
                seen = []
                for it in gateway.items:
                    if it["category"] not in seen:
                        seen.append(it["category"])
                return self.send(200, {"items": [{"item": c} for c in seen]})
            if sub == ["data-groups"]:
                if method != "GET":
                    return self.send(405)
                cat = query.get("category", [None])[0]
                items = [{"id": g, "category": it["category"]} for it in gateway.items for g in gateway.groups
                         if cat is None or it["category"] == cat]
                uniq, out = set(), []
                for g in items:
                    if g["id"] not in uniq:
                        uniq.add(g["id"])
                        out.append(g)
                return self.send(200, {"items": out})
            if sub == ["data"]:
                if method != "GET":
                    return self.send(405)
                split = lambda k: [x for v in query.get(k, []) for x in v.split(",") if x]  # noqa: E731
                out = {"items": gateway.list(split("categories"), split("groups"), split("tags"))}
                if query.get("include-schema", [""])[0] == "true":
                    out["schema"] = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "DataList", "type": "object"}
                return self.send(200, out)
            if len(sub) == 2 and sub[0] == "data":
                item_id = sub[1]
                try:
                    if method == "GET":
                        return self.send(200, {"id": item_id, "data": gateway.read(item_id)})
                    if method == "PUT":
                        body = self.write_body()
                        if body is None:
                            return            # rejection already sent
                        gateway.write(item_id, body)
                        return self.send(204)
                    return self.send(405)
                except DataNotFound as e:
                    return self.send(404, error_json("error-response", f"not found: {e}"))
                except DataReadOnly:
                    return self.send(400, error_json("error-response", "read only"))
                except DataInternal:
                    return self.send(500, error_json("error-response", "An internal error occurred"))
            self.send(404)

        def write_body(self):
            """axum Json<WriteRequest>: 415 without a JSON content type, 400 for invalid JSON,
            422 when the body is not a WriteRequest. Returns the `data` member."""
            ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n) if n else b""
            if ctype != "application/json":
                self.text(415, "Expected request with `Content-Type: application/json`")
                return None
            try:
                body = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError) as e:
                self.text(400, f"Failed to parse the request body as JSON: {e}")
                return None
            if not isinstance(body, dict) or "data" not in body:
                self.text(422, "Failed to deserialize the JSON body into the target type: missing field `data`")
                return None
            return body["data"]
    return H


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != "nt"   # no silent double bind on Windows


def serve(gateway, host, port, base=None):
    srv = Server((host, port), handler_for(gateway, base))
    threading.Thread(target=srv.serve_forever, name="sovd-standin-http", daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser(description="Stand-in of the opensovd-gateway binary (PR #40 contract)")
    ap.add_argument("--address", default=config.SCORE_GATEWAY_ADDRESS, help="host:port, like SCORE_GATEWAY_ADDRESS")
    a = ap.parse_args()
    host, _, port = a.address.rpartition(":")
    host, port = host or "127.0.0.1", int(port or "7690")
    gateway = CruiseGateway()
    try:
        serve(gateway, host, port)
    except OSError as e:
        print(f"cannot listen on {host}:{port}: {e.strerror or e}. Another program uses it "
              f"(see: ss -ltnp 'sport = :{port}'). Stop it or set SCORE_GATEWAY_ADDRESS.", flush=True)
        raise SystemExit(1)
    print(f"opensovd-gateway stand-in v{config.VERSION} on http://{host}:{port}{config.SOVD_BASE} - component "
          f"'{gateway.COMPONENT_ID}', debounce failed {config.CRUISE_DEBOUNCE_FAILED_MS} ms / passed "
          f"{config.CRUISE_DEBOUNCE_PASSED_MS} ms (PR #40 contract, head d388985)", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
