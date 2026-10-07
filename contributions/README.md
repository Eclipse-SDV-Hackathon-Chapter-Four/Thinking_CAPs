# S-CORE and Eclipse SDV contributions

Evidence and artifacts for completed local fixes, their upstream review, and a later
Eclipse SDV Hackathon submission. Inventory initially captured on **2026-10-04**; consolidated additions on **2026-10-07**.

| Project / issue | Contribution | Local result | Upstream / next action |
| --- | --- | --- | --- |
| [SOME/IP #84](remediation/someip-84-publication/README.md) | Full identity/discovery implementation with eight proposed native component requirements | Full build and 722 SOCom cases pass; 177 linked cases; all 243 code/build headers checked | [Draft PR #322](https://github.com/eclipse-score/inc_someip_gateway/pull/322) for user review; ECA passed; requirement/IP review, integration and CI pending |
| [Lifecycle #704](issues/eclipse-score/lifecycle/704/README.md) | Generate three communication configurations from shared definitions | Fabro/DeepSeek Flash patch verified; 113 native cases pass; scoped local owner approval recorded | Issue open; upstream-template PR body and title prepared; upstream review/CI pending |
| [Diagnostics #16](issues/eclipse-score/inc_diagnostics/16/README.md) | Diagnostic API to OpenSOVD provider adapter | Five patches recovered; native validation pending | [Native PR #40](https://github.com/eclipse-score/inc_diagnostics/pull/40) open; actual ECA check fails; author DCO, IP disposition and native validation pending |
| [Communication #1265](issues/eclipse-score/communication/1265/engineering-review/score-rust-engineering-review-kohskpez/README.md) | Assess Rust COM identifier-pasting dependency; generic Rust workflow retained | Documentation patch; six Linux integration cases passed; agent engineering review complete, retain pastey0.2.3 recommended | Issue open; exact compiler qualification/adoption and human acceptance pending; historical evidence preserved |
| [Communication #1167](communication-1167/README.md) | COM API idempotency integration test and repository code headers | Six non-QNX fork Host jobs pass; 507 GCC15 tests; zero new-test lint findings. Separate header repair: 2,367 code paths, 91 repaired files, zero code findings; 136 non-code findings remain | [PR #1335](https://github.com/eclipse-score/communication/pull/1335) and [PR #1341](https://github.com/eclipse-score/communication/pull/1341) open; ECA passed; native workflow approval, code-owner review, copyright handling and merge queue pending |
| [S-CORE #3115](issues/eclipse-score/score/3115/README.md) | AI SDLC / SpecKit tooling evaluation using `s-core_sw_fabric` experience | Explicit selection/rationale for all eight tools; native version 3 and complete merge packet; local CI passes | PR #3307 ready for review; one code owner approval required; hosted workflows await maintainer approval; native acceptance pending |
| [S-CORE #2850](issues/eclipse-score/score/2850/README.md) | Native assurance harness MVP | Native adapter, rules/blocks, 30 search + 10 held-out scenarios, full traces, CI and review packet | Stacked adapter follow-up selected; #628 integration, inherited typing debt and human acceptance pending |
| [CDA #543](issues/eclipse-opensovd/classic-diagnostic-adapter/543/README.md) | Replace Option error paths with Result | Patch recovered; snapshot and manifest bound; native testing pending | [Native PR #601](https://github.com/eclipse-opensovd/classic-diagnostic-adapter/pull/601) open; actual ECA check fails; review and current-revision verification pending |
| [Communication #1236](issues/eclipse-score/communication/1236/README.md) | Buildifier CI enforcement | Native warnings repaired; final pinned lint and regression fixtures pass | [PR packet prepared](communication-followup-20261007/README.md); native CI/codeowner review pending |
| [Communication #1031](issues/eclipse-score/communication/1031/README.md) | AoU visibility and traceability | Public API/fixture and real provider consumption verified | [Companion proposal](communication-followup-20261007/pr-config-management.md); full consumer safety integration blocked on owner decisions |
| [Communication #751](issues/eclipse-score/communication/751/README.md) | CodeQL production-source completeness | Current 516/516 inputs hash-match; 218 queries/reporting pass; 508 host tests pass, 7 skipped | [Verification packet](communication-followup-20261007/verification.md); headers verified; hosted/platform CI and review pending |
| [Communication #1104](issues/eclipse-score/communication/1104/README.md) | CodeQL finding locations | Native query restores links; 501 findings preserved and 281 empty URI occurrences removed | [Query fix and full current-suite evidence](communication-followup-20261007/README.md); native review pending |

The first two rows are completed local implementations with retained measurements.
Upstream review, merge and issue closure have their own statuses. The diagnostics row
retains historical recovered patches alongside a distinct published revision and is excluded from the submission's completed-fix count.
The communication assessment was added on **2026-10-06** and is excluded from completed/accepted fix counts.
The tooling evaluation packet was added on **2026-10-07** and is a proposed assessment,
excluded from completed/accepted fix counts. Its scoped offline verifier checks the new
packet and referenced native evidence independently. The initial repository-wide verifier failure is retained in the packet as history.

The [qualification and adoption decision packet](assessment-decisions-20261007/README.md)
sets out proposed dispositions, missing evidence and reviewer roles for #1265 and the
assessment-only entries, including adjacent upstream-owned/unimplemented scopes.
The user [accepted the prepared packet](assessment-decisions-20261007-acceptance.json)
on **2026-10-07**. Native qualification/adoption and engineering acceptance remain
pending; these entries contribute no completed-fix claim.

The 2026-10-07 import reconciles registry metadata with frozen snapshots and restores
a missing, exact-hash original Bazel binary; the current full registry verifier passes.
The inventory covers identifiable contributions in the inspected local factory
handoffs and this repository; add other completed work as its artifacts are recovered.

## Contents

- [registry.json](registry.json): issue identity, scope, baseline, evidence and PR status.
- `issues/<organization>/<project>/<issue>/`: readable record, upstream snapshot,
  provenance, original patches/logs/licenses and SHA-256 artifact manifest.
- [templates/issue.md](templates/issue.md): reusable record for additional issues.
- [Reusable author DCO](DCO.md): Jefferson's signing identity, commit trailer and
  the complete DCO 1.1 text for contribution-specific certification.
- [Evidence gaps](EVIDENCE_GAPS.md): references still needing original artifacts.
- [Native fault-storage write-through packet](fault-storage-write-through/README.md):
  new local preparation, separate from the historic completed-fix inventory above;
  exported patch, native regressions and upstream PR draft, with publication pending.
- [Communication Rust API queue](issues/eclipse-score/communication/rust-api-queue/README.md):
  12 per-issue folders (#1261, #250, #560, #781, #490, #173, #1264, #1263, #794, #782, #1062, #741)
  with sealed evidence, upstream snapshots and PR drafts; portable branch bundles for #1261, #250,
  #560 (Linux-verified) and #781, #490 (drafts). Nothing pushed upstream; acceptance pending.
- [OpenBSW transportRouter packet](openbsw-transport-router/README.md): prepared upstream
  contribution of a diagnostic gateway router module for Eclipse OpenBSW (issue draft,
  signed-off patch, PR description, gate evidence); not yet submitted, no upstream issue yet.
- [Submission checklist](submission/README.md) and [hackathon PR draft](submission/hackathon-pr-description.md).
- [Assessment decisions](assessment-decisions-20261007/README.md): baseline-bound proposals,
  qualification/adoption inputs, empty acceptance-record template and offline verifier.

## Verify the evidence

From the repository root, with Python 3.10 or later:

```bash
python3 scripts/verify_contributions.py
python3 scripts/verify_contributions.py --json
```

The verifier checks every captured file, the current patches, the lifecycle bundle's original
manifest, every entry in the SOME/IP portable manifest and its 269 candidate source
hashes. It reads archives without unpacking or running their contents. A successful
check establishes artifact integrity against the recorded hashes; it does not rerun
native tests or grant engineering acceptance. Git and the manifests travel with the
bundle; no factory installation or workstation paths are needed for verification.

Lifecycle retains the earlier Codex packet alongside the approved Fabro/DeepSeek Flash
implementation and local upstream PR packet. Current registry references select the
approved Flash patch. Missing legacy envelopes and wider unmeasured checks remain explicit.

## Add or update a contribution

1. Create `issues/<organization>/<project>/<issue>/README.md` using the template.
2. Capture the actual upstream issue URL/status/date and implementation baseline.
3. Copy original patches, test commands, logs, results, relevant licenses and notices;
   keep failed attempts and known gaps. Record their source and SHA-256 hashes in
   `artifact-manifest.json` using the existing `files` mapping format.
4. Add a registry entry and a row above. Use `evidence_missing` until evidence exists,
   `implemented_locally` for measured local work, and `merged_upstream` only with the
   actual merged PR URL. Describe partial issue scope explicitly.
5. Run the verifier. Preserve original evidence bytes when adding newer records;
   refresh manifests only for intentional additions, with the reason in provenance.
6. Update PR/review/merge links and the submission draft as contributions advance.

Keep native code PRs directed to their individual upstream projects. The hackathon
PR can collect the contribution records and evidence in one submission. Organizer
destination, submission format and competition eligibility still need confirmation
against the actual competition instructions before submission.


## Consolidated import — 2026-10-07

The consolidated evidence on `main` combines the Rust issue queue,
chatbot #2850, tooling #3115 and newly imported records. It contains **24 issue
records**; this count includes proposals, failed checks and unimplemented scopes.
It is not a count of accepted fixes. Native submissions retain their own status.

- [Communication bug queue](communication-bug-queue-20261006/IMPORT.md): all 11,203
  original regular files retained, including large archive bytes stored as
  deduplicated hash-bound parts. Original failed attempts and later diagnosis remain.
- [#1167 sync history](communication-1167/import-history/2026-10-07-before-sync/sync-record.json):
  seven new publication artifacts, six updated records, all six earlier versions preserved.
- [Import audit](audits/2026-10-07-import-record.json): source hashes, registry
  corrections, original-tool recovery and measured integrity results.

Verify imported bytes and the complete registry from this repository root:

```bash
python3 scripts/verify_missing_contributions.py
python3 scripts/verify_contributions.py --json
```

These checks verify retained artifacts; they rerun no native tests or provider calls
and supply no engineering acceptance. The consolidated contribution branch has been merged into `main`.

## Current Eclipse compliance — 2026-10-07

Use the [current remediation record](compliance/2026-10-07/README.md) and each
registry entry's `prepared_pr_draft` for new submissions. Sealed issue packets and
the initial audit remain historical. All unresolved submissions are marked
`submission_candidate=false`; earlier candidate flags are retained separately.
The verifier checks recovered patch series and separately recorded submitted
heads. It also verifies the restored [OpenBSW transportRouter packet](openbsw-transport-router/README.md)
and native fault-storage packet. Neither is claimed merged or accepted.


## Rust API readiness follow-up — 2026-10-07

[Communication #1261, #250 and #560 completion packet](issues/eclipse-score/communication/rust-api-queue/completion-20261007/README.md)
contains the integrated configured-LoLa contribution, portable source artifacts,
PR draft and exact-source verification results. All 40 changed code files carry
the native Apache-2.0 notices and pass the modified-file checker. The full host
suite passes 510 targets and ASan passes 509, with native skips recorded. The
TSan finding, inherited full-tree notice findings, incomplete macro-test Clippy
coverage, document findings, QCC and human/IP/hosted acceptance remain pending.
The [preceding readiness review](issues/eclipse-score/communication/rust-api-queue/readiness-review-20261007/README.md)
and original proposals remain historical evidence. The contribution remains a
proposal, excluded from accepted-fix counts; broader unconfigured discovery in
#1261 remains open.
