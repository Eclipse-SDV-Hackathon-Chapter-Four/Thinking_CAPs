# Communication #1236 — Bug: buildifier setup in CI missess some issues

Current status: **native_lint_fixed_review_pending**. Native buildifier and regression fixtures pass; 27 original warnings repaired. Final-source checks and native CI/codeowner review tracked in follow-up.

Use the [2026-10-07 native contribution packet](../../../../communication-followup-20261007/README.md),
[final verification](../../../../communication-followup-20261007/verification.md) and
[PR draft](../../../../communication-followup-20261007/pr-communication.md).
The submission patch targets `cef680454e8586daca9f953084dca33fb3759d0c`.
Native owner acceptance and required hosted checks remain pending.
[Draft PR #1342](https://github.com/eclipse-score/communication/pull/1342) is open for user review; no merge or issue closure is claimed. For #1031, complete production integration remains
incomplete; production safety decisions are explicitly deferred in the PR.

The imported patch/draft and status below are **historical**. They are retained
for chronology; apply the new combined patch for the proposed contribution.
The old #1104 normalizer is superseded by the native query correction.

License headers are verified across both complete repositories; both native
copyright checks pass. The final analyzer reports 2,127 findings with zero empty
file URIs. See the packet’s license review and final source-bound evidence.

---


[Upstream issue](https://github.com/eclipse-score/communication/issues/1236), observed open on 2026-10-07.

Status: **draft_imported_native_lint_failure**. Global buildifier enforcement remains failed on 27 unchanged native source subjects.

The [imported queue](../../../../communication-bug-queue-20261006/IMPORT.md)
retains the full original run, failed attempts, corrections, diagnostics and
review history. [Latest recovery handoff](../../../../communication-bug-queue-20261006/recovery-1/RESUME.md)
and [later diagnosis](../../../../communication-bug-queue-20261006/recovery-1/offline-followup/DIAGNOSIS-20261007.md)
provide the chronology. The frozen source inventory identifies the captured bytes.

[Candidate patch](communication-1236.patch) and [original PR draft](pr-description.md)
are copied byte-for-byte from `recovery-1/results/1236`. They are historical proposals;
this import does not perform native execution or declare readiness. Native
baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.

Human review, remaining native checks and qualification are pending. No native
upstream PR, merge or issue closure is performed. Verify retained evidence with
`python3 scripts/verify_missing_contributions.py` and the repository-wide verifier.
