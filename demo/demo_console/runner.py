"""The 13 verification checks. Run from the page (POST /api/run) or from the
command line: python runner.py [--json report.json]. Exit code 0 = all pass.
"""
import argparse
import json
import sys
import time

import config
from backends import Backends, bit_set


class Check:
    def __init__(self, num, name, fn):
        self.num, self.name, self.fn = num, name, fn


def wait_for(fn, timeout, period=0.1):
    """Poll fn() until it returns a truthy value or the timeout passes.
    Returns (value, elapsed_s)."""
    t0 = time.time()
    while True:
        v = fn()
        if v:
            return v, time.time() - t0
        if time.time() - t0 > timeout:
            return None, time.time() - t0
        time.sleep(period)


def norm_code(code):
    return str(code or "").strip().upper().lstrip("0") or "0"


def find_fault(items, code):
    for it in items:
        if norm_code(it.get("code")) == norm_code(code):
            return it
    return None


# ------------------------------------------------------------------ checks

def c01(b):
    h = b.health()["sovd"]
    return h["up"], f"{h['status']} in {h['ms']} ms" if h["up"] else (h["error"] or f"HTTP {h['status']}")


def c02(b):
    if not b.cda.token and not b.cda.fetch_token():
        return False, f"token: {b.cda.token_error}"
    h = b.health()["cda"]
    return h["up"], f"{h['status']} in {h['ms']} ms" if h["up"] else (h["error"] or f"HTTP {h['status']}")


def c03(b):
    h = b.health()["sim"]
    return h["up"], f"{h['status']} in {h['ms']} ms" if h["up"] else (h["error"] or f"HTTP {h['status']}")


def c04(b):
    d = b.docker()
    if not config.DOCKER_CONTAINERS:
        return True, "no container expected (DOCKER_CONTAINERS is empty)"
    if not d["available"]:
        return False, d["error"] or "docker not available"
    missing = [n for n, ok in d["expected_running"].items() if not ok]
    return not missing, "all running" if not missing else "not running: " + ", ".join(missing)


def c05(b):
    s1 = b.stats()
    if not s1["ok"]:
        return False, s1["error"]
    if s1["age_s"] is None or s1["age_s"] > 3:
        return False, f"file is {s1['age_s']} s old"
    time.sleep(1.3)
    s2 = b.stats()
    grew = [k for k in s2["counters"] if s2["counters"][k] > s1["counters"].get(k, 0)]
    return bool(grew), ("increasing: " + ", ".join(grew)) if grew else "no counter increased in 1.3 s"


def c06(b):
    note = ""
    _, deb = b.sovd_read(config.SOVD_ITEM_DEBOUNCE)
    if isinstance(deb, dict) and deb.get("frozen"):  # a previous freeze must not fail this check
        b.sovd_write(config.SOVD_ITEM_FREEZE, False)
        time.sleep(0.3)
        note = " (sensor was frozen: released first)"
    r, d1 = b.sovd_read(config.SOVD_ITEM_SPEED)
    if not r.ok or not isinstance(d1, dict):
        return False, r.error or f"HTTP {r.status}"
    time.sleep(0.4)
    _, d2 = b.sovd_read(config.SOVD_ITEM_SPEED)
    ok = isinstance(d2, dict) and d2.get("ts", 0) > d1.get("ts", 0)
    return ok, f"{d1.get('value')} {d1.get('unit', '')}, timestamp {'advances' if ok else 'does not advance'}{note}"


def c07(b):
    """Precondition. If a previous run left the sensor frozen, unfreeze and wait."""
    _, d = b.sovd_read(config.SOVD_ITEM_DEBOUNCE)
    if isinstance(d, dict) and d.get("state") != "PASSED":
        b.sovd_write(config.SOVD_ITEM_FREEZE, False)
        wait_for(lambda: (b.sovd_read(config.SOVD_ITEM_DEBOUNCE)[1] or {}).get("state") == "PASSED", 8)
    _, d = b.sovd_read(config.SOVD_ITEM_DEBOUNCE)
    _, faults = b.sovd_faults()
    failing = [f.get("code") for f in faults if bit_set(f.get("status"), 0)]
    ok = isinstance(d, dict) and d.get("state") == "PASSED" and not failing
    return ok, f"state {d.get('state') if isinstance(d, dict) else '?'}, failing faults: {failing or 'none'}"


def c08(b):
    r = b.sovd_write(config.SOVD_ITEM_FREEZE, True)
    return r.ok, f"PUT sensor_freeze=true -> {r.status or r.error}"


