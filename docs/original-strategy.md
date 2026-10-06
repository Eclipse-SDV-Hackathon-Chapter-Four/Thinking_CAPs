# SDV Hackathon Chapter Four: Winning Strategy

## Trusted Cruise Control: From Corrupted Signal to Diagnostic Evidence

**Architecture baseline:** Cruise Control Diagnostics Architecture v4.1  
**Team:** Five contributors  
**Track:** Eclipse SDV Hackathon Chapter Four, Track 2  
**Primary goal:** Deliver reviewable upstream contributions with a stable, reproducible end-to-end demonstration.

---

## 1. Executive Strategy

The architecture already provides a detailed OpenSOVD diagnostic chain, concrete contribution candidates, a Cruise Control scenario, fault ownership, standard diagnostic entities, and multiple fallback levels.

The winning strategy is not to replace the existing architecture with a separate E2E concept. E2E protection becomes the technical differentiator that strengthens the existing diagnostic chain.

> **Build a trustworthy Cruise Control diagnostic chain where S-CORE detects communication-integrity failures through E2E protection, reports them through the agreed Fault Library interface, and exposes the resulting diagnostic evidence through OpenSOVD.**

### Strategic hierarchy

1. **Primary contribution:** Accepted, reviewable upstream contributions around existing OpenSOVD and S-CORE work.
2. **Technical differentiator:** E2E protection in the S-CORE SOME/IP Gateway.
3. **Demo backbone:** The existing Cruise Control diagnostics architecture.
4. **Fault and evidence path:** Fault Library to DFM-lite to OpenSOVD faults resource.
5. **Validation asset:** X-Verse scenarios and deterministic fault injection.
6. **Bonus projects:** openDuT and AutoSD only after the core path is stable.

---

## 2. Winning Story in One Sentence

> **A Cruise Control function receives information over an untrusted SOME/IP channel, S-CORE verifies whether the communication can be trusted, and OpenSOVD explains the resulting failure to an external diagnostic client.**

### End-to-end journey

```text
Vehicle signal
    ↓
Cruise Control function
    ↓
Protected SOME/IP message
    ↓
S-CORE SOME/IP Gateway
    ↓
E2E verification
    ↓
mw::com sample plus integrity status
    ↓
cruise-diag monitor
    ↓
Fault Library
    ↓
DFM-lite
    ↓
OpenSOVD faults resource
    ↓
Diagnostic client
```

---

## 3. Why the Strategy Changed

The Cruise Control architecture already defines:

- A partner Cruise Control application publishing `CruiseControlStatus`
- SOME/IP and SOME/IP-SD between two machines
- S-CORE `someipd` and `gatewayd`
- Local communication through mw::com
- A Rust `cruise-diag` application
- Fault reporting through `fault-lib`
- A DFM-lite stand-in behind upstream interfaces
- OpenSOVD data and faults resources
- A SOVD client and live console
- A Classic Diagnostic Adapter path
- Three live fallback levels and a video fallback

E2E protection should therefore be inserted into the established path rather than creating a second architecture.

---

## 4. E2E as the Missing Trust Layer

The current partner interface contains:

- `vehicle_speed`
- `vehicle_speed_q`
- `set_speed`
- `cc_state`
- `sensor_fault_status`
- `alive_counter`

The stronger upstream contribution is a proper E2E mechanism:

```text
Current proposal
vehicle_speed_q + alive_counter

Improved proposal
payload + configured E2E profile + CRC + counter + E2E check result
```

| Concern | Owner |
|---|---|
| Is the vehicle speed physically plausible? | Partner Cruise Control application |
| Is the communication payload intact? | S-CORE E2E Gateway |
| Has a message been repeated or lost? | E2E checking and receiving monitor |
| Has communication stopped completely? | `cruise-diag` watchdog |
| How is the fault reported and stored? | Fault Library and DFM-lite |
| How is the result exposed externally? | OpenSOVD |

> **Delivery does not equal trust. E2E establishes whether the delivered message can safely be consumed.**

---

## 5. Revised Fault Model

### Existing faults

- **F1:** `CC.SpeedInputInvalid`
- **F1-prime:** `CC.SpeedInputObserver`
- **F2:** `CC.LostCommunication`

