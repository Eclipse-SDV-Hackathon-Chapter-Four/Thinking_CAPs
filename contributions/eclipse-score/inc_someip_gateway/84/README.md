# SOME/IP #84 — duplicate server registration

| Field | Record |
| --- | --- |
| Upstream issue | [Revise version handling in socom #84](https://github.com/eclipse-score/inc_someip_gateway/issues/84) |
| Local status | Scoped implementation verified; local approval and PR preparation recorded |
| Upstream status | Open at 2026-10-04; upstream PR URL not recorded |
| Baseline | `f8a196c3b16d5172d898394ab99b0ed81346d63d` |
| Implementation / verification source | `s-core_sw_fabric` SOME/IP handoff; direct initial trial followed by Fabro verification/repair |
| Final native run | `01M40Y7RJF9NZJTE2N9Z3BAAXA` |

## Problem and fix

Two SOCom servers with the same service ID, major version and instance, but different
minor versions, could register separately against one database record and reach a
duplicate-server assertion. Registration identity now excludes minor version, so
the second server construction returns `Construction_error::duplicate_service`.
Six native source/build/test files change; regression tests cover identity, boundaries,
compatibility, ordering and connector lifecycle.

This implements the duplicate-registration slice of #84. Public identifier types,
optional discovery filters and the broader minor-version representation remain open.
The upstream PR draft uses **Related to #84**; it does not close the whole issue.

## Evidence and artifacts

- [Verified native patch](imported/pr-preparation/someip-84-verified.patch),
  [six candidate file hashes](imported/pr-preparation/candidate-files.json) and
  [patch application verification](imported/pr-preparation/preparation-verification.json).
- [Original prepared PR body](imported/pr-preparation/pr-description.md),
  [title](imported/pr-preparation/pr-title.txt) and
  [approved closure scope](imported/pr-preparation/closure-scope.md).
- [Final terminal status](imported/factory/runs/score-someip84-repair-b4ard87e/terminal-status.json),
  [stage outcomes](imported/factory/runs/score-someip84-repair-b4ard87e/native-stage-outcomes.json),
  [review resolution](imported/factory/runs/score-someip84-repair-b4ard87e/review-resolution.json) and
  [local approval record](imported/factory/runs/score-someip84-repair-b4ard87e/external-user-approval.json).
- [Complete portable evidence archive](imported/factory/runs/score-someip84-repair-b4ard87e/review-packet.tar.gz)
  (36,969,655 bytes), with candidate sources, commands, raw logs, integration XML,
  performance datasets, flamegraphs, frozen collectors and failed-run history.
- [Original offline verification](imported/factory/runs/score-someip84-repair-b4ard87e/offline-packet-verification.json),
  [repair report](imported/factory/review-repair-run.md) and
  [workflow graph](imported/factory/current-workflow.svg).
- [Readable extracted evidence](readable/README.md): byte-identical selected results
  and XML from the archive, with their original statuses.
- [Provenance](provenance.json), [artifact hashes](artifact-manifest.json),
  [upstream snapshot](upstream-snapshot.json), [LICENSE](imported/LICENSE) and [NOTICE](imported/NOTICE).

| Retained measurement | Result |
| --- | --- |
| GCC 12 / Clang 19 focused regressions | 91 tests pass each |
| Native unit target and formatting | Pass |
| Linux QEMU integration | Six targets execute; 13 applicable cases pass; one QNX-only case excluded |
| Native profiling | Two targets pass; 12 datasets and 12 flamegraphs retained |
| Offline evidence verification | 1,046 manifest entries and 269 candidate source hashes verified |

Passing checks reused in the final run are bound to unchanged candidate hashes and
original evidence identities. Fresh integration came from run
`01M40XMJ9K182CG0SWBNVPY7AB`; final profiling executed in the final run. Factory
verification is documented; the initial implementation was drafted directly in
the Codex session. This is not evidence that a factory agent authored all native code.

Historical measurement records still say human validation was pending; the later
external user approval is retained separately. Upstream committer review/CI, QNX
execution, tool qualification and full MISRA acceptance remain open.

Patch SHA-256: `c581f6319e5301d751b0a1caf2e51fbc8eda374d172199b121c1962158479732`.
Archive SHA-256: `2b8f5c40ae194ba06f8e6c95933c05727ec8f4bec563ef7c4fc10ef3e33fa6da`.

## Later upstream PR

Use the prepared native title/body and patch. Validate patch application against the
intended upstream branch and rerun affected checks if rebasing changes the candidate.
Attach or link this evidence bundle, obtain required review/CI, then record the PR,
merge commit and issue scope decision in [the registry](../../../registry.json).
