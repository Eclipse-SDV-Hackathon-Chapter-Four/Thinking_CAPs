# openDuT Ethernet testbench research

Prepared 4 October 2026 for F001. AAOS/FOTA is deferred by the user. This is a source inspection and deployment design; no CARL, EDGAR, cluster, virtual interfaces, or traffic campaign was started during this research.

## Inspected baseline

| Item | Observed fact |
| --- | --- |
| Checkout | `/home/jefferson/opendut`, origin `eclipse-opendut/opendut` |
| Source pin | `a2447d876905d3293577f360af877229ca989017`; working tree clean at inspection |
| Workspace version | `0.11.0-alpha` in `Cargo.toml` |
| Required toolchain | `1.97.1` in `rust-toolchain.toml`; only `stable-x86_64-unknown-linux-gnu` installed on host |
| Bundled source build artifacts | No `target/` directory present |
| Docker | Daemon readable; `docker ps` returned no running containers; Compose `v5.6.0` |
| Host inspection tools | `ip`, `tcpdump`, `jq`, `uuidgen`, `openssl` available; `/dev/net/tun` present; `cross` not on PATH |
| Host underlay | Wi-Fi `wlp0s20f3`, route `192.168.1.0/24`; Ethernet `enp67s0` has no carrier |
| Existing virtual interfaces | Cuttlefish and Tailscale present; no `br-opendut` or `wt0` in inspected host interface list |

These facts establish available tooling, not kernel/capability permission for GRE/NetBird, backend health, or S-CORE compatibility. Privileged execution, DNS, images, certificates, and outbound downloads have not been exercised.

## What actually transports Ethernet

CARL's configured default Ethernet bridge is `br-opendut` (`opendut-carl/carl.toml`). EDGAR creates that Linux bridge, joins the configured DUT Ethernet interface, and joins a GRE TAP interface toward the other peer. NetBird/WireGuard provides the VPN interface `wt0`. The Ethernet frames travel over GRE inside the VPN; the inspected implementation is not VXLAN.

Primary local source:

- `opendut-edgar/src/service/tasks/create_ethernet_bridge.rs`
- `opendut-edgar/src/service/tasks/manage_joined_interfaces.rs`
- `opendut-edgar/src/service/network_interface/manager/gretap.rs`
- `doc/src/user-manual/edgar/troubleshooting.md`

The upstream test environment creates a DUT veth pair with these commands, from `.ci/deploy/testenv/edgar/scripts/create_edgar_service.sh` and `managed.sh`:

```sh
ip link add dut0 type veth peer name dut0local
ip link set dev dut0 up
ip link set dev dut0local up
```

Register **dut0** with CARL. Bind the application side to **dut0local**, or move that side into an application namespace. Do not give management `eth0` to EDGAR as the DUT interface: bridging the management interface can disrupt CARL, NetBird, DNS, and diagnostics.

## Why the existing vehicle path does not yet prove openDuT

`/home/jefferson/autoverse/vecu/s-core/cc_s-core/deployment/xverse/docker_setup/docker-compose.yaml` uses host networking and shares host `/tmp` explicitly to permit VSOMEIP local Unix-domain communication with the existing Zenoh/SOME-IP bridge. Its `vsomeip.json`, and the bridge's `config/vsomeip.gateway.json`, use `127.0.0.1`.

Adding an unrelated working openDuT cluster would leave this control path on local IPC/loopback. The deployed gateway and receiving SOME/IP daemon must be separated onto two DUT endpoints, with integration-owned configuration overlays that bind their actual unicast DUT addresses. Preserve bridge source, service/event IDs, payload encoding, and the bidirectional Cruise Control return path. Keep the S-CORE gatewayd/mw::com/cruise-control IPC together on the receiving side; isolate `/tmp` between peers so VSOMEIP cannot shortcut the tested wire path.

Inspected bridge mappings:

