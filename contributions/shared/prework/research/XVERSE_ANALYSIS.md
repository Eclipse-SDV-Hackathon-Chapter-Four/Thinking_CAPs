# X-Verse Analysis - Cruise Control Container

## What is X-Verse?

X-Verse is the **Docker deployment configuration** from the Cruise Control team that packages the S-CORE components needed for the demo.

| Field | Value |
|-------|-------|
| **Location** | `cc_s-core/deployment/xverse/docker_setup/` |
| **Type** | Docker Compose deployment |
| **Owner** | Cruise Control team |
| **Purpose** | Run S-CORE stack in container |

---

## X-Verse Container Contents

```
┌─────────────────────────────────────────────────────────┐
│                    X-Verse Container                     │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │car_simulation│  │   someipd    │  │   gatewayd   │  │
│  │              │  │              │  │              │  │
│  │ Speed, RPM,  │  │  vSomeIP     │  │   mw::com    │  │
│  │ Brake, Temp  │  │  Router      │  │   Gateway    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └────────┬────────┴─────────┬────────┘          │
│                  │                  │                    │
│         UDP :30509 (SOME/IP)   LoLa IPC (/dev/shm)     │
│                  │                  │                    │
│  ┌───────────────┴──────────────────┴───────────────┐  │
│  │              cruise_control_main                  │  │
│  │                                                   │  │
│  │  PID Controller + Fault Detection + DTC Storage  │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                               │
└──────────────────────────┼───────────────────────────────┘
                           │
                     TCP :7700
                           │
                           ▼
              ┌────────────────────────┐
              │   Our Code (Bridge)    │
              └────────────────────────┘
```

---

## X-Verse Files

| File | Purpose |
|------|---------|
| `docker-compose.yaml` | Container orchestration |
| `Dockerfile` | Container image definition |
| `entrypoint.sh` | Container startup script |
| `vsomeip.json` | vSomeIP main configuration |
| `vsomeip-local.json` | Local vSomeIP config |
| `vsomeip-router.json` | Router configuration |

---

## X-Verse Components

### 1. car_simulation

| Attribute | Details |
|-----------|---------|
| **Purpose** | Simulate vehicle physics |
| **Outputs** | Speed, RPM, Brake position, Temperature |
| **Protocol** | SOME/IP events |
| **Port** | UDP :30509 |

### 2. someipd (vSomeIP)

| Attribute | Details |
|-----------|---------|
| **Version** | vSomeIP 3.6.1 |
| **Purpose** | SOME/IP message routing |
| **Config** | `vsomeip.json` |
| **Sockets** | `/tmp/vsomeip-*` |

### 3. gatewayd (mw::com)

| Attribute | Details |
|-----------|---------|
| **Purpose** | S-CORE middleware gateway |
| **IPC** | LoLa (shared memory) |
| **External Port** | TCP :7700 |
| **Internal** | `/dev/shm` |

### 4. cruise_control_main

| Attribute | Details |
|-----------|---------|
| **Purpose** | Cruise control application |
| **Features** | PID controller, fault detection, DTC storage |
| **Input** | Speed signal from gatewayd |
| **Output** | Throttle commands, fault reports |

---

## Network Configuration

| Port | Protocol | Purpose |
|------|----------|---------|
| UDP :30509 | SOME/IP | Car simulation events |
| TCP :7700 | mw::com | Gateway external access |
| `/tmp/vsomeip-*` | Unix socket | vSomeIP IPC |
| `/dev/shm` | Shared memory | LoLa IPC |

---

## Docker Compose Structure

```yaml
version: '3.8'
services:
  xverse:
    build: .
    network_mode: host      # Uses host networking
    volumes:
      - /tmp:/tmp           # vSomeIP sockets
      - /dev/shm:/dev/shm   # LoLa shared memory
    ports:
      - "7700:7700"         # mw::com gateway
      - "30509:30509/udp"   # SOME/IP
```

---

## Integration Point for Our Code

Our code connects to X-Verse at **TCP :7700**:

```
X-Verse (gatewayd)          Our Code
      │                         │
      │    TCP :7700            │
      │◄───────────────────────►│
      │                         │
      │  mw::com messages       │
      │  (speed, faults, etc)   │
      │                         │
```

### What Our Code Receives

| Signal | Type | Source |
|--------|------|--------|
| `current_speed` | f64 | car_simulation |
| `target_speed` | f64 | cruise_control |
| `throttle` | f64 | cruise_control |
| `fault_status` | DtcStatus | cruise_control |

---

## Why X-Verse Matters

| Reason | Impact |
|--------|--------|
| Provides S-CORE stack | We don't have to build S-CORE |
| Already tested | Cruise team verified it works |
| Matches production | Real S-CORE architecture |
| Easy to run | Just `docker-compose up` |

---

## Our Responsibility

| Component | Owner | What We Do |
|-----------|-------|------------|
| X-Verse container | Cruise Team | Use as-is |
| cruise_bridge | Us | Connect to TCP :7700 |
| cruise_diag | Us | Monitor faults |
| sovd_adapter | Us | Expose to OpenSOVD |
| Dashboard | Us | Display data |

---

## Run Commands

```bash
# Start X-Verse
cd cc_s-core/deployment/xverse/docker_setup
docker-compose up -d

# Verify it's running
docker ps
netstat -an | grep 7700

# View logs
docker-compose logs -f
```

---

*Analysis prepared for Eclipse SDV Hackathon 2026*
*This is PRE-WORK research only - no code written*
