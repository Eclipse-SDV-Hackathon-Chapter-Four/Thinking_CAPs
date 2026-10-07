# Prepared draft — human review required

# Improvement

## Description

Enables backend-free application tests through the public score_com_mock facade. Independently built runtimes are isolated, clones share a registry, and each subscription receives into its own bounded FIFO. Discovery, provider cleanup, asynchronous receive/cancellation, streams and generated interfaces are covered by native tests.

## Related ticket

Addresses #490.

## Design and review

Native CommData has no Clone/Sync bound. One recipient receives by ownership transfer; multicast requires explicit register_cloneable_data::<T>() and otherwise fails before delivery. Queues retain newest values on overflow, do not replay before subscription, and clean up on unsubscribe/drop. The mock uses dynamic allocations/std mutexes for tests. Please review these semantics and deliberate panic on overlapping asynchronous receives. Native detailed design is updated; production trait bounds and dependency pins remain unchanged.

## Validation

On main `c77751819b8885a902540dbef7f0fe25cf85d51c`, candidate `0b363baf2a0520c8e31b617378459457c197e9a7`: 6 selected Bazel test targets passed (54 cases passed, 2 ignored, zero failed). Native Clippy and formatting of changed Rust/C++/BUILD sources passed. Complete commands, source hashes, raw logs, test XML/BEP, lint reports and earlier failures are in the [sealed review packet](https://github.com/jnsagai/communication/tree/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/490); its verification-summary.json and artifact-manifest.json bind the results.

Includes 19 mock unit tests, one runnable mock doc test, a generated public-interface test, native concept/macro suites, and the explicitly selected manual macro doc target (two baseline examples ignored). The original-draft regressions reproduced runtime leakage and subscriber sample stealing before the fix.

## Remaining merge gates

Native ECA check, full project CI (GCC15, QCC, ASan/UBSan, TSan and linters), review-checklists, code-owner approval and merge queue remain pending on the submitted revision. Local tests do not replace these gates or native engineering/safety/qualification acceptance. The contributor has approved the proposed behavior. This PR stays in Draft for the contributor to review and mark ready manually; upstream design/applicability acceptance remains pending.

## Reproduction and evidence

[Exact commands, input hashes and reproduction instructions](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/490/reproduce.md). The [review packet](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/490/review-packet.md) contains requirement/ownership/concurrency analysis, and the [merge checklist](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/490/merge-readiness.md) enumerates every required gate. The sealed packet predates publication; [human approval](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/490/human-approval.json) and [strict ECA validation](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/490/eca-validation-result.json) are later supplements.

Upstream main advanced to `4c12cfe27ba51d97346dfaa27a2c539385590bde` through safety-documentation changes after the local tests. This PR preserves the exact tested candidate and records the tested baseline above; hosted CI must validate the submitted merge revision. No full CI matrix, safety qualification or maintainer acceptance is claimed.

## License headers

Every changed code/build file (5 files) passed the native score_tooling copyright checker using the unmodified repository template and configuration: zero missing, misplaced, wrong-format, duplicate or mismatched-license headers. The changed Markdown design document preserves its complete existing Eclipse/Apache-2.0 header and was checked separately because the native tool has no Markdown template. [Full file/hash audit and raw checker output](https://github.com/jnsagai/communication/tree/2fdc2a88c2272db4c6a5641443a4b033c2e1ee3c/contribution-evidence/communication/490/license-header-audit-20261007). No source changes were necessary; the submitted code head and prior native test evidence are unchanged.


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)
- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
