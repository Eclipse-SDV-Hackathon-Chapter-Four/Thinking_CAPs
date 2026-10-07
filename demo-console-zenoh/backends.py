# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: SOVD client for the PR #40 contract)
# Goal: Clients for the SOVD gateway (PR #40 contract), the CDA and the ECU simulator, plus the traffic log, Docker status and DTC status decoder.
"""Clients for the three backends, the traffic log, Docker status and the DTC status
decoder. Shared by server.py, faults.py, auto_dtc.py and runner.py so they all talk to
the backends the same way (and every call lands in the traffic log).

SOVD side (opensovd-gateway of PR #40, opensovd-core routes at pin 29e806f):
    GET  {base}/version-info                                  -> {"sovd_info": [...]}
    GET  {base}/v1/components                                 -> {"items": [{"id","name","href"}]}
    GET  {base}/v1/components/{component}/data                -> {"items": [{"id","name","category","groups"?}]}
    GET  {base}/v1/components/{component}/data/{id}           -> {"id", "data": {...}}
    PUT  {base}/v1/components/{component}/data/{id}  {"data"} -> 204
    errors: {"error_code": "error-response", "message": ...} with 404 / 400 / 500
"""
import json
import subprocess
import threading
import time
import urllib.error
import urllib.request
from collections import deque

import config

# ---------------------------------------------------------------- status byte

# ISO 14229-1 DTC status byte, bit 0 first
BIT_NAMES = [
    ("testFailed", "test_failed"),
    ("testFailedThisOperationCycle", "test_failed_this_operation_cycle"),
    ("pendingDTC", "pending_dtc"),
    ("confirmedDTC", "confirmed_dtc"),
    ("testNotCompletedSinceLastClear", "test_not_completed_since_last_clear"),
    ("testFailedSinceLastClear", "test_failed_since_last_clear"),
    ("testNotCompletedThisOperationCycle", "test_not_completed_this_operation_cycle"),
    ("warningIndicatorRequested", "warning_indicator_requested"),
]
SHORT = {0: "failing", 1: "failed this cycle", 2: "pending", 3: "confirmed",
         4: "not completed since clear", 5: "failed since clear",
         6: "not completed this cycle", 7: "warning indicator"}


def decode_status(status):
    """Accepts an int, a hex string or a CDA-style object (named booleans + optional
    hex mask). Returns {raw, hex, bits[8], summary}."""
    raw = None
    if isinstance(status, bool):
        status = None
    if isinstance(status, int):
        raw = status & 0xFF
    elif isinstance(status, str):
        try:
            raw = int(status.replace("0x", "").replace("0X", ""), 16) & 0xFF
        except ValueError:
            raw = None
    elif isinstance(status, dict):
        mask = status.get("mask")
        if isinstance(mask, str):
            try:
                raw = int(mask.replace("0x", ""), 16) & 0xFF
            except ValueError:
                raw = None
        if raw is None:
            raw = 0
            for bit, (camel, snake) in enumerate(BIT_NAMES):
                if status.get(snake) or status.get(camel):
                    raw |= 1 << bit
    bits = [{"bit": bit, "name": camel, "set": bool(raw is not None and (raw >> bit) & 1)}
            for bit, (camel, _snake) in enumerate(BIT_NAMES)]
    words = [SHORT[b["bit"]] for b in bits if b["set"]]
    return {"raw": raw, "hex": None if raw is None else f"0x{raw:02X}",
            "bits": bits, "summary": ", ".join(words) if words else "no bits set"}


def bit_set(status, bit):
    d = decode_status(status)
    return d["raw"] is not None and bool((d["raw"] >> bit) & 1)


def norm_code(code):
    return str(code or "").strip().upper().lstrip("0") or "0"


def find_fault(items, code):
    for it in items or []:
        if norm_code(it.get("code")) == norm_code(code):
            return it
    return None


def active_fault(items, code):
    """The real CDA lists every DTC of the ECU database, inactive ones with status 00;
    a DTC counts as present only when its status is not 00."""
    f = find_fault(items, code)
    return f if f and decode_status(f.get("status"))["raw"] else None


# ---------------------------------------------------------------- traffic log

class TrafficLog:
    """Ring buffer of backend calls. The Authorization header is never stored."""

    def __init__(self, size=500):
        self.entries = deque(maxlen=size)
        self.seq = 0
        self.lock = threading.Lock()
        self.counts = {}

    def add(self, **entry):
        with self.lock:
            self.seq += 1
            entry["seq"] = self.seq
            entry["t"] = time.time()
            self.entries.append(entry)
            self.counts[entry.get("backend")] = self.counts.get(entry.get("backend"), 0) + 1

    def since(self, seq, limit=200):
        with self.lock:
            out = [e for e in self.entries if e["seq"] > seq]
        return out[-limit:]


