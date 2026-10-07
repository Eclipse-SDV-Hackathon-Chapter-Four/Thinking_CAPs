# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Cruise diag stand-in for the S-CORE side: Zenoh input, monitors and a SOVD-style API on :7690.
"""Cruise diag stand-in: the S-CORE side of the demo until the real chain runs.

    virtual vehicle --Zenoh--> [ VehicleLink -> CruiseDiag ] --SOVD-style HTTP :7690--> console

It plays the part of cruise diag + the SOVD gateway with #16/#156 (a stand-in, not a
fake: the speed and the faults come from the real vehicle data). When the real gateway
runs, point the console's SOVD_URL at it and stop this process.

    python score_app.py                 # Zenoh as configured in config.py
    python score_app.py --no-zenoh      # no subscription (tests feed the link directly)

SOVD-style API (under /sovd):
  GET    /version-info
  GET    /v1/components
  GET    /v1/components/{cruise-control|cruise-diag}
  GET    /v1/components/{entity}/data                 list of data items
  GET    /v1/components/cruise-control/data/vehicle_speed
  GET    /v1/components/cruise-control/data/debounce
  GET    /v1/components/cruise-diag/data/link_status
  GET    /v1/components/{entity}/faults               #156 model
  DELETE /v1/components/{entity}/faults               clear (test reset)
"""
import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import config
import discover
from cruise_diag import CruiseDiag
from vehicle_link import VehicleLink


def settings_from_config():
    return {"f1_threshold": config.F1_THRESHOLD, "speed_min": config.SPEED_MIN_KMH, "speed_max": config.SPEED_MAX_KMH,
            "link_timeout_s": config.LINK_TIMEOUT_MS / 1000.0, "f1_code": config.F1_CODE, "f2_code": config.F2_CODE,
            "entity": config.SOVD_ENTITY, "diag_entity": config.SOVD_DIAG_ENTITY}


class ScoreApp:
    """Owns the link, the diagnostics, the monitor cycle and the stats writer."""

    def __init__(self, link=None, stats_file=None, clock=time.monotonic, wall=time.time):
        self.link = link or VehicleLink(config.SPEED_KEY, config.speed_factor(), config.ZENOH_CONNECT, clock, wall)
        self.diag = CruiseDiag(self.link, settings_from_config(), clock, wall)
        self.stats_file = stats_file if stats_file is not None else config.STATS_FILE
        self.requests = 0
        self._req_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

    def count_request(self):
        with self._req_lock:
            self.requests += 1

    def start(self, tick_s=None):
        tick_s = tick_s or config.DIAG_TICK_S

        def cycle():
            last_stats = 0.0
            while not self._stop.wait(tick_s):
                self.diag.tick()
                now = time.time()
                if now - last_stats >= 1.0:
                    last_stats = now
                    self.write_stats(now)
        self._thread = threading.Thread(target=cycle, name="cruise-diag-cycle", daemon=True)
        self._thread.start()

    def follow_vehicle(self, host, every_s=5.0, find=discover.find):
        """While no speed sample arrives, scout `host` again and reconnect when none of our
        endpoints is announced any more (a restarted vehicle listens on new random ports)."""
        def loop():
            while not self._stop.wait(every_s):
                if self.link.status(config.LINK_TIMEOUT_MS / 1000.0)["state"] == "live":
                    continue
                endpoints = find(host)
                if endpoints and not set(endpoints) & set(self.link.endpoints):
                    print(f"vehicle {host} now on {','.join(endpoints)} - reconnecting", flush=True)
                    self.link.reconnect(endpoints)
        threading.Thread(target=loop, name="vehicle-finder", daemon=True).start()

    def stop(self):
        self._stop.set()
        self.link.stop()

    def write_stats(self, now):
        if not self.stats_file:
            return
        try:
            tmp = self.stats_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"ts": now, "source": "cruise diag stand-in (Zenoh)",
                           "counters": {"vehicle_samples": self.link.samples, "sovd_requests": self.requests}}, f)
            os.replace(tmp, self.stats_file)
        except OSError:
            pass