| Direction | Service / instance | Selected event | Configured transport |
| --- | --- | --- | --- |
| Bridge to receiver | `4660 / 1` (`0x1234 / 0x0001`) | velocity `30501` (`0x7725`) | gateway TCP `30510`, UDP `30511` |
| Receiver to bridge | `3000 / 1` (`0x0BB8 / 0x0001`) | target speed `30600`, throttle `30601` | someipd TCP `30512`, UDP `30513` |
| Discovery | SOME/IP SD | offers/subscriptions | UDP `30490`, multicast `224.0.0.1` in inspected configs |

The mapping values above come from the current local bridge `config/mapping.json` and S-CORE deployment configuration. Verify the actual transport by capture; event IDs are not UDP port numbers. Discovery and port-wide interruption alone do not identify the speed stream when several events share the same connection. A later injector must parse the selected flow or truthfully label a broader service interruption. Reliable SOME/IP requires stream-aware handling rather than a naive per-packet event filter.

## Feasible two-peer deployment

Use EDGAR outside the S-CORE image, with a separately invoked campaign runner. The lowest uncertainty upstream deployment shape is one CARL backend and two isolated Linux peer hosts/VMs. A single-machine implementation can use two separate EDGAR container network namespaces, each with its own config/application persistence and DUT veth; the gateway container shares peer A's namespace and the S-CORE container shares peer B's namespace. Container support is described as experimental upstream, so this is a spike with explicit exit evidence, not a proven deployment.

Candidate address plan, subject to a fresh route-overlap check:

| Plane | Peer A | Peer B | Purpose |
| --- | --- | --- | --- |
| DUT overlay | `192.168.123.101/24` on `dut0local` | `192.168.123.102/24` on `dut0local` | SOME/IP data and control return |
| Management underlay | Separately assigned container/VM address | Separately assigned container/VM address | CARL, NetBird control, DNS, diagnostics |
| VPN | NetBird-assigned address on `wt0` | NetBird-assigned address on `wt0` | GRE carriage; do not invent static VPN addresses |

The DUT subnet is taken from upstream troubleshooting examples and did not appear in inspected host routes. Recheck container, VPN and host routes before provisioning. On the single-host design, management may share a Docker bridge, but only the DUT veth and EDGAR-managed GRE TAP join `br-opendut`; never directly connect the two application DUT endpoints with a Docker bridge or host veth.

The stock `.ci/docker/edgar/docker-compose.yml` has `network_mode: host`, fixed `container_name: opendut-edgar`, and shared named persistence volumes. Two stock copies on one host do not give isolated peers. Both would attempt to use the same host `wt0`, bridge, and config. A custom integration Compose or separate VMs is needed.

Do not reduce the stock THEO cluster to two peers with `--scale peer=1`: `.ci/deploy/testenv/edgar/scripts/managed.sh` waits for five hard-coded peer IDs and applies a five-peer, CAN-enabled cluster with a legacy container executor. `cargo theo testenv cluster start` also performs CAN checks and cleanup. Its DUT veth mechanism is reusable, but its full campaign is not the proposed Ethernet-only two-peer setup.

## Source-verified commands and prerequisites

Commands below are checked against current source definitions. They have **not** been executed as a deployment. Backend/CLI authentication and a complete compatible artifact set are prerequisites.

Build tooling comes from `.cargo/config.toml`, `.ci/cargo-ci/src/packages/edgar.rs`, and `.ci/cargo-ci/src/tasks/build.rs`:

```sh
cd /home/jefferson/opendut
git rev-parse HEAD
rustup toolchain list
cargo ci edgar distribution --target x86_64-unknown-linux-gnu
cargo ci cleo distribution --target x86_64-unknown-linux-gnu
cargo theo testenv provision
cargo theo testenv start --skip-firefox --skip-telemetry
```

