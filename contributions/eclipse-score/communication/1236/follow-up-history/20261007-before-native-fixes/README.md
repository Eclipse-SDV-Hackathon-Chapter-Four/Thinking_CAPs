# Communication #1236 — Bug: buildifier setup in CI missess some issues

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
`python3 contributions/shared/scripts/verify_missing_contributions.py` and the repository-wide verifier.
