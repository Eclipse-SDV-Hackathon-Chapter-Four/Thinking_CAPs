# Correction 3 — issue #781 "Implementation of MethodInArgPtr in rust side"

Issue: `eclipse-score/communication` #781 (label `rust-api`, state `open`, 0 comments)
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `implementation` · Platform: Linux (`linux_x64`) only · No QNX · Model: DeepSeek Flash
Correction counter: **3 of at most 3** (this file, final) · Prior failed native attempts retained: **0, 1 and 2**
Measured subject: workspace patch, `measured_subject_hashes_sha256 =
29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45`

Status: **blocker sustained (final correction) — no source/test change, no check weakened.**
The latest bounded native result (attempt `2`) fails only on the `lint` check, and that failure is the
same invocation-level Bazel aspect-registration duplication already recorded in `correction-1.md`
(attempt `0`) and `correction-2.md` (attempt `1`). It is **not** a measured source or test defect: the
aspect never analysed the subject, so no clippy diagnostic exists to correct. No measured source/test
defect is present in any attempt, so there is nothing this correction may truthfully edit.
Engineering acceptance remains a **pending offline human decision**.

---

## 1. Latest bounded native evidence read (operator-supplied)

Source: `.rust-queue/reports/native-check-summary.json` (attempt `2`, `kind =
measured_native_command`, `exit_code = 1`, `infrastructure_error = null`,
`engineering_acceptance = "pending"`). Native raw result:
`jobs/781/execution/check-2/native-result.json`, sha256
`f213936ca9e519cb7ef75e61486c549fa909e129669c39a4631fd7bb066c5b31`.

| # | kind | target (BUILD-derived) | exit | outcome |
| --- | --- | --- | --- | --- |
| 1 | query | `//score/mw/com/impl/methods:method_signature_element_ptr` | 0 | PASS |
| 2 | build | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` | 0 | PASS |
| 3 | build | `//score/mw/com/impl/plumbing/rust/test_support:test_helper_size_provider` | 0 | PASS |
| 4 | test | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_test_rs` | 0 | PASS (`1 test passes`) |
| 5 | docs | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_doc_test` | 0 | PASS |
| 6 | lint | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` | 1 | **FAIL (analysis)** |

Measured inventory: **6 recorded / 5 pass / 1 fail / 0 executed-by-agent**. The three regression rows
of `check-plan.json` (`sample_ptr_test_rs`, `sample_allocatee_ptr_test_rs`,
`method_signature_element_ptr_test`) were again **not** part of this recorded run; they remain
**pending**, not failed and not passed. No counter is reset and no passing evidence is added.

### 1.1 Three retained attempts compared (history preserved, not overwritten)

| Field | attempt 0 | attempt 1 | attempt 2 |
| --- | --- | --- | --- |
| `native_result` sha256 | `80bb1dd491d9aa5c65e7fd38f68ab3c7757a502d251302c59b16390838f9c9a8` | `4a7c41e23bf2483404bd5e12d825c9b31d57f7b3a0bf08684f9644051bed2713` | `f213936ca9e519cb7ef75e61486c549fa909e129669c39a4631fd7bb066c5b31` |
| `measured_subject_hashes_sha256` | `29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45` | `29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45` | `29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45` |
| passing checks | query, build ×2, test, docs | query, build ×2, test, docs | query, build ×2, test, docs |
| failing check | lint (aspect registration) | lint (aspect registration) | lint (aspect registration) |
| `infrastructure_error` | `null` | `null` | `null` |

The measured subject hash is **byte-identical across all three attempts** (no source/test edit occurred
between them), and the failing `lint` tail is textually the same error each time. Three independent
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

Every check — including the `query` of the existing C++ target
`//score/mw/com/impl/methods:method_signature_element_ptr` — also carries:

```
WARNING: Duplicate rc file: .../workspaces/781/quality/static_analysis/static_analysis.bazelrc is read
multiple times, it is a standard rc file location but must have been unnecessarily imported earlier.
```

## 3. Root-cause classification — invocation, not source/test (sustained)

`@@score_rust_policies+//clippy:linters.bzl%clippy_strict` is registered once by the `clippy` config
in `quality/static_analysis/static_analysis.bazelrc` (re-read this correction, unchanged):

```
build:_lint  --extra_toolchains=@sarif_parser_toolchains//:all
build:clippy --config=_lint
build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict
```

and is imported once by the workspace `.bazelrc`:

```
import %workspace%/quality/static_analysis/static_analysis.bazelrc
```

The recorded run reports that same rc file is "read multiple times" and that `_lint` was "expanded
more than once"; consequently the single `--aspects=...%clippy_strict` flag from `build:clippy`
reaches the analysis phase twice, which Bazel rejects (`aspect ... added more than once`) before the
aspect analyses any target. The duplication is a command-line/rc-import condition. The repository
patch under test touches only Rust source, the plumbing `BUILD` and the `test_support` C++ helper —
none of which can register a command-line aspect twice, and the same duplicate-rc warning also appears
on the untouched C++ `query` check. `.bazelrc`, `.bazelrc.ai_checker` and
`quality/static_analysis/static_analysis.bazelrc` were re-read and are **not** modified by this patch.

