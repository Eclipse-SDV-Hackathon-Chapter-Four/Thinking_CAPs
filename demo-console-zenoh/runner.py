# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: checks and scenarios against the PR #40 gateway contract)
# Goal: The 13 verification checks and the three fault scenarios, from the page or the command line.
"""Verification for v2.1.

13 automatic checks (page button or CLI). They only observe the vehicle side, verify the
gateway's PR #40 contract, and do a classic DTC round trip on a code the automation does
not own:

    python runner.py [--json report.json]

Scenario tests make a fault happen and follow the whole reaction
(fault qualified -> automatic classic DTC -> read back through the CDA -> heal):

    python runner.py --scenario lost-link|invalid-speed|stuck-switch|all [--sim-url http://127.0.0.1:7449]

  lost-link      the vehicle stops publishing: F2 (console link monitor) -> U0104 -> DTC
  invalid-speed  the vehicle publishes invalid values: F1 verdict -> bridge -> gateway switch
                 -> gateway debounce -> P0500 confirmed -> DTC (then valid values: heal)
  stuck-switch   no vehicle action: PUT speed_sensor_stuck directly on the gateway (the
                 write path of PR #40) -> debounce -> P0500 -> DTC, then PUT false -> heal

With --sim-url the test vehicle (vehicle_sim.py) is driven automatically; without it the
runner tells you what to do on the real vehicle and waits. The checks and scenarios need
the console server (its observer and fault model); from the CLI they read it over HTTP.
Exit code 0 = all pass.
"""
import argparse
import json
import sys
import time
import urllib.request

import config
from backends import Backends, active_fault, decode_status, find_fault
from faults import STAGES

CRUISE_STATES = ("standby", "active", "unavailable")


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


# ------------------------------------------------------------------ console access (in process or over HTTP)

def console_api(ctx, name):
    """A console view: from the console object when the runner runs inside the server,
    else over HTTP from the running console. Never raises."""
    c = ctx.get("console")
    if c is not None:
        views = {"vehicle": c.vehicle_view, "sovd": c.sovd_view, "faults": lambda: {"items": c.faults.faults_view()},
                 "auto": c.auto.status, "stats": c.stats}
        return views[name]()
    url = f"http://127.0.0.1:{config.CONSOLE_PORT}/api/{name}"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": f"console not reachable at {url}: {e}"}


def link(ctx):
    return (console_api(ctx, "vehicle") or {}).get("link") or {}


def tester_fault(ctx, code):
    return find_fault((console_api(ctx, "faults") or {}).get("items"), code)


def console_probe(ctx):
    c = ctx.get("console")
    if c is not None:
        return c.probe_contract()
    return (console_api(ctx, "sovd") or {}).get("contract") or {}


# ------------------------------------------------------------------ automatic checks

def c01(b, ctx):
    h = b.health()["sovd"]
    if not h["up"]:
        return False, h["error"] or f"HTTP {h['status']}"
    return True, f"SOVD {h.get('sovd_version')} at {h.get('base_uri')} in {h['ms']} ms"


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
    lk = link(ctx)
    if not lk:
        return False, (console_api(ctx, "vehicle") or {}).get("error") or "no link view from the console"
    if lk.get("error"):
        return False, lk["error"]
    ok = lk.get("connected") or lk.get("state") == "live"
    return bool(ok), (f"state {lk.get('state')}, peers {lk.get('peers')}, routers {lk.get('routers')}, "
                      f"endpoints {','.join(lk.get('endpoints') or []) or '-'}")


def c06(b, ctx):
    lk = link(ctx)
    rate, age = lk.get("rate_hz") or 0, lk.get("age_ms")
    ok = lk.get("state") == "live" and rate >= 1
    return ok, f"{rate} samples/s on '{lk.get('key')}', last {age} ms ago, raw '{lk.get('last_raw')}'"


