# Data Flow - Signal Path from Car to Dashboard

## End-to-End Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW                                   │
│                                                                       │
│  ┌─────────────┐                                                     │
│  │ Car Sim     │ ──SOME/IP──► speed=120.5 km/h                       │
│  │ (Layer 0)   │              UDP :30509                             │
│  └─────────────┘                    │                                 │
│                                     ▼                                 │
│  ┌─────────────┐                                                     │
│  │ someipd     │ ──routes──► vSomeIP message                         │
│  │ (Layer 2)   │              /tmp/vsomeip-*                         │
│  └─────────────┘                    │                                 │
│                                     ▼                                 │
│  ┌─────────────┐                                                     │
│  │ gatewayd    │ ──mw::com──► LoLa message                          │
│  │ (Layer 2)   │              /dev/shm                               │
│  └─────────────┘                    │                                 │
│                                     ▼                                 │
│  ┌─────────────┐                                                     │
│  │ cruise_ctrl │ ──processes──► PID output + fault check            │
│  │ (Layer 1)   │                                                     │
│  └─────────────┘                    │                                 │
│                              TCP :7700                                │
│  ═══════════════════════════════════╪═══════════════════════════════ │
│  ║           X-VERSE CONTAINER      ║                                │
│  ═══════════════════════════════════╪═══════════════════════════════ │
│                                     ▼                                 │
│  ┌─────────────┐                                          OUR CODE   │
│  │cruise_bridge│ ──subscribes──► speed, fault events                │
│  │ (Layer 3)   │                                                     │
│  └─────────────┘                    │                                 │
│                                     ▼                                 │
│  ┌─────────────┐                                          OUR CODE   │
│  │ cruise_diag │ ──monitors──► fault detection                       │
│  │ (Layer 3)   │              debounce 5s confirm, 2s heal           │
│  └─────────────┘                    │                                 │
│                                     ▼                                 │
│  ┌─────────────┐                                          OUR CODE   │
│  │sovd_adapter │ ──exposes──► SOVD data/fault resources             │
│  │ (Layer 4)   │              PR #16                                 │
│  └─────────────┘                    │                                 │
│                                     ▼                                 │
│  ┌─────────────┐                                                     │
│  │ OpenSOVD    │ ──serves──► REST API                               │
│  │ (Layer 5)   │              GET /components/hpc/data               │
│  └─────────────┘              :7690                                  │
│                                     │                                 │
│                                     ▼                                 │
│  ┌─────────────┐                                          OUR CODE   │
│  │ Dashboard   │ ──displays──► Speed: 120.5 km/h                    │
│  │ (Layer 6)   │              DTC: CC001 CONFIRMED                   │
│  └─────────────┘              :8080                                  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Signal Types

### Normal Signals

| Signal | Type | Source | Destination |
|--------|------|--------|-------------|
| `current_speed` | f64 | Car Sim | cruise_control |
| `target_speed` | f64 | User input | cruise_control |
| `throttle` | f64 | cruise_control | Car Sim |
| `brake_position` | f64 | Car Sim | cruise_control |

### Fault Signals

| Signal | Type | Source | Destination |
|--------|------|--------|-------------|
| `speed_valid` | bool | cruise_diag | sovd_adapter |
| `dtc_status` | u8 | cruise_diag | sovd_adapter |
| `fault_active` | bool | cruise_diag | Dashboard |

---

## Fault Detection Flow

```
1. Speed signal arrives
        │
        ▼
2. cruise_diag checks freshness
   - Last update > 1s ago?
        │
        ├── NO → Signal OK
        │
        └── YES → Start debounce timer
                        │
                        ▼
3. Debounce confirm (5000ms)
   - Still stale?
        │
        ├── NO → Reset timer
        │
        └── YES → Set DTC
                        │
                        ▼
4. DTC created: CC001
   - status_mask = 0x09 (testFailed | confirmedDtc)
   - occurrence_counter++
   - first_occurrence = now()
        │
        ▼
5. sovd_adapter exposes fault
   - GET /components/hpc/faults/CC001
        │
        ▼
6. Dashboard shows:
   - "FAULT: Speed Signal Stale"
   - "Status: CONFIRMED"
```

---

## Protocol Details

### Layer 0 → Layer 2: SOME/IP

```
Header:
  Service ID: 0x1234
  Method ID: 0x8001 (event)
  Length: 8

Payload:
  speed: f64 = 120.5
```

### Layer 2 → Layer 3: mw::com (TCP)

```
Message:
  topic: "cruise/speed"
  timestamp: 1696593600000
  payload: { "value": 120.5, "unit": "km/h" }
```

### Layer 4 → Layer 5: SOVD REST

```
GET /sovd/v1/components/hpc/data/current_speed

Response:
{
  "id": "current_speed",
  "category": "currentData",
  "data": {
    "value": 120.5,
    "unit": "km/h",
    "timestamp": "2026-10-07T10:00:00Z"
  }
}
```

### Layer 5 → Layer 6: Dashboard Fetch

```
GET http://localhost:7690/sovd/v1/apps/cruise/data/current_speed

Response displayed as:
┌─────────────────────┐
│ Speed: 120.5 km/h   │
│ Status: OK          │
└─────────────────────┘
```

---

## Timing Requirements

| Transition | Max Latency | Notes |
|------------|-------------|-------|
| Car Sim → someipd | 1ms | Same container |
| someipd → gatewayd | 1ms | LoLa IPC |
| gatewayd → cruise_bridge | 5ms | TCP |
| cruise_diag fault detection | 5000ms | Debounce period |
| sovd_adapter → OpenSOVD | 1ms | In-process |
| OpenSOVD → Dashboard | 50ms | HTTP poll |

---

## Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| Signal stale | No update for 1s | Set DTC, show warning |
| Connection lost | TCP timeout | Reconnect, log error |
| Invalid data | Range check | Substitute safe value |
| SOVD unavailable | HTTP 5xx | Retry with backoff |

---

*Data flow prepared for Eclipse SDV Hackathon 2026*
*This is PRE-WORK design only - no code written*
