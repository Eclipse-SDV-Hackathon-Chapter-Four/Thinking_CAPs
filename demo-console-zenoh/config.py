# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: All settings of the console processes, read from environment variables with demo defaults.
"""Settings for every process of the v2 console: environment variables with demo defaults.

Nothing else hard-codes an address, a key, a code or a threshold. The page gets the
non-secret part through /api/config (see public()).
"""
import os


def _env(name, default):
    return os.environ.get(name, default)


def _bool(name, default):
    return _env(name, default).strip().lower() in ("1", "true", "yes", "on")


def _list(name, default):
    return [x.strip() for x in _env(name, default).split(",") if x.strip()]


VERSION = "2.0.0"

# ---------------------------------------------------------------- console (tester)
CONSOLE_HOST = _env("CONSOLE_HOST", "0.0.0.0")
CONSOLE_PORT = int(_env("CONSOLE_PORT", "8080"))
HTTP_TIMEOUT = float(_env("HTTP_TIMEOUT", "1.5"))          # seconds, per backend call

# ---------------------------------------------------------------- vehicle input (Zenoh)
# The virtual vehicle publishes the speed as a text float32 ("96.4") on this key.
# Its Zenoh peers listen on random ports: with VEHICLE_HOST set, the stand-in finds them
# by scouting (discover.py) and finds them again after a vehicle restart.
VEHICLE_HOST = _env("VEHICLE_HOST", "").strip()             # IP of the vehicle laptop
ZENOH_MODE = _env("ZENOH_MODE", "peer")                     # peer | client
ZENOH_CONNECT = _list("ZENOH_CONNECT", "" if VEHICLE_HOST else "tcp/127.0.0.1:7447")  # fixed endpoints
ZENOH_LISTEN = _list("ZENOH_LISTEN", "")                    # optional: let the vehicle connect to us
ZENOH_MULTICAST_SCOUTING = _bool("ZENOH_MULTICAST_SCOUTING", "true")
SPEED_KEY = _env("SPEED_KEY", "vehicle/status/velocity_status")
SPEED_UNIT = _env("SPEED_UNIT", "km/h")                     # km/h | m/s (converted to km/h)
SPEED_MIN_KMH = float(_env("SPEED_MIN_KMH", "0"))           # plausibility range of the F1 monitor
SPEED_MAX_KMH = float(_env("SPEED_MAX_KMH", "300"))

# ---------------------------------------------------------------- cruise diag stand-in (S-CORE side)
# Serves the SOVD-style API the console reads, until the real gateway with #156 runs.
STANDIN_HOST = _env("STANDIN_HOST", "0.0.0.0")
STANDIN_PORT = int(_env("STANDIN_PORT", "7690"))
DIAG_TICK_S = float(_env("DIAG_TICK_S", "0.1"))             # monitor cycle
LINK_TIMEOUT_MS = int(_env("LINK_TIMEOUT_MS", "500"))       # F2: no sample for longer than this
F1_THRESHOLD = int(_env("F1_THRESHOLD", "5"))               # F1: implausible samples to qualify FAILED
F1_CODE = _env("F1_CODE", "P0500")                          # SAE J2012: vehicle speed sensor "A"
F2_CODE = _env("F2_CODE", "U0104")                          # SAE J2012: lost communication with cruise control module
STATS_FILE = _env("STATS_FILE", "stats.json")

# ---------------------------------------------------------------- SOVD (stand-in today, real gateway later)
SOVD_URL = _env("SOVD_URL", f"http://127.0.0.1:{STANDIN_PORT}")
SOVD_BASE = _env("SOVD_BASE", "/sovd")
SOVD_ENTITY = _env("SOVD_ENTITY", "components/cruise-control")      # owns F1 and the speed
SOVD_DIAG_ENTITY = _env("SOVD_DIAG_ENTITY", "components/cruise-diag")  # owns F2 and the link status
SOVD_ITEM_SPEED = _env("SOVD_ITEM_SPEED", "vehicle_speed")
SOVD_ITEM_DEBOUNCE = _env("SOVD_ITEM_DEBOUNCE", "debounce")
SOVD_ITEM_LINK = _env("SOVD_ITEM_LINK", "link_status")

