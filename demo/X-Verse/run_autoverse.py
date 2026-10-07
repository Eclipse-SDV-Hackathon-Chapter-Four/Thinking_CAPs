#!/usr/bin/env python3
"""
Supervisor for Autoverse tasks with:
  - monitor auto-detection for the CARLA client window (Step 3),
  - clean start (kills stale client & server),
  - clean shutdown (kills CARLA client & server).

Steps
-----
1) cd $AUTOVERSE_ROOT                                  && just serve-nvidia
2) cd $AUTOVERSE_ROOT/vecu/vcu_zenoh/src               && python3 main.py
3) cd $AUTOVERSE_ROOT/vecu/simulink/pid_controller     && python3 main.py
4) cd $AUTOVERSE_ROOT/bridges/carla/examples           && python3 automate.py

Behavior
--------
- On start:
    * Kills stale CARLA server (by names & ports) and stale instances of the three steps.
- During run:
    * Starts all three steps and supervises them.
    * Puts the CARLA client window on the *second* monitor automatically.
- On exit (Ctrl-C/SIGTERM):
    * Gracefully terminates all child processes (including the CARLA client).
    * Also kills any CARLA server processes (by patterns and by ports).
- Logs stdout/stderr to ~/.cache/autoverse-runner/logs

Environment overrides
---------------------
- AUTOVERSE_DISPLAY_NAME="HDMI-0"      -> prefer a monitor by name
- AUTOVERSE_DISPLAY_INDEX="1"          -> prefer a monitor by index (0-based)
- AUTOVERSE_PYTHON="/usr/bin/python3"   -> component Python interpreter
- CARLA_PORT="2000"                    -> CARLA RPC/server port to kill by
- CARLA_STREAMING_PORT="2001"          -> CARLA streaming port to kill by

Command-line arguments
----------------------
- --carla-mock                         -> Run automate.py in CARLA mock mode
- --enable-camera-display              -> Enable camera display in automate.py
- --only-zenoh-modules                 -> Use only Zenoh-based modules (VCU and PID Controller) 

Notes
-----
- Uses X11 positioning for reliable window placement (Wayland can ignore positions). We set SDL_VIDEODRIVER=x11 for Step 3.
- If your CARLA server runs in Docker, we can add container cleanup on request.
"""

from __future__ import annotations
import argparse
import atexit
import fcntl
import os
import re
import json
import shutil
import shlex
import signal
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import psutil

# -------- Configuration -------------------------------------------------------

# The checkout this launcher lives in, wherever that is (e.g. ~/autoverse or
# Thinking_CAPs/demo/X-Verse). Step paths are relative to it; the steps also
# inherit it, so their control scripts can find sibling components.
os.environ.setdefault("AUTOVERSE_ROOT", str(Path(__file__).resolve().parent))

PYTHON = sys.executable or "python3"
PYTHON_BIN_DIR: Optional[Path] = None

def select_python(requested: Optional[str], carla_mock: bool,
                  only_zenoh_modules: bool) -> str:
    """Select an interpreter with the component dependencies before stopping anything."""
    modules = ["pygame", "numpy", "zenoh", "evdev"]
    if not carla_mock:
        modules.append("carla")
    if only_zenoh_modules:
        modules.append("matplotlib")
    probe = (
        "import importlib, json, sys\n"
        "errors = {}\n"
        "for name in sys.argv[1:]:\n"
        "    try: importlib.import_module(name)\n"
        "    except Exception as exc: errors[name] = str(exc)\n"
        "print(json.dumps(errors))\n"
    )
    candidates = [requested] if requested else [PYTHON, "/usr/bin/python3"]
    failures = []
    for candidate in dict.fromkeys(candidates):
        executable = shutil.which(candidate)
        if not executable:
            failures.append(f"{candidate}: executable not found")
            continue
        try:
            result = subprocess.run(
                [executable, "-c", probe, *modules],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "PYGAME_HIDE_SUPPORT_PROMPT": "1"},
            )
            if result.returncode:
                failures.append(f"{executable}: {result.stderr.strip()}")
                continue
            errors = json.loads(result.stdout.strip().splitlines()[-1])
        except (OSError, subprocess.TimeoutExpired, ValueError, IndexError) as exc:
            failures.append(f"{executable}: {exc}")
            continue
        if not errors:
            if executable != PYTHON:
                info(f"Using component Python: {executable}")
            return executable
        failures.append(f"{executable}: {errors}")
    raise RuntimeError(
        "No Python interpreter has the required component packages. "
        "Use --python /path/to/python with pygame, numpy, eclipse-zenoh, evdev "
        "and the CARLA API matching your server installed.\n" + "\n".join(failures)
    )

