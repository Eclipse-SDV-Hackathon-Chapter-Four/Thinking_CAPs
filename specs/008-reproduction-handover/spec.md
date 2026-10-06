# F008 — Reproduction and judging handover
Prepared 4 October 2026. Depends on reviewed F001–F005; AAOS/FOTA deferred, F007 optional
extensions not admitted while real simulation and updater prerequisites remain unavailable.

## User scenarios and testing
US1 P1: A contributor obtains frozen sources, builds selected components and repeats the core.
Acceptance: clean integration/source checkout, explicit assets/pins, bounded commands and interpretable
native campaign evidence. Shared caches/assets must be declared; second-person signoff remains separate.
US2 P1: A reviewer can assess the contribution and reproduce its tests without conversation history.
Acceptance: precise problem/behavior, exported upstream patches, native tests, claim/evidence map and
continuation work. No public submission, maintainer agreement, merge or event eligibility assumed.
US3 P2: The team can rehearse the bounded demonstration and recover its owned test resources.
Acceptance: short technical/pitch scripts, actual fault/recovery timeline and labelled fallback;
no fabricated update/real-vehicle/simulation results. Restore original unrelated environment.

## Requirements
FR001/REQ017: Provide runnable setup/core campaign instructions and a reproduction record with
operator/environment identity. Verify clean-source self-reproduction; human signoff remains pending
until a real second contributor performs it. Do not fabricate that contributor or environment.
FR002/REQ022: Prepare narrow maintainer-facing contribution packet around actual upstream need,
changed artifacts and reproducible native tests, with ownership/approval/publication limitations.
FR003/REQ010/016: Freeze inputs and distinguish reused/prepared/integration/upstream/fixture/real
claims. Record event-start revision later, not invented now. Preserve failed/blocked evidence.
FR004: Replace stale repository entry-point claims with current verified commands/results and limits.
FR005/REQ012: Supply owned teardown/recovery and finish with baseline containers unchanged and
owned runtime removed; no network/GPU/user changes beyond recorded task resources.
FR006: Attempt recovery of the real CARLA gate using exact existing launch/source configuration as
bounded local work if useful; no driver/system changes or passing claim from process startup alone.
FR007: Record concise rehearsal/pitch, evidence paths and continuation issues for native /faults,
real simulation, second-person signoff and deferred AAOS/FOTA.

## Success criteria
SC001: Clean-source self-reproduction of the native core campaign passes, with cache/host sharing
reported. Actual second-person acceptance stays explicitly pending.
SC002: Reviewable patch packet and handover independently identify code/tests/live verification/limits.
SC003: Original repositories/containers remain preserved; scoped teardown verified.
SC004: CARLA limitation either resolves with actual evidence or remains precisely blocked.

## Edge cases
Missing build cache/toolchain, fresh source layout, wrong patch pin, mutable image/tag, changed
asset, disk exhaustion, interrupted teardown, stale TLS credentials, inaccurate historic README,
partial upstream gates and reviewer without the original machine.
