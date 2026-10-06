# F002 completion and convergence — 2026-10-04

Completed the receiver diagnostic vertical slice. Actual C++ receiver/controller is instrumented
in isolated worktree `/home/jefferson/sdv-score-diagnostics`, preserving the original checkout
and bridge. Native pinned OpenSOVD provides discovery and a read-only App data resource.

## Verification achieved
- Six Rust cache/clock/provenance/freshness/restart tests pass; Clippy all-targets with warnings
  denied passes after correcting one style finding; formatting applied.
- C++ sender test delivers a datagram and proves missing/full socket paths remain nonblocking.
- Controller Bazel build and existing cruise_control_unit_tests target pass (see build log).
  Initial build found the fixed-capacity receive callback could not hold an extra runtime index;
  event index is now a compile-time template argument, preserving callback capacity.
- Native HTTP fixture: eight checks pass, evidence/f002-http-fixture.
- Actual receiver integration: eight checks pass, evidence/f002-receiver. Fixture inputs traverse
  unchanged native bridge -> gateway/daemon -> mw::com -> actual controller -> diagnostic cache.
  Actual speed/artifact identity/engagement are observed; existing positive throttle return is
  received; speed-only loss becomes stale while other events continue; input recovery is observed.
  Removing the diagnostic server does not stop control output.

This is L2 preparation evidence: vehicle inputs are fixture-generated; CARLA and openDuT were
not run. It establishes the real native receiver/provider boundary, not complete vehicle acceptance.
Freshness thresholds are provisional and are not engineering-accepted deadlines.
Acceptance means decoded by the consumer, not integrity/functional plausibility approval.
Sequence IDs and native E2E remain unavailable. Native HTTP faults remain absent.

## Convergence
FR-001–007, SC-001–004, all eight user-story scenarios/edge cases, plan paths and twelve
principles reviewed against implemented scope. Source observations, actual controller state,
nonblocking sender, cache freshness/provenance and fixture/live labels are represented.
No actionable F002 scope gaps; tasks left unchanged during convergence.
Native faults/fault lifecycle, real CARLA campaign and openDuT traffic remain separate backlog gates.

## Reproduction
Use pinned Cargo.lock and existing S-CORE build toolchain. Apply the exported patch at base
93f8ea1e6f76714496c092902e00c9b91c58cdc8, build the cruise main and unit target, then run
`/usr/bin/python3 OpenSOVD/tests/receiver_integration_smoke.py --binary <diagnostic binary> --score-source
<patched cc_s-core> --baseline-source <original cc_s-core> --output evidence/<new-run-id>`.
The smoke starts/removes only uniquely named test containers and keeps IPC in a private mount.
