#!/usr/bin/env python3
"""Read-only readiness audit. Available dependencies are not an E2E verdict."""
import argparse
import hashlib
import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPOSITORIES = {
    "autoverse": "autoverse",
    "bridge": "autoverse/bridges/someip/zenoh-someip-bridge",
    "s-core": "autoverse/vecu/s-core",
    "carla-bridge": "carla-simulator-bridge",
    "opensovd-core": "opensovd-core",
    "opendut": "opendut",
    "cluster": "digital-cluster-vecu",
}
CONFIGURATIONS = [
    "autoverse/run_autoverse.py",
    "autoverse/vecu/s-core/cc_s-core/MODULE.bazel",
    "autoverse/vecu/s-core/cc_s-core/score/cruise_control/config/mw_com_config.json",
    "autoverse/vecu/s-core/cc_s-core/deployment/xverse/docker_setup/docker-compose.yaml",
    "autoverse/vecu/s-core/cc_s-core/deployment/xverse/docker_setup/vsomeip.json",
    "autoverse/vecu/s-core/cc_s-core/tests/integration/gateway_mw_someip_config.json",
]


def command(args, cwd=None, timeout=15):
    try:
        result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return {"command": args, "exit_code": result.returncode,
                "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": args, "exit_code": None, "error": str(exc)}


def repository(path):
    if not path.is_dir():
        return {"path": str(path), "status": "blocked", "reason": "checkout absent"}
    rev = command(["git", "rev-parse", "HEAD"], path)
    if rev["exit_code"] != 0:
        return {"path": str(path), "status": "blocked", "reason": "revision unavailable"}
    status = command(["git", "status", "--porcelain"], path)
    diff = command(["git", "diff", "HEAD", "--binary"], path)
    return {"path": str(path), "status": "inspected", "revision": rev["stdout"],
            "worktree_status": status["stdout"].splitlines(),
            "tracked_diff_sha256": hashlib.sha256(diff.get("stdout", "").encode()).hexdigest()}


def exit_code(checks):
    states = {check["status"] for check in checks}
    if "failed" in states:
        return 1
    return 0 if states == {"passed"} else 2


def audit(workspace):
    repos = {name: repository(workspace / relative) for name, relative in REPOSITORIES.items()}
    files = {}
    for relative in CONFIGURATIONS:
        path = workspace / relative
        files[relative] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()} if path.is_file() else {"status": "missing"}
    checks = [{"id": "checkout-" + name, "status": "passed" if value["status"] == "inspected" else "blocked",
               "reason": value.get("reason", "revision inspected; execution not established")}
              for name, value in repos.items()]
    for port, name in ((2000, "carla-rpc"),):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=2):
                checks.append({"id": name, "status": "passed", "reason": "TCP reachable; vehicle behavior not tested"})
        except OSError as exc:
            checks.append({"id": name, "status": "blocked", "reason": str(exc)})
    docker = command(["docker", "ps", "--format", "{{.Names}}"])
    names = docker.get("stdout", "").splitlines()
    for name in ("bridge-e2e", "docker_setup-adas_score-1"):
        checks.append({"id": name, "status": "passed" if name in names else "blocked",
                       "reason": "running; function not tested" if name in names else "container not running"})
    tools = {name: command(args) for name, args in {
        "python": ["python3", "--version"], "rust": ["rustc", "--version"],
        "cargo": ["cargo", "--version"], "docker": ["docker", "--version"],
    }.items()}
    images = {}
    for name in ("zenoh-someip-bridge:latest", "docker_setup-adas_score:latest"):
        result = command(["docker", "image", "inspect", name, "--format", "{{.Id}}"])
        images[name] = result.get("stdout") if result["exit_code"] == 0 else {"status": "unavailable"}
    manifest = {"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(),
                "work_classification": "prepared", "mode": "read-only readiness audit",
                "repositories": repos, "configurations": files, "tools": tools, "images": images,
                "limitations": ["No closed-loop vehicle behavior tested", "No openDuT path established", "AAOS FOTA deferred by user"]}
    code = exit_code(checks)
    return manifest, {"schema_version": 1, "status": {0: "passed", 1: "failed", 2: "blocked"}[code],
                      "claim": "dependency readiness only", "checks": checks}, code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path, default=Path.home())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Refuse overwrites to preserve previous evidence.
    args.output.mkdir(parents=True, exist_ok=False)
    manifest, results, code = audit(args.workspace_root.resolve())
    for name, value in (("manifest", manifest), ("results", results)):
        (args.output / f"{name}.json").write_text(json.dumps(value, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