The repository's own native CI documents the correct invocation and the exact failure mode to avoid in
`.github/workflows/_linter.yml` (cited in `correction-1.md` §3): the aspect is deliberately not passed
via a separate `--aspect=` in addition to `--config=clippy`, because Bazel rejects the same aspect
being registered twice.

Conclusion:

- The lint failure is caused by the clippy aspect being applied **twice** through duplicated
  rc/config expansion. It is an **invocation/platform defect**, not a defect in the changed Rust
  source, BUILD rules, test, or C++ helper.
- **No clippy diagnostic was produced** in any of the three attempts. The aspect never ran on the
  subject; therefore no measured source/test lint finding exists to correct.
- Every subject-executing check that did run (query, build ×2, Rust FFI size/align test, rustdoc)
  passed on the same, unchanged subject hash in all three attempts.

### 3.1 On `infrastructure_error: null`

The collector records `infrastructure_error = null`. That field is the collector's own
crash/harness-unavailability channel; a `null` value here does **not** convert an analysis-time aspect
registration failure into a source defect, and the operator instruction's blocker condition is not
read as being bypassed by the literal field value. The relevant facts are unchanged and dispositive:

1. no clippy diagnostic was ever emitted against the subject, and
2. all subject-executing checks pass on a byte-identical subject hash across three attempts, and
3. the failing tail is a Bazel *analysis/config* error (`configs expanded more than once`,
   `aspect ... added more than once`), reproducible on an unchanged subject.

The operator rule is "**Correct only a measured source/test defect**". There is no measured source/test
defect in the supplied evidence; consequently there is nothing truthful to edit, and no check may be
dropped or weakened to force a green result. The failure is recorded as the blocker it is.

## 4. Action taken in this correction

Per the correction rule "correct only a measured source/test defect" and "do not change code or weaken
checks" when the evidence instead shows a non-source (invocation) cause:

- **No source, BUILD, test, FFI-helper, `.bazelrc`, CI, or BUILD-derived label was modified.**
- The lint policy (`clippy_strict`), toolchain/pin files, licenses/SPDX headers and supported configs
  are unchanged; nothing was suppressed or excluded to force a pass.
- The lint check was **not** dropped, retargeted or downgraded in `check-plan.json`; an obligation is
  not removed to make a run look green. No passing evidence is fabricated.
- Prior failed evidence is retained unmodified in `native-check-summary.json` (attempts `0`, `1` and
  `2`, each with the lint check failed) and in `correction-1.md` / `correction-2.md`.
- Counters are not reset: native attempt count is unchanged at `2`; the recorded lint check remains
  **failed**; engineering acceptance remains **pending**.
- `check-plan.json`, `implementation.md`, `review-packet.md`, `scope.md`, `_probe.txt`,
  `correction-1.md` and `correction-2.md` are left as-is so the deterministic collector measures the
  same subject hash. This correction adds only `correction-3.md`.

## 5. Correction requested of the deterministic collector (not agent authority)

Command stages, raw evidence and check invocation are outside agent authority. The deterministic
collector is asked to re-issue only the `lint` check for
`//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` such that the
`@score_rust_policies//clippy:linters.bzl%clippy_strict` aspect is registered **exactly once** on the
Linux config, mirroring native CI `.github/workflows/_linter.yml`:

- `aspect lint --bazel-flag=--config=<linux_x64> --bazel-flag=--config=clippy -- //<target>`, **or**
  equivalently `bazel build --config=<linux_x64> --config=clippy //<target>`,
- **without** additionally passing `--aspects=...%clippy_strict` and **without** reading
  `quality/static_analysis/static_analysis.bazelrc` twice (the run imported it more than once and
  expanded `_lint` more than once in all three attempts).

This is a check-invocation correction only; it neither changes nor weakens the lint obligation. No
source edit is warranted, or truthful, before the aspect actually runs once on the subject. The three
pending regression rows of `check-plan.json` should also be restored to the recorded run so the
regression obligations are measured rather than left pending.

## 6. Preserved state and next action

- Retained: `native-check-summary.json` (attempt `2`, lint failed), `check-plan.json`,
  `implementation.md`, `review-packet.md`, `scope.md`, `correction-1.md`, `correction-2.md`,
  `_probe.txt`.
- Engineering acceptance: **pending offline human decision**; unresolved design/ownership items from
  `implementation.md` §5 (FFI ownership/destruction of the move-only type, placement, `Send` contract,
  `MethodReturnTypePtr`, requirements/design impact) remain open and are **not** resolved here.
- Concrete next action: the collector fixes the lint invocation (§5) and restores the three pending
  regression checks; only then can a genuine clippy result exist. Afterwards submit the patch and the
  open decisions for offline review. This is the final permitted correction (`3 of 3`); the blocker is
  not resolvable from source within the agent's authority.

*No credentials are embedded. This correction records a blocker; it does not certify, qualify or
accept the native work product.*
