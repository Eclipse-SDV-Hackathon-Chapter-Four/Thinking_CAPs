# F003 — Local openDuT Ethernet testbench
Created 2026-10-04. Preparation; AAOS/FOTA deferred.

## User scenarios and testing
US1 (P1): Deploy two real managed peers and one Ethernet cluster. Independent test:
CARL reports both peer/device identities online; EDGAR joins DUT veth and GRE TAP to br-opendut.
US2 (P1): Carry the existing vehicle input and control return through that cluster.
Independent test: captures and native receiver data identify selected SOME/IP traffic.
US3 (P2): Prove dependency and cleanup. Independent test: disabling the tunnel stops
selected DUT flow while management diagnostics remain reachable; restoration recovers flow.

## Requirements
FR-001: Pin matched CARL/CLEO/EDGAR release and artifact digests; record actual IDs.
FR-002: Isolate two peer namespaces, DUT addresses and local IPC. No host interface changes.
FR-003: Preserve bridge code and service/event/payload mappings through configuration overlays.
FR-004: Keep management diagnostics reachable independently of the DUT path.
FR-005: Bounded deployment/readiness, scoped captures, assertions and owned-resource cleanup.
FR-006: Keep TLS keys/setup tokens private; commit no credentials or packet payload archives.
FR-007: Label local VPN-disabled Ethernet accurately; no distributed VPN/CARLA claims from fixtures.

## Success criteria
SC-001: Two real EDGAR peers/devices and one deployed cluster carry Ethernet frames.
SC-002: Actual receiver and bidirectional selected SOME/IP traffic use the tunnel.
SC-003: Negative path, recovery and resource cleanup pass deterministic assertions.
SC-004: A fresh operator can repeat the pinned local profile from the guide.

## Edge cases
Kernel/capability denial, TLS mismatch, enrollment timeout, process loss, conflicting networks,
partial setup, stale tokens, overlay mismatch, direct-route/local-IPC bypass and cleanup failure.
Blocking evidence must retain the exact failed gate rather than report live success.
