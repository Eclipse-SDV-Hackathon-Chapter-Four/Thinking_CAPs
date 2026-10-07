# correction-1.md — Issue #794 (correction 1 of at most 3)

"Improvement: Remove bazel `tags = [\"manual\"]` from rust test targets"

- **Repository / issue**: eclipse-score/communication #794
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- **Runtime / model**: Linux only; DeepSeek Flash only. No QNX task or execution.
- **Stage**: deterministic `check 794 0` failed (`passed: false`, `exit_code: 1`);
  this is correction attempt 1 of at most 3.
- **Supplied evidence read**: `.rust-queue/reports/native-check-summary.json`
  (copy of the `check-0` bounded native summary, `attempt: 0`) and the bounded
  native summary echoed in the stage prompt.
- **Authority**: disposable workspace only. Shell, delegation, publishing and
  acceptance tools are blocked; the agent executed **no** native command. Command
  stages and raw evidence remain outside agent authority. No QNX work.

## 1. Measured outcome of check-0 (per supplied bounded native summary)

`measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`;
`native_result.sha256 = 540888a838acecc054b0024a6c6f4826a64712465c48158b1cb27e445b25f87c`;
`infrastructure_error = null`.

| # | kind | target(s) | exit | outcome |
| --- | --- | --- | --- | --- |
| 1 | query | `//score/mw/com/rust/score_com_concept:all` | 0 | pass (shows `rust_test score_com_concept-test`, `rust_doc_test score_com_concept-macros-tests`, forwarding `...-macros-unit-tests`) |
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
| 12 | lint | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | 1 | **FAIL — analysis error, no source diagnostic emitted** |

Every source/test/build/docs/query obligation passed. Exactly one check failed,
and it failed during Bazel **analysis configuration**, not on a code finding.

## 2. Root cause of the single failure (measured, source-backed)

Bounded tail of check 12:

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

The clippy aspect is registered twice by the native lint invocation. Source shows
the repository registers it exactly once:

- `quality/static_analysis/static_analysis.bazelrc:29-30` — `build:clippy`
  expands `--config=_lint` and adds
  `--aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict` **once**.
- `.github/workflows/_linter.yml:83-86` documents the exact prohibition: the
  aspect is deliberately **NOT** also passed via `--aspect=` because "*Bazel
  rejects the same aspect being registered twice.*" The CI job registers it only
  through `--bazel-flag=--config=clippy` (`:115-125`).
- `.bazelrc:188` imports `quality/static_analysis/static_analysis.bazelrc` once.

Because the `clippy` config itself registers the aspect once, the duplicate
registration can only come from the invoking command expanding/configuring the
clippy aspect twice (e.g. `--config=clippy` supplied more than once, or
`--config=clippy` combined with an explicit `--aspects=...clippy_strict`). The
emitted `configs were expanded more than once: [_lint]` warning is consistent with
`_lint` being pulled in twice (directly and transitively via `clippy`). This is a
**command/configuration defect in the native lint invocation**, and it is the
exact failure mode the checked-in CI workflow already guards against. It is not a
defect in any file the issue's change surface touches.

## 3. Why no source/test correction applies

1. **No measured source/test defect.** All 11 non-lint checks passed; the lint
   check emitted no clippy diagnostic — it aborted in analysis. The failing check
   never reached the repository's lint policy.
2. **Premise already implemented at baseline; nothing to edit.** The
   runtime and concept test targets requested by the issue carry no
   `tags = ["manual"]`:
   - `//score/mw/com/rust/score_com_concept:score_com_concept-test` —
     `score/mw/com/rust/score_com_concept/BUILD:35-44` (no `tags`; only
     `target_compatible_with = ["@platforms//os:linux"]`).
   - `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`
     — `.../com-api-runtime-lola/BUILD:36-46` (no `tags`; Linux constraint).
   - `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test`
     — `score/mw/com/example/com-api-example/BUILD:52-74` (no `manual`; sanitizer
     `select` only).
   The only retained `manual` Rust target is the concept doc test
   (`score_com_concept/BUILD:54`), intentionally kept for the documented
   `rust_doc_test`/LLD native-link limitation, and out of #794 scope. The
   `rust_unit_test` `_linux` target's `manual` tag
   (`quality/unit_testing/unit_testing.bzl:170`) is by macro design and likewise
   not in scope. Removing any of these would be a regression or would violate the
   "do not remove exclusions to obtain cleanliness" rule.
3. **No check may be weakened.** Removing the lint obligation, dropping a target,
   or relaxing `clippy_strict` to convert the run green is prohibited. The check
   plan is retained unchanged.

No file under `score/` or `quality/` was modified by this correction. The
candidate source still equals the baseline for every path in the change surface.

## 4. Blocker and required external action

**Blocker class**: native-**invocation/configuration** defect in the `lint` check
(duplicate `clippy_strict` aspect registration). It is external to the agent's
change surface and cannot be corrected from repository source without weakening
CI lint policy, which is forbidden.

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
invocation that does **not** additionally pass `--aspects=...clippy_strict` and
does not repeat `--config=clippy`/`--config=_lint`. Command construction is
outside agent authority, so the correction stops here and the blocker is recorded
rather than patched around.

Retained failure: check-0's result stands. `engineering_acceptance` remains
**pending**; this agent neither marks native work accepted nor fabricates a pass.

## 5. Preserved evidence and unresolved items (unchanged from prior stages)

- Prior failed `check-0` evidence is retained verbatim in
  `.rust-queue/reports/native-check-summary.json`; it was **not** modified,
  overwritten, or re-labelled by this correction.
- `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` remains
  intentionally `manual` (documented LLD limitation).
- Tokio multi-thread sanitizer findings (LSan leak; TSan `<String as Clone>::clone`
  race) on `com-api-example-tokio-integration-test` remain **pending offline
  acceptance**; the sanitizer `target_compatible_with` gate is untouched.
- Requirement/design/verification native IDs remain **unknown** (issue template
  boxes unchecked; not discoverable from selected sources). Not fabricated.

## 6. Manifest and next action

- Source diff in this correction: **none** (candidate source == baseline).
- Report artifact produced by this correction:
  - `.rust-queue/reports/correction-1.md` (this file)
- Unchanged, preserved: `.rust-queue/reports/scope.md`,
  `.rust-queue/reports/implementation.md`,
  `.rust-queue/reports/check-plan.json`,
  `.rust-queue/reports/native-check-summary.json`.
- File digests are **not computable** within the file-tool boundary (no
  shell/hash tooling); binding is by exact repository-relative path and baseline
  commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.

**Concrete next action** (bound environment, outside agent authority): re-run the
`lint` check with a single clippy-aspect registration as in §4; keep all other
check-plan entries as-is. Expected at baseline `381d43d`: the two library builds,
the runtime and concept tests, the two doc tests, the concept macro unit test,
and the default-config example test all pass, and the lint analysis completes
without the `added more than once` aspect error. No source patch is owed for
#794.
