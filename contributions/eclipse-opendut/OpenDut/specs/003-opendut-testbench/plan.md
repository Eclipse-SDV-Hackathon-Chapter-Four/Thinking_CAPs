# F003 implementation plan
Branch contributions/eclipse-sdv-hackathon; 2026-10-04; [spec](spec.md).
## Technical context
Docker rootful isolated namespaces, Bash/Python external runner, matched openDuT 0.10.2
(commit eb8d15df6a65719db4b77c4ef660695ce238cf03), native application images already audited.
Private generated TLS and enrollment files; CARL persistence in owned volume.
NET_ADMIN peers; GRE kernel autoload is an implementation gate. Scope two local peers,
VPN/OIDC disabled, TLS enabled, no CAN/executor/NetBird claims. Tests: enrollment, Ethernet,
real SOME/IP/receiver, negative tunnel dependency, management reachability and cleanup.
## Constitution check
All twelve principles checked before/after design. Preserve source and control return;
pin inputs, label fixture traffic/preparation, scope namespace mutations, record failure.
No deviations. FOTA excluded. Research agents already resolved deployment unknowns.
## Structure
contributions/eclipse-opendut/OpenDut/config/testbench/{Peer.Dockerfile,peer-entrypoint.sh,versions.json};
contributions/eclipse-opendut/OpenDut/scripts/opendut_testbench.py; contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py; evidence/f003-*.
## Design
Generate local CA/server SAN carl in ignored private state; immutable CARL/EDGAR images,
verified CLEO archive; derive peer tooling image and record actual digest. Use management
172.30.77.0/24 and DUT192.168.123.0/24 only after overlap checks. Separate peer-local IPC.
Run CLEO in network to discover/enroll/deploy, never expose raw setup strings in evidence.
Bound every external operation. Negative test disables DUT GRE inside peer namespace only.
Cleanup undeploys owned cluster and destroys only owned resources.