### New fault: F3 `CC.CommunicationIntegrityFailed`

**Detected by:** The S-CORE receiving side, based on the gateway E2E result.

**Candidate trigger conditions:**

- CRC mismatch
- Repeated counter
- Unexpected counter discontinuity
- Wrong sequence
- Invalid protection information

The final trigger set must match the selected E2E profile and maintainer-approved scope.

| Fault | Meaning | Owner |
|---|---|---|
| F1 | Invalid speed input identified by the function | Partner Cruise Control function |
| F1-prime | Locally observed implausible input | `cruise-diag`, fallback only |
| F2 | No communication beyond the configured timeout | `cruise-diag` watchdog |
| F3 | A message arrived but E2E verification failed | S-CORE receiving side |
| ECU DTCs | Internal faults of the classic ECU | Classic ECU simulator |

> **F1 detects invalid function input. F2 detects silence. F3 detects corrupted communication. Each fault has one reason and one owner.**

---

## 6. Preserve the Agreed Fault Path

```text
E2E check result
    ↓
cruise-diag communication-integrity monitor
    ↓
fault-lib Reporter for F3
    ↓
FaultSink
    ↓
DFM-lite
    ↓
FaultProvider
    ↓
OpenSOVD faults resource
```

Avoid a custom HTTP shortcut from the gateway directly to the demo console. E2E failures should use the agreed Fault Library path.

---

## 7. Revised Demonstration

### Step 1: Trusted cruising

- Valid protected Cruise Control messages
- CRC succeeds
- Counter sequence is valid
- Cruise Control is active
- No faults

### Step 2: Sensor fault

- Partner detects invalid speed input
- `sensor_fault_status` becomes `FAILED`
- Cruise Control enters `UNAVAILABLE`
- F1 is published through the Fault Library

### Step 3: Diagnose the function

- SOVD client reads F1
- Fault status and snapshot are visible

### Step 4: Corrupt the communication

- Fault injector modifies one protected byte or protection field
- SOME/IP still delivers the message
- S-CORE E2E verification fails
- F3 is reported
- The application does not silently treat the data as valid

### Step 5: Pull the cable

- No sample arrives
- The timeout expires
- F2 is reported
- The demo distinguishes integrity failure from complete communication loss

### Step 6: Show diagnostic breadth

- The same client reads a classic ECU through the CDA
- Modern S-CORE diagnostics and legacy ECU diagnostics are visible through one diagnostic experience

> **When the cable is pulled, we detect silence. When the cable stays connected but the data is corrupted, we detect broken trust. OpenSOVD explains both.**

---

## 8. Contribution Portfolio

### PR A: S-CORE E2E contribution

- E2E plug-in interface or bounded implementation slice
- One event-based provider or profile slice
- Outbound protection
- Inbound verification
- Configuration and schema validation
- Unit and component tests
- Requirement traceability
- Clear limitations and continuation plan

### PR B: OpenSOVD agreed contribution slice

Only after coordination with existing owners and maintainers:

- Mock wiring
- End-to-end tests
- Status semantics
- Fault-provider integration support
- Documentation or examples

### PR C: Demonstration and integration assets

- Cruise Control diagnostic integration
- X-Verse scenario
- DFM-lite stand-in
- Fault Library wiring
- Reproduction scripts
- Architecture documentation

---

## 9. Role of Each Project

### S-CORE

- Hosts the core upstream contribution
- Protects and verifies SOME/IP communication
- Carries trusted data and integrity status toward the application

### OpenSOVD

- Exposes faults and diagnostic evidence
- Provides the diagnostic model and client-facing API
- Gives the failure a community continuation path

### X-Verse

- Provides the realistic scenario
- Generates valid and invalid communication sequences
- Drives deterministic fault injection
- Strengthens the demo without becoming an upstream dependency

### openDuT

First bonus stretch goal:

- Reproduce the communication fault campaign
- Capture valid, corrupted, repeated, missing and recovered scenarios
- Stay outside the critical upstream test path

### AutoSD

Second bonus stretch goal:

- Provide a representative deployment target
- Be attempted only after the core Linux path is stable

### Priority

```text
1. S-CORE E2E contribution
2. OpenSOVD fault path
3. Stable Cruise Control demo
4. Independent automated tests
5. openDuT bonus
6. AutoSD bonus
```

