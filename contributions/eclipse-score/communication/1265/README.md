# Communication #1265 — Rust identifier-pasting assessment

A local documentation patch and reusable S-CORE Rust workflow are prepared for
[communication #1265](https://github.com/eclipse-score/communication/issues/1265).
The selected communication baseline already uses **pastey 0.2.3**. The patch records
its exact dependency configuration, four identifier forms, provenance and licenses,
maintenance/safety implications, three design alternatives, and existing S-CORE
classification/AoU/qualification obligations. It proposes retaining the current locked
crate while completing communication-specific adoption and offline engineering review.

**Status:** assessment implemented locally; native verification failed before execution;
engineering acceptance and upstream submission pending. This record is excluded from
completed/accepted fix counts. No upstream issue, PR or repository was modified.

## Artifacts

- [Native patch](communication-1265.patch), [changed files](candidate-hashes.json),
  [patch applicability](patch-apply-check.json) and
  [assessment](candidate/score/mw/com/rust/design/identifier_pasting_assessment.md).
- [Generic Rust workflow](workflow/score-rust-workflow/SKILL.md): use
  `$score-rust-workflow` for Rust issues across S-CORE repositories. It covers defects,
  APIs, unsafe/FFI, concurrency, platforms, documentation and dependencies. The factory
  copy is `.agents/skills/score-rust-workflow`; a local Codex skills symlink is installed.
- [Verification report](verification-report.json),
  [direct local static measurements](static-verification.json),
  [supervisor review](supervisor-review.md), [correction ledger](correction-ledger.json).
- [Review packet](review-packet.md), [PR draft](pr-description.md),
  [issue snapshot](upstream-snapshot.json), [provenance](provenance.json),
  [artifact manifest](artifact-manifest.json), [file sizes](artifact-sizes.json), [licenses](licenses/).
- `sources/`: checksum-pinned native source archives, crate archives/full crate sources,
  upstream classification/architecture/requirements/AoU/test sources and repository
  metadata observations. Published native statuses are retained as source assertions.
- `execution/`: exact command-only Fabro graph/configuration, frozen inputs, native
  run/event/stage responses and raw failure logs. Private tokens and server database
  are excluded. These scripts retain original execution paths for audit; they are not
  a portable one-command replay launcher.

## Verification and supervision

The patch passes `git apply --check` against communication
`e3d126c2d7569345cf5f790310702eb00cd86b06`. Direct local hashing verifies all **2,879**
candidate subjects against the frozen map: one existing README changed, one assessment
added, no source deleted. Production Rust, dependency locks and policy bytes are unchanged.
These are static checks outside Fabro; they are not Rust test results.

Native Fabro run `01M475MP83BBNK7VHZ3231Z657`, workflow version
`58e12f36e3afe57027375342152381e4105a12a5da81ba0571a9b3a28b851280`, had explicit
read-only supervisor `/root/rust_issue_supervisor`, zero provider usage and no paid,
agent or human-approval nodes. `verify` and `export` both failed during storage validation:
the sanitized PATH omitted `/usr/sbin`, so `losetup` could not be launched. **No Bazel
or Rust native tests ran. The collector did not generate its verification/export files.**
Fabro's terminal lifecycle says `succeeded` because the graph routed failures to its exit;
that status does not imply verification success. This packet was exported separately
outside Fabro after termination and preserves both failures.

The user authorized at most **three fixes**. All three were consumed (guarded source
extraction, preserving final-newline diff semantics, correct Fabro graph entrypoint).
No repair, relaunch or native execution outside Fabro was used to bypass the exhausted
limit. The frozen binding's descriptive pre-execution count still says 2; the actual
ledger and final accounting say 3. Its original bytes are retained and the discrepancy
is disclosed. The owned private server is stopped; scratch remains bound to the selected
external Linux build volume.

## Remaining review

Review the proposed dependency decision and communication-specific adoption/qualification
scope offline, including the certified compiler AoU, trace parsing limitation, tool
management applicability and platform coverage. Native macro/unit/manual doctest,
copyright, full CI and separate score-crates qualification test evidence remain missing;
no advisory database sweep was performed. Source hashes, tests or Fabro termination cannot
substitute for engineering acceptance. A future corrected native run needs fresh task
authority beyond this run's exhausted three-fix limit. Upstream ECA/review/CI remains pending.

From the hackathon repository root, `python3 contributions/shared/scripts/verify_contributions.py` verifies
retained artifact hashes. It does not rerun native checks or accept engineering decisions.
