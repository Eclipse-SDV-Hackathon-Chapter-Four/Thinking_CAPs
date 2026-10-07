# Correction 1 of 3 — issue 1062 (blocker report)

**Issue:** eclipse-score/communication#1062 — *Improvement: E2E protection for Rust Method/Field APIs*
**Mode:** `design` (`.rust-queue/context/task.json`)
**Baseline:** `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
**Platform/config:** Linux only (`linux_x64` → `linux_x64_gcc_15`); no QNX
**Model:** DeepSeek Flash
**Measured stage:** `check 1062 0` (attempt 0) — **failed**; `exit_code = 1`
**Native evidence (retained):** `native_result.sha256 = 28c9a8a08112d2698dcbbabf90384cc6a05dce9f4fa6b4da590ba3a4ceb058a2` (job `check-0/native-result.json`)
**Measured subject hash:** `measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`
**Engineering acceptance:** **pending** (not claimed; unchanged)

> **Outcome of this correction:** no source or test defect was found. The single
> failing check is an **invocation/infrastructure defect** (the pinned Clippy aspect is
> supplied to Bazel more than once), plus the already-recorded **missing design/backend
> prerequisites**. Per the correction rules, **no code was changed and no check was
> weakened**; the blocker is recorded here. Prior failed evidence and counters are preserved.

## 1. Bounded native result as supplied by the operator

The operator-supplied bounded summary (`.rust-queue/reports/native-check-summary.json`)
reports `passed: false`, `infrastructure_error: null`, with 10 checks:

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

Only the lint row fails. Rows 1–9 are builds, unit/integration tests and documentation
builds executed on Linux at the bound baseline and are recorded as measured, not asserted.

## 2. Root cause of the failing lint row (invocation, not source/test)

The bounded tail of check 10 contains, in order:

1. `WARNING: The following configs were expanded more than once: [_lint]. For repeatable
   flags, repeats are counted twice and may lead to unexpected behavior.`
2. `ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once`
3. `WARNING: errors encountered while analyzing target '<each of the 3 targets>', it will not be built.`
4. `ERROR: command succeeded, but not all targets were analyzed` → `exit 1`.

The native configuration declares this exact aspect **once**:

- `quality/static_analysis/static_analysis.bazelrc:29-30`
  `build:clippy --config=_lint` and
  `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`

`_lint` is inherited by `clippy` (line 29). The documented native usage is a single
`bazel test --config=clippy //...` (`static_analysis.bazelrc:27-30`), which applies the
aspect exactly once. The warning that `_lint` was expanded twice, together with Bazel's
`aspect ... added more than once` error on the same analysis, shows the failing invocation
supplied the Clippy aspect via **two** paths (the `clippy` config plus an explicit aspect
flag / a second lint config) inside one `bazel build` of the three lint targets.

Therefore:

- The repository's lint/CI policy and pins are **not** defective; the aspect is declared once
  and no lint suppression exists anywhere (`static_analysis.bazelrc` read at baseline).
- The failure is a property of the **command construction / harness invocation**, i.e. the
  operator-side measurement stage — which is outside agent authority
  (“Command stages and raw evidence are outside agent authority”; “Models draft and
  deterministic commands measure”).
- No `score/mw/com/**` source or test file participates in the failure; analysis aborted
  before any action ran on the three targets.
- This is not repairable by a source/test patch. Editing `.bazelrc`,
  `static_analysis.bazelrc`, the pins or the aspect would alter native lint/CI policy, which
  is explicitly forbidden; trimming the lint check-plan or its targets would be weakening a
  check and is equally forbidden.

**Classification: infrastructure/invocation defect (duplicate pinned `clippy_strict`
aspect), not a measured source/test defect.**

## 3. Missing design/backend prerequisites (already open blockers)

Independently of the lint invocation, the issue's stated scope cannot be implemented at this
baseline, so no defect in code exists to correct:

- **Rust `Method<T>` / `Field<T>` API absent.** `interface!` deliberately rejects both arms
  (`score/mw/com/rust/score_com_concept/interface_macros.rs:110-122`); the negative doctests
  assert that rejection. Per issue body, these are #782 scope.
- **C++ E2E protection/verification API unpublished.** Maintainer comment `5634513270`
  (2026-09-11): the C++ E2E API is still being designed and will be shared later; Rust must
  derive its API from it, and Rust error classes are restricted to what C++ provides.
- **AUTOSAR-spec-derived E2E is license-restricted** in S-CORE (comment `5634513270`); the
  fork prototype (`5632794860`) is input data, not accepted design or evidence.
- **No accepted E2E design exists** (issue body: “Not designed yet”), so the design-mode
  deliverable is assessment + exported decisions, not code.

These reproduce the pending items already recorded in `scope.md` §5, `e2e-design-draft.md`
§3, `implementation.md` §8 and `open-decisions.json` (OD-1…OD-8). Nothing about them changed
with the failed lint row.

## 4. Correction decision (what was and was not done)

- **No source file changed.** `score/mw/com/**` remains at baseline `381d43d`.
- **No test added/removed and no lint/CI policy, pin, license or aspect edited.**
- **No check-plan change:** `.rust-queue/reports/check-plan.json` already conforms to the
  supplied Linux collector schema
  (`{"checks":[{"kind","targets","reason","native_obligation","config"}]}`, `config = linux_x64`)
  and every target is a real BUILD-derived label; all 9 non-lint checks actually passed under it.
- **No evidence fabricated or rewritten.** `native-check-summary.json` and the raw
  `native_result` reference/hash are retained unchanged.
- **Counters preserved:** this is correction **1 of 3**; attempt **0** remains failed; global
  attempt/correction counters are not reset.
- **Engineering acceptance remains `pending`.**

## 5. Concrete next action (operator-side, then re-measure)

1. Re-run the lint measurement with the pinned aspect supplied **exactly once** — e.g. the
   documented single-config form `bazel test --config=clippy <the 3 BUILD-derived targets>`
   (optionally combined with the Linux toolchain config, without re-adding
   `@score_rust_policies//clippy:linters.bzl%clippy_strict` or `--config=_lint`/`--config=clippy`
   twice). This preserves the exact native aspect, targets and strictness — it removes only the
   duplicate flag, so it is not a check weakening.
2. Re-measure under the same baseline and subject hashes; retain this failed attempt as history.
3. Keep the design deliverable blocked until the C++ E2E API is published and the Rust
   `Method<T>`/`Field<T>` API (#782) lands, then accept the E2E design (OD-1…OD-8) before
   implementing and running the planned native checks.
