# Improvement

## Description

Enables backend-free application tests through the public score_com_mock facade. Independently built runtimes are isolated, clones share a registry, and each subscription receives into its own bounded FIFO. Discovery, provider cleanup, asynchronous receive/cancellation, streams and generated interfaces are covered by native tests.

## Related ticket

Addresses #490.

## Design and review

Native CommData has no Clone/Sync bound. One recipient receives by ownership transfer; multicast requires explicit register_cloneable_data::<T>() and otherwise fails before delivery. Queues retain newest values on overflow, do not replay before subscription, and clean up on unsubscribe/drop. The mock uses dynamic allocations/std mutexes for tests. Please review these semantics and deliberate panic on overlapping asynchronous receives. Native detailed design is updated; production trait bounds and dependency pins remain unchanged.

## Validation

On main `c77751819b8885a902540dbef7f0fe25cf85d51c`, candidate `0b363baf2a0520c8e31b617378459457c197e9a7`: 6 selected Bazel test targets passed (54 cases passed, 2 ignored, zero failed). Native Clippy and formatting of changed Rust/C++/BUILD sources passed. Complete commands, source hashes, raw logs, test XML/BEP, lint reports and earlier failures are in the offline contribution packet `evidence/native-fix-20261007`; its verification-summary.json and artifact-manifest.json bind the results.

Includes 19 mock unit tests, one runnable mock doc test, a generated public-interface test, native concept/macro suites, and the explicitly selected manual macro doc target (two baseline examples ignored). The original-draft regressions reproduced runtime leakage and subscriber sample stealing before the fix.

## Remaining merge gates

Native ECA check, full project CI (GCC15, QCC, ASan/UBSan, TSan and linters), review-checklists, code-owner approval and merge queue remain pending on the submitted revision. Local tests do not replace these gates or native engineering/safety/qualification acceptance. Keep the PR in Draft until the documented design/applicability decisions are reviewed.
