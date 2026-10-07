# Improvement

## Description

Adds the Rust MethodInArgPtr ABI representation with exclusive lifetime-bound ownership of the input and activity flag. Moving the owner transfers responsibility; dropping it clears the flag without freeing the input. Native tests compare size/alignment and member representation with the real C++ object and exercise both languages’ move/destruction behavior.

## Related ticket

Addresses #781.

## Design and review

The representation is measured for Linux x86_64 against the actual non-trivial C++ type. Safe construction exclusively borrows both referents; no Clone/Copy or Send/Sync is exposed. A future method bridge must use explicit pointer-based ownership operations. This change implements the ABI owner requested by #781; method-runtime integration (#782) and its caller/callee AoU evidence remain separate work.

## Validation

On main `c77751819b8885a902540dbef7f0fe25cf85d51c`, candidate `d39eb127221538d623a3ddb4c8b519396a0528b1`: 5 selected Bazel test targets passed (40 cases passed, 0 ignored, zero failed). Native Clippy and formatting of changed Rust/C++/BUILD sources passed. Complete commands, source hashes, raw logs, test XML/BEP, lint reports and earlier failures are in the offline contribution packet `evidence/native-fix-20261007`; its verification-summary.json and artifact-manifest.json bind the results.

Includes four owner unit tests, six doc tests (one runnable and five compile-fail), adjacent Rust pointer regression tests and 13 native C++ pointer tests.

## Remaining merge gates

Native ECA check, full project CI (GCC15, QCC, ASan/UBSan, TSan and linters), review-checklists, code-owner approval and merge queue remain pending on the submitted revision. Local tests do not replace these gates or native engineering/safety/qualification acceptance. Keep the PR in Draft until the documented design/applicability decisions are reviewed.
