# S-CORE Rust issue review packet — issue #1264 (`thiserror` in the Rust COM API)

Assessment packet. Companion files in this directory: `scope.md` (full findings),
`dependency-assessment.md` (consolidated dependency/design decision package),
`check-plan.json` (native check plan), `implementation.md` (changed paths and unresolved
concerns), `native-check-summary.json` (latest measured native result, attempt 2) and
`correction-1.md` / `correction-2.md` / `correction-3.md` (retained failure/correction
history). No source patch is included.

## Scope and binding

- Issue/repository, retrieval time, source commit and current issue/PR state:
  - eclipse-score/communication#1264, open, unassigned, 0 comments, label `rust-api`,
    parent #173. Source commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
  - Issue/PR activity retrieval was **blocked** (network/collector boundary); no retrieval
    time can be recorded. `context/comments.json` = `[]`.
- User authority, permitted writes/executions, artifact destination and budget limits:
  - File tools only inside the disposable workspace; shell/delegation/publishing/acceptance
    blocked; Linux only; DeepSeek Flash only; no QNX. Artifacts: `.rust-queue/reports/`.
- Process/tailoring/requirement/design/safety/policy versions, hashes and native IDs:
  - score-rust-workflow SKILL v1.0.0; fabric pin `98d1d5f42dad412a09a888ea25e59c62fa6371ce`
    work products `wp__tlm_plan`, `wp__tool_verification_report` (v1/status `valid`, type
    definitions only). Static analysis: `score_rust_policies` 0.0.5 `clippy_strict`.
    **No native requirement/design ID binds the Rust error enums** (traceability gap).
- Source/lock/tool/environment/storage-selection bindings:
  - `MODULE.bazel` line 41 (`score_crates` 0.0.11), `MODULE.bazel.lock` lines 9908–9938
    (thiserror 2.0.21 / thiserror-impl 2.0.21), `.bazelrc` (lockfile_mode=error, Linux
    config, imported static-analysis config). Toolchain: Ferrocene
    `ferrocene_x86_64_unknown_linux_gnu_llvm`, Bazel declared 8.7.0, rules_rust 0.68.2-score.
- Final patch and baseline-to-patched source digest or manifest:
  - None (assessment; no patch). File digests not computed — hashing/collector tools are
    outside agent authority in this run.
- Technical completion status; engineering acceptance status and decision references:
  - Technical: assessment complete; the native plan was **measured twice** (attempts 1 and 2) with the
    same unchanged subject hash: in each, 7 of 8 checks exit 0 and the `lint` check is **blocked by a
    duplicated clippy aspect / `_lint` config in the lint command** (not a source/test defect; see
    `correction-2.md` and the latest `correction-3.md`). Engineering acceptance: **not
    granted / pending offline human decision**.

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact ID and revision | Changed artifact | Required check | Evidence/hash | Gap or proposed disposition |
|---|---|---|---|---|---|
| Record pinned version, features, error types | None found; dependency/macro assessment obligation | None (record in reports) | query `//score/mw/com/rust/score_com_concept:score_com_concept` (resolves the `@score_communication_crate_index//:thiserror` hub edge via the lock) | `scope.md` §3–§4; lock lines 9908–9938 | License text pending; sync 3.0.6 not cross-checked upstream |
| Review behavior, provenance, license, maintenance, safety | Dependency/macro assessment | None | build + test over public crate and consumers | `scope.md` §4–§5 | License/advisories not retrievable (network blocked) |
| Document retain vs implement directly | none scheduled | None | options in `scope.md` §6 | `scope.md` §6 | Decision is a pending human call |
| Record qualification artifacts and API/maintenance impact | `wp__tlm_plan` / `wp__tool_verification_report` (unassigned) | None | `check-plan.json` checks | `scope.md` §7, `check-plan.json` | Tool/component applicability unassigned |

Baseline reconciliation: premise confirmed (thiserror derives on public enums). No PR or
dependents changed the surface. Impact on requirements/design/interfaces: none found, but
"unaffected" is not asserted — it is "no matching requirement/design artifact found".

## Dependency and macro assessment

- Resolved crate: `thiserror` **2.0.21**, features `default`, `std`, edition 2021,
  sha256 `09e52cb86a36cede5cb101bf8908837b3e4c6e5e59fe7fd85c23fb56200d189e`.
  Generator: `thiserror-impl` **2.0.21** proc macro, sha256
  `fe5197923287db20a58125f0bc85c062f7f2c892de97b18c356f9efb14b28524`; deps
  `proc-macro2` 1.0.107, `quote` 1.0.47, `syn` 3.0.6. Build script generated.