def handler_for(app):
    entities = {config.SOVD_ENTITY: "Cruise control (surrogate for the vehicle)",
                config.SOVD_DIAG_ENTITY: "Cruise diag (vehicle computer)"}
    data_items = {config.SOVD_ENTITY: {config.SOVD_ITEM_SPEED: app.diag.speed_view,
                                       config.SOVD_ITEM_DEBOUNCE: app.diag.debounce_view},
                  config.SOVD_DIAG_ENTITY: {config.SOVD_ITEM_LINK: app.diag.link_view}}
    v1 = "/sovd/v1/"

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "CruiseDiagStandIn/" + config.VERSION

        def log_message(self, *args):
            pass

        def reply(self, obj, status=200):
            body = b"" if obj is None else json.dumps(obj).encode()
            self.send_response(status)
            if body:
                self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def error(self, status, code, message):
            self.reply({"error_code": code, "message": message}, status)

        def do_GET(self):
            self.route("GET")

        def do_DELETE(self):
            self.route("DELETE")

        def do_PUT(self):
            self.route("PUT")

        def do_POST(self):
            self.route("POST")

        def route(self, method):
            app.count_request()
            path = self.path.split("?")[0].rstrip("/")
            base = f"http://{self.headers.get('Host', 'localhost')}/sovd/v1"
            if path == "/sovd/version-info":
                return self.reply({"sovd_info": [{"version": "1.1.0", "base_uri": base, "vendor_info": {
                    "name": "cruise diag stand-in (Zenoh)", "version": config.VERSION}}]})
            if path == "/sovd/v1/components":
                return self.reply({"items": [{"id": e.split("/")[-1], "name": n, "href": f"{base}/{e}"}
                                             for e, n in entities.items()]})
            if not path.startswith(v1):
                return self.error(404, "resource-not-found", path)
            rest = path[len(v1):]
            entity = next((e for e in entities if rest == e or rest.startswith(e + "/")), None)
            if entity is None:
                return self.error(404, "resource-not-found", f"unknown entity in {path}")
            sub = rest[len(entity):].strip("/")
            if sub == "":
                return self.reply({"id": entity.split("/")[-1], "name": entities[entity],
                                   "data": f"{base}/{entity}/data", "faults": f"{base}/{entity}/faults"})
            if sub == "data" and method == "GET":
                return self.reply({"items": [{"id": k, "href": f"{base}/{entity}/data/{k}"} for k in data_items[entity]]})
            if sub.startswith("data/"):
                item = sub[len("data/"):]
                view = data_items[entity].get(item)
                if view is None:
                    return self.error(404, "resource-not-found", f"no data item {item}")
                if method != "GET":
                    return self.error(405, "method-not-allowed", "read-only data item")
                return self.reply({"id": item, "data": view()})
            if sub == "faults":
                if method == "GET":
                    return self.reply({"items": app.diag.faults_view(entity)})
                if method == "DELETE":
                    app.diag.clear_faults(entity)
                    return self.reply(None, 204)
                return self.error(405, "method-not-allowed", "faults: GET or DELETE")
            self.error(404, "resource-not-found", path)
    return H


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != "nt"   # no silent double bind on Windows


def serve(app, host, port):
    srv = Server((host, port), handler_for(app))
    threading.Thread(target=srv.serve_forever, name="sovd-standin-http", daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser(description="Cruise diag stand-in (Zenoh input, SOVD-style API)")
    ap.add_argument("--port", type=int, default=config.STANDIN_PORT)
    ap.add_argument("--no-zenoh", action="store_true", help="do not subscribe (for tests and offline use)")
    a = ap.parse_args()
    app = ScoreApp()
    connect, found = config.ZENOH_CONNECT, ""
    if not a.no_zenoh:
        if config.VEHICLE_HOST and not connect:
            connect = discover.find(config.VEHICLE_HOST)
            found = (f" (found on {config.VEHICLE_HOST} by scouting)" if connect
                     else f" (no Zenoh node answers on {config.VEHICLE_HOST} yet - scouting again every 5 s)")
            connect = connect or [f"tcp/{config.VEHICLE_HOST}:7447"]
        app.link.start(config.ZENOH_MODE, connect, config.ZENOH_LISTEN, config.ZENOH_MULTICAST_SCOUTING)
        if config.VEHICLE_HOST:
            app.follow_vehicle(config.VEHICLE_HOST)
    app.start()
    try:
        serve(app, config.STANDIN_HOST, a.port)
    except OSError as e:
        print(f"cannot listen on port {a.port}: {e.strerror or e}. Another program uses it "
              f"(see: ss -ltnp 'sport = :{a.port}'). Stop it or set STANDIN_PORT.", flush=True)
        app.stop()
        raise SystemExit(1)
    if app.link.error:
        state = f"NO VEHICLE INPUT - {app.link.error}"
    else:
        state = f"subscribed to '{config.SPEED_KEY}' via {config.ZENOH_MODE} {','.join(app.link.endpoints)}{found}"
    print(f"cruise diag stand-in v{config.VERSION} on :{a.port} - {state}", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        app.stop()


if __name__ == "__main__":
    main()