Running Cargo in this checkout selects Rust `1.97.1`; it can trigger a toolchain download. Distribution builds invoke `cross`, bundle NetBird and rperf, and generate license metadata. Install/build dependencies must be resolved separately; a raw EDGAR debug binary is not equivalent to the packaged setup artifact. Base development dependencies are `build-essential`, `pkg-config`, and `libssl-dev` per `doc/src/development/getting-started.md`.

Do not silently mix image defaults. The local backend Compose defaults CARL to `0.10.2`, while the standalone EDGAR Compose defaults to `0.10.0-alpha` and the checked-out source reports `0.11.0-alpha`. Select either a matched release bundle with recorded digests or build and tag a matched CARL/CLEO/EDGAR set from the inspected source. Compatibility between these differing defaults is unverified.

Backend prerequisites include Docker/Compose, resolvable `opendut.local`, `auth.opendut.local`, `netbird-api.opendut.local`, `netbird-relay.opendut.local`, `signal.opendut.local`, the backend CA, OIDC credentials, and NetBird provisioning. Upstream `doc/src/user-manual/carl/setup.md` documents the Compose secret-provisioning flow; avoid its destructive `rm -rf` cleanup when reusing existing secrets. Stock localenv publishes `80`, `443`, `8081`, and localhost `8080`; check for collisions before launch. Preserve credentials in private files/environment references and redact evidence. Upstream scripts use shell tracing and sometimes print setup strings, so raw setup logs require redaction.

Generate unique peer and device IDs, then run the following with variables populated from the deployment manifest. Source: `opendut-cleo/src/main.rs` and `opendut-cleo/src/commands/{peer,network_interface,device,cluster_descriptor,cluster_deployment,generate_setup_string}`.

```sh
# Run from a configured, authenticated CLEO client. Repeat for A and B.
opendut-cleo create peer --id "$PEER_ID" --name "$PEER_NAME" --location local-hackathon
opendut-cleo create network-interface --peer-id "$PEER_ID" --type ethernet --name dut0
opendut-cleo create device --peer-id "$PEER_ID" --device-id "$DEVICE_ID" --name "$DEVICE_NAME" --interface dut0
opendut-cleo generate-setup-string "$PEER_ID"

# In each isolated peer, using its own setup-string environment variable:
./opendut-edgar setup managed --skip-can --no-confirm --log-file=-

# Create a cluster containing the two DUT devices and deploy it:
opendut-cleo create cluster-descriptor --name cc-testbench --cluster-id "$CLUSTER_ID" --leader-id "$PEER_A_ID" --device-ids "$DEVICE_A_ID" "$DEVICE_B_ID"
opendut-cleo create cluster-deployment "$CLUSTER_ID"
opendut-cleo await cluster-peers-online "$CLUSTER_ID"
opendut-cleo list --output json peers
opendut-cleo list --output json cluster-deployments
```

`generate-setup-string` takes a **positional peer UUID** at this pin; old README examples using `--id` are stale. `--type ethernet` is the actual accepted enum value; the old example `--type eth` is stale. Do not export or retain generated setup strings in Git or public evidence.

Managed setup normally uses root privileges and creates a systemd service. For a container entrypoint, source-supported flags are `--skip-service-run --skip-can`; run `./opendut-edgar service` afterward. The stock container entrypoint already uses `--skip-service-run` but omits `--skip-can`; either supply CAN dependencies or use an integration-owned entrypoint for the Ethernet-only deployment. `--skip-can` must also mean no CAN devices are registered. Setup's default `--mtu` is `1542`; check the actual underlay, VPN, GRE, and DUT MTUs and exercise realistic payload sizes before claiming reliable carriage.

## Diagnostic management remains reachable during interruption

Run the diagnostic collector/provider with the receiving application, expose its HTTP service over peer B's management interface, and invoke it from an external runner through the management address or an explicit published management port. Keep this path off `dut0local`, `br-opendut`, and the selected SOME/IP interruption rule. Restrict interruption to the selected DUT traffic; never bring down management `eth0`, the backend, or the entire `wt0` interface as the default fault injection.

