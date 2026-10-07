# implementation.md — Issue #794

"Improvement: Remove bazel `tags = ["manual"]` from rust test targets"

- **Repository / issue**: eclipse-score/communication #794
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- **Runtime / model**: Linux only; DeepSeek Flash only. No QNX task or execution.
- **Authority**: disposable workspace only. Shell, delegation, publishing and
  acceptance tools are blocked; the agent executed **no** native command.
  Deterministic command stages and raw evidence remain outside agent authority.
- **Change decision**: **premise already implemented at baseline — no source
  change warranted and none made.**

## 1. Actual changed paths

**None.**

No file was created, deleted or modified under `score/`, `quality/` or any
native build path by this agent. The candidate source equals the baseline for
every path in the issue's change surface. Only this report file
(`.rust-queue/reports/implementation.md`) was produced; the pre-existing
`.rust-queue/reports/scope.md` and `.rust-queue/reports/check-plan.json` are
unchanged.

Per the task instruction, for an already-implemented premise the correct outcome
is to document the remaining gaps rather than duplicate code. There is no
source diff to bind.

## 2. Why no edit is warranted (issue acceptance vs. baseline source)

The issue narrows the ask to removing `tags = ["manual"]` for the **runtime** and
**concept** test target of the `score_com` Rust library. Both are already
non-`manual` at the baseline, so removing the tag would be a no-op; any edit
would be churn or regression.

| Target (BUILD label) | Rule | `tags = ["manual"]` | Evidence (baseline file:lines) |
| --- | --- | --- | --- |
| `//score/mw/com/rust/score_com_concept:score_com_concept-test` | `rust_test` | **absent** | `score/mw/com/rust/score_com_concept/BUILD:35-44` |
| `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | `rust_test` | **absent** | `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD:36-46` |
| `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | `rust_test` | **absent** (gated only under sanitizers) | `score/mw/com/example/com-api-example/BUILD:52-74` |
| `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | `rust_doc_test` | **present, intentional** | `score/mw/com/rust/score_com_concept/BUILD:46-56` (tag at `:54`) |
| `//score/mw/com/rust/score_com_macros:score-com-macros-tests` | `rust_doc_test` | **absent** | `score/mw/com/rust/score_com_macros/BUILD:29-33` |
| `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | `rust_doc_test` | **absent** | `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD:48-53` |
| `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests` | `rust_unit_test` | forwarding target non-manual | `score/mw/com/rust/score_com_concept/BUILD:58-63`; macro `quality/unit_testing/unit_testing.bzl:149-195` |
| `//score/mw/com/impl/plumbing/rust:sample_ptr_test_rs`, `...:sample_allocatee_ptr_test_rs` | `rust_unit_test` | forwarding targets non-manual | `score/mw/com/impl/plumbing/rust/BUILD:49-74` |