def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """True when something accepts TCP connections on host:port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def container_running(name: str) -> bool:
    """True when the named Docker container exists and is running."""
    result = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", name],
                            capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.strip() == "true"


def build_steps(
    carla_mock: bool = False,
    enable_camera_display: bool = False,
    only_zenoh_modules: bool = False,
    external_carla_server: bool = False,
    carla_host: str = "127.0.0.1",
    carla_port: int = 2000,
    vcu_zenoh: bool = False) -> List[Dict]:
    """Build the STEPS list with optional arguments for automate.py"""
    
    # Build automate.py command with optional flags
    automate_cmd = [
        PYTHON,
        "automate.py",
        "--carla-host",
        carla_host,
        "--carla-port",
        str(carla_port),
    ]

    if carla_mock:
        automate_cmd.append("--carla-mock")
    elif enable_camera_display:
        automate_cmd.append("--enable-camera-display")

    # Define steps dynamically according to user configuration
    steps = []

    # Zenoh router on tcp/127.0.0.1:7447, which every component connects to.
    # Started only when nothing answers there yet (and it is not our own
    # container from a previous run), so an existing router is reused and
    # never stopped. Version matches the Zenoh Python API (just install-zenoh).
    # AUTOVERSE_ZENOH_ROUTER=0 disables it.
    router_name = "autoverse-zenoh-router"
    if os.environ.get("AUTOVERSE_ZENOH_ROUTER", "1") != "0" and (
            not port_open("127.0.0.1", 7447) or container_running(router_name)):
        steps.append({
            "name": "Zenoh router (Docker)",
            "containers": [router_name],
            "cwd": "$HOME",
            "cmd": ["sh", "-c",
                    f"docker inspect {router_name} >/dev/null 2>&1 || "
                    f"docker run -d --init --rm --name {router_name} --network host "
                    f"{os.environ.get('ZENOH_ROUTER_IMAGE', 'eclipse/zenoh:1.3.4')}"],
            "stp": ["sh", "-c", f"docker rm -f {router_name} >/dev/null 2>&1 || true"],
            "kill_patterns": [],
            "startup_delay_sec": 2.0,
        })
    
    # Conditionally add CARLA Server step (only when not in mock mode)
    if not carla_mock and not external_carla_server:
        steps.append({
            "name": "CARLA Server (NVIDIA option)",
            "cwd": "$AUTOVERSE_ROOT",
            "cmd": ["just", "server-nvidia", "Epic", str(carla_port)],
            "kill_patterns": ["just server-nvidia"],
            "startup_delay_sec": 2.0,
        })

    # ThreadX zonal lighting controller on the MXChip AZ3166 board (USB,
    # SLCAN over the ST-LINK serial port).  Only added when the board is
    # plugged in.  Its ctl.sh runs the unchanged Zenoh2CAN bridge, which maps
    # vcu/control/{brake,reverse}_sts to CAN 0x1F1 and the board's 0x1F4
    # replies to vehicle/lights/*_cmd (applied to CARLA by the virtual
    # vehicle), plus a watchdog that restarts it when the board re-enumerates.
    # Started before the VCU so it sees the VCU's first status changes.
    # Overrides: AZ3166_PORT (serial device), THREADX_DIR (solution folder).
    # Default: next to this checkout when it lives in Thinking_CAPs
    # (demo/X-Verse -> ../../ThreadX), else ~/Thinking_CAPs/ThreadX.
    threadx_sibling = Path(__file__).resolve().parents[2] / "ThreadX"
    threadx_dir = os.path.expandvars(os.environ.get(
        "THREADX_DIR",
        str(threadx_sibling) if (threadx_sibling / "ctl.sh").is_file() else "$HOME/Thinking_CAPs/ThreadX"))
    az3166_ports = sorted(Path("/dev/serial/by-id").glob("usb-STMicroelectronics_STM32_STLink_*-if02"))
    az3166_port = os.environ.get("AZ3166_PORT") or (str(az3166_ports[0]) if az3166_ports else "")
    if az3166_port and os.path.exists(az3166_port) and os.path.isfile(os.path.join(threadx_dir, "ctl.sh")):
        steps.append({
            "name": "ThreadX zonal lights (AZ3166)",
            "detached": True,
            "cwd": threadx_dir,
            "cmd": ["./ctl.sh", "start"],
            "stp": ["./ctl.sh", "down"],
            "kill_patterns": [],
            "startup_delay_sec": 1.0,
        })

    # Conditionally add modules based on the communication protocol
    if only_zenoh_modules:
        steps.append({
            "name": "VCU Module Python",
            "cwd": "$AUTOVERSE_ROOT/vecu/vcu_zenoh/src",
            "cmd": [PYTHON, "main.py"],
            "kill_patterns": [
                "vecu/vcu_zenoh/src/main.py",
                "vcu_zenoh/src/main.py",
            ],
            "startup_delay_sec": 1.0,
        })

        steps.append({
            "name": "ADAS Module Python Zenoh",
            "cwd": "$AUTOVERSE_ROOT/vecu/simulink/pid_controller",
            "cmd": [PYTHON, "main.py"],
            "kill_patterns": [
                "vecu/simulink/pid_controller/main.py",
                "pid_controller/main.py",
            ],
            "startup_delay_sec": 1.0,
        })
    
    # SOME/IP and CAN Modules or VCU Zenoh
    else:
        if vcu_zenoh:
            steps.append({
                "name": "VCU Module Python",
                "cwd": "$AUTOVERSE_ROOT/vecu/vcu_zenoh/src",
                "cmd": [PYTHON, "main.py"],
                "kill_patterns": [
                    "vecu/vcu_zenoh/src/main.py",
                    "vcu_zenoh/src/main.py",
                ],
                "startup_delay_sec": 1.0,
            })
        # placeholder needs to be reviewed
        # else:
        #     steps.append({
        #         "name": "Zenoh to CAN bridge",
        #         "cwd": "$AUTOVERSE_ROOT/bridges/can/can-zenoh-bridge-python/src",
        #         "cmd": [PYTHON, "bridge.py", "config/config.json"],
        #         "kill_patterns": [
        #             "bridges/can/can-zenoh-bridge-python/src",
        #             "src/bridge.py"
        #         ],
        #         "startup_delay_sec": 1.0,
        #     })

        steps.append({
            "name": "Zenoh to SOME-IP bridge",
            "containers": [os.environ.get("CONTAINER", "bridge-e2e")],
            "cwd": "$AUTOVERSE_ROOT/bridges/someip/zenoh-someip-bridge",
            "cmd": ["./scripts/ctl.sh",  "start"],
            "stp": ["./scripts/ctl.sh",  "stop"],
            "kill_patterns": [],
            "startup_delay_sec": 1.0,
        })

        steps.append({
            "name": "ADAS Module S-CORE",
            "containers": (
                ["docker_setup-adas_score-1"]
                if os.environ.get("SCORE_FOR", "X-Verse") == "X-Verse"
                else ["docker_setup-someipd-1", "docker_setup-client-1"]
                + (["docker_setup-adas_score-1"]
                   if os.environ.get("SCORE_FOR") == "All" else [])
            ),
            "cwd": "$AUTOVERSE_ROOT/vecu/s-core",
            "cmd": ["./ctl.sh",  "start"],
            "stp": ["./ctl.sh",  "stop"],
            "kill_patterns": [],
            "startup_delay_sec": 5.0,
        })

    # OTA stack -  EOL backend + RTCU vECU, from
    # vecu/ota/docker-compose.yaml (one-shot certgen runs first).  The X-Verse APK is
    # delivered ONLY through this OTA plane — cuttlefish ctl.sh no longer
    # installs it at container-creation time.  The backend is the Java 21 /
    # Spring Boot rewrite: compose builds it from backend/Dockerfile (maven
    # multi-stage), so --build keeps it in sync with the sources.  ctl.sh up
    # also waits for https://localhost:9444 and opens it in the browser.
    steps.append({
        "name": "OTA stack: EOL backend + RTCU (APK installer)",
        "containers": ["ota-backend", "ota-rtcu"],
        "cwd": "$AUTOVERSE_ROOT/vecu/ota",
        "cmd": ["./ctl.sh", "up"],      # compose up -d --build + opens EOL console
        "stp": ["./ctl.sh", "stop"],
        "kill_patterns": [],
        "startup_delay_sec": 1.0,
    })

    # Common modules always used
    steps.append({
        "name": "Vehicle Manual Control module",
        "cwd": "$AUTOVERSE_ROOT/bridges/carla/examples",
        "cmd": [PYTHON, "vehicle_manual_control.py"],
        "kill_patterns": [
            "bridges/carla/examples/vehicle_manual_control.py",
            "/examples/vehicle_manual_control.py",
            "python.*vehicle_manual_control.py",
        ],
        "startup_delay_sec": 1.0,
    })
    steps.append({
        "name": "CARLA automate.py",
        "cwd": "$AUTOVERSE_ROOT/bridges/carla/examples",
        "cmd": automate_cmd,
        "kill_patterns": [
            "bridges/carla/examples/automate.py",
            "/examples/automate.py",
            "python.*automate.py",
        ],
        "startup_delay_sec": 1.0,
    })
    steps.append({
        "name": "ANDROID Cuttlefish",
        "containers": [os.environ.get("CONTAINER", "cuttlefish-orchestration-cont")],
        "cwd": "$AUTOVERSE_ROOT/aaos_digital_cluster/cuttlefish_emulator",
        "cmd": ["./ctl.sh",  "start"],
        "stp": ["./ctl.sh",  "stop"],
        "kill_patterns": [],
        "startup_delay_sec": 1.0,
    })

    # Component-specific overrides avoid sharing the generic IMAGE/CONTAINER
    # values between the bridge and Android during an isolated SSD bring-up.
    settings = {
        "Zenoh to SOME-IP bridge": ("AUTOVERSE_BRIDGE", "zenoh-someip-bridge", "bridge-e2e"),
        "ANDROID Cuttlefish": ("AUTOVERSE_ANDROID", "cuttlefish-orchestration-img", "cuttlefish-orchestration-cont"),
    }
    for step in steps:
        if step["name"] in settings:
            prefix, image_default, container_default = settings[step["name"]]
            if os.environ.get(prefix + "_IMAGE") or os.environ.get(prefix + "_CONTAINER"):
                image = os.environ.get(prefix + "_IMAGE", image_default)
                container = os.environ.get(prefix + "_CONTAINER", container_default)
                step["containers"] = [container]
                for action in ("cmd", "stp"):
                    step[action] = ["env", "IMAGE=" + image, "CONTAINER=" + container, *step[action]]
        if step["name"] == "ADAS Module S-CORE" and os.environ.get("COMPOSE_PROJECT_NAME"):
            step["containers"] = [name.replace("docker_setup-", os.environ["COMPOSE_PROJECT_NAME"] + "-", 1)
                                  for name in step["containers"]]

    # Automatically add step numbers to names
    for i, step in enumerate(steps, start=1):
        step["name"] = f"Step {i}: {step['name']}"

    return steps

LOG_DIR = Path.home() / ".cache" / "autoverse-runner" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

GRACEFUL_TERM_TIMEOUT = 10.0
FORCE_KILL_TIMEOUT = 3.0
CONTROL_STOP_TIMEOUT = 60.0
CONTROL_START_TIMEOUT = 540.0
CONTAINER_CHECK_INTERVAL = 5.0


def acquire_runner_lock():
    """Hold the stack lock until all shutdown handlers have completed."""
    lock_path = LOG_DIR.parent / "runner.lock"
    lock_file = lock_path.open("a+")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_file.seek(0)
        owner = lock_file.read().strip() or "unknown"
        lock_file.close()
        raise RuntimeError(f"Autoverse is already running (PID {owner}).")
    lock_file.seek(0)
    lock_file.truncate()
    lock_file.write(str(os.getpid()))
    lock_file.flush()
    return lock_file


def check_containers(names: List[str]) -> None:
    """Check the containers themselves, rather than their detached launchers."""
    result = subprocess.run(
        ["docker", "container", "inspect", "--format", "{{json .State}}", *names],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode:
        raise RuntimeError(f"Cannot inspect containers: {result.stderr.strip()}")
    states = [json.loads(line) for line in result.stdout.splitlines()]
    if len(states) != len(names):
        raise RuntimeError("Docker returned an incomplete container status.")
    for name, state in zip(names, states):
        if not state["Running"] or state.get("Paused") or state.get("Restarting"):
            raise RuntimeError(
                f"Container {name} is {state['Status']} "
                f"(exit={state['ExitCode']}, OOMKilled={state['OOMKilled']}). "
                f"Inspect with: docker logs {name}"
            )

# ---- CARLA server cleanup config --------------------------------------------

# Common CARLA/UE4 process names on Linux; matched with `pkill -f`.
CARLA_KILL_PATTERNS: List[str] = [
    "CarlaUE4-Linux-Shipping",
    "CarlaUE4Server-Linux-Shipping",
    "CarlaUE4Server",
    "CarlaUE4/Binaries/Linux/CarlaUE4-",
    "CarlaUE4.sh",
    "CarlaUE4.sh -prefernvidia",
    "UE4Editor",
    "UE4-Linux-Shipping",
    "CarlaUE4",
    "manual_control_steeringwheel_zenoh.py",
]

def _int_env(name: str, default: int) -> int:
    v = os.environ.get(name, "").strip()
    return int(v) if v.isdigit() else default

# Ports used by CARLA server (defaults; override via env)
CARLA_PORTS: List[int] = [
    _int_env("CARLA_PORT", 2000),
    _int_env("CARLA_STREAMING_PORT", 2001),
]

# -------- Pretty logging ------------------------------------------------------

def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def info(msg: str) -> None:
    print(f"[{ts()}] ℹ️  {msg}", flush=True)

def ok(msg: str) -> None:
    print(f"[{ts()}] ✅ {msg}", flush=True)

def warn(msg: str) -> None:
    print(f"[{ts()}] ⚠️  {msg}", flush=True)

def err(msg: str) -> None:
    print(f"[{ts()}] ❌ {msg}", flush=True)

# -------- Monitor detection ---------------------------------------------------

@dataclass
class Monitor:
    index: int
    name: str
    width: int
    height: int
    x: int
    y: int
    primary: bool

def _run(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)

def _parse_listmonitors(text: str) -> List[Monitor]:
    """
    Parse `xrandr --listmonitors`.
      e.g. "1: +HDMI-0 3840/1198x2160/336+369+1440  HDMI-0"
           "0: +*DP-4  2560/527x1440/296+0+0        DP-4"
    """
    mons: List[Monitor] = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(
            r"^(\d+):\s+\+(\*?)([A-Za-z0-9\-\._]+)\s+(\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)",
            line,
        )
        if not m:
            continue
        idx = int(m.group(1))
        primary = (m.group(2) == "*")
        name = m.group(3)
        w = int(m.group(4))
        h = int(m.group(5))
        x = int(m.group(6))
        y = int(m.group(7))
        mons.append(Monitor(idx, name, w, h, x, y, primary))
    return mons

def _parse_xrandr_connected(text: str) -> List[Monitor]:
    """
    Fallback parser for plain `xrandr` lines:
      "HDMI-0 connected 3840x2160+369+1440 ..."
      "DP-4 connected primary 2560x1440+0+0 ..."
    """
    mons: List[Monitor] = []
    idx = 0
    for line in text.splitlines():
        if " connected" not in line:
            continue
        name_match = re.match(r"^([A-Za-z0-9\-\._]+)\s+connected(\s+primary)?\s+", line)
        if not name_match:
            continue
        name = name_match.group(1)
        primary = bool(name_match.group(2))
        geo = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
        if not geo:
            continue
        w, h, x, y = map(int, geo.groups())
        mons.append(Monitor(idx, name, w, h, x, y, primary))
        idx += 1
    return mons

def detect_second_monitor(prefer_name: Optional[str] = None,
                          prefer_index: Optional[int] = None) -> Optional[Monitor]:
    """Pick the 'second' monitor: prefer env-provided, else first non-primary, else index 1."""
    try:
        mons = _parse_listmonitors(_run(["xrandr", "--listmonitors"]))
    except Exception:
        try:
            mons = _parse_xrandr_connected(_run(["xrandr"]))
        except Exception as e:
            warn(f"Could not run xrandr for monitor detection: {e}")
            return None

    if not mons:
        warn("No monitors parsed from xrandr output.")
        return None

    if prefer_index is not None:
        for m in mons:
            if m.index == prefer_index:
                return m

    if prefer_name:
        for m in mons:
            if m.name == prefer_name:
                return m

    non_primary = [m for m in mons if not m.primary]
    if non_primary:
        return non_primary[0]

    return mons[1] if len(mons) >= 2 else None

# -------- Process utilities ---------------------------------------------------

def check_dir(path: str) -> None:
    if not Path(path).is_dir():
        raise FileNotFoundError(f"Directory does not exist: {path}")

def pgrep(pattern: str) -> List[int]:
    try:
        out = subprocess.check_output(["pgrep", "-f", pattern], text=True)
        return [int(x) for x in out.strip().splitlines() if x.strip().isdigit()]
    except subprocess.CalledProcessError:
        return []

def pkill(pattern: str, sig: str) -> None:
    subprocess.run(["pkill", sig, "-f", pattern], check=False)

def kill_existing(patterns: List[str], label: str) -> None:
    if not patterns:
        return
    found = False
    for pat in patterns:
        pids = pgrep(pat)
        if pids:
            found = True
            warn(f"{label}: found existing PIDs for '{pat}': {pids}")
    if not found:
        info(f"{label}: no previous instances found.")
        return

    for pat in patterns:
        pkill(pat, "-TERM")

    deadline = time.time() + GRACEFUL_TERM_TIMEOUT
    while time.time() < deadline:
        still = []
        for pat in patterns:
            still.extend(pgrep(pat))
        if not still:
            ok(f"{label}: previous instances terminated gracefully.")
            return
        time.sleep(0.5)

    warn(f"{label}: forcing kill of lingering processes.")
    for pat in patterns:
        pkill(pat, "-KILL")

    deadline = time.time() + FORCE_KILL_TIMEOUT
    while time.time() < deadline:
        still = []
        for pat in patterns:
            still.extend(pgrep(pat))
        if not still:
            ok(f"{label}: lingering processes killed.")
            return
        time.sleep(0.25)

    err(f"{label}: some processes may still be running.")

def kill_process_tree(pid: int, sig: signal.Signals = signal.SIGTERM, timeout: float = 5.0) -> None:
    """
    Kill a process and all its children recursively using psutil.
    This ensures child processes spawned by automate.py (like virtual_vehicle.py) are also terminated.
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Send signal to children first
        for child in children:
            try:
                info(f"  Terminating child process: {child.pid} ({child.name()})")
                child.send_signal(sig)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Then send signal to parent
        try:
            parent.send_signal(sig)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Wait for processes to terminate
        gone, alive = psutil.wait_procs(children + [parent], timeout=timeout)
        
        # Force kill any survivors
        for p in alive:
            try:
                warn(f"  Force killing process: {p.pid} ({p.name()})")
                p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
    except psutil.NoSuchProcess:
        # Process already dead
        pass
    except Exception as e:
        warn(f"  Error killing process tree for PID {pid}: {e}")

