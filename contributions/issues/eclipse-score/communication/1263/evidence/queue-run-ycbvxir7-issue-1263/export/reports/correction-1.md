# Correction 1 — issue #1263 (`futures` usage in the Rust COM API)

Baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Mode: **assessment**. Linux only;
QNX out of scope. Correction 1 of at most 3.

## 1. Inputs read for this correction

- Operator-supplied bounded result summary: `.rust-queue/reports/native-check-summary.json`
  (from `jobs/1263/execution/check-0/native-result.json`,
  sha256 `bc814ba7d7ed44e1ce4ba2519315cb4f0d24fb55de456c2427ef82fc647ccc4c`).
- Prior stage artifacts: `.rust-queue/reports/{scope.md,implementation.md,check-plan.json,review-packet.md}`.
- Bound evidence sources: `quality/static_analysis/static_analysis.bazelrc` (lines 14–31)
  and `.bazelrc` (lines 36–42, 186–188), plus `score_com_concept/BUILD` and
  `com-api-runtime-lola/BUILD` label existence.
- `.rust-queue/context/issue.json`, `comments.json` (`[]`), `task.json`.

## 2. Measured result of check-0 (native, collector-owned)

`attempt 0`, `kind = measured_native_command`, `passed = false`,
`engineering_acceptance = pending`, `measured_subject_hashes_sha256 =
3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`.

Fifteen checks appear in the bounded summary. **Fourteen passed** (exit 0):

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

## 3. Characterisation of the single failing check (decisive)

The lint check did not produce a single Clippy finding. Its bounded tail reports a
Bazel **analysis/invocation** failure before any lint action ran:

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
[98 / 290] checking cached actions
1 process: 303 action cache hit, 1 internal
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

Source-backed explanation: `quality/static_analysis/static_analysis.bazelrc:30` adds the
aspect exactly once via `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`
(`:29` `build:clippy --config=_lint`). Bazel's `--aspects` is additive, so the aspect is
registered twice only when that config/aspect is supplied twice on the command line. The
paired `[_lint] expanded more than once` warning is the same duplicate-expansion signature.
No `clippy_strict` diagnostics, no per-target lint actions, and no source/test output exist.
The pinned policy module and its config were not modified by this task
(`score_rust_policies` 0.0.5; `clippy_strict` aspect; no repository file edited).

## 4. Classification and decision

- **No measured source or test defect exists.** All six builds, all six tests (including
  the async/sync SCTs and the tokio integration test) and both docs checks pass at the
  bound subject hash. The failure is entirely at Bazel analysis time in the lint
  invocation.
- The failure is an **infrastructure / collector-invocation defect** (duplicate
  `--config=clippy` / duplicate `--aspects=…clippy_strict` expansion), not a Rust COM API
  code or regression-test defect. The harness left `infrastructure_error` at `null`, but
  the structural evidence above identifies the invocation layer, and command stages/raw
  evidence are outside agent authority.
- **Decision: do not change code and do not weaken checks.** Per the correction rules,
  when the evidence is infrastructure rather than a source/test defect, correction-1
  records the blocker instead of editing source, BUILD, lock, license, lint or CI policy.
  No repository file under `score/`, `quality/`, `MODULE.bazel`, `.bazelrc` or BUILD was
  touched. `clippy_strict` is not suppressed or relaxed.

## 5. Preserved evidence (not reset, not fabricated)

- Prior failed result retained: check-0 `passed = false`, exit 1, native-result sha256
  `bc814ba7…`; nothing was re-run, no counter was reset and no passing evidence was
  created by this correction.
- The bounded summary contains **15 of the 17** planned `check-plan.json` entries. The
  second planned lint group (`//score/mw/com/rust:score_com`, `…:score_com_mock`,
  `//score/mw/com/example/com-api-example:com-api-example-lib`) and the dependency
  resolution `query` are **absent from the supplied summary**; they remain
  **unrun/pending**, not passing and not failed. This is preserved as missing evidence.
- `engineering_acceptance` stays `pending`; the harness value was not altered.
- Dependency inventory (exact `futures` version/features/checksums/license/NOTICE,
  advisories) and safety-relevance/native work-product IDs remain **unknown** from the
  prior stages and are unaffected by this correction.

## 6. Blocker statement and next action

**Blocker (correction-1):** the single failing native check is the Clippy lint group, and
it fails because the `clippy_strict` aspect is applied more than once during a single Bazel
analysis (duplicate config/aspect expansion). This is an environment/invocation defect
outside agent authority; it is not a measured source or test defect, so no code edit is
warranted and no check may be weakened.

**Next action (collector/operator):** re-invoke the lint obligation on `linux_x64` with the
`clippy_strict` aspect supplied exactly once (a single `--config=clippy`, or a single
`--aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`, never both and never a
repeated `--config=clippy`). Then run the still-absent second lint group and the
dependency-resolution `query` so the full planned denominator is measured. If the duplicate
aspect persists under a de-duplicated invocation, the blocker escalates to the
`score_rust_policies` 0.0.5 / harness configuration owner as a tooling prerequisite.

No readiness, qualification or acceptance claim is made. This report only recommends; an
authorized human decides offline.
