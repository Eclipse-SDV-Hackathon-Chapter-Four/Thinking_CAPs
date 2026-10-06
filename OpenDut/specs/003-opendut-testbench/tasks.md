# F003 tasks
## Setup and foundation
- [X] T001 Specify two-peer local scope and consolidate release research in OpenDut/specs/003-opendut-testbench/.
- [X] T002 Pin images/artifact and implement private preparation in OpenDut/config/testbench/ and OpenDut/scripts/opendut_testbench.py.
- [X] T003 Implement isolated peer setup/capability/network preflight with bounded owned-resource lifecycle.
## US1 — Deployment
- [X] T004 Enroll real peers/devices and deploy one cluster; export redacted state and interfaces.
- [X] T005 Prove Ethernet and GRE forwarding with actual managed interfaces.
## US2 — Vehicle path
- [X] T006 Generate existing SOME/IP config overlays and isolated peer-local IPC.
- [X] T007 Run unchanged bridge plus actual instrumented receiver and capture bidirectional selected flow.
## US3 — Dependency and cleanup
- [X] T008 Interrupt/restore tunnel while diagnostic management remains reachable.
- [X] T009 Verify owned-resource cleanup and repeat deployment.
## Review
- [X] T010 Write completion and requirement-to-evidence links; converge all feature requirements.
Dependencies: T002/T003 precede T004/T005; those precede T006/T007/T008. Cleanup always runs.

## Phase 5: Convergence
- [X] T011 [FR-005/SC-003] Ensure cleanup attempts every owned application/capture even if tunnel restoration or packet parsing fails; OpenDut/tests/opendut_receiver_smoke.py.
- [X] T012 [FR-005/SC-003] Add deterministic forced-failure exercise and retain cleanup assertions, then rerun successful path after changes.
