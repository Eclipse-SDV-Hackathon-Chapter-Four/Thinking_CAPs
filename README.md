# Thinking CAPs

> **Open-Source at the Core. Cyber-Physical by Design. AI-Powered. Software-Defined.**

## Contributions

This inventory groups **44 contribution entries** by Eclipse project: upstream
fixes and proposals, dependency assessments, implemented integrations and planned
extensions. It includes the original 42 entries plus the documentation-assistant
pilot and repository code-header cleanup. Contribution names link to their records
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
| [SOME/IP #84 — service identity and duplicate registration](contributions/remediation/someip-84-requirements/README.md) | SOME/IP Gateway: SOCom identifiers, registration and discovery | Locally verified; native requirements and maintainer review pending | Not submitted |
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
| [Repository code-header cleanup](contributions/communication-1167/repository-license-headers/README.md) | Communication implementation, build helpers, fixtures and generated code | Open PR; code-header checks passed; non-code findings remain | [Communication #1341](https://github.com/eclipse-score/communication/pull/1341) |
| [S-CORE #3115 — AI SDLC tooling evaluation](contributions/issues/eclipse-score/score/3115/README.md) | Infrastructure: AI-tool evaluation and decision records | Open PR; native CI/adoption/review pending | [S-CORE #3307](https://github.com/eclipse-score/score/pull/3307) |
| [S-CORE #2850 — native assurance harness](https://github.com/eclipse-score/docs-as-code/pull/926) | `docs-as-code`: assurance evaluation, native gates and structured traces | Draft PR; integration and qualification review pending | [docs-as-code #926](https://github.com/eclipse-score/docs-as-code/pull/926) |
| [Cruise control, receiver observations and fault injection](docs/reproduction.md) | S-CORE application integration; SOME/IP and Zenoh vehicle-data bridges | Integrated and exercised on the recorded bench | N/A — integration |
| [S-CORE Software Factory](contributions/issues/eclipse-score/score/3115/README.md) | Team engineering automation: development, verification, review and evidence; Hephaestus workflow pilot | Implementation and pilot evidence retained; native adoption pending | Related: [S-CORE #3307](https://github.com/eclipse-score/score/pull/3307), [Hephaestus #14](https://github.com/eclipse-hephaestus/hephaestus/pull/14) |
| [Safety Evaluation Kit](docs/hackathon/project-plan.md#safety-evaluation-kit) | Safety/dependability workflow: impact, traceability and evidence/review gates | Concept; best-effort extension | N/A — concept |

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
| [X-COM Serial2CAN bridge](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/X-Verse/bridges/serial2can/README.md) | Team SLCAN-to-CAN bridge; Zenoh2CAN and ThreadX ECU transport | Implemented and tested; hardware/live CARLA evidence retained | N/A — integration |

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
| [AAOS / OTA backend extension](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/blob/main/demo/X-Verse/aaos_digital_cluster/OTA_PROPOSAL.md) | Planned Java OTA backend adaptation; no Jakarta specification/module selected or implemented | Existing baseline available; Jakarta adaptation and end-to-end update verification deferred | N/A — planned extension |

## Overview

Thinking CAPs connects open-source vehicle software, simulation, diagnostics and
automated testing into a software-defined vehicle (SDV) engineering environment.
The main scenario runs cruise control with a simulated vehicle, interrupts its
communication path, observes the application and diagnostic response, and verifies
recovery. A second integration runs a ThreadX lighting controller in an AutoSD
virtual machine.

This repository contains integration code, configuration, test runners,
documentation and retained evidence. It also holds patches and review records for
contributions to upstream Eclipse projects. The full vehicle environment uses
additional source checkouts, container images and simulation assets configured
separately.

## Start Here

Choose the path that matches what you want to do:

| Your goal | Read first |
| --- | --- |
| Understand the system | [How the Pieces Fit Together](#how-the-pieces-fit-together), then the [architecture documents](docs/architecture/README.md) |
| Find code, configuration or tests | [Repository Structure](#repository-structure) |
| Build and run the native cruise-control scenario | [Getting Started](#getting-started), then the [reproduction guide](docs/reproduction.md) |
| Use the browser UI for diagnosis and test campaigns | [Vehicle Lab dashboard guide](docs/dashboard.md) |
| Run the lighting controller or AutoSD VM | [ThreadX guide](ThreadX/README.md) or [AutoSD guide](AutoSD/README.md) |
| Review an upstream fix or its evidence | [Contributions](#contributions) and the [contribution index](contributions/README.md) |
| Understand the team, scope and event plan | [Team](#team) and the [detailed project plan](docs/hackathon/project-plan.md) |

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

The software-factory and engineering-assistant work is documented in the
[contribution records](contributions/README.md), alongside its verification and review evidence.

## Repository Structure

### Component Code and Integrations

| Location | What you will find |
| --- | --- |
| [OpenSOVD/](OpenSOVD/README.md) | Native Rust diagnostic providers, fault configuration, upstream patches, build scripts, tests and component evidence. Start with `integration/diagnostics/` for cruise-control diagnosis. |
| [OpenDut/](OpenDut/README.md) | Managed two-peer testbench configuration, lifecycle scripts, receiver/network tests and deployment evidence. The directory is spelled `OpenDut`; the project is openDuT. |
| [ThreadX/](ThreadX/README.md) | C lighting-controller application using the ThreadX Linux simulation port, its CAN contract, build configuration, tests and artifacts. |
| [AutoSD/](AutoSD/README.md) | VM provisioning and workload deployment, service configuration, managed-network support and lighting-integration evidence. |
| [score/](score/README.md) | Earlier S-CORE cruise-control ECU/bridge integration, Docker configuration and build scripts. The native campaign's external S-CORE checkout is selected through its configuration. |
| [integration/dashboard/](integration/dashboard/) | Current Vehicle Lab Python service and browser UI (`web/`). Launch it with `scripts/run_dashboard.py`. |
| [demo/](demo/README.md) and [dashboard/](dashboard/README.md) | Earlier gateway/CDA demonstration stacks, live consoles and replay assets. For the current Vehicle Lab service, use `docs/dashboard.md`. |
| [X-Verse/](X-Verse/) | Retained Serial2CAN hardware and live-vehicle run artifacts. The full X-Verse simulation is an external dependency. |

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
Local working directories such as `OpenBSW/` may also exist without their source
being tracked here; see the [recorded integration inventory](#contributions)
for that work's scope and evidence.

## Getting Started

For a first visit, browse the architecture and component READMEs before starting
services. You can inspect the [recorded campaign replay](evidence/f009-recorded-replay-final/index.html)
in a browser without a running vehicle environment.

For execution, use a Linux environment and the prerequisites for your chosen
component. The native core needs Python 3.10+, Docker access, pinned native tools,
source checkouts and container images. CARLA adds simulation/server assets; AutoSD
adds QEMU/KVM. Exact inputs and versions are documented in the
[reproduction guide](docs/reproduction.md) and component READMEs.

Run commands below from the repository root.

1. **Prepare Python dependencies** in a local virtual environment:

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements-core.txt
   ```

   For CARLA campaigns, install `requirements-carla.txt` in that environment as well.

2. **Prepare the native environment** using [docs/reproduction.md](docs/reproduction.md).
   It covers acquiring the pinned assets, preparing and deploying openDuT, copying
   `tests/campaigns/local.example.json` to `.local/campaign.json`, and updating paths,
   image IDs and tools for your machine. Several example image IDs refer to assets
   built on the reference host; a new clone needs those assets built or acquired.

3. **Select a campaign** once the configured bench and binaries are ready:

   ```sh
   .venv/bin/python scripts/run_campaign.py --config .local/campaign.json --scenario core --output evidence/my-core
   ```

   `core` uses fixture vehicle inputs with real native receiver, network and fault
   processing. `carla` uses the actual simulator. Use a new output directory for
   every run. The reproduction guide includes clean-source builds, other scenarios
   and teardown instructions.

4. **Start Vehicle Lab** if you want diagnosis and test management in a browser:

   ```sh
   cp config/dashboard/local.example.json .local/dashboard.json
   # Update paths, bench state and native inputs for your environment first.
   .venv/bin/python scripts/run_dashboard.py --config .local/dashboard.json --port 8791
   ```

   Open <http://127.0.0.1:8791>. The [dashboard guide](docs/dashboard.md) explains
   configuration, bench deployment, diagnosis availability and campaign controls.

## Testing and Evidence

Use [tests/README.md](tests/README.md) for the shared test suite and component
READMEs for native build, Rust, controller and integration checks. After installing
the selected dependencies, run the shared Python regressions with:

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Campaign output includes results, manifests, logs and summaries. The
[claim/evidence map](docs/claim-evidence.md) explains what each recorded check
establishes. Saved reports describe historical runs; live diagnosis comes from
the running provider. Independent new-machine reproduction remains a separate
acceptance step in the [reproduction guide](docs/reproduction.md).

To check retained contribution files against their recorded hashes:

```sh
python3 scripts/verify_contributions.py
```

This checks artifact integrity. Native test results, human review and upstream
acceptance are recorded separately in each contribution packet.

## Team

| Name | Role | GitHub | Main areas |
| --- | --- | --- | --- |
| Jefferson Nascimento | System Architect, AI Engineer | [jnsagai](https://github.com/jnsagai) | Architecture, S-CORE Software Factory and assistant, ThreadX and OpenBSW ECUs |
| Bruno Campos | Software Engineer | [campos1796](https://github.com/campos1796) | S-CORE application, OTA, IVI and X-Verse communication |
| Yasser | Software Engineer | [yasser2026-spec](https://github.com/yasser2026-spec) | OpenSOVD, automated review and documentation |
| Puru | Software Engineer | [EP1991](https://github.com/EP1991) | OpenSOVD, Classic Diagnostic Adapter and diagnostics dashboard |
| Siva | Test Engineer | [siveshvar](https://github.com/siveshvar) | openDuT and OpenSOVD |

The [detailed project plan](docs/hackathon/project-plan.md) preserves work-package
responsibilities, challenge alignment, scope priorities, demonstration phases,
quality expectations and team working agreements.

## License

Repository code is covered by [Apache-2.0](LICENSE). Upstream dependencies and
retained third-party artifacts keep their own licenses and notices.
