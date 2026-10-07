# Detailed design — X-Verse end-to-end demonstration

Design of the elements in the [architecture](../swe2-architecture/architecture.md), at the
level needed to understand and test the end-to-end behaviour. Component internals are
documented in their own repositories (OTA vECU README and ASPICE package, S-CORE
`cruise_control/docs`, `third_party/cruise_diag`, SOME/IP bridge README).

## Launcher (SWR-01)

| Unit | Design |
| --- | --- |
| `build_steps()` | Ordered step list: Zenoh router (only when `127.0.0.1:7447` does not answer, or our container is running), CARLA server, ThreadX (board present), VCU, SOME/IP bridge, S-CORE, OTA, manual control, CARLA client, Cuttlefish. Paths are relative to `AUTOVERSE_ROOT` (the launcher's directory). |
| Step types | *process* (supervised child), *containers* (control script start, then container state checked periodically), *detached* (control script start; stopped with its `stp` command). |
| Shutdown | Ctrl+C / SIGTERM: children terminated, then every control step's `stp` in reverse order, then CARLA cleanup. |

## Vehicle network (SWR-02 – SWR-04)

| Key | Producer | Consumer | Payload |
| --- | --- | --- | --- |
| `vehicle/status/velocity_status` | Virtual vehicle | VCU, SOME/IP bridge, cluster | km/h, text float |
| `vehicle/status/clock_status` | Virtual vehicle | SOME/IP bridge | s, text float |
| `vehicle/command/brake_pedal_sts`, `acc_pedal_sts`, `steer_sts` | Manual control | VCU, virtual vehicle | 0..1, text float |
| `vehicle/control/cc_engage_req`, `reverse_req` | Manual control | VCU | `1` / `0` |
| `vehicle/control/speed_publish_inhibit` | Manual control (`I`) | Virtual vehicle | `True` / `False` |
| `vcu/control/throttle_cmd`, `brake_cmd` | VCU | Virtual vehicle | 0..1 |
| `vcu/control/cc_engage_sts`, `brake_sts`, `reverse_sts` | VCU | Bridge, cluster, lighting | `true` / `false`, on change |
| `adas/cruise_control/cancel_req` | Bridge (from S-CORE) | VCU | `true` / `false` |

VCU rules: cruise control engages at ≥ 10 km/h in forward gear; braking (pedal above
threshold) or `cancel_req = true` disengages it.

## Cruise-control ECU (SWR-06, SWR-07)

| Unit | Design |
| --- | --- |
| `SignalLossGuard` | Evaluated every 50 ms cycle. Lost = no accepted `ego_velocity_sts` sample for `CRUISE_SIGNAL_BUDGET_MS` (1000) + `CRUISE_DEBOUNCE_FAILED_MS` (100). Cruise active when lost: disengage, stop `adas_cc_target_speed_sts` and `adas_throttle_req`, send `adas_cc_cancel_req = true` each cycle until `vcu_cc_engage_sts` reports disengaged. |
| Diagnostic publisher | Non-blocking per-cycle observation over `SCORE_DIAGNOSTIC_SOCKET`. |
| `cruise-control-diag` | Debounces observations (`CRUISE_DEBOUNCE_PASSED_MS` 150, startup grace 2000 ms), qualifies `CC.LostCommunication`, serves `diag_api` data resources through PR #16 `sovd_adapter` on `SCORE_GATEWAY_ADDRESS` (`0.0.0.0:7691`). |
| SOVD data | `/sovd/v1/components/cruise_control/data/{vehicle_speed, cruise_state, cc_lost_communication, cc_fault_injection}`; DTC payload `{fault, status: passed/failed, test_failed, confirmed}`. |

## OTA vECU (SWR-08 – SWR-11)

| Unit | Design |
| --- | --- |
| certgen | One-shot container: CA, `server.crt`, `client-<target>.crt` with CN = target id, into `data/certs`. |
| Backend | Java 21 / Spring Boot. Operator `:9444` (server TLS): artifacts (SHA-256), campaigns, devices. Device `:9443` (mutual TLS, CA-signed client required): register, targets, manifest, artifact, status. SQLite state. |
| RTCU | Single vehicle agent. Per cycle (~10 s): probe each `targets[].adb_endpoint` (TCP + `adb get-state`), report reachability, poll manifest per target, download, verify SHA-256, `adb install -r`, report `downloading → installing → success/failed`. Unreachable target → `failed`. |
| Targets | `PC-CUTTLEFISH-01` (`127.0.0.1:6520`), `PI-ANDROID-15` (`10.42.0.35:5555`, Ethernet). |