def c07(b, ctx):
    r1, comps = b.sovd_components()
    if not r1.ok:
        return False, f"GET components: {r1.problem()}"
    ids = [c.get("id") for c in comps if isinstance(c, dict)]
    if config.SOVD_COMPONENT not in ids:
        return False, f"component '{config.SOVD_COMPONENT}' not listed: {ids}"
    r2, items = b.sovd_data_list()
    if not r2.ok:
        return False, f"GET data: {r2.problem()}"
    by_id = {i.get("id"): i for i in items if isinstance(i, dict)}
    want = config.sovd_items()
    missing = [v for v in want.values() if v not in by_id]
    if missing:
        return False, f"data items missing: {missing}; served: {list(by_id)}"
    cat = by_id[want["switch"]].get("category")
    cats = ", ".join(f"{i['id']} ({i.get('category')})" for i in items)
    return cat == "storedData", f"{cats}" + ("" if cat == "storedData" else f"; expected {want['switch']} in storedData")


def c08(b, ctx):
    it = config.sovd_items()
    out, ok = [], True
    r, sp = b.sovd_read(it["speed"])
    v = (sp or {}).get("value") if isinstance(sp, dict) else None
    good = isinstance(v, (int, float)) and config.SPEED_MIN_KMH <= v <= config.SPEED_MAX_KMH
    ok &= good
    out.append(f"{it['speed']} {v} {(sp or {}).get('unit') if isinstance(sp, dict) else ''}".strip() if r.ok else f"{it['speed']}: {r.problem()}")
    r, st = b.sovd_read(it["state"])
    s = (st or {}).get("state") if isinstance(st, dict) else None
    ok &= s in CRUISE_STATES
    out.append(f"{it['state']} {s}" if r.ok else f"{it['state']}: {r.problem()}")
    r, fs = b.sovd_read(it["fault"])
    stage = (fs or {}).get("status") if isinstance(fs, dict) else None
    ok &= stage in STAGES
    out.append(f"{it['fault']} {(fs or {}).get('fault') if isinstance(fs, dict) else ''} {stage}".strip() if r.ok else f"{it['fault']}: {r.problem()}")
    r, sw = b.sovd_read(it["switch"])
    stuck = (sw or {}).get("stuck") if isinstance(sw, dict) else None
    ok &= isinstance(stuck, bool)
    out.append(f"{it['switch']} {stuck}" if r.ok else f"{it['switch']}: {r.problem()}")
    return bool(ok), " · ".join(out)


def c09(b, ctx):
    f1 = (console_api(ctx, "vehicle") or {}).get("f1") or {}
    s = console_api(ctx, "sovd") or {}
    br = s.get("bridge") or {}
    gw = ((s.get("items") or {}).get("fault") or {}).get("data") or {}
    stuck = ((s.get("items") or {}).get("switch") or {}).get("data") or {}
    console_ok = f1.get("state") == "PASSED" and not f1.get("failed")
    gateway_ok = gw.get("status") == "passed" and stuck.get("stuck") is False
    sync_ok = (not br.get("enabled")) or br.get("in_sync") in (True, None)
    return bool(console_ok and gateway_ok and sync_ok), (
        f"console F1 {f1.get('state')} {f1.get('counter')}/{f1.get('threshold')} · gateway {gw.get('fault')} "
        f"{gw.get('status')} · switch {stuck.get('stuck')} · bridge {'on' if br.get('enabled') else 'off'}"
        f"{'' if not br.get('enabled') else ', in sync' if br.get('in_sync') else ', NOT in sync'}")


def c10(b, ctx):
    lk = link(ctx)
    f = tester_fault(ctx, config.F2_CODE)
    failing = f is not None and f.get("qualified_failed")
    ok = bool(lk.get("monitor_armed")) and f is not None and not failing
    return ok, (f"monitor {'armed' if lk.get('monitor_armed') else 'NOT armed (no valid sample yet)'}, "
                f"{config.F2_CODE} {f.get('stage') if f else 'missing'} status {decode_status(f.get('status'))['hex'] if f else '-'}")


def c11(b, ctx):
    s1 = console_api(ctx, "stats") or {}
    if not s1.get("ok"):
        return False, s1.get("error") or "no stats from the console"
    time.sleep(1.3)
    s2 = console_api(ctx, "stats") or {}
    c1, c2 = s1.get("counters") or {}, s2.get("counters") or {}
    want = ("observer_ticks", "gateway_polls")
    grew = [k for k in want if c2.get(k, 0) > c1.get(k, 0)]
    err = s2.get("cycle_error")
    return len(grew) == len(want) and not err, ("increasing: " + ", ".join(grew) + (f" · last error: {err}" if err else "")) \
        if grew else "observer / gateway cycle not advancing"


