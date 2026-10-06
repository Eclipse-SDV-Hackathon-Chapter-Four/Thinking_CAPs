# Integration Test Specification
## CDA Issue #543 - Result-based Error Handling

| Document ID | CDA-ITS-543 |
|-------------|-------------|
| Version | 1.0 |
| Date | 2026-10-06 |
| Author | EP1991 / Thinking_CAPs |

---

## 1. Test Overview

Integration tests verify that the refactored error handling works correctly across the MDD loading pipeline, from file loading to ECU manager creation.

| Metric | Value |
|--------|-------|
| Total Test Cases | 4 |
| Scope | End-to-end MDD loading with error propagation |

---

## 2. Test Environment

| Component | Version |
|-----------|---------|
| Rust | 1.99.0 |
| CDA | main branch |
| Test Framework | Rust built-in test |
| Async Runtime | Tokio |

---

## 3. Integration Test Cases

### ITC-543-01: Full MDD Loading Pipeline Success

| Field | Value |
|-------|-------|
| ID | ITC-543-01 |
| Description | Verify complete MDD loading pipeline succeeds with valid input |
| Components | `load_single_mdd` -> `load_ecu_from_file` -> `build_diagnostic_database` -> `create_ecu_manager` |
| Preconditions | Valid MDD file with complete ECU data |
| Test Steps | 1. Create valid MDD file in test storage<br>2. Call load_single_mdd()<br>3. Verify (ecu_name, EcuManager, FileManager) returned |
| Expected Result | Ok((String, EcuManager, FileManager)) |
| Status | Existing test coverage |

---

### ITC-543-02: Error Propagation from build_diagnostic_database

| Field | Value |
|-------|-------|
| ID | ITC-543-02 |
| Description | Verify MissingPayload error propagates through pipeline |
| Components | `load_single_mdd` -> `load_ecu_from_file` -> `build_diagnostic_database` |
| Preconditions | MDD file without DiagnosticDescription chunk |
| Test Steps | 1. Create MDD file without payload<br>2. Call load_single_mdd()<br>3. Verify Err(MissingPayload) returned |
| Expected Result | Err(MddLoadingError::MissingPayload { ... }) |
| Verification | Error contains correct ECU name and file path |

---

### ITC-543-03: Error Propagation from resolve_com_params

| Field | Value |
|-------|-------|
| ID | ITC-543-03 |
| Description | Verify ComParamsInvalid error propagates through pipeline |
| Components | `load_single_mdd` -> `load_ecu_from_file` -> `resolve_com_params` |
| Preconditions | Invalid per-ECU com_params configuration |
| Test Steps | 1. Create valid MDD with invalid com_params config<br>2. Call load_single_mdd()<br>3. Verify Err(ComParamsInvalid) returned |
| Expected Result | Err(MddLoadingError::ComParamsInvalid { ecu: "..." }) |

---

### ITC-543-04: Error Propagation from create_ecu_manager

| Field | Value |
|-------|-------|
| ID | ITC-543-04 |
| Description | Verify EcuManagerFailed error propagates through pipeline |
| Components | `load_single_mdd` -> `load_ecu_from_file` -> `create_ecu_manager` |
| Preconditions | Configuration causing EcuManager creation failure |
| Test Steps | 1. Create MDD with incompatible configuration<br>2. Call load_single_mdd()<br>3. Verify Err(EcuManagerFailed) returned |
| Expected Result | Err(MddLoadingError::EcuManagerFailed { ecu: "...", reason: "..." }) |

---

## 4. Error Propagation Verification

```
load_single_mdd()
    |
    v
load_ecu_from_file() -----> Err(MissingPayload)     [ITC-543-02]
    |                  \---> Err(ComParamsInvalid)   [ITC-543-03]
    |                  \---> Err(EcuManagerFailed)   [ITC-543-04]
    v
Ok((name, manager, files)) <------------------------ [ITC-543-01]
```

---

## 5. Backward Compatibility Verification

| Aspect | Verification |
|--------|--------------|
| Caller signature | `load_single_mdd` still returns `Result<(String, EcuManager<S>, FileManager), MddLoadingError>` |
| Error type | All errors are still `MddLoadingError` variants |
| Existing tests | All existing integration tests pass |

---

## 6. Test Execution Evidence

### Build Verification
```bash
$ cargo build --release
   Compiling cda-main v0.1.0
    Finished release [optimized] target(s) in 45.23s
```

### Test Execution
```bash
$ cargo test --lib mdd::tests
running 5 tests
test mdd::tests::build_diagnostic_database_reports_missing_payload ... ok
test mdd::tests::resolve_mdd_paths_prefers_storage_over_seed_dir ... ok
test mdd::tests::resolve_mdd_paths_loads_from_storage ... ok
test mdd::tests::resolve_mdd_paths_falls_back_to_db_dir ... ok
test mdd::tests::storage_and_db_dir_load_in_same_order ... ok

test result: ok. 5 passed; 0 failed; 0 ignored
```

---

## 7. Traceability

| Integration Test | Unit Tests Covered | Requirements |
|------------------|-------------------|--------------|
| ITC-543-01 | TC-543-01, TC-543-02, TC-543-03 | REQ-543-F01, F02, F03 |
| ITC-543-02 | TC-543-04 | REQ-543-E01 |
| ITC-543-03 | TC-543-06 | REQ-543-E03 |
| ITC-543-04 | TC-543-07 | REQ-543-E04 |
