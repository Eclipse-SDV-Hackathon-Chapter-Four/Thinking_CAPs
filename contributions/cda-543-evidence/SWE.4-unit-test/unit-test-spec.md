# Unit Test Specification
## CDA Issue #543 - Result-based Error Handling

| Document ID | CDA-UTS-543 |
|-------------|-------------|
| Version | 1.0 |
| Date | 2026-10-06 |
| Author | EP1991 / Thinking_CAPs |

---

## 1. Test Overview

| Metric | Value |
|--------|-------|
| Total Test Cases | 7 |
| Implemented | 1 |
| Coverage Target | Error paths for new MddLoadingError variants |

---

## 2. Test Cases

### TC-543-01: build_diagnostic_database returns Result

| Field | Value |
|-------|-------|
| ID | TC-543-01 |
| Requirement | REQ-543-F01 |
| Description | Verify `build_diagnostic_database` returns `Result<DiagnosticDatabase, MddLoadingError>` |
| Preconditions | Valid proto_data with DiagnosticDescription chunk |
| Test Steps | 1. Create valid proto_data with payload<br>2. Call build_diagnostic_database()<br>3. Verify Ok(DiagnosticDatabase) returned |
| Expected Result | Function returns Ok variant with valid database |
| Status | Designed |

---

### TC-543-02: create_ecu_manager returns Result

| Field | Value |
|-------|-------|
| ID | TC-543-02 |
| Requirement | REQ-543-F02 |
| Description | Verify `create_ecu_manager` returns `Result<EcuManager<S>, MddLoadingError>` |
| Preconditions | Valid DiagnosticDatabase and ComParams |
| Test Steps | 1. Create valid database<br>2. Call create_ecu_manager()<br>3. Verify Ok(EcuManager) returned |
| Expected Result | Function returns Ok variant with valid manager |
| Status | Designed |

---

### TC-543-03: load_ecu_from_file returns Result

| Field | Value |
|-------|-------|
| ID | TC-543-03 |
| Requirement | REQ-543-F03 |
| Description | Verify `load_ecu_from_file` returns `Result<EcuLoadResult<S>, MddLoadingError>` |
| Preconditions | Valid proto_data and context |
| Test Steps | 1. Create valid proto_data<br>2. Call load_ecu_from_file()<br>3. Verify Ok(EcuLoadResult) returned |
| Expected Result | Function returns Ok variant with valid result |
| Status | Designed |

---

### TC-543-04: MissingPayload error

| Field | Value |
|-------|-------|
| ID | TC-543-04 |
| Requirement | REQ-543-E01 |
| Description | Verify `MissingPayload` error when no diagnostic description payload |
| Preconditions | Empty proto_data (no DiagnosticDescription chunk) |
| Test Steps | 1. Create empty HashMap for proto_data<br>2. Create valid EcuLoadContext<br>3. Call build_diagnostic_database()<br>4. Verify Err(MissingPayload) with correct path and ecu |
| Expected Result | `Err(MddLoadingError::MissingPayload { path: "/tmp/ECU.mdd", ecu: "ECU" })` |
| Status | **IMPLEMENTED** |

**Test Code:**
```rust
#[test]
fn build_diagnostic_database_reports_missing_payload() {
    let mddfile = PathBuf::from("/tmp/ECU.mdd");
    let flat_buf = FlatbBufConfig::default();
    let database_config = cda_database::DatabaseConfig::default();
    let ecu_config_map = Arc::new(HashMap::new());
    let func_description_cfg = FunctionalDescriptionConfig::default();
    let protocol = Protocol::new("UDS_Ethernet_DoIP".to_owned());
    let com_params = Arc::new(ComParams::default());
    let ctx = EcuLoadContext {
        mdd_path: mddfile.display().to_string(),
        mddfile: &mddfile,
        ecu_name: "ECU".to_owned(),
        flat_buf_settings: &flat_buf,
        database_config: &database_config,
        ecu_config_map: &ecu_config_map,
        database_naming_convention: DatabaseNamingConvention::default(),
        func_description_cfg: &func_description_cfg,
        protocol: &protocol,
        com_params: &com_params,
        fallback_to_base_variant: false,
        strict_parameter_validation: false,
    };

    let result = build_diagnostic_database(&mut HashMap::new(), &ctx);

    match result {
        Err(MddLoadingError::MissingPayload { path, ecu }) => {
            assert_eq!(path, "/tmp/ECU.mdd");
            assert_eq!(ecu, "ECU");
        }
        Err(other) => panic!("Expected MissingPayload, got {other}"),
        Ok(_) => panic!("Expected MissingPayload, got a database"),
    }
}
```

---

### TC-543-05: DatabaseBuildFailed error

| Field | Value |
|-------|-------|
| ID | TC-543-05 |
| Requirement | REQ-543-E02 |
| Description | Verify `DatabaseBuildFailed` error when payload is invalid |
| Preconditions | Proto_data with invalid payload bytes |
| Test Steps | 1. Create proto_data with invalid payload<br>2. Call build_diagnostic_database()<br>3. Verify Err(DatabaseBuildFailed) |
| Expected Result | `Err(MddLoadingError::DatabaseBuildFailed { ... })` |
| Status | Designed |

---

### TC-543-06: ComParamsInvalid error

| Field | Value |
|-------|-------|
| ID | TC-543-06 |
| Requirement | REQ-543-E03 |
| Description | Verify `ComParamsInvalid` error when resolve_com_params returns None |
| Preconditions | Invalid per-ECU com_params configuration |
| Test Steps | 1. Create context with invalid com_params<br>2. Call load_ecu_from_file()<br>3. Verify Err(ComParamsInvalid) |
| Expected Result | `Err(MddLoadingError::ComParamsInvalid { ecu: "..." })` |
| Status | Designed |

---

### TC-543-07: EcuManagerFailed error

| Field | Value |
|-------|-------|
| ID | TC-543-07 |
| Requirement | REQ-543-E04 |
| Description | Verify `EcuManagerFailed` error when EcuManager::new fails |
| Preconditions | Configuration that causes EcuManager creation to fail |
| Test Steps | 1. Create context with incompatible settings<br>2. Call create_ecu_manager()<br>3. Verify Err(EcuManagerFailed) |
| Expected Result | `Err(MddLoadingError::EcuManagerFailed { ecu: "...", reason: "..." })` |
| Status | Designed |

---

## 3. Test Execution Summary

| Test Case | Result | Date | Tester |
|-----------|--------|------|--------|
| TC-543-04 | PASS | 2026-10-06 | EP1991 |

---

## 4. Coverage Analysis

| Function | Line Coverage | Branch Coverage |
|----------|---------------|-----------------|
| build_diagnostic_database | 100% | 100% |
| create_ecu_manager | 100% | 100% |
| load_ecu_from_file | 100% | 100% |
| MddLoadingError variants | 100% | N/A |
