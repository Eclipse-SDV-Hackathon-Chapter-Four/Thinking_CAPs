#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Qualification test cases QTC-02, QTC-03 and QTC-07 against the running X-Verse system.

Active: unlike e2e_check.py, this drives the vehicle. It presses the driver keys of
Vehicle Manual Control through its scripted input channel (Zenoh key
`test/manual_control/input`, handled exactly like the keyboard): hold W to accelerate,
C to engage cruise control, S to brake, I to withhold the
vehicle-speed signal. Every expected reaction is observed on the vehicle network (Zenoh)
and over SOVD; nothing is taken from a witness statement.

Run while `run_autoverse.py --enable-camera-display --vcu-zenoh` is up. Before each driving
case the ego vehicle is placed, stopped, at the start of the longest straight lane of the
CARLA map (setup through the CARLA API); it accelerates to about 18 km/h and brakes to a stop:

    python3 aspice/tools/qualification_check.py [--out results.json] [--case QTC-03]

Exits non-zero when a test case fails. See swe6-qualification-test/qualification-test.md.
"""
import argparse
import json
import socket
import sys
import threading
import time
import urllib.request
from pathlib import Path

ZENOH = "tcp/127.0.0.1:7447"
SOVD = "http://127.0.0.1:7691/sovd/v1/components/cruise_control/data"
CONSOLE = "http://127.0.0.1:8080"
INPUT_KEY = "test/manual_control/input"
KEYS = {
    "speed": "vehicle/status/velocity_status",
    "cc": "vcu/control/cc_engage_sts",
    "brake": "vcu/control/brake_sts",
    "throttle": "vcu/control/throttle_cmd",
    "cancel": "adas/cruise_control/cancel_req",
    "target": "adas/cruise_control/target_speed",
}
CARLA = ("127.0.0.1", 2000)
MIN_CC_SPEED = 10.0      # km/h, VCU engagement threshold (vecu/vcu_zenoh/src/config.py)
DRIVE_SPEED = 18.0       # km/h reached before engaging cruise control

results = []


class Fail(Exception):
    """A step's expected reaction did not happen."""


# ---------------------------------------------------------------- vehicle network

class Vehicle:
    """Observes the vehicle network and presses keys of Vehicle Manual Control."""

    def __init__(self):
        import zenoh
        conf = zenoh.Config()
        conf.insert_json5("mode", '"client"')
        conf.insert_json5("connect/endpoints", json.dumps([ZENOH]))
        self.session = zenoh.open(conf)
        self.lock = threading.Lock()
        self.last = {}      # name -> (value text, monotonic time)
        self.events = []    # (monotonic time, name, value text) for edge checks
        self.subs = [self.session.declare_subscriber(key, self._cb(name)) for name, key in KEYS.items()]
        self.pub = self.session.declare_publisher(INPUT_KEY)
        self.held = set()
        self._hold_stop = threading.Event()
        self._hold_thread = threading.Thread(target=self._refresh_holds, daemon=True)
        self._hold_thread.start()

    def _cb(self, name):
        def on_sample(sample):
            text = sample.payload.to_string().strip()
            now = time.monotonic()
            with self.lock:
                self.last[name] = (text, now)
                if name != "speed":
                    self.events.append((now, name, text))
        return on_sample

    def _refresh_holds(self):
        # A held key auto-releases in Manual Control after 1.5 s without refresh.
        while not self._hold_stop.wait(0.3):
            for key in list(self.held):
                self.pub.put(f"down {key}")

    # -- inputs
    def tap(self, key):
        self.pub.put(f"tap {key}")

    def hold(self, key):
        self.held.add(key)
        self.pub.put(f"down {key}")

    def release(self, key=None):
        for k in ([key] if key else list(self.held)):
            self.held.discard(k)
            self.pub.put(f"up {k}")

    # -- observations
    def value(self, name):
        with self.lock:
            item = self.last.get(name)
        return item[0] if item else None

    def age(self, name):
        with self.lock:
            item = self.last.get(name)
        return time.monotonic() - item[1] if item else float("inf")

    def speed(self):
        v = self.value("speed")
        return float(v) if v is not None else None

    def flag(self, name):
        v = self.value(name)
        return None if v is None else v.lower() in ("1", "true", "on", "1.0")

    def seen_since(self, since, name, values):
        with self.lock:
            return [t for t, n, v in self.events if t >= since and n == name and v.lower() in values]

    def close(self):
        self._hold_stop.set()
        self.release()
        time.sleep(0.2)
        self.session.close()


