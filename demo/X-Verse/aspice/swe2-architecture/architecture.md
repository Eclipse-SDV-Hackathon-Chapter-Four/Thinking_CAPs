# Software architecture — X-Verse end-to-end demonstration

The demonstration is a set of cooperating processes and containers on one host, plus the
optional Raspberry Pi. They communicate over three buses: **Zenoh** (vehicle network),
**SOME/IP** (S-CORE ECU) and **HTTPS** (SOVD diagnostics, OTA). The launcher owns the
lifecycle of all of them.

## Views

| View | Diagram |
| --- | --- |
| System context | [context.puml](diagrams/context.puml) |
| Components and deployment | [components.puml](diagrams/components.puml) |
| Lost speed signal → cruise cancel + DTC | [sequence-dtc.puml](diagrams/sequence-dtc.puml) |
| Over-the-air update of the cluster app | [sequence-ota.puml](diagrams/sequence-ota.puml) |

The report embeds the rendered views.

## Software elements

| Element | Implementation | Responsibility | Requirements |
| --- | --- | --- | --- |
| Launcher | `run_autoverse.py` (autoverse) | Start/stop order, Zenoh router, supervision | SWR-01 |
| Virtual vehicle | `bridges/carla/examples/virtual_vehicle.py` (carla-simulator-bridge) | CARLA ego vehicle ↔ Zenoh vehicle state and commands | SWR-02 |
| Manual control | `bridges/carla/examples/vehicle_manual_control.py` | Driver requests, `I`-key speed inhibit | SWR-03 |
| VCU | `vecu/vcu_zenoh` (vcu-zenoh-python) | Throttle/brake, cruise-control engagement | SWR-04 |
| SOME/IP bridge | `bridges/someip/zenoh-someip-bridge`, container `bridge-e2e` | Zenoh ↔ SOME/IP payload conversion | SWR-05 |
| Cruise-control app | `vecu/s-core/cc_s-core/score/cruise_control`, container `docker_setup-adas_score-1` | Cruise control, signal-loss guard, cancel request | SWR-06 |
| Diagnostics server | `cruise-control-diag` on Eclipse inc_diagnostics + PR #16 `sovd_adapter` (`vecu/s-core/third_party`) | DTC `CC.LostCommunication`, SOVD data on `:7691/sovd` | SWR-07 |
| certgen | `vecu/ota/certgen` (otaRTCU), container `ota-certgen` | CA, server and per-target client certificates | SWR-08 |
| OTA backend | `vecu/ota/backend/java`, container `ota-backend` | Operator console/API `:9444`, mTLS device API `:9443`, campaigns | SWR-09 |
| RTCU | `vecu/ota/rtcu`, container `ota-rtcu` | Vehicle OTA agent: poll, verify, adb install, report | SWR-10 |
| Android target | `vecu/aaos_cuttlefish` (Cuttlefish), Raspberry Pi 4 | Runs the cluster app, accepts adb installs | SWR-11 |

## Interfaces

| Interface | Between | Protocol | Detail |
| --- | --- | --- | --- |
| IF-01 Vehicle state | Virtual vehicle → VCU, bridge | Zenoh `tcp/127.0.0.1:7447` | `vehicle/status/*` (speed, clock) |
| IF-02 Driver requests | Manual control → VCU, virtual vehicle | Zenoh | `vehicle/command/*`, `vehicle/control/*` |
| IF-03 VCU commands | VCU → virtual vehicle, bridge | Zenoh | `vcu/control/*` |
| IF-04 ECU signals | SOME/IP bridge ↔ cruise-control app | SOME/IP service 3000 / 4660 | speed in, throttle request and cancel request (event 30603) out |
| IF-05 ADAS outputs | SOME/IP bridge → VCU | Zenoh | `adas/cruise_control/*` |
| IF-06 Diagnostic observations | Cruise-control app → diagnostics server | Unix socket `/tmp/score-xverse/diagnostics.sock` | per-cycle speed-signal observations |
| IF-07 SOVD | Tester → diagnostics server | HTTP `:7691/sovd/v1` | components, data, DTC |
| IF-08 OTA operator | Operator → OTA backend | HTTPS `:9444` | console, artifacts, campaigns, devices |
| IF-09 OTA device | RTCU → OTA backend | HTTPS `:9443`, mutual TLS | register, targets, manifest, artifact, status |
| IF-10 Installation | RTCU → Android targets | adb (private server `:5038`) | `adb install -r` |

## Allocation rationale

- The safety reaction to a lost speed signal stays in the application (SWR-06); the
  diagnostics server only reports it (SWR-07). Both evaluate the same signal contract, so
  the DTC and the reaction agree.
- One RTCU serves all Android targets of the vehicle; targets differ only in their adb
  endpoint. An unreachable target is a reported state, never a hang (SWR-10).
- The launcher treats control-script components (containers, detached services) and
  processes uniformly, so one command starts and stops the whole system (SWR-01).
