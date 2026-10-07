# SWE.1 Software Requirements Specification

| Document ID | INC-DIAG-16-SWE1-REQ |
|-------------|----------------------|
| Issue | #16 |
| Component | sovd_adapter |
| Date | 2026-10-07 |

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for the `sovd_adapter` crate, which bridges S-CORE `diag_api::DataResource` instances to the OpenSOVD gateway via `opensovd_core::DataProvider`.

### 1.2 Scope
The adapter enables diagnostic data resources to be served over SOVD/REST without requiring application code changes.

### 1.3 References
- Issue #16: Adapter: expose diag_api::DataResource as opensovd_core::DataProvider
- PR #6: Gateway CDA Integration (base branch)
- opensovd_core DataProvider trait specification
- diag_api DataResource trait specification

---

## 2. Functional Requirements

### 2.1 Resource Registration

| REQ-ID | REQ-REG-001 |
|--------|-------------|
| Title | Resource Registration API |
| Description | The adapter SHALL provide a `DataResourceRegistry` to register `diag_api::DataResource` instances with their metadata |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-REG-002 |
|--------|-------------|
| Title | Duplicate ID Detection |
| Description | The registry SHALL reject registration of resources with duplicate IDs |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-REG-003 |
|--------|-------------|
| Title | Empty ID Rejection |
| Description | The registry SHALL reject registration of resources with empty IDs |
| Priority | Medium |
| Verification | Unit Test |

| REQ-ID | REQ-REG-004 |
|--------|-------------|
| Title | Registration Order Preservation |
| Description | The registry SHALL preserve the order of resource registration for listings |
| Priority | Medium |
| Verification | Unit Test |

### 2.2 DataProvider Implementation

| REQ-ID | REQ-PROV-001 |
|--------|--------------|
| Title | List Resources |
| Description | The provider SHALL implement `list()` returning metadata for all registered resources |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-PROV-002 |
|--------|--------------|
| Title | Filter by Category |
| Description | The provider SHALL support filtering resources by category |
| Priority | Medium |
| Verification | Unit Test |

| REQ-ID | REQ-PROV-003 |
|--------|--------------|
| Title | Filter by Group |
| Description | The provider SHALL support filtering resources by group |
| Priority | Medium |
| Verification | Unit Test |

| REQ-ID | REQ-PROV-004 |
|--------|--------------|
| Title | Read Resource |
| Description | The provider SHALL implement `read(data_id, include_schema)` dispatching to the underlying `DataResource::read` |
| Priority | High |
| Verification | Integration Test |

| REQ-ID | REQ-PROV-005 |
|--------|--------------|
| Title | Write Resource |
| Description | The provider SHALL implement `write(data_id, value)` dispatching to the underlying `DataResource::write` |
| Priority | High |
| Verification | Integration Test |

| REQ-ID | REQ-PROV-006 |
|--------|--------------|
| Title | Read-Only Enforcement |
| Description | The provider SHALL reject writes to resources marked as read-only |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-PROV-007 |
|--------|--------------|
| Title | Not Found Error |
| Description | The provider SHALL return `DataError::NotFound` for unknown resource IDs |
| Priority | High |
| Verification | Unit Test |

### 2.3 Payload Format Support

| REQ-ID | REQ-FMT-001 |
|--------|-------------|
| Title | JSON Payload Support |
| Description | The adapter SHALL support JSON payloads with optional schema |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-FMT-002 |
|--------|-------------|
| Title | UTF-8 Payload Support |
| Description | The adapter SHALL support UTF-8 text payloads served as JSON strings |
| Priority | Medium |
| Verification | Unit Test |

| REQ-ID | REQ-FMT-003 |
|--------|-------------|
| Title | Binary Payload Support |
| Description | The adapter SHALL support binary payloads served as hex strings |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-FMT-004 |
|--------|-------------|
| Title | UDS Adapter Compatibility |
| Description | UDS adapters (RDBI/WDBI) SHALL work without additional code when registered with Binary format |
| Priority | High |
| Verification | Unit Test |

### 2.4 Error Handling

| REQ-ID | REQ-ERR-001 |
|--------|-------------|
| Title | SOVD Error Mapping |
| Description | The adapter SHALL map `diag_api::Error` SOVD codes to `opensovd_core::DataError` |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-ERR-002 |
|--------|-------------|
| Title | UDS NRC Mapping |
| Description | The adapter SHALL map UDS Negative Response Codes to `DataError::Internal` with hex code |
| Priority | Medium |
| Verification | Unit Test |

### 2.5 Async Handle Resolution

| REQ-ID | REQ-ASYNC-001 |
|--------|---------------|
| Title | Ready Handle Resolution |
| Description | The adapter SHALL resolve `ReadValueHandle::Ready` synchronously |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-ASYNC-002 |
|--------|---------------|
| Title | Pending Handle Resolution |
| Description | The adapter SHALL await `ReadValueHandle::Pending` futures |
| Priority | High |
| Verification | Unit Test |

| REQ-ID | REQ-ASYNC-003 |
|--------|---------------|
| Title | Closure Handle Resolution |
| Description | The adapter SHALL execute closures wrapped in Pending handles |
| Priority | Medium |
| Verification | Unit Test |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| REQ-ID | REQ-PERF-001 |
|--------|--------------|
| Title | Lock Scope |
| Description | The Mutex lock on resources SHALL NOT be held across await points |
| Priority | High |
| Verification | Code Review |

### 3.2 Compatibility

| REQ-ID | REQ-COMPAT-001 |
|--------|----------------|
| Title | Rust Edition |
| Description | The adapter SHALL compile with Rust 2021 edition |
| Priority | High |
| Verification | Build Test |

| REQ-ID | REQ-COMPAT-002 |
|--------|----------------|
| Title | Bazel Build |
| Description | The adapter SHALL build with Bazel rules_rust |
| Priority | High |
| Verification | Build Test |

---

## 4. Traceability Matrix

| Requirement | Design | Test |
|-------------|--------|------|
| REQ-REG-001 | registry.rs | register_keeps_insertion_order |
| REQ-REG-002 | registry.rs | register_rejects_duplicate_id |
| REQ-REG-003 | registry.rs | register_rejects_empty_id |
| REQ-REG-004 | registry.rs | register_keeps_insertion_order |
| REQ-PROV-001 | provider.rs | list_all_in_registration_order |
| REQ-PROV-002 | provider.rs | list_filters_by_category_and_group |
| REQ-PROV-003 | provider.rs | list_filters_by_category_and_group |
| REQ-PROV-004 | provider.rs | read_value_and_schema_on_request |
| REQ-PROV-005 | provider.rs | write_reaches_the_resource |
| REQ-PROV-006 | provider.rs | write_read_only_is_rejected |
| REQ-PROV-007 | provider.rs | read_unknown_id_is_not_found |
| REQ-FMT-001 | convert.rs | reply_value_per_payload_kind |
| REQ-FMT-002 | convert.rs | reply_value_per_payload_kind |
| REQ-FMT-003 | convert.rs | reply_value_per_payload_kind |
| REQ-FMT-004 | provider.rs | uds_adapter_served_without_extra_code |
| REQ-ERR-001 | convert.rs | read_error_formats_sovd_and_uds |
| REQ-ERR-002 | convert.rs | read_error_formats_sovd_and_uds |
| REQ-ASYNC-001 | handle.rs | read_ready |
| REQ-ASYNC-002 | handle.rs | read_future |
| REQ-ASYNC-003 | handle.rs | read_closure |

---

*Prepared by: EP1991 | Thinking_CAPs | Eclipse SDV Hackathon Chapter 4 2026*
