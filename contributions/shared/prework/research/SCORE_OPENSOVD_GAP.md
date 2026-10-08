# S-CORE and OpenSOVD Integration Gap Analysis

## The Problem - Epic #1766

| Field | Value |
|-------|-------|
| **Epic** | #1766 - S-CORE ↔ OpenSOVD Integration |
| **Gap** | No bridge exists between S-CORE middleware and OpenSOVD diagnostics |
| **Impact** | S-CORE apps can't expose diagnostics via SOVD standard |

---

## Current State

### S-CORE (Eclipse Score)

| Attribute | Details |
|-----------|---------|
| **Repository** | https://github.com/eclipse-score |
| **Purpose** | Safety-certified middleware for automotive |
| **IPC** | mw::com (SOME/IP compatible), LoLa, iceoryx2 |
| **Language** | Rust + C++ |
| **Safety** | Up to ASIL-B |

### OpenSOVD

| Attribute | Details |
|-----------|---------|
| **Repository** | https://github.com/eclipse-opensovd |
| **Purpose** | ISO 17978 SOVD diagnostic server |
| **Protocol** | REST/HTTP + JSON |
| **Language** | Rust |
| **Safety** | QM (diagnostics) |

---

## The Gap

```
S-CORE Apps                    OpenSOVD Server
    │                               │
    │  mw::com / LoLa / iceoryx2    │  REST/HTTP
    │                               │
    └──────────── ??? ──────────────┘
                  │
            NO BRIDGE EXISTS
```

### What's Missing

| Component | Status | What It Should Do |
|-----------|--------|-------------------|
| **sovd_adapter** | Not implemented | Translate S-CORE data to SOVD resources |
| **DataProvider** | Not implemented | Expose mw::com signals as SOVD `data` |
| **FaultProvider** | Not implemented | Expose S-CORE faults as SOVD `faults` |
| **Component registration** | Not implemented | Register S-CORE components with SOVD |

---

## Our Solution - PR #16 (sovd_adapter)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        S-CORE                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ someipd  │  │ gatewayd │  │cruise_app│                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │             │                         │
│       └─────────────┴─────────────┘                         │
│                     │ mw::com                               │
│                     ▼                                       │
│  ┌──────────────────────────────────────────┐              │
│  │           sovd_adapter (PR #16)          │ ◄── OUR CODE │
│  │  ┌──────────────┐  ┌─────────────────┐   │              │
│  │  │ DataProvider │  │ FaultProvider   │   │              │
│  │  └──────────────┘  └─────────────────┘   │              │
│  └──────────────────────────────────────────┘              │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │ TCP :7700
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     OpenSOVD                                │
│  ┌──────────────────────────────────────────┐              │
│  │            opensovd-server               │              │
│  │         REST API :7690                   │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## sovd_adapter Components (To Build During Hackathon)

### 1. Main Adapter (`lib.rs`)

| Function | Purpose |
|----------|---------|
| `SovdAdapter::new()` | Create adapter instance |
| `register_component()` | Register S-CORE component with SOVD |
| `handle_request()` | Process SOVD requests |
| `start()` | Start adapter server |

### 2. DataProvider (`data_provider.rs`)

| Function | Purpose |
|----------|---------|
| `get_data()` | Get data value from mw::com |
| `set_data()` | Set data value via mw::com |
| `list_resources()` | List available data resources |

### 3. FaultProvider (`fault_provider.rs`)

| Function | Purpose |
|----------|---------|
| `get_faults()` | Get faults from S-CORE |
| `clear_fault()` | Clear a fault |
| `get_status()` | Get DTC status bits |

### 4. Component (`component.rs`)

| Function | Purpose |
|----------|---------|
| `Component::new()` | Create component |
| `add_data_resource()` | Add data to component |
| `add_fault_sink()` | Add fault monitoring |

---

## Integration Point - inc_diagnostics

| Field | Value |
|-------|-------|
| **Repository** | eclipse-score/inc_diagnostics |
| **PR** | #16 |
| **Location** | `score/mw/diag/sovd_adapter/` |
| **Purpose** | S-CORE diagnostic adapter module |

---

## Data Flow After Integration

```
1. Speed signal from car simulation
        │
        ▼
2. someipd receives SOME/IP message
        │
        ▼
3. gatewayd routes via mw::com
        │
        ▼
4. cruise_app processes signal
        │
        ▼
5. sovd_adapter exposes via DataProvider  ◄── PR #16
        │
        ▼
6. OpenSOVD server serves REST API
        │
        ▼
7. Dashboard fetches and displays
```

---

## Why This Matters

| Stakeholder | Benefit |
|-------------|---------|
| **OEMs** | Standard diagnostic interface for S-CORE apps |
| **Tool vendors** | One SOVD client works with all S-CORE vehicles |
| **Eclipse** | Integration between two major SDV projects |
| **Hackathon** | Scores high on "Ecosystem Integrability" |

---

## Estimated Effort

| Component | Lines | Time |
|-----------|-------|------|
| `lib.rs` | ~300 | 1.5h |
| `data_provider.rs` | ~200 | 1h |
| `fault_provider.rs` | ~150 | 1h |
| `component.rs` | ~100 | 30min |
| `types.rs` | ~80 | 30min |
| `error.rs` | ~70 | 30min |
| **Total** | **~900** | **~5h** |

---

*Analysis prepared for Eclipse SDV Hackathon 2026*
*This is PRE-WORK research only - no code written*
