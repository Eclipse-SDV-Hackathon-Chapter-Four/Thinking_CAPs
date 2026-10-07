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
./ctl.sh build    # build the images only (setup.sh runs this)
./ctl.sh up       # build (cached) + start everything, open http://localhost:8080
./ctl.sh check    # the console's 13 checks, inside the console container
./ctl.sh stop | start | down | logs
```

The first build compiles the gateway (about 2 min) and the CDA (about 15 min), longer than
`run_autoverse.py` waits for a step to start, so `setup.sh` runs `./ctl.sh build` beforehand; later
runs reuse the images. `OPENSOVD_CDA=0` leaves the CDA + ECU simulator out, `OPENSOVD_BROWSER=0` skips the browser,
`CRUISE_DEBOUNCE_FAILED_MS` / `CRUISE_DEBOUNCE_PASSED_MS` set the gateway debounce (demo 1500 / 1000).

This folder and [`../SOVD_Adapter_Console`](../SOVD_Adapter_Console/) belong to Thinking_CAPs and
sit next to `demo/X-Verse`, like `ThreadX/`: they are not part of the X-Verse (autoverse) copy, so
`scripts/sync-xverse.sh` never duplicates them. `run_autoverse.py` (step "OpenSOVD vECU": `./ctl.sh up`,
`./ctl.sh stop` on shutdown) and `setup.sh` (`./ctl.sh build`) find this folder next to their checkout
(`demo/X-Verse` → `demo/OpenSOVD`, also through a `~/autoverse` link), else at
`~/Thinking_CAPs/demo/OpenSOVD`; `OPENSOVD_VECU_DIR` overrides it.

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
