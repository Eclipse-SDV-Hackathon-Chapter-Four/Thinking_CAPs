# Correction 1 of 3 — Issue #782: Runtime implementation for Rust Method APIs

- **Repository / issue**: `eclipse-score/communication` #782 "Improvement: Runtime implementation
  for Rust Method APIs" (`open`, label `rust-api`).
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (unchanged; no source edit by this run).
- **Correction**: 1 of at most 3 (`max_source_corrections = 3`, `.rust-queue/context/task.json`).
- **Authority**: DeepSeek Flash only; Linux only; no QNX task/execution; file tools only. Shell,
  network/web, delegation, publishing and acceptance tools blocked. Command stages and raw evidence
  are outside agent authority.
- **Disposition**: **no source/test change; no check weakened — blocker recorded.** The measured
  failure is a command/config-layer (harness) defect, and the issue itself remains gated on a missing
  design/backend prerequisite. Retained prior failed results unchanged.

## 1. Measured native result read (operator-supplied, attempt 0)

Source: `.rust-queue/reports/native-check-summary.json` (this workspace). Native result file:
`…/jobs/782/execution/check-0/native-result.json`
(`sha256 854eb26d50980e6c2a683773eb508f6be4738021524ab65ddc0d51811c2d1033`).
`measured_subject_hashes_sha256 =
3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`.
`infrastructure_error = null`. `passed = false` (overall), `exit_code = 1`.

Per-check outcome (all `config = linux_x64`, `timed_out = false`):

| # | kind | target(s) | exit |
|---|---|---|---|
| 1 | query | `//score/mw/com/rust:score_com` | 0 |
| 2 | build | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 |
| 3 | build | `//score/mw/com/impl/rust/com-api/com-api-ffi-lola:bridge_ffi_rs` | 0 |
| 4 | build | `…:bridge_ffi_lola` | 0 |
| 5 | build | `…:registry_bridge_macro_cpp` | 0 |
| 6 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | 0 |
| 7 | build | `//score/mw/com/rust:score_com` | 0 |
| 8 | test | `…:com-api-runtime-lola-tests` | 0 (PASSED) |
| 9 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | 0 (PASSED) |
| 10 | test | `…:score_com_concept-macros-unit-tests` | 0 (PASSED) |
| 11 | test | `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | 0 (PASSED) |
| 12 | test | `//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync` | 0 (PASSED) |
| 13 | test | `//score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test:test_com_api_async` | 0 (PASSED) |
| 14 | build | `//score/mw/com/example/com-api-example/com-api-gen:com-api-gen` | 0 |
| 15 | build | `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs` | 0 |
| 16 | docs | `…:com-api-runtime-lola-doc-tests` | 0 |
| 17 | docs | `…:score_com_concept-macros-tests` | 0 |
| 18 | docs | `//score/mw/com/rust/score_com_macros:score-com-macros-tests` | 0 |
| 19 | **lint** | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | **1** |

Only check 19 (lint) failed. Checks 1–18 passed (`engineering_acceptance` stays `pending`; the
overall envelope is `passed = false` solely because of check 19).

## 2. Diagnosis of check 19 — not a source/test defect

Exact bounded tail (native summary, check 19):

