# Local openDuT Ethernet testbench
Prepared 4 October 2026; AAOS/FOTA deferred. The matched 0.10.2 release runs TLS CARL and two
NET_ADMIN EDGAR containers in distinct namespaces. VPN/OIDC are disabled for this local
profile; actual CARL rollout creates br-opendut and GRE TAP over the management network.
No NetBird/WireGuard/distributed-site claim is made.

Pins are in versions.json. contributions/eclipse-opendut/OpenDut/scripts/opendut_testbench.py implements prepare/up/status/down;
Peer.Dockerfile adds namespace/capture tools. Private PKI, enrollment strings and packet
archives live under ignored .local/. No signing key is mounted into runtime containers.
State directory0700 protects the runtime server key, which CARL UID1000 reads through a
separate bind mount. Certificates expire after seven days; prepare a fresh state directory
for later runs. Resources have a unique ownership label; teardown refuses unrelated labels.

Use the [feature quickstart](../../specs/003-opendut-testbench/quickstart.md). Verified evidence:
[contributions/shared/evidence/f003-receiver-version-matched](../../evidence/f003-receiver-version-matched/results.json),
[f003-cleanup](../../evidence/f003-cleanup/results.json), and
[f003-repeat-deployment](../../evidence/f003-repeat-deployment/results.json).
The source research remains historical preparation input, not an assertion of a live VPN.

The receiver smoke mounts configuration overlays without editing bridge source. They set
DUT unicast, each process's local routing host, explicit UDP event reliability and vSomeIP's
scalar UDP port syntax. The network config advertises output major0 to match the existing
bridge's DEFAULT_MAJOR subscription0; baseline advertises1. Service/event/group IDs and
payloads remain those of the current bridge. These adjustments are necessary for network
transport; the original local Unix IPC run did not exercise these negotiation constraints.
Syntax is grounded in [vSomeIP configuration](https://github.com/COVESA/vsomeip/blob/master/documentation/vsomeipConfiguration.md)
and actual daemon/bridge source; successful receiver/control-return evidence validates this
selected configuration. GRE capture uses numeric IP protocol47 because the minimal EDGAR
image lacks /etc/protocols and tcpdump resolved the symbolic gre filter incorrectly.

DUT192.168.123.101/.102 each lives on a private veth peer; management172.30.77.11/.12 remains
separate. App containers share only their designated peer's network namespace; S-CORE local
IPC is confined to peerB. Diagnostic HTTP binds only peerB management address. Disabling the
observed managed tunnel caused accepted speed to become stale while source heartbeat and
HTTP remained available, then recovery restored consumption. Fixture Zenoh vehicle inputs,
actual applications/openDuT; CARLA has not yet run in this testbench.
