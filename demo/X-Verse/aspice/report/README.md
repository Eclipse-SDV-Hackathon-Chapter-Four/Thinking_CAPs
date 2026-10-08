# ASPICE SWE.1–SWE.6 report — X-Verse end-to-end demonstration

Generated 2026-10-08 01:11:06 by `aspice/tools/generate_report.py` (the same data as [aspice-swe-report.html](aspice-swe-report.html) and [summary.json](summary.json)).

CARLA · virtual vehicle · Zenoh VCU · SOME/IP bridge · S-CORE ECU with DTC `CC.LostCommunication` over SOVD (inc_diagnostics PR #16 `sovd_adapter`) · OTA vECU (certgen, EOL backend, RTCU) · Android targets.

## Summary

| Software requirements verified | Test cases passed | Unit test cases / checks | Traceability issues |
| --- | --- | --- | --- |
| **14/15** | **29/30** | **400** | **0** |

Demonstration work products for code quality and traceability; not an assessed capability level. Work products: [requirements](../swe1-requirements/), [architecture](../swe2-architecture/architecture.md), [detailed design](../swe3-detailed-design/detailed-design.md), [unit](../swe4-unit-verification/unit-verification.md), [integration](../swe5-integration-test/integration-test.md) and [qualification](../swe6-qualification-test/qualification-test.md) test specifications.

## SWE.2 Architecture

![components](../swe2-architecture/diagrams/components.svg)

![context](../swe2-architecture/diagrams/context.svg)

![sequence-dtc](../swe2-architecture/diagrams/sequence-dtc.svg)

![sequence-ota](../swe2-architecture/diagrams/sequence-ota.svg)

## SWE.1 Software requirements

| ID | Requirement | Derived from | Allocated to | Status |
| --- | --- | --- | --- | --- |
| SWR-01 | The launcher shall start the components in dependency order, start a Zenoh router when none answers on `127.0.0.1:7447`, supervise processes and containers, and stop everything it started on Ctrl+C. | SYS-05 | Launcher | ✅ VERIFIED |
| SWR-02 | The virtual vehicle shall publish the vehicle state (speed, clock) on Zenoh and apply the VCU throttle, brake and steering commands to the CARLA ego vehicle. | SYS-01 | Virtual vehicle | ✅ VERIFIED |
| SWR-03 | Vehicle Manual Control shall publish the driver requests (pedals, steering, cruise control, reverse), toggle a vehicle-speed publish inhibit with the `I` key, and accept the same key presses on its scripted input channel (`test/manual_control/input`) for automated tests. | SYS-01, SYS-03 | Manual control | ✅ VERIFIED |
| SWR-04 | The VCU shall compute throttle and brake commands, engage cruise control only at 10 km/h or more, and disengage it on braking and on the ADAS cancel request. | SYS-01, SYS-03 | VCU | ✅ VERIFIED |
| SWR-05 | The Zenoh–SOME/IP bridge shall convert payloads between Zenoh keys and SOME/IP events according to its mapping, including the cruise-control cancel request (event 30603). | SYS-02, SYS-03 | SOME/IP bridge | ✅ VERIFIED |
| SWR-06 | The S-CORE cruise-control application shall compute the throttle request and, when no speed sample was accepted for the signal budget plus the failed debounce, cancel cruise control and send the cancel request until the VCU reports disengaged. | SYS-02, SYS-03 | Cruise-control app | ✅ VERIFIED |
| SWR-07 | The cruise-control diagnostics server shall qualify DTC `CC.LostCommunication` with the same signal contract and debounce, and serve it with the vehicle speed and cruise state over SOVD through the PR #16 `sovd_adapter`. | SYS-03 | Diagnostics server | ✅ VERIFIED |
| SWR-08 | certgen shall create a CA, a server certificate and one client certificate per vehicle target, with the target id as common name. | SYS-04 | certgen | ✅ VERIFIED |
| SWR-09 | The OTA backend shall offer the operator console and API, accept device connections only with a client certificate from its CA, store artifacts with their SHA-256 and track campaigns with per-target status. | SYS-04 | OTA backend | ✅ VERIFIED |
| SWR-10 | The RTCU shall register the vehicle, probe every configured target, poll for campaigns, verify the artifact digest, install it with adb and report each phase; a campaign for an unreachable target shall end as failed instead of hanging. | SYS-04 | RTCU | ✅ VERIFIED |
| SWR-11 | The Android target shall boot, accept adb installs from the RTCU and run the cluster application. | SYS-04 | Android target | ✅ VERIFIED |
| SWR-12 | The OpenSOVD gateway shall serve component `cruise` with `vehicle_speed`, `cruise_state`, `speed_sensor_fault_status` (time-based debounce) and the read-write injection switch `speed_sensor_stuck` over SOVD on `:7690`. | SYS-06 | OpenSOVD gateway | ✅ VERIFIED |
| SWR-13 | The SOVD Adapter Console shall subscribe to the vehicle speed on Zenoh, qualify P0500 (implausible speed, mirrored into the gateway's switch) and U0104 (no sample for more than 500 ms), and mirror each confirmed and healed fault as a classic DTC in the ECU simulator, read back through the CDA. | SYS-06 | SOVD Adapter Console | ✅ VERIFIED |
| SWR-14 | The classic diagnostic path shall serve the ECU simulator's DTCs over the CDA's SOVD API (UDS over DoIP behind it). | SYS-06 | CDA + ECU simulator | ✅ VERIFIED |
| SWR-15 | The ThreadX lighting ECU shall receive the VCU brake and reverse status as CAN frame `0x1F1` through the Zenoh2CAN bridge and answer with the light commands in `0x1F4`, published as `vehicle/lights/*_cmd`. | SYS-07 | ThreadX lighting ECU | ⚠️ PARTIAL |

## SWE.4 Unit verification

| ID | Test | Verifies | Result | Detail |
| --- | --- | --- | --- | --- |
| UT-LAUNCHER | `tests/test_run_autoverse.py` (Python unittest) | SWR-01 | ✅ PASS | OK — 15 cases |
| UT-SOMEIP | `tests/payload/test_convert.cpp` (`test_convert`) | SWR-05 | ✅ PASS | checks=213 failures=0 (build/test_convert) — 213 cases |
| UT-SCORE | `score/cruise_control/tests/cruise_control_test.cpp` (gtest) | SWR-06 | ✅ PASS | bazel test //score/cruise_control/...: 1 target(s), 15 test cases — Executed 1 out of 1 test: 1 test passes. — 15 cases |
| UT-PR16 | `//score/mw/diag/sovd_adapter:all` (inc_diagnostics, PR #16) | SWR-07 | ✅ PASS | bazel test //score/mw/diag/sovd_adapter:all: 1 target(s), 27 test cases — Executed 1 out of 1 test: 1 test passes. — 27 cases |
| UT-OTA | `backend/java/src/test` (JUnit 5, Spring Boot) | SWR-09 | ✅ PASS | 12 JUnit suites (mvn test) — 70 cases |
| UT-CONSOLE | `external_hackathon_ecus/SOVD_Adapter_Console/tests` (Python unittest: observer, gateway stand-in semantics, fault model and bridge, automatic DTC, discovery, end-to-end without Zenoh, real Zenoh pub/sub) | SWR-13 | ✅ PASS | OK (skipped=1) — 57 cases |
| UT-THREADX | `external_hackathon_ecus/ThreadX/tests` (C: lighting protocol, SLCAN codec and edge cases) | SWR-15 | ✅ PASS | ctest in the image build stage: 100% tests passed, 0 tests failed out of 3 — 3 cases |

## SWE.5 Integration test

`tools/e2e_check.py` against the running system — run now (2026-10-08T01:11:30+0100)

| ID | Test | Verifies | Result | Detail |
| --- | --- | --- | --- | --- |
| ITC-01 | Zenoh router reachable | SWR-01 | ✅ PASS | tcp/127.0.0.1:7447 accepts connections |
| ITC-02 | Supervised containers running | SWR-01 | ✅ PASS | all running |
| ITC-03 | Vehicle state and driver requests on Zenoh | SWR-02, SWR-03 | ✅ PASS | received 3/3 |
| ITC-04 | VCU commands on Zenoh | SWR-04 | ✅ PASS | received 2/2 |
| ITC-05 | Speed reaches the S-CORE ECU over SOME/IP | SWR-05, SWR-07 | ✅ PASS | vehicle_speed 0.0 km/h, age 43 ms |
| ITC-06 | Cruise-control state exposed | SWR-06 | ✅ PASS | state standby, identity sha256:ae275d890718… |
| ITC-07 | DTC served through PR #16 `sovd_adapter` | SWR-07 | ✅ PASS | components ['cruise_control'], DTC CC.LostCommunication status passed |
| ITC-08 | certgen PKI | SWR-08 | ✅ PASS | verified against ca.crt: server.crt, client-PC-CUTTLEFISH-01.crt, client-PI-ANDROID-15.crt |
| ITC-09 | Device API requires mutual TLS | SWR-09 | ✅ PASS | without client cert: rejected; with client cert: HTTP/1.1 400 Bad Request |
| ITC-10 | RTCU registered and targets reported | SWR-09, SWR-10 | ✅ PASS | PC-CUTTLEFISH-01 reachable, PI-ANDROID-15 unreachable; last seen 9 s ago |
| ITC-11 | Campaign outcomes recorded per target | SWR-10 | ✅ PASS | success: PC-CUTTLEFISH-01 #23, PI-ANDROID-15 #19; unreachable target closed as failed: #8 |
| ITC-12 | CARLA ego vehicle present | SWR-02 | ✅ PASS | ego_vehicle vehicle.audi.etron (id 24) |
| ITC-13 | Android target ready with the cluster app | SWR-11 | ✅ PASS | boot_completed=1, cluster app installed |
| ITC-14 | OpenSOVD gateway (PR #40) serves the cruise component | SWR-12 | ✅ PASS | component cruise with vehicle_speed (currentData), cruise_state (currentData), speed_sensor_fault_status (currentData), speed_sensor_stuck (storedData); VehicleSpeedSensorStuck passed |
| ITC-15 | SOVD Adapter Console checks | SWR-12, SWR-13, SWR-14 | ✅ PASS | 13/13 passed |
| ITC-16 | ThreadX zonal lighting ECU on the AZ3166 board | SWR-15 | NOT RUN | AZ3166 board not connected |

## SWE.6 Qualification test

| ID | Test | Verifies | Result | Detail |
| --- | --- | --- | --- | --- |
| QTC-01 | One-command start and stop | SWR-01 | ✅ PASS | 2 supervised run(s) reached 'Supervisor is now running', 2 completed shutdown (~/.cache/autoverse-runner) |
| QTC-02 | Drive and cruise control | SWR-02, SWR-03, SWR-04 | ✅ PASS | vehicle network live, scripted input channel answers, cruise control off; ego placed on spawn point 80 of Town10HD_Opt (178 m straight lane); W held: 0.1 → 18.3 km/h in 1.3 s; C: VCU engaged after 0.05 s; S-CORE active, set speed 14.8 km/h; cruise control keeps the vehicle moving at 11.6..14.4 km/h for 8 s (set 14.8) without pedal; S: cruise control disengaged after 0.05 s, vehicle stopped (recorded 2026-10-08T01:10:39+0100) |
| QTC-03 | Lost speed signal | SWR-03, SWR-04, SWR-05, SWR-06, SWR-07 | ✅ PASS | vehicle network live, scripted input channel answers, cruise control off; ego placed on spawn point 80 of Town10HD_Opt (178 m straight lane); W held: 0.0 → 18.6 km/h in 1.4 s; C: VCU engaged after 0.05 s; S-CORE active, set speed 15.4 km/h; I: vehicle speed no longer published; DTC CC.LostCommunication failed (confirmed) 1.22 s after I; cancel request sent, VCU disengaged 1.22 s after I, S-CORE standby; I again: speed restored, DTC passed 0.22 s later; S: cruise control disengaged after 0.00 s, vehicle stopped (recorded 2026-10-08T01:10:39+0100) |
| QTC-04 | OTA update of the Cuttlefish cluster | SWR-09, SWR-10, SWR-11 | ✅ PASS | campaign #23 v5.3: downloading → installing → success |
| QTC-05 | OTA update of the Raspberry Pi | SWR-10 | ✅ PASS | campaign #19 v1.4: downloading → installing → success |
| QTC-06 | OTA to an unreachable target | SWR-10 | ✅ PASS | campaign #8 closed failed: target unreachable at RTCU probe (adb 192.168.1.72:5555) |
| QTC-07 | Lost speed signal seen by the OpenSOVD vECU | SWR-13, SWR-14 | ✅ PASS | vehicle network live, scripted input channel answers, cruise control off; console fault memory reset; I: console U0104 (lost communication) qualified 0.62 s after I; ECU DTC 01E242 reads 0x2F via CDA (23 ms); I again: U0104 healed after 0.51 s, ECU DTC 01E242 reads 0x28 (recorded 2026-10-08T01:10:39+0100) |

## Bidirectional traceability

| Requirement | Unit | Integration | Qualification | Status |
| --- | --- | --- | --- | --- |
| SWR-01 | UT-LAUNCHER | ITC-01 ITC-02 | QTC-01 | ✅ VERIFIED |
| SWR-02 | — | ITC-03 ITC-12 | QTC-02 | ✅ VERIFIED |
| SWR-03 | — | ITC-03 | QTC-02 QTC-03 | ✅ VERIFIED |
| SWR-04 | — | ITC-04 | QTC-02 QTC-03 | ✅ VERIFIED |
| SWR-05 | UT-SOMEIP | ITC-05 | QTC-03 | ✅ VERIFIED |
| SWR-06 | UT-SCORE | ITC-06 | QTC-03 | ✅ VERIFIED |
| SWR-07 | UT-PR16 | ITC-05 ITC-07 | QTC-03 | ✅ VERIFIED |
| SWR-08 | — | ITC-08 | — | ✅ VERIFIED |
| SWR-09 | UT-OTA | ITC-09 ITC-10 | QTC-04 | ✅ VERIFIED |
| SWR-10 | — | ITC-10 ITC-11 | QTC-04 QTC-05 QTC-06 | ✅ VERIFIED |
| SWR-11 | — | ITC-13 | QTC-04 | ✅ VERIFIED |
| SWR-12 | — | ITC-14 ITC-15 | — | ✅ VERIFIED |
| SWR-13 | UT-CONSOLE | ITC-15 | QTC-07 | ✅ VERIFIED |
| SWR-14 | — | ITC-15 | QTC-07 | ✅ VERIFIED |
| SWR-15 | UT-THREADX | ITC-16 | — | ⚠️ PARTIAL |

## Provenance

| Repository | Branch | Commit |
| --- | --- | --- |
| autoverse | dev/sdv-hackathon-2026 | ef19057 SOVD Adapter Console README: run it from its new folder (local changes) |
| bridges/carla | dev/sdv-hackathon-2026 | 69d0574 Find the X-Verse checkout from AUTOVERSE_ROOT in automate.py (local changes) |
| bridges/someip | dev/sdv-hackathon-2026 | 3db6b78 Map S-CORE cruise-control cancel request to Zenoh |
| bridges/can | dev/sdv-hackathon-2026 | 33b52ca Point serial2can-bridge docs at its new location; list both bridges |
| vecu/s-core | dev/sdv-hackathon-2026 | fcd0319 Keep the ECU container's bazel outputs reachable after root builds |
| vecu/vcu_zenoh | dev/sdv-hackathon-2026 | c15aea2 Disengage cruise control on the ADAS cancel request |
| vecu/ota | dev/sdv-hackathon-2026 | d90e6d5 Follow the Cuttlefish vECU to vecu/aaos_cuttlefish |
| vecu/aaos_cuttlefish | dev/sdv-hackathon-2026 | bd0af0c PRE-WORK: deliver the X-Verse APK through OTA; pin display DPI |

Regenerate with the system running: `python3 aspice/tools/generate_report.py --full`.
