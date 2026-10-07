# scope.md — Issue #794 scope and reconciliation

## Scope and binding

- **Issue / repository**: eclipse-score/communication issue #794 —
  "Improvement: Remove bazel `tags = ["manual"]` from rust test targets".
  Issue body narrows the ask to: remove `tags = ["manual"]` for the *runtime* and
  *concept* test target of the `score_com` Rust library.
- **Task**: `.rust-queue/context/task.json` (issue 794, mode `implementation`).
- **Baseline commit**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
  (`fix(clang-tidy): justify external linkage in compiler warnings fixture (#1295)`).
- **Issue state / latest comment**: open; one comment by the issue author
  (`bharatGoswami8`) at `2026-10-05T06:20:13Z`, issue `updated_at`
  `2026-10-05T06:20:31Z`. The comment is *prose data*, not instruction authority;
  it is cross-checked below against the checked-out source.
- **Runtime / model**: Linux only; DeepSeek Flash only. No QNX work or execution.
- **Retrieval/binding date**: 2026-10-06 (environment date). Network/PR fetch is
  unavailable in this workspace (web tools and shell are outside the file-tool
  boundary), so no live PR activity beyond the supplied comment was retrieved.
- **Authority**: disposable workspace only. Shell, delegation, publishing and
  acceptance tools are blocked, so no native command was executed by the agent;
  deterministic command stages and raw evidence are outside agent authority.
  Permitted writes: this disposable copy, reports under `.rust-queue/reports/`.
- **Native IDs / requirements**: none were located in the touched build files, and
  the issue template leaves both "Affects Detailed Design" and
  "Requirements / Architecture are not affected" unchecked. Requirement/design
  identifiers therefore remain **unknown** (not fabricated).

## Sources inspected (baseline `381d43d`, working tree)

All Rust source packages in the repository were enumerated (`**/*.rs`, 30 files)
and every containing BUILD file was read. Files that define or gate the issue's
targets:

- `score/mw/com/rust/score_com_concept/BUILD` — `rust_test score_com_concept-test`,
  `rust_doc_test score_com_concept-macros-tests`, `rust_unit_test score_com_concept-macros-unit-tests`.
- `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD` — `rust_test
  com-api-runtime-lola-tests`, `rust_doc_test com-api-runtime-lola-doc-tests`.
- `score/mw/com/example/com-api-example/BUILD` — `rust_test
  com-api-example-tokio-integration-test`.
- `score/mw/com/rust/score_com_macros/BUILD` — `rust_doc_test score-com-macros-tests`.
- `score/mw/com/impl/plumbing/rust/BUILD` — `rust_unit_test sample_allocatee_ptr_test_rs`,
  `sample_ptr_test_rs`.
- `quality/unit_testing/unit_testing.bzl` — `rust_unit_test` macro semantics.
- `quality/integration_testing/integration_testing.bzl` — integration test macro.
- CI/config: `.github/workflows/_build_and_test_gcc15.yml`,
  `_thread_sanitizer.yml`, `_address_sanitizer.yml`, `_linter.yml`;
  `.bazelrc`; `quality/sanitizer/sanitizer.bazelrc`;
  `quality/static_analysis/static_analysis.bazelrc`; `MODULE.bazel`.

## Baseline reconciliation (key finding)

**The issue's requested removal is already present at the baseline source.**
No Rust test target in the issue's scope carries `tags = ["manual"]`:

| Target (BUILD label) | Rule | `tags = ["manual"]` at baseline | Other gating |
| --- | --- | --- | --- |
| `//score/mw/com/rust/score_com_concept:score_com_concept-test` | `rust_test` | **absent** | `target_compatible_with = ["@platforms//os:linux"]` |
| `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | `rust_test` | **absent** | `target_compatible_with = ["@platforms//os:linux"]` |
| `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | `rust_test` | **absent** | Linux + `select(any_sanitizer -> incompatible)` |
| `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | `rust_doc_test` | **present (intentional)** | Linux; documented `rust_doc_test` native-link limitation |
| `//score/mw/com/rust/score_com_macros:score-com-macros-tests` | `rust_doc_test` | absent | Linux |
| `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | `rust_doc_test` | absent | Linux |
| `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests` | `rust_unit_test` | forwarding target not manual; internal `_linux` target manual by macro design | — |

The author comment and the checked-out source agree: the runtime/concept test
targets are enabled, the example target is enabled but excluded under sanitizers,
and only the `score_com_concept` doc test remains `manual`. Therefore the issue's
premise ("remove the tag") is **already satisfied** by the selected source, and
making a source edit would be a no-op or a regression.

### Why the remaining `manual` tag must be preserved

`//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` is a
`rust_doc_test` whose `deps` transitively link C++ (`score_com ->
com-api-runtime-lola -> bridge_ffi_lola -> :registry_bridge_macro_cpp`). The
BUILD file documents that `rust_doc_test` inherits `crate_type="lib"`, causing
`_add_native_link_flags()` to skip CC native deps, which fails under LLVM's strict
LLD linker. Removing `manual` would expose a failing doc test to
`bazel test //...` in every CI job. This is out of scope for #794 (the author
comment classifies it as unrelated to the sanitizer work that motivated the
issue) and removing it would violate "do not suppress/relax to obtain
cleanliness".

