#!/usr/bin/env python3
"""Exercise native OpenSOVD using an explicitly labelled local observation fixture."""
import argparse
import hashlib
import json
import signal
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    results, requests = [], []
    def check(name, condition):
        results.append({"id": name, "status": "passed" if condition else "failed"})
        if not condition:
            raise AssertionError(name)
    def request(url):
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read())
        requests.append({"url": url, "observed_at_monotonic_ns": time.monotonic_ns(), "response": data})
        return data

    code = 0
    try:
        with tempfile.TemporaryDirectory(prefix="sdv-http-fixture-") as directory:
            path = str(Path(directory) / "receiver.sock")
            with socket.socket() as reservation:
                reservation.bind(("127.0.0.1", 0))
                port = reservation.getsockname()[1]
            base = f"http://127.0.0.1:{port}/sovd"
            command = [str(args.binary.resolve()), "--socket", path, "--listen", f"127.0.0.1:{port}",
                       "--base-uri", base, "--speed-timeout-ms", "100", "--heartbeat-timeout-ms", "200"]
            with (args.output / "server.txt").open("w") as log:
                process = subprocess.Popen(command, stdout=log, stderr=log)
                try:
                    deadline = time.monotonic() + 10
                    while True:
                        try:
                            root = request(base + "/v1")
                            break
                        except OSError:
                            if process.poll() is not None or time.monotonic() >= deadline:
                                raise RuntimeError("native server unavailable")
                            time.sleep(.025)
                    app = request(request(root["apps"])["items"][0]["href"])
                    metadata = request(app["data"])["items"]
                    check("discovered-actual-resource", any(item["id"] == "cc.observation" for item in metadata))
                    # Pinned implementation lists resource IDs; it advertises the data collection link.
                    uri = app["data"] + "/cc.observation"
                    view = request(uri)["data"]["value"]
                    check("startup-unknown", view["receiver_state"] == "unknown" and view["observation"] is None)
                    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
                    accepted = time.monotonic_ns()
                    observation = {"schema_version": 1, "source_instance": "cruise-control",
                        "source_session": "explicit-http-fixture", "boot_id": boot,
                        "clock_domain": "linux-clock-monotonic", "observed_at_monotonic_ns": accepted,
                        "received_at_monotonic_ns": accepted, "last_accepted_at_monotonic_ns": accepted,
                        "vehicle_speed": 42.5, "target_speed": 45.0, "cc_state": "engaged",
                        "software_identity": "fixture-only", "sample_id": None,
                        "integrity_result": "not_available", "acceptance_kind": "decoded_by_consumer"}
                    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sender:
                        def publish(value):
                            sender.sendto(json.dumps(value).encode(), path)
                            time.sleep(.015)
                        publish(observation)
                        view = request(uri)["data"]["value"]
                        check("fixture-value-roundtrip", view["observation"]["vehicle_speed"] == 42.5
                              and view["observation"]["cc_state"] == "engaged" and view["speed_unit"] == "km/h")
                        check("unavailable-integrity-labelled", view["observation"]["integrity_result"] == "not_available")
                        time.sleep(.11)
                        observation["observed_at_monotonic_ns"] = time.monotonic_ns()
                        publish(observation)
                        view = request(uri)["data"]["value"]
                        check("unrelated-heartbeat-speed-stale", view["receiver_state"] == "available"
                              and view["freshness_state"] == "stale" and view["observation"]["cc_state"] == "engaged")
                        invalid = {**observation, "boot_id": "wrong-boot"}
                        publish(invalid)
                        check("invalid-provenance-rejected", request(uri)["data"]["value"]["rejected_observations"] >= 1)
                    time.sleep(.21)
                    view = request(uri)["data"]["value"]
                    check("collector-loss-unknown", view["receiver_state"] == "stale" and view["freshness_state"] == "unknown")
                finally:
                    process.send_signal(signal.SIGINT)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                check("test-owned-socket-cleaned", not Path(path).exists())
    except (OSError, RuntimeError, AssertionError, KeyError, subprocess.SubprocessError) as exc:
        results.append({"id": "smoke-execution", "status": "failed", "reason": str(exc)})
        code = 1
    manifest = {"schema_version": 1, "mode": "fixture observations with real native OpenSOVD HTTP server",
                "work_classification": "prepared", "receiver": "fixture; not S-CORE/CARLA",
                "native_faults": False, "openDuT_path": False,
                "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest() if args.binary.is_file() else None,
                "budgets": {"speed_ms": 100, "heartbeat_ms": 200, "engineering_validated": False}}
    for name, data in (("manifest", manifest), ("requests", requests),
                       ("results", {"status": "passed" if code == 0 else "failed", "checks": results})):
        (args.output / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
