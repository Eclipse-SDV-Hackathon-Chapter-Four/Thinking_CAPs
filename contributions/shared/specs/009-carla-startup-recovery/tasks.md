# F009 executable tasks
## Foundation and diagnosis
- [X] T001 Specify source-based recovery scope and inspect original requirements/current evidence.
- [X] T002 Compare early and late fresh client version/world calls against an owned server.
## US1 — Readiness
- [X] T003 Implement bounded fresh-client readiness and meaningful retry/deadline regressions.
- [X] T004 Verify actual owned CARLA world/actor/physical frames with private runtime cleanup.
## US2 — Native vehicle campaign
- [X] T005 Align CARLA/diagnostic/controller startup; preserve fixture behavior and startup assertions.
- [X] T006 Execute real CARLA/native campaign and fixture regression; preserve all verdicts.
## Review and handover
- [X] T007 Verify owned cleanup/original-state preservation; update handover/claims to actual evidence.
- [X] T008 Converge against specification/plan/constitution and commit locally.
Dependencies: T002 before T003; T004 before T005/T006; verification before T007/T008.

## Phase 1: Convergence
- [X] T009 Preserve explicit compiler/schema inputs through overlay setup and verify declared tools are executed per FR005 / Constitution VII (partial).
- [X] T010 Supply explicit harness steering through the existing manual topic and verify sustained physical/native acceptance without overriding native throttle per FR004 / US2 (partial).

## Phase 2: Convergence
- [X] T011 Require repeated native request / existing VCU normalization / subsequent actor-actuation matches with zero operator pedal; reject unrelated positive throttle per FR004 / US2 (partial).

## Phase 3: Convergence
- [X] T012 Verify the current committed reproduction helper with new clean source/native build directories, explicit fresh compiler/schema execution, native core and real CARLA campaigns, then owned teardown per FR005 / SC003 / original reproducible-handover requirement (partial).
- [X] T013 Supply an offline, explicitly historical replay of the saved stable physical run, with source hashes and original verdicts, per FR005 / original F008 stable-run recording and labelled fallback deliverable (partial).

T012 proof: `contributions/shared/evidence/f009-reproduction-current/verification.json`,
`contributions/shared/evidence/f009-reproduction-physical/results.json` and `contributions/shared/evidence/f009-reproduction-bench-down`.
This is the agent's shared-host self-run. The later preservation audit is partial:
`contributions/shared/evidence/f009-reproduction-preservation.json` records one changed original autoverse
dirty-diff identity, left intact; locked application/configuration hashes remain unchanged.
T013 proof: `contributions/shared/evidence/f009-recorded-replay-final`, `contributions/shared/evidence/f009-replay-browser`
and `contributions/shared/evidence/f009-replay-gates` (fixture, failed-run and tampered-source rejection).

## Phase 4: Convergence
- [X] T014 Account for the current original autoverse dirty-diff mismatch and resolve the remaining original-workspace preservation comparison without changing unrelated state per SC003 / Constitution I (partial; HIGH).

T014 proof: `contributions/shared/evidence/f009-preservation-recheck/verification.json` reruns the original
auditor, including universal newline normalization. All seven comparisons pass.
The previous comparison omitted that normalization for156 CRLF sequences; it did
not establish an original-source change. Raw/text identities and method are recorded,
and no original file was edited to resolve the discrepancy.
