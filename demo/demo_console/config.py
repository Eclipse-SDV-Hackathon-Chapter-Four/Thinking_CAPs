"""Console configuration: environment variables with demo defaults.

Every backend address, entity name and file path lives here, so the page and
the runner never hard-code them (they read /api/config or import this module).
"""
import os


def _env(name, default):
    return os.environ.get(name, default)


# Console itself
CONSOLE_HOST = _env("CONSOLE_HOST", "0.0.0.0")
CONSOLE_PORT = int(_env("CONSOLE_PORT", "8080"))
HTTP_TIMEOUT = float(_env("HTTP_TIMEOUT", "1.5"))  # seconds, per backend call

# S-CORE application behind the SOVD gateway (opensovd-core server)
SOVD_URL = _env("SOVD_URL", "http://127.0.0.1:7690")
SOVD_BASE = _env("SOVD_BASE", "/sovd")                       # gateway mount path
SOVD_ENTITY = _env("SOVD_ENTITY", "components/cruise-control")  # entity under /v1
SOVD_ITEM_SPEED = _env("SOVD_ITEM_SPEED", "vehicle_speed")
SOVD_ITEM_DEBOUNCE = _env("SOVD_ITEM_DEBOUNCE", "debounce")
SOVD_ITEM_FREEZE = _env("SOVD_ITEM_FREEZE", "sensor_freeze")

# Classic Diagnostic Adapter (Docker, upstream)
CDA_URL = _env("CDA_URL", "http://127.0.0.1:20002")
CDA_BASE = _env("CDA_BASE", "/vehicle/v15")
CDA_ECU = _env("CDA_ECU", "flxc1000")                  # SOVD component id of the ECU
CDA_CLIENT_ID = _env("CDA_CLIENT_ID", "test_client")
CDA_CLIENT_SECRET = _env("CDA_CLIENT_SECRET", "test_secret")
CDA_TOKEN = _env("CDA_TOKEN", "")                      # optional: skip the token call

# ECU simulator control API (Docker, upstream test container)
SIM_URL = _env("SIM_URL", "http://127.0.0.1:8181")
SIM_ECU = _env("SIM_ECU", "FLXC1000")
SIM_FAULT_MEMORY = _env("SIM_FAULT_MEMORY", "Standard")
DEMO_DTC = _env("DEMO_DTC", "01E240")                  # default code injected by the page and the runner
DEMO_DTC_MASK = _env("DEMO_DTC_MASK", "2F")            # failing, pending, confirmed, this cycle, since clear

# Files and Docker
STATS_FILE = _env("STATS_FILE", "stats.json")
# Container names expected to be running; empty string = no container expected (fakes)
DOCKER_CONTAINERS = [c for c in _env("DOCKER_CONTAINERS", "cda,ecu-sim").split(",") if c.strip()]


def public():
    """What the page may know (no secrets)."""
    return {
        "sovd": {"url": SOVD_URL, "base": SOVD_BASE, "entity": SOVD_ENTITY,
                 "items": {"speed": SOVD_ITEM_SPEED, "debounce": SOVD_ITEM_DEBOUNCE, "freeze": SOVD_ITEM_FREEZE}},
        "cda": {"url": CDA_URL, "base": CDA_BASE, "ecu": CDA_ECU},
        "sim": {"url": SIM_URL, "ecu": SIM_ECU, "fault_memory": SIM_FAULT_MEMORY},
        "demo_dtc": {"code": DEMO_DTC, "mask": DEMO_DTC_MASK},
        "stats_file": STATS_FILE,
        "docker_containers": DOCKER_CONTAINERS,
        "timeout_s": HTTP_TIMEOUT,
    }
