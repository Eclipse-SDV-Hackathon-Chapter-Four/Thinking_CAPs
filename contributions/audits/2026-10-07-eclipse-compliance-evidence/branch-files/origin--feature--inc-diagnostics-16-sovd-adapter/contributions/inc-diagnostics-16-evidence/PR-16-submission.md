# PR #16 Submission Documentation

| Field | Value |
|-------|-------|
| Date | 2026-10-07 |
| Contributor | EP1991 / Thinking_CAPs |
| Hackathon | Eclipse SDV Hackathon Chapter 4 2026 |

---

## 1. Submission Target Confirmation

| Item | Value |
|------|-------|
| **Upstream Repository** | eclipse-score/inc_diagnostics |
| **Issue** | https://github.com/eclipse-score/inc_diagnostics/issues/16 |
| **Issue Title** | Adapter: expose diag_api::DataResource as opensovd_core::DataProvider |
| **Fork Repository** | EP1991/inc_diagnostics |
| **Branch** | feature/16-sovd-adapter-dataprovider |
| **Base Branch** | gateway_cda_int (PR #6) |

---

## 2. Contribution Requirements Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Eclipse Account | DONE | EP1991 registered |
| ECA Signed | DONE | Eclipse Contributor Agreement signed |
| Issue Claimed | DONE | Comment posted on #16 |
| Fork Created | DONE | EP1991/inc_diagnostics |
| Code Style Compliance | DONE | ASCII only, SPDX headers |
| Conventional Commits | DONE | `feat(sovd_adapter): ...` format |
| No AI Attribution | DONE | Clean commit message |

---

## 3. Implementation Summary

### 3.1 New Crate: sovd_adapter

| File | Lines | Purpose |
|------|-------|---------|
| `lib.rs` | 36 | Public API exports |
| `registry.rs` | 203 | Resource registration with metadata |
| `provider.rs` | 321 | DataProvider trait implementation |
| `convert.rs` | 260 | Type conversions diag_api <-> opensovd_core |
| `handle.rs` | 95 | Async handle resolution |
| `BUILD` | 54 | Bazel build rules |

**Total: 969 lines**

### 3.2 Key Types

```rust
// Registry for diag_api resources
pub struct DataResourceRegistry { ... }

// DataProvider implementation
pub struct SovdDataProvider { ... }

// Payload format for UDS adapters
pub enum PayloadFormat { Json, Utf8, Binary }
```

### 3.3 Gateway Integration (Cruise Control)

| File | Change |
|------|--------|
| `score/opensovd-gateway/BUILD` | +32 lines - add dependencies |
| `score/opensovd-gateway/src/cruise.rs` | +380 lines - Cruise control diagnostics |
| `score/opensovd-gateway/src/main.rs` | +97 / -27 lines - wire adapter |

### 3.4 Cruise Control Resources

| Resource | Category | Access | Description |
|----------|----------|--------|-------------|
| `vehicle_speed` | currentData | read | Vehicle speed sensor reading |
| `cruise_state` | currentData | read | Cruise control state (standby/active/unavailable) |
| `speed_sensor_fault_status` | currentData | read | Debounced fault status |
| `speed_sensor_stuck` | storedData | read/write | Fault injection control |

---

## 4. Commits

| # | Commit | Message |
|---|--------|---------|
| 1 | 378491c | feat(diag_api): re-export JsonSchemaRequired |
| 2 | a9af0a8 | feat(sovd_adapter): serve diag_api DataResources as an opensovd DataProvider |
| 3 | 4a5c470 | feat(opensovd-gateway): serve cruise control diag_api resources instead of demo data |

---

## 5. Acceptance Criteria (from Issue #16)

| Criteria | Status |
|----------|--------|
| DataResource registered through adapter is readable/writable over SOVD/REST | DONE |
| UDS-backed resources served without extra code | DONE |
| Categories/groups/tags reflect DataResourceMetadata | DONE |
| Tests in sovd_adapter and gateway | DONE |

---

## 6. Test Coverage

### 6.1 sovd_adapter Tests

| Test | Description |
|------|-------------|
| `metadata_maps_every_field` | Verify metadata conversion |
| `encoding_follows_format_and_schema_flag` | Reply encoding selection |
| `reply_value_per_payload_kind` | JSON/UTF8/Binary handling |
| `request_payload_per_format` | Write payload conversion |
| `read_error_formats_sovd_and_uds` | Error mapping |
| `register_keeps_insertion_order` | Registry ordering |
| `register_rejects_duplicate_id` | Duplicate detection |
| `list_all_in_registration_order` | Provider listing |
| `read_value_and_schema_on_request` | Read with schema |
| `write_reaches_the_resource` | Write propagation |
| `uds_adapter_served_without_extra_code` | Binary format support |

### 6.2 Gateway Integration Tests

| Test | Description |
|------|-------------|
| `serves_diag_api_resources_not_demo_data` | Cruise component visible |
| `injected_fault_is_debounced_then_reported` | Debounce semantics |
| `read_only_resource_rejects_writes` | Read-only enforcement |

### 6.3 Cruise Module Tests

| Test | Description |
|------|-------------|
| `failed_only_after_failed_duration` | Debounce timing |
| `short_glitch_never_qualifies` | Transient filtering |
| `recovery_needs_passed_duration` | Recovery debounce |
| `injection_freezes_the_speed` | Stuck sensor simulation |
| `injection_rejects_bad_body` | Input validation |

---

## 7. Submission Reference

| Field | Value |
|-------|-------|
| PR URL | https://github.com/eclipse-score/inc_diagnostics/pull/40 |
| PR Number | #40 |
| Submission Date | 2026-10-07 |
| Status | SUBMITTED - Awaiting maintainer review |

---

## 8. Dependencies

| Dependency | Relation |
|------------|----------|
| PR #6 (gateway_cda_int) | Base branch |
| opensovd_core | External dependency |
| diag_api | Internal S-CORE crate |

---

*Prepared by: EP1991 | Thinking_CAPs | Eclipse SDV Hackathon Chapter 4 2026*
