Adds a LoLa integration test for repeated `OfferService`, `StopOfferService`, `StartFindService`, `Subscribe` and `Unsubscribe` calls. It compares discovered service identity/cardinality, verifies absence after each stop, checks subscription state and rejection after each unsubscribe, and verifies sample delivery and recovery with finite deadlines. The harness requires application exit 0. Production APIs are unchanged.

Repeated discovery uses the same callback and instance specifier. Distinct search-operation handles follow the native implementation; each operation must report the unchanged discovered service state and is stopped. Callback storage remains alive for the whole test.

Root BUILD also fixes the existing copyright checker input paths for BUILD/MODULE.bazel. This utility change is isolated from the test directory for separate review.

Relates to #1167.

[Fork Host run 37645549862](https://github.com/jnsagai/communication/actions/runs/37645549862) passed all six native non-QNX jobs on predecessor PR head `4683338ab53393d16e0a3eb1aa5c8c27e1728057`:

- GCC15 build: 507 tests pass, seven skip; separate module integration build passes.
- ASan/UBSan/leak: 506 tests pass, eight skip; new runtime/schema tests pass.
- TSan: 404 tests pass, 110 skip; native rules exclude Docker integration (Ticket-249859), while the new schema test passes.
- Clang-tidy, clippy and Ruff jobs pass. Report review identified one remaining new-test warning preferring an anonymous namespace over static function linkage.

Current PR head `2aead7cd18c96b907e086c8b59797b527f65567d` resolves that warning without changing assertions, behavior, execution controls or suppression settings. Native formatter and strict Eclipse ECA validation pass. [Final-source Host run 37652549770](https://github.com/jnsagai/communication/actions/runs/37652549770) is running; predecessor results above are retained with their explicit source identity.

Copyright comparison at the verified upstream `cef680454e8586daca9f953084dca33fb3759d0c` baseline has 200 inherited findings with zero PR additions. The full repository check remains failed. Seven header-eligible contribution files pass; two JSON configurations have no native header template. No waiver is claimed.

QNX is excluded from this contributor verification as requested. The upstream Host workflow requires maintainer approval to run; code-owner approval and merge-queue entry remain outstanding. Fork results do not supply required upstream GitHub statuses.
