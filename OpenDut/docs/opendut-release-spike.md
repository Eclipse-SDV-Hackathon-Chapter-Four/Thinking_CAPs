# F003 matched-release local Ethernet spike

Prepared 4 October 2026. This research performed read-only host/source/registry inspection and streamed two release archives into memory to verify hashes and archive contents. No image was pulled, service launched, interface created, or cluster enrolled by this research. The commands below are implementation inputs, not executed deployment evidence. AAOS/FOTA remains deferred.

## Selected feasible profile

Use matched openDuT **0.10.2**, one CARL container, a CLEO client, and two isolated rootful Docker EDGAR namespaces. CARL retains TLS; OIDC and VPN are disabled for this local test network. CARL still enrolls real peers/devices and rolls out EDGAR Linux bridges and GRE TAP tunnels over their management addresses. This provides a real **local openDuT Ethernet** claim when actual DUT traffic and tunnel-dependency evidence pass. It provides no NetBird/WireGuard or distributed-site claim.

This mode is explicitly supported in release source:

- `opendut-carl/carl-development.toml`: `[vpn] enabled = false` and OIDC disabled.
- `opendut-carl/src/settings/vpn.rs`: returns `Vpn::Disabled` when `vpn.enabled=false`.
- `opendut-carl/src/manager/peer_manager/generate_peer_setup.rs`: emits `VpnPeerConfiguration::Disabled` and `AuthConfig::Disabled`.
- `opendut-carl/src/manager/cluster_manager/mod.rs`: reads each online peer's `remote_host` and still assigns/rolls out the cluster; skips VPN group creation when VPN is disabled.
- `opendut-edgar/src/service/vpn/mod.rs`: disabled VPN returns `vpn.disabled.remote.host` as the peer's own reachable address.
- `opendut-edgar/src/setup/start/mod.rs`: skips VPN tasks for a disabled setup, skips systemd with `--skip-service-run`, and skips custom service user/capability installation when service user is root.

