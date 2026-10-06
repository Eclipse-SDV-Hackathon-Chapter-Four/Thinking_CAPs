# Detailed Design Document
## CDA Issue #543 - Result-based Error Handling in mdd.rs

| Document ID | CDA-DDD-543 |
|-------------|-------------|
| Version | 1.0 |
| Date | 2026-10-06 |
| Author | EP1991 / Thinking_CAPs |

---

## 1. Module: cda-main/src/mdd.rs

### 1.1 Error Enum Extension

**File:** `cda-main/src/mdd.rs`
**Lines:** 45-63

```rust
#[derive(Debug, thiserror::Error)]
pub enum MddLoadingError {
    // Existing variants
    #[error("Failed to load MDD {path}: {reason}")]
    LoadFailed { path: String, reason: String },

    #[error("Failed to decompress MDD {path}: {reason}")]
    DecompressFailed { path: String, reason: String },

    // NEW: Issue #543
    #[error("No diagnostic description payload for ECU {ecu} in MDD {path}")]
    MissingPayload { path: String, ecu: String },

    #[error("Failed to create database for ECU {ecu} from MDD {path}: {reason}")]
    DatabaseBuildFailed {
        path: String,
        ecu: String,
        reason: String,
    },

    #[error("Invalid per-ECU com_params for ECU {ecu}")]
    ComParamsInvalid { ecu: String },

    #[error("Failed to create ECU manager for ECU {ecu}: {reason}")]
    EcuManagerFailed { ecu: String, reason: String },
}
```

---

### 1.2 Function: build_diagnostic_database

**Purpose:** Extract and build the diagnostic database from proto data.

**Signature Change:**
```rust
// BEFORE
fn build_diagnostic_database(
    proto_data: &mut HashMap<ChunkType, Vec<Chunk>>,
    ctx: &EcuLoadContext<'_>,
) -> Option<cda_database::datatypes::DiagnosticDatabase>

// AFTER
fn build_diagnostic_database(
    proto_data: &mut HashMap<ChunkType, Vec<Chunk>>,
    ctx: &EcuLoadContext<'_>,
) -> Result<cda_database::datatypes::DiagnosticDatabase, MddLoadingError>
```

**Implementation Details:**

| Step | Before | After |
|------|--------|-------|
| Payload extraction | `.and_then()` chain with `or_else` logging | `.ok_or_else()` returning `MissingPayload` |
| Database creation | `.map_err()` with logging, `.ok()` | `.map_err()` returning `DatabaseBuildFailed` |

**Error Conditions:**
1. `MissingPayload` - When `ChunkType::DiagnosticDescription` is not found or has no payload
2. `DatabaseBuildFailed` - When `DiagnosticDatabase::new_from_bytes()` fails

---

### 1.3 Function: create_ecu_manager

**Purpose:** Create an ECU manager from diagnostic database and configuration.

**Signature Change:**
```rust
// BEFORE
fn create_ecu_manager<S: SecurityPlugin>(
    diag_database: cda_database::datatypes::DiagnosticDatabase,
    protocol: Protocol,
    ecu_type: EcuManagerType,
    effective_com_params: &ComParams,
    ctx: &EcuLoadContext<'_>,
) -> Option<EcuManager<S>>

// AFTER
fn create_ecu_manager<S: SecurityPlugin>(
    diag_database: cda_database::datatypes::DiagnosticDatabase,
    protocol: Protocol,
    ecu_type: EcuManagerType,
    effective_com_params: &ComParams,
    ctx: &EcuLoadContext<'_>,
) -> Result<EcuManager<S>, MddLoadingError>
```

**Error Conditions:**
1. `EcuManagerFailed` - When `EcuManager::new()` returns an error

---

### 1.4 Function: load_ecu_from_file

**Purpose:** Load and process a single ECU from MDD file.

**Signature Change:**
```rust
// BEFORE
fn load_ecu_from_file<S: SecurityPlugin>(
    proto_data: HashMap<ChunkType, Vec<Chunk>>,
    ctx: &EcuLoadContext<'_>,
    per_ecu_cfg: Option<&EcuConfig>,
) -> Option<EcuLoadResult<S>>

// AFTER
fn load_ecu_from_file<S: SecurityPlugin>(
    proto_data: HashMap<ChunkType, Vec<Chunk>>,
    ctx: &EcuLoadContext<'_>,
    per_ecu_cfg: Option<&EcuConfig>,
) -> Result<EcuLoadResult<S>, MddLoadingError>
```

**Call Flow:**
```
load_ecu_from_file
    |-> build_diagnostic_database()  -- ? operator
    |-> resolve_com_params()         -- .ok_or_else(ComParamsInvalid)
    |-> create_ecu_manager()         -- ? operator
    |-> extract_file_chunks()
    \-> Ok(EcuLoadResult)
```

---

### 1.5 Function: load_single_mdd (Caller Update)

**Change:** Simplified error handling

```rust
// BEFORE
let result = load_ecu_from_file(proto_data, &ctx, per_ecu_cfg).ok_or_else(|| {
    MddLoadingError::LoadFailed {
        path: mdd_path.clone(),
        reason: format!("Failed to load ECU {ecu_name} from MDD"),
    }
})?;

// AFTER
let result = load_ecu_from_file(proto_data, &ctx, per_ecu_cfg)?;
```

**Rationale:** Now that `load_ecu_from_file` returns a specific `MddLoadingError`, we no longer need to wrap it with a generic `LoadFailed` error.

---

## 2. Data Flow

```
MDD File
    |
    v
load_single_mdd()
    |
    +-- decompress (if needed)
    +-- load_proto_data()
    |
    v
load_ecu_from_file()
    |
    +-- build_diagnostic_database()
    |       |-> Result<DiagnosticDatabase, MissingPayload|DatabaseBuildFailed>
    |
    +-- resolve_com_params()
    |       |-> Option<ComParams> -> Result via ok_or_else(ComParamsInvalid)
    |
    +-- create_ecu_manager()
    |       |-> Result<EcuManager, EcuManagerFailed>
    |
    v
Result<EcuLoadResult, MddLoadingError>
```

---

## 3. Traceability

| Design Element | Requirement | Test Case |
|----------------|-------------|-----------|
| `MddLoadingError::MissingPayload` | REQ-543-E01 | TC-543-04 |
| `MddLoadingError::DatabaseBuildFailed` | REQ-543-E02 | TC-543-05 |
| `MddLoadingError::ComParamsInvalid` | REQ-543-E03 | TC-543-06 |
| `MddLoadingError::EcuManagerFailed` | REQ-543-E04 | TC-543-07 |
| `build_diagnostic_database()` | REQ-543-F01 | TC-543-01 |
| `create_ecu_manager()` | REQ-543-F02 | TC-543-02 |
| `load_ecu_from_file()` | REQ-543-F03 | TC-543-03 |
