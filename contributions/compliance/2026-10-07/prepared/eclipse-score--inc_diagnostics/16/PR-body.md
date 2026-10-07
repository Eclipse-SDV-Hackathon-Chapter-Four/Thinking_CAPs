## Summary
- Implement `SovdDataProvider` adapter that implements `opensovd_core::DataProvider` backed by `diag_api::DataResource` instances
- Add `DataResourceRegistry` to manage resources with their metadata
- Replace demo Constant providers in opensovd-gateway with cruise control diag_api resources
- Add time-based debounce for fault qualification (mirrors DTC semantics)

## Components Added

### sovd_adapter crate
| File | Purpose |
|------|---------|
| `lib.rs` | Public API: `SovdDataProvider`, `DataResourceRegistry`, `PayloadFormat` |
| `registry.rs` | Resource registration with metadata |
| `provider.rs` | `DataProvider` trait implementation |
| `convert.rs` | Type conversions between diag_api and opensovd_core |
| `handle.rs` | Async handle resolution (Ready/Pending) |

### opensovd-gateway changes
| File | Change |
|------|--------|
| `BUILD` | Add sovd_adapter and diag_api dependencies |
| `main.rs` | Wire cruise control resources instead of demo data |
| `cruise.rs` | Cruise control diagnostics with fault injection |

## Cruise Control Resources
| Resource | Category | Access | Description |
|----------|----------|--------|-------------|
| `vehicle_speed` | currentData | read | Vehicle speed sensor reading |
| `cruise_state` | currentData | read | Cruise control state (standby/active/unavailable) |
| `speed_sensor_fault_status` | currentData | read | Debounced fault status |
| `speed_sensor_stuck` | storedData | read/write | Fault injection control |

## Features
- `list()`/`categories()`/`groups()` derived from `DataResourceMetadata`
- `read(data_id, include_schema)` dispatches to `DataResource::read`, converts encoding
- `write(data_id, value)` dispatches to `DataResource::write`
- Error mapping: `diag_api::Error` / `DataError` to `opensovd_models::ErrorCode`
- Per-resource `PayloadFormat` (JSON, UTF8, Binary) for UDS adapters

## Test Evidence
- Unit tests in `sovd_adapter` crate
- Integration tests in `opensovd-gateway` using `opensovd-client`
- Cruise control debounce logic tests

Closes #16

Contributed by: EP1991 | Thinking_CAPs | Eclipse SDV Hackathon Chapter 4 2026

## AI assistance and review

- Anthropic Claude Opus 5.5 (user-confirmed on 2026-10-07)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
