# Eclipse SDV Hackathon 2026 - Contribution Files Reference

## Overview

| Contribution | Repository | Lines | Files |
|--------------|------------|-------|-------|
| **PR #16** (sovd_adapter) | eclipse-score/inc_diagnostics | ~900 | 15+ |
| **Issue #553** (8 API fixes) | eclipse-opensovd/opensovd-core | ~770 | 25+ |
| **CDA #543** (Bug fix) | eclipse-opensovd/classic-diagnostic-adapter | ~230 | 2 |
| **Demo** (Cruise Control) | Our repository | ~800 | 30+ |
| **Total** | | **~3,870** | **70+** |

---

## 1. PR #16: sovd_adapter (S-CORE ↔ OpenSOVD Bridge)

**Location:** `third_party/inc_diagnostics/`

### Core Rust Files

| File | Path | Lines | Description | Key Functions |
|------|------|-------|-------------|---------------|
| **sovd_adapter.rs** | `score/mw/diag/sovd_adapter/src/lib.rs` | ~300 | Main adapter implementation | `SovdAdapter::new()`, `register_component()`, `handle_request()` |
| **data_provider.rs** | `score/mw/diag/sovd_adapter/src/data_provider.rs` | ~200 | DataProvider trait impl | `get_data()`, `set_data()`, `list_resources()` |
| **fault_provider.rs** | `score/mw/diag/sovd_adapter/src/fault_provider.rs` | ~150 | Fault/DTC provider | `get_faults()`, `clear_fault()`, `get_status()` |
| **component.rs** | `score/mw/diag/sovd_adapter/src/component.rs` | ~100 | Component registration | `Component::new()`, `add_data_resource()` |
| **types.rs** | `score/mw/diag/sovd_adapter/src/types.rs` | ~80 | Type definitions | `DtcStatus`, `FaultEntry`, `DataValue` |
| **error.rs** | `score/mw/diag/sovd_adapter/src/error.rs` | ~70 | Error handling | `AdapterError`, `Result<T>` |

### Build Configuration

| File | Path | Description |
|------|------|-------------|
| **Cargo.toml** | `score/mw/diag/sovd_adapter/Cargo.toml` | Rust dependencies |
| **BUILD.bazel** | `score/mw/diag/sovd_adapter/BUILD.bazel` | Bazel build rules |
| **lib.rs** | `score/mw/diag/sovd_adapter/src/lib.rs` | Module exports |

### C++ Headers (diag_api)

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **diag_api.h** | `score/mw/diag/api/diag_api.h` | ~150 | Main diagnostic API |
| **data_resource.h** | `score/mw/diag/api/data_resource.h` | ~80 | Data resource interface |
| **fault_sink.h** | `score/mw/diag/api/fault_sink.h` | ~60 | Fault sink interface |
| **diag_result.h** | `score/mw/diag/diag_result.h` | ~40 | Result types |
| **byte_types.h** | `score/mw/diag/byte_types.h` | ~30 | Byte type definitions |

---

## 2. Issue #553: OpenSOVD API Fixes (8 Compliance Issues)

**Location:** `third_party/opensovd-core/`

### Fixed Files

| # | File | Path | Fix Description | ISO Reference |
|---|------|------|-----------------|---------------|
| 1 | **data.rs** | `opensovd-core/src/data.rs` | Mode.value mandatory | ISO 17978-3 §7.4 |
| 2 | **bulkdata.rs** | `opensovd-core/src/bulkdata.rs` | Category enum fix | ISO 17978-3 §8.2 |
| 3 | **discovery.rs** | `opensovd-core/src/discovery.rs` | Discovery endpoint | ISO 17978-3 §6.1 |
| 4 | **component.rs** | `opensovd-server/src/routes/entities/component.rs` | Restart endpoint | ISO 17978-3 §7.8 |
| 5 | **area.rs** | `opensovd-server/src/routes/entities/area.rs` | Area listing fix | ISO 17978-3 §7.2 |
| 6 | **app.rs** | `opensovd-server/src/routes/entities/app.rs` | App metadata | ISO 17978-3 §7.3 |
| 7 | **error.rs** | `opensovd-server/src/routes/error.rs` | Error response format | ISO 17978-3 §9.1 |
| 8 | **version.rs** | `opensovd-server/src/routes/version.rs` | Version endpoint | ISO 17978-3 §6.2 |

