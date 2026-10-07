# External-crate dependency and design assessment — eclipse-score/communication #173

Issue: *Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate)*
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Activity: assessment. No source, dependency, lock or policy change is made or authorized.
Engineering acceptance and any retain/replace/internal decision remain **pending offline
human decision**.

This document consolidates the dependency/design assessment for the crates named by the
prompt: `pastey`, `thiserror` and `futures`. It complements `scope.md` (task binding,
premise reconciliation, macro surface) and `check-plan.json` (native check inventory).

## 1. Issue premise

The issue states the COM-API "currently utilizes the external **paste** crate ...".
At the pinned baseline this premise is **outdated**: the interface macros already use
`pastey`, not `paste`.

- `score/mw/com/rust/score_com_concept/interface_macros.rs` — `interface_common!`,
  `interface_consumer!`, `interface_producer!` expand inside
  `score_com::pastey::paste! { ... }` (lines 134, 146, 163, 195).
- `score/mw/com/rust/score_com_concept/BUILD:22` — `proc_macro_deps` includes
  `@score_communication_crate_index//:pastey`.
- `score/mw/com/rust/score_com_concept/lib.rs:29-30` — `#[doc(hidden)] pub use pastey;`.
- `score/mw/com/rust/score_com.rs:144-146` — `pub use score_com_concept::pastey;` with a
  comment citing this issue.

So the paste→pastey migration referenced by the issue is already implemented. The
remaining substance is the **policy for uncertified external crates**, now tracked
outside this repository by `score-crates#42` (linked in the single issue comment,
`comments.json`). That issue and its sub-issues (`total: 3, completed: 0`) are not
reachable in this session.

## 2. Resolved crate inventory

Resolution path: `MODULE.bazel` declares
`bazel_dep(name = "score_crates", version = "0.0.11", repo_name = "score_communication_crate_index")`
(line 41); the generated crate-index specs are recorded in `MODULE.bazel.lock`.
The digests below are **carried** from the `scope.md` §3 extraction of that lock; the
lock content could not be re-read in this session (content search is bounded to
filenames/counts here). They are baseline-carried evidence, not a fresh resolver run.

| Crate | Version | Kind / role | Edition | Declared features | Archive source | sha256 (index) |
| --- | --- | --- | --- | --- | --- | --- |
| `pastey` | `0.2.3` | proc-macro, no deps; **host** | 2018 | (none) | `https://static.crates.io/crates/pastey/0.2.3/download` | `2ee67f1008b1ba2321834326597b8e186293b049a023cdef258527550b9935b4` |
| `thiserror` | `2.0.21` | lib; pulls proc-macro `thiserror-impl 2.0.21`; **target** | 2021 | `default`, `std` | `.../thiserror/2.0.21/download` | `09e52cb86a36cede5cb101bf8908837b3e4c6e5e59fe7fd85c23fb56200d189e` |
| `thiserror-impl` | `2.0.21` | proc-macro; **host** | 2021 | — | `.../thiserror-impl/2.0.21/download` | `fe5197923287db20a58125f0bc85c062f7f2c892de97b18c356f9efb14b28524` |
| `futures` | `0.3.34` | lib facade; **target** (+ executor sub-crates) | 2018 | `alloc`, `async-await`, `default`, `executor`, `futures-executor`, `std` | `.../futures/0.3.34/download` | `9a31d2a3fbaaeb2af2368bbdd904aa8e812d3c04a1ee10d3171f52d556e5d0a3` |
| `paste` | `1.0.15` | proc-macro + build script; **unused** | 2018 | (none) | `.../paste/1.0.15/download` | `57c0d7b74b563b49d38dae00a0c37d4d6de9b432382b2892f0574ddcae73fd0a` |
| `quote` | `1.0.47` | proc-macro support (host) | — | — | index | — |
| `syn` | `2.0.119` / `3.0.6` | proc-macro support (host) | — | — | index | — |

Direct COM-API consumers (BUILD-derived, verified):

