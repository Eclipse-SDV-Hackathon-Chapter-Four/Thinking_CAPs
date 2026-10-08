#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test cases ITC-01..ITC-16 against the running X-Verse system.

Read-only towards the vehicle: it subscribes, queries and inspects. The only write is the
SOVD Adapter Console's classic round trip (ITC-15), which sets and deletes one test DTC
in the ECU simulator. A case whose element is not present (ThreadX without the AZ3166
board) reports NOT RUN.
Run while `run_autoverse.py --enable-camera-display --vcu-zenoh` is up:

    python3 aspice/tools/e2e_check.py [--out results.json]

Exits non-zero when a test case fails. See swe5-integration-test/integration-test.md.
"""
import argparse
import json
import socket
import ssl
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OTA = ROOT / "vecu" / "ota"
CERTS = OTA / "data" / "certs"
ZENOH = "tcp/127.0.0.1:7447"
SOVD = "http://127.0.0.1:7691/sovd/v1"
OPERATOR = "https://127.0.0.1:9444"
DEVICE = ("127.0.0.1", 9443)
CONTAINERS = ["bridge-e2e", "docker_setup-adas_score-1", "ota-backend", "ota-rtcu",
              "cuttlefish-orchestration-cont", "opensovd-gateway", "sovd-adapter-console",
              "testcontainer-cda-1", "testcontainer-ecu-sim-1"]
GATEWAY = "http://127.0.0.1:7690/sovd/v1"
THREADX = ROOT / "external_hackathon_ecus" / "ThreadX"
TARGETS = ["PC-CUTTLEFISH-01", "PI-ANDROID-15"]

results = []


def case(case_id, title):
    def wrap(fn):
        def run():
            started = time.time()
            try:
                ok, detail = fn()
            except Exception as exc:  # a crashing check is a failed check
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            status = "NOT RUN" if ok is None else "PASS" if ok else "FAIL"
            results.append({"id": case_id, "title": title, "status": status,
                            "detail": detail, "duration_s": round(time.time() - started, 2)})
            print(f"{case_id} {status}  {title}  — {detail}")
        return run
    return wrap


def get_json(url, insecure=False):
    ctx = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(url, timeout=5, context=ctx) as resp:
        return json.load(resp)


def zenoh_keys(keys, seconds=3.0):
    import zenoh
    conf = zenoh.Config()
    conf.insert_json5("mode", '"client"')
    conf.insert_json5("connect/endpoints", json.dumps([ZENOH]))
    seen = {}
    session = zenoh.open(conf)
    try:
        subs = [session.declare_subscriber(k, lambda s: seen.setdefault(str(s.key_expr), s.payload.to_string()))
                for k in keys]
        deadline = time.time() + seconds
        while time.time() < deadline and len(seen) < len(keys):
            time.sleep(0.05)
        del subs
    finally:
        session.close()
    return seen


@case("ITC-01", "Zenoh router reachable")
def itc01():
    with socket.create_connection(("127.0.0.1", 7447), timeout=2):
        return True, "tcp/127.0.0.1:7447 accepts connections"


@case("ITC-02", "Supervised containers running")
def itc02():
    states = {}
    for name in CONTAINERS:
        r = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", name], capture_output=True, text=True)
        states[name] = r.stdout.strip() == "true"
    down = [n for n, up in states.items() if not up]
    return not down, "all running" if not down else f"not running: {', '.join(down)}"


@case("ITC-03", "Vehicle state and driver requests on Zenoh")
def itc03():
    keys = ["vehicle/status/velocity_status", "vehicle/status/clock_status", "vehicle/command/brake_pedal_sts"]
    seen = zenoh_keys(keys)
    missing = [k for k in keys if k not in seen]
    return not missing, f"received {len(seen)}/{len(keys)}" + (f", missing {missing}" if missing else "")


@case("ITC-04", "VCU commands on Zenoh")
def itc04():
    keys = ["vcu/control/throttle_cmd", "vcu/control/brake_cmd"]
    seen = zenoh_keys(keys)
    missing = [k for k in keys if k not in seen]
    return not missing, f"received {len(seen)}/{len(keys)}" + (f", missing {missing}" if missing else "")


@case("ITC-05", "Speed reaches the S-CORE ECU over SOME/IP")
def itc05():
    data = get_json(f"{SOVD}/components/cruise_control/data/vehicle_speed")["data"]
    return data["age_ms"] < 1000, f"vehicle_speed {data['value']} {data['unit']}, age {data['age_ms']} ms"


@case("ITC-06", "Cruise-control state exposed")
def itc06():
    data = get_json(f"{SOVD}/components/cruise_control/data/cruise_state")["data"]
    ok = bool(data.get("state")) and str(data.get("software_identity", "")).startswith("sha256:")
    return ok, f"state {data.get('state')}, identity {str(data.get('software_identity'))[:19]}…"


@case("ITC-07", "DTC served through PR #16 sovd_adapter")
def itc07():
    comps = [c["id"] for c in get_json(f"{SOVD}/components")["items"]]
    items = [d["id"] for d in get_json(f"{SOVD}/components/cruise_control/data")["items"]]
    dtc = get_json(f"{SOVD}/components/cruise_control/data/cc_lost_communication")["data"]
    ok = "cruise_control" in comps and "cc_lost_communication" in items and dtc["status"] == "passed"
    return ok, f"components {comps}, DTC {dtc['fault']} status {dtc['status']}"


@case("ITC-08", "certgen PKI")
def itc08():
    ca = CERTS / "ca.crt"
    checked = []
    for name in ["server"] + [f"client-{t}" for t in TARGETS]:
        crt = CERTS / f"{name}.crt"
        verify = subprocess.run(["openssl", "verify", "-CAfile", str(ca), str(crt)], capture_output=True, text=True)
        if verify.returncode:
            return False, f"{crt.name} does not verify: {verify.stdout.strip()} {verify.stderr.strip()}"
        if name.startswith("client-"):
            subject = subprocess.run(["openssl", "x509", "-in", str(crt), "-noout", "-subject"],
                                     capture_output=True, text=True).stdout
            if f"CN = {name[7:]}" not in subject and f"CN={name[7:]}" not in subject:
                return False, f"{crt.name}: unexpected subject {subject.strip()}"
        checked.append(crt.name)
    return True, f"verified against ca.crt: {', '.join(checked)}"


@case("ITC-09", "Device API requires mutual TLS")
def itc09():
    def handshake(cert=None):
        ctx = ssl._create_unverified_context()
        if cert:
            ctx.load_cert_chain(CERTS / f"{cert}.crt", CERTS / f"{cert}.key")
        with socket.create_connection(DEVICE, timeout=5) as raw, ctx.wrap_socket(raw) as tls:
            tls.sendall(b"GET /api/v1/manifest HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            return tls.recv(64).split(b"\r\n")[0].decode()
    # TLS 1.3 enforces the client certificate after the handshake: the server
    # closes the connection without an HTTP response (or with an alert).
    try:
        rejected = not handshake().startswith("HTTP/")
    except (ssl.SSLError, ConnectionError, OSError):
        rejected = True
    status = handshake(f"client-{TARGETS[0]}")
    return rejected and status.startswith("HTTP/"), f"without client cert: {'rejected' if rejected else 'ACCEPTED'}; with client cert: {status}"


@case("ITC-10", "RTCU registered and targets reported")
def itc10():
    devices = {d["target"]: d for d in get_json(f"{OPERATOR}/api/devices", insecure=True)}
    cf = devices.get(TARGETS[0], {})
    fresh = time.time() - cf.get("lastSeen", 0) < 120
    summary = ", ".join(f"{t} {'reachable' if d['reachable'] else 'unreachable'}" for t, d in devices.items())
    return bool(cf.get("reachable")) and fresh, f"{summary}; last seen {int(time.time() - cf.get('lastSeen', 0))} s ago"


@case("ITC-11", "Campaign outcomes recorded per target")
def itc11():
    campaigns = get_json(f"{OPERATOR}/api/campaigns", insecure=True)
    ok_ids = {t: [c["campaignId"] for c in campaigns if c["target"] == t and c["status"] == "success"] for t in TARGETS}
    unreachable = [c["campaignId"] for c in campaigns if c["status"] == "failed"
                   and any("unreachable" in s.get("detail", "") for s in c["statuses"])]
    ok = all(ok_ids.values()) and bool(unreachable)
    return ok, (f"success: {', '.join(f'{t} #{max(i)}' for t, i in ok_ids.items() if i)}; "
                f"unreachable target closed as failed: #{', #'.join(map(str, unreachable))}")


@case("ITC-12", "CARLA ego vehicle present")
def itc12():
    import carla
    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(5)
    egos = [a for a in client.get_world().get_actors().filter("vehicle.*") if a.attributes.get("role_name") == "ego_vehicle"]
    return bool(egos), f"ego_vehicle {egos[0].type_id} (id {egos[0].id})" if egos else "no ego_vehicle actor"


@case("ITC-13", "Android target ready with the cluster app")
def itc13():
    serial = "localhost:6520"
    subprocess.run(["adb", "connect", serial], capture_output=True, text=True, timeout=15)
    boot = subprocess.run(["adb", "-s", serial, "shell", "getprop", "sys.boot_completed"],
                          capture_output=True, text=True, timeout=15).stdout.strip()
    pkgs = subprocess.run(["adb", "-s", serial, "shell", "pm", "list", "packages"],
                          capture_output=True, text=True, timeout=30).stdout
    installed = "com.example.digitalclusterapp" in pkgs
    return boot == "1" and installed, f"boot_completed={boot or '?'}, cluster app {'installed' if installed else 'missing'}"


@case("ITC-14", "OpenSOVD gateway (PR #40) serves the cruise component")
def itc14():
    expected = {"vehicle_speed": "currentData", "cruise_state": "currentData",
                "speed_sensor_fault_status": "currentData", "speed_sensor_stuck": "storedData"}
    comps = [c["id"] for c in get_json(f"{GATEWAY}/components")["items"]]
    items = {d["id"]: d.get("category") for d in get_json(f"{GATEWAY}/components/cruise/data")["items"]}
    wrong = [f"{k} ({items.get(k)})" for k, cat in expected.items() if items.get(k) != cat]
    fault = get_json(f"{GATEWAY}/components/cruise/data/speed_sensor_fault_status")["data"]
    ok = "cruise" in comps and not wrong and fault.get("status") in ("passed", "prefailed", "failed", "prepassed")
    return ok, (f"component cruise with {', '.join(f'{k} ({v})' for k, v in items.items())}; "
                f"{fault.get('fault')} {fault.get('status')}" + (f"; wrong: {', '.join(wrong)}" if wrong else ""))


@case("ITC-15", "SOVD Adapter Console checks (Zenoh, gateway, CDA, ECU simulator)")
def itc15():
    r = subprocess.run(["docker", "exec", "sovd-adapter-console", "python", "runner.py"],
                       capture_output=True, text=True, timeout=180)
    lines = r.stdout.strip().splitlines()
    failed = [l.split()[1] + " " + " ".join(l.split()[2:6]) for l in lines if l.startswith("FAIL")]
    total = lines[-1] if lines else r.stderr.strip()[-120:]
    return r.returncode == 0 and not failed, total + (f"; failed: {'; '.join(failed)}" if failed else "")


@case("ITC-16", "ThreadX zonal lighting ECU on the AZ3166 board")
def itc16():
    if not list(Path("/dev/serial/by-id").glob("usb-STMicroelectronics_STM32_STLink_*-if02")):
        return None, "AZ3166 board not connected"
    out = subprocess.run([str(THREADX / "ctl.sh"), "status"], capture_output=True, text=True, timeout=30).stdout
    state = dict(l.split(":", 1) for l in out.splitlines() if ":" in l)
    running = "running" in state.get("watchdog", "") and state.get("bridge", "").strip() != ""
    connected = "not connected" not in state.get("board", "not connected")
    seen = zenoh_keys(["vehicle/lights/brake_lights_cmd", "vehicle/lights/reverse_lights_cmd"], seconds=3)
    return running and connected and bool(seen), (f"watchdog {state.get('watchdog', '?').strip()}, bridge "
                                                  f"{state.get('bridge', '').strip() or 'down'}, board "
                                                  f"{state.get('board', '?').strip()}, light commands seen: {sorted(seen)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, help="write the results as JSON")
    args = parser.parse_args()
    for check in (itc01, itc02, itc03, itc04, itc05, itc06, itc07, itc08, itc09, itc10, itc11, itc12, itc13,
                  itc14, itc15, itc16):
        check()
    record = {"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "host": socket.gethostname(), "cases": results}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(record, indent=2) + "\n")
    failed = [r["id"] for r in results if r["status"] == "FAIL"]
    passed = sum(r["status"] == "PASS" for r in results)
    not_run = [r["id"] for r in results if r["status"] == "NOT RUN"]
    print(f"{passed}/{len(results)} passed" + (f"; not run: {', '.join(not_run)}" if not_run else "")
          + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
