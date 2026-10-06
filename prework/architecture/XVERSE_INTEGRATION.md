# Eclipse SDV Hackathon 2026 - Full Architecture with X-Verse

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                             │
│  LAYER 6: DASHBOARD                                                        ★ OUR CODE      │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           Dashboard (HTML/JS/Python)                                 │   │
│  │                              http://localhost:8080                                   │   │
│  │         Speed Display | State | DTCs | Fault Injection | Recovery Controls          │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                              ▲                                              │
│                                              │ REST API (HTTP)                              │
│                                              ▼                                              │
│  LAYER 5: OPENSOVD SERVER                                          UPSTREAM + ★ FIXES      │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                        OpenSOVD Gateway (Rust/Axum)                                  │   │
│  │                           http://localhost:7690                                      │   │
│  │                                                                                      │   │
│  │   GET  /sovd/v1/components/{id}/faults     ─── Issue #553 Fix: Mode.value          │   │
│  │   PUT  /sovd/v1/components/{id}/status/restart ─── Issue #553 Fix: Restart endpoint│   │
│  │   GET  /sovd/v1/components/{id}/data       ─── Issue #553 Fix: Bulk-data category  │   │
│  │                                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                              ▲                                              │
│                                              │ DataProvider / FaultProvider Traits          │
│                                              ▼                                              │
│  LAYER 4: SOVD ADAPTER (PR #16)                                            ★ OUR CODE      │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           sovd_adapter (Rust)                                        │   │
│  │                                                                                      │   │
│  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                     │   │
│  │   │  DataProvider   │  │  FaultProvider  │  │  ModeProvider   │                     │   │
│  │   │  get_data()     │  │  get_faults()   │  │  get_modes()    │                     │   │
│  │   │  set_data()     │  │  clear_fault()  │  │  activate()     │                     │   │
│  │   └─────────────────┘  └─────────────────┘  └─────────────────┘                     │   │
│  │                                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                              ▲                                              │
│                                              │ DTC Events / Data Resources                  │
│                                              ▼                                              │
│  LAYER 3: DIAGNOSTICS                                                      ★ OUR CODE      │
│  ┌───────────────────────────────────┐  ┌───────────────────────────────────────────────┐  │
│  │        cruise_diag (Rust)         │  │            cruise_bridge (Rust)                │  │
│  │                                   │  │                                                │  │
│  │  ┌─────────────┐ ┌─────────────┐ │  │  ┌─────────────────────────────────────────┐  │  │
│  │  │FaultMonitor │ │ DtcStorage  │ │  │  │         MwComBridge                     │  │  │
│  │  │             │ │             │ │  │  │                                         │  │  │
│  │  │ check()     │ │ store_dtc() │ │◄─┼──│  subscribe_speed()                      │  │  │
│  │  │ debounce    │ │ get_dtcs()  │ │  │  │  publish_state()                        │  │  │
│  │  │ 5s confirm  │ │ clear()     │ │  │  │                                         │  │  │
│  │  │ 2s heal     │ │             │ │  │  │  TCP Connection to gatewayd:7700        │  │  │
│  │  └─────────────┘ └─────────────┘ │  │  └─────────────────────────────────────────┘  │  │
│  │                                   │  │                                                │  │
│  │  DTC U0100: Speed Sensor Lost    │  │                                                │  │
│  └───────────────────────────────────┘  └───────────────────────────────────────────────┘  │
│                                                             ▲                               │
│                                                             │ TCP :7700                     │
│ ════════════════════════════════════════════════════════════╪═══════════════════════════════
│                                                             │                               │
│                              X-VERSE DOCKER CONTAINER       │         CRUISE CONTROL TEAM   │
│ ┌───────────────────────────────────────────────────────────┼─────────────────────────────┐ │
│ │                                                           ▼                             │ │
│ │  LAYER 2: S-CORE GATEWAY                                                                │ │
│ │  ┌─────────────────────────────────┐  ┌───────────────────────────────────────────────┐│ │
│ │  │        gatewayd                 │  │                 someipd                        ││ │
│ │  │        (mw::com)                │  │               (vSomeIP 3.6.1)                  ││ │
│ │  │                                 │  │                                                ││ │
│ │  │  ┌───────────┐ ┌─────────────┐ │  │  ┌─────────────────────────────────────────┐  ││ │
│ │  │  │ LoLa IPC  │ │ TCP Bridge  │ │◄─┼──│          SOME/IP Protocol               │  ││ │
│ │  │  │ /dev/shm  │ │   :7700     │ │  │  │                                         │  ││ │
│ │  │  │           │ │             │ │  │  │  Service Discovery (UDP :30490)         │  ││ │
│ │  │  │ Zero-copy │ │ External    │ │  │  │  Events (UDP :30509)                    │  ││ │
│ │  │  │ PreSer.   │ │ Clients     │ │  │  │                                         │  ││ │
│ │  │  └───────────┘ └─────────────┘ │  │  │  /tmp/vsomeip-0 (local socket)          │  ││ │
│ │  │                                 │  │  └─────────────────────────────────────────┘  ││ │
│ │  │  mw_com_config.json            │  │  vsomeip.json                                  ││ │
│ │  └─────────────────────────────────┘  └───────────────────────────────────────────────┘│ │
│ │                         ▲                                   ▲                          │ │
│ │                         │ LoLa IPC                          │ SOME/IP                  │ │
│ │                         │ (Shared Memory)                   │ (UDP Events)             │ │
│ │                         ▼                                   ▼                          │ │
│ │  LAYER 1: CRUISE CONTROL ECU                                                           │ │
│ │  ┌─────────────────────────────────────────────────────────────────────────────────┐  │ │
│ │  │                        cruise_control_main (C++)                                 │  │ │
│ │  │                                                                                  │  │ │
│ │  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐ │  │ │
│ │  │   │  PID Controller │  │  State Machine  │  │     mw::com Skeleton            │ │  │ │
│ │  │   │                 │  │                 │  │                                  │ │  │ │
│ │  │   │  Kp = 0.25      │  │  STANDBY        │  │  CruiseControlSkeleton          │ │  │ │
│ │  │   │  Ki = 0.03      │  │  ACTIVE         │  │  - SpeedEvent                   │ │  │ │
│ │  │   │  Kd = 0.12      │  │  DISABLING      │  │  - StateField                   │ │  │ │
│ │  │   │                 │  │  DISABLED       │  │  - ThrottleField                │ │  │ │
│ │  │   │  50ms loop      │  │                 │  │                                  │ │  │ │
│ │  │   └─────────────────┘  └─────────────────┘  └─────────────────────────────────┘ │  │ │
│ │  │                                                                                  │  │ │
│ │  └─────────────────────────────────────────────────────────────────────────────────┘  │ │
│ │                                              ▲                                         │ │
│ │                                              │ SOME/IP Events                          │ │
│ │                                              ▼                                         │ │
│ │  LAYER 0: CAR SIMULATION                                                               │ │
│ │  ┌─────────────────────────────────────────────────────────────────────────────────┐  │ │
│ │  │                        car_simulation (C++)                                      │  │ │
│ │  │                                                                                  │  │ │
│ │  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐ │  │ │
│ │  │   │ Vehicle Physics │  │  Speed Sensor   │  │     vSomeIP Publisher           │ │  │ │
│ │  │   │                 │  │                 │  │                                  │ │  │ │
│ │  │   │  Mass: 1500kg   │  │  OK / FAILED    │  │  Service 0x1234                 │ │  │ │
│ │  │   │  Drag: 0.3      │  │  (Fault Inject) │  │  Instance 0x5678                │ │  │ │
│ │  │   │  Max: 250 km/h  │  │                 │  │  Event 0x8001 (Speed)           │ │  │ │
│ │  │   │                 │  │                 │  │                                  │ │  │ │
│ │  │   └─────────────────┘  └─────────────────┘  └─────────────────────────────────┘ │  │ │
│ │  │                                                                                  │  │ │
│ │  └─────────────────────────────────────────────────────────────────────────────────┘  │ │
│ │                                                                                        │ │
│ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                             │
│  TESTING: openDuT                                                          ★ OUR CONFIG    │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │   Distributed Test Orchestration | 13 Assertions | Fault Injection Scenarios        │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
                                    FAULT INJECTION FLOW
                                    ═══════════════════

  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │  Dashboard   │ ──────► │   OpenSOVD   │ ──────► │ sovd_adapter │
  │  (Browser)   │  HTTP   │   Gateway    │  Trait  │   (PR #16)   │
  └──────────────┘  PUT    └──────────────┘  Call   └──────────────┘
        │                                                   │
        │ Click "Inject Fault"                              │ store_dtc()
        ▼                                                   ▼
  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │   Response   │ ◄────── │    Fault     │ ◄────── │ cruise_diag  │
  │  DTC U0100   │  JSON   │   Provider   │  Event  │ FaultMonitor │
  └──────────────┘         └──────────────┘         └──────────────┘
                                                            │
                                                            │ check_signal(None)
                                                            ▼
                                    ╔═══════════════════════════════════╗
                                    ║  DEBOUNCE LOGIC                   ║
                                    ║  ─────────────────                ║
                                    ║  0ms:   Signal Lost → PENDING     ║
                                    ║  5000ms: PENDING → CONFIRMED      ║
                                    ║         Store DTC U0100           ║
                                    ║         Warning Indicator ON      ║
                                    ╚═══════════════════════════════════╝
                                                            │
                                                            │ Notify
                                                            ▼
  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │ cruise_bridge│ ◄────── │   gatewayd   │ ◄────── │ cruise_ctrl  │
  │  (TCP:7700)  │  LoLa   │   (mw::com)  │  LoLa   │ State=DISABL │
  └──────────────┘  IPC    └──────────────┘  IPC    └──────────────┘
                                    ▲
                                    │
                           X-VERSE CONTAINER
```

---

## Component Responsibility Matrix

| Layer | Component | Location | Owner | Port/Protocol |
|-------|-----------|----------|-------|---------------|
| **6** | Dashboard | Our repo | ★ **OUR CODE** | HTTP :8080 |
| **5** | OpenSOVD Gateway | opensovd-core | UPSTREAM + ★ **FIXES** | HTTP :7690 |
| **4** | sovd_adapter | inc_diagnostics | ★ **OUR CODE (PR #16)** | Internal |
| **3** | cruise_diag | Our repo | ★ **OUR CODE** | Internal |
| **3** | cruise_bridge | Our repo | ★ **OUR CODE** | TCP :7700 |
| **2** | gatewayd | X-Verse | Cruise Team | TCP :7700, LoLa |
| **2** | someipd | X-Verse | Cruise Team | UDP :30509 |
| **1** | cruise_control | X-Verse | Cruise Team | LoLa IPC |
| **0** | car_simulation | X-Verse | Cruise Team | SOME/IP |
| **T** | openDuT config | Our repo | ★ **OUR CONFIG** | - |

---

## X-Verse Container Details

```
┌─────────────────────────────────────────────────────────────────────┐
│                     X-VERSE DOCKER CONTAINER                        │
│                                                                     │
│  docker-compose.yaml                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  services:                                                   │   │
│  │    score-xverse:                                             │   │
│  │      build: .                                                │   │
│  │      network_mode: host        # Host networking             │   │
│  │      volumes:                                                │   │
│  │        - /tmp:/tmp             # vSomeIP sockets             │   │
│  │        - /dev/shm:/dev/shm     # LoLa shared memory          │   │
│  │      environment:                                            │   │
│  │        - VSOMEIP_CONFIGURATION=/etc/vsomeip.json             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  entrypoint.sh                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  #!/bin/bash                                                 │   │
│  │  # Start someipd (SOME/IP daemon)                           │   │
│  │  ./someipd &                                                 │   │
│  │                                                              │   │
│  │  # Start gatewayd (mw::com router)                          │   │
│  │  ./gatewayd --config /etc/mw_com_config.json &              │   │
│  │                                                              │   │
│  │  # Start cruise control application                         │   │
│  │  ./cruise_control_main                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Exposed:                                                           │
│  ├── TCP :7700    (gatewayd external bridge)                       │
│  ├── UDP :30509   (SOME/IP events)                                  │
│  ├── UDP :30490   (SOME/IP service discovery)                       │
│  └── /tmp/vsomeip-* (local Unix sockets)                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. cruise_bridge ↔ X-Verse (gatewayd)

```
┌─────────────────┐                    ┌─────────────────┐
│  cruise_bridge  │                    │    gatewayd     │
│   (Our Code)    │                    │   (X-Verse)     │
│                 │    TCP :7700       │                 │
│  MwComBridge    │◄──────────────────►│  TCP Bridge     │
│                 │                    │                 │
│  - Subscribe    │    JSON Messages   │  - Route to     │
│    SpeedEvent   │◄──────────────────►│    LoLa IPC     │
│  - Publish      │                    │  - Proxy to     │
│    StateField   │                    │    SOME/IP      │
└─────────────────┘                    └─────────────────┘

Message Format:
{
  "type": "Event",
  "channel_id": 4097,  // 0x1001 = CRUISE_SPEED
  "payload": [120, 0, 0, 0],  // Speed in bytes
  "timestamp_ms": 1699123456789
}
```

### 2. Data Flow: Speed Event

```
Car Simulation
     │
     │ vSomeIP Event (Service 0x1234, Event 0x8001)
     ▼
someipd (vSomeIP 3.6.1)
     │
     │ Internal routing
     ▼
gatewayd (mw::com)
     │
     │ LoLa IPC (shared memory)
     ▼
cruise_control (C++)
     │
     │ PID calculation
     ▼
gatewayd (mw::com)
     │
     │ TCP :7700
     ▼
cruise_bridge (Rust)  ◄── OUR CODE
     │
     │ Internal Rust channel
     ▼
cruise_diag (Rust)  ◄── OUR CODE
     │
     │ FaultMonitor check
     ▼
sovd_adapter (Rust)  ◄── OUR CODE (PR #16)
     │
     │ DataProvider trait
     ▼
OpenSOVD Gateway  ◄── UPSTREAM + OUR FIXES (Issue #553)
     │
     │ REST API
     ▼
Dashboard (HTML/JS)  ◄── OUR CODE
```

---

## Ports & Protocols Summary

| Port | Protocol | Component | Direction | Purpose |
|------|----------|-----------|-----------|---------|
| **8080** | HTTP | Dashboard | IN | Web UI |
| **7690** | HTTP | OpenSOVD | IN | REST API |
| **7700** | TCP | gatewayd | IN/OUT | mw::com bridge |
| **30509** | UDP | someipd | IN/OUT | SOME/IP events |
| **30490** | UDP | someipd | IN/OUT | Service discovery |
| - | Unix | /tmp/vsomeip-* | Local | vSomeIP local |
| - | SHM | /dev/shm | Local | LoLa IPC |

---

## Run Commands

### Start X-Verse (Cruise Control Team)

```bash
cd /path/to/adas_s-core-dev-sdv-hackathon-2026/cc_s-core

# Build binaries
bazel build \
    //tests/integration/gatewayd \
    //tests/integration/someipd \
    //score/cruise_control:cruise_control_main

# Start X-Verse container
docker compose --project-directory deployment/xverse/docker_setup up -d
```

### Start Our Stack (On Top of X-Verse)

```bash
# Terminal 1: Start OpenSOVD Gateway
cd layer5-sovd/opensovd-server
cargo run --release -- --port 7690

# Terminal 2: Start cruise_bridge + cruise_diag + sovd_adapter
cd our-demo
cargo run --release -- --gateway localhost:7700 --sovd localhost:7690

# Terminal 3: Start Dashboard
cd layer6-dashboard/web
python3 server.py
```

### Or Use Docker Compose (Everything)

```bash
docker-compose -f docker-compose-full.yaml up -d
```

---

## Visual: Hackathon Demo Flow

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          HACKATHON DEMO (60 seconds)                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  0:00 ──► NORMAL OPERATION                                                    ║
║           Dashboard shows: Speed=120, State=ACTIVE, Faults=0                  ║
║           ┌─────────────────────────────────────────────────────────────┐    ║
║           │  [████████████████████████░░░░░░]  120 km/h                 │    ║
║           │  State: ACTIVE    Target: 120    Faults: 0                  │    ║
║           └─────────────────────────────────────────────────────────────┘    ║
║                                                                               ║
║  0:15 ──► FAULT INJECTION                                                     ║
║           Click "Inject Fault" button                                         ║
║           Speed signal stops flowing from car_simulation                      ║
║                                                                               ║
║  0:20 ──► FAULT DETECTION                                                     ║
║           cruise_diag detects signal timeout (100ms)                          ║
║           FaultState: OK → PENDING                                            ║
║                                                                               ║
║  0:25 ──► FAULT CONFIRMATION                                                  ║
║           After 5s debounce: PENDING → CONFIRMED                              ║
║           DTC U0100 stored: "Lost Communication with Speed Sensor"            ║
║           Dashboard shows: State=DISABLING, Faults=1                          ║
║           ┌─────────────────────────────────────────────────────────────┐    ║
║           │  [████░░░░░░░░░░░░░░░░░░░░░░░░░░]  45 km/h                  │    ║
║           │  State: DISABLING    Target: 120    Faults: 1  ⚠️           │    ║
║           │  ┌─────────────────────────────────────────────────────┐   │    ║
║           │  │ U0100 - Lost Communication with Speed Sensor        │   │    ║
║           │  └─────────────────────────────────────────────────────┘   │    ║
║           └─────────────────────────────────────────────────────────────┘    ║
║                                                                               ║
║  0:35 ──► SAFE DISABLE                                                        ║
║           Vehicle decelerates to 0 km/h                                       ║
║           State: DISABLING → DISABLED                                         ║
║                                                                               ║
║  0:40 ──► DIAGNOSIS VIA API                                                   ║
║           curl http://localhost:7690/sovd/v1/components/cruise-ecu/faults     ║
║           Response: {"faults": [{"dtc": "U0100", "confirmedDtc": true}]}      ║
║                                                                               ║
║  0:50 ──► RECOVERY                                                            ║
║           PUT http://localhost:7690/sovd/v1/components/cruise-ecu/status/restart
║           Fault cleared, system returns to STANDBY                            ║
║           Dashboard shows: Speed=0, State=STANDBY, Faults=0                   ║
║                                                                               ║
║  1:00 ──► DEMO COMPLETE ✓                                                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

*Architecture document for Eclipse SDV Hackathon 2026*
*X-Verse integration with our diagnostic layer contribution*