- `score_com_concept` — `proc_macro_deps: pastey`; `deps: futures, thiserror`
  (`score/mw/com/rust/score_com_concept/BUILD:20-32`).
- `score_com_macros` — `deps: quote, syn`
  (`score/mw/com/rust/score_com_macros/BUILD:23-26`).
- `com-api-example-lib` / `com-api-example` — `clap`, `futures`
  (`score/mw/com/example/com-api-example/BUILD:21-49`).
- async packages add `futures`; `com-api-example-tokio-integration-test` also `tokio`
  (`score/mw/com/test/basic_rust_api/consumer_async_apis/BUILD:39`;
  `.../com-api-example/BUILD:68-73`).

`paste 1.0.15` is present in the index but is **not referenced by any inspected
COM-API BUILD file**; an index entry is not evidence of usage.

## 3. Per-crate assessment

### 3.1 `pastey 0.2.3` (the issue's crate, post-migration)

- **Observed usage.** Only the suffix form `[<ident Suffix>]` inside `paste!`, for four
  generated type-name suffixes: `[<$id Interface>]`, `[<$id Consumer>]`,
  `[<$id Producer>]`, `[<$id OfferedProducer>]`. No prefix composition, case
  conversion, raw identifiers or multi-token schemes are used.
- **Generator role / trust.** Host-side proc-macro executed at compile time. It can
  emit identifiers/items into the target code; a compromised macro could inject code
  that still compiles. No native tool trust/qualification classification for `pastey`
  exists locally (unknown).
- **Failure modes.** Wrong suffix/hygiene → generated type names absent/renamed →
  downstream compilation and the in-crate `validation_tests` fail. Semantically wrong
  `INTERFACE_ID`/event wiring can compile and requires test/runtime detection. See
  `scope.md` §5.
- **Provenance/license/maintenance.** Version, archive URL and index digest are known.
  Source archive, license/notice texts and advisories were **not** inspected (network
  blocked, nothing vendored). License and maintenance status are **unknown**.

### 3.2 `thiserror 2.0.21` (+ `thiserror-impl 2.0.21`)

- **Observed usage.** `use thiserror::Error;` and `#[derive(..., Error)]` on the
  `ServiceFailedReason`, `ProducerFailedReason`, `ConsumerFailedReason` enums in
  `score/mw/com/rust/score_com_concept/error.rs` (lines 19-53).
- **Roles.** `thiserror` is a target library; `thiserror-impl` is a host proc-macro
  that generates the `Display`/`Error` impls. Both compile in the Rust build path.
- **Failure modes.** A wrong derive expansion yields missing/incorrect `Display`
  strings or `Error::source`; local `#[error("...")]` text is a user-visible contract
  and is only checked where tests assert it. Build-time trust applies to
  `thiserror-impl` as a host proc-macro.
- **Provenance/license/maintenance.** Same limitation as `pastey`: version/URL/digest
  known, license and advisories **not** verified.

### 3.3 `futures 0.3.34`

- **Observed usage.** `score_com_concept` `deps` and async consumer/example packages
  (BUILD references above). It is a target library facade; the enabled features
  (`default` = `std` + `async-await` + `executor` + `alloc` …) are carried from the
  index entry, not recomputed by a resolver run in this session.
- **Failure modes.** Feature unification or version skew could change runtime
  behavior of async consumers without failing the macro surface; detection relies on
  the async integration/consumer targets and the example tests.
- **Provenance/license/maintenance.** Unknown, as above.

### 3.4 `paste 1.0.15` (legacy name in the issue)

Present in the crate index but unreferenced by COM-API. Replacing `pastey` with `paste`
would restore the issue's wording but contradicts the observed migration; it is not
recommended without new evidence.

## 4. Native obligations and existing work products

- Process obligations (`references/dependency-and-macros.md`, `native-verification.md`):
  resolved dependency inventory; host/target role separation; macro invocation
  coverage; generated-API compatibility via real downstream compilation; docs/lint.
