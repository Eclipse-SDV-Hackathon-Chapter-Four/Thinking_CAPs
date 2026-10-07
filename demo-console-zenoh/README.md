<!--
  Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
  Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
  Created: 2026-10-06 · Latest version: 2026-10-07
  Goal: How the console works, how to start it, its API, settings, checks and known limits.
-->
# Demo Console v2 (Zenoh input)

> Developed mainly with Claude Fable 5.1 (Anthropic) for the Eclipse SDV Hackathon 2026 · created 2026-10-06 · latest version 2026-10-07.

Live console for the cruise control diagnostics demo (Eclipse SDV Hackathon, Chapter Four).
v2 takes the **vehicle speed from the virtual vehicle over Eclipse Zenoh** instead of a simulated
sensor, detects two faults from it, and **automatically mirrors each fault as a DTC in the classic
ECU**, read back through the Classic Diagnostic Adapter. v1 (the first console, with simulated data) is not part of this folder.

## What changed from v1

| | v1 | v2 |
|---|---|---|
| Speed source | sine curve in `fakes.py` | virtual vehicle, Zenoh key `vehicle/status/velocity_status` |
| Sensor fault | "Freeze sensor" button | **F1 P0500**: implausible values (NaN, text, < 0 or > 300 km/h), counter debounce |
| Link supervision | — | **F2 U0104**: no sample for > 500 ms ("lost communication with cruise control module") |
| Classic DTC | "Inject DTC" form | **automatic**: fault starts → ECU DTC set (0x2F) → read back via CDA; fault heals → 0x28 |
| SOVD entities | `cruise-control` | `cruise-control` (speed, F1) + `cruise-diag` (link status, F2), one owner per fault |
| Checks | 13, with freeze | 13 passive checks + 2 scenario tests (lost link, invalid speed) |
| Dependencies | standard library | standard library + `eclipse-zenoh` 1.x |

## Architecture

```
 virtual vehicle ──Zenoh──► score_app.py (cruise diag stand-in, :7690) ──SOVD-style HTTP──► server.py (console, :8080) ◄── browser
 "96.4" @ ~20 Hz            VehicleLink → CruiseDiag (F1, F2)                                  │  auto_dtc.py
 tcp/127.0.0.1:7447         faults in the #156 model, stats.json                               │  (test harness)
                                                                                               ▼
                                              ECU simulator :8181 ◄── control API (test only) ─┘
                                                    ▲ UDS / DoIP
                                              CDA :20002 ◄── SOVD + Bearer token ── server.py (read back, page)
```

`score_app.py` is a **stand-in** for "cruise diag + SOVD gateway with #16/#156": the speed and the
faults come from real vehicle data, only the serving part is ours. When the real gateway runs,
set `SOVD_URL` to it and stop `score_app.py`; the console stays the same.

The automatic DTC lives in the **console** on purpose: it drives the simulator's control API,
which is test-only, so it must not live in the vehicle computer.

## Quick start (Ubuntu / WSL)

Once (Ubuntu has no `pip` yet; this asks for your password):

```bash
sudo apt-get install -y python3-venv
```

Then, in an Ubuntu window that **stays open** (WSL stops Ubuntu and Docker when the last window closes):

```bash
cd demo-console-zenoh && ./run.sh
```

Open **http://localhost:8080** in the Windows browser. `run.sh` creates `~/.venvs/demo-console-zenoh`,
installs `eclipse-zenoh`, starts the stand-in in the background and the console in the foreground.

- **v1 and v2 use the same ports** (7690, 8080): stop any v1 console first.
- **Real vehicle on another laptop:** `VEHICLE_HOST=<its IP> ./run.sh` (`./run.sh find` shows the IP).
  Its Zenoh peers listen on random ports. The stand-in finds them by scouting, and finds them again after a vehicle restart.
- No virtual vehicle at hand? Start the test vehicle in a second window: `./run.sh vehicle`.
  It publishes the same key as the real one, so never run both.

| Command | What it does |
|---|---|
| `./run.sh` | stand-in + console |
| `VEHICLE_HOST=10.169.127.81 ./run.sh` | the same, with the real vehicle on that laptop |
| `./run.sh find` | list the Zenoh nodes on the network (vehicle IP and ports) |
| `./run.sh vehicle` | test vehicle (20 Hz, control API on :7449) |
| `./run.sh check` | the 13 checks |
| `./run.sh scenario` | lost link + invalid speed, driving the test vehicle automatically |
| `./run.sh scenario-manual` | the same against the real vehicle: it prints what to do and waits |
| `./run.sh test` | unit + end-to-end tests |

On the page: **C** resets the faults (both SOVD entities + ECU memory + automation), **R** runs the checks, **A** acknowledges new DTCs.

### Signal workflow block (bottom left)

