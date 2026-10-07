# Communication #490 — Implement isolated Rust COM mock runtime

Enables backend-free application tests through the public score_com_mock facade. Independently built runtimes are isolated, clones share a registry, and each subscription receives into its own bounded FIFO. Discovery, provider cleanup, asynchronous receive/cancellation, streams and generated interfaces are covered by native tests.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/490 |
| Local status | Draft PR published; selected local Linux checks passed; upstream CI and maintainer review pending |
| Verified baseline | `c77751819b8885a902540dbef7f0fe25cf85d51c` |
| Candidate commit | `0b363baf2a0520c8e31b617378459457c197e9a7` |
| Branch | `feature/490-mock-runtime-verified` (portable bundle and disposable workspace; reference clone unchanged) |
| Native verification | 6 targets; 54 cases passed, 2 ignored, zero failed; selected Clippy and formatting passed |
| Upstream publication | [Draft PR #1340](https://github.com/eclipse-score/communication/pull/1340) |
| Contributor behavior approval | Approved in this session; upstream engineering acceptance pending |

## PR artifacts

- [git-am patch](communication-490.patch) and [portable branch bundle](feature-490-mock-runtime-verified.bundle).
- [PR title](pr-title.txt) and [PR description](pr-description.md).
- [Review packet](evidence/native-fix-20261007/review-packet.md), [test evidence](evidence/native-fix-20261007/verification-summary.json), [merge checklist](evidence/native-fix-20261007/merge-readiness.md), [reproduction](evidence/native-fix-20261007/reproduce.md).
- [Final source/patch binding](evidence/native-fix-20261007/candidate/source-binding.json) and [packet manifest](evidence/native-fix-20261007/artifact-manifest.json).

The patch cleanly applies to the recorded current-main baseline and produces the candidate Git tree; the bundle was verified. The full final source matches the test and lint input manifests. Import into a disposable clone as documented in reproduction; local preparation preserved the reference clone; later publication is recorded below.

## Scope and pending decisions

Approve isolated runtime lifecycle, bounded FIFO/no-replay semantics, explicit clone registration for multicast and panic on overlapping async receives. Confirm test-only dynamic allocation and any additional requirements/qualification obligations.

The former unverified mock now has passing native event-runtime and generated public API evidence. Multicast requires explicit Clone registration because native CommData does not require Clone or Sync. See the packet for receive/overflow/concurrency semantics and test-runtime limitations.

The project requires ECA, its exact required CI checks, an approving/code-owner review and merge queue. Full repository tests, QNX/sanitizers and official lint statuses remain pending; no local result or artifact substitutes for them. The ECA status subsequently passed on the published PR; other gates remain pending. [merge-readiness.md](evidence/native-fix-20261007/merge-readiness.md) inventories each gate and reviewer decision.

## History and provenance

Historical draft records are preserved in [previous-record](evidence/native-fix-20261007/previous-record/); older sealed evidence folders remain unchanged. Original Fabro correction budgets were exhausted; this user-authorized direct engineering follow-up did not resume those loops or make paid calls. The earlier draft bundles remain historical and do not contain this fix. Current [provenance.json](provenance.json) and [artifact-manifest.json](artifact-manifest.json) bind these records. That packet predates publication. The later [publication record](publication/README.md) records the approved behavior, fork/branch publication, draft PR and strict ECA validation; no issue closure, merge or upstream acceptance was made.

## Draft publication

[PR #1340](https://github.com/eclipse-score/communication/pull/1340) is open from `jnsagai:feature/490-mock-runtime-verified` against
`eclipse-score/communication:main`. Its exact head, six changed files, title/body and draft
state were checked. Your ECA account `jnascimento6p0` passed strict validation for the
author/committer commit email. You approved the proposed behavior and will review and
mark ready manually. Hosted CI and maintainer approval remain separate pending gates.

[Public sealed review evidence](https://github.com/jnsagai/communication/tree/b7da4c751f19e666ea53d22632c32a975e74df29/contribution-evidence/communication/490) is on a separate fork branch,
without adding evidence files to the native PR's code diff. The tested baseline remains
`c77751819b8885a902540dbef7f0fe25cf85d51c`; upstream's later safety-documentation changes are recorded in
[upstream-at-publication.json](publication/upstream-at-publication.json). The original
sealed native packet remains unchanged.

## License-header verification

All 5 changed source/build files passed the native
copyright checker with the unmodified Eclipse contributor / Apache-2.0 template.
The changed Markdown design document also has its existing complete header, verified separately.
[Local audit](license-header-audit-20261007/README.md) and [published audit](https://github.com/jnsagai/communication/tree/2fdc2a88c2272db4c6a5641443a4b033c2e1ee3c/contribution-evidence/communication/490/license-header-audit-20261007)
retain per-file hashes, exact commands and raw output. No header/source changes
were necessary; the PR code head remains `0b363baf2a0520c8e31b617378459457c197e9a7`.
