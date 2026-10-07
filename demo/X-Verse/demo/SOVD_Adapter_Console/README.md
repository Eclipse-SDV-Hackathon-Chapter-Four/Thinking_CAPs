<!--
  Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
  Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
  Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: adapted to the opensovd-gateway of feature/16-sovd-adapter-dataprovider)
  Goal: How the console works, how to start it against the stand-in or the Rust gateway, its API, settings, checks and known limits.
-->
# Demo Console v2.1 (Zenoh input · PR #40 gateway contract)

> Developed mainly with Claude Fable 5.1 (Anthropic) for the Eclipse SDV Hackathon 2026 · created 2026-10-06 · latest version 2026-10-07.

Live console for the cruise control diagnostics demo. v2.1 adapts the console to the
**opensovd-gateway of PR #40** (inc_diagnostics, branch `feature/16-sovd-adapter-dataprovider`,
head `d388985`): the SOVD side is now that binary, or a faithful Python stand-in of it. Nothing in
the branch was changed; all changes are on the console side.

## What the gateway of PR #40 serves, and how the console uses it

| Data item (component `cruise`, `GET|PUT /sovd/v1/components/cruise/data/{id}`) | Category | Body | Console use |
|---|---|---|---|
| `vehicle_speed` | currentData, read-only | `{"value": 101.3, "unit": "km/h"}` (the gateway's own simulated sensor, `cruise.rs`) | shown in the SOVD block ("gateway sensor"); the big speed on the page is the vehicle's Zenoh value |
| `cruise_state` | currentData, read-only | `{"state": "active|standby|unavailable", "set_speed": 100.0}` | shown with the fault |
| `speed_sensor_fault_status` | currentData, read-only | `{"fault": "VehicleSpeedSensorStuck", "status": "passed|prefailed|failed|prepassed", "test_failed", "confirmed"}` | **F1 (P0500)** as the audience sees it: the gateway's time-based debounce |
| `speed_sensor_stuck` | storedData, **read-write** | `PUT {"data": {"stuck": true|false}}` → 204 | the **bridge**: the console mirrors its own F1 verdict (Zenoh plausibility) into this switch |

The gateway has no faults resource (#156) and no link supervision, so **F2 (U0104, lost
communication)** stays in the console until the Rust diag-host gets a VehicleLink.

```
 virtual vehicle --Zenoh--> [ VehicleLink -> Observer (F1, F2) -> FaultModel ] <--SOVD--> opensovd-gateway (PR #40, :7690)
 "96.4" @ ~20 Hz                              |                       | bridge: PUT speed_sensor_stuck
                                              v                       v
                                       automatic DTC -> ECU simulator :8181 <-- CDA :20002 (read back) <-- console :8080
```

`score_app.py` is a contract double of the Rust binary: same URLs, JSON, debounce (`CRUISE_DEBOUNCE_FAILED_MS`,
`CRUISE_DEBOUNCE_PASSED_MS`), `SCORE_GATEWAY_ADDRESS`, and the same error answers (including the HTTP 500 for a bad
switch body, review finding CR-04). `SOVD_URL` switches the console between them with no other change.

## Quick start (Ubuntu / WSL)

```bash
cd demo-console-zenoh && ./run.sh                 # stand-in + console, http://localhost:8080
./run.sh vehicle                                  # test vehicle (second window) when no real vehicle publishes
GATEWAY_BIN=~/sdv/review/cargo-pr40/target/debug/opensovd-gateway ./run.sh rust   # the real Rust gateway + console
./run.sh docker                                   # gateway + this console + CDA as containers (= ../OpenSOVD/ctl.sh up)
SOVD_URL=http://127.0.0.1:7690 ./run.sh           # console only, against a gateway you started yourself
VEHICLE_HOST=10.169.127.81 ./run.sh               # real vehicle on another laptop (finds its Zenoh ports)
./run.sh check | scenario | scenario-manual | test
```

`run.sh` exports demo debounce values (failed 1500 ms, passed 1000 ms; the Rust defaults are 5000/2000) for the
stand-in and for the binary it starts. Building the Rust binary: `bazel build //score/opensovd-gateway:opensovd-gateway`
in the inc_diagnostics checkout once the Bazel dependency `@opensovd_core//:tracing-subscriber` exists (review finding
CR-13), or a small Cargo workspace over the same sources with opensovd-core at rev `29e806f`, then `cargo build -p opensovd-gateway`.

If a browser tab still shows the v2.0 page, reload it: the old page polls entities that no longer exist.

## Faults

| Fault | Source | Fails when | Qualified by |
|---|---|---|---|
| **P0500** vehicle speed sensor fault | gateway `speed_sensor_fault_status`, fed through the bridge | the console's F1 plausibility verdict (5 implausible samples) sets `speed_sensor_stuck` | the gateway's TimeBased debounce (`failed` after `CRUISE_DEBOUNCE_FAILED_MS`) |
| **U0104** lost communication | console link monitor | no sample for > 500 ms | immediately (timeout) |

Status byte shown (ISO 14229-1, simplified as stated on stage): bit 0 = raw test result; bits 2+3 = qualified
failed, kept as stored until **Reset**. failed = `0x0D`, prepassed = `0x0C`, healed = `0x0C`, never failed = `0x00`.
The automatic classic DTC follows the **qualified** result only: confirmed → ECU DTC `0x2F`, qualified passed → `0x28`.

**Verified live against the real Rust gateway (d388985), real CDA and ECU simulator, 2026-10-07:** 13/13 checks;
lost link: U0104 qualified 584 ms after the vehicle stopped, DTC via CDA 258 ms later; invalid speed: raw failing
after 583 ms, confirmed by the gateway after 2.0 s (1.5 s debounce), DTC 416 ms, `cruise_state` unavailable; heal
1.45 s; gateway switch written directly: confirmed after 1.64 s. 15/15 scenario steps.

## Console API

`/api/config`, `/api/health`, `/api/docker`, `/api/stats`, `/api/vehicle` (link, speed, F1), `/api/sovd` (the four
items as last read, contract probe, bridge state), `/api/faults`, `/api/auto`, `/api/log`, `POST /api/switch`
(test only: write the gateway's switch), `POST /api/reset`, `GET|POST /api/run`, `/proxy/{sovd,cda,sim}/...`.

## Checks and scenarios

13 checks: gateway version-info · CDA token · ECU simulator · Docker · Zenoh connected · samples arriving ·
**SOVD contract (component + four items)** · SOVD reads · F1 chain idle and in sync · F2 armed · console cycles
alive · automatic DTC running · classic round trip. Three scenarios (`./run.sh scenario`): `lost-link`,
`invalid-speed` (via the bridge), `stuck-switch` (direct PUT on the gateway, the write path of #16).

Tests: 57 (`./run.sh test`): observer, stand-in semantics (ported Rust tests) and HTTP contract, fault model and
bridge, automation, discovery, end-to-end without Zenoh (13 checks + three scenarios), real Zenoh pub/sub.

## Files

`config.py` settings · `vehicle_link.py` Zenoh subscriber · `observer.py` F1/F2 monitors · `faults.py` fault model +
bridge · `backends.py` SOVD/CDA/simulator clients · `auto_dtc.py` classic DTC mirror · `server.py` console ·
`runner.py` checks + scenarios · `score_app.py` gateway stand-in · `vehicle_sim.py` test vehicle · `discover.py`
scouting · `classic_fakes.py` offline CDA/simulator · `static/` page · `tests/` · `run.sh`.

## Known limits

- The gateway's `vehicle_speed` is its own simulation, not the Zenoh value: PR #40 has no VehicleLink. The page
  shows both and labels them.
- F2 and the DTC mirror live in the console (tester); they move into the Rust diag-host with the VehicleLink.
- The Bazel build of the branch fails until CR-13 is fixed (see the review folder); the Cargo harness builds it.
- WSL's NAT network drops multicast, so `discover.py` scouts from the Windows side (needs Python on Windows). If the
  vehicle itself runs inside WSL on its laptop, give it a fixed port behind `netsh interface portproxy` and start the
  console with `ZENOH_CONNECT=tcp/<its IP>:7447`. On Windows there is no `docker` command: set `DOCKER_CONTAINERS=" "`.