# ---- CARLA server kill helpers ----------------------------------------------

def pids_listening_on_ports(ports: List[int]) -> Set[int]:
    """
    Find PIDs listening on the given TCP ports using `ss` (preferred) or `lsof` (fallback).
    """
    pids: Set[int] = set()

    # Try `ss`
    try:
        out = subprocess.check_output(["ss", "-H", "-ltnp"], text=True, stderr=subprocess.STDOUT)
        for line in out.splitlines():
            for port in ports:
                if f":{port} " in line or f"]:{port} " in line or f":{port}\n" in line:
                    for pid in re.findall(r"pid=(\d+)", line):
                        pids.add(int(pid))
        if pids:
            return pids
    except Exception:
        pass

    # Fallback `lsof`
    for port in ports:
        try:
            out = subprocess.check_output(
                ["lsof", "-nP", "-i", f"TCP:{port}", "-sTCP:LISTEN", "-t"],
                text=True,
                stderr=subprocess.STDOUT
            )
            for pid in out.split():
                if pid.isdigit():
                    pids.add(int(pid))
        except Exception:
            continue

    return pids

def terminate_pids(pids: Set[int], label: str) -> None:
    if not pids:
        return
    warn(f"{label}: sending SIGTERM to PIDs {sorted(pids)}")
    for pid in list(pids):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pids.discard(pid)

    deadline = time.time() + GRACEFUL_TERM_TIMEOUT
    while time.time() < deadline and pids:
        for pid in list(pids):
            if not Path(f"/proc/{pid}").exists():
                pids.discard(pid)
        time.sleep(0.25)

    if not pids:
        ok(f"{label}: all PIDs terminated gracefully.")
        return

    warn(f"{label}: forcing SIGKILL to remaining PIDs {sorted(pids)}")
    for pid in list(pids):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

