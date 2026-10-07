# Correction 1 — communication#490 mock runtime

Status: **no source/test defect measured; blocking infrastructure/configuration defect recorded.**
No source file, test, BUILD rule, check plan, pin or lint policy was changed by this correction.
No failed evidence was deleted or re-labelled and no check was weakened or dropped.

- Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- Issue: `eclipse-score/communication#490`, state `open`, label `rust-api`, 0 comments
- Platform scope: Linux only (`linux_x64`); no QNX task/execution
- Measured attempt: `attempt 0`, `passed: false`, `exit_code: 1`
- Measured subject hash (operator-supplied):
  `fe6316d4663c54c272ae145176de4255221852d24527c3a1debae2494b538824`
- Raw native result (outside agent authority; retained by operator):
  `…/jobs/490/execution/check-0/native-result.json`,
  sha256 `b6fa500e5f64802ce96c384ae252a75fc58ae7ca6d974660aaf228a15d8f45d5`
- Bounded summary read: `.rust-queue/reports/native-check-summary.json` (unchanged)
- `infrastructure_error` field: `null` (harness did not classify; classification below is from the
  raw bounded log text, not from a harness label)
- Engineering acceptance: **pending** (unchanged)

## 1. What the supplied native summary measured

| # | kind | target(s) | exit | outcome |
|---|------|-----------|------|---------|
| 1 | query | `…/com-api-runtime-mock`, `//score/mw/com/rust:score_com_mock` | 0 | resolved both rules |
| 2 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` | 0 | build succeeded |
| 3 | build | `//score/mw/com/rust:score_com_mock` | 0 | build succeeded |
| 4 | build | `//score/mw/com/rust:score_com` | 0 | build succeeded |
| 5 | test | `…/com-api-runtime-mock:com-api-runtime-mock-tests` | 0 | 1 test passes |
| 6 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | 0 | 1 test passes |
| 7 | test | `…/com-api-runtime-lola:com-api-runtime-lola-tests` | 0 | 1 test passes |
| 8 | docs | `…/com-api-runtime-mock:com-api-runtime-mock-doc-tests` | 0 | rustdoc target built |
| 9 | docs | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | 0 | rustdoc target built |
| 10 | lint | `…/com-api-runtime-mock:com-api-runtime-mock` | **1** | **failed: duplicate clippy aspect** |

Nine of ten checks passed. The only failure is the `clippy` lint check, which failed during
analysis/flag expansion before any lint action could run.

## 2. Root cause of the single failing check (evidence-bound)

Exact lines from the bounded tail of the failing `lint` check:

```
WARNING: Duplicate rc file:
  …/workspaces/490/quality/static_analysis/static_analysis.bazelrc is read multiple times,
  it is a standard rc file location but must have been unnecessarily imported earlier.
WARNING: The following configs were expanded more than once: [_lint]. For repeatable flags,
  repeats are counted twice and may lead to unexpected behavior.
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
WARNING: errors encountered while analyzing target '…:com-api-runtime-mock', it will not be built.
INFO: Found 1 target...
Target //…:com-api-runtime-mock up-to-date:
  bazel-bin/…/libcom_api_runtime_mock-751917231.rlib
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

The lint policy is declared at `quality/static_analysis/static_analysis.bazelrc:27-30`:

```
# Clippy configuration
build:clippy --config=_lint
build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict
```

`_lint` itself only sets toolchains/output-groups/tolerance flags
(`static_analysis.bazelrc:15-18`); it does **not** register `clippy_strict`.
The only place the aspect is registered is the `build:clippy --aspects=…` line.

Mechanism: the bounded log shows `static_analysis.bazelrc` is read/imported more than once during
the lint invocation (`Duplicate rc file …`), so the single `--config=clippy` expansion applies the
`--aspects=…%clippy_strict` option line more than once. Bazel rejects registering the same aspect
twice (`aspect … added more than once`) and refuses to analyze the lint target
(`not all targets were analyzed`). `--config=clippy` is the only config in the repository that
carries a non-idempotent `--aspects` option; the duplicate read therefore only becomes fatal for the
lint check. This is consistent with `cli`/CI usage `bazel test --config=clippy …`
(`static_analysis.bazelrc:28`) which registers the aspect once.

## 3. Why this is not a measured source/test defect

- The failure occurs at Bazel **analysis / flag-expansion** time, before any lint action executes;
  the library target itself is reported `up-to-date`.
- The error names a command-line option (`--aspects=…%clippy_strict`) that is duplicated by rc-file
  double-loading. It is independent of `runtime.rs` or `BUILD` content: any target built with a
  doubled `--config=clippy` fails identically, and no source edit can change option-flag
  duplication.
- All eight source-derived checks (query/build/test/docs, including the mock round-trip test and the
  mock rustdoc target added by the patch) passed with exit `0`. There is no failing source or test
  to correct.
- The lint check never produced a clippy finding, so no lint violation is measured either. Recording
  a specific clippy defect now would be fabrication.

Consequently no authorized source/test correction exists for this measurement. Editing source cannot
be justified by the log, and removing/altering the lint check or the `clippy`/`_lint` config would
weaken the pinned static-analysis policy, which is forbidden (SKILL: preserve native lint profiles;
do not suppress lints to make a check pass).

## 4. Blocker (owned outside agent authority)

**Blocker:** the collector's lint invocation loads
`quality/static_analysis/static_analysis.bazelrc` more than once (e.g. an explicit `--bazelrc=`
addition to the `import %workspace%/quality/static_analysis/static_analysis.bazelrc` at
`.bazelrc:188`), so `--config=clippy` registers `clippy_strict` twice and Bazel aborts analysis.

Required action (collector/command stage, not this workspace): ensure the static-analysis bazelrc is
loaded exactly once for the lint check (single `--config=clippy`, single rc import), then re-run the
lint check. Until then the `clippy` obligation for `…:com-api-runtime-mock` is **unexecuted**.

## 5. Preserved evidence / pending decisions

- `.rust-queue/reports/native-check-summary.json` retained verbatim: `attempt 0`, `passed: false`,
  `exit_code: 1`, subject hash `fe6316…`, raw result hash `b6fa500e…`. Counters not reset.
- `.rust-queue/reports/check-plan.json` retained unchanged; its `lint` entry stays, so the obligation
  is preserved rather than dropped.
- No source, BUILD, pin, license, feature or lint-policy change was made in this correction; the
  applied subject still carries its original Apache-2.0 headers (e.g.
  `…/com-api-runtime-mock/runtime.rs:1-12`).
- Prior unresolved design questions (registry model, `cancellable_receive` semantics,
  `max_num_samples` enforcement, requirements/architecture impact) remain open and are not altered
  here.
- Engineering acceptance remains **pending**; this report does not accept, qualify or release
  anything.

## 6. Next action

1. Collector/command stage de-duplicates the rc load so the lint check runs `--config=clippy` once.
2. Re-run the `lint` check on `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock`.
3. If clippy then reports findings, those become a **measured** source defect for a later correction;
   if clean, the check set is green and the packet can proceed to offline engineering review.