- Provenance: crates.io pinned archive, no repo override/patch. License/notice: **unknown**
  (not in checked-in source; registry/archive inspection blocked). Maintenance/advisories:
  **unknown**.
- Invocations: `#[derive(Debug, ScoreDebug, Error)]` + `#[error("...")]` on 7 public enums in
  `score/mw/com/rust/score_com_concept/error.rs`; re-exported through `lib.rs` (`pub use
  error::*`) and `score/mw/com/rust/score_com.rs`. No `#[from]`/`#[source]`; generated
  `Error::source()` chain is therefore absent.
- Failure modes: compile-time attribute errors are detected; silent Display drift is not
  covered by any found test; proc-macro/build-script is a host supply-chain surface.

| Option | Compatibility and build impact | Provenance/license/maintenance | Qualification/verification effort | Proposed rationale and gaps |
|---|---|---|---|---|
| Retain (draft rec.) | None | pinned archive; license/maintenance pending | re-run plan; document | default on current evidence |
| Replace | lock + transitive + semantics change | new provenance to evaluate | full downstream + behavior | no source-backed motivation |
| Internal | removes macro/build-script surface; must hand-reproduce messages | in-repo, no external license | must add Display/behavior tests | only if policy requires; not sourced |

Recommended draft: **retain**; authority for the decision: authorized maintainers/codeowners.

## Verification and expected checks

Full list with targets, reasons and obligations is in `check-plan.json` (query/build/test/docs/lint on
`linux_x64`). Latest collector evidence is in `native-check-summary.json` (measured attempt 2:
`measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`,
the same subject hash measured in attempt 1; `passed: false`, `infrastructure_error: null`).
Measured outcomes (attempt 1 and attempt 2 identical):

| Check | Targets | exit | Result |
|---|---|---|---|
| query ×2 | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | resolved |
| build | `score_com_concept`, `//score/mw/com/rust:score_com` | 0 | built |
| build | runtime, generated `basic_rust_api`, example lib | 0 | built |
| test | `score_com_concept-test`, `-macros-unit-tests`, `com-api-runtime-lola-tests` | 0 | 3/3 pass |
| test | sync/async consumer integration tests, example tokio test | 0 | 3/3 pass |
| docs | `-macros-tests`, `com-api-runtime-lola-doc-tests` | 0 | built |
| **lint** | `score_com_concept` | **1** | **blocked: `aspect ... added more than once` (analysis)**

The `lint` failure is a duplicated `clippy_strict` aspect / `_lint` config in the lint command
(infrastructure/backend prerequisite), not a source or test defect; it reproduced identically in
attempts 1 and 2 on the unchanged subject. The check plan is left unchanged and no passing lint
evidence is claimed. See `correction-2.md` and the latest `correction-3.md`. Baseline and candidate
generated-API compatibility was **not** measured (no candidate patch exists).

## Offline decisions and portable evidence

- Proposed decisions and required reviewers: retain thiserror (draft); license/provenance
  acceptance; tool/component applicability; Display-string contract. Reviewers: native
  maintainers/codeowners, safety/qualification role as applicable.
- Pending acceptance/gaps: partial native evidence (7/8 checks exit 0 in both attempts; `lint` blocked
  by a duplicated clippy aspect in the lint command — see `correction-2.md` and `correction-3.md`);
  license/advisory data; requirement trace; Display-string tests; host/target feature unification; QNX
  explicitly out of scope.
- Packet location: `.rust-queue/reports/` — `scope.md`, `dependency-assessment.md`,
  `check-plan.json`, `implementation.md`, `native-check-summary.json`, `correction-1.md`,
  `correction-2.md`, `correction-3.md`, this file.
- Manifest: file digests and sizes were **not computed** (hashing tools outside agent
  authority); record them from the collector before acceptance.
- Reproduction: see `check-plan.json` targets and the source-bound pin tables in `scope.md`.
- Concrete next action: correct the lint invocation so the pinned `clippy_strict` aspect is applied
  once, re-run `check-plan.json` on baseline `381d43d…` via the bound Linux collector, then obtain the
  offline retain/replace decision.
