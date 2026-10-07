# Correction 2 — issue #781 "Implementation of MethodInArgPtr in rust side"

Issue: `eclipse-score/communication` #781 (label `rust-api`, state `open`, 0 comments)
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `implementation` · Platform: Linux (`linux_x64`) only · No QNX · Model: DeepSeek Flash
Correction counter: **2 of at most 3** (this file) · Prior failed native attempts retained: **0 and 1**
Measured subject: workspace patch, `measured_subject_hashes_sha256 =
29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45`

Status: **blocker sustained — no source/test change, no check weakened.** The latest bounded native
result (attempt `1`) fails only on the `lint` check, and that failure is the same invocation-level
Bazel aspect-registration duplication already recorded in `correction-1.md` for attempt `0`. It is
**not** a measured source or test defect: the aspect never analysed the subject, so no clippy
diagnostic exists to correct. Engineering acceptance remains a **pending offline human decision**.

---

## 1. Latest bounded native evidence read (operator-supplied)

Source: `.rust-queue/reports/native-check-summary.json` (attempt `1`, `kind =
measured_native_command`, `exit_code = 1`, `infrastructure_error = null`,
`engineering_acceptance = "pending"`). Native raw result:
`jobs/781/execution/check-1/native-result.json`, sha256
`4a7c41e23bf2483404bd5e12d825c9b31d57f7b3a0bf08684f9644051bed2713`.

| # | kind | target (BUILD-derived) | exit | outcome |
| --- | --- | --- | --- | --- |
| 1 | query | `//score/mw/com/impl/methods:method_signature_element_ptr` | 0 | PASS |
| 2 | build | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` | 0 | PASS |
| 3 | build | `//score/mw/com/impl/plumbing/rust/test_support:test_helper_size_provider` | 0 | PASS |
| 4 | test | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_test_rs` | 0 | PASS (`1 test passes`) |
| 5 | docs | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_doc_test` | 0 | PASS |
| 6 | lint | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` | 1 | **FAIL (analysis)** |

Measured inventory: **6 recorded / 5 pass / 1 fail / 0 executed-by-agent**. The three regression
rows of `check-plan.json` (`sample_ptr_test_rs`, `sample_allocatee_ptr_test_rs`,
`method_signature_element_ptr_test`) were again **not** part of this recorded run; they remain
**pending**, not failed and not passed. No counter is reset and no passing evidence is added.

### 1.1 Attempt-0 vs attempt-1 comparison (retained, not overwritten)

| Field | attempt 0 | attempt 1 |
| --- | --- | --- |
| `native_result` sha256 | `80bb1dd491d9aa5c65e7fd38f68ab3c7757a502d251302c59b16390838f9c9a8` | `4a7c41e23bf2483404bd5e12d825c9b31d57f7b3a0bf08684f9644051bed2713` |
| `measured_subject_hashes_sha256` | `29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45` | `29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45` |
| passing checks | query, build ×2, test, docs | query, build ×2, test, docs |
| failing check | lint (aspect registration) | lint (aspect registration) |
| `infrastructure_error` | `null` | `null` |

The measured subject hash is **byte-identical across both attempts** (no source/test edit occurred
between them), and the failing `lint` tail is textually the same error. Two independent
measurements of an **unchanged** subject producing the **same analysis-time failure** is dispositive
that the failure is a property of the lint invocation, not of the patch.

## 2. Exact failing evidence (lint, check #6)

From the bounded tail of the operator-supplied `lint` check (`exit_code = 1`):

```
WARNING: The following configs were expanded more than once: [_lint]. For repeatable flags, ...
...
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
...
WARNING: errors encountered while analyzing target '//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs', it will not be built.
...
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

The same invocation still printed the up-to-date artifact, confirming the target itself is valid:

```
INFO: Found 1 target...
Target //score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs up-to-date:
  bazel-bin/score/mw/com/impl/plumbing/rust/libmethod_in_arg_ptr_rs-375123505.rlib
```

## 3. Root-cause classification — invocation, not source/test (sustained)

`@@score_rust_policies+//clippy:linters.bzl%clippy_strict` is registered once by the `clippy`
config in `quality/static_analysis/static_analysis.bazelrc` (unchanged, re-read this correction):

```
build:clippy --config=_lint
build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict
```

