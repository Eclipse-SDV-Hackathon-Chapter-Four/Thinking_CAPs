Adds a QM LoLa integration test on Linux for repeated `OfferService`, `StopOfferService`, `StartFindService`, `Subscribe` and `Unsubscribe` calls. It compares discovered service identity/cardinality, verifies absence after each stop, checks subscription state and rejection after each unsubscribe, and verifies sample delivery and recovery with finite deadlines. The harness requires application exit 0. Production APIs are unchanged.

Repeated discovery uses the same callback and instance specifier. Distinct search-operation handles follow the native implementation; every operation must report unchanged discovered service state and is stopped. Callback storage remains alive for the whole test. Follow-ups resolve all introduced clang-tidy findings without changing assertions, execution controls or suppression settings.

Root BUILD also fixes the existing copyright checker input paths for BUILD/MODULE.bazel. This utility change is isolated from the new test directory for separate review.

Relates to #1167.

[Final-source fork Host verification](https://github.com/jnsagai/communication/actions/runs/37652549770) passes all six native non-QNX jobs for PR head `2aead7cd18c96b907e086c8b59797b527f65567d`, merged with upstream `cef680454e8586daca9f953084dca33fb3759d0c` (source tree `dcee6cdd36f7826eda8fe47cb75a578b769f65e2`).

- Address & Undefined Behavior Sanitizer / Build & Test: Executed 506 out of 514 tests: 506 tests pass and 8 were skipped.
- GCC15 / Build & Test: Executed 507 out of 514 tests: 507 tests pass and 7 were skipped.
- Thread Sanitizer / Build & Test: Executed 404 out of 514 tests: 404 tests pass and 110 were skipped.
- Separate module integration build passes.
- Clang-tidy, clippy and Ruff pass with zero findings in the new test directory. Native formatter and strict Eclipse ECA validation pass.

TSan retains the shared native Docker-integration exclusion (Ticket-249859); its new schema test passes. The new runtime and schema tests pass under GCC15 and ASan/UBSan/leak. The report artifacts contain 19 clang-tidy warnings and 5 clippy warnings outside the new test, and 0 Ruff findings. Failed/superseded predecessor attempts remain preserved.

Direct pinned-checker comparison at the verified baseline reports 200 identical inherited copyright findings and zero PR additions; the full check remains failed. Seven header-eligible contribution paths pass; two JSON configurations have no native header template. No waiver is claimed.

Every header-eligible changed file exactly matches the project's Eclipse copyright/license template, including `SPDX-License-Identifier: Apache-2.0`; existing creation years are retained. JSON configurations remain valid JSON. AI assistance: the original draft used DeepSeek deepseek-v4-flash, and review/corrections/verification used OpenAI Codex. Native human maintainer review remains required before merge.

QNX is excluded from contributor verification as requested. Upstream main advanced during verification; those later changes are not claimed tested by this fork run. Native Host workflow approval, required upstream statuses, code-owner approval, inherited copyright handling and the merge queue remain maintainer-owned. Fork results do not supply the required upstream GitHub statuses.

The user-requested repository-wide code-header repair is independently proposed in [PR #1341](https://github.com/eclipse-score/communication/pull/1341): 2,367 code paths audited, 91 files repaired, zero code-header findings. Its remaining whole-repository diagnostics are non-code content; this PR's pinned-baseline results above retain their original source identity.