def c09(b):
    v, el = wait_for(lambda: (b.sovd_read(config.SOVD_ITEM_DEBOUNCE)[1] or {}).get("state") in ("PREFAILED", "FAILED"), 1.0)
    return bool(v), f"debounce left PASSED after {el * 1000:.0f} ms" if v else "still PASSED after 1 s"


def c10(b):
    v, el = wait_for(lambda: (b.sovd_read(config.SOVD_ITEM_DEBOUNCE)[1] or {}).get("state") == "FAILED", 8.0)
    if not v:
        return False, "FAILED not reached within 8 s"

    def failing_confirmed():
        _, faults = b.sovd_faults()
        return [f for f in faults if bit_set(f.get("status"), 0) and bit_set(f.get("status"), 3)]
    f, el2 = wait_for(failing_confirmed, 2.0)
    return bool(f), (f"FAILED after {el:.1f} s; fault {f[0].get('code')} testFailed+confirmedDTC after {el2 * 1000:.0f} ms"
                     if f else "no fault with testFailed and confirmedDTC set")


def c11(b):
    r = b.sovd_write(config.SOVD_ITEM_FREEZE, False)
    if not r.ok:
        return False, f"PUT sensor_freeze=false -> {r.status or r.error}"

    def not_failing():
        _, faults = b.sovd_faults()
        return faults and not any(bit_set(f.get("status"), 0) for f in faults)
    v, el = wait_for(not_failing, 8.0)
    _, faults = b.sovd_faults()
    kept = [f.get("code") for f in faults if bit_set(f.get("status"), 3)]
    return bool(v), (f"testFailed back to 0 after {el:.1f} s; confirmedDTC kept on {kept or 'none'}"
                     if v else "testFailed still set after 8 s")


def c12(b):
    r = b.sim_inject(config.DEMO_DTC, config.DEMO_DTC_MASK)
    if not r.ok:
        return False, f"inject -> {r.status or r.error}"
    want = int(config.DEMO_DTC_MASK, 16)

    def visible():
        _, items = b.cda_faults()
        return find_fault(items, config.DEMO_DTC)
    f, el = wait_for(visible, 3.0, 0.3)
    if not f:
        return False, f"DTC {config.DEMO_DTC} not in the CDA list after 3 s"
    from backends import decode_status
    got = decode_status(f.get("status"))["raw"]
    ok = got == want
    return ok, f"visible after {el * 1000:.0f} ms; status 0x{got:02X}" + ("" if ok else f", expected 0x{want:02X}")


def c13(b):
    r = b.sim_clear()
    if not r.ok:
        return False, f"clear -> {r.status or r.error}"
    v, el = wait_for(lambda: not find_fault(b.cda_faults()[1], config.DEMO_DTC), 3.0, 0.3)
    return bool(v), f"gone after {el * 1000:.0f} ms" if v else "still listed by the CDA after 3 s"


CHECKS = [
    Check(1, "SOVD gateway answers", c01),
    Check(2, "CDA answers with the token", c02),
    Check(3, "ECU simulator answers", c03),
    Check(4, "Expected Docker containers run", c04),
    Check(5, "Stats file fresh, counters increase", c05),
    Check(6, "Speed readable, timestamp advances", c06),
    Check(7, "At start: PASSED, no failing fault", c07),
    Check(8, "Freeze accepted", c08),
    Check(9, "Debounce PREFAILED within 1 s", c09),
    Check(10, "FAILED: testFailed and confirmedDTC set", c10),
    Check(11, "Unfreeze: testFailed back to 0", c11),
    Check(12, "Injected DTC in the CDA list, bits match", c12),
    Check(13, "Cleared DTC gone from the CDA list", c13),
]


def run_all(backends, progress=None):
    """Runs every check in order. progress(result) is called after each one."""
    results = []
    for c in CHECKS:
        t0 = time.time()
        try:
            ok, detail = c.fn(backends)
        except Exception as e:  # a check must never take the runner down
            ok, detail = False, f"{type(e).__name__}: {e}"
        res = {"num": c.num, "name": c.name, "ok": bool(ok), "detail": str(detail), "ms": round((time.time() - t0) * 1000)}
        results.append(res)
        if progress:
            progress(res)
    return results


def main():
    ap = argparse.ArgumentParser(description="Demo Console verification runner")
    ap.add_argument("--json", help="write the report to this file")
    args = ap.parse_args()
    b = Backends()

    def show(r):
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['num']:>2}  {r['name']:<42} {r['ms']:>6} ms  {r['detail']}")
    print("Demo Console: 13 checks\n")
    results = run_all(b, show)
    passed = sum(r["ok"] for r in results)
    print(f"\n{passed}/{len(results)} passed")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "results": results}, f, indent=2)
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