def c12(b, ctx):
    st = console_api(ctx, "auto") or {}
    if st.get("enabled") is False:
        return True, "automatic DTC is switched off (AUTO_DTC=0)"
    ok = bool(st.get("running")) and not st.get("error")
    mapping = ", ".join(f"{k}->{v}" for k, v in (st.get("map") or {}).items())
    return ok, (f"running, {mapping}, {st.get('polls')} polls" if ok else st.get("error") or "not running")


def c13(b, ctx):
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
    if got != want:
        return False, f"visible after {el * 1000:.0f} ms with status 0x{got:02X}, expected 0x{want:02X}"
    r = b.sim_delete(config.DEMO_DTC)
    if not r.ok:
        return False, f"delete -> {r.status or r.error}"
    v, el2 = wait_for(lambda: not active_fault(b.cda_faults()[1], config.DEMO_DTC), 3.0, 0.3)
    return bool(v), (f"set 0x{got:02X} visible via CDA after {el * 1000:.0f} ms, gone after {el2 * 1000:.0f} ms; other DTCs untouched"
                     if v else "still active in the CDA list 3 s after the delete")


CHECKS = [
    Check(1, "SOVD gateway answers (version-info)", c01),
    Check(2, "CDA answers with the token", c02),
    Check(3, "ECU simulator answers", c03),
    Check(4, "Expected Docker containers run", c04),
    Check(5, "Zenoh: console connected to the vehicle", c05),
    Check(6, "Zenoh: speed samples arriving", c06),
    Check(7, "SOVD contract: component and four data items (#16)", c07),
    Check(8, "SOVD reads: speed, state, fault status, switch", c08),
    Check(9, "F1 chain idle and in sync (console, bridge, gateway)", c09),
    Check(10, "F2 link monitor: armed, not failing", c10),
    Check(11, "Console cycles alive (observer, gateway poll)", c11),
    Check(12, "Automatic classic DTC running", c12),
    Check(13, "Classic round trip: inject, read via CDA, delete", c13),
]


def run_all(backends, progress=None, console=None):
    """Runs every automatic check in order. progress(result) is called after each one."""
    ctx = {"console": console}
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


def set_switch(ctx, b, stuck):
    c = ctx.get("console")
    if c is not None:
        return c.faults.set_switch(stuck, origin="scenario")
    return b.sovd_write(config.SOVD_ITEM_SWITCH, {"stuck": stuck}, origin="scenario")


KINDS = ("lost-link", "invalid-speed", "stuck-switch")
LABELS = {"lost-link": "Lost communication (F2)", "invalid-speed": "Invalid speed (F1 via bridge)",
          "stuck-switch": "Gateway switch (F1 via PUT)"}
PREFIX = {"lost-link": "L", "invalid-speed": "I", "stuck-switch": "S"}