# ---------------------------------------------------------------- classic path (upstream, Docker)
CDA_URL = _env("CDA_URL", "http://127.0.0.1:20002")
CDA_BASE = _env("CDA_BASE", "/vehicle/v15")
CDA_ECU = _env("CDA_ECU", "flxc1000")
CDA_CLIENT_ID = _env("CDA_CLIENT_ID", "test_client")
CDA_CLIENT_SECRET = _env("CDA_CLIENT_SECRET", "test_secret")
CDA_TOKEN = _env("CDA_TOKEN", "")                            # optional: skip the token call
SIM_URL = _env("SIM_URL", "http://127.0.0.1:8181")
SIM_ECU = _env("SIM_ECU", "FLXC1000")
SIM_FAULT_MEMORY = _env("SIM_FAULT_MEMORY", "Standard")
DEMO_DTC = _env("DEMO_DTC", "01E240")                        # runner round trip; keep it outside AUTO_DTC_MAP
DEMO_DTC_MASK = _env("DEMO_DTC_MASK", "2F")

# ---------------------------------------------------------------- automatic classic DTC (test harness)
# When an S-CORE fault starts failing, the console puts the mapped DTC into the ECU
# simulator and reads it back through the CDA; when the fault heals, the DTC is kept as stored.
AUTO_DTC = _bool("AUTO_DTC", "true")
AUTO_DTC_MAP = _env("AUTO_DTC_MAP", "P0500=01E241,U0104=01E242")
AUTO_DTC_MASK_ACTIVE = _env("AUTO_DTC_MASK_ACTIVE", "2F")    # failing, this cycle, pending, confirmed, since clear
AUTO_DTC_MASK_HEALED = _env("AUTO_DTC_MASK_HEALED", "28")    # confirmed + failed since clear, no longer failing
AUTO_DTC_PERIOD_S = float(_env("AUTO_DTC_PERIOD_S", "0.5"))
AUTO_DTC_READBACK_S = float(_env("AUTO_DTC_READBACK_S", "3"))

# ---------------------------------------------------------------- Docker
DOCKER_CONTAINERS = _list("DOCKER_CONTAINERS", "cda,ecu-sim")


def speed_factor():
    """Factor from the published unit to km/h."""
    unit = SPEED_UNIT.strip().lower().replace(" ", "")
    if unit in ("km/h", "kmh", "kph"):
        return 1.0
    if unit in ("m/s", "mps"):
        return 3.6
    raise ValueError(f"SPEED_UNIT must be km/h or m/s, not {SPEED_UNIT!r}")


def dtc_map(text=None):
    """'P0500=01E241,U0104=01E242' -> {'P0500': '01E241', 'U0104': '01E242'} (validated)."""
    out = {}
    for pair in (AUTO_DTC_MAP if text is None else text).split(","):
        if not pair.strip():
            continue
        src, _, dst = pair.partition("=")
        src, dst = src.strip().upper(), dst.strip().upper()
        if not src or len(dst) != 6 or any(c not in "0123456789ABCDEF" for c in dst):
            raise ValueError(f"AUTO_DTC_MAP entry {pair!r}: expected CODE=6 hex digits")
        out[src] = dst
    return out


def public():
    """What the page may know (no secrets)."""
    return {
        "version": VERSION,
        "vehicle": {"key": SPEED_KEY, "unit": SPEED_UNIT, "host": VEHICLE_HOST, "connect": ZENOH_CONNECT, "mode": ZENOH_MODE,
                    "timeout_ms": LINK_TIMEOUT_MS, "range_kmh": [SPEED_MIN_KMH, SPEED_MAX_KMH]},
        "sovd": {"url": SOVD_URL, "base": SOVD_BASE, "entity": SOVD_ENTITY, "diag_entity": SOVD_DIAG_ENTITY,
                 "items": {"speed": SOVD_ITEM_SPEED, "debounce": SOVD_ITEM_DEBOUNCE, "link": SOVD_ITEM_LINK}},
        "faults": {"f1": F1_CODE, "f2": F2_CODE},
        "cda": {"url": CDA_URL, "base": CDA_BASE, "ecu": CDA_ECU},
        "sim": {"url": SIM_URL, "ecu": SIM_ECU, "fault_memory": SIM_FAULT_MEMORY},
        "auto_dtc": {"enabled": AUTO_DTC, "map": dtc_map(), "mask_active": AUTO_DTC_MASK_ACTIVE,
                     "mask_healed": AUTO_DTC_MASK_HEALED},
        "demo_dtc": {"code": DEMO_DTC, "mask": DEMO_DTC_MASK},
        "stats_file": STATS_FILE,
        "docker_containers": DOCKER_CONTAINERS,
        "timeout_s": HTTP_TIMEOUT,
    }
