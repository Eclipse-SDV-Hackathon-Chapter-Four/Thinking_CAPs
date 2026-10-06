#!/usr/bin/env python3
"""Fixture vehicle inputs across real managed openDuT Ethernet to the native receiver."""
import argparse
import hashlib
import json
import os
import statistics
from pathlib import Path
import signal
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import uuid

import zenoh

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from opendut_testbench import Bench, LABEL, REPO, run


def stream_stopped_after_cut(view, cut_ns, allowance_ns):
    """Allow bounded in-flight delivery; reject acceptance continuing past the cut."""
    accepted = (view.get("observation") or {}).get("last_accepted_at_monotonic_ns")
    return (view.get("receiver_state") == "available"
            and view.get("freshness_state") == "stale"
            and isinstance(accepted, int) and not isinstance(accepted, bool)
            and 0 < accepted <= cut_ns + allowance_ns)


def packets(path):
    """Summarize bounded Ethernet pcap without retaining payloads in Git."""
    data = path.read_bytes()
    endian = "<" if data[:4] in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1") else ">"
    if len(data) < 24 or struct.unpack_from(endian + "I", data, 20)[0] != 1:
        raise RuntimeError("expected Ethernet pcap")
    offset, count, gre, messages = 24, 0, 0, {}
    while offset + 16 <= len(data):
        size = struct.unpack_from(endian + "I", data, offset + 8)[0]
        payload = data[offset + 16:offset + 16 + size]
        offset += 16 + size
        count += 1
        if len(payload) < 34 or payload[12:14] != b"\x08\x00":
            continue
        ip = payload[14:]
        header = (ip[0] & 15) * 4
        if ip[9] == 47:
            gre += 1
        if ip[9] != 17 or len(ip) < header + 24:
            continue
        source_port, dest_port = struct.unpack_from("!HH", ip, header)
        if dest_port == 30490 or source_port == 30490:
            continue
        # vSomeIP can coalesce several SOME/IP messages into one UDP datagram.
        position = header + 8
        while position + 16 <= len(ip):
            service, event, length = struct.unpack_from("!HHI", ip, position)
            if length < 8 or position + 8 + length > len(ip):
                break
            key = f"{service}/{event}"
            messages[key] = messages.get(key, 0) + 1
            position += 8 + length
    return {"packets": count, "gre_packets": gre, "someip_ids": messages,
            "pcap_sha256": hashlib.sha256(data).hexdigest(), "payload_archive": "private; not committed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--score-source", type=Path, required=True)
    parser.add_argument("--baseline-source", type=Path, required=True)
    parser.add_argument("--bridge-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fail-after-disturbance", action="store_true", help="Exercise restoration/cleanup after a deliberate failed assertion")
    parser.add_argument("--fault-lifecycle", action="store_true", help="Require the native reporter/DFM/write-through profile")
    parser.add_argument("--inputs", type=Path, help="Explicit local tool/image inputs; required by the campaign wrapper")
    parser.add_argument("--carla-config", type=Path, help="Use an owned real CARLA plant and existing X-Verse/VCU instead of fixture speed")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    bench = Bench(args.state)
    if bench.state is None or bench.state["phase"] != "deployed":
        raise RuntimeError("real deployed testbench required")
    class EventJournal(list):
        def append(self, event):
            super().append(event)
            with (args.output / 'events-live.jsonl').open('a') as journal:
                journal.write(json.dumps(dict(event, clock_domain='linux-clock-monotonic')) + '\n')
    checks, records, returned, captures, names, events = [], [], [], [], [], EventJournal()
    baseline, baseline_times = {}, []
    executable_hashes = "not reached"
    capture_processes, session, tunnel = [], None, None
    mutex = threading.Lock()
    label = LABEL + "=" + bench.state["run_id"]
    identity = "sdv-net-" + uuid.uuid4().hex[:10]
    # Resolve actual IDs once; do not run mutable tags after resolution.
    inputs = json.loads(args.inputs.read_text()) if args.inputs else {}
    score_image = run(["docker", "image", "inspect", "--format", "{{.Id}}", inputs.get("score_image", "docker_setup-adas_score:latest")])
    bridge_image = run(["docker", "image", "inspect", "--format", "{{.Id}}", inputs.get("bridge_image", "zenoh-someip-bridge:latest")])
    cache_volume = inputs.get("bazel_volume", "eclipse-s-core-bazel-cache")
    plant = None
    def interrupted(signum, frame):
        raise RuntimeError("runner interrupted by signal " + str(signum))
    previous_handlers = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGINT, signal.SIGTERM)}
    code = 0
    def check(identifier, condition):
        checks.append({"id": identifier, "status": "passed" if condition else "failed"})
        if not condition:
            raise AssertionError(identifier)
    def request(uri, timeout=2):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(uri, timeout=timeout) as response:
            value = json.loads(response.read())
        records.append({"observed_at_monotonic_ns": time.monotonic_ns(), "uri": uri, "response": value})
        return value
    def container(suffix, peer, image, flags, command):
        name = identity + "-" + suffix
        # Register before creation: cancellation can interrupt docker run after
        # the daemon has created the container but before it returns to us.
        names.append(name)
        run(["docker", "run", "-d", "--name", name, "--label", label, "--network", "container:" + bench.name(peer),
             *flags, image, *command])
        return name
    with tempfile.TemporaryDirectory(prefix="sdv-opendut-apps-") as directory:
        private = Path(directory)
        for suffix in ("a", "b"):
            (private / suffix).mkdir()
        try:
            state = bench.status()
            (args.output / "deployment.json").write_text(json.dumps(state, indent=2) + "\n")
            check("two-real-peers", len(state["peers"]) == 2 and all(p["status"] == "Connected" for p in state["peers"]))
            check("one-real-cluster", len(state["clusters"]) == 1)
            for suffix in ("a", "b"):
                links = state["interfaces"][suffix]
                active_gre = [link for link in links if link["ifname"].startswith("gre-") and link.get("master") == "br-opendut"]
                check("managed-bridge-" + suffix, len(active_gre) == 1 and any(link["ifname"] == "dut0" and
                      link.get("master") == "br-opendut" for link in links))
                if suffix == "a":
                    tunnel = active_gre[0]["ifname"]
                for interface, kind, expression in (("dut0local", "dut", "udp port 30490 or udp port 30511 or udp port 30513"),
                                                   ("eth0", "gre", "ip proto 47")):
                    filename = identity + "-" + kind + ".pcap"
                    pidfile = "/run/opendut/" + identity + "-" + kind + ".pid"
                    command = ["docker", "exec", bench.name(suffix), "sh", "-c", 'echo $$ > "$1"; shift; exec timeout 180 "$@"',
                               "capture", pidfile, "tcpdump", "-U", "-nn", "-s", "0",
                               "-i", interface, "-w", "/run/opendut/" + filename, expression]
                    capture_processes.append((suffix, bench.path / suffix / Path(pidfile).name,
                        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
                    captures.append((suffix, kind, bench.path / suffix / filename))
            gateway = json.loads((args.bridge_source / "config/vsomeip.gateway.json").read_text())
            gateway.update(unicast="192.168.123.101", routing="gateway")
            score = json.loads((args.score_source / "deployment/xverse/docker_setup/vsomeip.json").read_text())
            score.update(unicast="192.168.123.102", routing="someipd")
            # Native daemon requests RT_UNKNOWN; explicit event configuration must
            # match the unchanged bridge's RT_UNRELIABLE offer/request behavior.
            input_service = gateway["services"][0]
            input_service["events"] = [{"event": event, "is_field": False, "is_reliable": False} for event in range(30500, 30504)]
            input_service["eventgroups"] = [{"eventgroup": event, "events": [event]} for event in range(30500, 30504)]
            for event in score["services"][0]["events"]:
                event["is_reliable"] = False
            score["services"].append(dict(input_service, unicast="192.168.123.101"))
            gateway["services"].append(dict(score["services"][0], unicast="192.168.123.102"))
            for config in (gateway, score):
                for service in config["services"]:
                    # vSomeIP's UDP endpoint is a scalar, unlike reliable.port.
                    if isinstance(service.get("unreliable"), dict):
                        service["unreliable"] = service["unreliable"]["port"]
            for name, value in (("bridge-overlay", gateway), ("score-overlay", score)):
                (private / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
                (args.output / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
            network_config = json.loads((args.score_source / "tests/integration/gateway_mw_someip_config.json").read_text())
            for service in network_config["service_types"]:
                if service["service_id"] == 3000:
                    service["service_version_major"] = 0  # unchanged bridge subscribes with DEFAULT_MAJOR=0
            (private / "network-overlay.json").write_text(json.dumps(network_config, indent=2) + "\n")
            (args.output / "network-overlay.json").write_text(json.dumps(network_config, indent=2) + "\n")
            compiler = inputs.get("flatc", "/var/cache/bazel/e97fe0dd2c3d7fe69841bf89910a450d/execroot/_main/bazel-out/k8-opt-exec-ST-d57f47055a04/bin/external/flatbuffers+/flatc")
            schema = inputs.get("gateway_schema", "/var/cache/bazel/e97fe0dd2c3d7fe69841bf89910a450d/external/score_someip_gateway+/score/config/mw_someip_config.fbs")
            run(["docker", "run", "--rm", "--network", "none", "--entrypoint", compiler,
                 "-v", cache_volume + ":/var/cache/bazel:ro", "-v", str(private) + ":/out",
                 score_image, "--binary", "-o", "/out", schema, "/out/network-overlay.json"])
            session = zenoh.open(zenoh.Config.from_json5(json.dumps({"mode": "peer", "listen": {"endpoints": ["tcp/172.30.77.1:7447"]},
                                "scouting": {"multicast": {"enabled": False}}})))
            def receive(sample):
                with mutex:
                    returned.append({"key": str(sample.key_expr), "payload": sample.payload.to_bytes().decode(),
                                     "observed_at_monotonic_ns": time.monotonic_ns()})
            subscriptions = [session.declare_subscriber(key, receive) for key in
                             ("adas/cruise_control/target_speed", "adas/cruise_control/thruttle_req")]
            container("bridge", "a", bridge_image, ["--entrypoint", "bash", "-v", str(private / "a") + ":/tmp",
                "-v", str(private / "bridge-overlay.json") + ":/opt/bridge/config/vsomeip.gateway.json:ro",
                "-e", "ZENOH_MODE=peer", "-e", "ZENOH_CONNECT=tcp/172.30.77.1:7447"], ["-c", "cd build && exec ./gateway"])
            if args.carla_config:
                from owned_carla import OwnedCarla
                plant = OwnedCarla(json.loads(args.carla_config.read_text()), args.output)
                try:
                    plant.start()
                    events.append({"kind": "carla-plant-ready", "monotonic_ns": time.monotonic_ns()})
                except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                    if str(error).startswith("runner interrupted by signal"):
                        raise
                    raise RuntimeError("CARLA prerequisite unavailable: " + str(error)) from error
            base = "http://172.30.77.12:7691/sovd"
            def start_diagnostics():
                options = ["--socket", "/tmp/receiver.sock", "--listen", "172.30.77.12:7691", "--base-uri", base,
                           "--speed-timeout-ms", "300", "--heartbeat-timeout-ms", "300"]
                if args.fault_lifecycle:
                    options += ["--fault-storage", "/tmp/fault-storage", "--startup-grace-ms", "2000",
                                "--failure-debounce-ms", "100", "--recovery-hold-ms", "150", "--monitor-poll-ms", "25", "--fault-query-ms", "50"]
                return container("diag", "b", bench.state["peer_image"], ["--entrypoint", "/sdv-diagnostics", "-v",
                str(args.binary.resolve()) + ":/sdv-diagnostics:ro", "-v", str(private / "b") + ":/tmp"],
                options)
            diagnostic_name = start_diagnostics()
            deadline = time.monotonic() + 10
            while True:
                try:
                    root = request(base + "/v1")
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise RuntimeError("native diagnostic readiness deadline exceeded")
                    time.sleep(.1)
            app = request(request(root["apps"])["items"][0]["href"])
            uri = app["data"] + "/cc.observation"
            fault_uri = app["data"] + "/cc.fault-history"
            check("startup-unknown", request(uri)["data"]["value"]["receiver_state"] == "unknown")
            if args.fault_lifecycle:
                check("fault-startup-not-healthy", request(fault_uri)["data"]["value"]["assessment"]["state"] in ("unknown", "unavailable"))
            digest = run(["docker", "run", "--rm", "--network", "none", "--entrypoint", "sha256sum", "-v",
                str(args.score_source.resolve()) + ":/home/source:ro", "-v", cache_volume + ":/var/cache/bazel:ro",
                score_image, "/home/source/bazel-bin/score/cruise_control/cruise_control_main"]).split()[0]
            executable_hashes = run(["docker", "run", "--rm", "--network", "none", "--entrypoint", "sha256sum",
                "-v", str(args.baseline_source.resolve()) + ":/home/baseline:ro", "-v", cache_volume + ":/var/cache/bazel:ro",
                score_image, "/home/baseline/bazel-bin/tests/integration/gatewayd/gatewayd.exe",
                "/home/baseline/bazel-bin/tests/integration/someipd/someipd.exe"])
            container("score", "b", score_image, ["--security-opt", "seccomp=unconfined", "--shm-size", "2g", "--entrypoint", "bash",
                "-v", str(args.score_source.resolve()) + ":/home/source:ro", "-v", str(args.baseline_source.resolve()) + ":/home/baseline:ro",
                "-v", cache_volume + ":/var/cache/bazel:ro", "-v", str(private / "b") + ":/tmp",
                "-v", str(private / "score-overlay.json") + ":/vsomeip.json:ro", "-e", "VSOMEIP_CONFIGURATION=/vsomeip.json",
                "-v", str(private / "network-overlay.bin") + ":/network-overlay.bin:ro", "-e", "SCORE_GATEWAY_CONFIG=/network-overlay.bin",
                "-v", str(REPO / "OpenSOVD/scripts/receiver_container_entrypoint.sh") + ":/entrypoint.sh:ro",
                "-e", "SCORE_DIAGNOSTIC_SOCKET=/tmp/receiver.sock", "-e", "SCORE_BUILD_IDENTITY=sha256:" + digest], ["/entrypoint.sh"])
            start = time.monotonic()
            def publish(duration, speed=42.5, engage="false", measure=False):
                end = time.monotonic() + duration
                while time.monotonic() < end:
                    if plant:
                        plant.step(engage == "true")
                    else:
                        session.put("vehicle/status/clock_status", str(time.monotonic() - start))
                        if speed is not None:
                            session.put("vehicle/status/velocity_status", str(speed))
                        session.put("vcu/control/cc_engage_sts", engage)
                    if measure:
                        sample = request(uri)["data"]["value"]["observation"]["last_accepted_at_monotonic_ns"]
                        if sample is not None and (not baseline_times or sample != baseline_times[-1]):
                            baseline_times.append(sample)
                    time.sleep(.05)
            publish(15)
            view = request(uri)["data"]["value"]
            # Service discovery can finish just after the first publication
            # window on a busy SSD host. Keep sending real inputs while waiting
            # for an actual accepted observation; never substitute fixture data.
            deadline = time.monotonic() + 30
            while view["freshness_state"] != "fresh" and time.monotonic() < deadline:
                publish(.25)
                view = request(uri)["data"]["value"]
            check("receiver-through-opendut", view["freshness_state"] == "fresh" and
                  (abs(view["observation"]["vehicle_speed"] - plant.speed()) < 3 if plant else view["observation"]["vehicle_speed"] == 42.5))
            if plant:
                check("real-carla-moving-actor", plant.speed() >= 10 and len(plant.samples) >= 50)
            check("actual-controller-artifact", view["observation"]["software_identity"] == "sha256:" + digest)
            if args.fault_lifecycle:
                publish(4 if plant else 2, measure=True)
                gaps = [b-a for a,b in zip(baseline_times, baseline_times[1:])]
                check("baseline-timing-measured", len(gaps) >= 20 and max(gaps) < 300_000_000)
                baseline = {"accepted_samples": len(baseline_times), "median_gap_ns": statistics.median(gaps),
                            "maximum_gap_ns": max(gaps), "harness_sleep_ns": 50_000_000,
                            "timeout_ns": 300_000_000, "failure_debounce_ns": 100_000_000, "recovery_hold_ns": 150_000_000,
                            "startup_grace_ns": 2_000_000_000, "poll_ns": 25_000_000, "query_ns": 50_000_000,
                            "scheduling_allowance_ns": 100_000_000, "engineering_validated": False}
                nominal = request(fault_uri)["data"]["value"]
                check("native-dfm-nominal", nominal["query_state"] == "available" and nominal["report_stage"] == "passed"
                      and nominal["assessment"]["state"] == "healthy" and nominal["storage"]["acknowledged_mutations"] >= 1)
                check("data-only-fault-exposure", nominal["native_faults_resource"] is False)
            publish(1.5, engage="true")
            publish(1, speed=40, engage="true")
            view = request(uri)["data"]["value"]
            check("engagement-preserved", view["observation"]["cc_state"] == "engaged")
            with mutex:
                check("control-return-through-opendut", any(item["key"].endswith("thruttle_req") and float(item["payload"]) > 0 for item in returned))
            events.append({"kind": "diagnostic-stall-start", "monotonic_ns": time.monotonic_ns()})
            run(["docker", "kill", "--signal", "SIGSTOP", diagnostic_name])
            with mutex:
                return_count = len(returned)
            publish(.7, speed=40, engage="true")
            unreachable = False
            try:
                request(uri, timeout=.15)
            except OSError:
                unreachable = True
            with mutex:
                continuing = len(returned) > return_count + 5
            check("diagnostic-stall-control-continues", unreachable and continuing)
            run(["docker", "kill", "--signal", "SIGCONT", diagnostic_name])
            publish(.5, speed=40, engage="true")
            view = request(uri)["data"]["value"]
            check("diagnostic-stall-recovery", view["freshness_state"] == "fresh")
            events.append({"kind": "diagnostic-stall-end", "monotonic_ns": time.monotonic_ns()})
            if plant:
                check("real-carla-return-actuation", any(s["cc_engaged"] and s["applied_throttle"] > 0 for s in plant.samples))
                from owned_carla import correlate_return_actuation
                correlation = correlate_return_actuation(plant.samples, plant.throttle_damping, plant.throttle_limits)
                (args.output / "carla-control-return.json").write_text(json.dumps(correlation, indent=2) + "\n")
                check("real-carla-native-actuation-correlation", correlation["match_count"] >= correlation["required_matches"])
            events.append({"kind": "tunnel-down-request", "monotonic_ns": time.monotonic_ns(), "interface": tunnel})
            run(["docker", "exec", bench.name("a"), "ip", "link", "set", tunnel, "down"])
            cut_ns = time.monotonic_ns()
            events.append({"kind": "tunnel-down-complete", "monotonic_ns": cut_ns, "interface": tunnel})
            if args.fail_after_disturbance:
                raise AssertionError("deliberate failure after tunnel disturbance")
            publish(.8, speed=37, engage="true")
            view = request(uri)["data"]["value"]
            allowance_ns = baseline.get("scheduling_allowance_ns", 100_000_000)
            check("no-bypass-management-reachable", stream_stopped_after_cut(view, cut_ns, allowance_ns))
            # Use the final accepted sample, including any sample delivered while
            # the HTTP snapshot and link shutdown were in progress.
            before_loss = view["observation"]["last_accepted_at_monotonic_ns"]
            baseline["tunnel_down_complete_ns"] = cut_ns
            baseline["last_accepted_before_loss_ns"] = before_loss
            baseline["cut_acceptance_allowance_ns"] = allowance_ns
            if args.fault_lifecycle:
                failed = request(fault_uri)["data"]["value"]
                check("native-report-stored-query", failed["query_state"] == "available" and failed["report_stage"] == "failed"
                      and failed["fault"]["test_failed"] is True and failed["fault"]["confirmed"] is True
                      and failed["fault"]["occurrence_counter"] == 1 and failed["storage"]["last_error"] is None
                      and failed["storage"]["acknowledged_mutations"] >= 2)
                detector_delay = failed["assessment"]["detected_at_monotonic_ns"] - before_loss
                baseline["observed_detector_delay_from_last_accept_ns"] = detector_delay
                check("declared-detector-timing", 400_000_000 <= detector_delay <= 550_000_000 + baseline["maximum_gap_ns"])
                environment = failed["fault"]["environment"]
                check("actual-fault-attribution", environment["receiver"] == "cruise-control" and environment["stage"] == "failed"
                      and environment["session_hash"] == hashlib.sha256(view["observation"]["source_session"].encode()).hexdigest()
                      and environment["build_hash"] == hashlib.sha256(view["observation"]["software_identity"].encode()).hexdigest())
                events.append({"kind": "diagnostic-dfm-restart-request", "monotonic_ns": time.monotonic_ns()})
                run(["docker", "kill", "--signal", "SIGINT", diagnostic_name])
                deadline = time.monotonic() + 5
                while run(["docker", "inspect", "--format", "{{.State.Running}}", diagnostic_name]) == "true":
                    if time.monotonic() >= deadline:
                        raise RuntimeError("diagnostic graceful shutdown deadline exceeded")
                    time.sleep(.05)
                check("native-ipc-sigint-graceful", run(["docker", "inspect", "--format", "{{.State.ExitCode}}", diagnostic_name]) == "0"
                      and not (private / "b/receiver.sock").exists())
                logs = subprocess.run(["docker", "logs", diagnostic_name], capture_output=True, text=True, timeout=10, check=True)
                (args.output / "diagnostic-before-restart.log").write_text(logs.stdout + logs.stderr)
                run(["docker", "rm", diagnostic_name])
                names.remove(diagnostic_name)
                diagnostic_name = start_diagnostics()
                deadline = time.monotonic() + 10
                while True:
                    try:
                        restored = request(fault_uri)["data"]["value"]
                        if restored["query_state"] == "available": break
                    except OSError: pass
                    if time.monotonic() >= deadline:
                        raise RuntimeError("restarted native DFM query readiness deadline exceeded")
                    time.sleep(.05)
                events.append({"kind": "diagnostic-dfm-restart-complete", "monotonic_ns": time.monotonic_ns()})
                check("real-process-history-reload", restored["fault"]["test_failed"] is True and restored["fault"]["occurrence_counter"] == 1
                      and restored["fault"]["environment"] == environment and restored["storage"]["acknowledged_mutations"] == 0)
            events.append({"kind": "tunnel-up-request", "monotonic_ns": time.monotonic_ns(), "interface": tunnel})
            run(["docker", "exec", bench.name("a"), "ip", "link", "set", tunnel, "up"])
            events.append({"kind": "tunnel-up-complete", "monotonic_ns": time.monotonic_ns(), "interface": tunnel})
            publish(2, speed=39, engage="true")
            view = request(uri)["data"]["value"]
            check("tunnel-recovery-consumed", view["freshness_state"] == "fresh" and
                  (abs(view["observation"]["vehicle_speed"] - plant.speed()) < 3 if plant else view["observation"]["vehicle_speed"] == 39))
            if args.fault_lifecycle:
                recovered = request(fault_uri)["data"]["value"]
                check("native-recovery-retains-history", recovered["assessment"]["state"] == "healthy" and recovered["report_stage"] == "passed"
                      and recovered["fault"]["test_failed"] is False and recovered["fault"]["failed_since_clear"] is True
                      and recovered["fault"]["occurrence_counter"] == 1 and recovered["fault"]["environment"] == environment
                      and recovered["storage"]["acknowledged_mutations"] >= 1 and recovered["storage"]["last_error"] is None)
                check("actual-engagement-separate-from-recovery", view["observation"]["cc_state"] == "engaged")
                score_name = next(name for name in names if name.endswith("-score"))
                # T06 is abrupt collector loss while the upstream publisher runs.
                # Gracefully stopping the whole stack tears down SOME/IP before
                # the receiver and can legitimately report another stream fault.
                # Stop all receiver-container processes together instead; native
                # diagnostic SIGINT/SIGTERM behavior is checked separately.
                events.append({"kind": "receiver-container-loss", "signal": "SIGKILL",
                               "monotonic_ns": time.monotonic_ns()})
                run(["docker", "kill", "--signal", "SIGKILL", score_name])
                publish(.7, speed=41, engage="true")
                unavailable = request(fault_uri)["data"]["value"]
                check("collector-loss-is-unknown", unavailable["assessment"]["state"] == "unknown"
                      and unavailable["assessment"]["desired_stage"] is None and unavailable["query_state"] == "available"
                      and unavailable["fault"]["occurrence_counter"] == 1 and unavailable["fault"]["environment"] == environment)
                run(["docker", "kill", "--signal", "SIGTERM", diagnostic_name])
                deadline = time.monotonic() + 5
                while run(["docker", "inspect", "--format", "{{.State.Running}}", diagnostic_name]) == "true":
                    if time.monotonic() >= deadline:
                        raise RuntimeError("diagnostic SIGTERM shutdown deadline exceeded")
                    time.sleep(.05)
                check("native-ipc-sigterm-graceful", run(["docker", "inspect", "--format", "{{.State.ExitCode}}", diagnostic_name]) == "0"
                      and not (private / "b/receiver.sock").exists())
        except (OSError, RuntimeError, AssertionError, KeyError, subprocess.SubprocessError) as exc:
            code = 2 if str(exc).startswith("CARLA prerequisite unavailable:") else 1
            checks.append({"id": "execution", "status": "blocked" if code == 2 else "failed", "reason": str(exc)})
        finally:
            # Ignore repeated interrupts while restoring owned resources.
            for sig in previous_handlers:
                signal.signal(sig, signal.SIG_IGN)
            def cleanup_attempt(identifier, operation):
                nonlocal code
                try:
                    result = operation()
                    checks.append({"id": identifier, "status": "passed"})
                    return result
                except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
                    code = 1
                    checks.append({"id": identifier, "status": "failed", "reason": str(exc)})
                    return None
            if tunnel:
                cleanup_attempt("restore-tunnel", lambda: run(["docker", "exec", bench.name("a"), "ip", "link", "set", tunnel, "up"]))
            for suffix, pidfile, process in capture_processes:
                if pidfile.exists():
                    capture_pid = pidfile.read_text().strip()
                    if capture_pid.isdigit():
                        cleanup_attempt("stop-capture-" + suffix + "-" + pidfile.name, lambda: run(["docker", "exec", bench.name(suffix),
                            "sh", "-c", 'kill -INT "$1"', "stop-capture", capture_pid]))
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=5)
            time.sleep(.1)
            summaries = {}
            for suffix, kind, path in captures:
                if path.exists():
                    summary = cleanup_attempt("read-capture-" + suffix + "-" + kind, lambda: packets(path))
                    if summary is not None:
                        summaries[suffix + "-" + kind] = summary
            if code == 0:
                assertions = {"receiver-packet-provenance": summaries.get("b-dut", {}).get("someip_ids", {}).get("4660/30501", 0) > 0,
                              "return-packet-provenance": summaries.get("a-dut", {}).get("someip_ids", {}).get("3000/30601", 0) > 0,
                              "gre-packet-provenance": all(summaries.get(s + "-gre", {}).get("gre_packets", 0) > 0 for s in ("a", "b"))}
                for identifier, condition in assertions.items():
                    checks.append({"id": identifier, "status": "passed" if condition else "failed"})
                    code = max(code, int(not condition))
            for name in reversed(names):
                def remove_application():
                    existing = run(["docker", "ps", "-a", "--filter", "name=^/" + name + "$", "--format", "{{.ID}}"])
                    if not existing:
                        return  # Creation was interrupted before the daemon created it.
                    bench.ownership("container", name)
                    try:
                        if name.endswith("-bridge") or name.endswith("-diag"):
                            logs = subprocess.run(["docker", "logs", name], capture_output=True, text=True, timeout=10, check=True)
                            content = logs.stdout + logs.stderr
                            lines = content.splitlines()
                            retained = [line for line in lines if "0bb8" in line or "7788" in line or "7789" in line or
                                        "SUBSCR" in line or "error" in line or "ERROR" in line or "available" in line]
                            (args.output / (name.rsplit("-", 1)[-1] + ".txt")).write_text("\n".join(retained + lines[-100:]) + "\n")
                    finally:
                        run(["docker", "rm", "-f", name], timeout=20)
                cleanup_attempt("cleanup-" + name, remove_application)
            if session is not None:
                session.close()
            if plant is not None:
                cleanup_attempt("cleanup-owned-carla", plant.close)
            for filename in ("receiver.txt", "gatewayd.txt", "someipd.txt"):
                path = private / "b" / filename
                if path.exists():
                    (args.output / filename).write_text("\n".join(line for line in path.read_text(errors="replace").splitlines()
                        if "[CRUI]" in line or "ERROR" in line or "error:" in line or "[info]" in line or "[warning]" in line) + "\n")
            cleanup_attempt("restore-private-directory-owner", lambda: run(["docker", "run", "--rm", "--network", "none",
                "--entrypoint", "chown", "-v", str(private) + ":/cleanup", score_image, "-R", f"{os.getuid()}:{os.getgid()}", "/cleanup"]))
            manifest = {"schema_version": 1, "mode": "fixture vehicle inputs; real receiver and openDuT Ethernet", "work_classification": "prepared",
                        "CARLA": "not run", "VPN": "disabled local GRE underlay", "clock_domain": "linux-clock-monotonic",
                        "diagnostics_binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(), "score_image": score_image,
                        "bridge_image": bridge_image, "deployment_run_id": bench.state["run_id"], "budgets_ms": {"speed": 300, "heartbeat": 300, "provisional": True}}
            manifest["fault_lifecycle"] = args.fault_lifecycle
            manifest["baseline_timing"] = baseline
            manifest["native_daemon_executable_hashes"] = executable_hashes
            manifest["gateway_config_compiler"] = {"flatc": compiler, "schema": schema}
            if args.carla_config:
                manifest["mode"] = "real CARLA plant, existing X-Verse/VCU/bridge; real receiver and openDuT Ethernet; harness operator commands"
                manifest["CARLA"] = plant.identity if plant else "startup failed"
            for name, value in (("manifest", manifest), ("requests", records), ("return-events", returned), ("packets", summaries),
                                ("events", events),
                                ("results", {"status": "passed" if code == 0 else "blocked" if code == 2 else "failed", "checks": checks,
                                 "cleanup_contract": {"schema_version": 1,
                                     "application_checks": ["cleanup-" + name for name in names]}})):
                (args.output / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
            for sig, handler in previous_handlers.items():
                signal.signal(sig, handler)
    print(json.dumps(checks, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
