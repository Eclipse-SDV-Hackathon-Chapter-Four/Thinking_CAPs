# Correction 2 of 3 — issue 1062 (blocker report: repeated unchanged failure)

**Issue:** eclipse-score/communication#1062 — *Improvement: E2E protection for Rust Method/Field APIs*
**Mode:** `design` (`.rust-queue/context/task.json`)
**Baseline:** `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
**Platform/config:** Linux only (`linux_x64` → `linux_x64_gcc_15`); no QNX
**Model:** DeepSeek Flash
**Measured stage:** `check 1062 1` (attempt 1) — **failed**; `exit_code = 1`
**Native evidence (retained, latest as supplied):**
`.rust-queue/reports/native-check-summary.json` (`attempt = 1`), raw
`job check-1/native-result.json`, `native_result.sha256 = fd882dbaf05022f01006f6583f7ba8edfda2bbc16bfe45a24fc06d1d6301f43a`
**Measured subject hash:** `measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`
**Engineering acceptance:** **pending** (not claimed; unchanged)

> **Outcome of this correction:** no **measured source/test defect** exists to correct. The
> only failing check is the **lint** row, and it fails with the *same* invocation-level
> error as attempt 0 on an **unchanged measured subject**. The cause is the pinned Clippy
> aspect being supplied to Bazel **more than once** by the measurement invocation (outside
> agent authority), together with the design/backend prerequisites that remain missing.
> Per the correction rules, **no code was changed, no test was added, and no check was
> weakened**; the blocker is recorded here. Prior failed results are retained.

## 1. Latest bounded native result as supplied by the operator (attempt 1)

The operator-supplied bounded summary (`.rust-queue/reports/native-check-summary.json`,
`attempt: 1`) reports `passed: false`, `infrastructure_error: null`, `exit_code: 1`, with 10 checks:

| # | Kind | Targets | Exit | Result |
| --- | --- | --- | --- | --- |
| 1 | build | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | PASS |
| 2 | build | `//score/mw/com/rust:score_com`, `//score/mw/com/rust:score_com_mock` | 0 | PASS |
| 3 | build | `.../com-api-runtime-lola:com-api-runtime-lola`, `.../com-api-ffi-lola:bridge_ffi_rs`, `.../com-api-ffi-lola:bridge_ffi_lola` | 0 | PASS |
| 4 | build | `//score/mw/com/rust/score_com_cpp_bridge:register_interface` | 0 | PASS |
| 5 | test | `.../score_com_concept:score_com_concept-test`, `...:score_com_concept-macros-unit-tests` | 0 | PASS (2/2) |
| 6 | test | `.../com-api-runtime-lola:com-api-runtime-lola-tests` | 0 | PASS (1/1) |
| 7 | test | `.../consumer_sync_apis/integration_test:test_com_api_sync`, `.../consumer_async_apis/integration_test:test_com_api_async` | 0 | PASS (2/2) |
| 8 | docs | `.../com-api-runtime-lola:com-api-runtime-lola-doc-tests`, `...:score_com_concept-macros-tests` | 0 | PASS |
| 9 | docs | `//docs/sphinx:sphinx_doc` | 0 | PASS |
| 10 | **lint** | `.../score_com_concept:score_com_concept`, `//score/mw/com/rust:score_com`, `.../com-api-runtime-lola:com-api-runtime-lola` | **1** | **FAIL** |

Rows 1–9 executed on Linux at the bound baseline and are recorded as measured, not asserted.
Only the lint row fails.

## 2. Determination: repeated *unchanged* failure

Two independent facts establish that this is the same failure on the same subject, not a new
source/test regression:

1. **Measured subject hash is byte-identical across attempts.** Attempt 0 reported
   `measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`;
   attempt 1 reports the **same** value. The subject that was measured did not change between
   `check0` and `check1`.
2. **The failing row and its signature are byte-identical.** The lint `bounded_tail` at attempt 1
   contains the same error sequence as attempt 0 (
   `configs expanded more than once: [_lint]` →
   `ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once` →
   `errors encountered while analyzing target …` → `command succeeded, but not all targets were
   analyzed`, `exit 1`).

Because the subject is unchanged and the failure is unchanged, this is a **repeated unchanged
failure**. Per the workflow (*"stop on … a repeated unchanged failure"*), a further identical
rerun is not productive, and there is **no measured source or test defect** for this correction to
repair.

## 3. Root cause of the failing lint row: duplicate pinned `clippy_strict` aspect (invocation, not source)

The lint `bounded_tail` at attempt 1 contains, in order:

1. `WARNING: Duplicate rc file: …/quality/static_analysis/static_analysis.bazelrc is read multiple
   times, it is a standard rc file location but must have been unnecessarily imported earlier.`
   (this warning is emitted on **every** check, including the passing builds, so by itself it is benign)
2. `WARNING: The following configs were expanded more than once: [_lint].`
3. `ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once`
4. `WARNING: errors encountered while analyzing target '<each of the 3 lint targets>', it will not be built.`
5. `ERROR: command succeeded, but not all targets were analyzed` → `exit 1`.