def kill_carla_processes(label: str) -> None:
    """
    Kill CARLA server by patterns AND by well-known ports.
    (Safe to call at startup and shutdown.)
    """
    info(f"{label}: scanning for CARLA server...")
    # Kill by patterns
    kill_existing(CARLA_KILL_PATTERNS, f"{label} (patterns)")
    # Kill by listening ports (e.g., 2000/2001)
    port_pids = pids_listening_on_ports(CARLA_PORTS)
    if port_pids:
        terminate_pids(port_pids, f"{label} (ports {CARLA_PORTS})")
    else:
        info(f"{label}: no listeners on ports {CARLA_PORTS} found.")

# -------- Launch & supervise --------------------------------------------------

def start_process(name: str, cwd: str, cmd: List[str],
                  step3_monitor: Optional[Monitor] = None) -> Tuple[subprocess.Popen, Path, Path]:
    """
    Start a long-running process in its own process group and stream output to log files.
    For Step 3, apply SDL env to place window on second monitor (if detected).
    """
    # Expand environment variables in cwd
    cwd = os.path.expandvars(cwd)
    check_dir(cwd)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = name.lower().replace(" ", "_").replace("/", "_").replace(":", "")
    stdout_path = LOG_DIR / f"{safe_name}-{stamp}.out.log"
    stderr_path = LOG_DIR / f"{safe_name}-{stamp}.err.log"

    stdout_f = open(stdout_path, "ab", buffering=0)
    stderr_f = open(stderr_path, "ab", buffering=0)

    info(f"Starting: {name}")
    info(f"  cwd: {cwd}")
    info(f"  cmd: {' '.join(shlex.quote(c) for c in cmd)}")
    info(f"  logs:")
    info(f"     {stdout_path}")
    info(f"     {stderr_path}")

    env = os.environ.copy()
    # automate.py invokes a just recipe which runs python3 through PATH.
    # Keep that nested client on the same interpreter as the other modules.
    env["PATH"] = str(PYTHON_BIN_DIR or Path(PYTHON).parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONUNBUFFERED"] = "1"

    # Apply SDL placement for Step 3 only
    if "CARLA automate.py" in name and step3_monitor:
        env.setdefault("SDL_VIDEODRIVER", "x11")  # reliable positioning on X11
        env["SDL_VIDEO_WINDOW_POS"] = f"{step3_monitor.x},{step3_monitor.y}"        # windowed
        env["SDL_VIDEO_FULLSCREEN_DISPLAY"] = str(step3_monitor.index)              # fullscreen
        info(
            f"  monitor: index={step3_monitor.index} name={step3_monitor.name} "
            f"geom={step3_monitor.width}x{step3_monitor.height}+{step3_monitor.x}+{step3_monitor.y} "
            f"primary={step3_monitor.primary}"
        )
        info(
            f"  SDL env: SDL_VIDEODRIVER={env['SDL_VIDEODRIVER']}  "
            f"SDL_VIDEO_WINDOW_POS={env['SDL_VIDEO_WINDOW_POS']}  "
            f"SDL_VIDEO_FULLSCREEN_DISPLAY={env['SDL_VIDEO_FULLSCREEN_DISPLAY']}"
        )

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=stdout_f,
            stderr=stderr_f,
            preexec_fn=os.setsid,  # new process group for clean termination
            env=env,
        )
    finally:
        stdout_f.close()
        stderr_f.close()

    ok(f"{name} started with PID {proc.pid}")
    return proc, stdout_path, stderr_path