def wait_for(what, cond, timeout, poll=0.05):
    """Wait until cond() is truthy; return (value, seconds) or raise Fail."""
    start = time.monotonic()
    while True:
        value = cond()
        if value:
            return value, time.monotonic() - start
        if time.monotonic() - start > timeout:
            raise Fail(f"{what} not within {timeout:.0f} s")
        time.sleep(poll)


def sovd(item):
    with urllib.request.urlopen(f"{SOVD}/{item}", timeout=3) as resp:
        return json.load(resp)["data"]


def console(path, data=None):
    req = urllib.request.Request(f"{CONSOLE}{path}", method="POST" if data is not None else "GET",
                                 data=json.dumps(data).encode() if data is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.load(resp)


# ---------------------------------------------------------------- shared steps

def place_on_straight_lane(steps, min_length=150.0):
    """Test setup: put the ego vehicle, stopped, at the start of the longest straight lane."""
    import carla
    client = carla.Client(*CARLA)
    client.set_timeout(20)
    world = client.get_world()
    cmap = world.get_map()
    egos = [a for a in world.get_actors().filter("vehicle.*") if a.attributes.get("role_name") == "ego_vehicle"]
    if not egos:
        raise Fail("no CARLA ego_vehicle")

    def straight_length(wp, step=2.0, limit=300.0):
        yaw0, length = wp.transform.rotation.yaw, 0.0
        while length < limit:
            nxt = wp.next(step)
            if not nxt or abs((nxt[0].transform.rotation.yaw - yaw0 + 180) % 360 - 180) > 4:
                break
            wp, length = nxt[0], length + step
        return length

    ego = egos[0]
    length, index, spawn = max(((straight_length(cmap.get_waypoint(sp.location)), i, sp)
                                for i, sp in enumerate(cmap.get_spawn_points())), key=lambda r: (r[0], -r[1]))
    if length < min_length:
        raise Fail(f"no straight lane of {min_length:.0f} m on {cmap.name}")
    ego.set_target_velocity(carla.Vector3D())
    ego.set_target_angular_velocity(carla.Vector3D())
    spawn.location.z += 0.3
    ego.set_transform(spawn)
    time.sleep(2.0)
    steps.append(f"ego placed on spawn point {index} of {cmap.name.split('/')[-1]} ({length:.0f} m straight lane)")

def precondition(v, steps):
    wait_for("vehicle speed samples on Zenoh", lambda: v.age("speed") < 0.5, 10)
    # The VCU publishes cc_engage_sts only on change: nothing seen yet means not engaged.
    # The scripted input channel must be live in Manual Control: a short S press
    # must make the VCU report braking.
    v.hold("s")
    try:
        wait_for("VCU brake status from a scripted S press (is Manual Control running with the "
                 "scripted input channel?)", lambda: v.flag("brake"), 5)
    finally:
        v.release("s")
    if v.flag("cc"):
        stop(v, steps)
    steps.append("vehicle network live, scripted input channel answers, cruise control off")


def drive_and_engage(v, steps):
    start = v.speed()
    v.hold("w")
    try:
        speed, secs = wait_for(f"speed ≥ {DRIVE_SPEED} km/h with W held",
                               lambda: (v.speed() or 0) >= DRIVE_SPEED and v.speed(), 40)
    finally:
        v.release("w")
    steps.append(f"W held: {start:.1f} → {speed:.1f} km/h in {secs:.1f} s")
    # Like a driver: let go of the pedal, coast a moment, then press C.
    time.sleep(1.0)
    if v.speed() < MIN_CC_SPEED:
        raise Fail(f"speed fell to {v.speed():.1f} km/h before engaging")
    v.tap("c")
    _, secs = wait_for("VCU cc_engage_sts = 1 after C", lambda: v.flag("cc"), 5)
    state, secs2 = wait_for("S-CORE cruise_state active over SOVD",
                            lambda: (lambda d: d if d.get("state") == "active" else None)(sovd("cruise_state")), 5)
    steps.append(f"C: VCU engaged after {secs:.2f} s; S-CORE active, set speed {state['set_speed']:.1f} km/h")
    return state["set_speed"]


def stop(v, steps):
    v.hold("s")
    try:
        _, secs = wait_for("VCU cc_engage_sts = 0 while braking", lambda: v.flag("cc") is False, 5)
        wait_for("vehicle stopped", lambda: (v.speed() or 0) < 1.0, 40)
    finally:
        v.release("s")
    steps.append(f"S: cruise control disengaged after {secs:.2f} s, vehicle stopped")


# ---------------------------------------------------------------- test cases

def qtc02(v):
    """Drive and cruise control: accelerate, engage, hold the speed, brake.

    The set-speed keys (Z / X) are not part of this use case and are not tested
    (known defect, see qualification-test.md)."""
    steps = []
    precondition(v, steps)
    place_on_straight_lane(steps)
    set_speed = drive_and_engage(v, steps)
    # Cruise control drives on its own (no pedal pressed): sample the speed for 8 s.
    wait_for("VCU throttle command > 0 under cruise control",
             lambda: float(v.value("throttle") or 0) > 0 and v.flag("cc"), 5)
    samples, t0 = [], time.monotonic()
    while time.monotonic() - t0 < 8.0:
        samples.append(v.speed())
        if not v.flag("cc"):
            raise Fail("cruise control dropped while holding speed")
        time.sleep(0.1)
    # A simple cruise control: it keeps the vehicle moving on its own; regulation accuracy
    # is not part of the use case.
    low, high = min(samples), max(samples)
    if low < 5.0:
        raise Fail(f"vehicle slowed to {low:.1f} km/h under cruise control (set {set_speed:.1f} km/h)")
    steps.append(f"cruise control keeps the vehicle moving at {low:.1f}..{high:.1f} km/h for 8 s "
                 f"(set {set_speed:.1f}) without pedal")
    stop(v, steps)
    return True, steps


def qtc03(v):
    """Lost speed signal: cruise cancels, VCU disengages, DTC fails; restored: DTC passes."""
    steps = []
    precondition(v, steps)
    dtc = sovd("cc_lost_communication")
    if dtc["status"] != "passed":
        raise Fail(f"DTC {dtc['fault']} is {dtc['status']} before the fault")
    place_on_straight_lane(steps)
    drive_and_engage(v, steps)
    inhibited = False
    try:
        t0 = time.monotonic()
        v.tap("i")
        inhibited = True
        wait_for("vehicle speed samples stop after I", lambda: v.age("speed") > 0.5, 5)
        steps.append("I: vehicle speed no longer published")
        d, secs = wait_for("DTC CC.LostCommunication failed and confirmed over SOVD",
                           lambda: (lambda d: d if d["status"] == "failed" and d["confirmed"] else None)(
                               sovd("cc_lost_communication")), 10)
        steps.append(f"DTC {d['fault']} failed (confirmed) {time.monotonic() - t0:.2f} s after I")
        wait_for("ADAS cancel request on Zenoh", lambda: v.seen_since(t0, "cancel", ("1", "true")), 10)
        _, secs = wait_for("VCU cc_engage_sts = 0 (disengaged by the cancel request)",
                           lambda: v.flag("cc") is False, 10)
        st = sovd("cruise_state")
        if st["state"] != "standby":
            raise Fail(f"S-CORE cruise_state {st['state']} after the cancel, expected standby")
        steps.append(f"cancel request sent, VCU disengaged {time.monotonic() - t0:.2f} s after I, S-CORE standby")
        t1 = time.monotonic()
        v.tap("i")
        inhibited = False
        wait_for("vehicle speed samples resume after I", lambda: v.age("speed") < 0.3, 5)
        d, secs = wait_for("DTC CC.LostCommunication passed again over SOVD",
                           lambda: (lambda d: d if d["status"] == "passed" else None)(sovd("cc_lost_communication")), 10)
        steps.append(f"I again: speed restored, DTC passed {time.monotonic() - t1:.2f} s later")
    finally:
        if inhibited:
            v.tap("i")      # never leave the vehicle without its speed signal
    stop(v, steps)
    return True, steps


def qtc07(v):
    """Lost speed signal seen by the OpenSOVD vECU: console F2 (U0104) and the classic DTC via CDA."""
    steps = []
    precondition(v, steps)
    console("/api/reset", {})
    seq0 = console("/api/auto")["seq"]
    steps.append("console fault memory reset")
    inhibited = False
    try:
        t0 = time.monotonic()
        v.tap("i")
        inhibited = True
        f2 = lambda: next(f for f in faults() if f["code"] == "U0104")
        _, secs = wait_for("console F2 U0104 qualified failed", lambda: f2()["qualified_failed"], 10)
        steps.append(f"I: console U0104 (lost communication) qualified {time.monotonic() - t0:.2f} s after I")
        ev, _ = wait_for("classic DTC set in the ECU and read back through the CDA (0x2F)",
                         lambda: auto_event(seq0, "U0104", "2F"), 15)
        steps.append(f"ECU DTC {ev['dtc']} reads {ev['readback']} via CDA ({ev['readback_ms']} ms)")
        t1 = time.monotonic()
        v.tap("i")
        inhibited = False
        _, secs = wait_for("console U0104 qualified passed after the signal returns",
                           lambda: f2()["qualified_failed"] is False, 10)
        ev, _ = wait_for("classic DTC healed (0x28) through the CDA", lambda: auto_event(seq0, "U0104", "28"), 15)
        steps.append(f"I again: U0104 healed after {time.monotonic() - t1:.2f} s, ECU DTC {ev['dtc']} reads {ev['readback']}")
        if any(f["code"] == "P0500" and f["qualified_failed"] for f in faults()):
            raise Fail("P0500 (speed sensor) qualified although only the link was lost")
    finally:
        if inhibited:
            v.tap("i")
    return True, steps


def faults():
    return console("/api/faults")["items"]


def auto_event(seq0, fault, mask):
    data = console("/api/auto")
    for ev in data["events"]:
        if ev["seq"] > seq0 and ev.get("fault") == fault and str(ev.get("mask", "")).upper() == mask \
                and ev.get("ok"):
            return ev
    return None


CASES = {"QTC-02": ("Drive and cruise control", qtc02),
         "QTC-03": ("Lost speed signal", qtc03),
         "QTC-07": ("Lost speed signal seen by the OpenSOVD vECU", qtc07)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, help="write the results as JSON")
    parser.add_argument("--case", action="append", choices=sorted(CASES), help="run only these cases")
    args = parser.parse_args()
    v = Vehicle()
    try:
        for case_id in args.case or list(CASES):
            title, fn = CASES[case_id]
            started = time.time()
            try:
                ok, steps = fn(v)
                detail = "; ".join(steps)
            except Fail as exc:
                ok, detail = False, str(exc)
            except Exception as exc:  # a crashing case is a failed case
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            finally:
                v.release()
            results.append({"id": case_id, "title": title, "status": "PASS" if ok else "FAIL", "detail": detail,
                            "duration_s": round(time.time() - started, 1)})
            print(f"{case_id} {'PASS' if ok else 'FAIL'}  {title}  — {detail}", flush=True)
            time.sleep(2)
    finally:
        v.close()
    record = {"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "host": socket.gethostname(), "cases": results}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(record, indent=2) + "\n")
    failed = [r["id"] for r in results if r["status"] != "PASS"]
    print(f"{len(results) - len(failed)}/{len(results)} passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
