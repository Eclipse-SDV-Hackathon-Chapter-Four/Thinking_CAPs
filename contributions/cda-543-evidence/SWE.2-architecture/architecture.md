# Software Architecture Design
## CDA Issue #543 - Result-based Error Handling

| Document ID | CDA-SAD-543 |
|-------------|-------------|
| Version | 1.0 |
| Date | 2026-10-06 |
| Author | EP1991 / Thinking_CAPs |

---

## 1. Overview

This document describes the architectural changes for implementing proper error handling in the MDD loading pipeline of the Classic Diagnostic Adapter (CDA).

## 2. Architecture Diagrams

### 2.1 Component Architecture
See: `architecture.puml`

### 2.2 Error Flow Sequence
See: `error-flow.puml`

## 3. Design Decisions

### 3.1 Error Type Selection

| Decision | Use `Result<T, MddLoadingError>` instead of `Option<T>` |
|----------|--------------------------------------------------------|
| Rationale | Provides specific error information for debugging and logging |
| Alternatives | Keep `Option<T>` with separate logging (rejected: loses error context) |
| Impact | All callers must handle specific error variants |

### 3.2 Error Variant Design

```rust
pub enum MddLoadingError {
    // Existing variants
    LoadFailed { path: String, reason: String },
    DecompressFailed { path: String, reason: String },

    // New variants (Issue #543)
    MissingPayload { path: String, ecu: String },
    DatabaseBuildFailed { path: String, ecu: String, reason: String },
    ComParamsInvalid { ecu: String },
    EcuManagerFailed { ecu: String, reason: String },
}
```

### 3.3 Error Propagation Strategy

| Pattern | Usage |
|---------|-------|
| `?` operator | Propagate errors from Result-returning functions |
| `.ok_or_else()` | Convert `Option<T>` to `Result<T, E>` |
| `.map_err()` | Transform error types with context |

## 4. Interface Changes

### 4.1 Before (Option-based)

```rust
fn build_diagnostic_database(...) -> Option<DiagnosticDatabase>
fn create_ecu_manager<S>(...) -> Option<EcuManager<S>>
fn load_ecu_from_file<S>(...) -> Option<EcuLoadResult<S>>
```

### 4.2 After (Result-based)

```rust
fn build_diagnostic_database(...) -> Result<DiagnosticDatabase, MddLoadingError>
fn create_ecu_manager<S>(...) -> Result<EcuManager<S>, MddLoadingError>
fn load_ecu_from_file<S>(...) -> Result<EcuLoadResult<S>, MddLoadingError>
```

## 5. Traceability

| Requirement | Design Element |
|-------------|----------------|
| REQ-543-F01 | `build_diagnostic_database()` signature change |
| REQ-543-F02 | `create_ecu_manager()` signature change |
| REQ-543-F03 | `load_ecu_from_file()` signature change |
| REQ-543-E01 | `MddLoadingError::MissingPayload` variant |
| REQ-543-E02 | `MddLoadingError::DatabaseBuildFailed` variant |
| REQ-543-E03 | `MddLoadingError::ComParamsInvalid` variant |
| REQ-543-E04 | `MddLoadingError::EcuManagerFailed` variant |
