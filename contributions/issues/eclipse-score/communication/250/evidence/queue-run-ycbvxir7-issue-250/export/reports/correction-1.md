# Correction 1 — issue #250 `FindServiceSpecifier::Any`

Baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Linux only, DeepSeek Flash only.
Correction 1 of at most 3. No repository source change is made in this correction; the
measured result and the issue's own prerequisite are recorded as blockers per the correction
rules ("if evidence says infrastructure_unavailable or a design/backend prerequisite is
missing, do not change code or weaken checks; write the blocker").

## 1. Latest bounded native result re-read (operator-supplied)

Source: `.rust-queue/reports/native-check-summary.json` (`attempt: 0`),
`measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`,
`native_result.sha256 = ca749d2a5794b7dcfd17d42ac72b4399d75207688867bcf4eada49ac6cc9390a`.

| # | kind | targets (summary) | exit | outcome |
| --- | --- | --- | --- | --- |
| 0 | build | `score_com_concept`, `bridge_ffi_rs`, `registry_bridge_macro_cpp` | 0 | PASSED |
| 1 | build | `com-api-runtime-lola`, `com-api-runtime-mock`, `score_com`, `score_com_mock` | 0 | PASSED |
| 2 | test | `score_com_concept-test`, `score_com_concept-macros-unit-tests` | 0 | PASSED |
| 3 | test | `com-api-runtime-lola-tests` | 0 | PASSED |
| 4 | test | `com-api-example-tokio-integration-test` | 0 | PASSED |
| 5 | test | `test_com_api_sync`, `test_com_api_async` | 0 | PASSED |
| 6 | test | `test_find_any_semantics` | 0 | PASSED |
| 7 | build | `find_any_semantics:service`, `:client`, `:test_datatype` | 0 | PASSED |
| 8 | build | `basic_rust_api` generated/binary targets | 0 | PASSED |
| 9 | docs | `com-api-runtime-lola-doc-tests`, `score_com_concept-macros-tests` | 0 | PASSED |
| 10 | lint | `score_com_concept`, `com-api-runtime-lola`, `bridge_ffi_rs` | 1 | FAILED (infrastructure) |

Every build, test and docs check passed with the (no-op) draft subject. The single failing
check is the `lint` check, and its bounded tail shows the failure is not a lint finding in any
Rust source:

```
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
...
ERROR: command succeeded, but not all targets were analyzed
INFO: 1 process: 302 action cache hit, 1 internal.
ERROR: Build did NOT complete successfully
```

The same bounded tail also shows repeated-configuration warnings:
`Duplicate rc file: .../quality/static_analysis/static_analysis.bazelrc is read multiple times`
and `The following configs were expanded more than once: [_lint]`.

## 2. Diagnosis — infrastructure, not a source/test defect

The failure occurs during Bazel **analysis**, before any lint action runs (`1 process: 302
action cache hit`). It is caused by the `clippy_strict` aspect being registered/applied more
than once by the measurement command's own configuration (`--config=_lint` expanded more than
once, duplicate rc). It is not attributable to any file under version control:

- No `BUILD`, `.bazelrc`, `MODULE.bazel` or Rust source is implicated by the error text.
- The same targets pass when built (checks 0, 1, 2, 3, 5), so the aspect duplication is
  configuration-level, not target-level.
- Command stages and raw evidence are outside agent authority; the invocation that produced
  this error cannot be changed from this workspace.

There is therefore **no measured source/test defect to correct**. Weakening or deleting the
lint check (e.g. dropping it from `check-plan.json`) would be a prohibited weakening of a
check, so the lint entry is retained unchanged.

## 3. Prerequisite blocker for the issue itself (unchanged)

Independent of the lint infrastructure error, issue #250 remains blocked on an absent
design/backend prerequisite, exactly as assessed in `blocker-design-report.md` and
`implementation.md` and confirmed by the issue comments
(`.rust-queue/context/comments.json`, both CONTRIBUTOR):

- Comment 1: LoLa SD supports any-semantics via `flag_file_crawler.cpp`.
- Comment 2: any-semantics exists for `InstanceIdentifier`, but **not** for
  `InstanceSpecifier`; obtaining "all available services on the system" is the requested
  Rust API goal.

At this baseline the Rust FFI exposes only `InstanceSpecifier` overloads
(`bridge_ffi.rs:239-259`, `registry_bridge_macro.cpp:395-417, 507-525`) and no FFI returns a
discovered instance's identity; `Runtime::find_service` panics on `Any`
(`com-api-runtime-lola/runtime.rs:40-52`) and `get_instance_specifier` panics
(`consumer.rs:1070-1078`). A Rust-only patch cannot satisfy the acceptance criteria. This is a
human/engineering-decision blocker (semantics of `Any`; FFI/backend extension;
`ConsumerDescriptor` contract change), not a model-correctable source defect.

## 4. Actions taken in this correction

- Created `.rust-queue/reports/correction-1.md` (this file).
- No source, `BUILD`, design, license, pin, lint-policy, native-ID or published-status file
  was changed. No QNX task or configuration was touched.
- `check-plan.json` lint check retained unmodified (no check weakened).
- Prior failed/absent evidence retained: `native-check-summary.json` still records
  `passed: false` / `exit_code: 1` at `attempt: 0`; the earlier reports' statement that no
  trusted collector evidence existed at draft time remains as history. Counters were not reset
  and no passing evidence was fabricated.

## 5. Status

- Technical assessment: complete; no source correction is applicable.
- Measured subject: 10/11 checks passed; 1/11 (`lint`) blocked by duplicate-aspect
  infrastructure, not by the change.
- Engineering acceptance: **pending** — still gated on the three human decisions listed in
  `blocker-design-report.md` §4 and `review-packet.md` ("Offline decisions").
- Next action: (a) an operator-side fix to the lint measurement invocation (remove the
  duplicate `_lint` config / duplicate rc import) so the lint check can be re-measured; and
  (b) the pending human decisions before any `FindServiceSpecifier::Any` implementation.
