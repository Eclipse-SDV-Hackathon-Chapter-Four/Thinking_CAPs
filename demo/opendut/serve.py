#!/usr/bin/env python3
"""ThinkingCAPs dashboard for the CDA #543 before/after run through openDuT.

Serves dashboard/index.html and a small JSON API on 127.0.0.1 (stdlib only, no internet needed):

  GET  /api/live?since=N   events of the current or last run-both.sh run (runs/live/events.jsonl),
                           the console tail and whether a run is going on
  GET  /api/runs           recorded runs (runs/manual-*) that have a stock and a fix verdict
  GET  /api/run/<id>       verdicts + executor log of one recorded run, for the replay
  GET  /api/l1             unit test totals (L1) before and after, from runs/*-L1-*/summary.json
  POST /api/start          starts ../run-both.sh in the background (one run at a time)
  GET  /api/webdav         result ZIPs and MDD files on openDuT's WebDAV, with each ZIP's verdicts
  GET  /api/webdav/zip/<n> one result ZIP from WebDAV: verdicts, run.log, file list
  GET  /webdav/<path>      plain pass-through to WebDAV (folder listings, ZIP downloads)

WebDAV is reached the way the browser would, https://nginx-webdav.opendut.local through Traefik on
127.0.0.1:443 (checked against ../../opendut-ca.pem), so no /etc/hosts entry is needed.

  ./dashboard/serve.py [port]      default port 8090 -> http://127.0.0.1:8090
"""
import http.client
import io
import json
import re
import socket
import ssl
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from email.utils import parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUNS = ROOT / "runs"
LIVE = RUNS / "live"
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
STALE_AFTER = 400  # s without a new event: a run that never sent run_done counts as ended

WEBDAV_HOST = "nginx-webdav.opendut.local"
WEBDAV_ADDR = ("127.0.0.1", 443)
RESULTS_DIR = "/cda-543/results/"
MDD_DIR = "/cda-543/mdd/"
CA_FILE = ROOT.parent / "opendut-ca.pem"

proc = None  # run-both.sh started from the dashboard
zip_cache = {}  # (name, size) -> summary


