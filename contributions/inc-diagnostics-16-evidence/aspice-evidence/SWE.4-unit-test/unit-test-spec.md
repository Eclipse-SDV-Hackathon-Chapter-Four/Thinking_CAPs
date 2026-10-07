# SWE.4 Unit Test Specification

| Document ID | INC-DIAG-16-SWE4-UT |
|-------------|---------------------|
| Issue | #16 |
| Component | sovd_adapter |
| Date | 2026-10-07 |

---

## 1. Test Scope

Unit tests for the `sovd_adapter` crate covering:
- Registry operations
- Provider DataProvider implementation
- Type conversions
- Async handle resolution
- Cruise control module

---

## 2. Registry Tests (registry.rs)

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| UT-REG-001 | `register_keeps_insertion_order` | Register resources b, a and verify order | Order is [b, a] |
| UT-REG-002 | `register_rejects_duplicate_id` | Register same ID twice | Returns `DuplicateId` error |
| UT-REG-003 | `register_rejects_empty_id` | Register with empty string ID | Returns `EmptyId` error |
| UT-REG-004 | `default_format_is_json` | Register without format | Format is `PayloadFormat::Json` |

---

## 3. Convert Tests (convert.rs)

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| UT-CNV-001 | `metadata_maps_every_field` | Convert full metadata | All fields mapped correctly |
| UT-CNV-002 | `metadata_read_only_and_no_groups` | Convert read-only with no groups | `is_writable=false`, groups empty |
| UT-CNV-003 | `encoding_follows_format_and_schema_flag` | Test all format/schema combinations | Correct `ReplyMessageEncoding` |
| UT-CNV-004 | `reply_value_per_payload_kind` | Convert JSON/UTF8/Binary replies | Correct `Value` and schema |
| UT-CNV-005 | `request_payload_per_format` | Convert JSON/UTF8/Binary requests | Correct `RequestMessagePayload` |
| UT-CNV-006 | `request_payload_rejects_wrong_shapes` | Non-string for UTF8/Binary | Returns error |
| UT-CNV-007 | `read_error_formats_sovd_and_uds` | Map SOVD and UDS errors | Contains error text/hex code |
| UT-CNV-008 | `write_error_with_and_without_detail` | Map write errors | Contains path or message |

---

## 4. Handle Tests (handle.rs)

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| UT-HDL-001 | `read_ready` | Resolve Ready handle | Returns payload immediately |
| UT-HDL-002 | `read_future` | Resolve Pending with async future | Awaits and returns payload |
| UT-HDL-003 | `read_closure` | Resolve Pending with closure | Executes and returns payload |
| UT-HDL-004 | `read_error` | Resolve Ready error | Returns error |
| UT-HDL-005 | `write_ready_future_closure` | Test all write handle variants | All resolve correctly |

---

## 5. Provider Tests (provider.rs)

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| UT-PRV-001 | `list_all_in_registration_order` | List without filter | Returns all in order |
| UT-PRV-002 | `list_filters_by_category_and_group` | Filter by category/group/tag | Returns matching only |
| UT-PRV-003 | `categories_and_groups_come_from_metadata` | Query categories/groups | Deduped from metadata |
| UT-PRV-004 | `read_value_and_schema_on_request` | Read with/without schema | Schema included when requested |
| UT-PRV-005 | `read_unknown_id_is_not_found` | Read non-existent ID | Returns `NotFound` error |
| UT-PRV-006 | `read_error_is_internal_with_message` | Read from failing resource | Returns `Internal` with message |
| UT-PRV-007 | `write_reaches_the_resource` | Write and verify change | Value updated in resource |
| UT-PRV-008 | `write_read_only_is_rejected` | Write to read-only resource | Returns `ReadOnly` error |
| UT-PRV-009 | `uds_adapter_served_without_extra_code` | Register UDS adapter as Binary | Read returns hex, write accepts hex |
| UT-PRV-010 | `uds_adapter_registered_as_json_reports_mismatch` | UDS as JSON fails | Returns error about binary |

---

## 6. Cruise Tests (cruise.rs)

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| UT-CRU-001 | `failed_only_after_failed_duration` | Debounce timing for failure | PreFailed until duration |
| UT-CRU-002 | `short_glitch_never_qualifies` | Brief fault clears | Stays Passed |
| UT-CRU-003 | `recovery_needs_passed_duration` | Recovery debounce | PrePassed until duration |
| UT-CRU-004 | `injection_freezes_the_speed` | Stuck sensor simulation | Speed constant over time |
| UT-CRU-005 | `injection_rejects_bad_body` | Invalid stuck value | Returns error |

---

## 7. Test Coverage Summary

| Module | Tests | Coverage Focus |
|--------|-------|----------------|
| registry.rs | 4 | Registration, ordering, validation |
| convert.rs | 8 | Type conversions, error mapping |
| handle.rs | 5 | Async resolution patterns |
| provider.rs | 10 | DataProvider interface |
| cruise.rs | 5 | Debounce, fault injection |
| **Total** | **32** | |

---

## 8. Test Execution

```bash
# Run all unit tests
bazel test //score/mw/diag/sovd_adapter:sovd_adapter_test

# Run gateway tests
bazel test //score/opensovd-gateway:opensovd-gateway_test
```

---

*Prepared by: EP1991 | Thinking_CAPs | Eclipse SDV Hackathon Chapter 4 2026*
