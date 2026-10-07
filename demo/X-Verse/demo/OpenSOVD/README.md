# OpenSOVD vECU

The diagnostics side of the cruise control demo as containers, started like the other
X-Verse vECUs (`vecu/ota`, `vecu/s-core`) with a `ctl.sh`, and by `run_autoverse.py`.

| Container | What | Port |
|---|---|---|
| `opensovd-gateway` | `opensovd-gateway` of eclipse-score/inc_diagnostics PR #40 (`d388985`): component `cruise` with `vehicle_speed`, `cruise_state`, `speed_sensor_fault_status`, read-write `speed_sensor_stuck` | 7690 |
| `sovd-adapter-console` | [SOVD Adapter Console](../SOVD_Adapter_Console/): live vehicle speed from Zenoh (`tcp/127.0.0.1:7447`), the gateway, the fault bridge and the automatic classic DTC | 8080 |
| `testcontainer-ecu-sim-1`, `testcontainer-cda-1` | upstream classic-diagnostic-adapter test containers (ECU simulator + CDA), checkout at `../../upstream/classic-diagnostic-adapter` when it exists, else `.local/` (cloned at `c1a5d8b` on first `up`; test config `cda/cda-test-config.toml`) | 8181, 20002 |

All use the host network, so they meet on `127.0.0.1` like the S-CORE containers.

```bash
./ctl.sh up       # build (cached) + start everything, open http://localhost:8080
./ctl.sh check    # the console's 13 checks, inside the console container
./ctl.sh stop | start | down | logs
```

The first `up` compiles the gateway (about 2 min) and the CDA (about 15 min); later runs reuse the
images. `OPENSOVD_CDA=0` leaves the CDA + ECU simulator out, `OPENSOVD_BROWSER=0` skips the browser,
`CRUISE_DEBOUNCE_FAILED_MS` / `CRUISE_DEBOUNCE_PASSED_MS` set the gateway debounce (demo 1500 / 1000).

`run_autoverse.py` runs `./ctl.sh up` as the step "OpenSOVD vECU" and `./ctl.sh stop` on shutdown.
It finds this folder at `demo/OpenSOVD` in its own checkout (autoverse `dev/sdv-hackathon-2026`);
`OPENSOVD_VECU_DIR` overrides it.

## Gateway build

Bazel cannot build the binary yet (review finding CR-13), so `gateway/Dockerfile` fetches
inc_diagnostics at `d388985` and compiles the upstream sources in place with the Cargo
workspace in `gateway/harness/`, which mirrors the Bazel targets (`diag_api` split crates,
`diag_json` alias of `serde_json`, opensovd-core at `29e806f`). `gateway/harness/Cargo.lock`
pins the crate versions of the verified build. Build arguments `INC_DIAGNOSTICS_COMMIT` and
`INC_DIAGNOSTICS_REPO` select another revision.

## Verified (2026-10-07)

With the full X-Verse environment running (CARLA virtual vehicle on Zenoh, S-CORE, OTA,
Cuttlefish): `./ctl.sh up` → 13/13 console checks; `stop` / `start` cycle clean; the
`stuck-switch` scenario (P0500 confirmed after the 1.5 s debounce, ECU DTC 01E241 read back via
the CDA, healed) 5/5.
