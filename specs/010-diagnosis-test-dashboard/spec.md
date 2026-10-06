# Feature Specification: Vehicle Diagnosis and Test Management Dashboard

**Feature Branch**: `contributions/eclipse-sdv-hackathon` (feature directory `010-diagnosis-test-dashboard`)

**Created**: 2026-10-04

**Status**: Implemented; native/physical/browser verification recorded

**Input**: User description: "specify also a web-based dashboard to have a UI for the diagnosis via OpenSOVD and Test Manager via OpenDuT"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Diagnose the actual receiver (Priority: P1)

An operator selects the configured receiver and uses the Diagnosis view to inspect observations exposed by OpenSOVD. They can distinguish service availability from receiver freshness, see Cruise Control values with their source identity, and inspect communication fault history.

**Why this priority**: The demonstration needs a readable explanation of what the actual receiver consumed and why it reported a fault, including times when telemetry cannot support a conclusion.

**Independent Test**: With diagnosis available and no campaign running, observe fresh data, interrupt observations, and recover them. Verify that freshness and fault history follow the reported diagnostic truth.

**Acceptance Scenarios**:

1. **Given** OpenSOVD exposes a receiver with fresh observations, **When** it is selected, **Then** the view shows consumed speed, target speed, engagement, control output, units, sample age and available source identity, identifying unavailable fields individually.
2. **Given** diagnosis responds but the receiver has no first sample or its samples become stale, **When** the view refreshes, **Then** it shows unknown or stale separately from service availability and preserves the last observation timestamp.
3. **Given** the receiver monitor reports a failed communication fault and later recovery, **When** fault history is opened, **Then** the view shows the reported assessment, occurrence count and available transition times, labels monitor-derived assessment, and retains the earlier failure after recovery.
4. **Given** OpenSOVD becomes unreachable, **When** refresh fails, **Then** diagnosis is unavailable, retained values are labelled last observed, and cached data is never presented as current health.
5. **Given** the receiver restarts with a new identity, **When** observations arrive, **Then** the view identifies the new receiver session and does not combine its freshness with the previous session.

---

### User Story 2 - Run and stop campaigns on an openDuT testbench (Priority: P1)

An operator uses Test Manager to inspect the configured openDuT testbench, its peers and device attachments, choose a supported campaign, check prerequisites, and follow execution. They can request cancellation and see whether the runner restored resources it owns.

**Why this priority**: Visible, repeatable fault injection and recovery make diagnosis understandable and demonstrate meaningful openDuT use in the vehicle control path.

**Independent Test**: Run a campaign on the existing two-peer testbench, refresh the browser during execution, and cancel a second run during a link interruption. Verify authoritative run status, evidence and owned-resource restoration.

**Acceptance Scenarios**:

1. **Given** the configured testbench is reachable, **When** Test Manager opens, **Then** its peers, attached device interfaces, connectivity and observed deployment profile are visible with update times.
2. **Given** required services, artifacts or connections are missing, **When** a campaign is selected, **Then** missing prerequisites are listed and an attempted execution records a blocked outcome rather than a pass.
3. **Given** prerequisites are satisfied and the bench is idle, **When** a campaign starts, **Then** exactly one run receives an identifier and shows its campaign, testbench, evidence mode and progress.
4. **Given** a run is active, **When** the browser reloads, disconnects or a second browser opens, **Then** it reconnects to the authoritative run state without starting a duplicate or declaring the run stopped merely because the browser lost contact.
5. **Given** a run interrupted an owned link, **When** cancellation is requested, **Then** it remains pending until termination and cleanup are acknowledged; successful and failed cleanup are separately visible and unrelated resources remain unchanged.
6. **Given** checks finish, **When** results are displayed, **Then** passed, failed, blocked and skipped assertions retain their runner verdicts and reasons; cancellation is explicit and never treated as successful execution.

---

### User Story 3 - Review and share the evidence (Priority: P2)

An operator reviews a completed run's assertions, fault timeline, recovery and cleanup alongside captured diagnostic observations. They can download reports and provenance or open saved replay when the live environment is unavailable.

**Why this priority**: Judges and contributors must connect visible results to captured evidence and distinguish actual vehicle execution from fixtures and historical recordings.

**Independent Test**: Load one passed physical run, one fixture and one failed or blocked run; inspect and download their evidence without starting vehicle services.

**Acceptance Scenarios**:

