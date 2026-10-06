# Prepared native DFM storage contribution
Prepared 4 October 2026. No public submission, maintainer approval, merge or event eligibility
is claimed. Upstream: [eclipse-opensovd/fault-lib](https://github.com/eclipse-opensovd/fault-lib),
base12dac502616701734f90a61edca1326ae2ac6506. One changed upstream file:
`src/dfm_lib/src/sovd_fault_storage.rs`.

The current adapter mutates the process-global KVS cache without flushing. A same-process
manager restart can retain data while a new OS process sees no record. The new regression
fails with the original constructor; the prepared patch adds explicit `new_write_through` while
retaining default `new` flush policy. Mutations flush before acknowledging success; backend errors
propagate. Catalog-map errors other than KeyNotFound now fail instead of becoming empty/default
state or being overwritten. A failed flush can leave the in-memory mutation intact.

This is process-restart persistence, not a storage hardware/power-loss guarantee. Synchronous
storage I/O runs outside the Cruise Control loop. The integration separately exposes report,
query and actual storage acknowledgments, so query visibility is not treated as proof of durability.

## Review artifacts
- [Exported patch](write-through.patch), identical to [integration patch](../../patches/fault-storage/write-through.patch)
- [PR description draft](PR-description.md) and [test/continuation record](validation.md)
- [Unmodified failing regression](../../evidence/f004-unpatched-process-restart.txt)
- [Pinned-nightly native tests](../../evidence/f004-native-nightly-tests.txt), [Clippy](../../evidence/f004-upstream-clippy.txt)
- [Actual receiver/DFM process-restart evidence](../../evidence/f004-receiver-signal-fix/results.json)
- [Clean-source native reproduction](../../evidence/f008-reproduction-final/manifest.json)

The larger companion artifact is the receiver-to-native-OpenSOVD integration example/campaign.
It uses existing App data providers and labels its fault-data fallback. Native faults routing
belongs to [OpenSOVD#156](https://github.com/eclipse-opensovd/opensovd-core/issues/156)'s existing
owner; no duplicated `/faults` route or coordination claim is included.

Before public submission, follow the pinned repository's
[contribution instructions](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/CONTRIBUTING.md).
Those instructions require account/ECA and pre-commit/GitHub Actions gates. No pre-commit
configuration exists at this pin; its gate is not claimed. Account/agreement, full CI and
publication are pending, separately from these locally verified artifacts.