The recorded run reports `_lint` "expanded more than once", and consequently the same
`--aspects=...%clippy_strict` value reaches the analysis phase twice, which Bazel rejects
(`aspect ... added more than once`) before the aspect analyses any target. This is a
command-line/configuration duplication in the lint invocation; no `BUILD`-level mechanism can
register a command-line aspect twice.

The repository's own native CI documents the correct invocation and the exact failure mode to
avoid in `.github/workflows/_linter.yml` (re-read this correction):

> `--bazel-flag=--config=${{ matrix.bazel-config }}` reuses the same aspect + toolchain
> configuration as `bazel test --config=${{ matrix.bazel-config }}` ... — the aspect is
> deliberately NOT also passed via `--aspect=` here, since Bazel rejects the same aspect being
> registered twice.

Conclusion:

- The lint failure is caused by the clippy aspect being applied **twice** through duplicated
  config/aspect expansion. It is an **invocation/platform defect**, not a defect in the changed
  Rust source, BUILD rules, test, or C++ helper.
- **No clippy diagnostic was produced** in either attempt. The aspect never ran on the subject;
  therefore no measured source/test lint finding exists to correct.
- Every subject-executing check that did run (query, build ×2, Rust FFI size/align test, rustdoc)
  passed on the same, unchanged subject hash.
- `infrastructure_error` is recorded as `null` by the collector, but the recorded message is
  unambiguously an analysis-time aspect-registration error (`added more than once`) with the
  matching `configs expanded more than once` warning — not a compiler/linter finding.
  `infrastructure_error = null` must not be read as "source defect": the collector's field records
  its own crash/harness-unavailability channel, not every Bazel analysis failure.

## 4. Action taken in this correction

Per the correction rule "correct only a measured source/test defect" and "do not change code or
weaken checks" for an invocation-cause failure:

- **No source, BUILD, test, FFI-helper, `.bazelrc`, CI, or BUILD-derived label was modified.**
- The lint policy (`clippy_strict`), toolchain/pin files, licenses/SPDX headers and supported
  configs are unchanged; nothing was suppressed or excluded to force a pass.
- The lint check was **not** dropped, retargeted or downgraded in `check-plan.json`; an obligation
  is not removed to make a run look green.
- Prior failed evidence is retained unmodified in `native-check-summary.json` (attempts `0` and
  `1`, both with the lint check failed) and in `correction-1.md`.
- Counters are not reset: native attempt count is unchanged at `1`; the recorded lint check remains
  **failed**; engineering acceptance remains **pending**.
- `check-plan.json`, `implementation.md`, `review-packet.md`, `scope.md` and `_probe.txt` are left
  as-is so the deterministic collector measures the same subject hash. This correction adds only
  `correction-2.md`.

## 5. Correction requested of the deterministic collector (not agent authority)

Re-issue only the `lint` check for
`//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` such that the
`@score_rust_policies//clippy:linters.bzl%clippy_strict` aspect is registered **exactly once** on
the Linux config, mirroring native CI `.github/workflows/_linter.yml`:

- `aspect lint --bazel-flag=--config=<linux_x64> --bazel-flag=--config=clippy -- //<target>`, **or**
  equivalently `bazel build --config=<linux_x64> --config=clippy //<target>`,
- **without** additionally passing `--aspects=...%clippy_strict` and **without** repeating any
  `--config` that already expands the aspect (the current run expanded `_lint` more than once in
  both attempts `0` and `1`).

This is a check-invocation correction only; it neither changes nor weakens the lint obligation.
No source edit is warranted, or truthful, before the aspect actually runs once on the subject.

## 6. Preserved state and next action

- Retained: `native-check-summary.json` (attempt `1`, lint failed), `check-plan.json`,
  `implementation.md`, `review-packet.md`, `scope.md`, `correction-1.md`, `_probe.txt`.
- Engineering acceptance: **pending offline human decision**; unresolved design/ownership items
  from `implementation.md` §5 (FFI ownership/destruction of the move-only type, placement,
  `Send` contract, `MethodReturnTypePtr`, requirements/design impact) remain open and are **not**
  resolved here.
- Concrete next action: the collector fixes the lint invocation (§5), re-measures the unchanged
  subject hash, and restores the three pending regression checks; only then can a genuine clippy
  result exist; afterwards submit the patch and open decisions for offline review.

*No credentials are embedded. This correction records a blocker; it does not certify, qualify or
accept the native work product.*
