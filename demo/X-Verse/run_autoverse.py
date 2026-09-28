#!/usr/bin/env python3
"""
Supervisor for Autoverse tasks with:
  - monitor auto-detection for the CARLA client window (Step 3),
  - clean start (kills stale client & server),
  - clean shutdown (kills CARLA client & server).

Steps
-----
1) cd $HOME/autoverse                                  && just serve-nvidia
2) cd $HOME/autoverse/vecu/vcu_zenoh/src               && python3 main.py
3) cd $HOME/autoverse/vecu/simulink/pid_controller     && python3 main.py
4) cd $HOME/autoverse/bridges/carla/examples           && python3 automate.py

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
- CARLA_PORT="2000"                    -> CARLA RPC/server port to kill by
- CARLA_STREAMING_PORT="2001"          -> CARLA streaming port to kill by

Command-line arguments
----------------------
- --carla-mock                         -> Run automate.py in CARLA mock mode
- --enable-camera-display              -> Enable camera display in automate.py (temporary disabled, this arg is being passed as default to automate.py)
- --only-zenoh-modules                 -> Use only Zenoh-based modules (VCU and PID Controller) 

Notes
-----
- Uses X11 positioning for reliable window placement (Wayland can ignore positions). We set SDL_VIDEODRIVER=x11 for Step 3.
- If your CARLA server runs in Docker, we can add container cleanup on request.
"""

from __future__ import annotations
import argparse
import atexit
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import psutil

# -------- Configuration -------------------------------------------------------

PYTHON = sys.executable or "python3"

