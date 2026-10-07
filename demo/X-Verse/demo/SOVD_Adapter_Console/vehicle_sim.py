# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Test vehicle: publishes the speed over Zenoh like the virtual vehicle, with a control API to simulate faults.
"""Test vehicle: publishes the speed like the virtual vehicle does (a float32 as text on
`vehicle/status/velocity_status` over Zenoh), so the console can be tested without it.

    python vehicle_sim.py                       # listen on tcp/127.0.0.1:7447, 20 Hz, normal driving
    python vehicle_sim.py --mode invalid        # start with invalid values

Control API (test only, default http://127.0.0.1:7449), used by `runner.py --sim-url`:
    GET  /        current mode, rate, samples sent
    POST /mode    {"mode": "normal" | "stop" | "invalid" | "fixed", "value": 88.0}

It listens on the same port as the real vehicle: never run both at the same time.
"""
import argparse
import json
import math
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import config

MODES = ("normal", "stop", "invalid", "fixed")
INVALID_VALUES = ["nan", "-12.5", "999.9", "abc"]


class VehicleSim:
    def __init__(self, key=None, rate_hz=20.0, mode="normal", value=88.0):
        self.key = key or config.SPEED_KEY
        self.rate_hz, self.mode, self.value = rate_hz, mode, value
        self.sent = 0
        self.session = self.publisher = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._t0 = time.time()

    def open(self, listen=(), connect=(), mode="peer"):
        import zenoh
        zenoh.init_log_from_env_or("error")
        conf = zenoh.Config()
        conf.insert_json5("mode", json.dumps(mode))
        if listen:
            conf.insert_json5("listen/endpoints", json.dumps(list(listen)))
        if connect:
            conf.insert_json5("connect/endpoints", json.dumps(list(connect)))
        conf.insert_json5("scouting/multicast/enabled", "false")
        self.session = zenoh.open(conf)
        self.publisher = self.session.declare_publisher(self.key)

    def payload(self):
        """The next text to publish, or None when the vehicle is silent."""
        with self._lock:
            mode, value = self.mode, self.value
        if mode == "stop":
            return None
        if mode == "invalid":
            return INVALID_VALUES[self.sent % len(INVALID_VALUES)]
        if mode == "fixed":
            return f"{value:.1f}"
        t = time.time() - self._t0
        return f"{95 + 12 * math.sin(t / 7.0) + 1.5 * math.sin(t * 1.3):.1f}"

    def set_mode(self, mode, value=None):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        with self._lock:
            self.mode = mode
            if value is not None:
                self.value = float(value)

    def run(self):
        period = 1.0 / self.rate_hz
        nxt = time.perf_counter()
        while not self._stop.is_set():
            text = self.payload()
            if text is not None:
                self.publisher.put(text)
                self.sent += 1
            nxt += period
            self._stop.wait(max(0.0, nxt - time.perf_counter()))

    def start(self):
        threading.Thread(target=self.run, name="vehicle-sim", daemon=True).start()

    def stop(self):
        self._stop.set()
        try:
            if self.session is not None:
                self.session.close()
        except Exception:
            pass

    def status(self):
        with self._lock:
            return {"key": self.key, "mode": self.mode, "value": self.value, "rate_hz": self.rate_hz, "sent": self.sent}


def control_handler(sim):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def reply(self, obj, status=200):
            body = json.dumps(obj).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            self.reply(sim.status())

        def do_POST(self):
            if self.path.rstrip("/") != "/mode":
                return self.reply({"error": "not found"}, 404)
            n = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(n).decode() or "{}")
                sim.set_mode(body.get("mode"), body.get("value"))
            except (ValueError, AttributeError) as e:
                return self.reply({"error": str(e)}, 400)
            self.reply(sim.status())
    return H


def main():
    ap = argparse.ArgumentParser(description="Test vehicle publishing the speed over Zenoh")
    ap.add_argument("--listen", default=",".join(config.ZENOH_CONNECT), help="zenoh endpoints to listen on")
    ap.add_argument("--connect", default="", help="zenoh endpoints to connect to (e.g. a router)")
    ap.add_argument("--rate", type=float, default=20.0, help="messages per second")
    ap.add_argument("--mode", choices=MODES, default="normal")
    ap.add_argument("--value", type=float, default=88.0, help="speed for --mode fixed")
    ap.add_argument("--control-port", type=int, default=7449)
    a = ap.parse_args()
    sim = VehicleSim(rate_hz=a.rate, mode=a.mode, value=a.value)
    sim.open(listen=[e for e in a.listen.split(",") if e], connect=[e for e in a.connect.split(",") if e])
    sim.start()
    srv = ThreadingHTTPServer(("127.0.0.1", a.control_port), control_handler(sim))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"test vehicle: '{sim.key}' at {a.rate:g} Hz on {a.listen or a.connect}, mode {a.mode}; "
          f"control http://127.0.0.1:{a.control_port}/mode", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        sim.stop()


if __name__ == "__main__":
    main()
