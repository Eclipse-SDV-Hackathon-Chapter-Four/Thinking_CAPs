# Feature Specification: F001 — Baseline and compatibility audit

**Feature Branch**: `contributions/eclipse-sdv-hackathon`
**Created**: 2026-10-04
**Status**: Specified
**Input**: Implement the supplied plan against the current X-Verse/CARLA environment.

## User Scenarios & Testing

### User Story 1 — Identify the actual baseline (Priority: P1)
An integrator can identify code, runtime artifacts, signals and commands without modifying
the bridge or losing working changes.
**Independent Test**: Run the audit and inspect its revision/configuration manifest.
**Acceptance Scenarios**:
1. Given the workspace, when audited, then selected repositories have exact revisions,
   dirty state and available runtime artifact identities recorded.
2. Given missing binaries/services, when smoke testing, then missing prerequisites are
   named and no running vehicle function is claimed.

### User Story 2 — Select supported boundaries (Priority: P2)
An implementer can select observation, diagnostics, networking and update boundaries from source.
**Independent Test**: Review interfaces and the dated upstream capability matrix.
**Acceptance Scenarios**:
1. Given feature proposals, when audited, then issue state is distinguished from actual routes.
2. Given an unavailable updater, when planning, then target is unknown and F006 is blocked.

### Edge Cases
- Dirty nested repositories: preserve revision and dirty-state evidence.
- No CARLA server, no AAOS device or broken artifact links: blocked live result.
- GitHub unavailable: unknown current state rather than recycled observations.
- Shared IPC paths: avoid destructive existing launcher cleanup against running processes.

## Requirements

### Functional Requirements
- **FR-001 / REQ-001**: Preserve bridge bytes and unrelated worktree changes.
- **FR-002 / REQ-010**: Emit audit evidence with revisions, hashes and tool versions.
- **FR-003 / REQ-011**: Distinguish failed/blocked/skipped checks; incomplete live readiness exits nonzero.
- **FR-004 / REQ-016**: Classify prepared assets, real processes and fixture evidence.
- **FR-005 / REQ-022**: Inspect upstream issues and actual interfaces before contribution selection.
- **FR-006**: Locate/classify the existing AAOS update asset or name the missing input.
- **FR-007**: Establish constitution and separate F001–F008 backlog entries.

### Key Entities
- Baseline manifest: revision, dirty state, configuration digest and executable identity.
- Smoke result: check ID, verdict, command, output and limitation.
- Capability decision: source, observed state/date, implementation evidence and scope/blocker.

## Success Criteria

### Measurable Outcomes
- **SC-001**: Every selected dependency has a revision or explicit unavailable status.
- **SC-002**: A repeatable command produces evidence and names missing prerequisites.
- **SC-003**: F002–F008 have bounded next actions and accurate readiness statuses.
- **SC-004**: Bridge sources and user modifications remain unchanged by the audit.

## Assumptions
- Use the integration repository already selected in this conversation.
- Prefer existing pins over automatic upgrades to planning snapshots.
- Precise runtime blockers satisfy audit exit; full vehicle acceptance remains incomplete.
- Contract tests are required for verdicts and unavailable-observation preservation.
