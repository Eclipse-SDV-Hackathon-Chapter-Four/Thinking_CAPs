# Communication #751 — Bug: CodeQL ignores some production source files

[Upstream issue](https://github.com/eclipse-score/communication/issues/751), observed open on 2026-10-07.

Status: **draft_imported_linux_checks_review_pending**. Additional corrected candidate: 502 full tests pass, 6 skipped; copyright failure, full candidate query-analysis, QNX and complete production/dependency coverage remain unresolved.

The [imported queue](../../../../communication-bug-queue-20261006/IMPORT.md)
retains the full original run, failed attempts, corrections, diagnostics and
review history. [Latest recovery handoff](../../../../communication-bug-queue-20261006/recovery-1/RESUME.md)
and [later diagnosis](../../../../communication-bug-queue-20261006/recovery-1/offline-followup/DIAGNOSIS-20261007.md)
provide the chronology. The frozen source inventory identifies the captured bytes.

[Candidate patch](communication-751.patch) and [original PR draft](pr-description.md)
are copied byte-for-byte from `recovery-1/additional-751/results/751`. They are historical proposals;
this import does not perform native execution or declare readiness. Native
baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.

Human review, remaining native checks and qualification are pending. No native
upstream PR, merge or issue closure is performed. Verify retained evidence with
`python3 scripts/verify_missing_contributions.py` and the repository-wide verifier.