# ---------------------------------------------------------------- HTTP client

class Response:
    __slots__ = ("status", "body", "content_type", "ms", "error")

    def __init__(self, status=0, body=b"", content_type="", ms=0.0, error=None):
        self.status, self.body, self.content_type, self.ms, self.error = status, body, content_type, ms, error

    @property
    def ok(self):
        return 200 <= self.status < 300

    def json(self):
        try:
            return json.loads(self.body.decode("utf-8") or "null")
        except (ValueError, UnicodeDecodeError):
            return None

    def problem(self):
        """One line for logs and views: transport error, SOVD error body or HTTP status."""
        if self.error:
            return self.error
        if self.ok:
            return None
        j = self.json()
        if isinstance(j, dict) and j.get("message"):
            return f"HTTP {self.status} {j.get('error_code', '')}: {j['message']}".replace("  ", " ")
        text = self.body[:120].decode("utf-8", "replace").strip()
        return f"HTTP {self.status}" + (f": {text}" if text else "")


class Backend:
    def __init__(self, name, base_url, log, timeout=None):
        self.name, self.base_url, self.log = name, base_url.rstrip("/"), log
        self.timeout = timeout or config.HTTP_TIMEOUT

    def auth_headers(self):
        return {}

    def request(self, method, path, body=None, headers=None, _retry=True, origin=None):
        url = self.base_url + path
        hdrs = {"Accept": "application/json"}
        hdrs.update(self.auth_headers())
        hdrs.update(headers or {})
        data = None
        if body is not None:
            data = body if isinstance(body, (bytes, bytearray)) else json.dumps(body).encode()
            hdrs.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                resp = Response(r.status, r.read(), r.headers.get("Content-Type", ""))
        except urllib.error.HTTPError as e:
            resp = Response(e.code, e.read() or b"", e.headers.get("Content-Type", ""))
        except Exception as e:  # URLError, timeout, connection refused
            resp = Response(0, b"", "", error=type(e).__name__ + ": " + str(getattr(e, "reason", e)))
        resp.ms = round((time.perf_counter() - t0) * 1000, 1)
        self.log.add(backend=self.name, method=method, path=path, status=resp.status, ms=resp.ms,
                     error=resp.error, origin=origin)
        if resp.status == 401 and _retry and self.on_unauthorized():
            return self.request(method, path, body, headers, _retry=False, origin=origin)
        return resp

    def on_unauthorized(self):
        return False

    def get_json(self, path, origin=None):
        r = self.request("GET", path, origin=origin)
        return r, (r.json() if r.ok else None)


class CdaBackend(Backend):
    """Holds the bearer token. It is fetched at start and again on a 401."""

    def __init__(self, log):
        super().__init__("cda", config.CDA_URL, log)
        self.token = config.CDA_TOKEN or None
        self.token_error = None
        self._lock = threading.Lock()

    def auth_headers(self):
        return {"Authorization": "Bearer " + self.token} if self.token else {}

    def fetch_token(self):
        with self._lock:
            body = {"client_id": config.CDA_CLIENT_ID, "client_secret": config.CDA_CLIENT_SECRET}
            req = urllib.request.Request(self.base_url + config.CDA_BASE + "/authorize",
                                         data=json.dumps(body).encode(), method="POST",
                                         headers={"Content-Type": "application/json"})
            t0 = time.perf_counter()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    data = json.loads(r.read().decode())
                self.token = data.get("access_token") or None
                self.token_error = None if self.token else "no access_token in answer"
                status = r.status
            except urllib.error.HTTPError as e:
                self.token, self.token_error, status = None, f"HTTP {e.code}", e.code
            except Exception as e:
                self.token, self.token_error, status = None, str(getattr(e, "reason", e)), 0
            self.log.add(backend="cda", method="POST", path=config.CDA_BASE + "/authorize", status=status,
                         ms=round((time.perf_counter() - t0) * 1000, 1), error=self.token_error, origin=None)
            return self.token is not None

    def on_unauthorized(self):
        return self.fetch_token()


# ---------------------------------------------------------------- facade