In-repo truth at the bound baseline (re-read this stage, bounded):

- `.bazelrc:188` imports `quality/static_analysis/static_analysis.bazelrc` **exactly once**
  (a second `try-import` at lines 200/203 targets unrelated files).
- `quality/static_analysis/static_analysis.bazelrc:29-30` defines the aspect **once**:
  `build:clippy --config=_lint` and
  `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`.
- `build:_lint` (lines 15-18) sets only toolchain/output-group/fail-on-violation/keep-going flags;
  it does **not** declare the aspect.

Therefore the repository config is single-sourced and correct: a single
`bazel build --config=clippy <targets>` applies `clippy_strict` exactly once. The observed
`configs expanded more than once: [_lint]` **plus** `aspect … added more than once` can only arise if
the *invocation* applied the `clippy` config (or the aspect flag) twice — i.e. a
**command-construction / harness invocation defect**, not a repository defect.

Consequences:

- The failure is **not** a property of any `score/mw/com/**` source or test file; analysis aborted
  before any action ran on the three targets.
- It is **not repairable by a source/test patch**. Editing `.bazelrc`, `static_analysis.bazelrc`,
  the pins or the aspect would alter native lint/CI policy (forbidden); trimming the lint check-plan
  or its targets would be weakening a check (equally forbidden).
- The harness itself records `infrastructure_error: null`, so the lint row is a genuine non-zero
  check result; however its **cause is an invocation defect outside agent authority**
  (*"Command stages and raw evidence are outside agent authority"*), not a measured source/test defect.
- No lint suppression, pin change or policy change was made to try to force this row green.

**Classification: invocation/infrastructure defect (duplicate pinned `clippy_strict` aspect under a
duplicated `_lint`/`clippy` configuration), not a measured source/test defect.**

## 4. Missing design/backend prerequisites (unchanged from correction 1)

Independent of the lint invocation, the issue's stated scope cannot be implemented at this baseline,
so there is no defect in code to correct:

- **Rust `Method<T>` / `Field<T>` API absent.** `interface!` deliberately rejects both arms; the
  negative doctests assert that rejection. Per the issue body these are #782 scope.
- **C++ E2E protection/verification API unpublished.** Maintainer comment `5634513270`
  (2026-09-11): the C++ E2E API is still being designed and will be shared later; Rust must derive
  its API from it, and Rust error classes are restricted to what C++ provides.
- **AUTOSAR-spec-derived E2E is license-restricted in S-CORE** (comment `5634513270`); the fork
  prototype (`5632794860`) is input data, not accepted design or evidence.
- **No accepted E2E design exists** (issue body: "Not designed yet"), so the design-mode deliverable
  is assessment + exported decisions, not code.

These reproduce the pending items already recorded in `scope.md` §5, `e2e-design-draft.md` §3,
`implementation.md` §8 and `open-decisions.json` (OD-1…OD-8). Nothing about them changed with the
second failed lint row.

## 5. Correction decision (what was and was not done)

- **No source file changed.** `score/mw/com/**` remains at baseline `381d43d`.
- **No test added/removed and no lint/CI policy, pin, license or aspect edited.**
- **No check-plan change.** `.rust-queue/reports/check-plan.json` already conforms to the supplied
  Linux collector schema
  (`{"checks":[{"kind","targets","reason","native_obligation","config"}]}`, `config = linux_x64`)
  and every target is a real BUILD-derived label; all 9 non-lint checks actually passed under it.
  The lint row is retained as-is (not removed, downgraded or re-labelled) so no check is weakened.
- **No evidence fabricated or rewritten.** `native-check-summary.json` (attempt 1) and the raw
  `native_result` reference/hash are retained unchanged; `correction-1.md` (attempt-0 blocker report)
  is retained as history.
- **Counters preserved:** this is correction **2 of 3**; attempts **0 and 1** remain failed; global
  attempt/correction counters are not reset.
- **Engineering acceptance remains `pending`.**

## 6. Concrete next action (operator-side, then re-measure)

1. Re-run the lint measurement with the pinned aspect supplied **exactly once** — e.g. a single
   `bazel test --config=clippy <the 3 BUILD-derived Rust targets>` (optionally combined with the
   Linux toolchain config) **without** re-adding
   `@score_rust_policies//clippy:linters.bzl%clippy_strict`, without a second `--config=_lint` /
   `--config=clippy`, and without re-importing `static_analysis.bazelrc`. This preserves the exact
   native aspect, targets and strictness — it removes only the duplicate flag, so it is **not** a
   check weakening. This is a command-stage/harness change and is outside agent authority.
2. Re-measure under the same baseline and subject hashes; retain this failed attempt as history.
3. Keep the design deliverable blocked until the C++ E2E API is published and the Rust
   `Method<T>`/`Field<T>` API (#782) lands; then accept the E2E design (OD-1…OD-8) before
   implementing and running the planned native checks.
4. A **third** correction is **not warranted** on this evidence: the failure is unchanged and no
   source/test defect exists. Escalate the duplicate-aspect invocation to the operator rather than
   rerunning the same construction again.
