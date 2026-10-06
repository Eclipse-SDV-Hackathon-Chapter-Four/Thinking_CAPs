# F009 — CARLA startup recovery and physical vehicle acceptance
Prepared 4 October 2026. Continues the original vehicle milestone after F008 local handover.
AAOS/FOTA remains deferred; no optional middleware or X-Verse development admitted.

## User scenarios and testing
US1 P1: A server that becomes ready after launch can be reached despite an early client failure.
Acceptance: record a controlled early-client versus late-client/world comparison; readiness
retries recover using supported client creation within a fixed deadline. Never call TCP alone ready.
US2 P1: The actual simulated actor feeds the native receiver/network/control-return campaign.
Acceptance: CARLA frames, physical speed, actual returned controller request and applied vehicle
control are recorded; native fault/recovery/stall/history/cleanup checks remain explicit.
US3 P2: A failed launch/interrupted run restores only owned server/actor/bench resources.
Acceptance: existing source/containers preserved; private runtime removed and output retained.

## Requirements
FR001: Diagnose startup with actual RPC evidence and source-backed client behavior; distinguish
transport reachability from usable world/actor acceptance. Do not assert an unverified root cause.
FR002: Retry owned readiness with bounded fresh clients after failures; cap worker threads and
avoid changing original CARLA assets, bridge source, host drivers/network or X-Verse modules.
FR003: Align the diagnostic/controller start with a ready plant so unrelated engine startup
does not contaminate the selected loss scenario's initial state or occurrence counter.
FR004: Execute real physical/native campaign when feasible. Require actual frames/speed/return
actuation and native campaign assertions, without fixture substitution or relaxed verdicts.
FR005: Record source/config/commands and signal/resource cleanup; update current handover claims
only to the level achieved. Preserve previous blocked/failed evidence and human-signoff gap.

## Success criteria
SC001: Controlled startup comparison and updated helper reach a real world, or retain a precise
bounded remaining blocker. Fresh-client readiness is regression-tested at the connection boundary.
SC002: Actual CARLA/native campaign passes the selected checks with physical evidence, or fails/
blocks explicitly with owned cleanup; fixture campaign behavior remains verified separately.
SC003: Original source/container state preserved and new contribution committed locally.

## Edge cases
Connection refused before bind, persistent failed client, partial server startup, world unavailable
after version readiness, readiness deadline, native startup fault before plant publishes, actor
spawn failure, no physical movement, wrong return actuation, interrupted startup and cleanup.