children: List[Tuple[str, subprocess.Popen]] = []
CONTROL_STEPS: List[Dict] = []
SHUTTING_DOWN = False

USE_EXTERNAL_CARLA_SERVER = False

def stop_process(name: str, cwd: str, cmd: List[str]) -> Tuple[subprocess.Popen, Path, Path]:
    # Expand environment variables in cwd
    cwd = os.path.expandvars(cwd)
    check_dir(cwd)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = name.lower().replace(" ", "_").replace("/", "_").replace(":", "")
    stdout_path = LOG_DIR / f"{safe_name}-{stamp}.out.log"
    stderr_path = LOG_DIR / f"{safe_name}-{stamp}.err.log"

    stdout_f = open(stdout_path, "ab", buffering=0)
    stderr_f = open(stderr_path, "ab", buffering=0)

    info(f"Stopping: {name}")
    info(f"  cwd: {cwd}")
    info(f"  stp: {' '.join(shlex.quote(c) for c in cmd)}")
    info(f"  logs:")
    info(f"     {stdout_path}")
    info(f"     {stderr_path}")

    env = os.environ.copy()

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=stdout_f,
        stderr=stderr_f,
        env=env,
    )

    # Docker stop can take its full grace period. Do not start anything until
    # this command has completed successfully.
    try:
        returncode = proc.wait(timeout=CONTROL_STOP_TIMEOUT)
    except subprocess.TimeoutExpired:
        kill_process_tree(proc.pid, timeout=FORCE_KILL_TIMEOUT)
        proc.wait(timeout=FORCE_KILL_TIMEOUT)
        raise RuntimeError(f"Timed out stopping {name}. See {stderr_path}")
    finally:
        stdout_f.close()
        stderr_f.close()
    if returncode:
        raise RuntimeError(
            f"Failed to stop {name} (exit {returncode}). See {stderr_path}"
        )
    ok(f"{name} stopped")
    return proc, stdout_path, stderr_path