Sources were checked at [release v0.10.2](https://github.com/eclipse-opendut/opendut/tree/v0.10.2), commit `eb8d15df6a65719db4b77c4ef660695ce238cf03`. The local checkout's newer main revision is unchanged.

## Release artifacts and immutable image pins

The [GitHub release API](https://api.github.com/repos/eclipse-opendut/opendut/releases/tags/v0.10.2) reports publication `2026-06-12T13:57:24Z` and these Linux x86_64 artifacts:

| Artifact | Compressed bytes | SHA256 |
| --- | ---: | --- |
| `opendut-carl-x86_64-unknown-linux-gnu-0.10.2.tar.gz` | 127724133 | `9588e9dc914bf4fa53252728439fe7dd26e62ef521192d8a95066cc3712d3230` |
| `opendut-cleo-x86_64-unknown-linux-gnu-0.10.2.tar.gz` | 8263744 | `26ad914212f922d3c27fbf6eaf573636f5c4d2eb33f8046cc124f460804541b3` |
| `opendut-edgar-x86_64-unknown-linux-gnu-0.10.2.tar.gz` | 32095145 | `8170893db4c9951df0b0c20286d3d5df569b13dcd925b1f747503ad72fea6bf4` |

CLEO and EDGAR archives were streamed, SHA256-checked, and enumerated in memory; they match the API digests above. CARL archive digest is API metadata only. EDGAR archive contains the executable, `install/rperf`, `install/netbird.tar.gz`, licenses, and empty plugin manifest; raw binary-only deployment is insufficient for managed setup.

Public GHCR manifests exist for both official `0.10.2` images and report Linux amd64:

```text
ghcr.io/eclipse-opendut/opendut-carl@sha256:40fbb962329d2b9b0386a84ab02a814aa21af46e00f43441e6812ddb1fa8ef65
ghcr.io/eclipse-opendut/opendut-edgar@sha256:3dd9a2aa082490a5c5cf2f540bbac8adcb09bad36226acef6f06f26b30f16520
```

Compressed image layers total approximately 293.6 MB for CARL and 64.8 MB for EDGAR; disk cost after extraction is larger. CARL image runs as UID/GID 1000 (`carl`). Its standard `/opt/entrypoint.sh` prepares optional custom CA/hosts values and executes CARL; it does **not** require Keycloak when OIDC is disabled. The full localenv overrides that entrypoint with a script that waits for Keycloak/NetBird. For the lean profile execute `/opt/opendut-carl/opendut-carl` directly.

EDGAR image contains Ubuntu 24.04, CAN utilities/libraries and the complete distribution, runs as root, and uses `/entrypoint.sh`. Its stock entrypoint calls managed setup without `--skip-can`; replace it with the Ethernet-only entrypoint below. `iproute2`, `tcpdump`, and `jq` are not established by its image history, so add them in a small derived image for veth creation/probes.

Exact optional artifact retrieval, with a private cache outside committed evidence:

```sh
mkdir -p .local/opendut/0.10.2
chmod 700 .local/opendut
curl --fail --location --retry 3 --output .local/opendut/0.10.2/opendut-cleo.tar.gz https://github.com/eclipse-opendut/opendut/releases/download/v0.10.2/opendut-cleo-x86_64-unknown-linux-gnu-0.10.2.tar.gz
curl --fail --location --retry 3 --output .local/opendut/0.10.2/opendut-edgar.tar.gz https://github.com/eclipse-opendut/opendut/releases/download/v0.10.2/opendut-edgar-x86_64-unknown-linux-gnu-0.10.2.tar.gz
printf '%s\n' '26ad914212f922d3c27fbf6eaf573636f5c4d2eb33f8046cc124f460804541b3  .local/opendut/0.10.2/opendut-cleo.tar.gz' '8170893db4c9951df0b0c20286d3d5df569b13dcd925b1f747503ad72fea6bf4  .local/opendut/0.10.2/opendut-edgar.tar.gz' | sha256sum --check
tar -xzf .local/opendut/0.10.2/opendut-cleo.tar.gz -C .local/opendut/0.10.2
```

Use registry digest pins for runtime CARL/EDGAR; retrieve only CLEO if the images supply the other distributions. Archive retrieval does not require Rust, cross, or sudo.

## Host findings

Docker is rootful: security options list AppArmor, seccomp and cgroup namespace, without a rootless marker; Docker commands are accessible. Root inside a Docker-owned network namespace with `NET_ADMIN` can create veth/bridge/tunnel interfaces without host sudo. Actual capability/LSM success remains a spike exit check.

Host kernel `6.8.0-138-generic` configuration has `CONFIG_NET_IPGRE=m`, `CONFIG_NET_IPGRE_DEMUX=m`, `CONFIG_WIREGUARD=m`, `CONFIG_VETH=m`, `CONFIG_BRIDGE=m`, and `CONFIG_TUN=y`. Bridge is loaded; GRE/WireGuard were not shown in `lsmod`. GRE creation may trigger kernel module autoload. If it fails, record the actual kernel/capability error; no host module-loading command was executed. The lean profile does not need WireGuard or `/dev/net/tun`.

No locally listed images are openDuT, Keycloak, NetBird, or Traefik. Available related images include `zenoh-someip-bridge:latest`, `docker_setup-adas_score:latest`, `debian:bookworm-slim`, and `python:3.11-slim-bookworm`. No openDuT/NetBird/Keycloak volumes were listed and no localenv secrets file exists. A receiver-build container started by the main task is present; leave it untouched.

Disk was initially 8.1 GiB free/97% used and is now **16 GiB free/94% used** after the main task removed its own duplicate build artifacts. No pruning or deletion was performed by this research. Budget the lean images/derived tools and captures; do not launch full-stack image builds or remove unrelated images/volumes to reclaim space.

The inspected backend ports `80`, `443`, `8080`, and `8081` had no listening TCP sockets, but recheck before use. `opendut.local` DNS is unresolved. The lean profile uses Docker DNS `carl` and needs no host `/etc/hosts` edit.

## Lean configuration contract

Create an integration-owned Docker network, for example `172.30.77.0/24` after checking overlap, with CARL `.10`, peer A `.11`, peer B `.12`, and CLEO using Docker DNS `carl`. This is the **management/GRE underlay**. The two DUT endpoints remain `192.168.123.101/24` and `.102/24` on their own `dut0local`, subject to fresh overlap checks. No direct Docker network may join these DUT addresses.

Restrict CARL to the dedicated Docker network. If host UI access is needed, publish only `127.0.0.1:18080:8080`. Diagnostic management can later use peer B's management endpoint; do not bind the observation HTTP service to the DUT network as its only access path.

CARL environment keys are checked against `opendut-carl/carl.toml` and settings loading:

```text
OPENDUT_CARL_NETWORK_BIND_HOST=0.0.0.0
OPENDUT_CARL_NETWORK_BIND_PORT=8080
OPENDUT_CARL_NETWORK_REMOTE_HOST=carl
OPENDUT_CARL_NETWORK_REMOTE_PORT=8080
OPENDUT_CARL_NETWORK_TLS_ENABLED=true
OPENDUT_CARL_NETWORK_TLS_CA=/etc/opendut/tls/ca.pem
OPENDUT_CARL_NETWORK_TLS_CERTIFICATE=/etc/opendut/tls/carl.pem
OPENDUT_CARL_NETWORK_TLS_KEY=/etc/opendut/tls/carl.key
OPENDUT_CARL_NETWORK_TLS_SERVER_AUTH_ENABLED=false
OPENDUT_CARL_NETWORK_OIDC_ENABLED=false
OPENDUT_CARL_VPN_ENABLED=false
OPENDUT_CARL_OPENTELEMETRY_ENABLED=false
OPENDUT_CARL_PERSISTENCE_ENABLED=true
OPENDUT_CARL_PERSISTENCE_DATABASE_FILE=/var/lib/opendut/carl/data/carl.db
```

Mount a test-owned TLS directory read-only at `/etc/opendut/tls`, a named CARL data volume, and override entrypoint to the binary. The certificate must have SAN `DNS:carl`; use a fresh local CA and server certificate, not upstream insecure development private keys. Because CARL runs as UID 1000, its server private key must be readable by that UID while remaining private on the host. Generated `.local/` PKI and data are not committed.

One source-independent OpenSSL creation recipe:

```sh
umask 077
mkdir -p .local/opendut/pki
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 7 -keyout .local/opendut/pki/ca.key -out .local/opendut/pki/ca.pem -subj /CN=SDV-openDuT-local-CA -addext basicConstraints=critical,CA:TRUE -addext keyUsage=critical,keyCertSign,cRLSign
openssl req -new -newkey rsa:3072 -sha256 -nodes -keyout .local/opendut/pki/carl.key -out .local/opendut/pki/carl.csr -subj /CN=carl
printf '%s\n' 'subjectAltName=DNS:carl' 'basicConstraints=critical,CA:FALSE' 'keyUsage=critical,digitalSignature,keyEncipherment' 'extendedKeyUsage=serverAuth' > .local/opendut/pki/carl.ext
openssl x509 -req -sha256 -days 7 -in .local/opendut/pki/carl.csr -CA .local/opendut/pki/ca.pem -CAkey .local/opendut/pki/ca.key -CAcreateserial -out .local/opendut/pki/carl.pem -extfile .local/opendut/pki/carl.ext
chmod 644 .local/opendut/pki/ca.pem .local/opendut/pki/carl.pem
```

Do not mount the CA private key into runtime containers. Provision the runtime server key ownership via a short test-owned Docker helper if host UID differs from CARL's UID; host sudo is unnecessary. Store the signing key privately for teardown/reissuance.

CLEO client environment, release `opendut-cleo/cleo.toml` and `load_config("cleo", ...)` in `main.rs`:

```text
OPENDUT_CLEO_NETWORK_CARL_HOST=carl
OPENDUT_CLEO_NETWORK_CARL_PORT=8080
OPENDUT_CLEO_NETWORK_TLS_CA=/pki/ca.pem
OPENDUT_CLEO_NETWORK_OIDC_ENABLED=false
```

Mount only the public CA at `/pki/ca.pem` and unpacked CLEO at `/opt/opendut-cleo`. Configure each peer with:

```text
OPENDUT_EDGAR_SERVICE_USER=root
OPENDUT_EDGAR_VPN_ENABLED=false
OPENDUT_EDGAR_VPN_DISABLED_REMOTE_HOST=172.30.77.11  # peer A; .12 for peer B
OPENDUT_EDGAR_OPENTELEMETRY_ENABLED=false
```

`VPN_DISABLED_REMOTE_HOST` is **that peer's own address**, not the opposite peer or CARL address. EDGAR reports it to CARL, which uses the distinct peer addresses for GRE TAP rollout. Managed setup supplies peer identity, CARL URL, CA and disabled-auth configuration from the setup string; do not fabricate those values.

Each EDGAR needs its own writable `/etc/opendut` and `/opt/opendut/edgar` volumes, its own runtime setup file, and `cap_add: [NET_ADMIN]`. Use Docker's usual `NET_RAW` capability for ping/capture. Do not share `/etc`, host `/usr/bin`, host network, or `/tmp` across peers. The application may share its designated EDGAR network namespace later; its own local S-CORE IPC directory stays local to that peer.

The derived EDGAR image can install `iproute2 iputils-ping tcpdump jq ca-certificates` atop the pinned release image. Keep shell tracing disabled. Its entrypoint should implement:

```sh
#!/bin/sh
set -eu
ip link show dut0 >/dev/null 2>&1 || ip link add dut0 type veth peer name dut0local
ip link set dev dut0 up
ip link set dev dut0local up
ip addr replace "$DUT_ADDRESS/24" dev dut0local
# Peer A DUT_ADDRESS=192.168.123.101; peer B=.102.
# Enrollment writes a private peer-specific setup file into this bind-mounted directory.
while [ ! -s /run/opendut/peer-setup ]; do sleep 1; done
OPENDUT_EDGAR_SETUP_STRING=$(cat /run/opendut/peer-setup)
export OPENDUT_EDGAR_SETUP_STRING
/opt/opendut-edgar/opendut-edgar setup managed --no-confirm --skip-service-run --skip-can --log-file=-
unset OPENDUT_EDGAR_SETUP_STRING
exec /opt/opendut/edgar/opendut-edgar service
```

Managed setup copies the executable and rperf to `/opt/opendut/edgar`, writes `/etc/opendut/edgar.toml`, and writes the CA under `/etc/opendut/tls/ca.pem`. Root plus `--skip-service-run --skip-can` bypasses systemd, CAN module/dependency checks and service-user capability installation. Initial creation of `dut0` is required before registering its device/cluster.

## Enrollment and smoke commands

After CARL HTTPS readiness and the peer containers' veth creation, invoke the release CLEO within the management network. `PEER_A_ID`, `PEER_B_ID`, device IDs and `CLUSTER_ID` are manifest-owned UUIDs. Commands are source-checked at the release; variable values are implementation inputs.

```sh
opendut-cleo create peer --id "$PEER_A_ID" --name cc-bridge --location local
opendut-cleo create network-interface --peer-id "$PEER_A_ID" --type ethernet --name dut0
opendut-cleo create device --peer-id "$PEER_A_ID" --device-id "$DEVICE_A_ID" --name cc-bridge-dut --interface dut0
opendut-cleo generate-setup-string "$PEER_A_ID" > /run/opendut-a/peer-setup
opendut-cleo create peer --id "$PEER_B_ID" --name cc-receiver --location local
opendut-cleo create network-interface --peer-id "$PEER_B_ID" --type ethernet --name dut0
opendut-cleo create device --peer-id "$PEER_B_ID" --device-id "$DEVICE_B_ID" --name cc-receiver-dut --interface dut0
opendut-cleo generate-setup-string "$PEER_B_ID" > /run/opendut-b/peer-setup
opendut-cleo await peer-online "$PEER_A_ID" "$PEER_B_ID"
opendut-cleo create cluster-descriptor --name cc-local-ethernet --cluster-id "$CLUSTER_ID" --leader-id "$PEER_A_ID" --device-ids "$DEVICE_A_ID" "$DEVICE_B_ID"
opendut-cleo create cluster-deployment "$CLUSTER_ID"
opendut-cleo await cluster-peers-online "$CLUSTER_ID"
opendut-cleo list --output json peers
opendut-cleo list --output json cluster-deployments
```

Write setup files by atomic rename after generating them privately so peer processes never read partial strings. Check the release `--help` after extraction before first mutation; unlike older README snippets, UUID is positional for `generate-setup-string` and Ethernet enum is `ethernet`.

`docker compose exec peer-a ip -d -j link show` and the same on peer B must show each DUT and GRE TAP joined to `br-opendut`. `docker compose exec peer-a ping -c 3 192.168.123.102` is only an initial Ethernet smoke check. Capture `proto gre` on management `eth0` for this VPN-disabled profile; there is **no wt0**. Capture selected SOME/IP on DUT `dut0` once actual vehicle services are placed on their designated peers. Final acceptance remains the real input, return, diagnostics, fault/recovery and no-bypass criteria in [deployment research](opendut-deployment-research.md).

## Full NetBird localenv alternative

Not required for the selected local profile. Tagged localenv needs Postgres `14.15`, Keycloak `26.2.5`, Traefik `3.6.8`, and NetBird management/signal/relay `0.64.5`; several Dockerfiles also pull Ubuntu 24.04 and Red Hat UBI9 and build tooling layers. It provisions CA/certificates, passwords, Keycloak realms/clients/users, and NetBird keys. None are present here.

If later selected, use the **release's complete localenv** in an isolated checkout, not a partial copy of current main. The exact sequence is secret provisioning, private copy of `/provision`, then explicit core service startup:

```sh
# From an isolated release tree; OPENDUT_RELEASE_ROOT points to that tree.
docker compose -f "$OPENDUT_RELEASE_ROOT/.ci/deploy/localenv/docker-compose.yml" --env-file "$OPENDUT_RELEASE_ROOT/.ci/deploy/localenv/.env.development" up --build provision-secrets
# Copy into a new private directory; never delete/recreate existing unrelated secrets.
docker cp opendut-provision-secrets:/provision/. "$OPENDUT_PRIVATE_SECRET_DIR/"
OPENDUT_CARL_IMAGE_VERSION=0.10.2 OPENDUT_LOCALENV_TELEMETRY_ENABLED=0 docker compose -f "$OPENDUT_RELEASE_ROOT/.ci/deploy/localenv/docker-compose.yml" --env-file "$OPENDUT_RELEASE_ROOT/.ci/deploy/localenv/.env.development" --env-file "$OPENDUT_PRIVATE_SECRET_DIR/.env" up --detach --build keycloak-postgres keycloak init_keycloak traefik netbird-management netbird-signal netbird-relay carl
```

Additional blockers are resolvable backend hostnames, TLS/CA mounts, NetBird VPN capabilities and image/storage budget. Fix `SHARED_CERTS_HOST_DIR` to the actual private host directory if using that optional bind mount; the literal upstream `/provision` host path is not established here. Do not print a resolved Compose config or raw provision logs because they can include generated credentials. No full backend launch is proposed for F003's selected local profile.

## Remaining concrete spike checks

1. Pull matched pinned images; extend peer tools and extract the verified CLEO artifact. This removes the missing Rust/cross dependency.
2. Generate test-owned TLS files and ensure CARL UID 1000 can read its private key; verify HTTPS with the public CA.
3. Create dedicated Docker management network and two EDGAR namespaces with `NET_ADMIN`; verify veth and GRE module/capability behavior without host sudo.
4. Enroll exactly two peers/devices, deploy one cluster, and record routed Ethernet traffic through the EDGAR-managed GRE path. Report actual errors if source-supported disabled VPN mode fails in the release build.
5. Apply existing SOME/IP configuration overlays and isolated local IPC mounts, then prove the actual application traffic plus tunnel-dependency check. Preserve the diagnostic management path during interruption.

Disk, artifact retrieval and kernel configuration have feasible paths; live startup, capability success, release binary compatibility, cluster rollout and vehicle traffic remain unverified. Limit claims to the evidence actually obtained.
