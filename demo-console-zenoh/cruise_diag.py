# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Diagnostic logic of the stand-in: F1 speed plausibility and F2 lost-communication monitors, and the fault store.
"""Diagnostic logic of the cruise diag stand-in: two monitors and a small fault store.

No I/O, no threads, clock injected: everything here is deterministic and unit-tested.

F1 (P0500, entity cruise-control) - speed plausibility, counter-based debounce:
    every received sample is a test result: passing if it decodes to a finite value
    inside [min, max] km/h, failing otherwise. Failing adds 1 to the counter, passing
    removes 1 (bounded 0..threshold). FAILED is qualified at the threshold, PASSED when
    the counter is back at 0; PREFAILED / PREPASSED in between keep the last qualified
    result. F1 is only evaluated on samples, so a silent link does not touch it
    (one owner per fault: silence belongs to F2).

F2 (U0104, entity cruise-diag) - lost communication with the cruise control module:
    armed after the first valid sample; failing while no sample arrived for longer
    than the timeout; passing again with the next sample.

Status byte (ISO 14229-1), simplified as stated on stage: when a fault is qualified
failing, testFailed + pendingDTC + confirmedDTC are set (0x0D); when it heals only
testFailed is cleared (0x0C: the fault stays stored until cleared).
"""
import math
import threading

TEST_FAILED, PENDING, CONFIRMED = 0x01, 0x04, 0x08
QUALIFIED_FAILED = TEST_FAILED | PENDING | CONFIRMED


class Fault:
    def __init__(self, code, display, entity, monitor, severity=2):
        self.code, self.display, self.entity, self.monitor, self.severity = code, display, entity, monitor, severity
        self.status = 0x00
        self.occurrences = 0
        self.first_failed = None   # wall clock of the first qualified failure since clear
        self.last_change = None

    def set_failing(self, failing, wall):
        before = self.status
        if failing:
            if not self.status & TEST_FAILED:
                self.occurrences += 1
                self.first_failed = self.first_failed or wall
            self.status |= QUALIFIED_FAILED
        else:
            self.status &= ~TEST_FAILED & 0xFF
        if self.status != before:
            self.last_change = wall

    def clear(self, still_failing, wall):
        """ClearDiagnosticInformation: forget history; a fault failing right now stays failing."""
        self.status = QUALIFIED_FAILED if still_failing else 0x00
        self.occurrences = 1 if still_failing else 0
        self.first_failed = wall if still_failing else None
        self.last_change = wall

    def view(self):
        return {"code": self.code, "display": self.display, "status": self.status, "severity": self.severity,
                "monitor": self.monitor, "occurrences": self.occurrences,
                "first_failed": self.first_failed, "last_change": self.last_change}


class PlausibilityMonitor:
    """F1: counter-based debounce over per-sample plausibility results."""

    def __init__(self, threshold, vmin, vmax):
        self.threshold, self.vmin, self.vmax = max(1, int(threshold)), vmin, vmax
        self.counter = 0
        self.state = "PASSED"
        self.failed = False          # last qualified result
        self.last_reason = None

    def check(self, value_kmh, error):
        if error:
            return False, error
        if value_kmh is None or not math.isfinite(value_kmh):
            return False, "not a finite number"
        if not self.vmin <= value_kmh <= self.vmax:
            return False, f"outside {self.vmin:g}..{self.vmax:g} km/h"
        return True, None

    def report(self, passing):
        if passing:
            self.counter = max(0, self.counter - 1)
        else:
            self.counter = min(self.threshold, self.counter + 1)
        if self.counter >= self.threshold:
            self.failed, self.state = True, "FAILED"
        elif self.counter == 0:
            self.failed, self.state = False, "PASSED"
        else:
            self.state = "PREPASSED" if passing else "PREFAILED"
        return self.failed


class LinkMonitor:
    """F2: timeout supervision of the sample stream, armed after the first valid sample."""

    def __init__(self, timeout_s):
        self.timeout_s = timeout_s
        self.armed = False
        self.failed = False
        self.last_sample = None      # monotonic time

    def on_sample(self, t_mono, valid):
        self.last_sample = t_mono
        if valid:
            self.armed = True

    def tick(self, now):
        if self.armed and self.last_sample is not None:
            self.failed = (now - self.last_sample) > self.timeout_s
        return self.failed


class CruiseDiag:
    """Feeds the monitors from a VehicleLink and exposes SOVD-shaped snapshots."""

    def __init__(self, link, settings, clock, wall):
        s = settings
        self.link, self.clock, self.wall = link, clock, wall
        self.lock = threading.Lock()
        self.f1 = PlausibilityMonitor(s["f1_threshold"], s["speed_min"], s["speed_max"])
        self.f2 = LinkMonitor(s["link_timeout_s"])
        self.faults = {
            s["f1_code"]: Fault(s["f1_code"], "Vehicle speed signal implausible (observer check)",
                                s["entity"], "plausibility"),
            s["f2_code"]: Fault(s["f2_code"], "Lost communication with cruise control module",
                                s["diag_entity"], "timeout"),
        }
        self.f1_code, self.f2_code = s["f1_code"], s["f2_code"]
        self.entity, self.diag_entity = s["entity"], s["diag_entity"]
        self.speed = None            # last valid value, km/h
        self.speed_wall = None       # wall clock of that sample
        self.speed_mono = None
        self.sample_valid = None     # validity of the very last sample
        self.processed = 0

    def tick(self):
        """One monitor cycle: evaluate new samples (F1), then the timeout (F2)."""
        samples = self.link.drain()
        now, wall = self.clock(), self.wall()
        with self.lock:
            for smp in samples:
                passing, reason = self.f1.check(smp.value_kmh, smp.error)
                failed = self.f1.report(passing)
                self.f1.last_reason = reason
                self.faults[self.f1_code].set_failing(failed, smp.t_wall)
                self.f2.on_sample(smp.t_mono, passing)
                self.sample_valid = passing
                if passing:
                    self.speed, self.speed_wall, self.speed_mono = smp.value_kmh, smp.t_wall, smp.t_mono
                self.processed += 1
            self.faults[self.f2_code].set_failing(self.f2.tick(now), wall)

    # ------------------------------------------------------------ SOVD views
    def speed_view(self):
        now = self.clock()
        with self.lock:
            age = None if self.speed_mono is None else (now - self.speed_mono)
            stale = age is None or age > self.f2.timeout_s
            return {"value": None if self.speed is None else round(self.speed, 2), "unit": "km/h",
                    "ts": self.speed_wall, "age_ms": None if age is None else round(age * 1000),
                    "stale": stale, "last_sample_valid": self.sample_valid,
                    "source": f"zenoh:{self.link.key}"}

    def debounce_view(self):
        with self.lock:
            return {"state": self.f1.state, "counter": self.f1.counter, "threshold": self.f1.threshold,
                    "monitor": "plausibility", "range_kmh": [self.f1.vmin, self.f1.vmax],
                    "last_reason": self.f1.last_reason, "fault": self.f1_code}

    def faults_view(self, entity):
        with self.lock:
            return [f.view() for f in self.faults.values() if f.entity == entity]

    def clear_faults(self, entity):
        wall = self.wall()
        with self.lock:
            for f in self.faults.values():
                if f.entity == entity:
                    still = self.f1.failed if f.code == self.f1_code else self.f2.failed
                    f.clear(still, wall)

    def link_view(self):
        view = self.link.status(self.f2.timeout_s)
        with self.lock:
            view["monitor_armed"] = self.f2.armed
            view["fault"] = self.f2_code
        return view