Before disturbance, record `ip route get` for both remote DUT and diagnostic management destinations. During disturbance, prove the diagnostic endpoint still answers and reports receiving-side age/state while the selected communication flow stops. HTTP failure alone is not evidence of a communication-timeout fault. The actual diagnostic endpoint and provider remain a later feature dependency; no route is invented here.

## Acceptance evidence

Record per-peer interface output in the correct network namespace:

```sh
ip -j address show
ip -d -j link show
ip -j link show master br-opendut
ip -j route show
ip route get "$REMOTE_DUT_IP"
ip route get "$DIAGNOSTIC_MANAGEMENT_IP"
/opt/opendut/edgar/netbird/netbird status --detail
```

Capture only the selected traffic, replacing names and addresses from the manifest:

```sh
tcpdump -i dut0 -nn -s 0 -w dut-someip.pcap 'host 192.168.123.101 and host 192.168.123.102 and (tcp port 30510 or udp port 30511 or tcp port 30512 or udp port 30513)'
tcpdump -i wt0 -nn -s 0 -w vpn-gre.pcap 'proto gre'
```

For service discovery, take a separate scoped UDP `30490` capture. Record actual GRE TAP names from `ip -d link`, not guessed suffixes. Capture commands require adequate capability, storage and bounded duration, and were not run here.

Accept a meaningful openDuT path only when all of the following are evidenced:

1. CARL lists both distinct peer identities, both DUT devices, one deployed cluster, and online peers.
2. Both `dut0` and the relevant GRE TAP are attached to each peer's `br-opendut`; NetBird reports the peer connection.
3. Route/interface snapshots explain DUT forwarding and separate diagnostic reachability; configured unicast values match actual DUT addresses.
4. Packet capture identifies actual velocity events `4660/1/30501` on the receiving DUT side, and actual target/throttle return events on the other side. Logs or observer evidence establish receiver consumption, not just frame arrival.
5. Synchronized in-one-clock-domain event/capture evidence relates disturbance to missing received traffic and recovery to real resumed consumption. Do not infer cross-host latency without a clock uncertainty contract.
6. A bounded negative-path check removes or blocks the EDGAR-managed DUT tunnel path, then restores it with cleanup. The selected flow must fail without this path, while management diagnostics remain accessible. This disproves a local socket, direct Docker route, or alternative network bypass.

Ping between DUT addresses is an initial connectivity check, not the final Cruise Control/openDuT claim. Preserve captures, redacted deployment snapshots, image/source pins, assertions, and cleanup outcome under the integration evidence run ID.

## Blockers and executable next steps

| Dependency | State | Next action |
| --- | --- | --- |
| Matched CARL/CLEO/EDGAR artifacts | Missing/unselected | Choose matched release artifacts or prepare exact-source build dependencies; record digests before deployment |
| Required Rust and cross | Missing from host inspection | Install supported build tools if source build is selected; do not retarget source silently |
| Two isolated peer resources | Not created | Implement integration-owned isolated namespace Compose or provision two Linux VMs |
| DNS/CA/OIDC/NetBird backend | Not running/verified | Provision selected localenv and verify HTTPS/identity services and two-peer connectivity |
| Privileged network capabilities / GRE | Unverified | Exercise only dedicated peer namespaces and record outcome; do not modify Wi-Fi/Cuttlefish/Tailscale |
| Baseline SOME/IP uses local IPC | Incompatible with traffic-path claim | Prepare address/routing/configuration overlays and separate `/tmp` by peer without bridge source edits |
| Real receiver diagnostics and fault injection | Subsequent feature dependencies | Establish receiving-side provenance before asserting timeout/recovery |

Proceed first with reproducible configuration and build preparation, then a two-peer Ethernet smoke spike, then the unchanged vehicle applications on the DUT endpoints. Mark deployment acceptance blocked until real traffic and no-bypass evidence exist. Keep the external test runner as the committed mechanism; VIPER and legacy container executors are not prerequisites.
