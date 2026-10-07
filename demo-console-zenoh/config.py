# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: contract of the opensovd-gateway on feature/16-sovd-adapter-dataprovider)
# Goal: All settings of the console processes, read from environment variables with demo defaults.
"""Settings for every process of the v2 console: environment variables with demo defaults.

Nothing else hard-codes an address, a key, a code or a threshold. The page gets the
non-secret part through /api/config (see public()).

v2.1: the SOVD side is the opensovd-gateway binary of PR #40 (branch
feature/16-sovd-adapter-dataprovider, head d388985): component `cruise` with the four
data items below. score_app.py is a faithful stand-in of that binary (same URLs, same
JSON, same debounce, same environment variables), so SOVD_URL switches between them.
"""
import os


def _env(name, default):
    return os.environ.get(name, default)


def _bool(name, default):
    return _env(name, default).strip().lower() in ("1", "true", "yes", "on")


def _list(name, default):
    return [x.strip() for x in _env(name, default).split(",") if x.strip()]


VERSION = "2.1.0"

# ---------------------------------------------------------------- console (tester)
CONSOLE_HOST = _env("CONSOLE_HOST", "0.0.0.0")
CONSOLE_PORT = int(_env("CONSOLE_PORT", "8080"))
HTTP_TIMEOUT = float(_env("HTTP_TIMEOUT", "1.5"))          # seconds, per backend call

# ---------------------------------------------------------------- vehicle input (Zenoh)
# The virtual vehicle publishes the speed as a text float32 ("96.4") on this key.
# Its Zenoh peers listen on random ports: with VEHICLE_HOST set, the console finds them
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

# ---------------------------------------------------------------- console observer (the tester's own monitors)
# F1 and F2 are evaluated in the console from the Zenoh samples. F1's verdict is mirrored
# into the gateway's injection switch (FAULT_BRIDGE); F2 stays in the console until the
# Rust diag-host gets its own VehicleLink.
DIAG_TICK_S = float(_env("DIAG_TICK_S", "0.1"))             # observer cycle
LINK_TIMEOUT_MS = int(_env("LINK_TIMEOUT_MS", "500"))       # F2: no sample for longer than this
F1_THRESHOLD = int(_env("F1_THRESHOLD", "5"))               # F1: implausible samples to qualify FAILED
F1_CODE = _env("F1_CODE", "P0500")                          # SAE J2012: vehicle speed sensor "A"
F2_CODE = _env("F2_CODE", "U0104")                          # SAE J2012: lost communication with cruise control module

# ---------------------------------------------------------------- SOVD gateway (PR #40 contract)
# opensovd-gateway of feature/16-sovd-adapter-dataprovider: opensovd-core server mounted at
# SOVD_BASE, component SOVD_COMPONENT served by sovd_adapter (#16) with four data items.
SOVD_URL = _env("SOVD_URL", "http://127.0.0.1:7690")
SOVD_BASE = _env("SOVD_BASE", "/sovd")
SOVD_COMPONENT = _env("SOVD_COMPONENT", "cruise")
SOVD_ITEM_SPEED = _env("SOVD_ITEM_SPEED", "vehicle_speed")                 # currentData, read-only
SOVD_ITEM_STATE = _env("SOVD_ITEM_STATE", "cruise_state")                  # currentData, read-only
SOVD_ITEM_FAULT = _env("SOVD_ITEM_FAULT", "speed_sensor_fault_status")     # currentData, read-only
SOVD_ITEM_SWITCH = _env("SOVD_ITEM_SWITCH", "speed_sensor_stuck")          # storedData, read-write
SOVD_POLL_S = float(_env("SOVD_POLL_S", "0.2"))             # console poll of the gateway
FAULT_BRIDGE = _bool("FAULT_BRIDGE", "true")                # mirror the console's F1 verdict into the switch

# ---------------------------------------------------------------- stand-in of the gateway (score_app.py)
# Same environment variables as the Rust binary (score/opensovd-gateway/src/main.rs).
SCORE_GATEWAY_ADDRESS = _env("SCORE_GATEWAY_ADDRESS", "127.0.0.1:7690")
CRUISE_DEBOUNCE_FAILED_MS = int(_env("CRUISE_DEBOUNCE_FAILED_MS", "5000"))   # TimeBased: fault must hold this long
CRUISE_DEBOUNCE_PASSED_MS = int(_env("CRUISE_DEBOUNCE_PASSED_MS", "2000"))   # TimeBased: recovery must hold this long
STANDIN_PORT = int(SCORE_GATEWAY_ADDRESS.rsplit(":", 1)[-1] or "7690")
STANDIN_HOST = SCORE_GATEWAY_ADDRESS.rsplit(":", 1)[0] or "127.0.0.1"

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
# When a fault is confirmed, the console puts the mapped DTC into the ECU simulator and reads
# it back through the CDA; when the fault is qualified passed again, the DTC is kept as stored.
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


def sovd_items():
    """The four data items of the PR #40 contract, by role."""
    return {"speed": SOVD_ITEM_SPEED, "state": SOVD_ITEM_STATE, "fault": SOVD_ITEM_FAULT, "switch": SOVD_ITEM_SWITCH}


def public():
    """What the page may know (no secrets)."""
    return {
        "version": VERSION,
        "vehicle": {"key": SPEED_KEY, "unit": SPEED_UNIT, "host": VEHICLE_HOST, "connect": ZENOH_CONNECT, "mode": ZENOH_MODE,
                    "timeout_ms": LINK_TIMEOUT_MS, "range_kmh": [SPEED_MIN_KMH, SPEED_MAX_KMH], "f1_threshold": F1_THRESHOLD},
        "sovd": {"url": SOVD_URL, "base": SOVD_BASE, "component": SOVD_COMPONENT, "items": sovd_items(),
                 "poll_s": SOVD_POLL_S, "bridge": FAULT_BRIDGE,
                 "debounce_ms": {"failed": CRUISE_DEBOUNCE_FAILED_MS, "passed": CRUISE_DEBOUNCE_PASSED_MS}},
        "faults": {"f1": F1_CODE, "f2": F2_CODE},
        "cda": {"url": CDA_URL, "base": CDA_BASE, "ecu": CDA_ECU},
        "sim": {"url": SIM_URL, "ecu": SIM_ECU, "fault_memory": SIM_FAULT_MEMORY},
        "auto_dtc": {"enabled": AUTO_DTC, "map": dtc_map(), "mask_active": AUTO_DTC_MASK_ACTIVE,
                     "mask_healed": AUTO_DTC_MASK_HEALED},
        "demo_dtc": {"code": DEMO_DTC, "mask": DEMO_DTC_MASK},
        "docker_containers": DOCKER_CONTAINERS,
        "timeout_s": HTTP_TIMEOUT,
    }