def build_steps(carla_mock: bool = False, enable_camera_display: bool = False, only_zenoh_modules: bool = False, vcu_zenoh: bool = False) -> List[Dict]:
    """Build the STEPS list with optional arguments for automate.py"""
    
    # Build automate.py command with optional flags
    automate_cmd = [PYTHON, "automate.py"]
    if carla_mock:
        automate_cmd.append("--carla-mock")
    else:
        # Always pass this argument to automate.py to make it True by default
        automate_cmd.append("--enable-camera-display")

    # Define steps dynamically according to user configuration
    steps = []
    
    # Conditionally add CARLA Server step (only when not in mock mode)
    if not carla_mock:
        steps.append({
            "name": "CARLA Server (NVIDIA option)",
            "cwd": "$HOME/autoverse",
            "cmd": ["just", "server-nvidia"],
            "kill_patterns": ["just server-nvidia"],
            "startup_delay_sec": 2.0,
        })

    # Conditionally add modules based on the communication protocol
    if only_zenoh_modules:
        steps.append({
            "name": "VCU Module Python",
            "cwd": "$HOME/autoverse/vecu/vcu_zenoh/src",
            "cmd": [PYTHON, "main.py"],
            "kill_patterns": [
                "vecu/vcu_zenoh/src/main.py",
                "vcu_zenoh/src/main.py",
            ],
            "startup_delay_sec": 1.0,
        })

        steps.append({
            "name": "ADAS Module Python Zenoh",
            "cwd": "$HOME/autoverse/vecu/simulink/pid_controller",
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
                "cwd": "$HOME/autoverse/vecu/vcu_zenoh/src",
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
        #         "cwd": "$HOME/autoverse/bridges/can/can-zenoh-bridge-python/src",
        #         "cmd": [PYTHON, "bridge.py", "config/config.json"],
        #         "kill_patterns": [
        #             "bridges/can/can-zenoh-bridge-python/src",
        #             "src/bridge.py"
        #         ],
        #         "startup_delay_sec": 1.0,
        #     })

        steps.append({
            "name": "Zenoh to SOME-IP bridge",
            "cwd": "$HOME/autoverse/bridges/someip/zenoh-someip-bridge",
            "cmd": ["./scripts/ctl.sh",  "start"],
            "stp": ["./scripts/ctl.sh",  "stop"],
            "kill_patterns": [],
            "startup_delay_sec": 1.0,
        })

        steps.append({
            "name": "ADAS Module S-CORE",
            "cwd": "$HOME/autoverse/vecu/s-core",
            "cmd": ["./ctl.sh",  "start"],
            "stp": ["./ctl.sh",  "stop"],
            "kill_patterns": [],
            "startup_delay_sec": 5.0,
        })
    
         
    # Common modules always used
    steps.append({
        "name": "Vehicle Manual Control module",
        "cwd": "$HOME/autoverse/bridges/carla/examples",
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
        "cwd": "$HOME/autoverse/bridges/carla/examples",
        "cmd": automate_cmd,
        "kill_patterns": [
            "bridges/carla/examples/automate.py",
            "/examples/automate.py",
            "python.*automate.py",
        ],
        "startup_delay_sec": 1.0,
    })
    
    # Automatically add step numbers to names
    for i, step in enumerate(steps, start=1):
        step["name"] = f"Step {i}: {step['name']}"
    
    return steps

LOG_DIR = Path.home() / ".cache" / "autoverse-runner" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

GRACEFUL_TERM_TIMEOUT = 10.0
FORCE_KILL_TIMEOUT = 3.0

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

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=stdout_f,
        stderr=stderr_f,
        preexec_fn=os.setsid,  # new process group for clean termination
        env=env,
    )

    ok(f"{name} started with PID {proc.pid}")
    return proc, stdout_path, stderr_path

children: List[Tuple[str, subprocess.Popen]] = []

def stop_process(name: str, cwd: str, cmd: List[str])-> Tuple[subprocess.Popen, Path, Path]:
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

    ok(f"{name} stopped with PID {proc.pid}")
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
    # First stop our child processes (includes CARLA client from Step 3)
    if children:
        warn("Shutting down all child processes...")
        for name, proc in children:
            terminate_process(proc, name)
        ok("All child processes stopped.")
    # Then ensure CARLA server is gone (even if it wasn't our child)
    kill_carla_processes("CARLA (shutdown)")

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

    args = parser.parse_args()
    
    # Build steps with optional arguments
    STEPS = build_steps(
        carla_mock=args.carla_mock,
        enable_camera_display=args.enable_camera_display,
        only_zenoh_modules=args.only_zenoh_modules,
        vcu_zenoh= args.vcu_zenoh
    )
    
    # Log configuration
    info("=" * 60)
    info("Autoverse Supervisor Starting")
    info("=" * 60)
    info(f"CARLA Mock Mode: {'Enabled' if args.carla_mock else 'Disabled'}")
    # info(f"Camera Display rendering: {'Enabled' if args.enable_camera_display else 'Disabled'}")
    info(f"Use only Zenoh Modules: {'True' if args.only_zenoh_modules else 'False'}")
    info(f"Use VCU Zenoh Module: {'True' if args.vcu_zenoh else 'False'}")
    info(f"Logs Directory:")
    info(f"     {LOG_DIR}")
    info("=" * 60)
    
    # Cleanup on exit/signals
    atexit.register(shutdown_all)
    signal.signal(signal.SIGINT, lambda *_: shutdown_all())
    signal.signal(signal.SIGTERM, lambda *_: shutdown_all())

    # 0) Ensure CARLA server isn't already running from a previous session
    kill_carla_processes("CARLA (pre-start)")

    # 1) Stop previous instances of our steps
    info("Ensuring previous instances are not running...")
    for step in STEPS:
        if "stp" in step:
            stop_process(name=step["name"], cwd=step["cwd"], cmd=step["stp"])
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
    for step in STEPS:
        try:
            proc, out_log, err_log = start_process(
                step["name"], step["cwd"], step["cmd"], step3_monitor=step3_monitor
            )
            children.append((step["name"], proc))
            time.sleep(step.get("startup_delay_sec", 0.0))
        except Exception as e:
            err(f"Failed to start {step['name']}: {e}")
            continue

    if not children:
        err("No processes started. Exiting.")
        return 1

    info("Supervisor is now running. Press Ctrl-C to stop everything.")
    info(f"Logs directory:")
    info(f"     {LOG_DIR}")

    # 4) Supervise loop
    try:
        while True:
            for name, proc in list(children):
                rc = proc.poll()
                if rc is not None:
                    warn(f"{name} exited with code {rc}. See logs for details.")
                    children.remove((name, proc))
            if not children:
                warn("All child processes have exited.")
                break
            time.sleep(1.0)
    finally:
        # Send stop comand to all steps (copied from step 1)
        info("Ensuring previous instances are not running...")
        for step in STEPS:
            if "stp" in step:
                stop_process(name=step["name"], cwd=step["cwd"], cmd=step["stp"])

        shutdown_all()

    return 0

if __name__ == "__main__":
    sys.exit(main())
