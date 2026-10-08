# Measured checks

Baseline: `cef680454e8586daca9f953084dca33fb3759d0c`. Candidate: `8f7695f09614c979b8a5f4721e9f2346d500d127`. Patch SHA-256: `b8f1dcd9b5ca6d8594c0ad249eb5c2336ada471e3e77049becfed109f6fab04b`.

| Check | Local result | Evidence |
| --- | --- | --- |
| ownership-regression | pass; 4 executed targets | [evidence/resolved-ownership-regression/native-result.json](evidence/resolved-ownership-regression/native-result.json) |
| cfg-test-clippy | pass; 2 test actions, macro-forwarder coverage incomplete | [evidence/resolved-cfg-test-clippy/native-result.json](evidence/resolved-cfg-test-clippy/native-result.json) |
| format-check | pass | [evidence/resolved-format-check/native-result.json](evidence/resolved-format-check/native-result.json) |
| notice-changed | pass | [evidence/resolved-notice-changed/native-result.json](evidence/resolved-notice-changed/native-result.json) |
| serial-integrations | pass; 4 executed targets | [evidence/resolved-serial-integrations/native-result.json](evidence/resolved-serial-integrations/native-result.json) |
| native-clippy | pass; 2 warning | [evidence/resolved-native-clippy/native-result.json](evidence/resolved-native-clippy/native-result.json) |
| native-ruff | pass | [evidence/resolved-native-ruff/native-result.json](evidence/resolved-native-ruff/native-result.json) |
| host-build | pass | [evidence/resolved-host-build/native-result.json](evidence/resolved-host-build/native-result.json) |
| host-tests | pass; 510 executed targets; 7 skipped | [evidence/resolved-extended-host-tests/native-result.json](evidence/resolved-extended-host-tests/native-result.json) |
| macro-and-doc-tests | pass; 4 executed targets | [evidence/resolved-extended-macro-and-doc-tests/native-result.json](evidence/resolved-extended-macro-and-doc-tests/native-result.json) |
| notice-full | fail | [evidence/resolved-extended-notice-full/native-result.json](evidence/resolved-extended-notice-full/native-result.json) |
| clang-tidy-full | pass; 19 warning | [evidence/resolved-extended-clang-tidy-full/native-result.json](evidence/resolved-extended-clang-tidy-full/native-result.json) |
| asan-full | pass; 509 executed targets; 8 skipped | [evidence/resolved-extended-asan-full/native-result.json](evidence/resolved-extended-asan-full/native-result.json) |
| tsan-full | fail; 405 executed targets; 112 skipped | [evidence/resolved-extended-tsan-full/native-result.json](evidence/resolved-extended-tsan-full/native-result.json) |
| resolved-module-graph | fail | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| test-inventory | pass | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| manual-inventory | pass | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| test-clippy-actions | pass | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| sanitizer-actions-asan_ubsan_lsan | pass | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| sanitizer-actions-tsan | pass | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| module-build | pass | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| module-dependencies | pass | [evidence/auxiliary-evidence/results.json](evidence/auxiliary-evidence/results.json) |
| Native semantic document validation | reported_findings | [DOCUMENT-VALIDATION.md](DOCUMENT-VALIDATION.md) |
| QCC - Build & Test | unavailable | [evidence/run-metadata/qnx-availability.json](evidence/run-metadata/qnx-availability.json) |

The emitted build events identify executed test targets. Captured XML outside that executed set may be earlier test output and is not counted as a fresh execution. Manual targets, ignored cases and unavailable platform checks are recorded explicitly. Analyzer execution and report severity are separate facts. The native hosted analyzer job also uses Aspect CLI hold-the-line strategy and uploads reports; this collector does not assert that hosted status. Older attempts and source epochs are retained as history and are not substituted for these results.

The TSAN run has 404 passing targets and one failing new subscription-state target; its 112 skipped targets are not passing results. See [sanitizer disposition](SANITIZER-COVERAGE.md). Whole-tree copyright has 200 unchanged baseline findings. The nested module-graph query fails on DNS resolution. These and the document/coverage gaps require disposition before merge.