---

## 10. Team of Five

| Team member | Primary ownership |
|---|---|
| X-Verse and architecture expert | Scenario, corruption injection, architecture, scope, story and demo choreography |
| S-CORE expert | E2E plug-in, gateway integration, configuration, maintainer alignment and upstream PR |
| Developer 3 | E2E provider, CRC, counter handling, configuration schema and unit tests |
| Developer 4 | `cruise-diag`, F2/F3 monitors, Fault Library integration and automated tests |
| Developer 5 | DFM-lite, OpenSOVD faults resource, SOVD client, documentation and handover |

Each contributor owns an artifact, not only an activity.

---

## 11. Hackathon Execution Plan

### Phase 1: Confirm the contribution

- Validate the current E2E gap
- Agree the insertion point with maintainers
- Select one bounded profile or provider slice
- Agree invalid-data behavior
- Create or reference the upstream issue
- Declare prepared artifacts

### Phase 2: Build the smallest vertical slice

```text
Partner or simulator
    ↓
Protected SOME/IP event
    ↓
someipd
    ↓
gatewayd E2E verification
    ↓
mw::com sample and integrity result
    ↓
cruise-diag
    ↓
Fault Library
    ↓
DFM-lite
    ↓
OpenSOVD client
```

### Phase 3: Add failure variants

1. Valid message
2. CRC corruption
3. Counter discontinuity
4. Communication timeout
5. Recovery, if supported by the agreed policy

### Phase 4: Protect technical quality

- Clean build
- Unit tests
- Component tests
- Automated integration test
- Configuration validation
- Requirement traceability
- Reproduction on a second machine
- Known limitations
- Draft PR opened early

### Phase 5: Add stretch integrations

- openDuT fault campaign
- AutoSD deployment

Stop stretch work if it threatens the primary PR, tests or demo stability.

---

## 12. Fallback Ladder

| Level | Source | What remains live |
|---|---|---|
| L3 | Partner Cruise Control through SOME/IP and mw::com | Full chain, including E2E and partner hook |
| L2 | Team-owned mw::com publisher | OpenSOVD and diagnostic chain, without external SOME/IP |
| L1 | In-process simulator | OpenSOVD, Fault Library, DFM-lite and diagnostic evidence |
| L0 | Recorded video | Evidence from the first stable full run |

Add a gateway-level test mode with a lightweight SOME/IP endpoint so the E2E path can run without the partner application.

---

## 13. Score Optimization

| Criterion | Strategy |
|---|---|
| Contribution Value | Advance an official S-CORE E2E requirement with a maintainer-aligned PR |
| Technical Quality | Provider abstraction, configuration, tests, traceability and clear boundaries |
| Ecosystem Impact | Connect S-CORE communication integrity with OpenSOVD diagnostic visibility |
| Reusability | Native automated tests do not depend on X-Verse or the full demo |
| Handover Clarity | Public issue, PR, architecture, README, evidence and limitations |
| Community Continuation | Additional profiles, production DFM and reference integration follow-ups |
| Focus and Initiative | Complete one vertical slice before any bonus technology |

### Bonus strategy

- **openDuT:** first bonus target
- **AutoSD:** second bonus target
- **OpenSOVD:** ecosystem-impact contributor, not an explicit bonus technology
- **Java/Jakarta EE:** exclude unless naturally required
- **ThreadX:** exclude from the base scope

---

## 14. Risk Register

| Risk | Mitigation |
|---|---|
| E2E gap differs from assumptions | Audit current main and confirm with maintainers |
| Existing OpenSOVD work is assigned | Coordinate a split and avoid racing the owner |
| Diagnostic adapter remains blocked | Keep the demo host independent and treat the adapter as stretch work |
| Partner interface is unavailable | Use L2 or a gateway test endpoint |
| Venue blocks multicast | Use direct cable, static IPs and deterministic configuration |
| E2E scope becomes too broad | One event, one profile slice, one valid case and two negative cases |
| LoLa change becomes necessary | Prefer gateway metadata and a bounded consumer contract |
| OpenSOVD path grows too large | Keep DFM-lite behind upstream interfaces |
| Bonus projects destabilize delivery | Gate openDuT and AutoSD behind a stable core slice |
| Safety claims exceed evidence | Say ASIL-B requirement context, not ASIL-B certification |
| Prepared work conflicts with rules | Inventory and declare every prepared artifact |