The two issue-scope targets keep `target_compatible_with = ["@platforms//os:linux"]`
(concept `BUILD:39`, runtime `BUILD:40`) — a platform constraint, not a `manual`
tag, and required until QNX Rust-test support lands (issue #1278).

This baseline state matches the issue author's data comment of 2026-10-05
(`.rust-queue/context/comments.json`): runtime and concept tests enabled, the
example test enabled but sanitizer-incompatible, and only the concept doc test
still `manual`.

## 3. Wildcard CI discovery verification (source-backed)

`manual` targets are skipped by `//...`. Because the runtime/concept tests no
longer carry `manual`, they are covered by the wildcard in every relevant job:

- Host build/test: `.github/workflows/_build_and_test_gcc15.yml:49` (`bazel
  build --config=ci //...`) and `:54` (`bazel test --config=ci //
  ... --build_tests_only`).
- ASan/UBSan/LSan: `.github/workflows/_address_sanitizer.yml:50`.
- TSan: `.github/workflows/_thread_sanitizer.yml:50`.
- Lint: `.github/workflows/_linter.yml:115-125` (`aspect lint ... -- //...`,
  clippy matrix entry).

The example target is non-`manual`, so it is discovered by all wildcards, but
its `target_compatible_with` `select` on
`@score_cpp_policies//sanitizers/flags:any_sanitizer`
(`score/mw/com/example/com-api-example/BUILD:64-67`) makes it report SKIPPED
under ASan/UBSan/LSan and TSan, exactly as documented in the BUILD comment
(`:57-63`) and the author comment.

The one intentionally-manual Rust test remains `score_com_concept-macros-tests`
(`score_com_concept/BUILD:54`); the BUILD comment (`:49-53`) documents that
`rust_doc_test` inherits `crate_type="lib"`, so `_add_native_link_flags()` skips
the linked C++ deps and the doc test fails under LLVM's strict LLD. Removing it
would inject a broken test into `bazel test //...` in every CI job and is
outside #794's scope. The task's "do not remove exclusions to create
cleanliness" rule applies here.

`rust_unit_test` macro internals also keep `manual` by design:
`quality/unit_testing/unit_testing.bzl:170` sets `tags = tags + ["manual"]` on
the internal `{name}_linux` target, while the discoverable forwarding target at
`:194` gets `tags = tags + ["unit"]` and no `manual`. These internal targets are
not in scope and were not changed.

## 4. Regression / consumer cases

No regression or consumer case is owed: no build rule, tag, dependency, source
file or public API changed, so there is no failure or compatibility risk to
capture. Adding a test that merely re-asserts the already-correct tagging would
duplicate implementation and is explicitly discouraged. The existing
verification obligations (wildcard CI discovery plus the explicit native targets
in `check-plan.json`) already exercise the consumers.

## 5. Unresolved concerns / gaps (preserved, not resolved)

1. **Pending offline acceptance — Tokio sanitizer findings.** The
   now-enabled `com-api-example-tokio-integration-test` is excluded from
   sanitizer configs via `target_compatible_with` (`BUILD:64-67`) because:
   - `--config=asan_ubsan_lsan`: LeakSanitizer reports leaks originating from
     `tokio::runtime::scheduler::multi_thread::MultiThread::new` / worker
     startup;
   - `--config=tsan_ubsan`: data race in `<String as Clone>::clone` between the
     test thread and a `tokio-rt-worker` thread.
   Neither stack frame is in COM code. Removing the sanitizer restriction
   requires a human decision (fix or targeted suppression) and is an explicit
   follow-up in the author comment, not part of #794 acceptance. Left untouched.
2. **`score_com_concept-macros-tests` remains `manual`.** Intentional, documented
   `rust_doc_test`/LLD native-link limitation (`BUILD:49-54`). Out of scope for
   #794; retained.
3. **Unknown native IDs.** Requirement / design / verification identifiers for
   the affected build rules were not discoverable from the selected sources, and
   the issue template leaves both "Affects Detailed Design" and "Requirements /
   Architecture are not affected" unchecked. They remain **unknown** (not
   fabricated).
4. **Missing native evidence preserved as missing.**
   `.rust-queue/reports/native-check-summary.json` does not exist in this
   workspace. No native check was run or observed by the agent; nothing is
   fabricated and no result is claimed.
5. **Technical vs. engineering completion.** This agent recommends; deterministic
   tools measure; authorized humans decide. Native work products are not marked
   qualified/released/accepted here, and the Tokio sanitizer investigation is not
   closed.

## 6. Check plan and next action

The conformant Linux (`config: linux_x64`) check plan is already recorded in
`.rust-queue/reports/check-plan.json` using BUILD-derived labels (no QNX). It
covers both issue-scope tests
(`//score/mw/com/rust/score_com_concept:score_com_concept-test`,
`//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`),
the library builds, the enabled-but-sanitizer-gated example test, the
non-manual doc tests, the concept macro unit test, and clippy lint of both
libraries.

**Concrete next action** (bound environment, outside agent authority): run the
checks in `check-plan.json` and record raw evidence into
`.rust-queue/reports/native-check-summary.json`. Expected result at baseline
`381d43d`: the two issue-scope tests and the two library builds pass; the
example test is SKIPPED only under sanitizer configs;
`score_com_concept-macros-tests` remains excluded by `manual`. No source patch
is required for #794.

## 7. Manifest

- Source diff: none (candidate source == baseline for every affected path).
- Report artifacts produced by this agent:
  - `.rust-queue/reports/implementation.md` (this file)
- Pre-existing, unchanged: `.rust-queue/reports/scope.md`,
  `.rust-queue/reports/check-plan.json`.
- File digests are **not computable** within the file-tool boundary (no
  shell/hash tooling); binding is by exact repository-relative path and baseline
  commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
