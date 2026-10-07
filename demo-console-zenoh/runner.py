# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: The 13 verification checks and the two fault scenarios, from the page or the command line.
"""Verification for v2.

13 automatic checks (page button or CLI). They only observe the vehicle side and do a
classic DTC round trip on a code the automation does not own:

    python runner.py [--json report.json]

Scenario tests make the vehicle misbehave and follow the whole reaction
(S-CORE fault -> automatic classic DTC -> read back through the CDA -> heal):

    python runner.py --scenario lost-link|invalid-speed|all [--sim-url http://127.0.0.1:7449]

With --sim-url the test vehicle (vehicle_sim.py) is driven automatically; without it the
runner tells you what to do on the real vehicle and waits. Exit code 0 = all pass.
"""
import argparse
import json
import sys
import time
import urllib.request

import config
from backends import Backends, active_fault, bit_set, decode_status, find_fault


class Check:
    def __init__(self, num, name, fn):
        self.num, self.name, self.fn = num, name, fn


def wait_for(fn, timeout, period=0.1):
    """Poll fn() until it returns a truthy value or the timeout passes. Returns (value, elapsed_s)."""
    t0 = time.time()
    while True:
        v = fn()
        if v:
            return v, time.time() - t0
        if time.time() - t0 > timeout:
            return None, time.time() - t0
        time.sleep(period)


def link(b):
    return b.sovd_read(config.SOVD_ITEM_LINK, config.SOVD_DIAG_ENTITY)[1] or {}


def score_fault(b, code):
    """The SOVD fault item for code, searched in both entities."""
    for entity in (config.SOVD_ENTITY, config.SOVD_DIAG_ENTITY):
        f = find_fault(b.sovd_faults(entity)[1], code)
        if f:
            return f
    return None


def auto_status(ctx):
    """From the console process when available, else over HTTP from a running console."""
    if ctx.get("auto") is not None:
        return ctx["auto"].status()
    url = f"http://127.0.0.1:{config.CONSOLE_PORT}/api/auto"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": f"console not reachable at {url}: {e}", "enabled": None, "running": False}


# ------------------------------------------------------------------ automatic checks

def c01(b, ctx):
    h = b.health()["sovd"]
    return h["up"], f"{h['status']} in {h['ms']} ms" if h["up"] else (h["error"] or f"HTTP {h['status']}")


def c02(b, ctx):
    if not b.cda.token and not b.cda.fetch_token():
        return False, f"token: {b.cda.token_error}"
    h = b.health()["cda"]
    return h["up"], f"{h['status']} in {h['ms']} ms" if h["up"] else (h["error"] or f"HTTP {h['status']}")


def c03(b, ctx):
    h = b.health()["sim"]
    return h["up"], f"{h['status']} in {h['ms']} ms" if h["up"] else (h["error"] or f"HTTP {h['status']}")


def c04(b, ctx):
    d = b.docker()
    if not config.DOCKER_CONTAINERS:
        return True, "no container expected (DOCKER_CONTAINERS is empty)"
    if not d["available"]:
        return False, d["error"] or "docker not available"
    missing = [n for n, ok in d["expected_running"].items() if not ok]
    return not missing, "all running" if not missing else "not running: " + ", ".join(missing)


def c05(b, ctx):
    lk = link(b)
    if not lk:
        return False, "no link_status from the SOVD side"
    if lk.get("error"):
        return False, lk["error"]
    ok = lk.get("connected") or lk.get("state") == "live"
    return bool(ok), (f"state {lk.get('state')}, peers {lk.get('peers')}, routers {lk.get('routers')}, "
                      f"endpoints {','.join(lk.get('endpoints') or []) or '-'}")


def c06(b, ctx):
    lk = link(b)
    rate, age = lk.get("rate_hz") or 0, lk.get("age_ms")
    ok = lk.get("state") == "live" and rate >= 1
    return ok, f"{rate} samples/s on '{lk.get('key')}', last {age} ms ago, raw '{lk.get('last_raw')}'"


def c07(b, ctx):
    r, d1 = b.sovd_read(config.SOVD_ITEM_SPEED)
    if not r.ok or not isinstance(d1, dict):
        return False, r.error or f"HTTP {r.status}"
    time.sleep(0.6)
    _, d2 = b.sovd_read(config.SOVD_ITEM_SPEED)
    d2 = d2 or {}
    v = d2.get("value")
    plausible = isinstance(v, (int, float)) and config.SPEED_MIN_KMH <= v <= config.SPEED_MAX_KMH
    advances = (d2.get("ts") or 0) > (d1.get("ts") or 0)
    return plausible and advances and not d2.get("stale"), \
        f"{v} km/h, {'fresh' if not d2.get('stale') else 'STALE'}, timestamp {'advances' if advances else 'does not advance'}"


def c08(b, ctx):
    _, d = b.sovd_read(config.SOVD_ITEM_DEBOUNCE)
    f = score_fault(b, config.F1_CODE)
    failing = f is not None and bit_set(f.get("status"), 0)
    ok = isinstance(d, dict) and d.get("state") == "PASSED" and f is not None and not failing
    return ok, (f"monitor {d.get('state') if isinstance(d, dict) else '?'}, "
                f"{config.F1_CODE} status {decode_status(f.get('status'))['hex'] if f else 'missing'}")


