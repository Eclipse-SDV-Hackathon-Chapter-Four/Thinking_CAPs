# Implementation report — issue #1264 (`thiserror` usage in the Rust COM API)

## Outcome

Task mode is **assessment** (`task.json` `"mode": "assessment"`; `scope.md` §1). The issue requests a
dependency/design assessment of the `thiserror` derives on the public COM error enums, not a code change.
This run therefore **delivers an assessment and makes no source-code change**. The premise (derives in
place) is already implemented at the baseline; only the assessment/decision was missing, so the
"smallest warranted change" is documentation, and existing code was left untouched to avoid duplicating
or perturbing public API behavior.

## Actual changed paths

All changes are inside the authorized artifact directory `.rust-queue/reports/`. No file under
`score/`, `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelrc`, CI config or lint policy was modified.

| Path | Change | Purpose |
|------|--------|---------|
| `.rust-queue/reports/dependency-assessment.md` | **New** | Consolidated source-bound dependency/design assessment answering all four acceptance criteria: pinned version/features/checksums, 7 public enums / 32 variants, generated `Display`/`Error` behavior, provenance/license/maintenance/safety, retain-vs-replace-vs-internal comparison with a draft recommendation, and qualification/tool-role obligations. |
| `.rust-queue/reports/implementation.md` | **New** (this file) | Records actual changed paths, the no-source-patch rationale and the unresolved concerns. |
| `.rust-queue/reports/check-plan.json` | **Edited (4 `native_obligation` strings)** | Replaced unsourceable CI "job name" strings with the actual observed workflow files/commands: `_build_and_test_gcc15.yml` (`bazel build|test --config=ci //...`) and `_linter.yml` matrix id `clippy` (`aspect lint --config=clippy` → `@score_rust_policies//clippy:linters.bzl%clippy_strict`). Targets, kinds, reasons and `config` are unchanged; JSON schema `{"checks":[{"kind","targets","reason","native_obligation","config"}]}` preserved. |
| `.rust-queue/reports/review-packet.md` | **Edited (companion list)** | Cross-references the two new companion files so the offline packet is self-contained. |

No `implementation.md`-declared source/API/lock change exists. Generated-API compatibility was **not**
measured on a candidate because there is no candidate (no patch).

## Why no source change

- `scope.md` §6 and `dependency-assessment.md` §6 show no source-backed defect, maintenance advisory or
  native policy that motivates replacing or hand-implementing the derives. The guidance is explicit:
  avoid replacing derives without a source-backed API/maintenance rationale.
- Replacing the derive changes public, re-exported behavior (`Error`/`Result` in `score/mw/com/rust/score_com.rs`)
  and the lock/transitive set; that is out of scope for a documentation/qualification issue.
- Hand-implementing `Display`/`Error` would add ~32 hand-maintained messages and new qualification
  obligations, and is only justified by a native requirement that was not found.
- Adding a `Display`-regression test would be a product change the issue does not authorize and could not
  be executed/verified in this run (shell blocked). It is recorded as a pending follow-up instead of a
  guessed, un-runnable test.

## Verification status

- No check from `check-plan.json` was executed. `.rust-queue/reports/native-check-summary.json` is **absent**;
  its absence is preserved as missing evidence, not filled in.
- Network retrieval (GitHub, crates.io, raw upstream license text) was re-attempted and **rejected at the
  tool boundary** in this run, so license text and dated maintenance/advisory review remain **unknown**.
- `context/comments.json` is `[]`; fresh issue/PR activity could not be reconciled.
- All results in `dependency-assessment.md` are source-anchored observations or explicitly-unknown values.
  Nothing is marked qualified/accepted/passing.
- **Update (correction 2):** the plan has since been measured once (attempt 1). See
  `native-check-summary.json`, the review packet's measured-outcomes table and `correction-2.md`:
  7/8 checks exit 0; the `lint` check is blocked by a duplicated `clippy_strict` aspect in the lint
  command (infrastructure, not a source/test defect). No passing lint evidence is claimed.
- **Update (correction 3):** the plan was re-measured (attempt 2) on the unchanged subject hash
  (`3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`) with the identical outcome:
  7/8 checks exit 0 and the same `lint` analysis-phase failure (`aspect ... added more than once`).
  This is a repeated unchanged failure and a backend/collector prerequisite gap, not a source/test
  defect; no code, check or status was changed. See `correction-3.md`. No passing lint evidence is
  claimed and the engineering decision remains pending offline acceptance.

## Unresolved concerns

1. **Engineering decision open:** retain vs replace vs hand-implement `thiserror` (draft recommendation:
   retain on current evidence). Requires an authorized human/codeowner of `score/mw/com/rust`.
2. **License/provenance unverified:** no in-repo `thiserror` license/notice; archive/registry unreachable.
   The pinned archive sha256 and URLs are recorded, but the license text is not.
3. **Maintenance/advisories unknown:** dated upstream/maintainer review not possible (network blocked).
4. **Native traceability gap:** no requirement/design artifact names the Rust error enums or their
   `Display` strings; the issue-template "unaffected" checkbox is not treated as evidence.
5. **Tool/component applicability unassigned:** fabric work products `wp__tlm_plan` /
   `wp__tool_verification_report` are v1/`valid` type definitions; whether they apply to the
   `thiserror-impl` host macro and/or the target library is an unaccepted human decision.
6. **`Display`-string contract undecided:** no baseline test asserts any message; whether messages are a
   contract needing a requirement ID + regression tests is pending.
7. **Host/target feature unification not separately measured** for `thiserror-impl`.
8. **No collector evidence:** the check plan is expected only; build/test/docs/lint results are unrun.
9. **QNX explicitly out of scope** for this run; Linux results cannot satisfy QNX obligations.

## Pending offline acceptance

Technical completion of this assessment does **not** constitute native engineering acceptance. Every
decision in `dependency-assessment.md` §10 remains pending, and no native work product is marked
evaluated/qualified/released. Next action: run `check-plan.json` via the bound Linux collector on baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e` (no patch), capture raw evidence into `native-check-summary.json`,
then obtain the offline retain/replace decision.
