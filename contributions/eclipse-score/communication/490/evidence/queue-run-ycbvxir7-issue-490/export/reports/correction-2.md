# Correction 2 — communication#490 mock runtime

Status: **no measured source/test defect; the single failing check is a command-level
(configuration/analysis) defect outside this workspace's authority. No code, BUILD rule,
check plan, pin, license or lint-policy file was changed by this correction. No failed
evidence was deleted or re-labelled and no check was weakened or dropped.**

- Issue: `eclipse-score/communication#490`, state `open`, label `rust-api`, 0 comments
  (`.rust-queue/context/issue.json`, `.rust-queue/context/comments.json` = `[]`)
- Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- Platform scope: Linux only (`linux_x64`); no QNX task/execution
- Latest measured attempt: **attempt 1** (`check1`), `passed: false`, `exit_code: 1`
- Measured subject hash (operator-supplied, unchanged from attempt 0):
  `fe6316d4663c54c272ae145176de4255221852d24527c3a1debae2494b538824`
- Raw native result (outside agent authority; retained by operator):
  `…/jobs/490/execution/check-1/native-result.json`,
  sha256 `b4851a3817e81168af62182e79c584a0beb37d5f5f4b942688e23716b866dd31`
- Bounded summary read: `.rust-queue/reports/native-check-summary.json` (attempt 1;
  prior attempt 0 summary retained in history, not overwritten)
- Harness `infrastructure_error` field: `null` (the harness did not classify this run).
  The classification below is derived from the bounded raw log text, **not** from a harness
  `infrastructure_unavailable` label; no relabeling is claimed.
- Engineering acceptance: **pending** (unchanged)

## 1. What the latest supplied native summary measured (attempt 1)

| # | kind | target(s) | exit | outcome |
|---|------|-----------|------|---------|
| 1 | query | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock`, `//score/mw/com/rust:score_com_mock` | 0 | both rules resolved |
| 2 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` | 0 | build succeeded |
| 3 | build | `//score/mw/com/rust:score_com_mock` | 0 | build succeeded |
| 4 | build | `//score/mw/com/rust:score_com` | 0 | build succeeded |
| 5 | test | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock-tests` | 0 | 1 test passes |
| 6 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | 0 | 1 test passes |
| 7 | test | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | 0 | 1 test passes |
| 8 | docs | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock-doc-tests` | 0 | rustdoc target built |
| 9 | docs | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | 0 | rustdoc target built |
| 10 | lint | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` | **1** | **failed: duplicate clippy aspect (analysis-time)** |

Nine of ten checks passed with exit `0`. This is byte-for-byte the same outcome set as
attempt 0 (only the two raw-result hashes differ); the measured subject hash is **identical**
across attempt 0 and attempt 1 (`fe6316…`). This is a **repeated unchanged failure**
(SKILL: stop on a repeated unchanged failure rather than broadening the run).

## 2. Root cause of the only failing check (evidence-bound)

Exact lines from the bounded tail of the attempt-1 `lint` check:

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

Relevant policy surface (read directly, unchanged by this correction):

- `quality/static_analysis/static_analysis.bazelrc:29-30` registers the aspect exactly once:
  ```
  build:clippy --config=_lint
  build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict
  ```
- `quality/static_analysis/static_analysis.bazelrc:15-18` (`_lint`) only sets extra toolchains,
  output groups, `fail_on_violation` and `keep_going`; it does **not** register any aspect.
- `.bazelrc:188` imports `quality/static_analysis/static_analysis.bazelrc`.

Mechanism (consistent with the bounded log): the rc file is loaded more than once for the
`lint` invocation (`Duplicate rc file … is read multiple times`). Because `build:clippy`
carries a **non-idempotent** `--aspects=…%clippy_strict` option, the duplicated load expands
`clippy`/`_lint` more than once (`configs were expanded more than once: [_lint]`) and adds the
same aspect twice. Bazel rejects duplicate aspect registration at analysis time and refuses to
analyze the lint target (`not all targets were analyzed`). For the non-`clippy` configs used by
checks 1–9 the same duplicate rc load is idempotent, which is why only the `lint` check fails.

## 3. Why no measured source/test defect exists (and why no correction is authorized)

- The error is raised at Bazel **analysis / flag-expansion** time, before any lint action runs;
  the library target is itself reported `up-to-date`.
- It names a command-line option (`--aspects=…%clippy_strict`) that is duplicated by rc-file
  double-loading. It is independent of `runtime.rs` or `BUILD` content: any target built under a
  doubled `--config=clippy` fails identically, and no edit to a source/BUILD file can change
  option-flag duplication.
- All eight source-derived checks (query/build/test/docs) passed with exit `0`, including the
  mock round-trip test `com-api-runtime-mock-tests` and the mock rustdoc target
  `com-api-runtime-mock-doc-tests` added by the implementation stage. There is no failing source
  or test to correct.
- The `lint` check never produced a clippy finding, so no lint violation is measured. Recording
  a specific clippy defect now would be fabrication.
- Editing the repository's `quality/static_analysis/static_analysis.bazelrc` or `.bazelrc`
  import (e.g. removing the `--config=_lint`/`--aspects` lines or the line-188 import) would
  alter the **pinned repository static-analysis policy** and/or drop the `clippy` obligation,
  which the workflow forbids (preserve native lint profiles; do not suppress lints or weaken
  checks to make a check pass). The gap is therefore disciplined: it is recorded, not patched.

Consequently there is **no authorized source/test correction** for this measurement.

## 4. Blocker (owned by the command/collector stage, not this workspace)

**Blocker:** the collector's `lint` invocation loads
`quality/static_analysis/static_analysis.bazelrc` more than once (it is already imported by
`.bazelrc:188`, and the bounded log proves a second load). The resulting duplicate expansion of
`build:clippy` registers `@score_rust_policies//clippy:linters.bzl%clippy_strict` twice, so Bazel
aborts analysis and the `clippy` obligation for
`//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` is **unexecuted**.