- Repository CI obligations (`CI.md`): build + unit tests (x86-64 linux); integration
  tests (x86-64 linux); Rust linting (`--config=clippy`, aspect
  `@score_rust_policies//clippy:linters.bzl%clippy_strict`, defined in
  `quality/static_analysis/static_analysis.bazelrc:27-30`); Rust formatting
  (`//:format_test`, `rust = //tools/lint:rustfmt_with_config`); API checks; docs.
- Native external-dependency tool: `//quality/dependency_compatibility_checker`
  builds a green/orange/red matrix for **Bazel module** versions. Its
  `config.yaml` covers `bazel`, `rules_cc`, `rules_python`, `rules_rust` only and
  does **not** cover Rust crates (`pastey`/`thiserror`/`futures`) — a coverage gap.
- Native tool-management work products referenced by the skill at process pin
  `98d1d5f42dad412a09a888ea25e59c62fa6371ce`: `wp__tlm_plan` and
  `wp__tool_verification_report` (version 1, status `valid`) are **type definitions,
  not instances**. No instance files exist in this workspace; applicability to the
  three crates is **unknown**, and no confidence/qualification decision is asserted.
- No Rust API-surface lock exists. The only committed API-surface lock is the C++
  clang-AST check `//score/mw/com:api_surface_test` (`quality/api_surface/README.md`),
  which does not cover the macro-generated Rust API.

## 5. Options comparison (proposal only)

| Option | Compatibility / build impact | Provenance / license / maintenance | Qualification & verification effort | Notes |
| --- | --- | --- | --- | --- |
| **Retain `pastey 0.2.3`** | none; already compiled and re-exported | version/digest known; license, maintenance, advisories unknown | reuse existing native tests/doctests + downstream targets; add dependency/tool justification | lowest churn; matches baseline; blocked on `score-crates#42` and provenance review |
| **Replace with `paste 1.0.15`** | BUILD + `lib.rs`/`score_com.rs` re-export edits | index entry exists; upstream suitability unestablished | full macro positive/negative + downstream re-verification | contradicts observed migration; not recommended without evidence |
| **Integrate into repo** (issue option 1) | vendor/import macro logic; new maintained in-repo code | removes one external proc-macro provider, moves license/notice/maintenance burden in-tree | design/maintenance ownership + full verification | maps to issue option 1; no authority here |
| **Manual implementation** (issue option 2) | reimplement only the four suffix operations; touches all three `interface_*` macros | removes `pastey`; internal code still carries qualification obligations | reproduce hygiene/diagnostics + all macro tests/doctests + downstream | maps to issue option 2; feasible in principle, higher maintenance |

Candidate recommendation (reviewable, **not** accepted): retain `pastey 0.2.3` at this
baseline and route the integrate-vs-manual policy through `score-crates#42` and the
native tool/qualification work products, because the baseline already depends on
`pastey`, only a narrow and well-covered suffix capability is exercised, and this task
holds no authority to change dependencies or accept a qualification. All options remain
open.

## 6. Gaps and unknowns (preserved)

- `.rust-queue/reports/native-check-summary.json` is **missing** in this workspace;
  native result summaries are therefore absent and not carried into this assessment.
- No native check was executed by this agent (shell/measurement outside agent
  authority). All `check-plan.json` entries are **planned, not run**.
- License/notice/upstream-maintenance/advisory data for `pastey`/`thiserror`/`futures`
  was not verified; nothing is vendored in-repo.
- `score-crates#42` (the linked policy/certification issue) is not fetchable here;
  its scope/status is unknown, as are the three sub-issues.
- Native tool work products have no project instances; applicability unknown.
- No Rust API-surface lock; only downstream compilation covers Rust generated-API
  stability.
- QNX is out of scope by task policy; QNX checks are recorded as unavailable, not
  evaluated.
- File sizes/hashes for the review-packet manifest must be produced by the
  deterministic collector; hashing is outside agent authority and is not fabricated.
