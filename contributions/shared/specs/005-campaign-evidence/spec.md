# F005 — Repeatable campaigns and truthful evidence
Prepared 4 October 2026. Depends on reviewed F002/F003/F004. AAOS/FOTA deferred.

## User scenarios and testing
US1 P1: An operator runs named scenarios and gets attributable, interpretable verdicts.
Acceptance: core startup/nominal/communication loss/recovery/diagnostic unavailability/collector
loss/native history restart yield explicit assertions, independent injection evidence and a manifest.
US2 P1: A missing environment or interrupted runner produces an honest outcome and scoped cleanup.
Acceptance: preflight absence exits blocked; assertion failure exits failed; deliberate failure after
injection verifies restoration without reporting the unfinished core campaign as passed.
US3 P2: An operator can select a real simulation campaign when available.
Acceptance: actual CARLA actor state and return actuation through existing assets are recorded;
a missing GPU/server/assets is blocked, never replaced by fixture inputs under a real label.

## Requirements
FR001/REQ010: Name scenarios, declare preconditions, expected results, seed and timing; record
revisions, dirty changes, executable/config identities, observations, clock domain and verdicts.
FR002/REQ011: Exit0 only for all selected acceptance checks passed, exit1 failed, exit2 blocked;
skipped/unselected/conditional checks must not inflate passed counts. Machine-readable results
and JUnit agree; summaries state implementation and verification limits.
FR003/REQ012: Restore only owned injections/app resources on success, failure and interruption.
FR004/REQ016: Identify fixture publishers, real receiver/network/storage and preparation;
keep archives private and evidence bounded. No AAOS/FOTA, native fault route, E2E or VIPER claim.
FR005/REQ004: Demonstrate control return while diagnostics is unavailable and source-loss unknown
while publisher continues; HTTP availability alone must not imply receiver freshness.
FR006: Allow tool/source paths from explicit local configuration rather than hidden cache paths.
FR007: Provide runnable instructions for another contributor; actual independent-person acceptance
is tracked in F008 and cannot be self-certified by the implementation agent.
FR008: A real CARLA selection records actual frames, physical actor speed and applied return path
using existing X-Verse classes/VCU when feasible. Restore owned actor/server without changing
pre-existing simulation state; declare any harness-generated operator commands.

## Success criteria
SC001: Fixture core plus deliberate failure-path campaign passes with truthful verdict/cleanup.
SC002: Missing prerequisite and child-verdict mismatch are tested and cannot report success.
SC003: Every selected check is traceable in results/JUnit/timeline/summary and manifest hashes.
SC004: Real simulation campaign either runs with native evidence or emits precise blocked evidence.

## Edge cases
Missing image/binary/patch/config/module, inactive bench, subprocess crash/nonzero, missing or
malformed evidence, child exit0 with failed checks, cleanup failure, SIGINT/SIGTERM, PID reuse,
changed binary during run, HTTP stall, interrupted injection and pre-existing CARLA process.