### `rust_unit_test` macro `manual` tags are by design

`quality/unit_testing/unit_testing.bzl` creates `{name}_linux` with
`tags = tags + ["manual"]` and a *discoverable forwarding* `{name}` with
`tags = tags + ["unit"]`. The `_linux`/`_qnx` internal targets are intentionally
`manual`; only the forwarding target participates in `//...`. These are **not**
in scope and must not be changed.

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact | Changed artifact | Required check | Evidence | Gap / disposition |
| --- | --- | --- | --- | --- | --- |
| Remove `manual` from `score_com` runtime test target | CI wildcard discovery in `.github/workflows/_build_and_test_gcc15.yml` (`bazel test --config=ci //... --build_tests_only`) | none (already removed at `381d43d`) | `test //score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | pending collector | none |
| Remove `manual` from `score_com` concept test target | same CI wildcard | none (already removed) | `test //score/mw/com/rust/score_com_concept:score_com_concept-test` | pending collector | none |
| Keep sanitizer findings from being hidden | `_address_sanitizer.yml`, `_thread_sanitizer.yml`; `@score_cpp_policies//sanitizers/flags:any_sanitizer` | none (already present) | `test //score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` (SKIPPED under sanitizer configs) | pending collector | Tokio leak/race investigation explicitly deferred by author |
| Do not relax lint/link policy to obtain a green run | `quality/static_analysis/static_analysis.bazelrc` (`clippy_strict`) | none | lint of the two libraries via clippy config | pending collector | none |
| Requirement/design impact | issue template boxes unchecked | none | n/a | unknown native IDs | remains **unknown/pending** |

**Patch status**: empty. Candidate source == baseline for every affected path.
No file under `score/` was modified by this agent.

## Native target inventory and CI discovery

CI gating (source-backed, `.github/workflows/`):

- Host: `bazel test --config=ci //... --build_tests_only` and
  `bazel build --config=ci //...`.
- ASan/UBSan/LSan: `bazel test --config=ci --config=asan_ubsan_lsan //... --build_tests_only`.
- TSan: `bazel test --config=ci --config=tsan //... --build_tests_only`.
- Lint: `aspect lint --bazel-flag=--config=ci --bazel-flag=--config=clippy ... -- //...`.

`bazel test //...` skips `manual`-tagged targets. Because the runtime/concept
test targets are *not* `manual`, they are already covered by the wildcard. The
`score_com_concept-macros-tests` doc test remains `manual` and is intentionally
outside wildcard discovery (its failure would otherwise break every job). The
example target is non-`manual` (discovered) but reports SKIPPED under any
sanitizer config via `target_compatible_with`.

## Expected-check inventory (denominator)

In scope and expected to run at `linux_x64`: the two library builds, the runtime
and concept tests, the example test (default config), the two non-manual doc
tests, the concept macro unit test, and clippy lint of both libraries.

Explicitly excluded / not expected to run:
- `score_com_concept-macros-tests` — `manual` (documented LLD limitation).
- `com-api-example-tokio-integration-test` under any sanitizer config — SKIPPED
  (`any_sanitizer` incompatible).
- `sample_ptr_test_rs` / `sample_allocatee_ptr_test_rs` under TSan — constrained
  by `@score_cpp_policies//sanitizers/constraints:no_tsan` (Ticket-246891).
- Internal `rust_unit_test` `_linux`/`_qnx` targets — `manual` by macro design.

## Pending, unresolved and carried items

- **Pending offline acceptance**: whether the Tokio multi-thread runtime leak
  (LSan) and `<String as Clone>::clone` race (TSan) in
  `com-api-example-tokio-integration-test` can be fixed/suppressed so the
  sanitizer `target_compatible_with` restriction can be removed. This is an
  explicit follow-up in the author comment, is not part of #794's acceptance, and
  is not claimed as resolved here.
- **Missing evidence preserved as missing**:
  `.rust-queue/reports/native-check-summary.json` does not exist in this
  workspace; no native check results were produced by the agent and none are
  fabricated.
- **Unknown native IDs**: requirement/design/verification identifiers for the
  affected build rules were not discoverable from the selected sources and remain
  unknown.
- **Certification/acceptance**: technical completion is separate from native
  engineering acceptance. This agent recommends; authorized humans decide.

## Manifest

No source files were changed, so there is no baseline-to-patched source digest to
bind. File-level SHA-256 digests of the inspected files are **not computable**
within the file-tool boundary (no shell/hash tooling), so digest values remain
explicitly unknown; the binding is by exact repository-relative path at baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e`.

Report artifacts produced by this agent:
- `.rust-queue/reports/scope.md` (this file)
- `.rust-queue/reports/check-plan.json`

## Concrete next action

Run the `linux_x64` checks in `.rust-queue/reports/check-plan.json` in the bound
environment and record raw evidence. Expected result: the two issue-scope tests
and the two library builds pass; the example test is SKIPPED only under sanitizer
configs; `score_com_concept-macros-tests` remains excluded by `manual`. No source
patch is required for #794 at baseline `381d43d`.