Five step chips show where the data is right now: **1 Signal** (Zenoh link state and rate) → **2 Speed** (value, stale, stopped) → **3 Monitor** (F1 debounce state and counter, F2 armed) → **4 Fault** (S-CORE faults failing) → **5 ECU DTC** (DTCs failing / stored in the ECU memory via the CDA). The arrows light up while samples arrive. Under the chips, left: a timeline of events derived from state changes on the page (link lost / back, vehicle stopped / moving, F1 state changes, S-CORE faults failing / healed / cleared, console → ECU DTC actions, DTCs failing, changing or disappearing in the ECU memory). Right: a **sweep scope** like a patient monitor, one screen = 40 s, the trace stays in place and only the cursor moves (nothing scrolls while data arrives): lane 1 the signal flow (samples/s, green = link live, red = lost), lane 2 the speed in km/h (gap = stale).

A **DTC that starts failing in the ECU memory** (new, or stored and failing again) flashes step 5, highlights its event line, counts up a red badge and plays an alarm tone. Browsers allow sound only after one click on the page: the *sound* label shows *ready* or *click the page once to enable*; an alarm raised before that is played at the first click. Ticking the box plays a short test tone. Click step 5 or press **A** to acknowledge. Everything is derived in the browser from the existing polls; nothing is stored server-side, so a page reload starts a new timeline.

## Vehicle input contract

| Item | Value |
|---|---|
| Transport | Eclipse Zenoh **1.x** (tested with 1.10.1); peer mode, connects to `tcp/127.0.0.1:7447`, or to the endpoints found on `VEHICLE_HOST` |
| Key | `vehicle/status/velocity_status` |
| Payload | float32 as text, e.g. `96.4` (whitespace and a trailing NUL are tolerated; a raw 4-byte float32 is accepted as a fallback) |
| Unit | km/h (`SPEED_UNIT=m/s` converts) |
| Rate | any; the demo expects ≥ 1 Hz, the test vehicle sends 20 Hz. F2 fires after 500 ms without a sample |

## Diagnostics

| Fault | Entity | Monitor | Fails when | Heals when |
|---|---|---|---|---|
| **P0500** vehicle speed signal implausible (observer check) | `cruise-control` | plausibility, counter debounce, threshold 5 | 5 more implausible than plausible samples | counter back to 0 |
| **U0104** lost communication with cruise control module | `cruise-diag` | timeout, armed after the first valid sample | no sample for > 500 ms | the next sample |

- A sample is plausible if it decodes to a finite number within 0..300 km/h.
- **One owner per fault.** Silence only affects F2. Invalid but present samples only affect F1; they keep the link alive.
- **Status byte** (ISO 14229-1, simplified as stated on stage): failing = `0x0D` (testFailed + pending + confirmed); healed = `0x0C` (stays stored until cleared).
- **Stale is a state, not a value.** The speed keeps the last valid value and is flagged `stale` once older than the timeout.

## Automatic classic DTC

| S-CORE fault | ECU DTC (`AUTO_DTC_MAP`) | on failing | on healed |
|---|---|---|---|
| P0500 | 01E241 | `0x2F` failing, this cycle, pending, confirmed, since clear | `0x28` confirmed + failed since clear |
| U0104 | 01E242 | `0x2F` | `0x28` |

How it works:
- It polls both SOVD fault lists every 0.5 s and reacts to **edges only**.
- After each change it reads the DTC back through the CDA and times it. Every change is logged, shown as a toast, and its calls appear in the traffic log with origin `auto`.
- If the simulator is unreachable, the change is retried after 5 s.
- **Reset faults** re-arms it.

**Verified against the real CDA + ECU simulator:**
- lost link: U0104 detected 678 ms after the vehicle stopped, DTC read back in 60 ms;
- invalid speed: P0500 failed after 326 ms, DTC read back in 49 ms.

## SOVD-style API of the stand-in (the contract for the real gateway)

Base `SOVD_URL` + `/sovd`.

