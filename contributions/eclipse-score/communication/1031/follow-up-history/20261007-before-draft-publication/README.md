# Communication #1031 — Clarify AoU traceability and visibility

Current status: **public_aou_api_verified_production_integration_blocked**. Public AoU API/fixture verified; actual Config Management provider build/TRLC pass. Production safety decisions are deferred at user request to a separate Config Management follow-up; the recorded full-index failure and remaining integration checks are retained. Native migration approval remains pending.

Use the [2026-10-07 native contribution packet](../../../../communication-followup-20261007/README.md),
[final verification](../../../../communication-followup-20261007/verification.md) and
[PR draft](../../../../communication-followup-20261007/pr-communication.md).
The submission patch targets `cef680454e8586daca9f953084dca33fb3759d0c`.
Native owner acceptance and required hosted checks remain pending; no upstream PR
or issue closure is claimed. For #1031, complete production integration remains
incomplete. Memory adequacy, QM/ASIL classification, received-AoU dispositions and safety-record/implementation evidence are explicitly deferred in both PR drafts. The companion remains a draft and #1031 stays open.

The imported patch/draft and status below are **historical**. They are retained
for chronology; apply the new combined patch for the proposed contribution.
The old #1104 normalizer is superseded by the native query correction.

License headers are verified across both complete repositories; both native
copyright checks pass. The final analyzer reports 2,127 findings with zero empty
file URIs. See the packet’s license review and final source-bound evidence.

---


[Upstream issue](https://github.com/eclipse-score/communication/issues/1031), observed open on 2026-10-07.

Status: **draft_imported_integration_pending**. Scoped native AoU/visibility checks retained; real production Config Management/profile and FMEA/LOBSTER integration remain unmeasured.

The [imported queue](../../../../communication-bug-queue-20261006/IMPORT.md)
retains the full original run, failed attempts, corrections, diagnostics and
review history. [Latest recovery handoff](../../../../communication-bug-queue-20261006/recovery-1/RESUME.md)
and [later diagnosis](../../../../communication-bug-queue-20261006/recovery-1/offline-followup/DIAGNOSIS-20261007.md)
provide the chronology. The frozen source inventory identifies the captured bytes.

[Candidate patch](communication-1031.patch) and [original PR draft](pr-description.md)
are copied byte-for-byte from `recovery-1/results/1031`. They are historical proposals;
this import does not perform native execution or declare readiness. Native
baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.

Human review, remaining native checks and qualification are pending. No native
upstream PR, merge or issue closure is performed. Verify retained evidence with
`python3 contributions/shared/scripts/verify_missing_contributions.py` and the repository-wide verifier.
