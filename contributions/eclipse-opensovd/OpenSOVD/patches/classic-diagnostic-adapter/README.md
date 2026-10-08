# Classic Diagnostic Adapter Patches (CDA #543)

Patches for eclipse-opensovd/classic-diagnostic-adapter fixing error handling.

## Files

| Patch | Size | Purpose |
|-------|------|---------|
| `0001-refactor-cda-main-return-Result-instead-of-Option-in.patch` | 13 KB | Result vs Option fix |

## Issue

https://github.com/eclipse-opensovd/classic-diagnostic-adapter/issues/543

## Apply

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

## Changes

| Function | Before | After |
|----------|--------|-------|
| `load_mdd_paths_from_storage` | `Option<Vec<PathBuf>>` | `Result<Vec<PathBuf>, MddLoadingError>` |
| `build_diagnostic_database` | `Option<DiagnosticDatabase>` | `Result<DiagnosticDatabase, MddLoadingError>` |
| `create_ecu_manager` | `Option<EcuManager<S>>` | `Result<EcuManager<S>, MddLoadingError>` |

---

*Recovered: 2026-10-06*