```
WARNING: The following configs were expanded more than once: [_lint]. For repeatable flags,
repeats are counted twice and may lead to unexpected behavior.
…
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
WARNING: errors encountered while analyzing target '//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola', it will not be built.
aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
WARNING: errors encountered while analyzing target '//score/mw/com/rust/score_com_concept:score_com_concept', it will not be built.
INFO: Found 2 targets...
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

Interpretation, bound to source:

- The failure occurs **during Bazel analysis**, before any clippy action runs. There is **no clippy
  diagnostic** (no `error:`/`warning:` from a lint rule) in the tail. It is therefore not a lint
  violation in any Rust source or test.
- The message `aspect … clippy_strict added more than once` with `configs … expanded more than once:
  [_lint]` means the same aspect flag was supplied twice on the Bazel command line. The native
  config chain (read at baseline) is:

  | File | Line | Content |
  |---|---|---|
  | `quality/static_analysis/static_analysis.bazelrc` | 15–18 | `build:_lint` flags |
  | `quality/static_analysis/static_analysis.bazelrc` | 29 | `build:clippy --config=_lint` |
  | `quality/static_analysis/static_analysis.bazelrc` | 30 | `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict` |
  | `.bazelrc` | 188 | `import %workspace%/quality/static_analysis/static_analysis.bazelrc` |

  Because `--aspects=…clippy_strict` is defined by `build:clippy`, it is added **once per expansion of
  `clippy`/`_lint`**. Passing that config (or `--config=_lint`) more than once on the invocation — or
  combining the lint config with an explicit `--aspects=…clippy_strict` — adds the aspect twice. The
  observed `[_lint]` double-expansion is the fingerprint of exactly that command-construction
  duplication. This is a **command/config-layer (harness/driver) defect**, which the task states is
  outside agent authority.
- The two lint targets are valid, existing, BUILD-derived labels: both were built successfully with
  exit 0 as checks 2 and 6. So the plan's lint `targets`/`config` are not the defect; the defect is in
  how the lint invocation is assembled, not in the repository.
- No repository source, test, BUILD, MODULE/lock, license, pin or lint **policy** file is implicated.
  Changing `static_analysis.bazelrc` (or removing the aspect) to "make the check pass" would **weaken
  the native lint policy**, which the correction rule and `native-verification.md` forbid.

## 3. Second, independent blocker — design/backend prerequisite absent

Independently of the lint harness defect, the issue's premise does not hold at the selected baseline.
The Rust Method API design/contract is not present at `381d43d`:

- `.rust-queue/context/comments.json` (2026-08-31, maintainer `bharatGoswami8`): *"The design proposed
  in …/pull/818 is still under review."* (2026-09-08): the runtime layer is backend-specific and
  invokes bridge FFI mapping to C++; issue #767 is a C++-backend concern.
- The contributor-reported `com-api-runtime-lola/method.rs` (`LolaMethodCaller`/`LolaMethodHandler`
  `todo!()` placeholders) is **not present** at `381d43d`; it lives on the unmerged #818 branch.
- Prerequisite **#781** status is unknown offline; design PR #777/#818 merge state is not retrievable
  (retrieval is a supplied snapshot only).
- Prior stages (`scope.md`, `implementation.md`, `review-packet.md`) already established that no
  Method trait, macro arm, error variant, runtime module or FFI symbol exists at baseline, and that
  implementing one would require inventing the API/ABI owned by the open design.

This is a **missing design/backend prerequisite**, matching the correction rule's
"design/backend prerequisite is missing" case: do not change code, do not weaken checks.

## 4. Actions taken in this correction

1. Read the latest bounded native result summary (`.rust-queue/reports/native-check-summary.json`).
2. Classified check 19 as an infrastructure/command-config defect (aspect/config duplicated at the
   Bazel command layer) and the issue as blocked on the missing #818/#777/#781 design prerequisite.
3. **No code change**: zero native files (Rust, C++, BUILD, MODULE, license, pin, lint/CI policy,
   design doc) modified. Baseline-to-working-tree source digest remains unchanged.
4. **No check weakened or removed**: `check-plan.json` lint check retained as-is; the lint targets,
   the `clippy_strict` aspect and the native lint policy are preserved.
5. **Prior failed results retained**: checks 1–19 above remain recorded exactly, including the failed
   lint exit code 1. No counter reset; no passing evidence fabricated; no evidence reused.
6. This report added under `.rust-queue/reports/`. File hashes are not claimed: hashing requires a
   shell, which is blocked in this environment (preserved as missing, not fabricated).

## 5. What would legitimately resolve check 19

Outside agent authority (command stage / harness owner):

- Assemble the lint invocation so `clippy`/`_lint` is expanded **exactly once**, i.e. do not pass both
  a `--config=clippy`/`--config=_lint` and an explicit `--aspects=…clippy_strict`, and do not repeat
  the lint config. The native per-config definition (`build:clippy --config=_lint` +
  `build:clippy --aspects=…clippy_strict`) is already correct; the duplication is in the invocation.

No repository change is the correct remedy, and none is made here.

## 6. Engineering status (unchanged boundaries)

- **Technical status**: assessment/blocker recorded. Implementation remains **blocked/pending** at
  `381d43d`: (a) the lint checkpoint cannot be measured due to a harness command/config defect, and
  (b) the Rust Method API design prerequisite (#818/#777, #781) is not present/admitted.
- **Engineering acceptance**: **none claimed / pending offline**. Passing checks or a successful run
  cannot supply the required human decision; no native work product is marked qualified/accepted.
- **Concrete next action**:
  1. Harness owner: fix the double-expansion of `clippy`/`_lint` in the lint invocation and re-run
     check 19 (all other 18 checks already pass and must not be regressed).
  2. Maintainer: admit/land the #818 Method design at an authorized revision and confirm prerequisite
     #781; then re-scope the implementation against that design.
