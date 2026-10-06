# System Architecture - 7-Layer Stack

## Overview

Our solution bridges Eclipse S-CORE and OpenSOVD through a 7-layer architecture for ADAS diagnostics.

---

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 6: Dashboard                                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  Web UI (HTML/JS) - Real-time speed, DTC, fault status      │ │
│ │  HTTP :8080                                                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 5: OpenSOVD Server                                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  opensovd-server (Rust) - ISO 17978-3 SOVD API              │ │
│ │  REST API :7690                                              │ │
│ │  Issue #553 fixes applied here                               │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 4: sovd_adapter (PR #16)                          OUR CODE│
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  S-CORE ↔ OpenSOVD Bridge                                   │ │
│ │  DataProvider, FaultProvider, Component registration        │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 3: cruise_diag + cruise_bridge                    OUR CODE│
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  Fault Monitoring (debounce, DTC generation)                │ │
│ │  mw::com Client (TCP :7700 connection)                      │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 2: S-CORE Middleware (X-Verse)              CRUISE TEAM  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  gatewayd (mw::com) - TCP :7700                             │ │
│ │  someipd (vSomeIP 3.6.1) - UDP :30509                       │ │
│ │  LoLa IPC (/dev/shm)                                        │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 1: cruise_control_main                        CRUISE TEAM│
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  PID Controller + Fault Detection + DTC Storage             │ │
│ │  Kp=0.25, Ki=0.03, Kd=0.12                                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 0: Car Simulation                             CRUISE TEAM│
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  Vehicle Physics (speed, RPM, brake, temperature)           │ │
│ │  SOME/IP Events                                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Layer 0: Car Simulation (Cruise Team)

| Attribute | Value |
|-----------|-------|
| **Owner** | Cruise Control Team |
| **Purpose** | Simulate vehicle physics |
| **Outputs** | Speed, RPM, Brake, Temperature |
| **Protocol** | SOME/IP events (UDP :30509) |

### Layer 1: cruise_control_main (Cruise Team)

| Attribute | Value |
|-----------|-------|
| **Owner** | Cruise Control Team |
| **Purpose** | Cruise control application |
| **Features** | PID controller, fault detection |
| **Protocol** | mw::com via LoLa |

### Layer 2: S-CORE Middleware (X-Verse - Cruise Team)

| Attribute | Value |
|-----------|-------|
| **Owner** | Cruise Control Team |
| **Components** | someipd, gatewayd |
| **Protocols** | SOME/IP, LoLa, mw::com |
| **External Port** | TCP :7700 |

### Layer 3: cruise_bridge + cruise_diag (OUR CODE)

| Attribute | Value |
|-----------|-------|
| **Owner** | Our Team |
| **Purpose** | Connect to X-Verse, monitor faults |
| **Language** | Rust |
| **Lines** | ~300 |

### Layer 4: sovd_adapter (OUR CODE - PR #16)

| Attribute | Value |
|-----------|-------|
| **Owner** | Our Team |
| **Purpose** | S-CORE to OpenSOVD bridge |
| **Language** | Rust |
| **Lines** | ~900 |
| **PR** | eclipse-score/inc_diagnostics #16 |

### Layer 5: OpenSOVD Server (Upstream + Issue #553)

| Attribute | Value |
|-----------|-------|
| **Owner** | Eclipse OpenSOVD (we fix bugs) |
| **Purpose** | ISO 17978-3 SOVD server |
| **Language** | Rust |
| **Our Fix** | Issue #553 (8 API fixes, ~770 lines) |

### Layer 6: Dashboard (OUR CODE)

| Attribute | Value |
|-----------|-------|
| **Owner** | Our Team |
| **Purpose** | Real-time visualization |
| **Technology** | HTML/JavaScript |
| **Lines** | ~200 |

---

## Protocol Stack

```
Layer 6 ──HTTP─────► REST API :8080
          │
Layer 5 ──HTTP─────► REST API :7690 (SOVD)
          │
Layer 4 ──Rust───────► In-process
          │
Layer 3 ──TCP──────► Port :7700 (mw::com)
          │
Layer 2 ──LoLa─────► /dev/shm (shared memory)
          │
Layer 1 ──SOME/IP──► UDP :30509
          │
Layer 0 ──Simulation
```

---

## Ownership Matrix

| Layer | Component | Owner | Lines | Hackathon Work |
|-------|-----------|-------|-------|----------------|
| 6 | Dashboard | Us | ~200 | Yes |
| 5 | OpenSOVD | Upstream | - | Issue #553 fix |
| 4 | sovd_adapter | Us | ~900 | PR #16 |
| 3 | cruise_bridge/diag | Us | ~300 | Yes |
| 2 | X-Verse | Cruise Team | - | No |
| 1 | cruise_control | Cruise Team | - | No |
| 0 | Car Sim | Cruise Team | - | No |

---

## Standards Compliance

| Standard | Layer | Purpose |
|----------|-------|---------|
| ISO 17978-3 | Layer 5 | SOVD API |
| ISO 14229-1 | Layer 3 | DTC format |
| ISO 26262 | Layer 1-2 | ASIL-B safety |
| SOME/IP | Layer 0-2 | In-vehicle comms |

---

*Architecture prepared for Eclipse SDV Hackathon 2026*
*This is PRE-WORK design only - no code written*
