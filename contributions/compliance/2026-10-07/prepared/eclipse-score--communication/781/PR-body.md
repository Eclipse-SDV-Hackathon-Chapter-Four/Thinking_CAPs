# Prepared draft — human review required

# Improvement

## Description

Adds the Rust MethodInArgPtr ABI representation with exclusive lifetime-bound ownership of the input and activity flag. Moving the owner transfers responsibility; dropping it clears the flag without freeing the input. Native tests compare size/alignment and member representation with the real C++ object and exercise both languages’ move/destruction behavior.

## Related ticket

Addresses #781.

## Design and review

The representation is measured for Linux x86_64 against the actual non-trivial C++ type. Safe construction exclusively borrows both referents; no Clone/Copy or Send/Sync is exposed. A future method bridge must use explicit pointer-based ownership operations. This change implements the ABI owner requested by #781; method-runtime integration (#782) and its caller/callee AoU evidence remain separate work.

## Validation

On main `c77751819b8885a902540dbef7f0fe25cf85d51c`, candidate `d39eb127221538d623a3ddb4c8b519396a0528b1`: 5 selected Bazel test targets passed (40 cases passed, 0 ignored, zero failed). Native Clippy and formatting of changed Rust/C++/BUILD sources passed. Complete commands, source hashes, raw logs, test XML/BEP, lint reports and earlier failures are in the [sealed review packet](https://github.com/jnsagai/communication/tree/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/781); its verification-summary.json and artifact-manifest.json bind the results.

Includes four owner unit tests, six doc tests (one runnable and five compile-fail), adjacent Rust pointer regression tests and 13 native C++ pointer tests.

## Remaining merge gates

Native ECA check, full project CI (GCC15, QCC, ASan/UBSan, TSan and linters), review-checklists, code-owner approval and merge queue remain pending on the submitted revision. Local tests do not replace these gates or native engineering/safety/qualification acceptance. The contributor has approved the proposed behavior. This PR stays in Draft for the contributor to review and mark ready manually; upstream design/applicability acceptance remains pending.

## Reproduction and evidence

[Exact commands, input hashes and reproduction instructions](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/781/reproduce.md). The [review packet](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/781/review-packet.md) contains requirement/ownership/concurrency analysis, and the [merge checklist](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/781/merge-readiness.md) enumerates every required gate. The sealed packet predates publication; [human approval](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/781/human-approval.json) and [strict ECA validation](https://github.com/jnsagai/communication/blob/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/781/eca-validation-result.json) are later supplements.

Upstream main advanced to `4c12cfe27ba51d97346dfaa27a2c539385590bde` through safety-documentation changes after the local tests. This PR preserves the exact tested candidate and records the tested baseline above; hosted CI must validate the submitted merge revision. No full CI matrix, safety qualification or maintainer acceptance is claimed.

## License headers

Every changed code/build file (6 files) passed the native score_tooling copyright checker using the unmodified repository template and configuration: zero missing, misplaced, wrong-format, duplicate or mismatched-license headers. [Full file/hash audit and raw checker output](https://github.com/jnsagai/communication/tree/2fdc2a88c2272db4c6a5641443a4b033c2e1ee3c/contribution-evidence/communication/781/license-header-audit-20261007). No source changes were necessary; the submitted code head and prior native test evidence are unchanged.


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)
- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
