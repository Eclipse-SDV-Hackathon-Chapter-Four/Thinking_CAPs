# Correction 3 of 3 — issue 1062 (final blocker report: no measured source/test defect)

**Issue:** eclipse-score/communication#1062 — *Improvement: E2E protection for Rust Method/Field APIs*
**Mode:** `design` (`.rust-queue/context/task.json`)
**Baseline:** `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
**Platform/config:** Linux only (`linux_x64` → `linux_x64_gcc_15`); no QNX
**Model:** DeepSeek Flash
**Measured stage:** `check 1062 2` (attempt 2) — **failed**; `exit_code = 1`
**Latest bounded native result (operator-supplied):** `.rust-queue/reports/native-check-summary.json`
(`attempt = 2`), raw `job check-2/native-result.json`,
`native_result.sha256 = 1d32a0c1f60fa254727681eaa08f9440464107da3baf364440cce3fe4ef4e8f8`
**Measured subject hash:** `measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`
**Engineering acceptance:** **pending** (not claimed; unchanged)

> **Outcome of this final correction:** the latest bounded native result contains **no measured
> source or test defect** for this correction to repair. Nine of ten checks pass; the single failing
> check is the **lint** row, and it fails with the *same* invocation-level error as attempts 0 and 1
> on a **byte-identical measured subject**. The cause is an **invocation/infrastructure defect**
> (the pinned `clippy_strict` aspect is supplied to Bazel more than once by the measurement command),
> and the issue's implementation remains **blocked on missing design/backend prerequisites**.
> Per the correction rules, **no code was changed, no test was added or removed, and no check was
> weakened**; the blocker is recorded here. Prior failed results (attempts 0 and 1) are retained and
> no counter is reset.

## 1. Latest bounded native result as supplied by the operator (attempt 2)

The operator-supplied bounded summary (`.rust-queue/reports/native-check-summary.json`, `attempt: 2`)
reports `passed: false`, `infrastructure_error: null`, `exit_code: 1`, with 10 checks:

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
Only the lint row fails. No failure in rows 1–9, and no new source/test failure, is present.

## 2. Determination: repeated *unchanged* failure (third independent measurement)

Three independent facts establish that this is the same failure on the same subject, not a source or
test regression:

1. **Measured subject hash is byte-identical across all three attempts.** Attempt 0, attempt 1 and
   attempt 2 each report
   `measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`.
   The subject that was measured did not change between `check0`, `check1` and `check2`.
2. **The failing row and its signature are byte-identical.** The lint `bounded_tail` at attempt 2
   contains the same ordered sequence as attempts 0 and 1:
   `Duplicate rc file: …/quality/static_analysis/static_analysis.bazelrc is read multiple times` →
   `configs expanded more than once: [_lint]` →
   `ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once` →
   `errors encountered while analyzing target …, it will not be built` →
   `command succeeded, but not all targets were analyzed`, `exit 1`.
3. **Only the lint row differs from the passing rows**, and it differs by failing during Bazel
   *analysis* (before any action runs on the three targets), so no Clippy diagnostic for any source
   file was produced at all.

Because the subject is unchanged and the failure is unchanged, this is a **repeated unchanged
failure**. Per the workflow (*"stop on … a repeated unchanged failure"*; *"Before broadening a
failing run, determine whether the subject changed or a relevant concern remains"*), a further
identical rerun is not productive, and there is **no measured source or test defect** for this
correction to repair.

## 3. Root cause of the failing lint row: duplicate pinned `clippy_strict` aspect (invocation, not source)

In-repo truth at the bound baseline (re-read this stage, bounded):

- `.bazelrc:188` imports `quality/static_analysis/static_analysis.bazelrc` **exactly once**.
  The other imports at lines 186–187 target coverage/sanitizer; lines 200/203 are `try-import`s of
  unrelated files. `.bazelrc.ai_checker` defines no clippy aspect.
- `quality/static_analysis/static_analysis.bazelrc:29-30` declares the aspect **once**:
  `build:clippy --config=_lint` and
  `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`.
- `build:_lint` (lines 15–18) sets only toolchain/output-group/fail-on-violation/keep-going flags;
  it does **not** declare the aspect.

Therefore the repository config is single-sourced and correct: a single
`bazel build --config=clippy <targets>` (or the documented `bazel test --config=clippy //...`)
applies `clippy_strict` exactly once. The observed
`configs expanded more than once: [_lint]` **together with**
`aspect … added more than once` can only arise if the *invocation* applied the `clippy` config (or the
aspect flag) more than once — i.e. a **command-construction / harness invocation defect**, not a
repository defect.

Consequences:

- The failure is **not** a property of any `score/mw/com/**` source or test file; analysis aborted
  before any action ran on the three targets.
