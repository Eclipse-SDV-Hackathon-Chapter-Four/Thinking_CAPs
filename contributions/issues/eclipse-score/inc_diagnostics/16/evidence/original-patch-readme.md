# inc_diagnostics Patches

Patches for eclipse-score/inc_diagnostics (PR #16).

## Files
- `0001-build-bazel-*.patch` - Fix cargo-bazel lock
- `0002-build-bazel-*.patch` - Expose tokio/serde
- `0003-feat-diag_api-*.patch` - Re-export types
- `0004-feat-sovd_adapter-*.patch` - DataProvider implementation
- `0005-feat-opensovd-gateway-*.patch` - Wire into gateway

## Apply
```bash
cd upstream/inc_diagnostics
git apply ../../patches/inc_diagnostics/*.patch
```