def terminate_process(proc: subprocess.Popen, name: str) -> None:
    if proc.poll() is not None:
        return
    warn(f"Stopping {name} (PID {proc.pid})...")
    try:
        kill_process_tree(proc.pid, signal.SIGTERM, timeout=GRACEFUL_TERM_TIMEOUT)
        if proc.poll() is not None:
            ok(f"{name} terminated gracefully.")
            return
    except Exception as e:
        warn(f"Error during graceful termination of {name}: {e}")

    warn(f"{name} did not stop in time. Sending SIGKILL.")
    try:
        kill_process_tree(proc.pid, signal.SIGKILL, timeout=FORCE_KILL_TIMEOUT)
    except Exception as e:
        err(f"Error during force kill of {name}: {e}")

def shutdown_all(*_args) -> None:
    global SHUTTING_DOWN
    if SHUTTING_DOWN:
        return
    SHUTTING_DOWN = True

    # First stop our child processes (includes CARLA client from Step 3)
    if children:
        warn("Shutting down all child processes...")
        for name, proc in children:
            terminate_process(proc, name)

        children.clear()
        ok("All child processes stopped.")

    for step in reversed(CONTROL_STEPS):
        try:
            stop_process(name=step["name"], cwd=step["cwd"], cmd=step["stp"])
        except Exception as exc:
            err(f"Shutdown failed for {step['name']}: {exc}")

    if USE_EXTERNAL_CARLA_SERVER:
        info(
            "External CARLA server mode: "
            "skipping CARLA server cleanup."
        )
    else:
        kill_carla_processes(
            "CARLA (shutdown)"
        )

