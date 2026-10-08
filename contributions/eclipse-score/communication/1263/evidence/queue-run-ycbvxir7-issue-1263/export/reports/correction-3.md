# Correction 3 — issue #1263 (`futures` usage in the Rust COM API)

Baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Mode: **assessment**. Linux only;
QNX out of scope. **Correction 3 of at most 3 (final).**

This correction reads the latest operator-supplied bounded native result summary
(`attempt 2`, i.e. `check-2`) and re-classifies only a **measured source/test defect**.
The measured evidence contains **no source/test defect**; the single failing check is an
invocation-layer / infrastructure defect (duplicate Clippy aspect expansion). Per the
correction rules, **no code is changed and no check is weakened**; the blocker is recorded
here. No counter is reset and no passing evidence is fabricated.

## 1. Inputs read for this correction

- Latest operator-supplied bounded summary: `.rust-queue/reports/native-check-summary.json`
  (`attempt 2`; `native_result.path = jobs/1263/execution/check-2/native-result.json`,
  `native_result.sha256 = f14d10bdf310c550c95cab1d75656f35a52c2b8f21d199e386c7785124d02ca3`).
- Prior stage artifacts retained read-only, not modified: `.rust-queue/reports/correction-1.md`,
  `correction-2.md`, `implementation.md`, `scope.md`, `review-packet.md`, `check-plan.json`.
- Bound evidence sources re-checked for the failing invocation:
  `quality/static_analysis/static_analysis.bazelrc:27–30`, `.bazelrc:185–188`, and the three
  affected BUILD files
  (`score/mw/com/rust/score_com_concept/BUILD`,
  `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD`,
  `score/mw/com/impl/rust/com-api/com-api-runtime-mock/BUILD`).
- `.rust-queue/context/issue.json`, `.rust-queue/context/comments.json` (`[]`), `task.json`.

## 2. Measured result of check-2 (native, collector-owned)

`attempt = 2`, `kind = measured_native_command`, `passed = false`, `exit_code = 1`,
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

## 3. Reproducibility across all three attempts (prior failures retained)

| Field | check-0 (`attempt 0`) | check-1 (`attempt 1`) | check-2 (`attempt 2`) |
| --- | --- | --- | --- |
| `passed` | false | false | false |
| `measured_subject_hashes_sha256` | `3626732016…f03996` | `3626732016…f03996` | `3626732016…f03996` (identical) |
| checks in summary | 15 (14 exit 0, 1 lint exit 1) | 15 (14 exit 0, 1 lint exit 1) | 15 (14 exit 0, 1 lint exit 1) |
| failing check | lint group (duplicate aspect) | lint group (duplicate aspect) | lint group (duplicate aspect) |
| `native_result.sha256` | `bc814ba7d7ed44e1ce4ba2519315cb4f0d24fb55de456c2427ef82fc647ccc4c` | `348dad650f0a00fec087424071a9ee58da7526469c6ca27193fff26d0a6ca354` | `f14d10bdf310c550c95cab1d75656f35a52c2b8f21d199e386c7785124d02ca3` |

The `measured_subject_hashes_sha256` value is byte-identical across **all three** attempts, so
the measured subject did not change. Corrections 1 and 2 made no source/BUILD/lock/policy
edit; this correction likewise makes none. The failing signature is unchanged. This is a
**repeated unchanged failure** (three consecutive byte-identical lint failures); per the
workflow, a broadened or edited retry is not warranted and no further correction attempt
remains (3 of 3 exhausted).

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
[7 / 12] checking cached actions
1 process: 303 action cache hit, 1 internal
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

Source-backed explanation (re-verified, unchanged from corrections 1–2):

- `quality/static_analysis/static_analysis.bazelrc:29` sets `build:clippy --config=_lint`
  and `:30` sets `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`
  **exactly once**. The paired `[_lint] expanded more than once` warning is the same
  duplicate-expansion signature.
- `.bazelrc:188` imports that file once. `.bazelrc:186–188` import the three quality rc files
  once each.
- **No source-side aspect application exists:** the three affected BUILD files were read in
  full and none of them sets an `aspects` attribute or otherwise references `clippy_strict`
  (`score_com_concept/BUILD`, `com-api-runtime-lola/BUILD`, `com-api-runtime-mock/BUILD`).
