# Correction 2 — issue #1263 (`futures` usage in the Rust COM API)

Baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Mode: **assessment**. Linux only;
QNX out of scope. Correction 2 of at most 3.

This correction reads the latest operator-supplied bounded native result summary
(`attempt 1`, i.e. `check-1`) and re-classifies only a **measured source/test defect**.
The measured evidence contains no source/test defect; the single failing check is an
invocation-layer (infrastructure) defect. Per the correction rules, **no code is changed
and no check is weakened**; the blocker is recorded here.

## 1. Inputs read for this correction

- Latest operator-supplied bounded summary: `.rust-queue/reports/native-check-summary.json`
  (`attempt 1`; `native_result.path = jobs/1263/execution/check-1/native-result.json`,
  `native_result.sha256 = 348dad650f0a00fec087424071a9ee58da7526469c6ca27193fff26d0a6ca354`).
- Prior stage artifacts retained read-only: `.rust-queue/reports/correction-1.md`,
  `implementation.md`, `scope.md`, `review-packet.md`, `check-plan.json`.
- Bound evidence sources for the failing invocation: `quality/static_analysis/static_analysis.bazelrc`
  (lines 14–30) and `.bazelrc` (lines 36–42, 186–188).
- `.rust-queue/context/issue.json`, `.rust-queue/context/comments.json` (`[]`), `task.json`.

## 2. Measured result of check-1 (native, collector-owned)

`attempt = 1`, `kind = measured_native_command`, `passed = false`, `exit_code = 1`,
`infrastructure_error = null`, `engineering_acceptance = pending`,
`measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`.

Fifteen checks appear in the bounded summary; **fourteen passed (exit 0)**:

| # | kind | targets | exit |
| --- | --- | --- | --- |
| 1 | build | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 |
| 2 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | 0 |
| 3 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` | 0 |
| 4 | build | `//score/mw/com/rust:score_com`, `//score/mw/com/rust:score_com_mock` | 0 |
| 5 | build | `//score/mw/com/example/com-api-example:com-api-example-lib`, `…:com-api-example` | 0 |
| 6 | build | `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`, `…/consumer_async_apis:bigdata-consumer-async`, `…/consumer_sync_apis:bigdata-consumer`, `…/producer_app:bigdata-producer` | 0 |
| 7 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | 0 (PASSED) |
| 8 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests` | 0 (PASSED) |
| 9 | test | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | 0 (PASSED) |
| 10 | test | `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | 0 (PASSED) |
| 11 | test | `//score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test:test_com_api_async` | 0 (PASSED) |
| 12 | test | `//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync` | 0 (PASSED) |
| 13 | docs | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | 0 |
| 14 | docs | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | 0 |

**One check failed (exit 1):** the `lint` check over
`//score/mw/com/rust/score_com_concept:score_com_concept`,
`//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola`,
`//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock`.

## 3. Reproducibility check against check-0 (evidence retained)

| Field | check-0 (`attempt 0`) | check-1 (`attempt 1`) |
| --- | --- | --- |
| `passed` | false | false |
| `measured_subject_hashes_sha256` | `3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996` | `3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996` (identical) |
| checks in summary | 15 (14 exit 0, 1 lint exit 1) | 15 (14 exit 0, 1 lint exit 1) |
| failing check | lint group (duplicate aspect) | lint group (duplicate aspect) |
| `native_result.sha256` | `bc814ba7d7ed44e1ce4ba2519315cb4f0d24fb55de456c2427ef82fc647ccc4c` | `348dad650f0a00fec087424071a9ee58da7526469c6ca27193fff26d0a6ca354` |

The `measured_subject_hashes_sha256` value is byte-identical across both attempts, so the
measured subject did not change between check-0 and check-1 (the correction-1 stage made no
source/BUILD/lock/policy edit). The failing signature is likewise unchanged. This is a
**repeated unchanged failure**, and per the workflow a broadened/edited retry is not
warranted; the run should stop on it.

## 4. Characterisation of the single failing check (decisive)

The lint check produced **no Clippy finding**. Its bounded tail reports a Bazel
analysis/invocation failure before any lint action ran:

