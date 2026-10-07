# Implementation / dependency assessment — `futures` in the Rust COM API (#1263)

Mode: **assessment** (from `.rust-queue/context/task.json`). Baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Linux only; QNX out of scope.

This issue is a dependency/qualification assessment (issue-types.md: "Documentation,
compliance or dependency-only work … A prose-only issue may end with an assessment rather
than a source patch"). **No source patch is authored and no dependency pin is changed.**
The smallest warranted deliverable is the recorded dependency/design assessment plus the
Linux collector check plan. Any retain/reduce/replace decision remains a reviewable
proposal until an authorized human accepts it offline.

## 1. Changed paths

| Path | Status in this stage | Contents |
| --- | --- | --- |
| `.rust-queue/reports/implementation.md` | **created** | This assessment, changed-path list and unresolved concerns. |
| `.rust-queue/reports/scope.md` | authored in the scope stage; re-verified here, not modified | Source-backed task binding, production/mock split, options, open items. |
| `.rust-queue/reports/check-plan.json` | authored in the scope stage; re-verified here, not modified | Linux collector check plan (schema `{checks:[{kind,targets,reason,native_obligation,config}]}`). |
| `.rust-queue/reports/review-packet.md` | authored in the scope stage; re-verified here, not modified | Review packet (acceptance trace, dependency table, evidence bindings, offline decisions). |

No repository source, BUILD, lock, license or CI-policy file was edited. This stage only
adds the implementation report; the artifacts already produced by the scope stage were
read and cross-checked against the baseline source and left byte-for-byte unchanged.

## 2. Re-verified baseline facts (source anchors)

The issue premise was re-checked against the baseline source, not accepted from the issue
prose. Bounded reads confirm:

| Claim | Anchor (verified at baseline) |
| --- | --- |
| Public API returns a `futures::Stream` | `score/mw/com/rust/score_com_concept/concept.rs:57` (`use futures::stream::Stream;`), `:931` (`fn to_stream<'a>(&'a mut self) -> impl Stream<Item = Result<Self::Sample<'a>>> + Unpin + 'a`) |
| Callback receive is a `core::future::Future`, not a `futures` executor | `concept.rs:55`; `consumer.rs:34`, `:917` |
| Production runtime uses `Stream` + `AtomicWaker` for receive wake | `com-api-runtime-lola/consumer.rs:40-41`, `:487`, `:676-689`, `:697-730`, `:791-827` |
| Register-before-receive avoids a missed wake-up | `consumer.rs:800-803` (comment + `waker_storage.register`) |
| Cancellation is polled first and the guard released on cancel/error/ready | `consumer.rs:713-778` |
| Async discovery uses `AtomicWaker` across the C++ callback/Rust poll boundary | `consumer.rs:925`, `:942`, `:993`, `:1011-1016` |
| Mock runtime is test-oriented | `com-api-runtime-mock/runtime.rs:34`, `:337-339` (`stream::empty()`), `:529` (`futures::executor::block_on`); `//score/mw/com/rust:score_com_mock` is `testonly = True` (`score/mw/com/rust/BUILD:33-44`) |
| Downstream/example use only | `com-api-example/src/consumer.rs:15-16`; `tests_using_tokio_runtime.rs:41` + tokio test; `basic_rust_api/consumer_async_apis/consumer_app.rs:31-32`, `:182` (`block_on` in `main`) |
| Design intent: no executor imposed | `score_com_concept/concept.rs:36`; `score/mw/com/rust/score_com.rs:27` |

Direct BUILD deps on `@score_communication_crate_index//:futures` (no `crate_features`, so
crate defaults): `score_com_concept/BUILD:30`, `com-api-runtime-lola/BUILD:32`,
`com-api-runtime-mock/BUILD:22`, `com-api-example/BUILD:26,48,71`,
`consumer_async_apis/BUILD:39`. No `Cargo.toml`/`Cargo.lock` exists in-tree (glob:
`**/Cargo.*` → empty); Bazel is the maintained build. No `AGENTS.md` exists in the tree.

## 3. Production versus mock/test use

- **Production:** the `futures::Stream` trait appears in the public
  `Subscription::to_stream` contract, and `futures::task::AtomicWaker` is the
  synchronization primitive that bridges the C++ receive/discovery callback thread to the
  Rust poll. `Context`/`Poll` are `core::task` re-exports. This is API/runtime behavior,
  including concurrency, cancellation and drop semantics — not a build-only tool.
- **Mock/test-only:** `futures::stream::empty` in the mock runtime and
  `futures::executor::block_on` in its `#[cfg(test)]` module; the mock crate is `testonly`.
- **Consumer/example:** `oneshot`, `FutureExt`, `StreamExt` and the example's
  `block_on`/tokio runtime are callers driving the public API. The API itself starts no
  executor and names no executor type; it must not impose one on users. The tokio
  integration test exists precisely to show the API runs under a caller-owned runtime.

## 4. Dependency inventory (what is known vs unknown)

- **Known:** declared dep `@score_communication_crate_index//:futures`; crate index is
  `bazel_dep(name = "score_crates", version = "0.0.11", repo_name =
  "score_communication_crate_index")` (`MODULE.bazel:41`); no `crate_features` attribute,
  so crate default features; Bazel-only build.
- **Unknown (must not be invented):** exact resolved `futures` version, effective/default
  features and feature unification, registry/source URL, resolved checksums, archive
  digest, license/NOTICE texts, maintainer/advisory status. The `score_crates` 0.0.11 index
  is an external module not vendored in this workspace and no Cargo manifest exists to read
  a version from. This is preserved as **missing evidence**, not asserted.

## 5. Options (proposals only)

| Option | Compatibility / build | Provenance, license, maintenance | Qualification effort | Disposition |
| --- | --- | --- | --- | --- |
| **A. Retain `futures`** | None; public `impl futures::Stream` + `AtomicWaker` semantics unchanged | Requires resolved index + license/NOTICE; otherwise unknown | Enumerate version/features/checksums/license/advisories; re-run check plan | **Recommended default** (no code/lock change) |
| **B. Reduce to `futures-core` (`Stream`) + `futures-task` (`AtomicWaker`)** | Trait identity identical (`futures::stream::Stream == futures_core::Stream`; `futures::task::AtomicWaker == futures_task::AtomicWaker`); changes pins/lock; mock/tests still need `futures`/`futures-executor`/channels | Same upstream repo; smaller closure but new pins need evidence | BUILD/lock update + native approval + full re-run | **Scoped follow-up proposal; not implemented** |
| **C. Replace with internal code / `core` only** | No stable `core` `Stream` at this MSRV; `AtomicWaker` would be reimplemented | Eliminates the dep, adds maintenance | High; new sync code + verification | **Not recommended** |

Recommendation: **retain (Option A)** with no change in this assessment, and record
Option B as a reviewable follow-up. Authority for any retain/reduce/pin decision is an
authorized repository codeowner/dependency reviewer; this report only proposes.

## 6. Required qualification artifacts (for Option A acceptance)

1. Resolved `futures` version, effective features and checksums from the `score_crates`
   0.0.11 index (query check in `check-plan.json`).
2. Upstream license and NOTICE texts (retrieval date), not inferred from the crate name.
3. Dated maintenance and advisory check.
4. Native component/library work products governing the Rust COM API — IDs **not
   discovered** from this baseline, so they remain unknown and must not be invented.
5. `wp__tlm_plan` / `wp__tool_verification_report` (process pin
   `98d1d5f42dad412a09a888ea25e59c62fa6371ce`, v1, status `valid`) are *type definitions*;
   a runtime library is not automatically a tool instance, so tool qualification is not
   assumed. Safety relevance and any tool/component classification stay human decisions.

## 7. Verification: check plan and status

The Linux collector check plan is `.rust-queue/reports/check-plan.json` (schema-conformant;
`kind` ∈ build/test/docs/lint/query; BUILD-derived labels; `config = linux_x64`). It covers:
public-API + runtime + mock builds; the abstraction unit/macro tests; LoLa runtime tests;
the tokio integration test and the async/sync SCTs; rustdoc targets (including the
`manual` `score_com_concept-macros-tests`); the three `clippy` `clippy_strict` targets; and
the dependency-resolution query.

Status: **no check has been executed by the agent.** Native result summaries
`.rust-queue/reports/native-check-summary.json` are **absent** in this workspace, so all
applicable checks are recorded as **unrun/pending** — this is preserved as missing
evidence, not as passing results. Raw evidence and exit codes are collector-owned and
outside agent authority. `score_com_concept-macros-tests` is `manual` with a documented
native-linking limitation; QNX is excluded (in-tree issue #1278). No fixtures are offered
as production evidence, and no check result is claimed to establish acceptance.

## 8. Unresolved concerns (must remain open)

1. Exact `futures` version/features/checksums/license/NOTICE/advisories — index not
   vendored; requires the resolution query.
2. Whether `futures` is safety-relevant, and the applicable native work-product/instance
   IDs — human decision; IDs not discovered.
3. Lint-policy applicability: `score_rust_policies` 0.0.5 (`clippy_strict`) is a dev
   dependency; the check plan applies it but its applicability is pending confirmation.
4. Native check execution and `native-check-summary.json` are absent (pending collector).
5. Whether the `manual` `score_com_concept-macros-tests` gives any doc-test coverage of the
   async `to_stream` contract — not established.
6. QNX Rust tests are out of scope by task instruction and #1278; no QNX evidence claimed.
7. No in-tree Rust requirement/design IDs were found to trace against; none were invented.

## 9. Validation performed in this stage

- Bounded source reads (≤200 lines) of the files named in `scope.md` §2, plus the owning
  BUILD files and `MODULE.bazel`/`.bazelrc`/`static_analysis.bazelrc`, to confirm every
  citation and BUILD label used by the check plan.
- Confirmed absence of Rust `Cargo.*` manifests and of `AGENTS.md` (glob).
- No build/test/lint/query run (shell and execution tools are blocked in this workspace);
  outcomes are deferred to the Linux collector.

## 10. Pending offline decisions and next action

Decisions required from authorized humans: (1) retain `futures` vs adopt Option B;
(2) whether `futures` is safety-relevant and any tool/component classification; (3) the
qualification artifacts to place under native work-product IDs. Concrete next action: run
the Linux collector against `check-plan.json`, then resolve the `score_crates` 0.0.11 index
to record the exact version/features/license/advisory evidence before routing the
retain-vs-reduce proposal to review. With the dependency inventory unknown and no native
results yet, **no readiness/qualification/acceptance claim is made.**