class Backends:
    """One object with everything the server, the fault model, the automation and the runner need."""

    def __init__(self, log=None):
        self.log = log or TrafficLog()
        self.sovd = Backend("sovd", config.SOVD_URL, self.log)
        self.cda = CdaBackend(self.log)
        self.sim = Backend("sim", config.SIM_URL, self.log)
        self._docker = (0.0, None)
        self._health = (0.0, None)
        self._lock = threading.Lock()

    # paths
    def sovd_component_path(self, component=None):
        return f"{config.SOVD_BASE}/v1/components/{component or config.SOVD_COMPONENT}"

    def sovd_data_path(self, item=None, component=None):
        p = self.sovd_component_path(component) + "/data"
        return p + (f"/{item}" if item else "")

    def cda_faults_path(self):
        return f"{config.CDA_BASE}/components/{config.CDA_ECU}/faults"

    def sim_dtc_path(self, code=None):
        return f"/{config.SIM_ECU}/dtc/{config.SIM_FAULT_MEMORY}" + (f"/{code}" if code else "")

    # SOVD gateway (PR #40 contract)
    def sovd_version(self, origin=None):
        """(response, {"version", "base_uri", "vendor_info"} of the first sovd_info entry or None)."""
        r, j = self.sovd.get_json(config.SOVD_BASE + "/version-info", origin)
        info = (j or {}).get("sovd_info") if isinstance(j, dict) else None
        return r, (info[0] if isinstance(info, list) and info and isinstance(info[0], dict) else None)

    def sovd_components(self, origin=None):
        r, j = self.sovd.get_json(f"{config.SOVD_BASE}/v1/components", origin)
        return r, ((j or {}).get("items") or []) if isinstance(j, dict) else []

    def sovd_data_list(self, component=None, origin=None):
        r, j = self.sovd.get_json(self.sovd_data_path(None, component), origin)
        return r, ((j or {}).get("items") or []) if isinstance(j, dict) else []

    def sovd_read(self, item, component=None, origin=None):
        """(response, the `data` member of the ReadResponse, or None)."""
        r, j = self.sovd.get_json(self.sovd_data_path(item, component), origin)
        return r, (j.get("data") if isinstance(j, dict) else None)

    def sovd_write(self, item, value, component=None, origin=None):
        """PUT {"data": value}; the gateway answers 204 on success."""
        return self.sovd.request("PUT", self.sovd_data_path(item, component), {"data": value}, origin=origin)

    # classic path
    def cda_faults(self, origin=None):
        r, j = self.cda.get_json(self.cda_faults_path(), origin)
        return r, (j or {}).get("items", []) if isinstance(j, dict) else []

    def sim_set(self, code, mask, origin=None):
        """Create or update one DTC in the simulator (a second PUT updates the mask)."""
        return self.sim.request("PUT", self.sim_dtc_path(), {"id": code, "statusMask": mask, "emissionsRelated": False},
                                origin=origin)

    def sim_delete(self, code, origin=None):
        return self.sim.request("DELETE", self.sim_dtc_path(code), origin=origin)

    def sim_clear(self, origin=None):
        return self.sim.request("DELETE", self.sim_dtc_path(), origin=origin)

    # health, cached for 1 s, the three pings in parallel
    def health(self):
        now = time.time()
        with self._lock:
            if self._health[1] and now - self._health[0] < 1.0:
                return self._health[1]
        result = {}

        def ping(name, backend, path):
            r = backend.request("GET", path)
            result[name] = {"up": r.ok, "status": r.status, "ms": r.ms, "error": r.error}
            if name == "sovd" and r.ok:
                j = r.json() or {}
                info = (j.get("sovd_info") or [{}])[0] if isinstance(j, dict) else {}
                result[name]["sovd_version"] = info.get("version") if isinstance(info, dict) else None
                result[name]["base_uri"] = info.get("base_uri") if isinstance(info, dict) else None

        jobs = [("sovd", self.sovd, config.SOVD_BASE + "/version-info"),
                ("cda", self.cda, config.CDA_BASE + "/components"),
                ("sim", self.sim, "/")]
        threads = [threading.Thread(target=ping, args=j, daemon=True) for j in jobs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        result["cda"]["token"] = bool(self.cda.token)
        result["cda"]["token_error"] = self.cda.token_error
        with self._lock:
            self._health = (time.time(), result)
        return result

    # docker ps, cached for 5 s
    def docker(self):
        now = time.time()
        with self._lock:
            if self._docker[1] and now - self._docker[0] < 5.0:
                return self._docker[1]
        out = {"available": False, "containers": [], "expected": config.DOCKER_CONTAINERS, "error": None}
        try:
            p = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.State}}\t{{.Status}}"],
                               capture_output=True, text=True, timeout=4)
            if p.returncode == 0:
                out["available"] = True
                for line in p.stdout.splitlines():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        out["containers"].append({"name": parts[0], "state": parts[1],
                                                  "status": parts[2] if len(parts) > 2 else ""})
            else:
                out["error"] = (p.stderr or "docker ps failed").strip()[:200]
        except Exception as e:
            out["error"] = f"{type(e).__name__}: {e}"[:200]
        running = {c["name"] for c in out["containers"] if c["state"] == "running"}
        out["expected_running"] = {name: any(name in r for r in running) for name in config.DOCKER_CONTAINERS}
        with self._lock:
            self._docker = (time.time(), out)
        return out
