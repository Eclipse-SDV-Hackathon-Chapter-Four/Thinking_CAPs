# Thinking CAPs

> **Open-Source at the Core. Cyber-Physical by Design. AI-Powered. Software-Defined.**

## Contributions

This inventory groups **45 contribution entries** by Eclipse project: upstream
fixes and proposals, dependency assessments, implemented integrations and planned
extensions. It includes the original 42 entries plus the documentation-assistant
pilot, repository code-header cleanup and end-to-end ASPICE evidence. Contribution names link to their records
or upstream proposals.

**PR status checked: 7 October 2026.** There are **11 distinct published upstream
PRs: one merged, six open and four draft**. Local verification describes retained
evidence; upstream acceptance is shown by the PR status. **Not submitted** means
no published team PR was found; **N/A** marks integration, assessment or concept
work without a standalone upstream PR.

Cross-project work appears under its primary project, with partner components
named in the module column. X-Verse, X-COM, CARLA, AAOS, the dashboard and the
software factory are supporting assets or team implementations. Detailed evidence
and remaining review requirements are in the [contribution index](contributions/README.md)
and [registry](contributions/registry.json).

### Eclipse S-CORE

[Eclipse Safe Open Vehicle Core](https://projects.eclipse.org/projects/automotive.score)
includes the Communication, SOME/IP Gateway, Lifecycle and Diagnostics modules.
Communication middleware is also called LoLa or `mw::com`.

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [SOME/IP #84 — service identity and duplicate registration](https://github.com/eclipse-score/inc_someip_gateway/issues/84) | SOME/IP Gateway: SOCom identifiers, registration and discovery | Locally verified; native requirements and maintainer review pending | Not submitted |
| [Lifecycle #704 — shared communication configuration](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/lifecycle/704/README.md) | Launch Manager: daemon/control-client configuration generation | Draft PR | [Lifecycle #762](https://github.com/eclipse-score/lifecycle/pull/762) |
| [Diagnostics #16 — diagnostic resource provider](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/issues/eclipse-score/inc_diagnostics/16/README.md) | `diag_api` / `sovd_adapter`: `DataResource` to OpenSOVD `DataProvider` | Open PR; native review pending | [Diagnostics #40](https://github.com/eclipse-score/inc_diagnostics/pull/40) |
| [Communication #1167 — COM API idempotency tests](contributions/communication-1167/README.md) | LoLa public COM-API integration tests | Open PR; Linux checks retained; native CI/review pending | [Communication #1335](https://github.com/eclipse-score/communication/pull/1335) |
| [Communication #1261 — stream available services](contributions/issues/eclipse-score/communication/1261/README.md) | Rust COM-API LoLa runtime: service discovery and FFI | Linux checks passed; review pending | Not submitted |
| [Communication #250 — typed find-any discovery](contributions/issues/eclipse-score/communication/250/README.md) | Rust COM-API: `FindServiceSpecifier::Any` | Linux checks passed; review pending | Not submitted |
| [Communication #560 — subscription-state handlers](contributions/issues/eclipse-score/communication/560/README.md) | Rust COM-API proxy events and FFI | Linux checks passed; review pending | Not submitted |
| [Communication #781 — method argument ownership](contributions/issues/eclipse-score/communication/781/README.md) | Rust method plumbing: `MethodInArgPtr<T>` | Draft PR; Linux checks passed | [Communication #1339](https://github.com/eclipse-score/communication/pull/1339) |
| [Communication #490 — in-process mock runtime](contributions/issues/eclipse-score/communication/490/README.md) | Rust `com-api-runtime-mock` | Draft PR; Linux checks passed | [Communication #1340](https://github.com/eclipse-score/communication/pull/1340) |
| [Communication #1265 — identifier-pasting dependency](contributions/issues/eclipse-score/communication/1265/engineering-review/score-rust-engineering-review-kohskpez/README.md) | Rust COM-API: `pastey` qualification/adoption | Assessment; native qualification and adoption pending | N/A — assessment |
| [Communication #173 — external crate inventory](contributions/issues/eclipse-score/communication/173/README.md) | Rust COM-API dependency qualification | Assessment; dependency decisions pending | N/A — assessment |
| [Communication #1264 — error-handling dependency](contributions/issues/eclipse-score/communication/1264/README.md) | Rust COM-API: `thiserror` | Assessment; native acceptance pending | N/A — assessment |
| [Communication #1263 — async dependency](contributions/issues/eclipse-score/communication/1263/README.md) | Rust COM-API: `futures` | Assessment; native acceptance pending | N/A — assessment |
| [Communication #794 — Rust test registration](contributions/issues/eclipse-score/communication/794/README.md) | Rust Bazel targets and manual tags | Tracked upstream work; no team patch | N/A — upstream-owned work |
| [Communication #782 — Method API runtime](contributions/issues/eclipse-score/communication/782/README.md) | Rust COM-API method backend | Assessment; another contributor active | N/A — assessment |
| [Communication #1062 — end-to-end protection](contributions/issues/eclipse-score/communication/1062/README.md) | Rust Method/Field API integrity protection | Design assessment; implementation pending | N/A — assessment |
| [Communication #741 — sample/tutorial relocation](contributions/issues/eclipse-score/communication/741/README.md) | Rust COM example application and tutorial | Tracked opportunity; not implemented | Not submitted |
| [Communication #1236 — buildifier enforcement](contributions/issues/eclipse-score/communication/1236/README.md) | Communication Bazel lint tooling and CI | Local fix verified; native CI/review pending | Not submitted |
| [Communication #1031 — assumptions-of-use traceability](contributions/issues/eclipse-score/communication/1031/README.md) | Communication safety analysis; companion Configuration Management provider integration | Public API/provider checks retained; consumer safety decisions pending | Not submitted |
| [Communication #751 — production CodeQL coverage](contributions/issues/eclipse-score/communication/751/README.md) | Communication static-analysis extraction/build pipeline | Current-source analysis retained; broader CI/review pending | Not submitted |
| [Communication #1104 — CodeQL finding locations](contributions/issues/eclipse-score/communication/1104/README.md) | Communication CodeQL query overrides and reporting | Native location fix verified; review pending | Not submitted |
| [Repository code-header cleanup](https://github.com/eclipse-score/communication/pull/1341) | Communication implementation, build helpers, fixtures and generated code | Open PR; code-header checks passed; non-code findings remain | [Communication #1341](https://github.com/eclipse-score/communication/pull/1341) |
| [S-CORE #3115 — AI SDLC tooling evaluation](contributions/issues/eclipse-score/score/3115/README.md) | Infrastructure: AI-tool evaluation and decision records | Open PR; native CI/adoption/review pending | [S-CORE #3307](https://github.com/eclipse-score/score/pull/3307) |
| [S-CORE #2850 — native assurance harness](https://github.com/eclipse-score/docs-as-code/pull/926) | `docs-as-code`: assurance evaluation, native gates and structured traces | Draft PR; integration and qualification review pending | [docs-as-code #926](https://github.com/eclipse-score/docs-as-code/pull/926) |
| [Cruise control, receiver observations and fault injection](docs/reproduction.md) | S-CORE application integration; SOME/IP and Zenoh vehicle-data bridges | Integrated and exercised on the recorded bench | N/A — integration |
| [S-CORE Software Factory](contributions/issues/eclipse-score/score/3115/README.md) | Team engineering automation: development, verification, review and evidence; Hephaestus workflow pilot | Implementation and pilot evidence retained; native adoption pending | Related: [S-CORE #3307](https://github.com/eclipse-score/score/pull/3307), [Hephaestus #14](https://github.com/eclipse-hephaestus/hephaestus/pull/14) |
| [Safety Evaluation Kit](#safety-evaluation-kit) | Safety/dependability workflow: impact, traceability and evidence/review gates | Concept; best-effort extension | N/A — concept |

### Eclipse OpenSOVD

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [CDA #543 — diagnostic loading errors](https://github.com/eclipse-opensovd/classic-diagnostic-adapter/issues/543) | Classic Diagnostic Adapter: `cda-main/src/mdd.rs` | **Merged upstream** | [CDA #601](https://github.com/eclipse-opensovd/classic-diagnostic-adapter/pull/601) |
| [OpenSOVD #156 — FaultProvider prototype](docs/hackathon/FAULT_PROVIDER_DESIGN.md) | Core fault-provider API and `/faults` resources | Legacy prototype; native completion pending | Not submitted |
| [Write-through fault storage](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/compliance/2026-10-07/original/fault-storage-write-through/README.md) | fault-lib: Diagnostic Fault Manager / `SovdFaultStorage` persistence | Locally verified; native review/CI pending | Not submitted |
| [Native receiver diagnosis and fault lifecycle](OpenSOVD/README.md) | App `DataProvider`; fault-lib Reporter, Diagnostic Fault Manager and query APIs | Integrated and exercised; native `/faults` routing remains conditional | N/A — integration |
| [Vehicle Lab dashboard](docs/dashboard.md) | Team Diagnosis and Test Manager UI; OpenSOVD diagnostic APIs and openDuT lifecycle | Implemented and browser-checked | N/A — integration |

The S-CORE Diagnostics adapter above also contributes to the OpenSOVD integration
through [Diagnostics PR #40](https://github.com/eclipse-score/inc_diagnostics/pull/40).

### Eclipse ThreadX

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [ThreadX #744 — stack-address width](contributions/threadx-744/README.md) | Kernel `_tx_thread_create`, stack initialization and MISRA alignment helpers | Fix and regression evidence retained; final review pending | Not submitted |
| [Linux zonal lighting controller](ThreadX/README.md) | GNU/Linux simulation port; threads, queues, timers and event flags; CAN/Zenoh application integration | Implemented and tested | N/A — integration |
| [MXChip AZ3166 lighting ECU](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/ThreadX/az3166/README.md) | Cortex-M4 / STM32F412 board integration; UART/SLCAN lighting firmware | Hardware and live CARLA checks retained | N/A — integration |

### Eclipse OpenBSW

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [Diagnostic transport-router patch](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/contributions/openbsw-transport-router/validation.md) | `libs/bsw/transportRouter`: routing, route observers and statistics | Locally verified; maintainer agreement/review pending | Not submitted |
| [Linux / S32K148EVB zonal gateway](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/OpenBSW/README.md) | DoIP/lwIP, DoCAN/ISO-TP, UDS, `transportRouter`, async and ThreadX board/RTOS binding | Integration checks retained; bus-load failure and qualification gaps remain | N/A — integration |

### Eclipse Zenoh

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [X-Verse / CARLA blueprint and repeatable startup](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/demo/X-Verse/README.md) | Team simulation/startup integration using Zenoh routing, S-CORE, OpenSOVD and openDuT | Drive, disturbance, diagnosis and recovery demonstrated on the recorded host | N/A — integration |
| [X-Verse end-to-end ASPICE evidence](demo/X-Verse/aspice/report/README.md) | Cross-project simulation, S-CORE cruise control, OpenSOVD diagnostics and AAOS OTA verification | Recorded evidence: 11/11 software requirements, 24/24 test cases and traceability | N/A — integration evidence |
| [X-COM Serial2CAN bridge](https://github.com/The-Xverse/zenoh2can_bridge/blob/dev/sdv-hackathon-2026/serial2can-bridge/README.md) | Team SLCAN-to-CAN bridge; Zenoh2CAN and ThreadX ECU transport | Implemented and tested; hardware/live CARLA evidence retained | N/A — integration |

Zenoh also supplies the vehicle-data transport in the S-CORE cruise-control and
ThreadX/AutoSD lighting integrations listed under those projects.

### Eclipse openDuT

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [Two-peer testbench and loss/recovery campaigns](OpenDut/README.md) | CARL coordination, EDGAR peers and CLEO management; team campaign runners | Deployment, disturbance, recovery and cleanup exercised | N/A — integration |

### Eclipse SDV Hephaestus

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [Software-factory workflow pilot, related to #11](contributions/issues/eclipse-hephaestus/hephaestus/11/README.md) | Engineering tooling catalog and workflow documentation | Open proposal; pilot adoption/review pending | [Hephaestus #14](https://github.com/eclipse-hephaestus/hephaestus/pull/14) |
| [S-CORE Docs Assistant pilot, related to #11](https://github.com/eclipse-hephaestus/hephaestus/pull/15) | Documentation tooling catalog; assistant retrieval/provenance pilot | Open proposal; Hephaestus corpus integration/adoption pending | [Hephaestus #15](https://github.com/eclipse-hephaestus/hephaestus/pull/15) |

### Eclipse Automotive Integration for AutoSD

The [Eclipse integration project](https://projects.eclipse.org/projects/automotive.autosd)
uses the AutoSD distribution from the CentOS Automotive SIG. Our work is a team
deployment integration in this ecosystem.

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [AutoSD vehicle-computer VM](AutoSD/README.md) | VM/workload provisioning; ThreadX simulation, Zenoh2CAN, OpenSOVD lighting provider and optional openDuT network | Integrated and exercised; reboot and recovery evidence retained | N/A — integration |

### Jakarta EE

| Contribution | Module / subsystem | Current status | Upstream PR |
| --- | --- | --- | --- |
| [AAOS / OTA backend extension](demo/X-Verse/aspice/report/README.md) | Java EOL backend and RTCU deployment; Jakarta specification/module not yet selected or implemented | OTA implemented and verified; Jakarta adaptation planned | N/A — planned extension |

## Overview

This repository brings together vehicle simulation, S-CORE applications,
OpenSOVD diagnostics, openDuT testing, ECU integrations and upstream contribution
records. Use the guide below to find the part you need; the full PR inventory,
demonstration walkthrough, team plan and working agreements remain in this README.

## Pre-Work: What Existed Before the Event

The team started the hackathon with the following upstream repositories and
existing software assets. These formed our pre-event baseline; they are not
presented as work developed during the event. Event development builds on this
baseline through integrations, features, fixes and verification.

### Standard Upstream Repositories

These are the existing open-source projects used as starting dependencies:

| Project | Pre-event baseline |
| --- | --- |
| CARLA | Default CARLA repository |
| Eclipse S-CORE | Standard project repository |
| Eclipse OpenSOVD | Standard project repository |
| Eclipse openDuT | Standard project repository |
| Eclipse ThreadX | Standard project repository |
| Eclipse OpenBSW | Standard project repository |
| Eclipse Zenoh | Standard project repository |

### Existing Team Assets

The following assets were already developed or available before the event:

| Asset | Pre-event version |
| --- | --- |
| X-Verse Lite | Standard X-Verse Lite version |
| S-CORE Software Factory | First draft release |
| AAOS IVI Application | Existing Android Automotive OS (AAOS) in-vehicle infotainment (IVI) application |
| OTA Manager | Existing C++ implementation |

See [Development Baseline and Event Work](#development-baseline-and-event-work)
for the distinction between the starting baseline and the planned event work.

## Start Here

| Your goal | Where to go |
| --- | --- |
| Identify what was available before the event | [Pre-Work](#pre-work-what-existed-before-the-event) |
| Find a PR, patch or contribution status | [Contributions](#contributions) and [contribution records](contributions/README.md) |
| Understand the folders and find source code | [Repository Structure](#repository-structure) |
| Understand the integrated system | [How the Pieces Fit Together](#how-the-pieces-fit-together) and [architecture documents](docs/architecture/README.md) |
| Drive the vehicle and try instrument-cluster OTA | [Run and Verify the End-to-End Demonstration](#run-and-verify-the-end-to-end-demonstration) |
| Run managed diagnostic and recovery campaigns | [Native reproduction guide](docs/reproduction.md) |
| Use the diagnosis and test-management UI | [Vehicle Lab dashboard guide](docs/dashboard.md) |
| Run a lighting ECU or diagnostic gateway | [ThreadX Linux](ThreadX/README.md), [AZ3166 hardware](ThreadX/az3166/README.md), [AutoSD](AutoSD/README.md) or [OpenBSW](OpenBSW/README.md) |
| Find test commands and understand saved results | [Shared tests](tests/README.md), [Quality Control](#quality-control) and [claim/evidence map](docs/claim-evidence.md) |
| Understand ownership, scope and team agreements | [Team Roster](#team-roster), [Responsibilities](#responsibilities), [Hackathon Scope](#hackathon-scope) and [How We Work](#how-we-work) |

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
| Bruno Campos | Software Engineer | [bruno](https://github.com/campos1796) | S-CORE application; OTA feature; IVI HPC; X-Verse communication layer |
| Yasser | Software Engineer | [yasser](https://github.com/yasser2026-spec)  | OpenSOVD; automated AI code review; solution documentation |
| Puru | Software Engineer | [puru](https://github.com/EP1991)  | OpenSOVD; CDA; diagnostics dashboard |
| Siva | Test Engineer | [siva](https://github.com/siveshvar) | openDuT; OpenSOVD |

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

## How the Pieces Fit Together

The cruise-control integration has a vehicle-control path and a diagnostic path:

```text
X-Verse / CARLA vehicle simulation
              ↕
     Zenoh–SOME/IP bridge
              ↕
 S-CORE cruise-control receiver and application
              │ receiver observations
              ▼
 OpenSOVD diagnostic provider → Vehicle Lab browser UI

openDuT manages the testbench network.
Campaign runners introduce disturbances, check recovery and save evidence.
```

- **X-Verse / CARLA** supplies the simulated vehicle and driving environment.
- **S-CORE** hosts the vehicle application. **Zenoh and SOME/IP** carry messages
  between it and the simulation.
- **OpenSOVD** exposes receiver observations and fault history over HTTP.
- **openDuT** provides the managed network for communication-loss and recovery tests.
- **Vehicle Lab** displays diagnosis, starts project test campaigns and opens saved reports.
- **ThreadX / AutoSD** provides the separate lighting path: vehicle status travels
  through a Zenoh-to-CAN gateway to the ThreadX controller, which returns brake and
  reverse-light decisions. AutoSD hosts the gateway, controller and lighting diagnostics.

The X-Verse supervisor also starts the OTA backend, update controller and Android
Automotive instrument cluster. The [X-Verse report](demo/X-Verse/aspice/report/README.md)
records the update campaigns and end-to-end checks. The separate [OpenBSW gateway](OpenBSW/README.md)
routes diagnostics from Ethernet to CAN-connected ECUs.

The software-factory and engineering-assistant work is documented in the
[contribution records](contributions/README.md), alongside its verification and review evidence.

## Repository Structure

### Component Code and Integrations

| Location | What you will find |
| --- | --- |
| [demo/X-Verse/](demo/X-Verse/README.md) | Main interactive vehicle workspace: launcher, setup, component import manifest, Android cluster/OTA assets and ASPICE requirements, tests and reports. Component sources are imported from their own repositories during setup. |
| [OpenSOVD/](OpenSOVD/README.md) | Native Rust diagnostic providers, fault configuration, upstream patches, build scripts, tests and component evidence. Start with `integration/diagnostics/` for cruise-control diagnosis. |
| [OpenDut/](OpenDut/README.md) | Managed two-peer testbench configuration, lifecycle scripts, receiver/network tests and deployment evidence. The directory is spelled `OpenDut`; the project is openDuT. |
| [ThreadX/](ThreadX/README.md) | C lighting-controller application using the ThreadX Linux simulation port, its CAN contract, build configuration, tests and artifacts. |
| [ThreadX/az3166/](ThreadX/az3166/README.md) | Physical MXChip AZ3166 lighting ECU: firmware, UART/SLCAN transport, board setup, tests and ASPICE work products. |
| [OpenBSW/](OpenBSW/README.md) | DoIP-to-CAN zonal diagnostic gateway for Linux and S32K148EVB, routing configuration, upstream module, tests and evidence. |
| [AutoSD/](AutoSD/README.md) | VM provisioning and workload deployment, service configuration, managed-network support and lighting-integration evidence. |
| [score/](score/README.md) | Earlier S-CORE cruise-control ECU/bridge integration, Docker configuration and build scripts. The native campaign's external S-CORE checkout is selected through its configuration. |
| [integration/dashboard/](integration/dashboard/) | Current Vehicle Lab Python service and browser UI (`web/`). Launch it with `scripts/run_dashboard.py`. |
| [demo/](demo/README.md) and [dashboard/](dashboard/README.md) | Gateway/CDA demonstration stacks, earlier live consoles and replay assets. `demo/X-Verse/` is the main interactive vehicle workspace; `integration/dashboard/` is the current Vehicle Lab service. |

Components generally keep their own `scripts/`, `tests/`, `config/`, `docs/`,
`specs/` and `evidence/` or `artifacts/` directories. Follow each component README
for its prerequisites and commands.

### Shared Tools, Documentation and Records

| Location | What you will find |
| --- | --- |
| [scripts/](scripts/README.md) | Shared audit, reproduction, campaign, dashboard, replay and contribution-verification commands. |
| [tests/](tests/README.md) | Shared Python regression tests, smoke checks and the campaign input example in `campaigns/local.example.json`. |
| [config/](config/) | Dependency audit/pins, upstream observations and the dashboard configuration example. |
| [docs/](docs/README.md) | Architecture, native reproduction, dashboard operation, handover, claim/evidence mapping and hackathon materials. |
| [specs/](specs/) | Shared feature requirements, implementation plans, tasks and acceptance records. Component-specific specifications also live inside components. |
| [contributions/](contributions/README.md) | Upstream issue records, patches, manifests, verification logs, review packets and submission material. `registry.json` is the consolidated issue registry. |
| [evidence/](evidence/) | Retained shared campaign results, logs, manifests, browser checks and recorded replays. Component-specific runs also live under their component. |
| [prework/](prework/README.md) | Preparation research, architecture, setup plans and presentation material. Read it as historical context alongside the dated contribution records. |
| [templates/](templates/) and [misc/](misc/) | Saved-campaign replay template and architecture image assets. |
| [.specify/](.specify/) and [.agents/skills/](.agents/skills/) | Spec Kit workflow configuration, templates and local agent instructions for specification-driven development. |
| [requirements-core.txt](requirements-core.txt) / [requirements-carla.txt](requirements-carla.txt) | Python dependencies for the core tools and optional CARLA integration. |
| [CONTRIBUTING.md](CONTRIBUTING.md), [NOTICE](NOTICE) and [LICENSES/](LICENSES/) | Contribution guidance, repository notice and license texts. |
| [component-layout.json](component-layout.json) | Component relocation map, local upstream checkout references and preserved-artifact hashes. |

### Compatibility Paths and Local Assets

Some root paths are symlinks kept for older scripts and saved manifests:

| Original path | Canonical location |
| --- | --- |
| `integration/diagnostics/` | `OpenSOVD/integration/diagnostics/` |
| `config/faults/` | `OpenSOVD/config/faults/` |
| `config/testbench/` | `OpenDut/config/testbench/` |
| `patches/<component>/` | `OpenSOVD/patches/<component>/` |
| `sovd/` | `OpenSOVD/legacy/` (earlier diagnostic scaffolding) |

Use the canonical component locations for new work. Additional script, test,
specification and evidence mappings are listed in [component-layout.json](component-layout.json).

`.local/`, build/cache directories and component `upstream/` checkouts contain
private state or locally acquired dependencies. They are configured or generated
during setup. The root `upstream/` directory currently contains a reference README;
the checkout does not include a populated set of upstream Git submodules.

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

See the [contribution status table](#contributions) for the diagnostics and
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

## Repository Contribution Guidance and License

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and review expectations.
Repository code is covered by [Apache-2.0](LICENSE); upstream dependencies and
retained third-party artifacts keep their own licenses and notices.

The repository navigation and folder guide were prepared with assistance from
OpenAI Codex.