1. **Given** a completed physical campaign, **When** it is selected, **Then** original verdicts, injections, diagnostic transitions, recovery and cleanup link to captured evidence with declared clock domains.
2. **Given** a fixture, saved replay or incomplete evidence, **When** it is opened, **Then** its mode and limitations remain visible and it cannot supply current live vehicle health.
3. **Given** artifacts exist, **When** they are downloaded, **Then** saved report, test report, manifest and applicable capture bytes and identities are preserved; secrets and unrelated files are excluded.
4. **Given** an artifact is missing or fails its recorded integrity check, **When** results are reviewed, **Then** the evidence problem is identified without rewriting the original runner verdict or asserting verified integrity.

---

### User Story 4 - Use an understandable demonstration interface (Priority: P2)

An operator navigates Diagnosis and Test Manager in a browser, reads status without relying only on color, and sees which capabilities the deployed environment actually supports.

**Why this priority**: The integration should be demonstrable without terminal knowledge or suggestions that conditional upstream capabilities are implemented.

**Independent Test**: Navigate primary flows with a keyboard at desktop and phone widths, including unavailable-service and historical-result views.

**Acceptance Scenarios**:

1. **Given** the dashboard is open, **When** the operator switches views, **Then** the selected target and active run remain identifiable and either view is reachable in at most two navigation actions.
2. **Given** a capability is unsupported, **When** its summary is viewed, **Then** it explains the limitation and offers no working-looking action that fabricates success.
3. **Given** a narrow display or keyboard-only interaction, **When** diagnosis is inspected and a campaign is run, **Then** labels, controls, focus and outcome reasons remain usable without color-only distinctions.

### Edge Cases

- Diagnosis available while the receiver is starting, stale, restarting or unknown.
- Fault history unavailable while observations remain available; capabilities are reported independently.
- openDuT management unreachable while a campaign continues; status remains last observed or unknown until reconciled.
- Double-clicked starts, requests from two browsers and a busy bench; only one campaign may own that bench.
- Cancellation during injection, restoration failure or runner termination; incomplete cleanup cannot appear successful.
- Browser closes during execution; closing a page does not cancel the run.
- Partial observations, missing units and separate simulation/observation clocks; missing values remain unavailable and clocks are not silently merged.
- Long history or large captures; bounded browsing and artifact download do not require loading every capture into the page.
- Historical physical run selected while live services are unavailable; historical truth remains separate from live status.
- Unusual target or run names are displayed as data and cannot create executable page content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide browser-accessible Diagnosis and Test Manager views preserving selected target and active run context. Acceptance: Story 4.1.
- **FR-002**: Diagnosis MUST discover configured receiver resources through OpenSOVD and display available fields without invented values. Acceptance: Story 1.1 and partial-observation edge case.
- **FR-003**: Diagnosis MUST distinguish service reachability, receiver freshness and fault assessment, retain timestamps and identity, and preserve unknown, stale and unavailable states. Acceptance: Stories 1.2, 1.4 and 1.5.
- **FR-004**: Diagnosis MUST display available fault history, occurrence and transition evidence and label monitor-derived assessment; unsupported native fault capabilities MUST be distinguished from supported history. Acceptance: Story 1.3 and unavailable-history edge case.
- **FR-005**: Test Manager MUST show observed openDuT peers, device attachments, connectivity and deployment profile, including local versus distributed connection and enabled networking capabilities. Acceptance: Story 2.1.
- **FR-006**: Test Manager MUST offer only supported configured project campaigns and identify prerequisites, target and physical, fixture or recorded evidence mode before execution. Acceptance: Stories 2.2 and 2.3.
- **FR-007**: Only one campaign MUST own a bench at a time; duplicate starts MUST be prevented and authoritative run identity/state recovered after reconnection. Acceptance: Stories 2.3 and 2.4 and concurrent-start edge case.
- **FR-008**: Operators MUST be able to request cancellation; requested cancellation, termination, successful cleanup and incomplete cleanup MUST be distinguished. Closing the browser MUST NOT cancel execution. Acceptance: Story 2.5 and browser-close edge case.
- **FR-009**: Run control and cleanup MUST affect only configured integration-owned resources; arbitrary commands and unrelated processes/networks MUST NOT be operator actions. Acceptance: Story 2.5 with preservation comparison.
- **FR-010**: The dashboard MUST preserve runner assertion verdicts and reasons, including failed, blocked and skipped outcomes, and show cancellation separately. Acceptance: Stories 2.6 and 3.4.
- **FR-011**: Operators MUST be able to inspect timelines and observations with their source and clock domains and links to captured evidence. Acceptance: Story 3.1.
- **FR-012**: Operators MUST be able to retrieve saved reports/provenance with unchanged artifact bytes; missing artifacts and failed integrity checks MUST be visible. Acceptance: Stories 3.3 and 3.4.
- **FR-013**: Historical reports and replay MUST remain visibly distinguished from live status; fixtures and recordings MUST NOT establish current physical success. Acceptance: Story 3.2 and saved-run edge case.
- **FR-014**: Dashboard refreshes and service loss MUST NOT synchronously delay vehicle control or automatically engage Cruise Control. Acceptance: induced UI service loss during a nominal campaign retains existing control assertions.
- **FR-015**: Primary flows MUST support keyboard operation, text-labelled outcomes and 360-pixel and 1280-pixel viewport widths. Acceptance: Story 4.3.
- **FR-016**: The dashboard MUST identify project campaign orchestration on an openDuT-managed bench separately from any unavailable upstream test executor/reporting capability. Acceptance: Story 4.2 against the deployment capability record.
- **FR-017**: The initial UI MUST exclude AAOS/FOTA, fault-history deletion, direct vehicle actuation and public publishing controls. Acceptance: primary-flow review contains no such actions or simulated deferred success.

