# Contribution Plan - What We Will Submit

## Summary

| # | Contribution | Repository | Type | Lines | Day |
|---|--------------|------------|------|-------|-----|
| 1 | CDA #543 | classic-diagnostic-adapter | Bug fix | ~230 | Day 1 |
| 2 | Issue #553 | opensovd-core | API fixes | ~770 | Day 1 |
| 3 | PR #16 | inc_diagnostics | New adapter | ~900 | Day 2 |
| 4 | Demo | Our repo | Integration | ~800 | Day 2 |
| **Total** | | | | **~2,700** | |

---

## Contribution 1: CDA #543 (Day 1 Morning)

### Target

| Field | Value |
|-------|-------|
| **Repository** | eclipse-opensovd/classic-diagnostic-adapter |
| **Issue** | https://github.com/eclipse-opensovd/classic-diagnostic-adapter/issues/543 |
| **Type** | Bug fix |
| **File** | `cda-main/src/mdd.rs` |

### Changes

| Function | Before | After |
|----------|--------|-------|
| `load_mdd_paths_from_storage` | `Option<Vec<PathBuf>>` | `Result<Vec<PathBuf>, MddLoadingError>` |
| `build_diagnostic_database` | `Option<DiagnosticDatabase>` | `Result<DiagnosticDatabase, MddLoadingError>` |
| `create_ecu_manager` | `Option<EcuManager<S>>` | `Result<EcuManager<S>, MddLoadingError>` |

### New Error Variants

```rust
StorageUnavailable { reason: String }
MissingPayload { path: String, ecu: String }
DatabaseBuildFailed { path: String, ecu: String, reason: String }
ComParamsInvalid { ecu: String }
EcuManagerFailed { ecu: String, reason: String }
```

---

## Contribution 2: Issue #553 (Day 1 Afternoon)

### Target

| Field | Value |
|-------|-------|
| **Repository** | eclipse-opensovd/opensovd-core |
| **Issue** | https://github.com/eclipse-opensovd/opensovd-core/issues/553 |
| **Type** | API compliance |
| **Standard** | ISO 17978-3 |

### 8 Fixes

| # | File | Fix | ISO Ref |
|---|------|-----|---------|
| 1 | `data.rs` | Mode.value mandatory | §7.4 |
| 2 | `bulkdata.rs` | Category enum | §8.2 |
| 3 | `discovery.rs` | Discovery endpoint | §6.1 |
| 4 | `component.rs` | Restart endpoint | §7.8 |
| 5 | `area.rs` | Area listing | §7.2 |
| 6 | `app.rs` | App metadata | §7.3 |
| 7 | `error.rs` | Error format | §9.1 |
| 8 | `version.rs` | Version endpoint | §6.2 |

---

## Contribution 3: PR #16 - sovd_adapter (Day 2)

### Target

| Field | Value |
|-------|-------|
| **Repository** | eclipse-score/inc_diagnostics |
| **PR** | #16 (to be created) |
| **Type** | New feature |
| **Purpose** | S-CORE ↔ OpenSOVD bridge |

### Files to Create

| File | Lines | Purpose |
|------|-------|---------|
| `lib.rs` | ~300 | Main adapter |
| `data_provider.rs` | ~200 | DataProvider trait |
| `fault_provider.rs` | ~150 | FaultProvider trait |
| `component.rs` | ~100 | Component registration |
| `types.rs` | ~80 | Type definitions |
| `error.rs` | ~70 | Error handling |
| `Cargo.toml` | ~30 | Dependencies |
| `BUILD.bazel` | ~40 | Bazel build rules |

---

## Contribution 4: Demo (Day 2)

### Components

| Component | Language | Lines | Purpose |
|-----------|----------|-------|---------|
| `cruise_bridge` | Rust | ~150 | mw::com client |
| `cruise_diag` | Rust | ~200 | Fault monitoring |
| `dashboard` | HTML/JS | ~200 | Web UI |
| `server.py` | Python | ~100 | HTTP server |

### Demo Flow

1. Start X-Verse container
2. cruise_bridge connects to TCP :7700
3. cruise_diag monitors speed signal
4. Inject signal loss (stop car_simulation)
5. DTC generated after 5s debounce
6. sovd_adapter exposes via SOVD
7. Dashboard shows fault status

---

## PR Submission Checklist

### CDA #543

- [ ] Fork repository
- [ ] Create branch `fix/cda-543-result-not-option`
- [ ] Implement changes
- [ ] Add tests
- [ ] Run `cargo test --locked --lib`
- [ ] Run `cargo clippy`
- [ ] Submit PR

### Issue #553

- [ ] Fork repository
- [ ] Create branch `fix/issue-553-api-compliance`
- [ ] Implement 8 fixes
- [ ] Add/update tests
- [ ] Run `cargo test`
- [ ] Run `cargo clippy`
- [ ] Submit PR

### PR #16

- [ ] Fork repository
- [ ] Create branch `feature/sovd-adapter`
- [ ] Create new crate structure
- [ ] Implement adapter
- [ ] Add tests
- [ ] Run `cargo build`
- [ ] Submit PR

---

## Evidence to Collect

| Evidence | When | Format |
|----------|------|--------|
| PR URLs | After submission | Links |
| Screenshots | After submission | PNG |
| Test logs | After tests pass | TXT |
| Demo video | Day 2 evening | MP4 |

---

*Plan prepared for Eclipse SDV Hackathon 2026*
*This is PRE-WORK planning only - no code written*