# -------- Main ---------------------------------------------------------------

def main() -> int:
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Autoverse Supervisor - Manages Autoverse components',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
        add_help=True  # Explicitly enable -h/--help (enabled by default)
    )

    # Create mutually exclusive group for CARLA mock and Camera Display rendering
    display_group = parser.add_mutually_exclusive_group()
    display_group.add_argument(
        '--carla-mock',
        action='store_true',
        dest='carla_mock',
        help='Run automate.py in CARLA mock mode (no actual CARLA Server required). '
             'Mutually exclusive with --enable-camera-display.'
    )
    display_group.add_argument(
        '--enable-camera-display',
        action='store_true',
        dest='enable_camera_display',
        help='Enable camera display rendering in automate.py (default: False - headless mode). '
             'Mutually exclusive with --carla-mock.'
    )
    
    parser.add_argument(
        '--only-zenoh-modules',
        action='store_true',
        dest='only_zenoh_modules',
        help='Use only Zenoh-based modules (VCU and PID Controller). '
             'When disabled, uses SOME/IP bridge and s-core ADAS container instead.'
    )
    
    parser.add_argument(
        '--vcu-zenoh',
        action='store_true',
        dest='vcu_zenoh',
        help='Use VCU Zenoh-based version.'
             'When disabled, the VCU CAN and CAN bridge should be launched manually.'
    )

    parser.add_argument(
        "--external-carla-server",
        action="store_true",
        help=(
            "Use an already running external CARLA server "
            "instead of starting or stopping CARLA locally"
        ),
    )

    parser.add_argument(
        "--carla-host",
        default="127.0.0.1",
        help=(
            "CARLA server address passed to the CARLA client "
            "(default: 127.0.0.1)"
        ),
    )

    parser.add_argument(
        "--carla-port",
        type=int,
        default=2000,
        help="CARLA RPC port (default: 2000)",
    )


    parser.add_argument(
        "--python",
        default=os.environ.get("AUTOVERSE_PYTHON"),
        help="Python for components (default: current Python, then system Python if packages are missing)",
    )

    args = parser.parse_args()

    try:
        runner_lock = acquire_runner_lock()
    except RuntimeError as exc:
        err(str(exc))
        return 1
    atexit.register(runner_lock.close)

    global PYTHON, PYTHON_BIN_DIR
    try:
        PYTHON = select_python(args.python, args.carla_mock, args.only_zenoh_modules)
    except RuntimeError as exc:
        err(str(exc))
        return 1

    # A private python3 shim also supports explicitly selected executables whose
    # directory's default python3 points at a different interpreter.
    python_bin = tempfile.TemporaryDirectory(prefix="autoverse-python-")
    PYTHON_BIN_DIR = Path(python_bin.name)
    (PYTHON_BIN_DIR / "python3").symlink_to(PYTHON)
    atexit.register(python_bin.cleanup)

    global USE_EXTERNAL_CARLA_SERVER

    USE_EXTERNAL_CARLA_SERVER = (
        args.external_carla_server
    )
    
    # Build steps with optional arguments
    STEPS = build_steps(
        carla_mock=args.carla_mock,
        enable_camera_display=args.enable_camera_display,
        only_zenoh_modules=args.only_zenoh_modules,
        vcu_zenoh= args.vcu_zenoh,
        external_carla_server=args.external_carla_server,
        carla_host=args.carla_host,
        carla_port=args.carla_port,
    )
    
    global CONTROL_STEPS
    CONTROL_STEPS = [step for step in STEPS if "stp" in step]

    # Log configuration
    info("=" * 60)
    info("Autoverse Supervisor Starting")
    info("=" * 60)
    info(f"CARLA Mock Mode: {'Enabled' if args.carla_mock else 'Disabled'}")
    info("External CARLA Server: "f"{'Enabled' if args.external_carla_server else 'Disabled'}")
    info(f"CARLA Endpoint: {args.carla_host}:{args.carla_port}")
    info(f"Camera Display rendering: {'Enabled' if args.enable_camera_display else 'Disabled'}")
    info(f"Component Python: {PYTHON}")
    info(f"Use only Zenoh Modules: {'True' if args.only_zenoh_modules else 'False'}")
    info(f"Use VCU Zenoh Module: {'True' if args.vcu_zenoh else 'False'}")
    info(f"Logs Directory:")
    info(f"     {LOG_DIR}")
    info("=" * 60)

    def handle_shutdown_signal(
        signum,
        _frame,
    ) -> None:
        warn(
            f"Received signal {signum}. "
            "Stopping supervisor."
        )

        shutdown_all()

        raise SystemExit(0)
    
    # Cleanup on exit/signals
    atexit.register(shutdown_all)
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    # 0) Ensure CARLA server isn't already running from a previous session
    if args.external_carla_server:
        info(
            "External CARLA server mode: "
            "skipping pre-start CARLA cleanup."
        )
    else:
        kill_carla_processes(
            "CARLA (pre-start)"
        )

    # 1) Stop previous instances of our steps
    info("Ensuring previous instances are not running...")
    for step in STEPS:
        if "stp" in step:
            try:
                stop_process(name=step["name"], cwd=step["cwd"], cmd=step["stp"])
            except Exception as exc:
                err(str(exc))
                return 1
        kill_existing(step["kill_patterns"], step["name"])

    # 2) Detect the second monitor (for Step 3 SDL placement)
    prefer_name = os.environ.get("AUTOVERSE_DISPLAY_NAME") or None
    prefer_index_env = os.environ.get("AUTOVERSE_DISPLAY_INDEX")
    prefer_index = int(prefer_index_env) if prefer_index_env and prefer_index_env.isdigit() else None

    step3_monitor: Optional[Monitor] = detect_second_monitor(
        prefer_name=prefer_name,
        prefer_index=prefer_index
    )

    if step3_monitor:
        ok(
            f"Second monitor detected → index={step3_monitor.index} "
            f"name={step3_monitor.name} "
            f"origin=({step3_monitor.x},{step3_monitor.y}) "
            f"size={step3_monitor.width}x{step3_monitor.height}"
        )
    else:
        warn("Could not detect a second monitor. Step 3 will use default display.")

    # 3) Start steps
    managed_containers = []
    for step in STEPS:
        try:
            proc, out_log, err_log = start_process(
                step["name"], step["cwd"], step["cmd"], step3_monitor=step3_monitor
            )
            children.append((step["name"], proc))
            # Control scripts (containers or a detached service) return once
            # the component is up; their stp command stops it at shutdown.
            if "containers" in step or step.get("detached"):
                returncode = proc.wait(timeout=CONTROL_START_TIMEOUT)
                if returncode:
                    raise RuntimeError(f"Start command exited with {returncode}. See {err_log}")
            time.sleep(step.get("startup_delay_sec", 0.0))
            if "containers" in step:
                check_containers(step["containers"])
                children.remove((step["name"], proc))
                managed_containers.append(step)
                ok(f"{step['name']}: containers are running")
            elif step.get("detached"):
                children.remove((step["name"], proc))
                ok(f"{step['name']}: running (managed by its control script)")
        except Exception as e:
            err(f"Failed to start {step['name']}: {e}")
            if "containers" in step:
                return 1
            continue

    if not children and not managed_containers:
        err("No processes started. Exiting.")
        return 1

    info("Supervisor is now running. Press Ctrl-C to stop everything.")
    info(f"Logs directory:")
    info(f"     {LOG_DIR}")

    # 4) Supervise processes and detached containers.
    next_container_check = 0.0
    try:
        while True:
            if managed_containers and time.monotonic() >= next_container_check:
                try:
                    check_containers([
                        name for step in managed_containers for name in step["containers"]
                    ])
                except Exception as exc:
                    err(str(exc))
                    return 1
                next_container_check = time.monotonic() + CONTAINER_CHECK_INTERVAL
            for name, proc in list(children):
                rc = proc.poll()
                if rc is not None:
                    warn(f"{name} exited with code {rc}. See logs for details.")
                    children.remove((name, proc))
            if not children and not managed_containers:
                warn("All components have exited.")
                break
            time.sleep(1.0)
    finally:
        shutdown_all()

    return 0

if __name__ == "__main__":
    sys.exit(main())