def c09(b, ctx):
    lk = link(b)
    f = score_fault(b, config.F2_CODE)
    failing = f is not None and bit_set(f.get("status"), 0)
    ok = bool(lk.get("monitor_armed")) and f is not None and not failing
    return ok, (f"monitor {'armed' if lk.get('monitor_armed') else 'NOT armed (no valid sample yet)'}, "
                f"{config.F2_CODE} status {decode_status(f.get('status'))['hex'] if f else 'missing'}")


def c10(b, ctx):
    s1 = b.stats()
    if not s1["ok"]:
        return False, s1["error"]
    if s1["age_s"] is None or s1["age_s"] > 3:
        return False, f"file is {s1['age_s']} s old"
    time.sleep(1.3)
    s2 = b.stats()
    grew = [k for k in s2["counters"] if s2["counters"][k] > s1["counters"].get(k, 0)]
    return bool(grew), ("increasing: " + ", ".join(grew)) if grew else "no counter increased in 1.3 s"


def c11(b, ctx):
    st = auto_status(ctx)
    if st.get("enabled") is False:
        return True, "automatic DTC is switched off (AUTO_DTC=0)"
    ok = bool(st.get("running")) and not st.get("error")
    mapping = ", ".join(f"{k}->{v}" for k, v in (st.get("map") or {}).items())
    return ok, (f"running, {mapping}, {st.get('polls')} polls" if ok else st.get("error") or "not running")


def c12(b, ctx):
    if config.DEMO_DTC.upper() in config.dtc_map().values():
        return False, f"DEMO_DTC {config.DEMO_DTC} is owned by AUTO_DTC_MAP: choose another code"
    r = b.sim_set(config.DEMO_DTC, config.DEMO_DTC_MASK)
    if not r.ok:
        return False, f"inject -> {r.status or r.error}"
    want = int(config.DEMO_DTC_MASK, 16)
    f, el = wait_for(lambda: active_fault(b.cda_faults()[1], config.DEMO_DTC), 3.0, 0.3)
    if not f:
        return False, f"DTC {config.DEMO_DTC} not in the CDA list after 3 s"
    got = decode_status(f.get("status"))["raw"]
    return got == want, f"visible after {el * 1000:.0f} ms; status 0x{got:02X}" + ("" if got == want else f", expected 0x{want:02X}")


def c13(b, ctx):
    r = b.sim_delete(config.DEMO_DTC)
    if not r.ok:
        return False, f"delete -> {r.status or r.error}"
    v, el = wait_for(lambda: not active_fault(b.cda_faults()[1], config.DEMO_DTC), 3.0, 0.3)
    return bool(v), (f"gone (or status 00) after {el * 1000:.0f} ms; other DTCs untouched" if v
                     else "still active in the CDA list after 3 s")


CHECKS = [
    Check(1, "SOVD side answers", c01),
    Check(2, "CDA answers with the token", c02),
    Check(3, "ECU simulator answers", c03),
    Check(4, "Expected Docker containers run", c04),
    Check(5, "Zenoh: connected to the vehicle", c05),
    Check(6, "Zenoh: speed samples arriving", c06),
    Check(7, "Speed via SOVD: plausible and fresh", c07),
    Check(8, "F1 plausibility: PASSED, not failing", c08),
    Check(9, "F2 link monitor: armed, not failing", c09),
    Check(10, "Stats file fresh, counters increase", c10),
    Check(11, "Automatic classic DTC running", c11),
    Check(12, "Classic: injected DTC read via CDA", c12),
    Check(13, "Classic: deleted DTC gone", c13),
]


def run_all(backends, progress=None, auto=None):
    """Runs every automatic check in order. progress(result) is called after each one."""
    ctx = {"auto": auto}
    results = []
    for c in CHECKS:
        t0 = time.time()
        try:
            ok, detail = c.fn(backends, ctx)
        except Exception as e:  # a check must never take the runner down
            ok, detail = False, f"{type(e).__name__}: {e}"
        res = {"num": c.num, "name": c.name, "ok": bool(ok), "detail": str(detail), "ms": round((time.time() - t0) * 1000)}
        results.append(res)
        if progress:
            progress(res)
    return results


# ------------------------------------------------------------------ scenarios

