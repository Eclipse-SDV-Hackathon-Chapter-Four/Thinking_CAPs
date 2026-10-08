#!/usr/bin/env python3
"""L2 integration: fixture inputs, unchanged bridge, real gateway/receiver/OpenSOVD."""
import argparse
import hashlib
import json
import os
import signal
import socket
import subprocess
import tempfile
import threading
import time
import urllib.request
import uuid
from pathlib import Path

import zenoh


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True, help="Native diagnostic server")
    parser.add_argument("--score-source", type=Path, required=True, help="Instrumented cc_s-core worktree")
    parser.add_argument("--baseline-source", type=Path, required=True, help="Untouched original cc_s-core")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    repo = Path(__file__).resolve().parents[4]
    name = "sdv-receiver-" + uuid.uuid4().hex[:10]
    names, records, checks, returns = [], [], [], []
    mutex = threading.Lock()
    code = 0
    server = None
    session = None
    def run(command, timeout=30):
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f"{command[0:3]}: {result.stderr[-2000:]}")
        return result.stdout.strip()
    def check(identifier, condition):
        checks.append({"id": identifier, "status": "passed" if condition else "failed"})
        if not condition:
            raise AssertionError(identifier)
    def request(uri):
        with urllib.request.urlopen(uri, timeout=2) as response:
            value = json.loads(response.read())
        records.append({"observed_at_monotonic_ns": time.monotonic_ns(), "uri": uri, "response": value})
        return value

    with tempfile.TemporaryDirectory(prefix="sdv-real-receiver-") as directory:
        local = Path(directory)
        sock = local / "receiver.sock"
        with socket.socket() as free:
            free.bind(("127.0.0.1", 0))
            port = free.getsockname()[1]
        base = f"http://127.0.0.1:{port}/sovd"
        try:
            # Refuse to compete with the live vehicle stack on its protocol ports.
            for container in ("bridge-e2e", "docker_setup-adas_score-1"):
                status = run(["docker", "inspect", "--format", "{{.State.Running}}", container])
                if status == "true":
                    raise RuntimeError("existing vehicle stack is running; refuse protocol collision")
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 7447))
            config = zenoh.Config.from_json5(json.dumps({"mode": "peer",
                "listen": {"endpoints": ["tcp/127.0.0.1:7447"]},
                "scouting": {"multicast": {"enabled": False}}}))
            session = zenoh.open(config)
            def returned(sample):
                with mutex:
                    returns.append({"key": str(sample.key_expr), "payload": sample.payload.to_bytes().decode(),
                                    "observed_at_monotonic_ns": time.monotonic_ns()})
            subscriptions = [session.declare_subscriber(key, returned) for key in
                ("adas/cruise_control/target_speed", "adas/cruise_control/thruttle_req")]
            log = (args.output / "diagnostics.txt").open("w")
            server = subprocess.Popen([str(args.binary.resolve()), "--socket", str(sock),
                "--listen", f"127.0.0.1:{port}", "--base-uri", base,
                "--speed-timeout-ms", "300", "--heartbeat-timeout-ms", "300"], stdout=log, stderr=log)
            deadline = time.monotonic() + 5
            while not sock.exists() and time.monotonic() < deadline:
                time.sleep(.02)
            root = request(base + "/v1")
            app = request(request(root["apps"])["items"][0]["href"])
            uri = app["data"] + "/cc.observation"
            check("startup-unknown", request(uri)["data"]["value"]["receiver_state"] == "unknown")
            digest = run(["docker", "run", "--rm", "--network", "none", "--entrypoint", "sha256sum",
                "-v", str(args.score_source.resolve()) + ":/home/source:ro",
                "-v", "eclipse-s-core-bazel-cache:/var/cache/bazel:ro", "docker_setup-adas_score:latest",
                "/home/source/bazel-bin/score/cruise_control/cruise_control_main"]).split()[0]
            run(["docker", "run", "-d", "--name", name + "-score", "--network", "host",
                "--security-opt", "seccomp=unconfined", "--shm-size", "2g", "--entrypoint", "bash",
                "-v", str(args.score_source.resolve()) + ":/home/source:ro",
                "-v", str(args.baseline_source.resolve()) + ":/home/baseline:ro",
                "-v", "eclipse-s-core-bazel-cache:/var/cache/bazel:ro", "-v", str(local) + ":/tmp",
                "-v", str(repo / "contributions/eclipse-opensovd/OpenSOVD/scripts/receiver_container_entrypoint.sh") + ":/entrypoint.sh:ro",
                "-e", "SCORE_DIAGNOSTIC_SOCKET=/tmp/receiver.sock", "-e", "SCORE_BUILD_IDENTITY=sha256:" + digest,
                "docker_setup-adas_score:latest", "/entrypoint.sh"])
            names.append(name + "-score")
            run(["docker", "run", "-d", "--name", name + "-bridge", "--network", "host",
                "--entrypoint", "bash", "-v", str(local) + ":/tmp",
                "-e", "ZENOH_MODE=peer", "-e", "ZENOH_CONNECT=tcp/127.0.0.1:7447",
                "zenoh-someip-bridge:latest", "-c", "cd build && exec ./gateway"])
            names.append(name + "-bridge")
            started = time.monotonic()
            def publish(duration, speed=42.5, engage="false"):
                end = time.monotonic() + duration
                while time.monotonic() < end:
                    session.put("vehicle/status/clock_status", str(time.monotonic() - started))
                    if speed is not None:
                        session.put("vehicle/status/velocity_status", str(speed))
                    session.put("vcu/control/cc_engage_sts", engage)
                    time.sleep(.05)
            publish(12)
            view = request(uri)["data"]["value"]
            check("actual-receiver-speed", view["receiver_state"] == "available"
                  and view["freshness_state"] == "fresh" and view["observation"]["vehicle_speed"] == 42.5)
            check("actual-artifact-identity", view["observation"]["software_identity"] == "sha256:" + digest)
            publish(1.5, engage="true")
            view = request(uri)["data"]["value"]
            check("actual-controller-engagement", view["observation"]["cc_state"] == "engaged"
                  and view["observation"]["target_speed"] == 42.5)
            publish(1.0, speed=40.0, engage="true")
            with mutex:
                check("preserved-control-return", any(item["key"].endswith("thruttle_req")
                      and float(item["payload"]) > 0 for item in returns))
            publish(.6, speed=None, engage="true")
            view = request(uri)["data"]["value"]
            check("speed-only-loss-attributed", view["receiver_state"] == "available"
                  and view["freshness_state"] == "stale" and view["observation"]["cc_state"] == "engaged")
            publish(.5, speed=39.0, engage="true")
            view = request(uri)["data"]["value"]
            check("actual-input-recovery", view["freshness_state"] == "fresh"
                  and view["observation"]["vehicle_speed"] == 39.0)
            server.send_signal(signal.SIGINT)
            server.wait(timeout=5)
            with mutex:
                before = len(returns)
            publish(.6, speed=38.0, engage="true")
            with mutex:
                check("diagnostics-loss-control-continues", len(returns) > before)
        except (OSError, RuntimeError, AssertionError, KeyError, subprocess.SubprocessError) as exc:
            checks.append({"id": "integration-execution", "status": "failed", "reason": str(exc)})
            code = 1
        finally:
            for container in reversed(names):
                subprocess.run(["docker", "rm", "-f", container], capture_output=True, timeout=20)
            if server is not None and server.poll() is None:
                server.send_signal(signal.SIGINT)
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill(); server.wait(timeout=5)
            if session is not None:
                session.close()
            # Retain scoped application messages; exclude daemon socket-table dumps/unrelated traffic.
            for filename in ("receiver.txt", "gatewayd.txt", "someipd.txt"):
                path = local / filename
                if path.exists():
                    lines = path.read_text(errors="replace").splitlines()
                    (args.output / filename).write_text("\n".join(line for line in lines
                        if "[CRUI]" in line or "ERROR" in line or "error:" in line) + "\n")
            if names:
                # Restore ownership only inside this run's private bind mount so ordinary
                # TemporaryDirectory cleanup can remove IPC directories created by container root.
                subprocess.run(["docker", "run", "--rm", "--network", "none", "--entrypoint", "chown",
                    "-v", str(local) + ":/cleanup", "docker_setup-adas_score:latest", "-R",
                    f"{os.getuid()}:{os.getgid()}", "/cleanup"], capture_output=True, timeout=20)
            manifest = {"schema_version": 1, "mode": "L2 fixture inputs; real native receiver/bridge/gateway/OpenSOVD",
                        "work_classification": "prepared", "CARLA": "not run", "openDuT": "not run",
                        "native_faults": False, "clock_domain": "linux-clock-monotonic",
                        "budgets": {"speed_ms": 300, "heartbeat_ms": 300, "engineering_validated": False},
                        "source_worktree": str(args.score_source), "baseline_source": str(args.baseline_source)}
            for filename, data in (("manifest", manifest), ("requests", records), ("return-events", returns),
                ("results", {"status": "passed" if code == 0 else "failed", "checks": checks})):
                (args.output / (filename + ".json")).write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
