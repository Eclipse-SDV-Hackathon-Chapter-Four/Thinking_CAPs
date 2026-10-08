# Tasks: F002 — Receiver diagnostics

## Phase 1: Setup
- [X] T001 Create isolated controller worktree and record base in contributions/eclipse-opensovd/OpenSOVD/specs/002-receiver-diagnostics/plan.md.
- [X] T002 Pin native OpenSOVD dependencies in contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/Cargo.toml and Cargo.lock.

## Phase 2: Foundation
- [X] T003 Define validated observation/cache types in contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/src/lib.rs.

## Phase 3: US1 — Actual state (P1)
Independent test: instrumented receiver values match native provider output.
- [X] T004 [US1] Add nonblocking sender tests in contributions/eclipse-opensovd/OpenSOVD/patches/receiver-diagnostics/test_sender.cpp.
- [X] T005 [US1] Instrument actual C++ receipt/acceptance/controller state in isolated controller worktree.
- [X] T006 [US1] Implement native OpenSOVD App data provider in contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/src/main.rs.
- [X] T007 [US1] Build controller and capture actual receiving-side diagnostic integration evidence in contributions/shared/evidence/f002-receiver/.

## Phase 4: US2 — Unknown/stale boundary (P2)
Independent test: absence, loss, restart and invalid clock remain distinguishable.
- [X] T008 [US2] Add Rust boundary/provenance/cache tests in contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/src/lib.rs.
- [X] T009 [US2] Add native HTTP fixture smoke in contributions/eclipse-opensovd/OpenSOVD/tests/diagnostic_http_smoke.py and contributions/shared/evidence/f002-http-fixture/.
- [X] T010 [US2] Verify unavailable/full diagnostic socket never blocks sender in contributions/eclipse-opensovd/OpenSOVD/patches/receiver-diagnostics/test_sender.cpp.

## Phase 5: Validation
- [X] T011 Export reviewable patch in contributions/eclipse-opensovd/OpenSOVD/patches/receiver-diagnostics/s-core-observation.patch and deployment guide contributions/eclipse-opensovd/OpenSOVD/scripts/run_diagnostics.sh.
- [X] T012 Record achieved verification levels/blockers in contributions/eclipse-opensovd/OpenSOVD/specs/002-receiver-diagnostics/completion.md and contributions/shared/docs/feature-backlog.md.

## Dependencies & Execution Order
Setup -> foundation -> US1 -> US2 -> review. Tests precede new transport logic.
T006 and upstream build preparation can progress separately after contract agreement.
MVP is truthful native data provider; live receiver acceptance requires T007 and is not replaced by T009.
