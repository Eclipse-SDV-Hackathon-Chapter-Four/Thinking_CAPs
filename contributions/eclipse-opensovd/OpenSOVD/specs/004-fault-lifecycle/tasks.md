# F004 tasks
## Foundation
- [X] T001 Specify scope and consolidate actual upstream APIs/persistence research.
- [X] T002 Pin optional native fault dependencies and catalog in contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics and contributions/eclipse-opensovd/OpenSOVD/config/faults/.
- [X] T003 Add failing OS-process durability/clear/write-error regression in isolated fault-lib worktree.
- [X] T004 Implement opt-in write-through native storage and export reviewable patch.
## US1 — Timeout policy
- [X] T005 Add meaningful monitor clock/startup/debounce/recovery/source-loss tests before implementation.
- [X] T006 Implement deterministic receiver watchdog outside control path.
## US2 — Upstream lifecycle/query
- [X] T007 Connect actual Reporter/FaultApi -> native IPC -> DFM write-through storage.
- [X] T008 Map cached native query evidence into labelled OpenSOVD cc.fault-history data resource.
- [X] T009 Run actual openDuT receiver timeout/recovery with measured baseline and stored history assertions.
- [X] T010 Verify separate OS-process fault history reload and durable clear, plus flush error propagation.
## US3 — Unavailability
- [X] T011 Test source loss/restart/query failure preserving unknown and retained history.
## Review
- [X] T012 Run affected upstream/contract/native tests and mandatory checks where available; document exact limits.
- [X] T013 Record requirement/evidence links and converge feature acceptance in completion.md.
Dependencies: T003 before T004; T005 before T006; T002/T004/T006 before T007/T008;
real T009 depends on completed F003. Native /faults remains a separately blocked milestone.

## Phase 5: Shutdown boundary discovered during implementation
- [X] T014 Initialize native signal handling before application SIGINT/SIGTERM ownership and verify clean shutdown with native IPC active.
