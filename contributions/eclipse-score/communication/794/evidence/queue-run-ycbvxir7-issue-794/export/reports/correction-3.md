# correction-3.md — Issue #794 (correction 3 of at most 3, FINAL)

"Improvement: Remove bazel `tags = [\"manual\"]` from rust test targets"

- **Repository / issue**: eclipse-score/communication #794
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- **Runtime / model**: Linux only; DeepSeek Flash only. No QNX task or execution.
- **Stage**: deterministic `check 794 2` failed (`passed: false`, `exit_code: 1`);
  this is the third and final correction attempt (3 of at most 3).
- **Supplied evidence read**: `.rust-queue/reports/native-check-summary.json`
  (copy of the `check-2` bounded native summary, `attempt: 2`) and the bounded
  native summary echoed in the stage prompt. The prior failed `check-0` and
  `check-1` results are retained and referenced, not overwritten.
- **Authority**: disposable workspace only. Shell, delegation, publishing and
  acceptance tools are blocked; the agent executed **no** native command. Command
  stages and raw evidence remain outside agent authority. No QNX work.
- **Outcome of this correction**: **no code change is applied.** The measured
  failure is a native-invocation/configuration defect (duplicate `clippy_strict`
  aspect registration) and **not** a measured source/test defect. The blocker is
  recorded here per the stage rule. The `#794`-scope source/test obligations
  already pass and the issue premise is already implemented at baseline.

## 1. Latest measured outcome (check-2, per supplied bounded native summary)

`attempt = 2`;
`native_result.path = .../jobs/794/execution/check-2/native-result.json`;
`native_result.sha256 = 2036a1437e615d7e955da364f808127ad99e58f64a71e26819e472d7919bf49b`;
`measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`;
`infrastructure_error = null`; `engineering_acceptance = pending`.

| # | kind | target(s) | exit | outcome |
| --- | --- | --- | --- | --- |
| 1 | query | `//score/mw/com/rust/score_com_concept:all` | 0 | pass (`rust_test score_com_concept-test`, `rust_doc_test score_com_concept-macros-tests`, forwarding `...-macros-unit-tests`) |
| 2 | build | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | pass (rlib produced) |
| 3 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | 0 | PASSED |
| 4 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests` | 0 | PASSED |
| 5 | query | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | 0 | pass (still `rust_doc_test`, retained `manual`) |
| 6 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | 0 | pass (rlib produced) |
| 7 | test | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | 0 | PASSED |
| 8 | docs | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | 0 | pass (rustdoc runner generated) |
| 9 | docs | `//score/mw/com/rust/score_com_macros:score-com-macros-tests` | 0 | pass (rustdoc runner generated) |
| 10 | build | `//score/mw/com/example/com-api-example:com-api-example-lib` | 0 | pass (rlib produced) |
| 11 | test | `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | 0 | PASSED in 6.1s (default config) |
| 12 | lint | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | 1 | **FAIL — analysis/configuration error, no source diagnostic emitted** |

All three checkpoints are **identical**:

| attempt | kind | `measured_subject_hashes_sha256` | `native_result.sha256` | non-lint checks | lint check |
| --- | --- | --- | --- | --- | --- |
| 0 (check-0) | measured_native_command | `3626732016…b56f03996` | `540888a838acecc054b0024a6c6f4826a64712465c48158b1cb27e445b25f87c` | all pass | fail (analysis) |
| 1 (check-1) | measured_native_command | `3626732016…b56f03996` | `fc14ae5909fc20fec78b1f5161d12a254a072810f021bee4c7d50fabfd3ff63d` | all pass | fail (analysis) |
| 2 (check-2) | measured_native_command | `3626732016…b56f03996` | `2036a1437e615d7e955da364f808127ad99e58f64a71e26819e472d7919bf49b` | all pass | fail (analysis) |

The subject hash is **byte-identical across all three measurements** (`3626…3996`),
confirming that no source change occurred between attempts (candidate source ==
baseline). This is a **repeated, unchanged failure**, which the workflow requires
us to stop on rather than broaden or iterate blindly.

## 2. Root cause of the single failure (measured, source-backed)

Bounded tail of check 12 (`check-2`):

```
WARNING: The following configs were expanded more than once: [_lint]. For repeatable flags, repeats are counted twice and may lead to unexpected behavior.
...
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
...
WARNING: errors encountered while analyzing target '//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola', it will not be built.
WARNING: errors encountered while analyzing target '//score/mw/com/rust/score_com_concept:score_com_concept', it will not be built.
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

