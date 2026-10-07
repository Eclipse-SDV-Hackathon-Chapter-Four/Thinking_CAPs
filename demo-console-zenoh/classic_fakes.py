# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Offline stand-ins for the CDA and the ECU simulator, for tests and laptops without Docker.
"""Offline stand-ins for the classic path, for tests and laptops without Docker:

  :20002 CDA (token, components, faults in the CDA model)
  :8181  ECU simulator control API (DTC memory: create/update, delete one, delete all)

Both share one DTC memory. Contracts follow the upstream services; where the real service
differs, the real service wins. The S-CORE side is not faked any more in v2 (score_app.py
reads the real vehicle over Zenoh).

    python classic_fakes.py [--cda-port 20002] [--sim-port 8181]
"""
import argparse
import json
import os
import re
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BIT = {"test_failed": 0, "test_failed_this_operation_cycle": 1, "pending_dtc": 2, "confirmed_dtc": 3,
       "test_not_completed_since_last_clear": 4, "test_failed_since_last_clear": 5,
       "test_not_completed_this_operation_cycle": 6, "warning_indicator_requested": 7}


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


def sim_handler(memory, ecu, fault_memories):
    class H(JsonHandler):
        def handle_any(self, method):
            path = self.path.split("?")[0]
            parts = [p for p in path.split("/") if p]
            if path == "/" and method == "GET":
                return self.reply({"name": "fake ECU simulator", "ecus": [ecu]})
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


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != "nt"


def serve(port, handler, host="0.0.0.0"):
    srv = Server((host, port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser(description="Offline CDA + ECU simulator for the Demo Console")
    ap.add_argument("--cda-port", type=int, default=20002)
    ap.add_argument("--sim-port", type=int, default=8181)
    ap.add_argument("--ecu", default="FLXC1000")
    a = ap.parse_args()
    memory = DtcMemory()
    serve(a.cda_port, cda_handler(memory, a.ecu.lower(), set()))
    serve(a.sim_port, sim_handler(memory, a.ecu, ["Standard", "Development"]))
    print(f"classic fakes: CDA :{a.cda_port}  ECU simulator :{a.sim_port}", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
