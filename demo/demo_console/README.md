# Demo Console

A live web console for the cruise control diagnostics demo (Eclipse SDV Hackathon, Chapter Four).
One Python process, standard library only, one web page. It shows two diagnostic paths side by side:

- **S-CORE path**: the cruise control app behind an SOVD gateway (`:7690`): live speed, sensor freeze, debounce, faults.
- **Classic ECU path**: a simulated ECU (`:8181`) read through the Classic Diagnostic Adapter (`:20002`) over UDS/DoIP.

## Run

```
python fakes.py            # development stand-ins for the three backends (terminal 1)
python server.py           # http://localhost:8080                          (terminal 2)
python runner.py           # the 13 checks from the command line
```

With the real services, start `server.py` only. Everything is configured by environment variables
(see `config.py`): `SOVD_URL`, `SOVD_ENTITY`, `CDA_URL`, `CDA_ECU`, `CDA_CLIENT_ID`, `CDA_CLIENT_SECRET`,
`SIM_URL`, `SIM_ECU`, `SIM_FAULT_MEMORY`, `STATS_FILE`, `DOCKER_CONTAINERS`, `CONSOLE_PORT`.
With the fakes there are no containers: set `DOCKER_CONTAINERS=` (empty) so check 4 passes.

Keys on the page: **F** freeze/unfreeze, **I** inject DTC, **C** clear, **R** run the 13 checks.

## Files

| File | Role |
|---|---|
| `server.py` | Serves the page, proxies `/proxy/{sovd,cda,sim}/…` to the backends (adds the CDA token), API for health, Docker, stats, log, runner |
| `backends.py` | Clients for the three backends, token handling, traffic log, `docker ps`, stats rates, DTC status decoder |
| `runner.py` | The 13 checks; `run_all()` for the page, `main()` for the CLI |
| `fakes.py` | Fake S-CORE app + stats writer, fake CDA, fake ECU simulator (shared DTC memory) |
| `static/` | `index.html`, `app.js`, `style.css` |
| `tests/` | `python -m unittest discover tests` |

## What the S-CORE app must provide (agree with the Rust developer)

Behind `SOVD_URL` + `/sovd`, entity `SOVD_ENTITY` (default `components/cruise-control`):

| Call | Answer |
|---|---|
| `GET /sovd/version-info` | health |
| `GET /sovd/v1/{entity}/data/vehicle_speed` | `{"id":"vehicle_speed","data":{"value":87.5,"unit":"km/h","ts":<epoch seconds>}}` |
| `GET /sovd/v1/{entity}/data/debounce` | `{"id":"debounce","data":{"state":"PASSED|PREFAILED|FAILED|PREPASSED","counter":n,"threshold":n,"frozen":bool}}` |
| `PUT /sovd/v1/{entity}/data/sensor_freeze` body `{"data": true|false}` | 204 |
| `GET /sovd/v1/{entity}/faults` | `{"items":[{"code":"P0500","display":"…","status":<UDS status byte>,"severity":n}]}` (#156 model) |
| `stats.json`, rewritten every second | `{"ts": <epoch seconds>, "counters": {"<name>": <int>, …}}` |

The classic path uses the upstream contracts as they are: CDA `POST /vehicle/v15/authorize`
(`client_id`, `client_secret`), `GET /vehicle/v15/components/{ecu}/faults`; simulator
`PUT|DELETE /{ecu}/dtc/{faultMemory}` with `{"id":"01E240","statusMask":"2F","emissionsRelated":false}`.

## The 13 checks

1 SOVD gateway answers · 2 CDA answers with the token · 3 ECU simulator answers · 4 expected Docker containers run ·
5 stats file fresh, counters increase · 6 speed readable, timestamp advances · 7 at start PASSED, no failing fault
(unfreezes first if a previous run left it frozen) · 8 freeze accepted · 9 debounce PREFAILED within 1 s ·
10 FAILED with testFailed and confirmedDTC · 11 unfreeze: testFailed back to 0 · 12 injected DTC in the CDA list
with matching bits · 13 cleared DTC gone from the CDA list.
