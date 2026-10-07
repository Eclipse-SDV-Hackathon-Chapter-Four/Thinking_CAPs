# Thinking CAPs

> **Open-Source at the Core. Cyber-Physical by Design. AI-Powered. Software-Defined.**

Thinking CAPs connects open-source vehicle software, simulation, diagnostics and
automated testing into a software-defined vehicle (SDV) engineering environment.
The main scenario runs cruise control with a simulated vehicle, interrupts its
communication path, observes the application and diagnostic response, and verifies
recovery. The X-Verse demonstration also includes instrument-cluster OTA updates.
A second integration runs a ThreadX lighting controller in an AutoSD virtual
machine, with separate physical ECU and diagnostic-gateway integrations.

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
| Drive the interactive vehicle and try OTA updates | [X-Verse demonstration](#interactive-x-verse-demonstration) and [full walkthrough](docs/hackathon/project-plan.md#run-and-verify-the-end-to-end-demonstration) |
| Build and run managed diagnostic campaigns | [Getting Started](#getting-started), then the [reproduction guide](docs/reproduction.md) |
| Use the browser UI for diagnosis and test campaigns | [Vehicle Lab dashboard guide](docs/dashboard.md) |
| Run a lighting ECU or diagnostic gateway | [ThreadX Linux](ThreadX/README.md), [AZ3166 hardware](ThreadX/az3166/README.md), [AutoSD](AutoSD/README.md) or [OpenBSW](OpenBSW/README.md) |
| Review an upstream fix or its evidence | [Contribution index](contributions/README.md) and [Contribution Status](#contribution-status) |
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

The X-Verse supervisor also starts the OTA backend, update controller and Android
Automotive instrument cluster. The [X-Verse report](demo/X-Verse/aspice/report/README.md)
records the update campaigns and end-to-end checks. The separate [OpenBSW gateway](OpenBSW/README.md)
routes diagnostics from Ethernet to CAN-connected ECUs.

The software-factory and engineering-assistant work is documented in the
[contribution records](contributions/README.md), alongside its verification and review evidence.

## Repository Structure

<a id="new-physical-ecu-integration"></a>

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

## Getting Started

For a first visit, browse the architecture and component READMEs before starting
services. You can inspect the [recorded campaign replay](evidence/f009-recorded-replay-final/index.html)
in a browser without a running vehicle environment.

For execution, use a Linux environment and the prerequisites for your chosen
component. The native core needs Python 3.10+, Docker access, pinned native tools,
source checkouts and container images. CARLA adds simulation/server assets; AutoSD
adds QEMU/KVM. Exact inputs and versions are documented in the
[reproduction guide](docs/reproduction.md) and component READMEs.

### Interactive X-Verse Demonstration

On a suitable Ubuntu x86-64 host with a graphical desktop, NVIDIA GPU for CARLA,
KVM for Cuttlefish and GitHub SSH access to the component repositories, start from
the repository root:

```sh
cd demo/X-Verse
./setup.sh --carla --cuttlefish                 # first installation
python3 run_autoverse.py --enable-camera-display --vcu-zenoh
```

The supervisor starts the vehicle, middleware, S-CORE, OTA services and Android
cluster. Stop it with Ctrl+C. Follow the [full demonstration walkthrough](docs/hackathon/project-plan.md#run-and-verify-the-end-to-end-demonstration)
for prerequisites, cluster APK installation, driving controls, signal-loss injection
and diagnostics. [Recorded ASPICE results](demo/X-Verse/aspice/report/README.md)
can be reviewed without provisioning the environment.

From `demo/X-Verse/`, verify the running environment with:

```sh
python3 aspice/tools/e2e_check.py
python3 aspice/tools/generate_report.py --full
```

### Managed Diagnostic Campaigns and Vehicle Lab

This workflow uses the openDuT-managed testbench and its own application/CARLA
lifecycle. Stop the interactive X-Verse supervisor and any separately started
Zenoh router before running it; the shared router port can otherwise conflict.
See the [X-Verse lifecycle guidance](demo/X-Verse/README.md#start-or-resume-x-verse).
Run the following commands from the repository root.

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

## Contribution Status

The [full contribution inventory](docs/hackathon/project-plan.md#contribution-status)
retains the README's **7 October 2026** review, including implemented integrations,
prepared patches, assessments, upstream PRs and remaining work. For individual
issues, follow the [contribution index](contributions/README.md) and
[registry](contributions/registry.json).

Local implementation and verification, submission, and upstream merging have
separate statuses. Planned items such as the
<a id="safety-evaluation-kit"></a>
[Safety Evaluation Kit](docs/hackathon/project-plan.md#safety-evaluation-kit) and
Jakarta adaptation are identified in the inventory and detailed plan. The X-Verse
OTA demonstration has its own recorded results; older managed-campaign documents
retain their historical AAOS/FOTA deferral.

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

This documentation restructuring was prepared with assistance from OpenAI Codex.
