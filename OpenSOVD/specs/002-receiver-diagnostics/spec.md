# Feature Specification: F002 — Actual receiving-side diagnostics

**Feature Branch**: `contributions/eclipse-sdv-hackathon`
**Created**: 2026-10-04
**Status**: Specified
**Input**: Expose actual S-CORE Cruise Control receiver state through native OpenSOVD.

## User Scenarios & Testing

### User Story 1 — Inspect actual receiver state (Priority: P1)
A diagnostic client discovers the controller and reads its actual accepted speed, target,
engagement, per-event receipt/acceptance timestamps and software identity.
**Independent Test**: Instrumented native consumer emits observations; OpenSOVD returns their values.
**Acceptance Scenarios**:
1. Given a speed sample accepted by the S-CORE consumer, when read, then its value/unit,
   receiver identity and timestamps are preserved through the diagnostic provider.
2. Given an unrelated clock update, when speed input has stopped, then speed age is not refreshed.
3. Given unavailable sequence/E2E, when read, then they are explicitly unavailable.

### User Story 2 — Distinguish stale and absent evidence (Priority: P2)
Clients can distinguish source absence, receiver silence, stale accepted values and healthy data.
**Independent Test**: Boundary tests cover startup, speed loss, heartbeat loss, wrong clock and restart.
**Acceptance Scenarios**:
1. Given no collector, when read, then values/state are unknown.
2. Given expired source heartbeat, when read, then receiver availability is stale even if cached speed exists.
3. Given diagnostics unavailable/slow, when the controller runs, then socket writes remain bounded/nonblocking.

### Edge Cases
- Datagram loss/full socket: drop observation; never block the control loop.
- Invalid speed payload: record receipt separately; acceptance timestamp must not advance.
- Wrong boot/clock, future timestamp, malformed JSON or conflicting source: reject observation.
- Controller restart: new source session resets cache provenance; no old healthy identity.
- CARLA sim clock may pause; freshness uses receiver host CLOCK_MONOTONIC only.

## Requirements

### Functional Requirements
- **FR-001 / REQ-001**: Bridge source and existing controller decisions remain unchanged.
- **FR-002 / REQ-002**: Observe native consumer and actual controller state with units/provenance.
- **FR-003 / REQ-003**: Never infer healthy, integrity pass or disengagement from missing observations.
- **FR-004 / REQ-004**: Bounded nonblocking local observation transport; HTTP reads cached state.
- **FR-005**: Validate contract version, boot/clock/source and timestamps before accepting observations.
- **FR-006 / REQ-019**: Per-event accepted age is distinct from received age; invalid payloads cannot refresh acceptance.
- **FR-007 / REQ-010**: Tests and runs distinguish fixture integration from real vehicle evidence.

### Key Entities
Observation: source session, boot ID, monotonic heartbeat, speed receipt/acceptance, values and identity.
Diagnostic view: original observation plus derived receiver/speed freshness and unavailable capabilities.

## Success Criteria

### Measurable Outcomes
- **SC-001**: Accepted speed changes are visible through native OpenSOVD with exact units/source.
- **SC-002**: Boundary tests distinguish startup, fresh, stale, invalid and source-unavailable states.
- **SC-003**: A missing/full diagnostic socket never prevents control iteration completion.
- **SC-004**: Live acceptance is complete only after instrumented real receiver comparison; fixtures are partial evidence.

## Assumptions
Linux co-located observer/provider with CLOCK_MONOTONIC and boot ID. No supported Rust mw::com
binding is assumed. Configurable freshness budgets are provisional until baseline jitter is measured.
Fault lifecycle, native faults, openDuT and updates are later separate features. Contract/native
integration tests are required. Instrumentation is prepared work in an isolated S-CORE worktree.