---

## 15. Updated Storytelling

### Act 1: A valid function

A Cruise Control function publishes over SOME/IP. S-CORE verifies E2E protection and makes trusted data available through mw::com. The SOVD client shows a healthy function.

### Act 2: The function detects invalid input

The partner identifies invalid speed input and places Cruise Control in `UNAVAILABLE`. The function reports F1 through the Fault Library. OpenSOVD exposes the status and snapshot.

### Act 3: Communication is corrupted

The message reaches the vehicle computer, but E2E protection is invalid. S-CORE recognizes that delivery does not equal trust. The receiving side reports F3 through the agreed path.

### Act 4: Communication disappears

The cable is pulled. No message arrives. The watchdog reports F2, distinguishing lost communication from corrupted communication.

### Act 5: One diagnostic language

The same SOVD client reads S-CORE faults and a classic ECU through the CDA.

> **The function owns its faults. The receiver owns communication failures. S-CORE establishes trust. OpenSOVD explains the result. X-Verse makes every scenario reproducible.**

---

## 16. Four-Minute Pitch

### 0:00 to 0:30 | Problem

“Software-defined vehicles exchange critical information across applications and ECUs. But receiving a message does not prove that the message is trustworthy.”

### 0:30 to 1:00 | Existing need

“S-CORE already defines an E2E protection requirement for the SOME/IP Gateway. We advance that requirement and connect its result to the OpenSOVD diagnostic model.”

### 1:00 to 1:30 | Contribution

“We implement a configurable E2E extension for the S-CORE SOME/IP Gateway. It protects outbound traffic, verifies inbound traffic and associates application data with an integrity result.”

### 1:30 to 2:30 | Demonstration

“A valid Cruise Control message passes CRC and sequence verification. Next, we corrupt a protected byte. SOME/IP still delivers the message, but S-CORE detects that it cannot be trusted and reports the failure through the Fault Library.”

### 2:30 to 3:10 | Corruption versus silence

“We pull the communication link. This time no message arrives. The watchdog reports lost communication. The client distinguishes invalid function input, corrupted communication and complete communication loss.”

### 3:10 to 3:40 | Ecosystem value

“X-Verse provides the scenario. S-CORE establishes trust. Fault Library and DFM-lite preserve ownership and status. OpenSOVD exposes the evidence. The same client can reach a classic ECU through the CDA.”

### 3:40 to 4:00 | Closing

“We created a reusable path from signal to trust, from broken trust to a fault, and from that fault to diagnostic evidence.”

---

## 17. Final Strategic Position

> **Build a Cruise Control diagnostic scenario on OpenSOVD and S-CORE, with E2E protection as the key upstream contribution that distinguishes corrupted communication from invalid function data and total communication loss.**

---

## 18. Definition of Done

- [ ] Maintainer-approved E2E scope
- [ ] Public issue or referenced upstream requirement
- [ ] Reviewable S-CORE pull request
- [ ] One E2E provider or profile slice
- [ ] Configuration and validation
- [ ] Nominal verification test
- [ ] CRC corruption test
- [ ] Counter discontinuity test
- [ ] Communication timeout test
- [ ] F3 reported through Fault Library
- [ ] DFM-lite mapping and snapshot
- [ ] Fault visible through OpenSOVD
- [ ] Stable full-chain demonstration
- [ ] L2 and L1 fallbacks
- [ ] Requirements-to-code-to-test traceability
- [ ] Reproduction instructions
- [ ] Known limitations
- [ ] Community continuation issues
- [ ] Prepared-work declaration

---

## Confidence Level

**Overall strategy confidence: 0.96**

## Key Caveats

- Confirm the E2E implementation gap against the current `inc_someip_gateway` main branch and maintainers.
- Coordinate existing OpenSOVD work with current issue owners.
- F3 requires agreement on ownership, entity mapping and status semantics.
- Do not claim ASIL-B certification.
- openDuT and AutoSD remain stretch goals until the core PR, tests and demo are stable.
