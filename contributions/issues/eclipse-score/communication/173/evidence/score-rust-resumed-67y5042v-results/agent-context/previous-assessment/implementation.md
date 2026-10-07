# Implementation record — eclipse-score/communication #173

Issue: *Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate)*
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `assessment` (`task.json`). Platform: Linux only. Engine: DeepSeek Flash.

## 1. Decision: no source change is warranted or authorized

`scope.md` §2 establishes that the issue's premise ("COM-API utilizes the external
`paste` crate") is **already outdated** at this baseline: the interface macros use
`pastey 0.2.3` (`interface_macros.rs:134,146,163,195`; `score_com_concept/BUILD:22`;
`lib.rs:30`; `score_com.rs:144-146`). The migration the issue references already exists.

The issue's remaining substance — *how uncertified external crates are handled*
(integrate into the repo vs. manual implementation) — is a **policy/qualification
decision**. Per the workflow, retain/replace/internal decisions remain reviewable
proposals until accepted by authorized humans, and this task holds no authority to
change dependencies, lockfiles, BUILD files, lint policy or to accept a qualification.
Consequently the smallest issue-scoped deliverable is the required dependency/design
assessment, not a code edit. Adding a Rust regression test would also be a source change
exceeding authority, and the generated-name/ID behavior is already exercised by the
in-tree `validation_tests` (`interface_macros.rs:734+`) and the downstream consumer
BUILD targets enumerated in `check-plan.json`.

No Cargo scaffolding, dependency upgrade, lint suppression or lockfile edit was made.

## 2. Actual changed paths

Only reports under the authorized `.rust-queue/reports/` destination were written.

| Path | Change | Purpose |
| --- | --- | --- |
| `.rust-queue/reports/dependency-assessment.md` | added | Required dependency/design assessment bound to `pastey`, `thiserror`, `futures` and the native tool/component work products. |
| `.rust-queue/reports/implementation.md` | added | This implementation record: changed paths and unresolved concerns. |
| `.rust-queue/reports/review-packet.md` | edited | Packet updated to reference the assessment, record the implementation-stage status and preserve missing evidence. |
| `.rust-queue/reports/scope.md` | unchanged | Scope/binding, premise reconciliation and macro inventory carried as evidence. |
| `.rust-queue/reports/check-plan.json` | unchanged | Already in the required Linux collector schema with BUILD-derived labels; no QNX entries. |

No file outside `.rust-queue/reports/` was created, edited or deleted. No native ID was
invented and no published status/license/pin was altered.

## 3. What was verified this stage (source-backed)

- Issue/comment binding and outdated premise: `issue.json`, `comments.json`, source
  locations above.
- Direct crate consumers: `score_com_concept/BUILD`, `score_com_macros/BUILD`,
  `com-api-example/BUILD`, `basic_rust_api/*/BUILD`.
- Native policy/tooling referenced by the assessment: `CI.md`,
  `quality/static_analysis/static_analysis.bazelrc`, `//:BUILD` (`format_test`),
  `quality/dependency_compatibility_checker/{README.md,config.yaml,BUILD}`,
  `quality/api_surface/README.md`.
- `dump`/`score_com_concept-macros-tests` retains its documented `manual` tag and
  native-link limitation (`score_com_concept/BUILD:46-56`) and must be enumerated, not
  reported as passed.

Content search of `MODULE.bazel.lock` was **not** possible in this session (content
search is bounded to filenames/counts); the index digests for the three crates are
**carried** from the `scope.md` §3 extraction and labelled as carried evidence in
`dependency-assessment.md`.

## 4. Unresolved concerns (carried; not resolved by this task)

1. **Missing native evidence.** `.rust-queue/reports/native-check-summary.json` does not
   exist in this workspace; the native check results referenced by the task are absent.
   No check in `check-plan.json` has been executed by this agent (shell/measurement are
   outside agent authority). All entries remain planned.
2. **Provenance/license/advisories unknown.** `pastey`, `thiserror`/`thiserror-impl` and
   `futures` license, notice, maintenance and advisory status were not verifiable
   (network blocked, nothing vendored). This blocks any retain/replace justification.
3. **Policy decision open.** `score-crates#42` (the linked cross-repo policy issue) and
   the three sub-issues are unreachable; the integrate-vs-manual approach is unresolved
   and requires the repository codeowners plus `score-crates`/process owners.
4. **No tool qualification instance.** Native `wp__tlm_plan` and
   `wp__tool_verification_report` are type definitions only; no project instances exist,
   so applicability and confidence for the host proc-macros are unknown. No
   qualification/confidence decision is asserted.
5. **Dependency-matrix coverage gap.** `//quality/dependency_compatibility_checker`
   covers Bazel modules only and does not include Rust crates; future crate
   compatibility evidence has no native carrier today.
6. **No Rust API-surface lock.** Rust generated-API stability relies on downstream
   compilation targets; there is no committed Rust equivalent of the C++
   `//score/mw/com:api_surface_test`.
7. **Platform coverage.** QNX and sanitizer variants are excluded/unavailable by task
   policy and are recorded as such, not evaluated.

## 5. Status and next action

Technical completion: assessment drafted and consolidated. Native engineering
acceptance (approach decision, qualification, license/provenance sign-off): **pending
offline human decision**. No certification, release/qualified status or confidence
decision is asserted.

Concrete next action: run the `check-plan.json` Linux checks with the bound toolchain and
record `native-check-summary.json`; then fetch `score-crates#42` and the native tool
work-product instances and obtain the human decisions in `review-packet.md`. Keep issue
#173 open; no code or dependency change is authorized here.