### Core Library Files

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **lib.rs** | `opensovd-core/src/lib.rs` | ~100 | Core library exports |
| **topology.rs** | `opensovd-core/src/topology.rs` | ~80 | Topology management |
| **entity/mod.rs** | `opensovd-core/src/entity/mod.rs` | ~50 | Entity module |
| **entity/component.rs** | `opensovd-core/src/entity/component.rs` | ~120 | Component entity |
| **entity/area.rs** | `opensovd-core/src/entity/area.rs` | ~80 | Area entity |
| **entity/app.rs** | `opensovd-core/src/entity/app.rs` | ~60 | App entity |

### Server Implementation

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **server.rs** | `opensovd-server/src/server.rs` | ~150 | HTTP server |
| **auth.rs** | `opensovd-server/src/auth.rs` | ~100 | Authentication |
| **tls.rs** | `opensovd-server/src/tls.rs` | ~80 | TLS configuration |
| **schema.rs** | `opensovd-server/src/schema.rs` | ~60 | JSON schema |
| **body.rs** | `opensovd-server/src/body.rs` | ~40 | Request body handling |

### Data Models

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **types.rs** | `opensovd-models/src/types.rs` | ~100 | Type definitions |
| **error.rs** | `opensovd-models/src/error.rs` | ~60 | Error models |
| **version.rs** | `opensovd-models/src/version.rs` | ~40 | Version info |
| **discovery.rs** | `opensovd-models/src/discovery.rs` | ~50 | Discovery models |
| **data.rs** | `opensovd-models/src/data.rs` | ~80 | Data models |
| **bulkdata.rs** | `opensovd-models/src/bulkdata.rs` | ~70 | Bulk data models |

### Data Providers

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **resource.rs** | `opensovd-providers/src/data/resource.rs` | ~120 | Resource provider |
| **constant.rs** | `opensovd-providers/src/data/constant.rs` | ~60 | Constant data |
| **builder.rs** | `opensovd-providers/src/data/builder.rs` | ~80 | Builder pattern |
| **mod.rs** | `opensovd-providers/src/data/mod.rs` | ~30 | Module exports |

---

## 3. CDA #543: Bug Fix (Result vs Option)

**Location:** `classic-diagnostic-adapter/`

| File | Path | Lines | Fix Description |
|------|------|-------|-----------------|
| **adapter.rs** | `src/adapter.rs` | ~180 | Changed `Option<T>` to `Result<T, E>` for proper error handling |
| **lib.rs** | `src/lib.rs` | ~50 | Updated exports |

**Before:**
```rust
fn get_dtc(&self) -> Option<DtcInfo>
```

**After:**
```rust
fn get_dtc(&self) -> Result<DtcInfo, AdapterError>
```

---

## 4. Demo: Cruise Control Diagnostics

**Location:** `demo/` and `EclipseHackthon2026/demo/`

### Dashboard (Layer 6)

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **index.html** | `demo/live/index.html` | ~200 | Dashboard UI |
| **server.py** | `demo/live/server.py` | ~150 | HTTP server for dashboard |
| **template.html** | `demo/replay/template.html` | ~100 | Replay template |
| **build.py** | `demo/replay/build.py` | ~80 | Build script |

### Rust Gateway Crates

| Crate | Path | Files | Description |
|-------|------|-------|-------------|
| **cruise-gateway** | `demo/gateway/crates/cruise-gateway/` | 3 | Main gateway binary |
| **cruise_diag** | `demo/gateway/crates/cruise_diag/` | 2 | Fault monitoring |
| **cruise_sim** | `demo/gateway/crates/cruise_sim/` | 2 | Cruise simulation |
| **sovd_adapter** | `demo/X-Verse/external_hackathon_ecus/OpenSOVD/gateway/harness/crates/sovd_adapter/` | 1 | SOVD adapter crate |
| **diag_api** | `demo/X-Verse/external_hackathon_ecus/OpenSOVD/gateway/harness/crates/diag_api/` | 1 | Diagnostic API |
| **diag_json** | `demo/X-Verse/external_hackathon_ecus/OpenSOVD/gateway/harness/crates/diag_json/` | 2 | JSON serialization |
| **data_resource** | `demo/X-Verse/external_hackathon_ecus/OpenSOVD/gateway/harness/crates/data_resource/` | 1 | Data resources |

