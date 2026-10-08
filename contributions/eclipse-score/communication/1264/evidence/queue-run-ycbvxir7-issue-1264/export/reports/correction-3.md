# Correction 3 — issue #1264 (`thiserror` usage in the Rust COM API)

Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Mode: assessment (no product source patch). Platform: Linux `linux_x64`. No QNX. DeepSeek Flash only.
Correction 3 of at most 3.

Evidence of record: the latest bounded native result summary supplied by the operator —
`.rust-queue/reports/native-check-summary.json` (`attempt: 2`, `passed: false`,
`infrastructure_error: null`, `measured_subject_hashes_sha256 =
3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`; raw result
`jobs/1264/execution/check-2/native-result.json`, sha256
`d08e07d5f9c76b431848b59975448cd7a62d8732bf46f67a9739579679e28c1b`).

## Prior failed results retained (not reset, not overwritten)

- **check0** — collector `AssertionError` at `driver_linux.py` line 87 on the `check-plan.json`
  schema (an external `@score_communication_crate_index//:thiserror` label in `targets[]`). Retained
  in `correction-1.md`. Correction 1 rewrote every `targets[]` entry to the `//package:target` form.
- **check1** — native run of the corrected plan: overall `passed: false`; 7 of 8 checks exited 0, the
  `lint` check exited 1 (`aspect ... added more than once`). Retained in `correction-2.md` and in the
  carried prior summary; no counter is reset and no passing evidence is fabricated.
- **check2** — the latest native run (attempt 2), recorded below. It reproduces the attempt-1
  outcome exactly, so it does not supersede or invalidate check1; both failures are kept as history.

## Attempt-2 measured outcomes (from the operator's summary)

| # | kind  | targets (abbreviated) | exit | outcome |
|---|-------|-----------------------|------|---------|
| 1 | query | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | resolved |
| 2 | query | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | resolved |
| 3 | build | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/rust:score_com` | 0 | build succeeded (fully cached) |
| 4 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola`, `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`, `//score/mw/com/example/com-api-example:com-api-example-lib` | 0 | build succeeded (fully cached) |
| 5 | test  | `...:score_com_concept-test`, `...:score_com_concept-macros-unit-tests`, `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | 0 | 3 tests pass |
| 6 | test  | `...consumer_sync_apis/integration_test:test_com_api_sync`, `...consumer_async_apis/integration_test:test_com_api_async`, `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | 0 | 3 tests pass |
| 7 | docs  | `...:score_com_concept-macros-tests`, `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | 0 | build succeeded (fully cached) |
| 8 | lint  | `//score/mw/com/rust/score_com_concept:score_com_concept` | **1** | **Bazel analysis error (aspect added more than once)** |

Seven of eight checks exited 0. The only non-zero exit is the `lint` check, and it failed with the
identical message seen in attempt 1. Because the subject hash is unchanged
(`3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996` in both attempts) and the
build/test/docs actions were served from cache, attempt 2 is a **repeated unchanged failure**; per the
SKILL "stop on a repeated unchanged failure" rule the plan is not broadened or repeatedly re-run by
this stage.

Prior compiler/runtime evidence for the pinned thiserror edge (attempt 1: `[285 / 290] Compiling Rust
proc-macro thiserror_impl v2.0.21`, `[286 / 290] ... thiserror v2.0.21`) is carried, not re-measured in
attempt 2 (its builds were entirely cache hits, consistent with the unchanged subject between runs).

## Defect determination: no measured source/test defect in attempt 2

The attempt-2 `lint` invocation again failed during Bazel's **analysis phase**, before any clippy
action ran:

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

Source-anchored facts are unchanged from `correction-2.md`:

- The failure is a Bazel option/config error, not a clippy finding: the pinned aspect
  `@score_rust_policies//clippy:linters.bzl%clippy_strict` and the shared `_lint` config were each
  supplied to the lint command **more than once** (`aspect ... added more than once`,
  `configs ... expanded more than once: [_lint]`).
- The repository defines that aspect exactly once, in
  `quality/static_analysis/static_analysis.bazelrc` lines 29–30
  (`build:clippy --config=_lint` /
  `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`). The
  `score_com_concept` `rust_library` declares no lint/aspect.
- The error occurs before analysis completes and the analyzed target is reported up-to-date, so the
  check produced **no clippy diagnostics about the source**. Every source-facing check (1–7) exited 0.

Conclusion: attempt 2 measures **no source/test defect**. Its single failing check is blocked by a
**duplicated lint invocation / missing correct lint-command prerequisite** (collector/backend side),
the same defect already recorded in `correction-2.md`. This is a design/backend prerequisite gap, not
a source/test defect to correct.

## Action taken: none — no code, check, or status change

Per the correction-3 rule, when the evidence shows a backend/infrastructure prerequisite is missing,
do **not** change code or weaken checks; record the blocker. Accordingly:

- No product source, `BUILD`, `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelrc`, CI workflow or lint
  policy was modified.
- `.rust-queue/reports/check-plan.json` is **unchanged**. Its `lint` entry remains source-backed by
  `.github/workflows/_linter.yml` (matrix id `clippy`; `aspect lint --bazel-flag=--config=clippy`)
  selecting the pinned `clippy_strict` aspect. Removing the check, changing its `kind`, or repointing
  its target would drop the pinned-lint obligation and is a prohibited weakening; the check stays in the
  plan as expected-but-blocked.
- No passing lint evidence is claimed. `native-check-summary.json` retains the measured attempt-2
  failure (`passed: false`), and the overall stage remains `passed: false`.
- Prior failed attempts (check0, check1) and their reports are retained as history.

Non-blocking observation (left as-is, carried from correction 2): the two `query` checks share the
in-repo target `//score/mw/com/rust/score_com_concept:score_com_concept`, so they are redundant. Both
exit 0; this is a plan-quality observation, not a measured source/test defect, so no change is made.

## Blocker (outside agent authority)

- **Blocked check:** `lint` on `//score/mw/com/rust/score_com_concept:score_com_concept`.
- **Cause:** the lint command receives the pinned clippy aspect and the `_lint` config more than once
  (`aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once`;
  `configs ... expanded more than once: [_lint]`), so Bazel aborts during analysis before any lint
  action runs. Reproduced identically in attempts 1 and 2 on the same subject hash.
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
`381d43dec900ab6a9076f3f30e7bfbdee019e26e` on the unchanged `check-plan.json`. Retain this file plus
the check0 traceback (`correction-1.md`), the check1 result (`correction-2.md`) and the attempt
summaries in `native-check-summary.json` as history. If the lint blocker cannot be removed by the
collector, the pinned-lint obligation remains an explicitly-unresolved gap for the offline human
review and must not be replaced by a weaker check.