- It is **not repairable by a source/test patch**. Editing `.bazelrc`, `static_analysis.bazelrc`, the
  pins or the aspect would alter native lint/CI policy (forbidden); trimming the lint check-plan or
  its targets would be weakening a check (equally forbidden).
- The harness records `infrastructure_error: null`, so the lint row is a genuine non-zero check
  result; however its **cause is an invocation defect outside agent authority**
  (*"Command stages and raw evidence are outside agent authority"*), not a measured source/test
  defect.
- No lint suppression, pin change, policy change or `--config` manipulation was made to try to force
  this row green.

**Classification: invocation/infrastructure defect (duplicate pinned `clippy_strict` aspect under a
duplicated `_lint`/`clippy` configuration), not a measured source/test defect.**

## 4. Missing design/backend prerequisites (unchanged from corrections 1 and 2)

Independent of the lint invocation, the issue's stated scope cannot be implemented at this baseline,
so there is no defect in code to correct:

- **Rust `Method<T>` / `Field<T>` API absent.** `interface!` deliberately rejects both arms —
  re-verified this stage at
  `score/mw/com/rust/score_com_concept/interface_macros.rs:110-122`, which emits
  `compile_error!("Method definitions are not supported…")` and the identical
  `compile_error!` for `Field<T>`. The negative compile-fail doctests assert that rejection. Per the
  issue body these are #782 scope. E2E protection cannot be attached to APIs the macro rejects.
- **C++ E2E protection/verification API unpublished.** Maintainer comment `5634513270`
  (LittleHuba, 2026-09-11): the C++ E2E API is still being designed and will be shared later; Rust
  must derive its API from it, and Rust error classes are restricted to what C++ provides.
- **AUTOSAR-spec-derived E2E is licence-restricted** in S-CORE (comment `5634513270`); the fork-only
  AUTOSAR prototype (`5632794860`) is input data, not accepted design or evidence.
- **No accepted E2E design exists** (issue body: "Not designed yet"; "needs a design discussion …
  before implementation"), so the design-mode deliverable is assessment + exported decisions, not
  code.

These reproduce the pending items already recorded in `scope.md` §5, `e2e-design-draft.md` §3,
`implementation.md` §8 and `open-decisions.json` (OD-1…OD-8). Nothing about them changed with the
third failed lint row.

## 5. Correction decision (what was and was not done)

- **No source file changed.** `score/mw/com/**` remains at baseline `381d43d`.
- **No test added/removed and no lint/CI policy, pin, license or aspect edited.**
- **No check-plan change / no check weakening.** `.rust-queue/reports/check-plan.json` already
  conforms to the supplied Linux collector schema
  (`{"checks":[{"kind","targets","reason","native_obligation","config"}]}`, `config = linux_x64`) and
  every target is a real BUILD-derived label; all 9 non-lint checks actually passed under it. The
  lint row is retained as-is (not removed, downgraded or re-labelled) so no check is weakened.
- **No evidence fabricated or rewritten.** `native-check-summary.json` (attempt 2) and the raw
  `native_result` reference/hash are retained unchanged; `correction-1.md` (attempt-0 blocker) and
  `correction-2.md` (attempt-1 blocker) are retained as history.
- **Counters preserved:** this is correction **3 of 3**; attempts **0, 1 and 2** remain failed; global
  attempt/correction counters are not reset.
- **Engineering acceptance remains `pending`.**
- **No new blocker was introduced by this stage**, and none was removed. The blocker is unchanged.

## 6. Concrete next action (operator-side, then re-measure)

1. **Fix the lint invocation (outside agent authority).** Re-run the lint measurement with the pinned
   aspect supplied **exactly once** — e.g. a single
   `bazel test --config=clippy <the 3 BUILD-derived Rust targets>` (optionally combined with the Linux
   toolchain config) **without** re-adding
   `@score_rust_policies//clippy:linters.bzl%clippy_strict`, without a second `--config=_lint` /
   `--config=clippy`, and without re-importing `static_analysis.bazelrc`. This preserves the exact
   native aspect, targets and strictness — it removes only the duplicate flag, so it is **not** a
   check weakening.
2. **Re-measure** under the same baseline and subject hashes; retain attempts 0–2 as history.
3. **Resolve the blocking prerequisites:** obtain the C++ E2E protection/verification API
   (OD-4, OD-5) and land the Rust `Method<T>`/`Field<T>` API (#782, OD-6); then accept the E2E design
   (OD-1…OD-3, OD-7, OD-8) before implementing and running the planned native checks.
4. **Escalation:** the duplicate-aspect invocation is a harness/command-stage issue outside agent
   authority. Do **not** rerun the same command construction; escalate it to the operator. A fourth
   correction on this evidence would be unwarranted: the failure is unchanged across three independent
   measurements and no source/test defect exists to correct.
