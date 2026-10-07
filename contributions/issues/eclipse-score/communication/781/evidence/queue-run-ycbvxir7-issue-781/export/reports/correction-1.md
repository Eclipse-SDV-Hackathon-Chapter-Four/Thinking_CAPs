# Correction 1 — issue #781 "Implementation of MethodInArgPtr in rust side"

Issue: `eclipse-score/communication` #781 (label `rust-api`, state `open`, 0 comments)
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `implementation` · Platform: Linux (`linux_x64`) only · No QNX · Model: DeepSeek Flash
Correction counter: **1 of at most 3** (this file) · Prior native attempt counter: **0** (unchanged)
Measured subject: workspace patch, `measured_subject_hashes_sha256 =
29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45`

Status: **blocker recorded — no source/test change, no check weakened.** The single failing
check is an invocation-level Bazel aspect registration duplication, not a measured source or
test defect. Engineering acceptance remains a **pending offline human decision**.

---

## 1. Bounded native evidence read (operator-supplied)

Source: `.rust-queue/reports/native-check-summary.json` (attempt `0`, `kind =
measured_native_command`, `exit_code = 1`, `infrastructure_error = null`,
`engineering_acceptance = "pending"`). Native raw result:
`jobs/781/execution/check-0/native-result.json`, sha256
`80bb1dd491d9aa5c65e7fd38f68ab3c7757a502d251302c59b16390838f9c9a8`.

| # | kind | target (BUILD-derived) | exit | outcome |
| --- | --- | --- | --- | --- |
| 1 | query | `//score/mw/com/impl/methods:method_signature_element_ptr` | 0 | PASS |
| 2 | build | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` | 0 | PASS |
| 3 | build | `//score/mw/com/impl/plumbing/rust/test_support:test_helper_size_provider` | 0 | PASS |
| 4 | test | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_test_rs` | 0 | PASS (`1 test passes`) |
| 5 | docs | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_doc_test` | 0 | PASS |
| 6 | lint | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` | 1 | **FAIL (analysis)** |

Measured inventory: **6 recorded / 5 pass / 1 fail / 0 executed-by-agent**. The three
regression rows of `check-plan.json` (`sample_ptr_test_rs`, `sample_allocatee_ptr_test_rs`,
`method_signature_element_ptr_test`) were **not** part of this recorded run; they remain
**pending**, not failed and not passed. No counter is reset and no passing evidence is added.

## 2. Exact failing evidence (lint, check #6)

From the bounded tail of the `lint` check (`exit_code = 1`):

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

Notably the same command still printed:

```
INFO: Found 1 target...
Target //score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs up-to-date:
  bazel-bin/score/mw/com/impl/plumbing/rust/libmethod_in_arg_ptr_rs-375123505.rlib
```

## 3. Root-cause classification — infrastructure invocation, not source

`@@score_rust_policies+//clippy:linters.bzl%clippy_strict` is registered by the `clippy`
config in `quality/static_analysis/static_analysis.bazelrc`:

```
build:_lint   --extra_toolchains=@sarif_parser_toolchains//:all
build:clippy  --config=_lint
build:clippy  --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict
```

The recorded run reports `_lint` "expanded more than once", and consequently the same
`--aspects=...%clippy_strict` value is added twice, which Bazel rejects
(`aspect ... added more than once`) before the aspect analyses any target. This is a
command-line/configuration duplication in the lint invocation.

The repository's own native CI documents exactly this failure mode and the correct
invocation in `.github/workflows/_linter.yml`:

> `--bazel-flag=--config=${{ matrix.bazel-config }}` reuses the same aspect + toolchain
> configuration as `bazel test --config=${{ matrix.bazel-config }}` ... — the aspect is
> deliberately NOT also passed via `--aspect=` here, **since Bazel rejects the same aspect
> being registered twice.**

Conclusion:

- The lint failure is caused by the clippy aspect being applied **twice** through duplicated
  config/aspect expansion. It is an **invocation/infrastructure defect**, not a defect in the
  changed Rust source, BUILD rules, test, or the C++ helper.
- **No clippy diagnostic was produced.** The aspect never ran on the subject; therefore no
  measured source/test lint finding exists to correct.
- All subject-executing checks that did run (query, build ×2, Rust FFI size/align test, rustdoc)
  passed on the same subject hash.

`infrastructure_error` is recorded as `null` by the collector, but the recorded message above
is unambiguously an analysis-time aspect-registration error (`added more than once`) with the
matching `configs expanded more than once` warning — not a compiler/linter finding and not a
property of the patch. A failure of a build tool to accept its own duplicated configuration is
not corrected by editing product source.

## 4. Action taken in this correction

Per the correction rule "correct only a measured source/test defect" and "do not change code or
weaken checks" for an infrastructure-cause failure:

- **No source, BUILD, test, FFI-helper, `.bazelrc`, or CI file was modified.**
- The lint policy (`clippy_strict`), pins, licenses/SPDX headers and supported configs are
  unchanged; nothing was suppressed or excluded to force a pass.
- Prior failed evidence is retained unmodified in `native-check-summary.json` (attempt `0`).
- Counters are not reset: native attempt remains `0`; the recorded lint check remains **failed**;
  engineering acceptance remains **pending**.
- `check-plan.json` and the drafted implementation (`implementation.md`, source patch) are left
  as-is so the deterministic collector measures the same subject hash.

## 5. Correction requested of the deterministic collector (not agent authority)

Re-issue only the `lint` check for
`//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` such that the
`@score_rust_policies//clippy:linters.bzl%clippy_strict` aspect is registered **exactly once**
on the Linux config, mirroring native CI `.github/workflows/_linter.yml`:

- `aspect lint --bazel-flag=--config=<linux_x64> --bazel-flag=--config=clippy -- //<target>`,
  **or** equivalently `bazel build --config=<linux_x64> --config=clippy //<target>`,
- **without** additionally passing `--aspects=...%clippy_strict` and **without** repeating any
  `--config` that already expands the aspect (the current run expanded `_lint` twice).

This is a check-invocation correction only; it neither changes nor weakens the lint obligation.
No source edit is warranted before the aspect actually runs once on the subject.

## 6. Preserved state and next action

- Retained: `native-check-summary.json` (attempt 0, lint failed), `check-plan.json`,
  `implementation.md`, `review-packet.md`, `scope.md`, `_probe.txt`.
- This correction adds only `correction-1.md`.
- Engineering acceptance: **pending offline human decision**; unresolved design/ownership items
  from `implementation.md` §5 (FFI ownership/destruction of the move-only type, placement,
  `Send` contract, `MethodReturnTypePtr`, requirements/design impact) remain open and are **not**
  resolved here.
- Concrete next action: collector fixes the lint invocation (§5), re-measures the unchanged
  subject hash, and restores the three pending regression checks; then submit the patch and open
  decisions for offline review.

*No credentials are embedded. This correction records a blocker; it does not certify, qualify or
accept the native work product.*