Required action (command stage — outside agent authority): ensure the static-analysis bazelrc and
the `clippy` config are applied exactly once for the lint check (single rc load, single
`--config=clippy`), then re-run the `lint` check on the same target. If clippy is then clean, the
check set is green and the packet can proceed to offline engineering review; if it reports
findings, those become a **measured** source defect for a later correction.

## 5. Preserved evidence, counters and pending decisions

- `.rust-queue/reports/native-check-summary.json` retained (attempt 1) exactly as supplied;
  attempt 0 (`b6fa500e…`) remains as prior history. Counters were **not** reset.
- `.rust-queue/reports/check-plan.json` retained **unchanged**; its `lint` entry remains, so the
  `clippy` obligation is preserved rather than dropped or weakened.
- `.rust-queue/reports/correction-1.md` retained unchanged.
- No source, BUILD, pin, license, feature or lint-policy change was made in this correction; the
  applied subject still carries its original Apache-2.0 headers (e.g.
  `…/com-api-runtime-mock/runtime.rs:1-12`). The measured subject hash is unchanged (`fe6316…`).
- Prior unresolved design questions (registry model, `cancellable_receive` semantics,
  `max_num_samples` enforcement, requirements/architecture impact) remain open and are not
  altered here.
- Engineering acceptance remains **pending**; this report does not accept, qualify or release
  anything.

## 6. Next action

1. Command/collector stage de-duplicates the rc load so the `lint` check runs `--config=clippy`
   once (single `quality/static_analysis/static_analysis.bazelrc` load).
2. Re-run the `lint` check on
   `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock`.
3. If clean, the check set is green; if it reports findings, open a later measured source
   correction. Do not change workspace source or lint policy to work around the duplicate-aspect
   analysis error.
