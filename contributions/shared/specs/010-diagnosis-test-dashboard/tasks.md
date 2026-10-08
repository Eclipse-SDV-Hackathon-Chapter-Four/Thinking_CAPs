# Tasks: Diagnosis and Test Management Dashboard

## Phase 1 — Setup

- [X] T001 Create local service/config entrypoints in contributions/shared/scripts/run_dashboard.py and contributions/shared/config/dashboard/local.example.json; preserve original source and exclude private state via .gitignore.

## Phase 2 — Foundations

- [X] T002 Implement local HTTP boundaries and scoped artifact/ledger helpers in contributions/shared/integration/dashboard/service.py; verify Host/Origin/token/path rejection in contributions/shared/tests/test_dashboard.py.
- [X] T003 Add validated authoritative run IDs and exclusive bench admission in contributions/shared/scripts/run_campaign.py plus live events in contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py; retain final verdict semantics.

## Phase 3 — US1 Diagnosis (P1)

Independent test: actual native provider unknown/fresh/stale/new session/outage;
fault query loss independent of observations; omitted output explicitly unavailable.

- [X] T004 [US1] Implement bounded OpenSOVD discovery/cache polling in contributions/shared/integration/dashboard/service.py and native-provider acceptance tests in contributions/shared/tests/test_dashboard.py.
- [X] T005 [US1] Render observational diagnosis/source/units/session and independent fault state in contributions/shared/integration/dashboard/web/app.js and contributions/shared/integration/dashboard/web/index.html.

## Phase 4 — US2 Test Manager (P1)

Independent test: two starts yield one UUID; blocked inputs remain blocked; reload
preserves active execution; cancellation restores owned resources or locks admission.

- [X] T006 [US2] Implement openDuT polling and supported campaign/prerequisite reporting in contributions/shared/integration/dashboard/service.py.
- [X] T007 [US2] Implement persisted start/cancel/cleanup/restart coordinator in contributions/shared/integration/dashboard/service.py; verify concurrency/failure boundaries in contributions/shared/tests/test_dashboard.py.
- [X] T008 [US2] Render bench, campaigns, authoritative run/progress and cancellation in contributions/shared/integration/dashboard/web/app.js.

## Phase 5 — US3 Evidence (P2)

Independent test: physical/fixture/failed/blocked original results are unchanged;
report downloads match registered hashes; missing/tampered artifacts are labelled.

- [X] T009 [US3] Implement historical inventory, original verdict/timeline/observation browsing and exact artifact integrity/download in contributions/shared/integration/dashboard/service.py.
- [X] T010 [US3] Render evidence review and historical replay links in contributions/shared/integration/dashboard/web/app.js; verify tamper/path/symlink boundaries in contributions/shared/tests/test_dashboard.py.

## Phase 6 — US4 Usability (P2)

Independent test: keyboard controls at360/1280 widths, outcomes have text, capability
limitations are readable and injected text never executes.

- [X] T011 [US4] Implement responsive accessible style/navigation in contributions/shared/integration/dashboard/web/style.css and contributions/shared/integration/dashboard/web/index.html.
- [X] T012 [US4] Verify real Chromium keyboard/reconnect/timing/layout/text handling in contributions/shared/tests/dashboard_browser_smoke.py and contributions/shared/evidence/f010-browser/.

## Phase 7 — Cross-cutting acceptance

- [X] T013 Capture actual native campaign, interruption cancellation, physical control with dashboard outage, owned teardown and preservation in contributions/shared/evidence/f010-live/.
- [X] T014 Document runnable dashboard and user-deferred second-contributor signoff in contributions/shared/docs/dashboard.md, contributions/shared/docs/completion-audit.md, contributions/shared/docs/feature-backlog.md and contributions/shared/specs/010-diagnosis-test-dashboard/spec.md.
- [X] T015 Run regression and Spec Kit convergence; record requirement/evidence review in contributions/shared/specs/010-diagnosis-test-dashboard/review.md and commit only this slice.

## Dependencies and implementation strategy

T001 -> T002/T003 -> T004/T006/T007 -> browser integration T005/T008.
US3 uses foundation artifacts; US4 finishes shared UI; T013/T014/T015 after all flows.
Independent example: US1 backend and US2 bench adapter have separate worker data;
US3 inventory and US4 stylesheet can be prepared independently after contracts.
Execute sequentially here to avoid shared-file edits. MVP is observational US1;
continue through all four stories and actual acceptance before claiming completion.