def scenario(b, kind, vehicle, ctx, progress=None):
    """kind: lost-link | invalid-speed | stuck-switch. Returns the list of step results."""
    code = config.F2_CODE if kind == "lost-link" else config.F1_CODE
    dtc = config.dtc_map().get(code)
    active, healed = int(config.AUTO_DTC_MASK_ACTIVE, 16), int(config.AUTO_DTC_MASK_HEALED, 16)
    debounce_failed = config.CRUISE_DEBOUNCE_FAILED_MS / 1000.0 if kind != "lost-link" else 0.0
    debounce_passed = config.CRUISE_DEBOUNCE_PASSED_MS / 1000.0 if kind != "lost-link" else 0.0
    results = []

    def step(name, fn):
        t0 = time.time()
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"{type(e).__name__}: {e}"
        res = {"num": f"{PREFIX[kind]}{len(results) + 1}", "name": name, "ok": bool(ok),
               "detail": str(detail), "ms": round((time.time() - t0) * 1000)}
        results.append(res)
        if progress:
            progress(res)
        return ok

    def fault():
        return tester_fault(ctx, code) or {}

    def qualified():
        return bool(fault().get("qualified_failed"))

    def pre():
        vehicle.act("normal", "make sure the virtual vehicle publishes valid speed values")
        v, el = wait_for(lambda: link(ctx).get("state") == "live" and link(ctx).get("monitor_armed")
                         and not qualified() and fault().get("stage") == "passed",
                         vehicle.patience + debounce_passed, 0.2)
        f = fault()
        return bool(v), (f"link live, {code} {f.get('stage')} (status {decode_status(f.get('status'))['hex']})" if v
                         else f"precondition not reached (link {link(ctx).get('state')}, {code} {f.get('stage')})")

    def trigger():
        if kind == "lost-link":
            vehicle.act("stop", "STOP the virtual vehicle's speed publisher (or pull its connection)")
        elif kind == "invalid-speed":
            vehicle.act("invalid", "make the virtual vehicle publish INVALID speed values (NaN, negative, > 300 or text)")
        else:
            r = set_switch(ctx, b, True)
            if not r.ok:
                return False, f"PUT {config.SOVD_ITEM_SWITCH} stuck=true -> {r.problem()}"
        raw, el_raw = wait_for(lambda: fault().get("test_failed"), vehicle.patience + config.LINK_TIMEOUT_MS / 1000, 0.05)
        v, el = wait_for(qualified, vehicle.patience + debounce_failed + 2, 0.05)
        f = fault()
        status = decode_status(f.get("status"))["hex"]
        if not v:
            return False, f"{code} not qualified after {el:.1f} s (stage {f.get('stage')}, raw failing after {el_raw * 1000:.0f} ms)"
        extra = f", cruise_state {f.get('cruise_state')}" if f.get("cruise_state") else ""
        return True, (f"{code} raw failing after {el_raw * 1000:.0f} ms, qualified FAILED after {(el_raw + el) * 1000:.0f} ms, "
                      f"status {status}{extra}")

    def auto_check(want):
        def run():
            if not dtc:
                return False, f"{code} is not in AUTO_DTC_MAP"
            v, el = wait_for(lambda: ecu_dtc_mask(b, dtc) == want, 5.0, 0.2)
            if v:
                return True, f"ECU DTC {dtc} reads 0x{want:02X} via CDA after {el * 1000:.0f} ms"
            got = ecu_dtc_mask(b, dtc)
            hint = "" if (console_api(ctx, "auto") or {}).get("running") else " (is the console server running?)"
            return False, (f"ECU DTC {dtc} is {'absent' if got is None else f'0x{got:02X}'} via CDA, "
                           f"expected 0x{want:02X}{hint}")
        return run

    def heal():
        if kind == "stuck-switch":
            r = set_switch(ctx, b, False)
            if not r.ok:
                return False, f"PUT {config.SOVD_ITEM_SWITCH} stuck=false -> {r.problem()}"
        else:
            vehicle.act("normal", "RESTART / repair the vehicle: valid speed values again")
        v, el = wait_for(lambda: not qualified(), vehicle.patience + debounce_passed + 5, 0.1)
        f = fault()
        if not v or not f:
            return False, f"{code} still qualified failed after {el:.1f} s (stage {f.get('stage')})"
        kept = bool(f.get("stored"))
        return kept, (f"qualified PASSED after {el * 1000:.0f} ms, stored flag {'kept' if kept else 'LOST'} "
                      f"(status {decode_status(f.get('status'))['hex']})")

    label = LABELS[kind]
    if not step(f"{label}: precondition", pre):
        return results
    if step(f"{label}: fault {code} qualified", trigger):
        step(f"{label}: ECU DTC set automatically, read via CDA", auto_check(active))
    if step(f"{label}: repaired, {code} healed", heal):
        step(f"{label}: ECU DTC healed, read via CDA", auto_check(healed))
    return results


def main():
    ap = argparse.ArgumentParser(description="Demo Console v2 verification")
    ap.add_argument("--json", help="write the report to this file")
    ap.add_argument("--scenario", choices=[*KINDS, "all"], help="run scenario tests instead")
    ap.add_argument("--sim-url", help="control URL of vehicle_sim.py, e.g. http://127.0.0.1:7449")
    args = ap.parse_args()
    b = Backends()
    ctx = {"console": None}

    def show(r):
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {str(r['num']):>3}  {r['name']:<58} {r['ms']:>6} ms  {r['detail']}", flush=True)

    if args.scenario:
        vehicle = Vehicle(args.sim_url)
        kinds = list(KINDS) if args.scenario == "all" else [args.scenario]
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