The failure is emitted by Bazel **analysis/configuration**, before any Rust
compilation or clippy diagnostic; no code/SARIF finding was produced.

The repository registers the clippy aspect **exactly once** and structurally
cannot have produced the duplicate:

- `quality/static_analysis/static_analysis.bazelrc:27-30` — `build:clippy`
  expands `--config=_lint` and adds
  `--aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict` **once**.
- `quality/static_analysis/static_analysis.bazelrc:14-18` — `build:_lint` adds
  only extra toolchains / output groups / `fail_on_violation` / `keep_going`; it
  does **not** add the clippy aspect. A single `--config=clippy` therefore
  registers the aspect once.
- `.bazelrc:186-188` — imports `quality/static_analysis/static_analysis.bazelrc`
  exactly once, and no other config in `.bazelrc` (or the optional
  `.bazelrc.ai_checker` / `user.bazelrc`) adds the clippy aspect. No
  `user.bazelrc` and no `.aspect/` directory exist in the workspace.
- `.github/workflows/_linter.yml:83-86` documents the exact prohibition: the
  aspect is deliberately **NOT** also passed via `--aspect=`, "*since Bazel
  rejects the same aspect being registered twice.*" The CI clippy job registers
  it only through `--bazel-flag=--config=clippy` (`:115-125`).

Because the checked-in `clippy` config already registers the aspect once, the
duplicate can only be produced by the **invoking command** expanding the
`clippy`/`_lint` config, or the aspect flag, more than once (e.g.
`--config=clippy` supplied twice, or `--config=clippy` combined with an explicit
`--aspects=…%clippy_strict`). The emitted
`configs were expanded more than once: [_lint]` warning is consistent with
`_lint` being pulled in twice, and the
`aspect …%clippy_strict added more than once` error is the direct consequence.

The `WARNING: Duplicate rc file: …/quality/static_analysis/static_analysis.bazelrc
is read multiple times …` line appears in **every** check (including the 11 that
pass) and is therefore a harness-level rc-file read, not the cause of the lint
failure by itself.

This is the **same** native-invocation/configuration defect recorded in
`correction-1.md` §2 and `correction-2.md` §2. It remains unaddressed by the
measurement pipeline because command construction is outside agent authority.

## 3. Why no source/test correction applies (measured-defect test)

1. **No measured source/test defect.** 11 of 12 checks pass; the only failure
   aborts in Bazel analysis configuration and emits no Rust
   source/compiler/clippy finding. There is no failing test, no compilation
   error and no lint diagnostic to correct. Editing source cannot remove a
   duplicate flag supplied by the invoking command.
2. **Premise already implemented at baseline; nothing to edit.** The runtime and
   concept test targets named by the issue carry no `tags = ["manual"]`:
   - `//score/mw/com/rust/score_com_concept:score_com_concept-test` —
     `score/mw/com/rust/score_com_concept/BUILD:35-44` (no `tags`; only
     `target_compatible_with = ["@platforms//os:linux"]`).
   - `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`
     — `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD:36-46` (no
     `tags`; Linux constraint).
   - `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test`
     — `score/mw/com/example/com-api-example/BUILD:52-74` (no `manual`; sanitizer
     `select` only).
   The only retained `manual` Rust test is the concept doc test
   (`score/mw/com/rust/score_com_concept/BUILD:46-56`, tag at `:54`),
   intentionally kept for the documented `rust_doc_test`/LLD native-link
   limitation and out of `#794` scope. The `rust_unit_test` internal `_linux`
   target's `manual` tag (`quality/unit_testing/unit_testing.bzl:170`) is by
   macro design; only the non-`manual` forwarding target (`:181-195`)
   participates in `//...`. Removing either would be a regression or would
   violate the "do not remove exclusions to obtain cleanliness" rule.