```
WARNING: The following configs were expanded more than once: [_lint]. For repeatable
         flags, repeats are counted twice and may lead to unexpected behavior.
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
...
WARNING: errors encountered while analyzing target '//score/mw/com/rust/score_com_concept:score_com_concept', it will not be built.
WARNING: errors encountered while analyzing target '//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola', it will not be built.
WARNING: errors encountered while analyzing target '//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock', it will not be built.
INFO:  Found 3 targets...
[1 / 1] no actions running
[126 / 290] checking cached actions
1 process: 303 action cache hit, 1 internal
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

Source-backed explanation (unchanged from correction-1): `quality/static_analysis/static_analysis.bazelrc:29`
sets `build:clippy --config=_lint` and `:30` sets
`build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`
exactly once. `.bazelrc:188` imports that file once. Bazel `--aspects` is additive and
`--config` inheritance is not de-duplicated, so the aspect is registered twice **only when
the invocation supplies the clippy config/aspect more than once** (e.g. an explicit
`--config=_lint` or explicit `--aspects=…clippy_strict` alongside `--config=clippy`). The
paired `[_lint] expanded more than once` warning is the same duplicate-expansion signature.
No `clippy_strict` diagnostic, no per-target lint action and no source/test output exist.
The repository's own config defines the aspect once; the duplicate is introduced at the
command/invocation layer, which is collector-owned and outside agent authority.

## 5. Classification and decision

- **No measured source or test defect exists.** All six builds, all six tests (including the
  async/sync SCTs and the tokio integration test) and both doc checks pass at the bound
  subject hash `3626732016…`.
- The failure is an **infrastructure/invocation defect** (duplicate `--config=clippy` /
  duplicate `--aspects=…clippy_strict` expansion), not a Rust COM API source or
  regression-test defect. `infrastructure_error` was left `null` by the harness, but the
  structural evidence above isolates the invocation layer; command stages and raw evidence
  are outside agent authority.
- **Decision: do not change code, do not weaken checks.** Because the evidence is
  infrastructure rather than a source/test defect, correction-2 records the blocker instead
  of editing source, BUILD, lock, license, lint or CI policy. No file under `score/`,
  `quality/`, `MODULE.bazel`, `.bazelrc` or any BUILD was touched by this correction.
  `clippy_strict` is not suppressed, relaxed or removed.

## 6. Preserved evidence (not reset, not fabricated)

- **Both prior failed results are retained.** check-0: `passed=false`, exit 1, native-result
  sha256 `bc814ba7…`. check-1: `passed=false`, exit 1, native-result sha256 `348dad65…`.
  Nothing was re-run by the agent, no counter was reset, and no passing evidence was
  created or substituted.
- The bounded summary still contains **15 of the 17** planned `check-plan.json` entries. The
  second planned lint group (`//score/mw/com/rust:score_com`, `…:score_com_mock`,
  `//score/mw/com/example/com-api-example:com-api-example-lib`) and the dependency
  resolution `query` are **absent** from the supplied summary; they remain **unrun/pending**,
  not passing and not failed. This is preserved as missing evidence.
- `engineering_acceptance` remains `pending`; the harness value was not altered.
- The dependency inventory (exact `futures` version/features/checksums/license/NOTICE,
  advisories) and native work-product IDs remain **unknown** from the prior stages and are
  unaffected by this correction.
- `score_com_concept-macros-tests` remains `manual` / excluded, and QNX remains out of scope.

## 7. Blocker statement and next action

**Blocker (correction-2):** the single failing native check is the Clippy lint group, and it
fails before analysis because the `clippy_strict` aspect is applied more than once in one
Bazel invocation (duplicate config/aspect expansion). This is an environment/invocation
defect outside agent authority; it is not a measured source or test defect, so no code edit
is warranted and no check may be weakened. The same failure was already recorded in
correction-1 and is reproduced byte-for-byte in check-1.

**Next action (collector/operator):** re-invoke the lint obligation on `linux_x64` with the
`clippy_strict` aspect supplied exactly once (a single `--config=clippy`, or a single
`--aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`, never both and never a
repeated `--config=clippy`/`--config=_lint`). Supply the still-absent second lint group and
the dependency-resolution `query` so the full planned denominator is measured. If the
duplicate aspect persists under a de-duplicated invocation, escalate the blocker to the
`score_rust_policies` 0.0.5 / harness configuration owner as a tooling prerequisite.

No readiness, qualification or acceptance claim is made. This report only recommends; an
authorized human decides offline.