### Key Entities *(include if feature involves data)*

- **Diagnostic target**: Configured receiver and available OpenSOVD resources/capabilities.
- **Observation**: Values, units, timestamp, age, freshness and source/session identity for a reported snapshot.
- **Fault entry**: Reported identifier, assessment, occurrence count, available transition times and assessment origin.
- **Testbench**: Configured openDuT peers, device attachments, observed connectivity, deployment profile and resource ownership.
- **Campaign definition**: Supported campaign, prerequisites, eligible testbench and evidence mode.
- **Campaign run**: Identifier, selected inputs, progress, authoritative state, verdicts, cancellation and cleanup outcome.
- **Evidence artifact**: Saved report, timeline, observation, replay or capture linked to a run with provenance and available integrity information.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Either primary view is reachable in at most two navigation actions; an operator identifies receiver freshness and selected run outcome within 30 seconds in a timed walkthrough.
- **SC-002**: At least 95% of newly acquired observations appear within two seconds of dashboard acquisition in a nominal demonstration. Diagnostic unreachability is labelled within five seconds of a failed refresh, retaining last-observed times.
- **SC-003**: Every startup, stale-receiver, diagnostic outage and restart acceptance case shows the expected state with zero false healthy indications.
- **SC-004**: Two simultaneous clients and repeated start actions create exactly one run per idle bench. Reload/reconnection recover that same run identifier in every acceptance case.
- **SC-005**: Passed, failed, blocked, skipped and cancelled examples retain 100% of underlying assertion verdicts/reasons. Missing prerequisites and incomplete cleanup yield zero successful campaign indications.
- **SC-006**: Cancellation during a controlled interruption restores all resources required by the runner's cleanup contract or visibly identifies each failed restoration; all unrelated-resource preservation comparisons pass.
- **SC-007**: Every available required report for a selected run downloads with matching saved content identity; every missing or integrity-failed artifact is labelled. Physical, fixture and recorded examples remain visibly distinct.
- **SC-008**: All primary flows can be completed with only a keyboard at 360-pixel and 1280-pixel widths, with readable labels and outcome reasons.
- **SC-009**: Repeated dashboard refresh and an induced dashboard outage leave existing nominal control and return-actuation assertions passing, with no automatic engagement introduced.

## Assumptions

- This specifies the requested dashboard; live UI implementation is verified in F010 evidence. Existing offline replay is a separate saved-evidence artifact.
- Initial deployment is a local hackathon tool on the configured host or explicitly configured private test network. Public hosting, multi-tenant access and account provisioning are outside this slice. Exposure and access controls will be addressed during planning.
- Existing X-Verse/CARLA, receiver diagnostics, native fault history, openDuT and deterministic campaign/evidence contracts are reused; vehicle components and bridge are preserved.
- The verified openDuT profile currently connects two local peers. Its observed profile must be reported without implying distributed networking or an available upstream executor.
- Existing campaign definitions govern injection duration, verdicts, prerequisites and cleanup. The dashboard exposes them rather than redefining fault acceptance or accepting arbitrary scripts.
- Diagnosis is observational. Direct control, fault deletion and updates are excluded; AAOS/FOTA remains deferred by the user.
- Two concurrent browsers and one active campaign per bench suffice for the first slice.
- The existing diagnostic contract determines freshness; UI polling does not redefine the receiver watchdog or equate service availability with fault health.
- Prepared work remains labelled preparation; the UI does not establish event eligibility or independent human reproduction.