3. **No check may be weakened.** Removing the lint obligation, dropping a target,
   editing `build:clippy` to drop the aspect (which the CI lint job depends on),
   inlining `_lint` to dodge the expansion warning, or relaxing `clippy_strict`
   to convert the run green is prohibited. The check plan in
   `.rust-queue/reports/check-plan.json` is retained unchanged.

No file under `score/`, `quality/` or any native build path was modified by this
correction. The candidate source still equals the baseline for every path in the
change surface, matching the unchanged `measured_subject_hashes_sha256`.

## 4. Blocker and required external action

**Blocker class**: native-**invocation/configuration** defect in the `lint`
check — the `clippy_strict` aspect is registered more than once because the
invoking command expands the `clippy`/`_lint` config (or passes the aspect flag)
more than once. It is **external to the agent's change surface** and cannot be
corrected from repository source without weakening CI lint policy, which is
forbidden.

This is **not** `infrastructure_unavailable` (`infrastructure_error = null`) and
**not** a missing design/backend prerequisite of `#794` — every `#794`-scope
source/test/build/docs obligation passes. It is an invocation-precondition
failure of the measurement command, repeated unchanged across attempts 0, 1 and
2, so the run stops here as required.

Deterministic re-measurement must re-run the lint obligation with the aspect
registered exactly once, matching the checked-in CI form
(`.github/workflows/_linter.yml:115-125`):

```
aspect lint \
  --bazel-flag=--config=ci \
  --bazel-flag=--config=clippy \
  -- //...
```

or, for the two library targets, a `bazel build --config=ci --config=clippy`
invocation that does **not** additionally pass `--aspects=…%clippy_strict` and
does not repeat `--config=clippy`/`--config=_lint`. Command construction is
outside agent authority, so the correction stops here and the blocker is recorded
rather than patched around.

## 5. Preserved evidence and unresolved items (unchanged from prior stages)

- Prior failed results are retained verbatim and **not** modified, overwritten or
  re-labelled:
  - `check-2` summary is the current content of
    `.rust-queue/reports/native-check-summary.json` (left as-is);
  - the earlier `check-0` and `check-1` failures and their analyses are preserved
    in `.rust-queue/reports/correction-1.md` and
    `.rust-queue/reports/correction-2.md`.
- `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` remains
  intentionally `manual` (documented `rust_doc_test`/LLD limitation).
- **Pending offline acceptance**: Tokio multi-thread sanitizer findings (LSan
  leak from `tokio::runtime::scheduler::multi_thread::MultiThread::new`; TSan
  `<String as Clone>::clone` race between the test thread and a `tokio-rt-worker`)
  on `com-api-example-tokio-integration-test` remain open; the sanitizer
  `target_compatible_with` gate is untouched. Fix-or-suppress is an explicit
  follow-up in the issue author's comment, not part of `#794` acceptance.
- **Unknown native IDs**: requirement/design/verification identifiers remain
  **unknown** (issue template boxes unchecked; not discoverable from selected
  sources). Not fabricated.
- No counter was reset and no passing evidence was fabricated;
  `engineering_acceptance` remains **pending**.

## 6. Manifest and next action

- Source diff in this correction: **none** (candidate source == baseline).
- Report artifact produced by this correction:
  - `.rust-queue/reports/correction-3.md` (this file)
- Unchanged, preserved: `.rust-queue/reports/scope.md`,
  `.rust-queue/reports/implementation.md`,
  `.rust-queue/reports/check-plan.json`,
  `.rust-queue/reports/native-check-summary.json`,
  `.rust-queue/reports/correction-1.md`,
  `.rust-queue/reports/correction-2.md`.
- File digests are **not computable** within the file-tool boundary (no
  shell/hash tooling); binding is by exact repository-relative path and baseline
  commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.

**Concrete next action** (bound environment, outside agent authority): re-run the
`lint` check with a single clippy-aspect registration as in §4; keep all other
check-plan entries as-is. Expected at baseline `381d43d`: the two library builds,
the runtime and concept tests, the two doc tests, the concept macro unit test,
and the default-config example test all pass, and the lint analysis completes
without the `added more than once` aspect error. No source patch is owed for
`#794`.