- Bazel's `--aspects` is additive and `--config` inheritance is not de-duplicated, so the
  aspect is registered twice **only when the invocation supplies the clippy config/aspect
  more than once** (e.g. an explicit `--config=_lint` or explicit
  `--aspects=…clippy_strict` alongside `--config=clippy`, or a repeated `--config=clippy`).

No `clippy_strict` diagnostic, no per-target lint action and no source/test output exist. The
repository's own config defines the aspect exactly once; the duplicate is introduced at the
command/invocation layer, which is collector-owned and outside agent authority. The builds
and tests invoked through the same rc-file set succeed, confirming the failure is specific to
the lint invocation's flag set, not to the repository sources.

## 5. Classification and decision

- **No measured source or test defect exists.** All six builds, all six tests (including the
  async/sync SCTs and the tokio integration test) and both doc checks pass at the bound
  subject hash `3626732016…`.
- The failure is an **infrastructure / invocation defect** (duplicate `--config=clippy` /
  duplicate `--aspects=…clippy_strict` expansion). The harness left `infrastructure_error`
  at `null`, but the structural evidence above isolates the invocation layer (duplicate
  `[_lint]` expansion; aspect defined once in the repository's config; no BUILD-level
  `aspects` attribute); command stages and raw evidence are outside agent authority.
- **Decision: do not change code, do not weaken checks.** Because the evidence is
  infrastructure rather than a source/test defect, correction-3 records the blocker instead
  of editing source, BUILD, lock, license, lint or CI policy. **No file under `score/`,
  `quality/`, `MODULE.bazel`, `.bazelrc` or any BUILD was touched by this correction.**
  `clippy_strict` is not suppressed, relaxed, removed or de-registered.

## 6. Preserved evidence (not reset, not fabricated)

- **All three failed results are retained.** check-0: `passed=false`, exit 1, native-result
  sha256 `bc814ba7…`. check-1: `passed=false`, exit 1, native-result sha256 `348dad65…`.
  check-2: `passed=false`, exit 1, native-result sha256 `f14d10bd…`. Nothing was re-run by
  the agent, no counter was reset, and no passing evidence was created or substituted.
- The bounded summary still contains **15 of the 17** planned `check-plan.json` entries. The
  second planned lint group (`//score/mw/com/rust:score_com`, `…:score_com_mock`,
  `//score/mw/com/example/com-api-example:com-api-example-lib`) and the dependency
  resolution `query` remain **absent** from the supplied summary; they stay
  **unrun/pending**, not passing and not failed. This is preserved as missing evidence.
- `engineering_acceptance` remains `pending`; the harness value was not altered.
- The dependency inventory (exact `futures` version/features/checksums/license/NOTICE,
  advisories) and native work-product IDs remain **unknown** from the prior stages and are
  unaffected by this correction.
- `score_com_concept-macros-tests` remains `manual` / excluded, and QNX remains out of scope.

## 7. Blocker statement and next action (final correction)

**Blocker (correction-3, final):** the single failing native check is the Clippy lint group,
and it fails before any lint action because the `clippy_strict` aspect is applied more than
once in one Bazel invocation (duplicate config/aspect expansion). This is an
environment/invocation defect outside agent authority; it is not a measured source or test
defect, so no code edit is warranted and no check may be weakened. The identical failure is
now reproduced byte-for-byte across check-0, check-1 and check-2 at an unchanged measured
subject hash.

**Next action (collector/operator):** re-invoke the lint obligation on `linux_x64` with the
`clippy_strict` aspect supplied exactly once — a single `--config=clippy`, or a single
`--aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`, never both and never a
repeated `--config=clippy`/`--config=_lint` (the `[_lint]` duplicate-expansion warning must
disappear). Also supply the still-absent second lint group and the dependency-resolution
`query` so the full planned denominator is measured. If the duplicate aspect persists under
a de-duplicated invocation, escalate to the `score_rust_policies` 0.0.5 / harness
configuration owner as a tooling prerequisite. Since correction 3 of 3 is now exhausted, no
further agent-side correction follows; the blocker is handed off unmodified.

No readiness, qualification or acceptance claim is made. This report only recommends; an
authorized human decides offline.