#### Key Rust Files

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **main.rs** | `cruise-gateway/src/main.rs` | ~150 | Gateway entry point |
| **bridge_link.rs** | `cruise-gateway/src/bridge_link.rs` | ~100 | mw::com bridge |
| **lib.rs** | `cruise_diag/src/lib.rs` | ~200 | Fault detection & DTC |
| **lib.rs** | `cruise_sim/src/lib.rs` | ~100 | Simulation interface |
| **lib.rs** | `diag_json/src/lib.rs` | ~80 | JSON handling |

### S-CORE Bridge (C++/Rust)

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **cruise_bridge.rs** | `demo/score/sdv_cruise/cruise_bridge.rs` | ~150 | Rust mw::com consumer |
| **cruise_api.rs** | `demo/score/sdv_cruise/cruise_api.rs` | ~100 | Cruise API bindings |
| **cruise_api.cpp** | `demo/score/sdv_cruise/cruise_api.cpp` | ~80 | C++ API impl |
| **cruise_ecu.cpp** | `demo/score/sdv_cruise/cruise_ecu.cpp` | ~120 | ECU simulation |
| **cruise_types.h** | `demo/score/sdv_cruise/cruise_types.h` | ~50 | Type definitions |
| **BUILD.bazel** | `demo/score/sdv_cruise/BUILD.bazel` | ~40 | Build rules |

### Cruise Control App (cc-app)

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **main.cpp** | `cc-app/src/main.cpp` | ~100 | Entry point |
| **cruise_control.cpp** | `cc-app/src/cruise_control.cpp` | ~200 | PID controller |
| **cruise_control.h** | `cc-app/src/cruise_control.h` | ~60 | Header |
| **dtc_backend.cpp** | `cc-app/src/dtc_backend.cpp` | ~150 | DTC storage |
| **dtc_backend.h** | `cc-app/src/dtc_backend.h` | ~40 | Header |
| **vehicle_sim.cpp** | `cc-app/src/vehicle_sim.cpp` | ~120 | Vehicle simulation |
| **vehicle_sim.h** | `cc-app/src/vehicle_sim.h` | ~30 | Header |
| **handover_client.cpp** | `cc-app/src/handover_client.cpp` | ~100 | Handover logic |
| **handover_client.h** | `cc-app/src/handover_client.h` | ~30 | Header |
| **wheel_check.cpp** | `cc-app/src/wheel_check.cpp` | ~80 | Wheel speed check |
| **wheel_check.h** | `cc-app/src/wheel_check.h** | ~20 | Header |
| **codec.cpp** | `cc-app/src/codec.cpp` | ~60 | Message codec |
| **codec.h** | `cc-app/src/codec.h` | ~25 | Header |
| **types.h** | `cc-app/src/types.h` | ~40 | Type definitions |

### Tests

| File | Path | Lines | Description |
|------|------|-------|-------------|
| **cruise_control_test.cpp** | `cc-app/test/cruise_control_test.cpp` | ~150 | PID tests |
| **dtc_backend_test.cpp** | `cc-app/test/dtc_backend_test.cpp` | ~100 | DTC tests |
| **vehicle_sim_test.cpp** | `cc-app/test/vehicle_sim_test.cpp` | ~80 | Simulation tests |
| **handover_client_test.cpp** | `cc-app/test/handover_client_test.cpp` | ~60 | Handover tests |
| **wheel_check_test.cpp** | `cc-app/test/wheel_check_test.cpp` | ~50 | Wheel tests |
| **codec_test.cpp** | `cc-app/test/codec_test.cpp` | ~40 | Codec tests |

---

## 5. openDuT Configuration

| File | Path | Description |
|------|------|-------------|
| **peer.yaml** | `demo/opendut/peer.yaml` | Peer configuration |
| **cda-test-config.toml** | `demo/X-Verse/external_hackathon_ecus/OpenSOVD/cda/cda-test-config.toml` | CDA test config |

---

## File Categories Summary

### By Language

| Language | Files | Lines | Purpose |
|----------|-------|-------|---------|
| **Rust (.rs)** | ~45 | ~2,500 | Core logic, adapters, servers |
| **C++ (.cpp/.h)** | ~20 | ~800 | ECU, mw::com bridge, tests |
| **Python (.py)** | ~8 | ~300 | Servers, build scripts |
| **HTML/JS** | ~4 | ~200 | Dashboard |
| **YAML/TOML** | ~5 | ~70 | Configuration |

### By Component

| Component | Files | Description |
|-----------|-------|-------------|
| **sovd_adapter** | 8 | S-CORE to OpenSOVD bridge |
| **opensovd-core fixes** | 15 | API compliance |
| **cruise_diag** | 4 | Fault monitoring |
| **cruise_bridge** | 5 | mw::com consumer |
| **cc-app** | 14 | Cruise Control ECU |
| **Dashboard** | 4 | Web UI |
| **Tests** | 12 | Unit/integration tests |
| **Config** | 3 | Build/deployment config |

---

## Key Code Patterns

### 1. DataProvider Trait (Rust)

```rust
// sovd_adapter/src/data_provider.rs
pub trait DataProvider: Send + Sync {
    fn get_data(&self, id: &str) -> Result<DataValue, Error>;
    fn set_data(&self, id: &str, value: DataValue) -> Result<(), Error>;
    fn list_resources(&self) -> Vec<DataResourceInfo>;
}
```

### 2. Fault Detection (Rust)

```rust
// cruise_diag/src/lib.rs
pub struct FaultMonitor {
    debounce_confirm: Duration,  // 5000ms
    debounce_heal: Duration,     // 2000ms
    dtc_storage: Vec<DtcEntry>,
}

