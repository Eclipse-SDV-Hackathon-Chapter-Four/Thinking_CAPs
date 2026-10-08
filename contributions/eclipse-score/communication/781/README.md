# Communication #781 — Implement lifetime-bound MethodInArgPtr ABI owner

Adds the Rust MethodInArgPtr ABI representation with exclusive lifetime-bound ownership of the input and activity flag. Moving the owner transfers responsibility; dropping it clears the flag without freeing the input. Native tests compare size/alignment and member representation with the real C++ object and exercise both languages’ move/destruction behavior.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/781 |
| Local status | Draft PR published; selected local Linux checks passed; upstream CI and maintainer review pending |
| Verified baseline | `c77751819b8885a902540dbef7f0fe25cf85d51c` |
| Candidate commit | `d39eb127221538d623a3ddb4c8b519396a0528b1` |
| Branch | `feature/781-method-in-arg-ptr-ownership` (portable bundle and disposable workspace; reference clone unchanged) |
| Native verification | 5 targets; 40 cases passed, 0 ignored, zero failed; selected Clippy and formatting passed |
| Upstream publication | [Draft PR #1339](https://github.com/eclipse-score/communication/pull/1339) |
| Contributor behavior approval | Approved in this session; upstream engineering acceptance pending |

## PR artifacts

- [git-am patch](communication-781.patch) and [portable branch bundle](feature-781-method-in-arg-ptr-ownership.bundle).
- [PR title](pr-title.txt) and [PR description](pr-description.md).
- [Review packet](evidence/native-fix-20261007/review-packet.md), [test evidence](evidence/native-fix-20261007/verification-summary.json), [merge checklist](evidence/native-fix-20261007/merge-readiness.md), [reproduction](evidence/native-fix-20261007/reproduce.md).
- [Final source/patch binding](evidence/native-fix-20261007/candidate/source-binding.json) and [packet manifest](evidence/native-fix-20261007/artifact-manifest.json).

The patch cleanly applies to the recorded current-main baseline and produces the candidate Git tree; the bundle was verified. The full final source matches the test and lint input manifests. Import into a disposable clone as documented in reproduction; local preparation preserved the reference clone; later publication is recorded below.

## Scope and pending decisions

Approve the Linux x86_64 representation, exclusive borrowed input/flag lifecycle and pointer-only future FFI boundary. Confirm applicability of MethodInArgPtrMatches@1 to subsequent method integration.

The former unresolved ABI/ownership point now has an explicit implementation and native representation/lifecycle evidence. Validation is Linux x86_64. Non-trivial C++ by-value ABI and end-to-end method IPC are outside #781’s ABI-type scope.

The project requires ECA, its exact required CI checks, an approving/code-owner review and merge queue. Full repository tests, QNX/sanitizers and official lint statuses remain pending; no local result or artifact substitutes for them. The ECA status subsequently passed on the published PR; other gates remain pending. [merge-readiness.md](evidence/native-fix-20261007/merge-readiness.md) inventories each gate and reviewer decision.

## History and provenance

Historical draft records are preserved in [previous-record](evidence/native-fix-20261007/previous-record/); older sealed evidence folders remain unchanged. Original Fabro correction budgets were exhausted; this user-authorized direct engineering follow-up did not resume those loops or make paid calls. The earlier draft bundles remain historical and do not contain this fix. Current [provenance.json](provenance.json) and [artifact-manifest.json](artifact-manifest.json) bind these records. That packet predates publication. The later [publication record](publication/README.md) records the approved behavior, fork/branch publication, draft PR and strict ECA validation; no issue closure, merge or upstream acceptance was made.

## Draft publication

[PR #1339](https://github.com/eclipse-score/communication/pull/1339) is open from `jnsagai:feature/781-method-in-arg-ptr-ownership` against
`eclipse-score/communication:main`. Its exact head, six changed files, title/body and draft
state were checked. Your ECA account `jnascimento6p0` passed strict validation for the
author/committer commit email. You approved the proposed behavior and will review and
mark ready manually. Hosted CI and maintainer approval remain separate pending gates.

[Public sealed review evidence](https://github.com/jnsagai/communication/tree/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/781) is on a separate fork branch,
without adding evidence files to the native PR's code diff. The tested baseline remains
`c77751819b8885a902540dbef7f0fe25cf85d51c`; upstream's later safety-documentation changes are recorded in
[upstream-at-publication.json](publication/upstream-at-publication.json). The original
sealed native packet remains unchanged.

## License-header verification

All 6 changed source/build files passed the native
copyright checker with the unmodified Eclipse contributor / Apache-2.0 template.
[Local audit](license-header-audit-20261007/README.md) and [published audit](https://github.com/jnsagai/communication/tree/2fdc2a88c2272db4c6a5641443a4b033c2e1ee3c/contribution-evidence/communication/781/license-header-audit-20261007)
retain per-file hashes, exact commands and raw output. No header/source changes
were necessary; the PR code head remains `d39eb127221538d623a3ddb4c8b519396a0528b1`.
