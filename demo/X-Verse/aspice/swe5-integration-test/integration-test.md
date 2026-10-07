# Integration test — X-Verse end-to-end demonstration

Black-box checks of the interfaces between the elements, run by
[`tools/e2e_check.py`](../tools/e2e_check.py) against the **running** system
(`run_autoverse.py --enable-camera-display --vcu-zenoh`). Read-only: nothing is injected
or changed.

| ID | Test case | Interfaces | Pass criterion | Verifies |
| --- | --- | --- | --- | --- |
| ITC-01 | Zenoh router reachable | IF-01..03 | TCP connect to `127.0.0.1:7447` | SWR-01 |
| ITC-02 | Supervised containers running | — | `bridge-e2e`, `docker_setup-adas_score-1`, `ota-backend`, `ota-rtcu`, `cuttlefish-orchestration-cont` are running | SWR-01 |
| ITC-03 | Vehicle state and driver requests on Zenoh | IF-01, IF-02 | `velocity_status`, `clock_status` and `brake_pedal_sts` received within 3 s | SWR-02, SWR-03 |
| ITC-04 | VCU commands on Zenoh | IF-03 | `vcu/control/throttle_cmd` and `brake_cmd` received within 3 s | SWR-04 |
| ITC-05 | Speed reaches the S-CORE ECU over SOME/IP | IF-01, IF-04, IF-06, IF-07 | SOVD `vehicle_speed` sample younger than 1 s | SWR-05, SWR-07 |
| ITC-06 | Cruise-control state exposed | IF-06, IF-07 | SOVD `cruise_state` reports a state and a software identity | SWR-06 |
| ITC-07 | DTC served through PR #16 `sovd_adapter` | IF-07 | component `cruise_control` listed, `cc_lost_communication` present, status `passed` with a fresh signal | SWR-07 |
| ITC-08 | certgen PKI | — | server and every client certificate verify against the CA; client CN = target id | SWR-08 |
| ITC-09 | Device API requires mutual TLS | IF-09 | TLS handshake without client certificate fails; with a client certificate the API answers | SWR-09 |
| ITC-10 | RTCU registered and targets reported | IF-08, IF-09 | operator API lists `PC-CUTTLEFISH-01` reachable with a recent `lastSeen` | SWR-09, SWR-10 |
| ITC-11 | Campaign outcomes recorded per target | IF-08..10 | a successful campaign for Cuttlefish and for the Pi, and a failed (closed) campaign for an unreachable target | SWR-10 |
| ITC-12 | CARLA ego vehicle present | — | actor with role `ego_vehicle` exists | SWR-02 |
| ITC-13 | Android target ready with the cluster app | IF-10 | `sys.boot_completed = 1` and `com.example.digitalclusterapp` installed | SWR-11 |
