# inc_diagnostics Patches (PR #16 - sovd_adapter)

Patches for eclipse-score/inc_diagnostics implementing the S-CORE ↔ OpenSOVD bridge.

## Files

| # | Patch | Size | Purpose |
|---|-------|------|---------|
| 1 | `0001-build-bazel-*.patch` | 925 B | Fix cargo-bazel lock |
| 2 | `0002-build-bazel-*.patch` | 1 MB | Expose tokio/serde dependencies |
| 3 | `0003-feat-diag_api-*.patch` | 998 B | Re-export JsonSchemaRequired |
| 4 | `0004-feat-sovd_adapter-*.patch` | 38 KB | DataProvider implementation |
| 5 | `0005-feat-opensovd-gateway-*.patch` | 20 KB | Wire into gateway |

## Apply

```bash
cd upstream/inc_diagnostics
git apply ../../patches/inc_diagnostics/*.patch
```

## Verify

```bash
bazel build //score/mw/diag/sovd_adapter:all
bazel test //score/mw/diag/sovd_adapter:all
```

---

*Recovered: 2026-10-06*
