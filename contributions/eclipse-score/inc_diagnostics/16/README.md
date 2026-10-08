# Diagnostics #16 — sovd_adapter (S-CORE ↔ OpenSOVD Bridge)

[Upstream issue #16](https://github.com/eclipse-score/inc_diagnostics/issues/16)
requests an adapter from diagnostic API resources to an OpenSOVD data provider.

## Local Status: **patches_recovered**

The five patch files have been recovered and are ready for testing.

## Patch Files

| # | File | Purpose |
|---|------|---------|
| 1 | `0001-build-bazel-apply-the-opensovd_core-cargo-bazel-lock.patch` | Fix cargo-bazel lock |
| 2 | `0002-build-bazel-expose-opensovd_core-s-tokio-and-serde_j.patch` | Expose tokio/serde |
| 3 | `0003-feat-diag_api-re-export-JsonSchemaRequired.patch` | Re-export types |
| 4 | `0004-feat-sovd_adapter-serve-diag_api-DataResources-as-an.patch` | DataProvider implementation |
| 5 | `0005-feat-opensovd-gateway-serve-HVAC-diag_api-resources-.patch` | Wire into gateway |

Location: `patches/inc_diagnostics/`

## Apply the Patches

```bash
cd upstream/inc_diagnostics
git apply ../../patches/inc_diagnostics/*.patch
```

## Key Components

### sovd_adapter crate

| File | Purpose |
|------|---------|
| `lib.rs` | Main adapter implementation |
| `data_provider.rs` | DataProvider trait impl |
| `fault_provider.rs` | FaultProvider trait impl |
| `component.rs` | Component registration |
| `types.rs` | Type definitions |
| `error.rs` | Error handling |

## Hackathon Tasks

- [ ] Apply patches to upstream checkout
- [ ] Run Bazel build
- [ ] Run tests
- [ ] Capture evidence
- [ ] Submit PR

[Snapshot](upstream-snapshot.json), [provenance](provenance.json) and
[captured artifact hashes](artifact-manifest.json) preserve the current evidence.

---

*Recovered: 2026-10-06*