class Vehicle:
    """Drives the test vehicle (vehicle_sim.py) or asks a human to act on the real one."""

    def __init__(self, sim_url=None, say=print):
        self.sim_url, self.say = sim_url, say

    def act(self, mode, instruction):
        if self.sim_url:
            req = urllib.request.Request(self.sim_url.rstrip("/") + "/mode", data=json.dumps({"mode": mode}).encode(),
                                         method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as r:
                return r.status == 200
        self.say(f"\n>>> ACTION: {instruction}\n")
        return True

    @property
    def patience(self):
        return 8.0 if self.sim_url else 90.0   # a human needs time


def ecu_dtc_mask(b, dtc):
    f = find_fault(b.cda_faults()[1], dtc)
    return None if f is None else decode_status(f.get("status"))["raw"]


def scenario(b, kind, vehicle, ctx, progress=None):
    """kind: lost-link | invalid-speed. Returns the list of step results."""
    code = config.F2_CODE if kind == "lost-link" else config.F1_CODE
    dtc = config.dtc_map().get(code)
    active, healed = int(config.AUTO_DTC_MASK_ACTIVE, 16), int(config.AUTO_DTC_MASK_HEALED, 16)
    results = []

    def step(name, fn):
        t0 = time.time()
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"{type(e).__name__}: {e}"
        res = {"num": f"{'L' if kind == 'lost-link' else 'I'}{len(results) + 1}", "name": name, "ok": bool(ok),
               "detail": str(detail), "ms": round((time.time() - t0) * 1000)}
        results.append(res)
        if progress:
            progress(res)
        return ok

    def failing():
        f = score_fault(b, code)
        return f is not None and bit_set(f.get("status"), 0)

    def pre():
        vehicle.act("normal", "make sure the virtual vehicle publishes valid speed values")
        v, el = wait_for(lambda: link(b).get("state") == "live" and link(b).get("monitor_armed") and not failing(),
                         vehicle.patience, 0.2)
        return bool(v), f"link live, {code} not failing" if v else f"precondition not reached ({link(b).get('state')})"

    def trigger():
        if kind == "lost-link":
            vehicle.act("stop", "STOP the virtual vehicle's speed publisher (or pull its connection)")
        else:
            vehicle.act("invalid", "make the virtual vehicle publish INVALID speed values (NaN, negative, > 300 or text)")
        v, el = wait_for(failing, vehicle.patience + config.LINK_TIMEOUT_MS / 1000, 0.05)
        f = score_fault(b, code)
        status = decode_status(f.get("status"))["hex"] if f else "?"
        return bool(v), (f"{code} testFailed after {el * 1000:.0f} ms, status {status}"
                         if v else f"{code} not failing after {el:.1f} s")

    def auto_check(want):
        def run():
            if not dtc:
                return False, f"{code} is not in AUTO_DTC_MAP"
            v, el = wait_for(lambda: ecu_dtc_mask(b, dtc) == want, 5.0, 0.2)
            if v:
                return True, f"ECU DTC {dtc} reads 0x{want:02X} via CDA after {el * 1000:.0f} ms"
            got = ecu_dtc_mask(b, dtc)
            hint = "" if auto_status(ctx).get("running") else " (is the console server running?)"
            return False, (f"ECU DTC {dtc} is {'absent' if got is None else f'0x{got:02X}'} via CDA, "
                           f"expected 0x{want:02X}{hint}")
        return run

    def heal():
        vehicle.act("normal", "RESTART / repair the vehicle: valid speed values again")
        v, el = wait_for(lambda: not failing(), vehicle.patience + 5, 0.1)
        f = score_fault(b, code)
        if not v or f is None:
            return False, f"{code} still failing after {el:.1f} s"
        kept = bit_set(f.get("status"), 3)
        return kept, (f"testFailed back to 0 after {el * 1000:.0f} ms, confirmedDTC "
                      f"{'kept' if kept else 'LOST'} (status {decode_status(f.get('status'))['hex']})")

    label = "Lost communication (F2)" if kind == "lost-link" else "Invalid speed (F1)"
    if not step(f"{label}: precondition", pre):
        return results
    if step(f"{label}: S-CORE fault {code} detected", trigger):
        step(f"{label}: ECU DTC set automatically, read via CDA", auto_check(active))
    if step(f"{label}: vehicle back, {code} healed", heal):
        step(f"{label}: ECU DTC healed, read via CDA", auto_check(healed))
    return results


def main():
    ap = argparse.ArgumentParser(description="Demo Console v2 verification")
    ap.add_argument("--json", help="write the report to this file")
    ap.add_argument("--scenario", choices=["lost-link", "invalid-speed", "all"], help="run scenario tests instead")
    ap.add_argument("--sim-url", help="control URL of vehicle_sim.py, e.g. http://127.0.0.1:7449")
    args = ap.parse_args()
    b = Backends()
    ctx = {"auto": None}

    def show(r):
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {str(r['num']):>3}  {r['name']:<52} {r['ms']:>6} ms  {r['detail']}", flush=True)

    if args.scenario:
        vehicle = Vehicle(args.sim_url)
        kinds = ["lost-link", "invalid-speed"] if args.scenario == "all" else [args.scenario]
        print(f"Demo Console v{config.VERSION}: scenario {', '.join(kinds)}"
              f" ({'automatic via ' + args.sim_url if args.sim_url else 'manual: follow the ACTION lines'})\n")
        results = [r for k in kinds for r in scenario(b, k, vehicle, ctx, show)]
    else:
        print(f"Demo Console v{config.VERSION}: {len(CHECKS)} checks\n")
        results = run_all(b, show)
    passed = sum(r["ok"] for r in results)
    print(f"\n{passed}/{len(results)} passed")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "results": results}, f, indent=2)
    sys.exit(0 if results and passed == len(results) else 1)


if __name__ == "__main__":
    main()
