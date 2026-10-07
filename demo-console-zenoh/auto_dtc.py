# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: follows the tester's fault model instead of SOVD fault lists)
# Goal: Test harness: mirrors each qualified fault into the classic ECU simulator as a DTC and reads it back via the CDA.
"""Automatic classic DTC (test harness): when a fault is qualified failed, the classic ECU
stores a matching DTC and the tester reads it back through the CDA.

    fault qualified failed  (stage failed)        ->  ECU simulator: DTC = MASK_ACTIVE (0x2F)
    fault qualified passed  (stage passed again)  ->  ECU simulator: DTC = MASK_HEALED (0x28)
    each change is then read back through the CDA (UDS over DoIP) and timed.

v2.1: the faults come from the tester's fault model (faults.py): F1 is the gateway's
debounced fault status, F2 the console's link monitor. A fault whose source cannot be
read (gateway down) is skipped, so no edge is invented from missing data.

This uses the simulator's control API, which is test-only, so it lives in the console
(the tester), not in the vehicle computer. Edges only: a fault that stays failing is not
re-injected; after a reset everything is evaluated afresh.
"""
import threading
import time
from collections import deque

from backends import decode_status, find_fault, norm_code


class AutoDtc:
    def __init__(self, backends, mapping, faults_source, mask_active="2F", mask_healed="28",
                 period_s=0.5, readback_s=3.0, enabled=True):
        self.b, self.faults_source = backends, faults_source
        self.mask_active, self.mask_healed = mask_active.upper(), mask_healed.upper()
        self.period_s, self.readback_s, self.enabled = period_s, readback_s, enabled
        self.map = dict(mapping)
        self._lock = threading.Lock()
        self.state = {code: {"dtc": dtc, "failing": None, "ecu_mask": None, "display": None, "retry_at": 0}
                      for code, dtc in mapping.items()}
        self.events = deque(maxlen=50)
        self.seq = 0
        self.error = None
        self.polls = 0
        self.last_poll = None
        self._stop = threading.Event()
        self._thread = None

    # ------------------------------------------------------------ loop
    def start(self):
        if not self.enabled or self._thread:
            return

        def loop():
            while not self._stop.is_set():
                try:
                    self.poll_once()
                except Exception as e:  # the automation must never die
                    self.error = f"{type(e).__name__}: {e}"[:200]
                self._stop.wait(self.period_s)
        self._thread = threading.Thread(target=loop, name="auto-dtc", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def poll_once(self):
        items = list(self.faults_source() or [])
        self.polls += 1
        self.last_poll = time.time()
        unavailable = [f["code"] for f in items if not f.get("available", True)]
        self.error = ("source not readable: " + ", ".join(unavailable)) if unavailable else None
        now = time.time()
        for code, st in self.state.items():
            f = find_fault(items, code)
            if f is None or not f.get("available", True):
                continue
            failing = bool(f.get("qualified_failed"))
            with self._lock:
                prev = st["failing"]
                st["display"] = f.get("display")
                waiting = now < st.get("retry_at", 0)
            if waiting:
                continue
            change = "failing" if failing and prev is not True else "healed" if not failing and prev is True else None
            ok = True
            if change:
                ok = self._apply(code, st, self.mask_active if change == "failing" else self.mask_healed, change)
            with self._lock:
                if ok:
                    st["failing"], st["retry_at"] = failing, 0
                else:
                    st["retry_at"] = now + 5.0   # keep the edge, try again later

    # ------------------------------------------------------------ one change
    def _apply(self, code, st, mask, change):
        dtc = st["dtc"]
        ev = {"fault": code, "display": st["display"], "change": change, "dtc": dtc, "mask": mask}
        t0 = time.perf_counter()
        r = self.b.sim_set(dtc, mask, origin="auto")
        ev["put_status"] = r.status
        if not r.ok:
            ev.update(ok=False, error=r.error or f"simulator answered HTTP {r.status}")
            self._record(ev)
            return False
        want = int(mask, 16)
        got = None
        deadline = time.perf_counter() + self.readback_s
        while time.perf_counter() < deadline:
            rr, items = self.b.cda_faults(origin="auto")
            if rr.ok:
                f = find_fault(items, dtc)
                got = decode_status(f.get("status"))["raw"] if f else None
                if got == want:
                    break
            time.sleep(0.15)
        ev["readback_ms"] = round((time.perf_counter() - t0) * 1000)
        ev["readback"] = None if got is None else f"0x{got:02X}"
        ev["ok"] = got == want
        if not ev["ok"]:
            ev["error"] = f"CDA shows {ev['readback'] or 'no entry'} for {dtc}, expected 0x{mask}"
        with self._lock:
            st["ecu_mask"] = mask if ev["ok"] else st["ecu_mask"]
        self._record(ev)
        # The PUT was accepted: the edge is done even if the read-back was slow (the event says so).
        return True

    def _record(self, ev):
        with self._lock:
            self.seq += 1
            ev["seq"], ev["t"] = self.seq, time.time()
            self.events.append(ev)

    # ------------------------------------------------------------ control and view
    def reset(self):
        """Forget the observed states (after the faults and the ECU memory were cleared)."""
        with self._lock:
            for st in self.state.values():
                st["failing"], st["ecu_mask"], st["retry_at"] = None, None, 0
        self._record({"change": "reset", "ok": True, "fault": None, "dtc": None, "mask": None})

    def status(self):
        with self._lock:
            return {"enabled": self.enabled, "running": bool(self._thread and self._thread.is_alive()),
                    "map": self.map, "mask_active": self.mask_active, "mask_healed": self.mask_healed,
                    "state": {k: dict(v) for k, v in self.state.items()},
                    "events": list(self.events), "seq": self.seq,
                    "polls": self.polls, "last_poll": self.last_poll, "error": self.error}

    def owns(self, dtc):
        return any(norm_code(d) == norm_code(dtc) for d in self.map.values())