impl FaultMonitor {
    pub fn check_signal(&mut self, signal: Option<f64>) -> FaultState {
        // Debounce logic here
    }
}
```

### 3. PID Controller (C++)

```cpp
// cc-app/src/cruise_control.cpp
class CruiseController {
    float Kp = 0.25f;
    float Ki = 0.03f;
    float Kd = 0.12f;

    float compute(float current_speed, float target_speed) {
        // PID calculation
    }
};
```

### 4. mw::com Bridge (Rust)

```rust
// cruise_bridge.rs
pub struct MwComBridge {
    proxy: CruiseControlProxy,
}

impl MwComBridge {
    pub async fn subscribe_speed(&self) -> impl Stream<Item = f64> {
        // Subscribe to speed events
    }
}
```

---

## Build Commands

```bash
# Build sovd_adapter (PR #16)
cd third_party/inc_diagnostics
cargo build --release -p sovd_adapter

# Build opensovd-core (Issue #553)
cd third_party/opensovd-core
cargo build --release

# Build cruise-gateway (Demo)
cd demo/X-Verse/external_hackathon_ecus/OpenSOVD/gateway/harness
cargo build --release

# Build cc-app (Cruise Control)
cd cc-app
bazel build //cc-app:cruise_control

# Run tests
cargo test --workspace
bazel test //cc-app/test:all
```

---

## Data Flow Through Files

```
Car Simulation (cruise_ecu.cpp)
       ↓
   SOME/IP
       ↓
someipd (S-CORE upstream)
       ↓
gatewayd (S-CORE upstream)
       ↓
cruise_bridge.rs ← OUR CODE
       ↓
cruise_diag/lib.rs ← OUR CODE (Fault detection)
       ↓
sovd_adapter/lib.rs ← OUR CODE (PR #16)
       ↓
opensovd-server ← FIXED (Issue #553)
       ↓
Dashboard (index.html) ← OUR CODE
```

---

*Document prepared for Eclipse SDV Hackathon 2026*
