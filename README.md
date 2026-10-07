# Thinking CAPs

> **Open-Source at the Core. Cyber-Physical by Design. AI-Powered. Software-Defined.**

## Who We Are

Thinking CAPs is a multidisciplinary automotive software team combining expertise in:

- Software-defined vehicle architecture
- Cyber-physical systems
- Embedded and vehicle software
- Diagnostics and middleware
- Simulation and virtual engineering
- Software automation
- Testing and open-source integration

Our goal is to show how open-source SDV projects, simulation assets, physical platforms, and development automation can be assembled into a representative environment for modern vehicle software engineering.

## Team Roster

| Name | Role | GitHub Handle | Contribution |
|---|---|---|---|
| Jefferson Nascimento | System Architect, AI Engineer | [jnsagai](https://github.com/jnsagai) | System architecture; S-CORE Dark Software Factory; S-CORE chatbot; ThreadX ECU; OpenBSW ECU |
| Bruno Campos | Software Engineer | [bruno](github.com/campos1796) | S-CORE application; OTA feature; IVI HPC; X-Verse communication layer |
| Yasser | Software Engineer | [yasser](https://github.com/yasser2026-spec)  | OpenSOVD; automated AI code review; solution documentation |
| Puru | Software Engineer | [puru](https://github.com/EP1991)  | OpenSOVD; CDA; diagnostics dashboard |
| Siva | Test Engineer | [siva](https://github.com/siveshvar) | openDuT; OpenSOVD |

## Contribution Status

**Last reviewed: 7 October 2026.** This inventory covers upstream issue work,
prepared patches, team integrations, assessments and planned extensions. Local
verification and merging into Thinking CAPs `main` are recorded separately from
acceptance by an upstream Eclipse project. Local results below are retained
measurements, not tests rerun for this README.

The 24 registered issue records, Hephaestus #11, ThreadX #744 and OpenSOVD #156
were checked against GitHub and remain open. Diagnostics #40, CDA #601,
S-CORE #3307 and Hephaestus #14 remain open and unmerged. The table uses the
[consolidated registry](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/registry.json),
linked contribution records and current PR checks. Evidence links point to
the consolidated `main` branch.

| Project / issue | Contribution | Current status and next step | Evidence / PR |
| --- | --- | --- | --- |
| [SOME/IP #84](https://github.com/eclipse-score/inc_someip_gateway/issues/84) | Reject duplicate SOCom servers across minor versions | **Locally verified.** Scoped fix and earlier owner review retained; amended contribution review and native submission pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/inc_someip_gateway/84/README.md) |
| [Lifecycle #704](https://github.com/eclipse-score/lifecycle/issues/704) | Generate three communication configurations from shared definitions | **Locally verified.** 113 native tests passed; native PR, CI and maintainer review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/lifecycle/704/README.md) |
| [Diagnostics #16](https://github.com/eclipse-score/inc_diagnostics/issues/16) | Expose diagnostic API resources through an OpenSOVD provider | **Submitted.** PR #40 open; documentation/license checks pass; ECA fails; native validation and review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/inc_diagnostics/16/README.md); [PR #40](https://github.com/eclipse-score/inc_diagnostics/pull/40) |
| [CDA #543](https://github.com/eclipse-opensovd/classic-diagnostic-adapter/issues/543) | Return `Result` instead of `Option` for diagnostic loading errors | **Submitted.** PR #601 open; ECA fails; maintainer review and verification of the published revision pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-opensovd/classic-diagnostic-adapter/543/README.md); [PR #601](https://github.com/eclipse-opensovd/classic-diagnostic-adapter/pull/601) |
| [Communication #1265](https://github.com/eclipse-score/communication/issues/1265) | Assess the Rust COM identifier-pasting dependency | **Assessment.** Six Linux integration cases passed; retaining locked `pastey` 0.2.3 recommended; qualification and human acceptance pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1265/engineering-review/score-rust-engineering-review-kohskpez/README.md) |
| [Communication #1167](https://github.com/eclipse-score/communication/issues/1167) | Add COM API idempotency integration tests | **Locally verified.** 503 tests passed, six skipped; inherited copyright findings retained; native PR and human acceptance pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/communication-1167/README.md) |
| [Communication #1261](https://github.com/eclipse-score/communication/issues/1261) | Stream newly available services with `find_all_services()` | **Linux checks passed.** Proposed fix retained; human review, broader CI and native PR pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1261/README.md) |
| [Communication #250](https://github.com/eclipse-score/communication/issues/250) | Support typed `FindServiceSpecifier::Any` discovery | **Linux checks passed.** Proposed fix retained; human review, broader CI and native PR pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/250/README.md) |
| [Communication #560](https://github.com/eclipse-score/communication/issues/560) | Expose event subscription state and change handlers | **Linux checks passed.** Proposed fix retained; human review, broader CI and native PR pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/560/README.md) |
| [Communication #781](https://github.com/eclipse-score/communication/issues/781) | Implement Rust `MethodInArgPtr<T>` plumbing | **Draft.** Partially verified; implementation completion and native verification pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/781/README.md) |
| [Communication #490](https://github.com/eclipse-score/communication/issues/490) | Provide an in-process Rust COM mock runtime | **Draft.** Unverified; native testing and review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/490/README.md) |
| [Communication #173](https://github.com/eclipse-score/communication/issues/173) | Assess external crates used by the COM API | **Assessment only.** No source change proposed; dependency disposition and human review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/173/README.md) |
| [Communication #1264](https://github.com/eclipse-score/communication/issues/1264) | Assess `thiserror` usage | **Assessment only.** No source change proposed; human review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1264/README.md) |
| [Communication #1263](https://github.com/eclipse-score/communication/issues/1263) | Assess `futures` usage | **Assessment only.** No source change proposed; human review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1263/README.md) |
| [Communication #794](https://github.com/eclipse-score/communication/issues/794) | Remove manual tags from Rust test targets | **Tracked opportunity.** Being handled upstream; no team patch retained. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/794/README.md) |
| [Communication #782](https://github.com/eclipse-score/communication/issues/782) | Assess Rust Method API runtime implementation | **Assessment only.** Another contributor is active; no team implementation retained. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/782/README.md) |
| [Communication #1062](https://github.com/eclipse-score/communication/issues/1062) | Assess end-to-end protection for Rust Method/Field APIs | **Design assessment.** Implementation and native verification pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1062/README.md) |
| [Communication #741](https://github.com/eclipse-score/communication/issues/741) | Move the Rust sample application into the tutorial | **Not implemented.** Tracked opportunity only. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/741/README.md) |
| [S-CORE tooling #3115](https://github.com/eclipse-score/score/issues/3115) | Evaluate AI SDLC / SpecKit using software-factory pilot evidence | **Draft PR.** PR #3307 open; ECA passes; inherited local documentation failure retained; comparative pilots, CI and acceptance pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/score/3115/README.md); [PR #3307](https://github.com/eclipse-score/score/pull/3307) |
| [S-CORE assistant #2850](https://github.com/eclipse-score/score/issues/2850) | Propose chatbot retrieval and provenance for the docs-as-code harness | **Proposal.** Source and deterministic evidence retained; native harness adapter and maintainer agreement pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/score/2850/README.md) |
| [Communication #1236](https://github.com/eclipse-score/communication/issues/1236) | Enforce buildifier consistently in CI | **Draft / blocked.** 27 baseline-identical lint findings remain; cleanup and review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1236/README.md) |
| [Communication #1031](https://github.com/eclipse-score/communication/issues/1031) | Improve assumptions-of-use visibility and traceability | **Draft.** Scoped checks retained; production configuration/FMEA integration and review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1031/README.md) |
| [Communication #751](https://github.com/eclipse-score/communication/issues/751) | Include production sources in CodeQL analysis | **Draft.** 502 tests passed, six skipped; copyright, full CodeQL analysis, QNX and coverage gaps remain. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/751/README.md) |
| [Communication #1104](https://github.com/eclipse-score/communication/issues/1104) | Restore locations for CodeQL findings | **Root cause reproduced.** Draft normalizer hides placeholders; restoring actual locations and native review remain pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/communication/1104/README.md) |
| [Hephaestus #11](https://github.com/eclipse-hephaestus/hephaestus/issues/11) | Propose a software-factory engineering workflow pilot | **Submitted proposal.** PR #14 open; local Hugo/Sphinx builds and ECA pass; pilot adoption and review pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-hephaestus/hephaestus/11/README.md); [PR #14](https://github.com/eclipse-hephaestus/hephaestus/pull/14) |
| [ThreadX #744](https://github.com/eclipse-threadx/threadx/issues/744) | Preserve stack pointer width under MISRA and stack checking | **In progress (last recorded).** Exploratory reproduction and retry evidence retained; native verification, human review and upstream PR pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/threadx-744/README.md) |
| [OpenSOVD #156](https://github.com/eclipse-opensovd/opensovd-core/issues/156) | Develop a FaultProvider prototype for the faults resource | **Legacy prototype.** Local HTTP/provider implementation retained; native upstream faults support and full vehicle integration remain pending. | [Design](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/docs/hackathon/FAULT_PROVIDER_DESIGN.md) |
| OpenBSW | Prepare the `transportRouter` upstream module | **Locally verified / unpublished.** 46 unit tests and two Bazel tests passed; maintainer issue agreement, human review and full CI pending. | [Validation](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/openbsw-transport-router/validation.md) |
| OpenSOVD fault-lib | Add explicit write-through fault storage | **Locally verified / unpublished.** Process-restart regression evidence retained; human reproduction/review and native CI pending. | [Record](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/compliance/2026-10-07/original/fault-storage-write-through/README.md) |
| X-Verse / CARLA | Integrate the cyber-physical vehicle blueprint and repeatable startup | **Implemented on the recorded host.** Drive, disturbance, diagnosis, recovery and verification demonstrated; fresh-machine/operator reproduction remains separate. | [Setup and scope](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/demo/X-Verse/README.md) |
| X-Verse end-to-end ASPICE evidence | Show that the full demonstration (CARLA, VCU, SOME/IP bridge, S-CORE ECU with DTC over SOVD via PR #16, OTA with certgen, EOL backend and RTCU) complies with ASPICE SWE.1–SWE.6 | **11/11 software requirements verified, 24/24 test cases pass, no traceability gaps.** Requirements, PlantUML architecture, detailed design, unit suites (launcher, SOME/IP, S-CORE cruise control, PR #16 `sovd_adapter`, OTA backend), 13 integration checks against the running system and qualification scenarios. | [Report](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/demo/X-Verse/aspice/report/README.md) · [HTML](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/demo/X-Verse/aspice/report/aspice-swe-report.html) · [Work products](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/demo/X-Verse/aspice/README.md) |
| S-CORE / Zenoh / SOME/IP | Connect cruise control, receiver observations and fault injection | **Integrated and exercised.** Real receiver traffic and return actuation captured; fault monitoring and recovery use the managed campaign. | [Campaign evidence](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/docs/reproduction.md) |
| OpenSOVD | Expose native receiver diagnosis and fault lifecycle | **Integrated and exercised.** App data resources, reporter/DFM, process restart and recovery retained; native `/faults` routing remains conditional. | [Integration](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/OpenSOVD/README.md) |
| openDuT | Manage a two-peer testbench and communication-loss/recovery campaigns | **Integrated and exercised.** Matched 0.10.2 deployment, disturbance, recovery and owned cleanup evidence retained. | [Testbench](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/OpenDut/README.md) |
| Vehicle Lab dashboard | Provide Diagnosis and Test Manager with evidence replay | **Implemented and browser-checked.** Native diagnosis, run admission, cancellation, recovery and artifact-integrity checks retained. | [UI and checks](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/docs/dashboard.md) |
| ThreadX / Linux | Implement the zonal brake/reverse lighting controller | **Implemented and tested.** Actual ThreadX GNU simulation port, CAN protocol and CARLA lighting integration exercised. | [Controller](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/ThreadX/README.md) |
| ThreadX / MXChip AZ3166 | Deploy the zonal lighting ECU on physical hardware | **Hardware and live CARLA checks retained.** UART/SLCAN transport, LEDs/OLED and SWE.1–SWE.6 work products available. | [Board and evidence](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/ThreadX/az3166/README.md) |
| AutoSD | Run ThreadX lighting, Zenoh2CAN and native OpenSOVD in a vehicle-computer VM | **Integrated and exercised.** QEMU/KVM guest, managed openDuT path, disturbance/recovery and reboot evidence retained. | [Measured evidence](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/AutoSD/artifacts/README.md) |
| X-COM / Serial2CAN | Connect serial-attached ECUs to the X-Verse CAN bus | **Implemented and tested.** Multiple ports, filtering, reconnect and bounded queues; AZ3166 hardware/live CARLA evidence retained. | [Bridge](https://github.com/The-Xverse/zenoh2can_bridge/blob/dev/sdv-hackathon-2026/serial2can-bridge/README.md) |
| OpenBSW / ThreadX | Implement a DoIP-to-CAN zonal gateway on Linux and S32K148EVB | **Integration tests passed.** 28 host and 10 board tests; ASPICE report retains a bus-load failure and remaining qualification gaps. | [Gateway and report](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/OpenBSW/README.md) |
| S-CORE Software Factory | Provide automated development, verification, review and evidence workflows | **Implementation and pilot evidence retained.** Eclipse tooling evaluation and Hephaestus proposals submitted; native adoption remains pending. | [Pilot](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/score/3115/README.md) |
| AAOS / OTA / Jakarta | Extend the existing IVI and update assets | **OTA implemented and verified; Jakarta planned.** Java EOL backend and RTCU deliver the cluster APK over mutual TLS to Cuttlefish and a Raspberry Pi 4; successful campaigns on both targets and a cleanly failed campaign for an unreachable target are recorded. Jakarta adaptation remains planned. | [ASPICE evidence](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/demo/X-Verse/aspice/report/README.md) |
| Safety Evaluation Kit | Propose safety-impact, evidence and approval gates for the factory | **Concept.** Implementation remains part of the best-effort extension scope. | [Scope](#safety-evaluation-kit) |

## Run and Verify the End-to-End Demonstration

The end-to-end demonstration is the X-Verse vehicle simulation in [`demo/X-Verse`](demo/X-Verse):
CARLA and the virtual vehicle → Zenoh VCU → Zenoh–SOME/IP bridge → Eclipse S-CORE
cruise-control ECU, which detects a lost vehicle-speed signal, cancels cruise control and
reports DTC `CC.LostCommunication` over SOVD (Eclipse inc_diagnostics PR #16
`sovd_adapter`) → OTA vECU (certgen, EOL backend, RTCU) updating the instrument cluster
on Android Automotive (Cuttlefish, optionally a Raspberry Pi 4). One command starts and
stops everything.

### Verify Without Running It

The [ASPICE SWE.1–SWE.6 report](demo/X-Verse/aspice/report/README.md) contains the
requirements, the architecture (PlantUML), the unit, integration and qualification
results and the traceability matrix, with every result recorded in the report itself:
11/11 software requirements verified, 24/24 test cases pass, no traceability gaps.
This needs no access to the X-Verse component repositories.

### Where the End-to-End Tests Reside

| What | Location (after step 2) | Run with |
| --- | --- | --- |
| ASPICE package: requirements, architecture, design, test specifications, report | [`demo/X-Verse/aspice/`](demo/X-Verse/aspice/README.md) | `python3 aspice/tools/generate_report.py --full` |
| End-to-end integration checks (13, read-only, against the running system) | [`demo/X-Verse/aspice/tools/e2e_check.py`](demo/X-Verse/aspice/tools/e2e_check.py) | `python3 aspice/tools/e2e_check.py` |
| Recorded results of the last run | [`demo/X-Verse/aspice/report/evidence/`](demo/X-Verse/aspice/report/evidence) | — |
| Launcher tests | [`demo/X-Verse/tests/`](demo/X-Verse/tests) | `python3 -m unittest tests.test_run_autoverse` |
| S-CORE cruise control and signal-loss guard (gtest) | `demo/X-Verse/vecu/s-core/cc_s-core/score/cruise_control/tests/` | Bazel in the S-CORE devcontainer (run by `--full`) |
| PR #16 `sovd_adapter` | `demo/X-Verse/vecu/s-core/third_party/inc_diagnostics` | Bazel in the S-CORE devcontainer (run by `--full`) |
| SOME/IP payload conversion | `demo/X-Verse/bridges/someip/zenoh-someip-bridge/tests/` | `build/test_convert` |
| OTA backend (JUnit) and live OTA cycle | `demo/X-Verse/vecu/ota/backend/java/src/test/`, `demo/X-Verse/vecu/ota/e2e/` | Maven container (run by `--full`) |

### Step by Step: Clone, Run and Verify

**Prerequisites.** Ubuntu 22.04 on x86-64 with a graphical desktop, an NVIDIA GPU for
CARLA, virtualization enabled in the BIOS/UEFI (`/dev/kvm`, for Android Cuttlefish),
internet access, plenty of free disk space (CARLA, Android images and container builds),
and a GitHub SSH key with read access to the The-Xverse repositories: the components are
imported from there.

1. **Clone.**

   ```bash
   git clone git@github.com:Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs.git
   cd Thinking_CAPs/demo/X-Verse
   ```

2. **Set up** (one time; it takes a while). Installs the host tools and Docker, checks
   KVM, imports every component with `vcs import` (each from its X-Verse repository,
   branch `dev/sdv-hackathon-2026`), builds S-CORE with its diagnostics server and the
   SOME/IP bridge, and installs CARLA and Cuttlefish. Add `--threadx` when an MXChip AZ3166
   board is used.

   ```bash
   ./setup.sh --carla --cuttlefish
   ```

3. **Start the demonstration.**

   ```bash
   python3 run_autoverse.py --enable-camera-display --vcu-zenoh
   ```

   It starts a Zenoh router if none is running, CARLA, the VCU, the SOME/IP bridge,
   S-CORE, the OTA stack, Vehicle Manual Control, the virtual vehicle and Cuttlefish. The
   EOL console opens at `https://localhost:9444`; Android is at `https://localhost:8443`
   (self-signed certificates: accept the warning).

4. **Install the cluster app over the air** (one time). In the EOL console, upload
   `aaos_digital_cluster/cuttlefish_emulator/apk/digital-cluster-app-debug.apk` with a
   version and **Push update** to `PC-CUTTLEFISH-01`; the campaign shows
   `downloading → installing → success`. Open the cluster app from Android's app menu.

5. **Drive.** Focus the **Vehicle Manual Control** window: `W` accelerate, `S` brake,
   `A`/`D` steer, `C` cruise control (from 10 km/h), `Z`/`X` set speed, `Q` reverse.

6. **Lose the speed signal and diagnose it.** With cruise control engaged, press `I`:
   after about 1.1 s S-CORE cancels cruise control and the VCU disengages. Read the DTC
   over SOVD:

   ```bash
   curl -s http://127.0.0.1:7691/sovd/v1/components/cruise_control/data/cc_lost_communication
   ```

   Press `I` again to restore the signal.

7. **Verify the end-to-end chain** while the system runs:

   ```bash
   python3 aspice/tools/e2e_check.py                # 13 integration checks, expect "13/13 passed"
   python3 aspice/tools/generate_report.py --full   # all suites + report in aspice/report/
   ```

8. **Stop** with **Ctrl+C** in the terminal of step 3; every component it started is
   stopped.

Optional hardware, detailed troubleshooting and every launcher option are described in the
[X-Verse README](demo/X-Verse/README.md): the Raspberry Pi 4 as second OTA target (step
10) and the ThreadX AZ3166 lighting ECU (step 12).

## Responsibilities

Roles are assigned by work package, but the team maintains collective responsibility for integration and demonstration readiness.

### Solution Architecture and Coordination

**Owner:** Jefferson

- Maintain the end-to-end system architecture and demonstration sequence.
- Coordinate work packages and integration decisions.
- Ensure alignment between X-Verse, S-CORE, SOME/IP, OpenSOVD, and optional Eclipse projects.
- Maintain the product storyline and final presentation.
- Control scope and prioritize the minimum viable demonstration.

### OpenSOVD and Diagnostic Integration

**Owner:** Purushotham

- Implement and validate the diagnostic integration path.
- Develop or refine the Rust-based adapter and diagnostic providers.
- Integrate the fault-injection mechanism with the vehicle-control path.
- Document the OpenSOVD environment and startup procedure.
- Support contribution packaging and upstream issue alignment.

### S-CORE Application and X-Verse Adaptation

**Owner:** Bruno

- Maintain the S-CORE cruise-control application.
- Implement vehicle-speed fault behaviour and DTC logic.
- Integrate the application with the SOME/IP gateway.
- Verify that invalid speed information causes cruise control to transition to a safe disabled state.
- Support end-to-end communication and application testing.

### Dashboard and Demonstration Experience

**Owner:** Yasser

- Provide a simple audience-facing dashboard.
- Expose cruise-control status, selected vehicle data, and diagnostic state.
- Provide fault-injection controls where feasible.
- Support architecture documentation and presentation material.
- Ensure the technical flow is understandable during the demonstration.
- Boardbring activity support and test via openDuT MXCHIP HW

### Deployment and Test Orchestration

**Owner:** Sivakumar

- Investigate and integrate openDUT where feasible.
- Support repeatable deployment and test execution.
- Define a virtual or simulated device-under-test path if physical hardware is unavailable.
- Maintain a fallback test-runner or CI-based scenario.
- Support environment bring-up and demonstration recovery.

## Challenge Alignment

### Selected Challenge

**Freestyle Track: Integration and Feature Development**

### Hackathon Objective

Leverage and integrate open-source SDV projects to address complex challenges in modern vehicle software development.

Our solution aligns with the challenge through four complementary dimensions:

1. **Integration:** Connect multiple Eclipse SDV projects, Capgemini Engineering open-source assets, simulation environments, and physical or virtual ECUs.
2. **Automation:** Apply an automated software factory and local engineering assistant to real S-CORE development tasks.
3. **Contribution:** Investigate open issues, implement improvements, and deliver fixes at a contribution-ready level.
4. **Extension:** Introduce reusable capabilities that can add value to the existing Eclipse SDV ecosystem.

The team selected the Freestyle Track with an integration and feature-development focus during the preparation phase.

## Hackathon Scope

### First Priority: Core Scope

#### Cyber-Physical SDV Blueprint

Create a representative cyber-physical blueprint integrating:

- Eclipse SDV projects
- X-Verse simulation assets
- Virtual ECUs
- Physical ECUs where feasible
- Vehicle communication middleware
- Diagnostics
- Deployment and test orchestration
- User interfaces and dashboards

The blueprint will provide an integrated environment for developing, running, diagnosing, and validating software-defined vehicle functions.

The primary demonstration will use a fault-aware cruise-control scenario in which:

1. X-Verse executes a virtual driving scenario.
2. An S-CORE application controls the cruise-control function. With the sovd_adapter feature implementation, we bridge the S-CORE diagnostic framework and the OpenSOVD gateway, enabling standardized vehicle diagnostics over REST/HTTP.
3. A controlled fault is introduced into the vehicle-speed path.
4. The application detects the invalid signal.
5. Cruise control transitions to a safe disabled state.
6. The diagnostic state is exposed through OpenSOVD.
7. The fault and application state are displayed to the user.
8. Test and deployment assets validate the scenario.

This extends the previously agreed S-CORE, OpenSOVD, X-Verse, and fault-injection demonstration.

See the [contribution status table](#contribution-status) for the diagnostics and
CDA issue records, current upstream pull requests and remaining review gates.

#### Dark Software Factory and Local Engineering Assistant

Advance automotive software development automation through two complementary capabilities.

##### S-CORE Software Factory

Use a dark factory, multi-agent development workflow to address selected small-to-medium-complexity S-CORE issues.

The workflow will cover:
- Issue and requirement analysis
- Implementation planning
- Code generation or modification
- Build execution
- Deterministic testing
- Static and security analysis where applicable
- Repair loops
- Evidence collection
- Traceability
- Human review and approval

##### S-CORE Local Bot Assistant

Use a local engineering assistant to:
- Navigate S-CORE documentation
- Locate relevant architectural information
- Support repository exploration
- Accelerate issue investigation
- Provide traceable responses based on available project documentation

Generated code must pass deterministic checks and human review.

#### Open-Source Contributions

Navigate open issues and bugs in Eclipse SDV repositories to accomplish the following.

##### A. Identify Contribution Opportunities

Select features, bugs, or integration gaps that Thinking CAPs can address during the event.

Selection criteria:

- Relevance to the blueprint
- Achievable scope
- Value to the Eclipse community
- Technical feasibility
- Testability
- Potential for upstream acceptance

##### B. Introduce Value-Adding Assets

Assess how the following assets could extend the Eclipse SDV ecosystem:

- X-Verse
- S-CORE Software Factory
- S-CORE documentation bot
- OTA Manager
- Simulation integration wrappers
- Communication bridges

##### C. Deliver Contribution-Ready Improvements

Target the highest practical maturity level within the event:

- Clearly defined problem
- Maintainable implementation
- Buildable code
- Documented design
- Automated or reproducible tests
- Reviewed changes
- Respected licensing and contribution requirements
- Pull request or patch prepared for upstream review

“Ready to merge” is the quality ambition. Actual merging remains subject to the respective project maintainers and governance processes.

### Second Priority: Best-Effort Extensions

Once the integrated baseline is stable, the team may extend the blueprint with the following capabilities.

#### New Physical ECU Integration

Introduce a physical or representative zonal ECU based on:

- Eclipse ThreadX
- Eclipse OpenBSW

Associated X-Verse wrappers and communication bridges will connect the device to the wider blueprint.

#### Jakarta-Based OTA Backend

Adapt the Java-based OTA backend to the Jakarta framework and connect it to the OTA Manager workflow.

#### Safety Evaluation Kit

Propose a Safety Evaluation Kit for the S-CORE Software Factory, focused on:

- Structured safety-impact assessment
- Evidence collection
- Validation gates
- Traceability
- Human approval
- Explicit identification of limitations

This will be presented as an engineering concept or demonstrator, not as formal functional-safety certification.

#### AutoSD Deployment

Deploy selected blueprint components in an AutoSD environment. Initial candidates include:

- OpenSOVD services
- Diagnostic adapters
- Integration services
- Dashboard backend
- Deployment and test utilities

AutoSD will remain an extension until the core demonstration is stable.

## Core Solution Idea

### Solution Title

**Thinking CAPs Open SDV Blueprint**

**A cyber-physical environment for development, diagnostics, automation, and shift-left validation**

### Problem Statement

Modern vehicle software development involves multiple projects, middleware technologies, virtual environments, physical devices, and specialized engineering tools.

Even when individual components work independently, teams still face difficulties with:

- Cross-project interoperability
- Reproducible environments
- Early testing without physical hardware
- Application-to-diagnostics integration
- Deployment across virtual and physical targets
- Efficient navigation of large repositories
- Converting open issues into tested contributions
- Maintaining quality when AI-assisted development is applied

### Proposed Solution

Thinking CAPs will assemble a reusable cyber-physical blueprint that connects open-source SDV technologies with X-Verse and engineering automation.

![Thinking CAPs EE architecture](misc/ee-architecture.png)

```text
Simulation and Scenario Execution
              |
           X-Verse
              |
   Communication and Wrappers
   Zenoh | SOME/IP | Serial2CAN
              |
      Vehicle Software Layer
       S-CORE | ThreadX
              |
 Application and Fault Management
       Cruise Control | DTC
              |
   Software-Oriented Diagnostics
           OpenSOVD
              |
 Deployment and Test Orchestration
        openDUT | AutoSD
              |
 Dashboard | Bot | Software Factory
```

This is the target architecture for the plan. Individual extensions will only be added after the core integration flow is stable.

### Main Demonstration Story

#### Phase 1: Develop and Run

- X-Verse runs a virtual vehicle.
- S-CORE hosts the cruise-control application.
- Zenoh and SOME/IP connect the simulated vehicle and application environment.
- The dashboard displays relevant vehicle and application states.

#### Phase 2: Inject and Detect a Fault

- X-Verse or a dedicated injector introduces a vehicle-speed fault.
- The S-CORE application detects missing or invalid speed information.
- Cruise control transitions to a safe disabled state.
- The diagnostic logic qualifies and records the fault.

#### Phase 3: Diagnose

- OpenSOVD exposes the diagnostic state.
- The dashboard or diagnostic client retrieves the fault.
- The user sees the relationship between the injected condition, application response, and diagnostic result.

#### Phase 4: Validate

- openDUT or an equivalent automated path executes the scenario.
- Test evidence confirms the expected behaviour.
- Logs and results are stored with the solution artifacts.

#### Phase 5: Improve

- The Software Factory addresses a selected S-CORE issue.
- The local bot assists with documentation and repository navigation.
- Human reviewers verify all proposed changes.
- Contribution-ready artifacts are prepared.

## Projects and Assets Involved

### Eclipse and Open-Source Projects

#### Core Projects

- Eclipse S-CORE
- Eclipse OpenSOVD
- Eclipse openDUT
- Eclipse Zenoh
- Eclipse ThreadX
- Eclipse OpenBSW
- Eclipse AutoSD
- Jakarta

#### Extension Projects and Technologies

- Java
- CARLA
- Android Automotive OS

A project will only be claimed as part of the implemented solution when it is meaningfully used through code, configuration, deployment, integration, testing, or demonstration.

### Capgemini Engineering Assets

- X-Verse
- S-CORE Software Factory
- S-CORE documentation bot
- Fabro Dashboard
- OTA Manager
- X-Verse integration wrappers
- X-COM communication bridges
- AAOS Instrument Cluster Application

The plan distinguishes between:

- Assets available before the event
- Assets modified during the event
- Newly created integrations
- Upstream Eclipse contributions
- Best-effort experimental extensions

## Development Baseline and Event Work

### Pre-Work Baseline

The following technologies and developments form the starting baseline:

- Standard CARLA repository
- Standard Eclipse SDV project repositories
- S-CORE
- OpenSOVD
- openDUT
- ThreadX
- OpenBSW
- Zenoh
- X-Verse Lite baseline
- First draft of the S-CORE Software Factory
- AAOS IVI application
- C++ OTA Manager
- Existing cruise-control integration
- Initial architecture and setup documentation

Pre-existing work will be identified transparently and will not be presented as development completed during the event.

### Event Development

#### Core Blueprint

- Integrate Eclipse SDV projects with X-Verse.
- Stabilize the cyber-physical blueprint.
- Document the architecture and deployment.
- Establish reproducible startup and test procedures.

#### Simulation and Fault Injection

- Implement or improve X-Verse fault injection.
- Connect the injector to the S-CORE application.
- Validate safe cruise-control deactivation.
- Expose the resulting diagnostic state through OpenSOVD.

#### Software Automation

- Enhance the S-CORE Software Factory.
- Apply it to selected S-CORE issues.
- Collect proven-in-use evidence.
- Demonstrate deterministic validation and human review.
- Improve the local S-CORE documentation bot.

#### Physical and Virtual Device Representation

- Integrate a ThreadX-based zonal-computer representation.
- Add OpenBSW as a best-effort physical ECU representation.
- Connect virtual or physical devices to the blueprint.

#### X-Verse Integrations

- Create or enhance simulation wrappers.
- Implement the X-COM Serial2CAN bridge.
- Connect new components without destabilizing the baseline.

#### OTA Extension

- Explore a Java implementation of the OTA Manager.
- Adapt the backend to Jakarta as a best-effort extension.

#### Open-Source Contributions

- Investigate open issues.
- Implement selected fixes or features.
- Add tests and documentation.
- Conduct peer review.
- Prepare issues, patches, or pull requests for maintainers.

## How We Work

### Lightweight Development Process

The team will use an integration-first, evidence-driven process.

#### Workstreams

1. Blueprint architecture and interfaces
2. S-CORE applications and diagnostics
3. OpenSOVD integration
4. X-Verse simulation and communication
5. Software Factory and bot
6. Device and hardware integration
7. Deployment, testing, and contributions

```text
Select
  ↓
Specify
  ↓
Design
  ↓
Implement
  ↓
Build
  ↓
Test
  ↓
Review
  ↓
Integrate
  ↓
Demonstrate
  ↓
Document
```

Each work item must have:

- A named owner
- Declared input and expected output
- Acceptance criteria
- Dependencies
- Evidence of testing
- Current status
- Integration target

### Progress Tracking

The team will use a lightweight board with:

- Backlog
- Selected
- In Progress
- In Review
- Integration
- Blocked
- Done

Prioritization will consider:

- Contribution value
- Blueprint relevance
- Implementation effort
- Integration risk
- Demonstration impact
- Available evidence
- Dependency on external maintainers or hardware

The shared GitHub repository will be the source of truth for code, architecture, documentation, scripts, testing evidence, and integration status.

## Quality Control

### Quality Principles

The team will prioritize:

1. Working integration over isolated feature quantity.
2. Reproducibility over machine-specific success.
3. Deterministic verification over unverified AI output.
4. Reviewable contributions over experimental patches.
5. Clear evidence over unsupported claims.
6. A stable baseline over uncontrolled scope expansion.

### Testing Strategy

#### Component Tests

Each component must be independently executable or testable.

#### Interface Tests

Connected components must be validated using controlled messages, mocks, or reference examples.

#### Integration Tests

The complete chain must be tested from simulated input to application response and diagnostic output.

#### Regression Tests

The known-good baseline must be rerun after critical integration changes.

#### Demonstration Tests

The team must verify that the complete scenario can be reproduced using the documented setup and startup sequence.

#### Contribution Tests

Proposed upstream changes should include, where applicable:

- Successful compilation
- Automated tests
- Static checks
- Interface validation
- Regression evidence
- Documentation
- Known limitations

### Code Review

- Critical changes require review by at least one additional team member.
- Interface changes require review from both affected workstreams.
- AI-generated or AI-modified code requires explicit human review.
- Experimental changes remain separate from the stable demonstration baseline.
- Upstream fixes should follow the target project’s contribution conventions.

### Document and Configuration Management

The repository will contain:

- Solution plan
- Architecture diagrams
- Root README
- Component-level setup instructions
- Test instructions
- Evidence
- Known limitations
- Contribution records
- Third-party and licensing information where applicable

Dependencies and working configurations should be pinned where practical. A known-good baseline will be clearly identified and protected.

## Team Communication

### Communication Channels

- Slack and Teams for immediate coordination
- GitHub issues for technical tasks and blockers
- Pull requests for review and integration
- Repository documentation for stable information
- A lightweight decision log for architectural choices

### Checkpoints

Each checkpoint will answer:

1. What is working?
2. What changed?
3. What is blocked?
4. Has the baseline been affected?
5. What evidence was produced?
6. What is the next highest-value task?
7. Should any best-effort item be stopped?

### Blocker Reporting

A blocker report must state:

- Affected component
- Observed behaviour
- Available evidence
- Affected dependency
- Help required
- Fallback option
- Scope impact

## Decision Making

### Decision Principles

Decisions will be made in the following order:

1. Protect the working blueprint.
2. Preserve safe application behaviour.
3. Maintain reproducibility.
4. Maximize ecosystem and contribution value.
5. Add optional technologies only when they provide demonstrable value.

### Resolving Design Disagreements

When alternatives compete:

1. Describe the options.
2. Identify architectural and interface impacts.
3. Compare integration risk.
4. Use a small technical experiment where practical.
5. Prefer the simplest option that satisfies the objective.
6. Record the decision and rationale.
7. Escalate unresolved scope decisions to the team lead.

### Time-Boxing and Fallback

If an item threatens the core solution:

1. Preserve the last known-good version.
2. Isolate the experiment.
3. Use the simpler fallback path.
4. Record the limitation.
5. Continue the end-to-end integration.
6. Return to the item only after the baseline is stable.

## Scope Priorities

### Must Have

- Cyber-physical blueprint architecture
- X-Verse virtual vehicle
- S-CORE cruise-control application
- Zenoh and SOME/IP communication
- Controlled fault injection
- Safe cruise-control deactivation
- OpenSOVD diagnostic visibility
- Lightweight dashboard or client
- Reproducible setup
- Test evidence
- Architecture and interface documentation

### Should Have

- Enhanced S-CORE Software Factory
- Proven-in-use automation evidence
- S-CORE documentation bot
- openDUT test execution
- X-Verse simulation wrappers
- Selected Eclipse issue fixes
- Contribution-ready patches or pull requests

### Could Have

- ThreadX zonal-computer representation
- Serial2CAN X-COM bridge
- AutoSD deployment
- OpenBSW physical ECU integration
- Jakarta-based OTA backend
- Safety Evaluation Kit concept

### Out of Core Scope

The following items must not block the core demonstration:

- Formal safety certification
- Production-ready OTA deployment
- Complete physical vehicle integration
- Integration of every listed Eclipse project
- Upstream acceptance or merging during the event
- Production maturity of the complete blueprint

## Definition of Success

The hackathon will be successful if Thinking CAPs can demonstrate:

- A functional cyber-physical SDV blueprint
- Meaningful integration of multiple Eclipse SDV projects
- A virtual vehicle running an S-CORE function
- Controlled fault injection
- Safe application behaviour
- Diagnostic visibility through OpenSOVD
- Repeatable deployment and validation
- Practical use of the Software Factory on a real issue
- Useful results from the local documentation bot
- Documented architecture and interfaces
- Tested, reviewed, and contribution-ready improvements
- Transparent separation between pre-existing work and event development
