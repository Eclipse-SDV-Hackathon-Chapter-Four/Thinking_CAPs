# Demo Plan - Cruise Control Diagnostics

## Demo Overview

| Field | Value |
|-------|-------|
| **Duration** | 60 seconds |
| **Use Case** | Speed Signal Loss Detection |
| **Outcome** | DTC displayed on dashboard via SOVD |

---

## Demo Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      DEMO SETUP                            │
│                                                            │
│  ┌─────────────┐         ┌─────────────┐                  │
│  │  X-Verse    │◄──TCP──►│cruise_bridge│                  │
│  │  Container  │  :7700  │cruise_diag  │                  │
│  └─────────────┘         └──────┬──────┘                  │
│                                 │                          │
│                                 ▼                          │
│                          ┌─────────────┐                  │
│                          │sovd_adapter │                  │
│                          └──────┬──────┘                  │
│                                 │                          │
│                                 ▼                          │
│                          ┌─────────────┐                  │
│                          │  OpenSOVD   │                  │
│                          │   :7690     │                  │
│                          └──────┬──────┘                  │
│                                 │                          │
│                                 ▼                          │
│                          ┌─────────────┐                  │
│                          │  Dashboard  │                  │
│                          │   :8080     │                  │
│                          └─────────────┘                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Demo Script (60 seconds)

### T+0s: Start

```
[Dashboard shows]
┌─────────────────────────────────────┐
│ Eclipse SDV Hackathon 2026          │
│                                     │
│ Speed: 120.5 km/h    Status: OK     │
│ Target: 120.0 km/h                  │
│ Throttle: 45%                       │
│                                     │
│ Faults: None                        │
└─────────────────────────────────────┘
```

**Say:** "Dashboard showing live speed from cruise control via SOVD."

### T+10s: Inject Fault

```bash
# Stop speed signal (simulate sensor failure)
docker exec xverse pkill car_simulation
```

**Say:** "Injecting speed signal loss - simulating sensor failure."

### T+15s: Debounce Period

```
[Dashboard shows]
┌─────────────────────────────────────┐
│ Speed: 120.5 km/h    Status: STALE  │
│ Target: 120.0 km/h                  │
│ Throttle: 0%                        │
│                                     │
│ Faults: Pending...                  │
│ Debounce: 3/5 seconds               │
└─────────────────────────────────────┘
```

**Say:** "System detecting stale signal. 5-second debounce before confirming fault."

### T+20s: DTC Confirmed

```
[Dashboard shows - RED ALERT]
┌─────────────────────────────────────┐
│ Speed: --- km/h      Status: FAULT  │
│ Target: 120.0 km/h                  │
│ Throttle: 0% (DISABLED)             │
│                                     │
│ FAULT DETECTED:                     │
│ ┌─────────────────────────────────┐ │
│ │ DTC: CC001                      │ │
│ │ Name: SpeedSignalStale          │ │
│ │ Status: CONFIRMED (0x09)        │ │
│ │ First: 2026-10-07 10:00:15      │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Say:** "Fault confirmed after 5-second debounce. DTC exposed via SOVD API."

### T+30s: Show SOVD API

```bash
curl http://localhost:7690/sovd/v1/components/hpc/faults/CC001 | jq
```

```json
{
  "code": "CC001",
  "fault_name": "SpeedSignalStale",
  "status": {
    "test_failed": true,
    "confirmed_dtc": true,
    "mask": "09"
  },
  "first_occurrence": "2026-10-07T10:00:15Z"
}
```

**Say:** "SOVD REST API returns ISO 17978-3 compliant fault data."

### T+40s: Restore Signal

```bash
docker exec xverse /start_car_simulation.sh
```

**Say:** "Restoring speed signal."

### T+45s: Healing

```
[Dashboard shows]
┌─────────────────────────────────────┐
│ Speed: 118.2 km/h    Status: HEAL   │
│ Target: 120.0 km/h                  │
│ Throttle: 48%                       │
│                                     │
│ Fault Healing: 1/2 seconds          │
└─────────────────────────────────────┘
```

**Say:** "System healing. 2-second debounce before clearing fault."

### T+50s: System Normal

```
[Dashboard shows - GREEN]
┌─────────────────────────────────────┐
│ Speed: 120.1 km/h    Status: OK     │
│ Target: 120.0 km/h                  │
│ Throttle: 44%                       │
│                                     │
│ Faults: None (CC001 healed)         │
└─────────────────────────────────────┘
```

**Say:** "System recovered. Fault healed. Full diagnostic flow via SOVD."

### T+60s: End

**Say:** "This demonstrates S-CORE to OpenSOVD bridge - our PR #16 contribution."

---

## Demo Commands

### Start Everything

```bash
# 1. Start X-Verse
cd cc_s-core/deployment/xverse/docker_setup
docker-compose up -d

# 2. Start our bridge
cd demo/X-Verse/external_hackathon_ecus/OpenSOVD/gateway/harness
cargo run --release &

# 3. Start OpenSOVD
opensovd-gateway --mock &

# 4. Start dashboard
cd demo/live
python3 server.py &

# 5. Open browser
open http://localhost:8080
```

### Inject Fault

```bash
docker exec xverse pkill car_simulation
```

### Restore Signal

```bash
docker exec xverse /start_car_simulation.sh
```

### Query SOVD

```bash
# List faults
curl http://localhost:7690/sovd/v1/components/hpc/faults

# Get specific fault
curl http://localhost:7690/sovd/v1/components/hpc/faults/CC001

# Get speed data
curl http://localhost:7690/sovd/v1/apps/cruise/data/current_speed
```

---

## Backup Plan

If live demo fails:

1. **Recorded video** - Pre-record the full demo
2. **Screenshots** - Show dashboard states
3. **SOVD output** - Show curl command outputs
4. **Architecture diagram** - Explain flow

---

## What Demo Proves

| Claim | Evidence |
|-------|----------|
| S-CORE ↔ OpenSOVD works | Live data flow |
| Fault detection works | DTC generated |
| SOVD compliance | REST API output |
| ISO 17978-3 format | JSON structure |
| Debounce logic | 5s confirm, 2s heal |

---

*Demo plan prepared for Eclipse SDV Hackathon 2026*
*This is PRE-WORK planning only - no code written*