class _WebDav(http.client.HTTPSConnection):
    """HTTPS to Traefik on localhost, with SNI and certificate check for the WebDAV host name."""

    def connect(self):
        sock = socket.create_connection(WEBDAV_ADDR, self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def webdav(method, path, headers=None):
    if CA_FILE.exists():
        ctx = ssl.create_default_context(cafile=str(CA_FILE))
        # openDuT's dev CA has no keyUsage extension, which Python >= 3.13 rejects in strict mode.
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    else:
        ctx = ssl._create_unverified_context()
    conn = _WebDav(WEBDAV_HOST, 443, context=ctx, timeout=8)
    try:
        conn.request(method, path, headers=headers or {})
        resp = conn.getresponse()
        return resp.status, resp.getheader("Content-Type", "application/octet-stream"), resp.read()
    finally:
        conn.close()


def webdav_list(path):
    status, _, body = webdav("PROPFIND", path, {"Depth": "1"})
    if status != 207:
        raise OSError(f"PROPFIND {path}: HTTP {status}")
    ns = {"D": "DAV:"}
    out = []
    for r in ET.fromstring(body).findall("D:response", ns):
        href = r.findtext("D:href", "", ns)
        if href.rstrip("/") == path.rstrip("/") or r.find(".//D:collection", ns) is not None:
            continue
        mod = r.findtext(".//D:getlastmodified", "", ns)
        out.append({
            "name": href.rsplit("/", 1)[-1],
            "size": int(r.findtext(".//D:getcontentlength", "0", ns) or 0),
            "modified": parsedate_to_datetime(mod).timestamp() if mod else 0,
        })
    return sorted(out, key=lambda f: f["name"], reverse=True)


def zip_details(name):
    status, _, body = webdav("GET", RESULTS_DIR + name)
    if status != 200:
        raise OSError(f"GET {name}: HTTP {status}")
    z = zipfile.ZipFile(io.BytesIO(body))
    files = [n for n in z.namelist() if not n.endswith("/")]
    read = lambda n: z.read(n).decode(errors="replace") if n in files else ""
    try:
        verdicts = json.loads(read("verdict.json") or "[]")
    except ValueError:
        verdicts = []
    log = read("run.log")
    m = re.search(r"variant (\w+)", log)
    code = read("exit-code").strip()
    return {
        "name": name, "files": files, "verdicts": verdicts if isinstance(verdicts, list) else [],
        "log": log, "variant": m.group(1) if m else None,
        "exit": int(code) if code.lstrip("-").isdigit() else None,
    }


def zip_summary(entry):
    key = (entry["name"], entry["size"])
    if key not in zip_cache:
        try:
            d = zip_details(entry["name"])
            zip_cache[key] = {
                "variant": d["variant"], "exit": d["exit"],
                "cases": [{"case": v.get("case"), "result": v.get("result")} for v in d["verdicts"]],
                "last": (d["log"].strip().splitlines() or [""])[-1],
            }
        except (OSError, zipfile.BadZipFile) as e:
            zip_cache[key] = {"variant": None, "exit": None, "cases": [], "last": f"unreadable: {e}"}
    return {**entry, **zip_cache[key]}


def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def live_events():
    events = []
    try:
        for line in (LIVE / "events.jsonl").read_text().splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
    except OSError:
        pass
    return events


def console_tail(lines=18):
    try:
        text = (LIVE / "console.log").read_text(errors="replace")
    except OSError:
        return []
    text = ANSI.sub("", text).replace("\r", "")
    return [l for l in text.splitlines() if l.strip()][-lines:]


def running(events):
    if proc is not None and proc.poll() is None:
        return True
    if not events or events[-1].get("type") in ("run_done", "error"):
        return False
    return time.time() - events[-1].get("t", 0) < STALE_AFTER


def variant(run_dir, v):
    d = run_dir / v
    verdicts = read_json(d / "verdict.json")
    if not isinstance(verdicts, list) or not verdicts:
        return None
    try:
        log = (d / "run.log").read_text(errors="replace")
    except OSError:
        log = ""
    try:
        code = int((d / "exit-code").read_text().strip())
    except (OSError, ValueError):
        code = None
    return {"verdicts": verdicts, "exit": code, "log": log}


def recorded_runs():
    out = []
    for d in sorted(RUNS.glob("manual-*"), reverse=True):
        if (d / "stock" / "verdict.json").exists() and (d / "fix" / "verdict.json").exists():
            out.append(d.name)
    return out


def l1_totals():
    def total(kind):
        dirs = sorted(RUNS.glob(f"*-L1-{kind}"))
        if not dirs:
            return None
        rows = read_json(dirs[-1] / "summary.json", [])
        return {
            "run": dirs[-1].name,
            "binaries": len(rows),
            "passed": sum(r.get("passed", 0) for r in rows),
            "failed": sum(r.get("failed", 0) for r in rows),
            "ignored": sum(r.get("ignored", 0) for r in rows),
        }
    return {"before": total("baseline"), "after": total("fix")}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path in ("/", "/index.html"):
            return self.send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/live":
            since = 0
            m = re.search(r"since=(\d+)", query)
            if m:
                since = int(m.group(1))
            events = live_events()
            return self.send(200, {
                "total": len(events),
                "events": events[since:] if since <= len(events) else events,
                "reset": since > len(events),
                "console": console_tail(),
                "running": running(events),
            })
        if path == "/api/runs":
            return self.send(200, recorded_runs())
        if path.startswith("/api/run/"):
            name = path.rsplit("/", 1)[-1]
            d = RUNS / name
            if not re.fullmatch(r"manual-[0-9TZ]+", name) or not d.is_dir():
                return self.send(404, {"error": "no such run"})
            return self.send(200, {"id": name, "stock": variant(d, "stock"), "fix": variant(d, "fix")})
        if path == "/api/l1":
            return self.send(200, l1_totals())
        if path == "/api/webdav":
            try:
                results = [zip_summary(f) for f in webdav_list(RESULTS_DIR) if f["name"].endswith(".zip")]
                mdd = webdav_list(MDD_DIR)
            except (OSError, ET.ParseError, ssl.SSLError) as e:
                return self.send(502, {"error": f"WebDAV not reachable: {e}"})
            return self.send(200, {"base": f"https://{WEBDAV_HOST}", "results_dir": RESULTS_DIR,
                                   "mdd_dir": MDD_DIR, "results": results, "mdd": mdd})
        if path.startswith("/api/webdav/zip/"):
            name = path.rsplit("/", 1)[-1]
            if not re.fullmatch(r"[\w.-]+\.zip", name):
                return self.send(404, {"error": "bad name"})
            try:
                return self.send(200, zip_details(name))
            except (OSError, zipfile.BadZipFile, ssl.SSLError) as e:
                return self.send(502, {"error": str(e)})
        if path.startswith("/webdav/"):
            dav_path = path[len("/webdav"):]
            if ".." in dav_path:
                return self.send(404, {"error": "bad path"})
            try:
                status, ctype, body = webdav("GET", dav_path)
            except (OSError, ssl.SSLError) as e:
                return self.send(502, {"error": f"WebDAV not reachable: {e}"})
            return self.send(status, body, ctype)
        static = HERE / path.lstrip("/")
        if re.fullmatch(r"/[\w.-]+\.html", path) and static.is_file():
            return self.send(200, static.read_bytes(), "text/html; charset=utf-8")
        self.send(404, {"error": "not found"})

    def do_POST(self):
        global proc
        if self.path != "/api/start":
            return self.send(404, {"error": "not found"})
        if running(live_events()):
            return self.send(409, {"error": "a run is already going on"})
        proc = subprocess.Popen(
            [str(ROOT / "run-both.sh")], cwd=ROOT,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self.send(202, {"started": True, "pid": proc.pid})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"ThinkingCAPs dashboard: http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
