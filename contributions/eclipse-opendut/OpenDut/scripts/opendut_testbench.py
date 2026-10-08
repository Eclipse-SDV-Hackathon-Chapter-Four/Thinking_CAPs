#!/usr/bin/env python3
"""Owned, TLS-enabled, VPN-disabled two-peer openDuT 0.10.2 deployment."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time
import urllib.request
import uuid

REPO = Path(__file__).resolve().parents[2]
PINS = json.loads((REPO / "OpenDut/config/testbench/versions.json").read_text())
LABEL = "sdv.opendut.run"


def run(args, timeout=90, private=False):
    result = subprocess.run([str(arg) for arg in args], text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        detail = "private operation failed" if private else (result.stderr + result.stdout)[-2500:]
        raise RuntimeError(f"{args[:3]} exited {result.returncode}: {detail}")
    return result.stdout.strip()


class Bench:
    def __init__(self, path):
        self.path = path.resolve()
        self.file = self.path / "deployment.json"
        self.state = json.loads(self.file.read_text()) if self.file.exists() else None

    def save(self):
        temporary = self.file.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.state, indent=2) + "\n")
        temporary.chmod(0o600)
        temporary.replace(self.file)

    def prepare(self, management_subnet="172.30.77.0/24"):
        network = ipaddress.ip_network(management_subnet)
        if network.version != 4 or network.prefixlen != 24 or network.overlaps(ipaddress.ip_network("192.168.123.0/24")):
            raise RuntimeError("management subnet must be IPv4 /24, separate from the DUT subnet")
        self.path.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.path.stat().st_uid != os.getuid():
            raise RuntimeError("private state must belong to current user")
        self.path.chmod(0o700)
        if self.state is not None:
            raise RuntimeError("state already prepared; use it or choose a new private directory")
        archive = self.path / "0.10.2/cleo.tar.gz"
        archive.parent.mkdir(exist_ok=True)
        if not archive.exists():
            with urllib.request.urlopen(PINS["cleo_url"], timeout=60) as response, archive.open("wb") as dest:
                shutil.copyfileobj(response, dest)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != PINS["cleo_sha256"]:
            raise RuntimeError("CLEO archive digest mismatch")
        with tarfile.open(archive) as bundle:
            bundle.extractall(archive.parent, filter="data")
        cleo = next((path for path in archive.parent.rglob("opendut-cleo") if path.is_file()), None)
        if cleo is None:
            raise RuntimeError("CLEO executable absent")
        run(["docker", "pull", PINS["carl_image"]], timeout=600)
        run(["docker", "build", "-f", REPO / "OpenDut/config/testbench/Peer.Dockerfile", "-t",
             "sdv-opendut-peer:0.10.2", REPO / "OpenDut/config/testbench"], timeout=600)
        peer_image = run(["docker", "image", "inspect", "--format", "{{.Id}}", "sdv-opendut-peer:0.10.2"])
        pki = self.path / "pki"
        pki.mkdir(mode=0o755)
        signing = self.path / "signing"
        signing.mkdir(mode=0o700)
        run(["openssl", "req", "-x509", "-newkey", "rsa:3072", "-sha256", "-nodes", "-days", "7",
             "-keyout", signing / "ca.key", "-out", pki / "ca.pem", "-subj", "/CN=SDV-local-openDuT-CA",
             "-addext", "basicConstraints=critical,CA:TRUE", "-addext", "keyUsage=critical,keyCertSign,cRLSign"])
        run(["openssl", "req", "-new", "-newkey", "rsa:3072", "-sha256", "-nodes",
             "-keyout", pki / "carl.key", "-out", signing / "carl.csr", "-subj", "/CN=carl"])
        ext = signing / "carl.ext"
        ext.write_text("subjectAltName=DNS:carl\nbasicConstraints=critical,CA:FALSE\n"
                       "keyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n")
        run(["openssl", "x509", "-req", "-sha256", "-days", "7", "-in", signing / "carl.csr",
             "-CA", pki / "ca.pem", "-CAkey", signing / "ca.key", "-CAcreateserial",
             "-out", pki / "carl.pem", "-extfile", ext])
        # Runtime key readable by CARL UID1000. Private parent0700 limits host access;
        # only the runtime PKI directory (never signing CA key) is mounted into CARL.
        for item in pki.iterdir():
            item.chmod(0o644)
        signing.joinpath("ca.key").chmod(0o600)
        identity = uuid.uuid4().hex
        self.state = {"schema_version": 1, "run_id": identity, "project": "sdv-od-" + identity[:10],
                      "pins": PINS, "peer_image": peer_image, "cleo": str(cleo), "phase": "prepared",
                      "management_subnet": str(network), "dut_subnet": "192.168.123.0/24",
                      "cluster_id": str(uuid.uuid4()), "peer_ids": [str(uuid.uuid4()) for _ in range(2)],
                      "device_ids": [str(uuid.uuid4()) for _ in range(2)]}
        self.save()
        return {"pins": PINS, "peer_image": peer_image, "tls_certificate_sha256":
                hashlib.sha256((pki / "carl.pem").read_bytes()).hexdigest()}

    def name(self, suffix):
        return self.state["project"] + "-" + suffix

    def management_address(self, host):
        return str(ipaddress.ip_network(self.state["management_subnet"]).network_address + host)

    def ownership(self, kind, name):
        actual = run(["docker", kind, "inspect", "--format", '{{json .Config.Labels}}' if kind == "container"
                      else '{{json .Labels}}', name])
        if json.loads(actual).get(LABEL) != self.state["run_id"]:
            raise RuntimeError(f"refuse unrelated {kind}: {name}")

    def cleo(self, *args, timeout=90, private=False):
        return run(["docker", "exec", self.name("a"), "timeout", str(timeout),
                    "/cleo/opendut-cleo", *args], timeout=timeout + 5, private=private)

    def up(self):
        if self.state is None or self.state["phase"] not in ("prepared", "removed"):
            raise RuntimeError("deployment must be prepared or removed before up")
        networks = [ipaddress.ip_network(self.state[k]) for k in ("management_subnet", "dut_subnet")]
        routes = json.loads(run(["ip", "-j", "route"]))
        existing = []
        for route in routes:
            if route.get("dst", "default") != "default":
                existing.append(ipaddress.ip_network(route["dst"], strict=False))
        for network in json.loads(run(["docker", "network", "inspect", *run(["docker", "network", "ls", "-q"]).split()])):
            existing.extend(ipaddress.ip_network(c["Subnet"]) for c in (network["IPAM"].get("Config") or []) if "Subnet" in c)
        if any(selected.overlaps(other) for selected in networks for other in existing if selected.version == other.version):
            raise RuntimeError("test subnet overlaps existing host/Docker route")
        label = LABEL + "=" + self.state["run_id"]
        self.state["phase"] = "starting"
        self.save()
        run(["docker", "network", "create", "--label", label, "--subnet", self.state["management_subnet"], self.name("mgmt")])
        run(["docker", "volume", "create", "--label", label, self.name("data")])
        run(["docker", "run", "--rm", "--network", "none", "--entrypoint", "chown", "-v",
             self.name("data") + ":/data", self.state["peer_image"], "1000:1000", "/data"])
        env = {"NETWORK_BIND_HOST": "0.0.0.0", "NETWORK_BIND_PORT": "8080", "NETWORK_REMOTE_HOST": "carl",
               "NETWORK_REMOTE_PORT": "8080", "NETWORK_TLS_ENABLED": "true", "NETWORK_TLS_CA": "/tls/ca.pem",
               "NETWORK_TLS_CERTIFICATE": "/tls/carl.pem", "NETWORK_TLS_KEY": "/tls/carl.key",
               "NETWORK_TLS_SERVER_AUTH_ENABLED": "false", "NETWORK_OIDC_ENABLED": "false", "VPN_ENABLED": "false",
               "OPENTELEMETRY_ENABLED": "false", "PERSISTENCE_ENABLED": "true", "PERSISTENCE_DATABASE_FILE": "/data/carl.db"}
        flags = [v for key, value in env.items() for v in ("-e", "OPENDUT_CARL_" + key + "=" + value)]
        run(["docker", "run", "-d", "--name", self.name("carl"), "--label", label, "--network", self.name("mgmt"),
             "--network-alias", "carl", "--ip", self.management_address(10), "-v", str(self.path / "pki") + ":/tls:ro",
             "-v", self.name("data") + ":/data", *flags, "--entrypoint", "/opt/opendut-carl/opendut-carl", PINS["carl_image"]])
        for index, suffix in enumerate(("a", "b")):
            private = self.path / suffix
            private.mkdir(exist_ok=True, mode=0o700)
            setup = private / "peer-setup"
            setup.unlink(missing_ok=True)
            run(["docker", "run", "-d", "--name", self.name(suffix), "--label", label,
                 "--network", self.name("mgmt"), "--ip", self.management_address(11 + index), "--cap-add", "NET_ADMIN",
                 "-v", str(private) + ":/run/opendut", "-v", str(Path(self.state["cleo"]).parent) + ":/cleo:ro",
                 "-v", str(self.path / "pki/ca.pem") + ":/pki/ca.pem:ro",
                 "-e", f"DUT_ADDRESS=192.168.123.{101 + index}", "-e", "OPENDUT_EDGAR_SERVICE_USER=root",
                 "-e", "OPENDUT_EDGAR_VPN_ENABLED=false", "-e", "OPENDUT_EDGAR_VPN_DISABLED_REMOTE_HOST=" + self.management_address(11 + index),
                 "-e", "OPENDUT_EDGAR_OPENTELEMETRY_ENABLED=false", "-e", "OPENDUT_CLEO_NETWORK_CARL_HOST=carl",
                 "-e", "OPENDUT_CLEO_NETWORK_CARL_PORT=8080", "-e", "OPENDUT_CLEO_NETWORK_TLS_CA=/pki/ca.pem",
                 "-e", "OPENDUT_CLEO_NETWORK_OIDC_ENABLED=false", self.state["peer_image"]])
        # A failed veth/capability gate is detected before enrollment.
        for suffix in ("a", "b"):
            run(["docker", "exec", self.name(suffix), "ip", "link", "show", "dut0"])
        version = self.cleo("--version")
        if "0.10.2" not in version:
            raise RuntimeError("CLEO version mismatch")
        self.cleo("generate-setup-string", "--help")
        deadline = time.monotonic() + 60
        while True:
            try:
                self.cleo("list", "--output", "json", "peers", timeout=5)
                break
            except (RuntimeError, subprocess.TimeoutExpired):
                if time.monotonic() >= deadline:
                    raise RuntimeError("CARL TLS/CLI readiness exceeded 60 seconds")
                time.sleep(1)
        for index, suffix in enumerate(("a", "b")):
            peer, device = self.state["peer_ids"][index], self.state["device_ids"][index]
            self.cleo("create", "peer", "--id", peer, "--name", "cc-" + suffix, "--location", "local")
            self.cleo("create", "network-interface", "--peer-id", peer, "--type", "ethernet", "--name", "dut0")
            self.cleo("create", "device", "--peer-id", peer, "--device-id", device, "--name", "cc-" + suffix + "-dut", "--interface", "dut0")
            token = self.cleo("generate-setup-string", peer, private=True)
            temporary = self.path / suffix / "setup.tmp"
            temporary.write_text(token + "\n")
            temporary.chmod(0o600)
            temporary.replace(self.path / suffix / "peer-setup")
        self.cleo("await", "peer-online", *self.state["peer_ids"], timeout=120)
        self.cleo("create", "cluster-descriptor", "--name", "cc-local-ethernet", "--cluster-id", self.state["cluster_id"],
                  "--leader-id", self.state["peer_ids"][0], "--device-ids", *self.state["device_ids"])
        self.cleo("create", "cluster-deployment", self.state["cluster_id"])
        self.cleo("await", "cluster-peers-online", self.state["cluster_id"], timeout=120)
        self.state["phase"] = "deployed"
        self.save()
        # Cluster peer-online precedes asynchronous EDGAR interface rollout.
        deadline = time.monotonic() + 45
        while True:
            try:
                ping = run(["docker", "exec", self.name("a"), "ping", "-I", "dut0local", "-c", "3", "-W", "2", "192.168.123.102"])
                break
            except RuntimeError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("managed Ethernet forwarding readiness exceeded 45 seconds")
                time.sleep(1)
        status = self.status()
        status["ping"] = ping
        return status

    def status(self):
        result = {"run_id": self.state["run_id"], "phase": self.state["phase"], "profile": "local TLS; VPN/OIDC disabled",
                  "pins": PINS, "peer_image": self.state["peer_image"], "peers": json.loads(self.cleo("list", "--output", "json", "peers")),
                  "devices": json.loads(self.cleo("list", "--output", "json", "devices")),
                  "descriptors": json.loads(self.cleo("list", "--output", "json", "cluster-descriptors")),
                  "clusters": json.loads(self.cleo("list", "--output", "json", "cluster-deployments")), "interfaces": {}, "routes": {}}
        for suffix in ("a", "b"):
            self.ownership("container", self.name(suffix))
            result["interfaces"][suffix] = json.loads(run(["docker", "exec", self.name(suffix), "ip", "-d", "-j", "link", "show"]))
            result["routes"][suffix] = json.loads(run(["docker", "exec", self.name(suffix), "ip", "-j", "route"]))
        return result

    def down(self):
        results = []
        # Undeploy when CARL/peer remains accessible, then remove owned namespaces.
        if self.state["phase"] == "deployed":
            try:
                self.cleo("delete", "cluster-deployment", self.state["cluster_id"], timeout=20)
                results.append({"id": "undeploy", "status": "passed"})
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                results.append({"id": "undeploy", "status": "failed", "reason": str(exc)})
        for kind, suffixes in (("container", ("a", "b", "carl")), ("network", ("mgmt",)), ("volume", ("data",))):
            for suffix in suffixes:
                name = self.name(suffix)
                inspect = subprocess.run(["docker", kind, "inspect", name], capture_output=True, timeout=10)
                if inspect.returncode:
                    results.append({"id": name, "status": "absent"})
                    continue
                self.ownership(kind, name)
                command = ["docker", "rm", "-f", name] if kind == "container" else ["docker", kind, "rm", name]
                run(command, timeout=30)
                results.append({"id": name, "status": "removed"})
        self.state["phase"] = "removed"
        self.save()
        return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "up", "status", "down"))
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--keep-on-failure", action="store_true", help="Retain owned resources for local debugging")
    parser.add_argument("--management-subnet", default="172.30.77.0/24", help="prepare only: IPv4 /24, separate from DUT network")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    bench = Bench(args.state)
    code = 0
    try:
        result = bench.prepare(args.management_subnet) if args.action == "prepare" else getattr(bench, args.action)()
        (args.output / "deployment.json").write_text(json.dumps(result, indent=2) + "\n")
        if args.action == "down" and any(item["status"] == "failed" for item in result):
            raise RuntimeError("undeployment failed; owned resources removed, inspect evidence")
        verdict = {"status": "passed", "action": args.action}
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
        code = 2
        verdict = {"status": "blocked", "action": args.action, "reason": str(exc)}
        if args.action == "up" and bench.state and bench.state["phase"] in ("starting", "deployed") and not args.keep_on_failure:
            try:
                verdict["cleanup"] = bench.down()
            except (OSError, RuntimeError, subprocess.SubprocessError) as cleanup_error:
                verdict["cleanup_error"] = str(cleanup_error)
    (args.output / "results.json").write_text(json.dumps(verdict, indent=2) + "\n")
    print(json.dumps(verdict, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
