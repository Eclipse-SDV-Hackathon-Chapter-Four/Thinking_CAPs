# Correction 3 of 3 — Issue #782: Runtime implementation for Rust Method APIs

- **Repository / issue**: `eclipse-score/communication` #782 "Improvement: Runtime implementation
  for Rust Method APIs" (`open`, label `rust-api`).
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (unchanged; no native source edited by the
  draft run, by fix1/fix2, or by correction 1/2).
- **Correction**: **3 of at most 3** (`max_source_corrections = 3`,
  `.rust-queue/context/task.json`). This is the final correction in the budget.
- **Authority**: DeepSeek Flash only; Linux only; no QNX task/execution; file tools only. Shell,
  network/web, delegation, publishing and acceptance tools are blocked. Command stages and raw
  evidence are outside agent authority.
- **Disposition**: **no source/test change; no check weakened — blocker recorded.** The single
  measured failure (check 19, `lint`) is a Bazel command/config-layer (harness) defect, **not** a
  measured source or test defect, and the issue is independently gated on a **missing design/backend
  prerequisite**. Prior failed results are retained unchanged; no counter reset; no passing evidence
  fabricated.

## 1. Latest bounded native result read (operator-supplied, attempt 2)

Source: `.rust-queue/reports/native-check-summary.json` (this workspace) — the latest bounded summary
supplied by the operator, `"attempt": 2`, matching driver `check 782 2`. Native result file:
`…/jobs/782/execution/check-2/native-result.json`
(`sha256 afb60ee7ef20f5064b854f7362303ef3a225434ce85a544f45cb03b058f78dd0`).

- `measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`
  — **identical to attempt 0 and attempt 1**, so the measured subject did not change across any
  attempt and no source-side edit is claimed or implied.
- `infrastructure_error = null`; `passed = false` (overall); `exit_code = 1`;
  `engineering_acceptance = "pending"`.

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

Only check 19 (lint) failed. Checks 1–18 passed. `engineering_acceptance` stays `pending`; the overall
envelope is `passed = false` solely because of check 19.

## 2. Diagnosis of check 19 — not a measured source/test defect

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

Interpretation, bound to source read in this workspace:

- The failure occurs **during Bazel analysis**, before any clippy action runs. There is **no clippy
  diagnostic** (no lint `error:`/`warning:` emitted by a lint rule) anywhere in the tail. It is
  therefore **not** a lint violation in any Rust source or test, and not a source/test defect.
- The warning `configs were expanded more than once: [_lint]` together with
  `aspect … clippy_strict added more than once` is the fingerprint of the **invocation** expanding
  the lint config chain more than once. The repository defines the aspect **exactly once**, per the
  native config re-read at baseline:
  - `quality/static_analysis/static_analysis.bazelrc` line 30:
    `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict` (the only
    definition of this aspect).
  - line 29: `build:clippy --config=_lint`.
  - lines 15–18: `build:_lint` sets only `--extra_toolchains`, `--output_groups`,
    `--@aspect_rules_lint//lint:fail_on_violation` and `--keep_going` — it does **not** define the
    aspect. So `clippy` adding `--config=_lint` is correct and non-duplicating **provided the
    invocation expands the config chain once**.
  - `.bazelrc` line 188 imports this file exactly once
    (`import %workspace%/quality/static_analysis/static_analysis.bazelrc`).
  A double expansion of `[_lint]` (and consequently the aspect from `clippy`) therefore arises from
  how the lint command is assembled at the **command/config layer (harness/driver)**, which the task
  states is outside agent authority.
- The two lint targets are valid, existing, BUILD-derived labels: both built successfully with exit 0
  as checks 2 and 6. So the plan's lint `targets` and `config` are not the defect; the defect is in
  how the lint command is assembled, not in the repository.
- No repository source, test, BUILD, MODULE/lock, license, pin or lint **policy** file is implicated.
  Editing `quality/static_analysis/static_analysis.bazelrc` (dropping the aspect or the `_lint`
  composition) to force check 19 to pass would **weaken the native lint policy**, which the
  correction rule and `native-verification.md` forbid.
- The attempt-2 result reproduces the same failure class recorded in `correction-1.md` §2 and
  `correction-2.md` §2 with an identical `measured_subject_hashes_sha256`, confirming there is no
  source-side remedy that the measured run can validate.

Because the measured failing check is not a source/test defect, there is **nothing within the
correction scope to correct in code or tests**.

## 3. Second, independent blocker — design/backend prerequisite absent

Independently of the lint harness defect, the issue's premise does not hold at the selected baseline.
The Rust Method API design/contract is not present at `381d43d`:

