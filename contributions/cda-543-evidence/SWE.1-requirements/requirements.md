# Software Requirements Specification
## CDA Issue #543 - Result-based Error Handling in mdd.rs

| Document ID | CDA-SRS-543 |
|-------------|-------------|
| Version | 1.0 |
| Date | 2026-10-06 |
| Author | EP1991 / Thinking_CAPs |
| Status | Approved |

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for refactoring the MDD loading functions in the Classic Diagnostic Adapter (CDA) to use `Result<T, E>` instead of `Option<T>` for improved error handling and diagnostics.

### 1.2 Scope
The changes affect the `cda-main/src/mdd.rs` module, specifically the ECU database loading pipeline.

### 1.3 References
- GitHub Issue: https://github.com/eclipse-opensovd/classic-diagnostic-adapter/issues/543
- Rust Error Handling Best Practices
- ASPICE SWE.1 Process Requirements

---

## 2. Requirements

### 2.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| REQ-543-F01 | The `build_diagnostic_database` function SHALL return `Result<DiagnosticDatabase, MddLoadingError>` instead of `Option<DiagnosticDatabase>` | High | Implemented |
| REQ-543-F02 | The `create_ecu_manager` function SHALL return `Result<EcuManager<S>, MddLoadingError>` instead of `Option<EcuManager<S>>` | High | Implemented |
| REQ-543-F03 | The `load_ecu_from_file` function SHALL return `Result<EcuLoadResult<S>, MddLoadingError>` instead of `Option<EcuLoadResult<S>>` | High | Implemented |
| REQ-543-F04 | The system SHALL provide specific error variants for each failure mode | High | Implemented |
| REQ-543-F05 | Error messages SHALL include context (ECU name, file path) for debugging | Medium | Implemented |

### 2.2 Error Variant Requirements

| ID | Error Variant | Description | Context Fields |
|----|---------------|-------------|----------------|
| REQ-543-E01 | `MissingPayload` | No diagnostic description payload found in MDD | `path`, `ecu` |
| REQ-543-E02 | `DatabaseBuildFailed` | Failed to create database from payload | `path`, `ecu`, `reason` |
| REQ-543-E03 | `ComParamsInvalid` | Invalid per-ECU communication parameters | `ecu` |
| REQ-543-E04 | `EcuManagerFailed` | Failed to create ECU manager | `ecu`, `reason` |

### 2.3 Non-Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| REQ-543-NF01 | Error handling SHALL follow Rust idiomatic patterns using `?` operator | High | Implemented |
| REQ-543-NF02 | Changes SHALL maintain backward compatibility with existing callers | High | Implemented |
| REQ-543-NF03 | Code SHALL pass `cargo clippy` without warnings | Medium | Verified |
| REQ-543-NF04 | Code SHALL follow CDA code style guidelines (ASCII only, no banner comments) | Medium | Verified |

---

## 3. Traceability Matrix

| Requirement | Design Element | Test Case | Status |
|-------------|----------------|-----------|--------|
| REQ-543-F01 | `build_diagnostic_database()` | TC-543-01 | Pass |
| REQ-543-F02 | `create_ecu_manager()` | TC-543-02 | Pass |
| REQ-543-F03 | `load_ecu_from_file()` | TC-543-03 | Pass |
| REQ-543-E01 | `MddLoadingError::MissingPayload` | TC-543-04 | Pass |
| REQ-543-E02 | `MddLoadingError::DatabaseBuildFailed` | TC-543-05 | Pass |
| REQ-543-E03 | `MddLoadingError::ComParamsInvalid` | TC-543-06 | Pass |
| REQ-543-E04 | `MddLoadingError::EcuManagerFailed` | TC-543-07 | Pass |

---

## 4. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | EP1991 | 2026-10-06 | Approved |
| Reviewer | Thinking_CAPs Team | 2026-10-06 | Approved |
