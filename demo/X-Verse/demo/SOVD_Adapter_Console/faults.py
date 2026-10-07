# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-07 · Latest version: 2026-10-07
# Goal: The tester's fault model: F1 from the gateway's fault status (fed through the injection switch), F2 from the console's link monitor.
"""Fault model of the tester (v2.1).

The gateway of PR #40 serves one fault, the speed sensor fault of `cruise.rs`, through the
data item `speed_sensor_fault_status` (stage passed / prefailed / failed / prepassed, a
time-based debounce) and lets a tester raise it through the writable item
`speed_sensor_stuck`. It has no faults resource (#156) and no link supervision. So:

  F1 (P0500)  the console observes the Zenoh samples (observer.py). Its qualified
              plausibility verdict is mirrored into the gateway's switch (the "bridge":
              PUT {"data": {"stuck": true|false}} on every change of the verdict), the
              gateway's own debounce qualifies the fault, and the fault the audience sees
              is read back from the gateway together with `cruise_state`.
  F2 (U0104)  lost communication: the console's link monitor, until the Rust diag-host
              gets a VehicleLink of its own. Not bridged (one switch, one fault).

Status byte shown for each fault (ISO 14229-1, simplified as stated on stage): bit 0
testFailed = the raw test result; bits 2+3 pendingDTC + confirmedDTC = the fault is or
was qualified failed since the last reset (stored). failed = 0x0D, prepassed = 0x0C,
passed after a failure = 0x0C, never failed = 0x00, prefailed before any failure = 0x01.
The classic DTC mirror (auto_dtc.py) follows the qualified result only.
"""
import threading
import time
from collections import deque

import config

STAGES = ("passed", "prefailed", "failed", "prepassed")
TEST_FAILED, PENDING, CONFIRMED = 0x01, 0x04, 0x08


def status_byte(test_failed, qualified_failed, stored):
    raw = TEST_FAILED if test_failed else 0
    if qualified_failed or stored:
        raw |= PENDING | CONFIRMED
    return raw


class TesterFault:
    """One fault as the tester tracks it: current stage plus memory since the last reset."""

    def __init__(self, code, display, source, monitor, severity=2):
        self.code, self.display, self.source, self.monitor, self.severity = code, display, source, monitor, severity
        self.stage = "passed"
        self.test_failed = False
        self.qualified_failed = False
        self.stored = False
        self.available = True        # False while the source cannot be read
        self.occurrences = 0
        self.first_failed = None     # wall clock of the first qualified failure since reset
        self.last_change = None
        self.extra = {}

    def update(self, stage, test_failed, wall, available=True, extra=None):
        stage = stage if stage in STAGES else "passed"
        qualified = stage in ("failed", "prepassed")
        changed = stage != self.stage or available != self.available or test_failed != self.test_failed
        if qualified and not self.qualified_failed:
            self.occurrences += 1
            self.stored = True
            self.first_failed = self.first_failed or wall
        self.stage, self.test_failed, self.qualified_failed, self.available = stage, bool(test_failed), qualified, available
        if changed:
            self.last_change = wall
        self.extra = dict(extra or {})

    def clear(self, wall):
        """ClearDiagnosticInformation: forget history; a fault failing right now stays failing."""
        self.stored = self.qualified_failed
        self.occurrences = 1 if self.qualified_failed else 0
        self.first_failed = wall if self.qualified_failed else None
        self.last_change = wall

    def status(self):
        return status_byte(self.test_failed, self.qualified_failed, self.stored)

    def view(self):
        return {"code": self.code, "display": self.display, "source": self.source, "monitor": self.monitor,
                "severity": self.severity, "stage": self.stage, "test_failed": self.test_failed,
                "qualified_failed": self.qualified_failed, "stored": self.stored, "available": self.available,
                "status": self.status(), "occurrences": self.occurrences, "first_failed": self.first_failed,
                "last_change": self.last_change, **self.extra}


def settings_from_config():
    return {"f1_code": config.F1_CODE, "f2_code": config.F2_CODE, "items": config.sovd_items(),
            "component": config.SOVD_COMPONENT, "bridge": config.FAULT_BRIDGE, "retry_s": 2.0}