- `.rust-queue/context/comments.json`: maintainer `bharatGoswami8` (2026-08-31) — *"The design proposed
  in …/pull/818 is still under review."*; the runtime layer is backend-specific and invokes bridge FFI
  mapping to C++ (2026-09-08 comment), so the Method work is not implementable at the Rust layer alone
  without the underlying backend change.
- Globbing in this workspace reconfirms the absence:
  - `score/mw/com/impl/rust/com-api/com-api-runtime-lola/**/*.rs` → only `consumer.rs`, `lib.rs`,
    `producer.rs`, `runtime.rs`. There is **no `method.rs`**, no `LolaMethodCaller`/`LolaMethodHandler`.
  - `score/mw/com/rust/**/*method*` → **no match**; `score/mw/com/**/method*.rs` → **no match**.
  - `score/mw/com/rust/design/**` → only architecture/module/sequence artifacts for the
    Event/lifecycle surface; **no Method design document or #777/#818 artifact**.
  The contributor-reported `method.rs` (`todo!()` placeholders) belongs to the unmerged #818 branch and
  is not in the baseline tree.
- Prerequisite **#781** status is unknown offline; design PR #777/#818 merge state is not retrievable
  (retrieval is a supplied snapshot only).
- Prior stages (`scope.md`, `implementation.md`, `review-packet.md`, `correction-1.md`,
  `correction-2.md`) already established that no Method trait, `interface!` arm, error variant, runtime
  module or FFI symbol exists at baseline, and that implementing one would require inventing the
  API/ABI owned by the open design.

This is a **missing design/backend prerequisite**, matching the correction rule's
"design/backend prerequisite is missing" case: **do not change code, do not weaken checks.**

## 4. Actions taken in this correction

1. Read the latest bounded native result summary (`.rust-queue/reports/native-check-summary.json`,
   attempt 2) supplied by the operator.
2. Classified check 19 as an infrastructure/command-config defect (lint config chain expanded twice at
   the Bazel command layer, adding `clippy_strict` more than once) and the issue as blocked on the
   missing #818/#777/#781 design prerequisite.
3. **No code change**: zero native files (Rust, C++, BUILD, MODULE, license, pin, lint/CI policy,
   design doc) modified. The `measured_subject_hashes_sha256` is unchanged from attempts 0 and 1, so no
   source-side edit is claimed or implied.
4. **No check weakened or removed**: `check-plan.json` lint check retained as-is; the lint targets, the
   `clippy_strict` aspect and the native lint policy are preserved.
5. **Prior failed results retained**: the attempt-0, attempt-1 and attempt-2 results remain recorded
   exactly, including the failed lint exit code 1 in `correction-1.md`, `correction-2.md` and
   `native-check-summary.json`. No counter reset; no passing evidence fabricated; no evidence reused
   under a new label.
6. This report added under `.rust-queue/reports/`. File hashes are **not** claimed: hashing requires a
   shell, which is blocked in this environment (preserved as missing, not fabricated).

## 5. What would legitimately resolve check 19

Outside agent authority (command stage / harness owner):

- Assemble the lint invocation so the `clippy`/`_lint` config chain is expanded **exactly once**,
  i.e. do not pass a duplicated `--config=clippy`/`--config=_lint` and do not combine a lint config
  with an explicit `--aspects=…clippy_strict`. The native per-config definitions
  (`build:_lint` at lines 15–18, `build:clippy --config=_lint` at line 29,
  `build:clippy --aspects=…clippy_strict` at line 30) are already correct; the duplication is in the
  invocation.

No repository change is the correct remedy, and none is made here.

## 6. Engineering status (unchanged boundaries)

- **Technical status**: assessment/blocker recorded. Implementation remains **blocked/pending** at
  `381d43d`: (a) the lint checkpoint cannot be measured due to a harness command/config defect that is
  outside agent authority, and (b) the Rust Method API design prerequisite (#818/#777, #781) is not
  present/admitted at baseline.
- **Correction budget**: this is correction **3 of 3**; the source-correction budget is exhausted with
  no source correction warranted by the measured evidence.
- **Engineering acceptance**: **none claimed / pending offline**. Passing checks or a successful run
  cannot supply the required human decision; no native work product is marked
  qualified/accepted/released.
- **Concrete next action**:
  1. Harness owner: fix the double-expansion of `clippy`/`_lint` in the lint invocation and re-run
     check 19 (all other 18 checks already pass and must not be regressed).
  2. Maintainer: admit/land the #818 Method design (and #777) at an authorized revision and confirm
     prerequisite #781; then re-scope the implementation against that design.
