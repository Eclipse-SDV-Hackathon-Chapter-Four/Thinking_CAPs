# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Vehicle input over Eclipse Zenoh: subscribes to the speed key, decodes samples, keeps link statistics.
"""Vehicle input over Eclipse Zenoh: subscribe to the speed key, decode each sample,
keep link statistics (connected, rate, age).

The virtual vehicle publishes a float32 as text, for example b"96.4", on
`vehicle/status/velocity_status`. Decoding never raises: an undecodable payload is
kept as an invalid sample, so the F1 plausibility monitor can count it.

The zenoh callback only parses and appends under a lock; the diagnostic logic
(cruise_diag.py) drains the samples on its own cycle. Tests call feed() directly.
"""
import json
import math
import struct
import threading
import time
from collections import deque


class SpeedSample:
    __slots__ = ("t_mono", "t_wall", "raw", "value_kmh", "error")

    def __init__(self, t_mono, t_wall, raw, value_kmh, error):
        self.t_mono, self.t_wall, self.raw, self.value_kmh, self.error = t_mono, t_wall, raw, value_kmh, error


def decode_speed(payload, factor=1.0):
    """bytes -> (value_kmh or None, printable raw text, error or None).

    Accepted: a text float ("96.4", " 9.64e1\\n", "96.4\\0"); as a fallback a 4-byte
    little-endian float32 that is not valid text. "nan"/"inf" decode to a number and
    are rejected later by the plausibility check, like any out-of-range value.
    """
    data = bytes(payload or b"")
    try:
        text = data.decode("utf-8").strip().strip("\x00").strip()
    except UnicodeDecodeError:
        text = None
    if text is not None and text != "":
        try:
            return float(text) * factor, text[:40], None
        except ValueError:
            return None, text[:40], "not a number"
    if len(data) == 4:
        value = struct.unpack("<f", data)[0]
        return value * factor, "float32 " + data.hex(), None
    return None, data[:20].hex() or "(empty)", "empty payload" if not data else "not a float32 string"


class VehicleLink:
    """Thread-safe store of received samples plus link statistics."""

    RATE_WINDOW_S = 2.0

    def __init__(self, key, factor=1.0, endpoints=(), clock=time.monotonic, wall=time.time, max_pending=2000):
        self.key, self.factor, self.endpoints = key, factor, list(endpoints)
        self.clock, self.wall = clock, wall
        self._lock = threading.Lock()
        self._pending = deque(maxlen=max_pending)    # drained by the diagnostic cycle
        self._recent = deque()                       # receive times for the rate
        self._last = None                            # last SpeedSample
        self.samples = 0
        self.invalid = 0
        self.session = None
        self._subscriber = None
        self.error = None                            # set when zenoh cannot start
        self._peers = (0.0, 0, 0)                     # (checked_at, peers, routers)
        self._options = ("peer", [], True)           # mode, listen, multicast scouting of the last start()

    # ------------------------------------------------------------ input
    def feed(self, payload):
        """Called for every received payload (zenoh thread or tests)."""
        now, wall = self.clock(), self.wall()
        value, raw, error = decode_speed(payload, self.factor)
        sample = SpeedSample(now, wall, raw, value, error)
        with self._lock:
            self.samples += 1
            if error:
                self.invalid += 1
            self._last = sample
            self._pending.append(sample)
            self._recent.append(now)
            while self._recent and now - self._recent[0] > self.RATE_WINDOW_S:
                self._recent.popleft()

    def drain(self):
        """All samples received since the last call, oldest first."""
        with self._lock:
            out = list(self._pending)
            self._pending.clear()
        return out

    # ------------------------------------------------------------ zenoh
    def start(self, mode="peer", connect=(), listen=(), multicast_scouting=True):
        """Open a zenoh session and subscribe. Never raises: problems end up in .error."""
        self._options = (mode, list(listen), multicast_scouting)
        try:
            import zenoh
        except ImportError:
            self.error = "eclipse-zenoh is not installed (pip install -r requirements.txt)"
            return False
        try:
            zenoh.init_log_from_env_or("error")
            conf = zenoh.Config()
            conf.insert_json5("mode", json.dumps(mode))
            if connect:
                conf.insert_json5("connect/endpoints", json.dumps(list(connect)))
            if listen:
                conf.insert_json5("listen/endpoints", json.dumps(list(listen)))
            conf.insert_json5("scouting/multicast/enabled", json.dumps(bool(multicast_scouting)))
            self.session = zenoh.open(conf)
            self._subscriber = self.session.declare_subscriber(self.key, lambda s: self.feed(s.payload.to_bytes()))
            self.endpoints = list(connect) or list(listen)
            self.error = None
            return True
        except Exception as e:  # bad endpoint syntax, version mismatch, ...
            self.error = f"zenoh: {type(e).__name__}: {e}"[:300]
            return False

    def reconnect(self, connect):
        """Re-open the session towards other endpoints (the vehicle restarted on new ports)."""
        self.stop()
        mode, listen, scouting = self._options
        return self.start(mode, connect, listen, scouting)

    def stop(self):
        try:
            if self._subscriber is not None:
                self._subscriber.undeclare()
            if self.session is not None:
                self.session.close()
        except Exception:
            pass
        self._subscriber = self.session = None

    def _peer_counts(self):
        """Connected zenoh peers/routers, re-read at most once per second."""
        now = self.clock()
        if self.session is None:
            return 0, 0
        if now - self._peers[0] >= 1.0:
            try:
                info = self.session.info
                self._peers = (now, len(list(info.peers_zid())), len(list(info.routers_zid())))
            except Exception:
                self._peers = (now, 0, 0)
        return self._peers[1], self._peers[2]

    # ------------------------------------------------------------ status
    def last(self):
        with self._lock:
            return self._last

    def status(self, timeout_s):
        """Link view for the SOVD link_status resource and the page."""
        now = self.clock()
        peers, routers = self._peer_counts()
        with self._lock:
            last = self._last
            while self._recent and now - self._recent[0] > self.RATE_WINDOW_S:
                self._recent.popleft()
            rate = len(self._recent) / self.RATE_WINDOW_S
            samples, invalid = self.samples, self.invalid
        age_ms = None if last is None else round((now - last.t_mono) * 1000)
        if self.error:
            state = "error"
        elif self.session is None and samples == 0:
            state = "no-session"
        elif last is None:
            state = "waiting" if (peers or routers) else "connecting"
        elif age_ms > timeout_s * 1000:
            state = "lost"
        else:
            state = "live"
        return {
            "state": state, "key": self.key, "endpoints": self.endpoints,
            "connected": bool(peers or routers), "peers": peers, "routers": routers,
            "samples": samples, "invalid_samples": invalid, "rate_hz": round(rate, 1),
            "age_ms": age_ms, "timeout_ms": round(timeout_s * 1000),
            "last_raw": None if last is None else last.raw,
            "last_value_kmh": None if last is None or last.value_kmh is None or not math.isfinite(last.value_kmh)
            else round(last.value_kmh, 2),
            "last_error": None if last is None else last.error,
            "error": self.error,
        }
