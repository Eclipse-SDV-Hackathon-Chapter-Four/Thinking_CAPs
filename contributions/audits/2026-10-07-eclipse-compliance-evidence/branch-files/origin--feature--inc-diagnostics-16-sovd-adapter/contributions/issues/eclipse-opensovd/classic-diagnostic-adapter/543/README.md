# CDA #543 — Return Result instead of Option for error handling

[Upstream issue #543](https://github.com/eclipse-opensovd/classic-diagnostic-adapter/issues/543)
requests changing `Option<T>` to `Result<T, E>` for proper error handling in `cda-main/src/mdd.rs`.

## Problem Statement

From the issue:

> "A bunch of code paths in cda-main/src/mdd.rs use Options to actually indicate an error.
> This is unusual and not a good design."

## Local Status: **patches_recovered**

The patch has been recovered and is ready for testing.

## Patch File

```
patches/classic-diagnostic-adapter/0001-refactor-cda-main-return-Result-instead-of-Option-in.patch
```

## Changes Made

### Functions Modified

| Function | Line | Before | After |
|----------|------|--------|-------|
| `load_mdd_paths_from_storage` | 256 | `Option<Vec<PathBuf>>` | `Result<Vec<PathBuf>, MddLoadingError>` |
| `build_diagnostic_database` | 431 | `Option<DiagnosticDatabase>` | `Result<DiagnosticDatabase, MddLoadingError>` |
| `create_ecu_manager` | 476 | `Option<EcuManager<S>>` | `Result<EcuManager<S>, MddLoadingError>` |

### New Error Variants

```rust
pub enum MddLoadingError {
    LoadFailed { path: String, reason: String },
    DecompressFailed { path: String, reason: String },
    StorageUnavailable { reason: String },           // NEW
    MissingPayload { path: String, ecu: String },    // NEW
    DatabaseBuildFailed { path: String, ecu: String, reason: String }, // NEW
    ComParamsInvalid { ecu: String },                // NEW
    EcuManagerFailed { ecu: String, reason: String }, // NEW
}
```

## Apply the Patch

```bash
cd upstream/classic-diagnostic-adapter
git apply ../../patches/classic-diagnostic-adapter/*.patch
```

## Verify

```bash
cargo build --release
cargo test --locked --lib
cargo clippy --all-targets -- -D warnings
```

## Hackathon Tasks

- [ ] Apply patch to upstream checkout
- [ ] Run tests
- [ ] Capture evidence
- [ ] Submit PR

---

*Recovered: 2026-10-06*