class FaultModel:
    """Polls the gateway, composes the two faults, runs the bridge. One lock; the HTTP calls
    happen outside it."""

    def __init__(self, backends, observer, settings=None, clock=time.monotonic, wall=time.time):
        s = settings or settings_from_config()
        self.b, self.obs, self.clock, self.wall = backends, observer, clock, wall
        self.items, self.component = dict(s["items"]), s["component"]
        self.retry_s = float(s.get("retry_s", 2.0))
        self.lock = threading.Lock()
        self.f1 = TesterFault(s["f1_code"], "Vehicle speed sensor fault",
                              f"sovd:{self.component}/{self.items['fault']}",
                              "gateway debounce (TimeBased), fed by the console's F1 plausibility verdict")
        self.f2 = TesterFault(s["f2_code"], "Lost communication with cruise control module",
                              "console:vehicle link", "timeout")
        self.gateway = {"reachable": None, "error": None, "component": self.component, "items": {},
                        "last_poll": None, "polls": 0}
        self.bridge = {"enabled": bool(s.get("bridge", True)), "item": self.items["switch"], "wanted": None,
                       "last_wanted": None, "pending": None, "sent": None, "sent_at": None, "gateway_stuck": None,
                       "in_sync": None, "retry_at": 0.0, "writes": 0, "failures": 0, "last_error": None,
                       "events": deque(maxlen=50), "seq": 0}

    # ------------------------------------------------------------ one cycle
    def poll(self):
        """Read the four items, update F1 from the gateway and F2 from the observer, run the bridge."""
        wall, now = self.wall(), self.clock()
        items, errors = {}, []
        for role in ("fault", "state", "speed", "switch"):
            r, d = self.b.sovd_read(self.items[role], origin="console")
            if r.ok and isinstance(d, dict):
                items[role] = {"data": d, "ms": r.ms}
            else:
                errors.append(f"{self.items[role]}: {r.problem() or 'no data'}")
        reachable = "fault" in items
        v = self.obs.verdicts()
        with self.lock:
            self.gateway.update(reachable=reachable, error="; ".join(errors) or None, items=items,
                                last_poll=wall, polls=self.gateway["polls"] + 1)
            extra = {"console_f1": v["f1_state"], "console_reason": v["f1_reason"]}
            if reachable:
                fd = items["fault"]["data"]
                extra.update(fault_name=fd.get("fault"), confirmed=bool(fd.get("confirmed")),
                             cruise_state=(items.get("state", {}).get("data") or {}).get("state"))
                self.f1.update(fd.get("status"), fd.get("test_failed"), wall, True, extra)
            else:
                extra.update(fault_name=self.f1.extra.get("fault_name"), cruise_state=None)
                self.f1.update(self.f1.stage, self.f1.test_failed, wall, False, extra)
            self.f2.update("failed" if v["f2_failed"] else "passed", v["f2_failed"], wall, True, {"armed": v["f2_armed"]})
        switch = (items.get("switch") or {}).get("data")
        self._bridge(bool(v["f1_failed"]), switch.get("stuck") if isinstance(switch, dict) else None, reachable, now, wall)

    def _bridge(self, wanted, gateway_stuck, reachable, now, wall):
        br = self.bridge
        with self.lock:
            br["wanted"], br["gateway_stuck"] = wanted, gateway_stuck
            br["in_sync"] = None if gateway_stuck is None else (gateway_stuck == wanted)
            if not br["enabled"]:
                return
            if br["last_wanted"] is None:
                if wanted:                                   # faulty from the start: tell the gateway
                    br["pending"] = True
            elif wanted != br["last_wanted"]:                # the verdict changed: an edge
                br["pending"] = wanted
            br["last_wanted"] = wanted
            if br["pending"] is None and wanted and gateway_stuck is False:
                br["pending"] = True                         # lost (gateway restarted): re-assert
            if br["pending"] is None or not reachable or now < br["retry_at"]:
                return
            value, reason = br["pending"], ("edge" if br["pending"] != br["sent"] else "re-assert")
        r = self.b.sovd_write(self.items["switch"], {"stuck": value}, origin="bridge")
        with self.lock:
            br["writes"] += 1
            br["seq"] += 1
            br["events"].append({"seq": br["seq"], "t": wall, "stuck": value, "reason": reason, "status": r.status,
                                 "ms": r.ms, "ok": r.ok, "error": r.problem()})
            if r.ok:
                br["sent"], br["sent_at"], br["pending"], br["retry_at"], br["last_error"] = value, wall, None, 0.0, None
            else:
                br["failures"] += 1
                br["last_error"], br["retry_at"] = r.problem(), now + self.retry_s

    # ------------------------------------------------------------ actions
    def set_switch(self, stuck, origin="page"):
        """Direct, test-only write of the gateway's injection switch (what the integration
        test of PR #40 does). The bridge keeps following the console's verdict: it only
        writes again when that verdict changes, or to re-assert a failing verdict."""
        r = self.b.sovd_write(self.items["switch"], {"stuck": bool(stuck)}, origin=origin)
        with self.lock:
            br = self.bridge
            br["seq"] += 1
            br["events"].append({"seq": br["seq"], "t": self.wall(), "stuck": bool(stuck), "reason": origin,
                                 "status": r.status, "ms": r.ms, "ok": r.ok, "error": r.problem()})
        return r

    def reset(self):
        """Forget the fault memory; put the switch back to the console's verdict (false unless
        the vehicle is faulty right now)."""
        wall = self.wall()
        with self.lock:
            self.f1.clear(wall)
            self.f2.clear(wall)
        wanted = bool(self.obs.verdicts()["f1_failed"])
        r = self.b.sovd_write(self.items["switch"], {"stuck": wanted}, origin="reset")
        with self.lock:
            br = self.bridge
            br["last_wanted"], br["pending"], br["retry_at"] = wanted, None, 0.0
            if r.ok:
                br["sent"], br["sent_at"], br["last_error"] = wanted, wall, None
            br["seq"] += 1
            br["events"].append({"seq": br["seq"], "t": wall, "stuck": wanted, "reason": "reset", "status": r.status,
                                 "ms": r.ms, "ok": r.ok, "error": r.problem()})
        return r

    # ------------------------------------------------------------ views
    def faults_view(self):
        with self.lock:
            return [self.f1.view(), self.f2.view()]

    def gateway_view(self):
        with self.lock:
            g = dict(self.gateway)
            g["items"] = {role: dict(v) for role, v in self.gateway["items"].items()}
            br = {k: v for k, v in self.bridge.items() if k != "events"}
            br["events"] = list(self.bridge["events"])
            g["bridge"] = br
            return g
