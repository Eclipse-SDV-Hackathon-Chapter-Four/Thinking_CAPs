# Correction 2 — issue #1264 (`thiserror` usage in the Rust COM API)

Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Mode: assessment (no product source patch). Platform: Linux `linux_x64`. No QNX. DeepSeek Flash only.
Evidence of record: the latest bounded native result summary supplied by the operator —
`.rust-queue/reports/native-check-summary.json` (`attempt: 1`, `passed: false`,
`infrastructure_error: null`, `measured_subject_hashes_sha256 =
3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`; raw result
`jobs/1264/execution/check-1/native-result.json`, sha256
`3af57aac77cf53a810c89c5b37d8fd23731022ab8b275c267994e54f057cb26c`).

## Prior failed results retained (not reset)

- **check0** — collector `AssertionError` at `driver_linux.py` line 87 on the `check-plan.json`
  schema (an external `@score_communication_crate_index//:thiserror` label in `targets[]`). Retained
  in `correction-1.md`. Correction 1 rewrote every `targets[]` entry to the `//package:target` form.
- **check1** — native run of the corrected plan: overall `passed: false`. Seven of eight checks
  exited 0; the `lint` check exited 1. Retained here and in `native-check-summary.json`; no passing
  evidence is fabricated and no counter is reset.

## Measured attempt-1 outcomes (from the operator's summary)

| # | kind  | targets (abbreviated) | exit | outcome |
|---|-------|-----------------------|------|---------|
| 1 | query | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | resolved |
| 2 | query | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | resolved |
| 3 | build | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/rust:score_com` | 0 | build succeeded |
| 4 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola`, `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`, `//score/mw/com/example/com-api-example:com-api-example-lib` | 0 | build succeeded |
| 5 | test  | `...:score_com_concept-test`, `...:score_com_concept-macros-unit-tests`, `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | 0 | 3 tests pass |
| 6 | test  | `...consumer_sync_apis/integration_test:test_com_api_sync`, `...consumer_async_apis/integration_test:test_com_api_async`, `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | 0 | 3 tests pass |
| 7 | docs  | `...:score_com_concept-macros-tests`, `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | 0 | build succeeded |
| 8 | lint  | `//score/mw/com/rust/score_com_concept:score_com_concept` | **1** | **Bazel analysis error (aspect added more than once)** |

The compiler/runtime evidence in checks 3–6 is real and shows the pinned `thiserror` 2.0.21 edge
(`[285 / 290] Compiling Rust proc-macro thiserror_impl v2.0.21`, `[286 / 290] ... thiserror v2.0.21`)
building and the public error-enum tests passing on this baseline.

## Defect determination: the failing check is not a source/test defect

The `lint` invocation failed during Bazel's **analysis phase**, before any clippy action ran:

```text
WARNING: The following configs were expanded more than once: [_lint]. For repeatable flags,
         repeats are counted twice and may lead to unexpected behavior.
...
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
...
WARNING: errors encountered while analyzing target
         '//score/mw/com/rust/score_com_concept:score_com_concept', it will not be built.
Target //score/mw/com/rust/score_com_concept:score_com_concept up-to-date:
  bazel-bin/score/mw/com/rust/score_com_concept/libscore_com_concept-1105774421.rlib
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

Facts, source-anchored:

- The failure is a Bazel option/config error, not a clippy finding: the pinned aspect
  `@score_rust_policies//clippy:linters.bzl%clippy_strict` and the shared `_lint` config were each
  supplied to the lint command **more than once** (`aspect ... added more than once`,
  `configs ... expanded more than once: [_lint]`).
- The repository defines that aspect exactly once, in
  `quality/static_analysis/static_analysis.bazelrc` lines 29–30
  (`build:clippy --config=_lint` / `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`).
  No `BUILD` file or package-level `.bzl` adds it again; the only `linters.bzl` in the tree is
  `tools/lint/linters.bzl`, which defines the clang-tidy and ruff aspects. The `score_com_concept`
  `rust_library` declares no lint/aspect and simply uses `@score_communication_crate_index//:thiserror`.
- The error occurs before analysis completes, so the check produced **no clippy diagnostics about the
  source**; the analyzed target is reported up-to-date (already compiled by check 3). A compilation or
  lint defect in the source would surface as a rule/build failure with diagnostics, not as a duplicated
  aspect at option parsing.
- Every source-facing check passed with exit 0 (checks 1–7): the owning crate, the public re-export,
  representative downstream consumers, unit tests, integration tests and rustdoc targets.

Conclusion: the `lint` check was **blocked by an invocation/configuration duplication in the lint
command** (an infrastructure/collector-side prerequisite), not by any defect in the source, tests,
BUILD, lockfile, CI, or lint policy. It is therefore not a measured source/test defect to correct.

## Action taken: none — blocker recorded

The correction-2 rule is to correct only a measured source/test defect and, when the evidence shows an
infrastructure/backend prerequisite is missing, to **not** change code or weaken checks. Accordingly:

- No product source, `BUILD`, `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelrc`, CI workflow or lint
  policy was modified.
- `.rust-queue/reports/check-plan.json` is **unchanged**. Its `lint` entry is source-backed by
  `.github/workflows/_linter.yml` (matrix id `clippy`; `aspect lint --bazel-flag=--config=clippy`)
  selecting the pinned `clippy_strict` aspect. Removing the check, changing its `kind`, or repointing
  its target would drop the pinned-lint obligation and is a prohibited weakening. The check stays in the
  plan as expected-but-blocked.
- No passing lint evidence is claimed. `native-check-summary.json` retains the measured failure, and the
  overall stage remains `passed: false`.

Non-blocking observation (left as-is): correction 1 gave the second `query` check the same in-repo
target as the first (`//score/mw/com/rust/score_com_concept:score_com_concept`), so the two query
checks are now redundant. Both exited 0; this is not a measured defect and no change is made.

## Blocker (outside agent authority)

- **Blocked check:** `lint` on `//score/mw/com/rust/score_com_concept:score_com_concept`.
- **Cause:** the lint command receives the pinned clippy aspect and the `_lint` config more than once,
  so Bazel aborts with `aspect ... added more than once` before any lint action runs.
- **Required remediation (deterministic / collector side, not agent authority):** invoke the pinned
  lint exactly once — e.g. the native CI route `aspect lint --bazel-flag=--config=clippy`, or a single
  `--config=clippy` without an additional `--config=_lint` or explicit
  `--aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`. Then re-run the deterministic
  `check` stage on the unchanged plan.
- This is a prerequisite/backend gap, not a source/test defect, so the fix belongs to the collector
  command configuration; the assessment artifacts and check plan remain valid.

## Pending offline acceptance (unchanged)

Technical progress does **not** constitute native engineering acceptance. The `thiserror`
retain/replace/hand-implement decision, license/provenance acceptance, tool/component applicability
(`wp__tlm_plan` / `wp__tool_verification_report`), and the `Display`-string contract remain pending an
authorized human decision (`scope.md` §10, `dependency-assessment.md` §10). No native work product is
marked evaluated/qualified/released. The lint check's blocking status is recorded, not resolved.

## Next action

Collector/operator: correct the lint invocation so the pinned `clippy_strict` aspect is applied once,
then re-run the deterministic `check` stage against baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e` on the unchanged `check-plan.json`. Retain this file, the
check0 traceback (`correction-1.md`) and the check1 summary (`native-check-summary.json`) as history.
