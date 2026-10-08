# Tasks: F001 — Baseline audit

## Phase 1: Setup
- [X] T001 Install existing Spec Kit Codex integration and establish .specify/memory/constitution.md.
- [X] T002 Preserve supplied inputs in contributions/shared/docs/implementation-brief.md and contributions/shared/docs/architecture/Cruise_Control.drawio.

## Phase 2: Foundation
- [X] T003 Define selected repositories and prepared-work identity in contributions/shared/config/dependencies.lock.json.

## Phase 3: US1 — Actual baseline (P1)
Independent test: audit emits revisions and explicit missing live prerequisites.
- [X] T004 [US1] Test verdict precedence and unavailable dependency handling in contributions/shared/tests/test_baseline_audit.py.
- [X] T005 [US1] Implement bounded read-only audit in contributions/shared/scripts/audit_baseline.py.
- [X] T006 [US1] Capture baseline smoke and artifact identities in contributions/shared/evidence/f001-local-preflight/.
- [X] T007 [US1] Document verified commands and runtime limitations in contributions/shared/docs/baseline.md.

## Phase 4: US2 — Integration boundaries (P2)
Independent test: sources support each selected interface and scope decision.
- [X] T008 [P] [US2] Record dated upstream capabilities in contributions/shared/docs/upstream-status.md.
- [X] T009 [P] [US2] Record openDuT topology prerequisites in contributions/eclipse-opendut/OpenDut/docs/opendut-deployment-research.md.
- [X] T010 [US2] Define actual receiver/process boundaries in contributions/shared/docs/interfaces.md.
- [X] T011 [US2] Record F001–F008 status and user-deferred FOTA in contributions/shared/docs/feature-backlog.md.

## Phase 5: Validation
- [X] T012 Record preparation inventory in contributions/shared/docs/prepared-work.md and F001 convergence in contributions/shared/specs/001-baseline-audit/completion.md.

## Dependencies & Execution Order
Setup -> foundation -> US1 -> US2 -> validation. T008/T009 can research separately;
T010 waits for both. US1 is the audit MVP; live vehicle acceptance is a separate milestone.