| Call | Answer |
|---|---|
| `GET /version-info` | `{"sovd_info":[{"version":"1.1.0","base_uri":…,"vendor_info":{…}}]}` |
| `GET /v1/components` | the two entities |
| `GET /v1/components/cruise-control/data/vehicle_speed` | `{"id":"vehicle_speed","data":{"value":96.4,"unit":"km/h","ts":…,"age_ms":…,"stale":false,"last_sample_valid":true,"source":"zenoh:vehicle/status/velocity_status"}}` |
| `GET /v1/components/cruise-control/data/debounce` | `{"data":{"state":"PASSED|PREFAILED|FAILED|PREPASSED","counter":n,"threshold":5,"range_kmh":[0,300],"last_reason":…,"fault":"P0500"}}` |
| `GET /v1/components/cruise-diag/data/link_status` | `{"data":{"state":"live|lost|waiting|connecting|error|no-session","connected":true,"peers":1,"rate_hz":20.0,"age_ms":…,"last_raw":"96.4","monitor_armed":true,…}}` |
| `GET /v1/components/{entity}/faults` | `{"items":[{"code":"U0104","display":…,"status":<UDS status byte>,"severity":2,"monitor":"timeout","occurrences":n}]}` (#156 model) |
| `DELETE /v1/components/{entity}/faults` | 204: clear; a fault failing right now stays failing |

The classic path uses the upstream contracts unchanged:
- **CDA:** `POST /vehicle/v15/authorize`, then `GET /vehicle/v15/components/{ecu}/faults`.
- **Simulator:** `PUT /{ecu}/dtc/{memory}` (a second PUT updates the mask), `DELETE /{ecu}/dtc/{memory}[/{code}]`.

## Settings (environment variables, see `config.py`)

| Variable | Default | Meaning |
|---|---|---|
| `VEHICLE_HOST` | – | IP of the vehicle laptop. The stand-in finds its Zenoh endpoints by scouting, and finds them again after a restart |
| `ZENOH_CONNECT` | `tcp/127.0.0.1:7447` (empty with `VEHICLE_HOST`) | fixed endpoints of the vehicle (or its Zenoh router); comma-separated |
| `ZENOH_MODE` / `ZENOH_LISTEN` / `ZENOH_MULTICAST_SCOUTING` | `peer` / – / `true` | Zenoh session options |
| `SPEED_KEY` / `SPEED_UNIT` | `vehicle/status/velocity_status` / `km/h` | input |
| `SPEED_MIN_KMH` / `SPEED_MAX_KMH` / `F1_THRESHOLD` | `0` / `300` / `5` | F1 |
| `LINK_TIMEOUT_MS` | `500` | F2 |
| `F1_CODE` / `F2_CODE` | `P0500` / `U0104` | fault codes |
| `AUTO_DTC` / `AUTO_DTC_MAP` | `true` / `P0500=01E241,U0104=01E242` | automatic classic DTC |
| `AUTO_DTC_MASK_ACTIVE` / `AUTO_DTC_MASK_HEALED` | `2F` / `28` | ECU status masks |
| `SOVD_URL`, `STANDIN_PORT`, `CONSOLE_PORT` | `:7690`, `7690`, `8080` | ports |
| `CDA_URL`, `CDA_ECU`, `SIM_URL`, `SIM_ECU`, `DEMO_DTC` | `:20002`, `flxc1000`, `:8181`, `FLXC1000`, `01E240` | classic path |
| `DOCKER_CONTAINERS` | `cda,ecu-sim` | expected containers (a single space = none) |

## Checks and scenarios

**13 checks** (page button or `./run.sh check`). They don't disturb the vehicle:
1 SOVD side answers · 2 CDA with token · 3 ECU simulator · 4 Docker containers · 5 Zenoh connected ·
6 samples arriving · 7 speed via SOVD plausible and fresh · 8 F1 PASSED · 9 F2 armed, not failing ·
10 stats file · 11 automatic DTC running · 12 classic round trip on `DEMO_DTC` · 13 delete it again
(other DTCs untouched).

**Scenarios** (`./run.sh scenario`). They make the vehicle misbehave and follow the whole chain:
precondition → S-CORE fault detected → ECU DTC set and read via CDA → vehicle back, fault healed
(confirmed kept) → ECU DTC healed and read via CDA. Both together: 10 steps.

**Tests:** 36, run with `./run.sh test`. They cover the payload decoding, the monitors (fake clock), the automation edges, the vehicle finder, an end-to-end run without Zenoh (13 checks + both scenarios), and real Zenoh pub/sub.

## Files

| File | Role |
|---|---|
| `config.py` | all settings |
| `vehicle_link.py` | Zenoh subscriber, payload decoding, link statistics |
| `discover.py` | finds Zenoh nodes by multicast scouting (in Windows Python when run from WSL) |
| `cruise_diag.py` | F1/F2 monitors and fault store (pure logic) |
| `score_app.py` | cruise diag stand-in: monitor cycle, SOVD-style API, stats.json |
| `auto_dtc.py` | automatic classic DTC (test harness, runs in the console) |
| `server.py` | console: page, proxies, API, reset, runner |
| `backends.py` | backend clients, traffic log, Docker, stats, status decoder |
| `runner.py` | 13 checks + scenarios |
| `vehicle_sim.py` | test vehicle with a control API |
| `classic_fakes.py` | offline CDA + ECU simulator (tests, laptops without Docker) |
| `static/` | page |
| `tests/` | unit and end-to-end tests |
| `run.sh`, `requirements.txt` | start-up |

## Known limits and next steps

- **The stand-in replaces the real chain for now.** The planned chain is virtual vehicle → Zenoh adapter → mw::com → cruise diag (Rust, fault-lib) → opensovd-core with #156. When it runs, point `SOVD_URL` at the real gateway; checks 5, 6 and 9 then need the `cruise-diag` entity and `link_status`, or must be adapted.
- **WSL's NAT network drops multicast,** so Zenoh's own scouting cannot see a vehicle on another laptop. `discover.py` scouts from the Windows side instead, using Windows Python through WSL interop. **It needs Python on Windows.** If the vehicle itself runs inside WSL on its laptop, its multicast never leaves that laptop either. Then that laptop must listen on a fixed port behind a port forward (`netsh interface portproxy` plus a firewall rule on that laptop), and this console starts with `ZENOH_CONNECT=tcp/<its IP>:7447`.
- **On Windows there is no `docker` command:** set `DOCKER_CONTAINERS=" "` there, or check 4 fails.
