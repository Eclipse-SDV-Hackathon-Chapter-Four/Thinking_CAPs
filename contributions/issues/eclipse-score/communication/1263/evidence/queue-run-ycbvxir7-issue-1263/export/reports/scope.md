# Scope — `futures` crate usage in the Rust COM API (issue #1263)

Assessment only. No source change is proposed as an accepted decision. All
retain/reduce/replace conclusions below are reviewable proposals pending authorized
offline human acceptance.

## 1. Task binding

| Field | Value |
| --- | --- |
| Issue | eclipse-score/communication #1263 — "Improvement: `futures` crate usage in the Rust COM API" |
| Issue state (provided snapshot) | open, 0 comments, 0 linked PRs, label `rust-api`, `updated_at` 2026-10-04T11:11:54Z |
| Repository | eclipse-score/communication (`module(name = "score_communication")`) |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Mode | assessment |
| Platform scope | Linux only (QNX explicitly out of scope per task instruction and per #1278 Rust-test limitation) |
| Authority | Reports under `.rust-queue/reports/` only. Shell, delegation, publishing and acceptance tools are blocked. |
| Live issue/PR re-fetch | **Unavailable** (network/web tools blocked in this workspace). Issue text is used as provided in `.rust-queue/context/issue.json`; `.rust-queue/context/comments.json` is `[]`. This is preserved as missing evidence, not treated as fresh. |
| Native result summaries | `.rust-queue/reports/native-check-summary.json` is **absent at authoring time**; native outcomes are pending and are not asserted here. |

Issue prose was treated as task data. The premise (public `Subscription::to_stream`
returns a `futures::Stream`; LoLa runtime uses `futures::task::AtomicWaker`; the mock
runtime uses stream helpers and an executor in support code; the COM API does not
require users to adopt an executor) was re-verified against the baseline source below.

## 2. Baseline source facts (source-backed)

- Public async surface is declared in `score/mw/com/rust/score_com_concept/concept.rs`:
  - `use futures::stream::Stream;` (line 57).
  - `Subscription::to_stream<'a>(&'a mut self) -> impl Stream<Item = Result<Self::Sample<'a>>> + Unpin + 'a`
    (line 931).
  - Async receive is expressed with `core::future::Future` (`receive`, `cancellable_receive`,
    `get_available_instances_async`), not a `futures` executor.
- Production runtime `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs`:
  - `use futures::stream::Stream;` (line 40) and
    `use futures::task::{AtomicWaker, Context, Poll};` (line 41).
  - `LolaSubscriberImpl { waker_storage: Arc<AtomicWaker>, ... }` (line 487).
  - `to_stream()` returns `SampleStream` (lines 676–689).
  - `ReceiveFuture { waker_storage: Arc<AtomicWaker>, ... }`; `poll` registers
    `self.waker_storage.register(ctx.waker())` (lines 697–730).
  - `impl Stream for SampleStream` registers the waker before the receive attempt
    to avoid a missed wake-up race (lines 791–826).
  - Async service discovery allocates `Arc::new(futures::task::AtomicWaker::new())`
    (line 925) and stores `Arc<futures::task::AtomicWaker>` (line 993); the C++
    callback calls `waker.wake()` (line 942) and `ServiceDiscoveryFuture::poll`
    registers the waker (line 1016).
  - `cancellable_receive` polls the caller-supplied cancellation future first and
    drops it with the receive future; no executor is started by the runtime.
- Mock/test runtime `score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs`:
  - `use futures::stream::{self, Stream};` (line 34); `to_stream` returns
    `stream::empty()` (lines 337–339).
  - Test module uses `futures::executor::block_on(...)` (line 529).
- Downstream/examples (users of the public API, not the API implementation):
  - `score/mw/com/example/com-api-example/src/consumer.rs`:
    `futures::channel::oneshot`, `futures::{FutureExt, StreamExt}` (lines 15–16).
  - `score/mw/com/example/com-api-example/tests_using_tokio_runtime.rs`:
    `futures::stream::StreamExt` (line 41); driven by `#[tokio::test(flavor = "multi_thread")]`.
  - `score/mw/com/test/basic_rust_api/consumer_async_apis/consumer_app.rs`:
    `futures::channel::oneshot`, `futures::{FutureExt, StreamExt}` (lines 31–32);
    `futures::executor::block_on` in `main` (line 182).
- BUILD direct dependencies on the crate (`@score_communication_crate_index//:futures`),
  with no `crate_features`, i.e. crate default features:
  - `score/mw/com/rust/score_com_concept/BUILD:30`
  - `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD:32`
  - `score/mw/com/impl/rust/com-api/com-api-runtime-mock/BUILD:22`
  - `score/mw/com/example/com-api-example/BUILD:26,48,71`
  - `score/mw/com/test/basic_rust_api/consumer_async_apis/BUILD:39`
- Design intent (source-backed): "The API does not enforce the necessity for internal
  threads or executors" (`score_com.rs:27`); "COM API does not enforce the necessity for
  internal threads or executors" (`concept.rs:36`). No executor type appears in the
  `score_com_concept` public API. `futures::executor` appears only in test/support code.

## 3. Production vs mock/test-only distinction

| Use | Location | Classification |
| --- | --- | --- |
| `futures::stream::Stream` in trait bound / return type | `score_com_concept/concept.rs` | **Production public API contract** |
| `futures::stream::Stream`, `futures::task::AtomicWaker`, `Context`, `Poll`; receive-stream and discovery wake | `com-api-runtime-lola/consumer.rs` | **Production runtime behavior (concurrency/cancellation/wake)** |
| `futures::stream::{self, Stream}`; `stream::empty()`; `futures::executor::block_on` | `com-api-runtime-mock/runtime.rs` | **Mock/test-only** (`//score/mw/com/rust:score_com_mock` is `testonly = True`) |
| `oneshot`, `FutureExt`, `StreamExt`, `block_on`; tokio runtime | `com-api-example`, `basic_rust_api` binaries/tests | **Consumer-side examples/tests; no executor imposed by the API** |

The only executor usage in-tree is in the mock runtime test module and in
example/integration test binaries. Neither is a production COM API component, and
neither forces an executor onto applications.

## 4. Dependency inventory status

- Declared dep: `@score_communication_crate_index//:futures` (the crate index is
  `bazel_dep(name = "score_crates", version = "0.0.11", repo_name =
  "score_communication_crate_index")`, `MODULE.bazel:41`).
- **Exact pinned version, enabled features, resolved checksums, source/archive digest and
  license/notice texts are UNKNOWN from this workspace**: the crate index is an external
  module not vendored here, there is no `Cargo.lock`/`Cargo.toml`, and shell/grep/network
  tools are blocked. No version number may be invented. Resolution requires the
  `score_crates` 0.0.11 crate-index evidence and a dependency query (see check plan).
- Enabled features: no `crate_features` attribute is set on any `futures` BUILD dep, so
  the crate default feature set is used; the actual default/feature unification must be
  confirmed from the resolved index (open).
- Upstream crate identity (name `futures`, dual MIT/Apache-2.0, maintainer activity,
  advisories) is **not asserted** here: it must be recorded from the resolved archive and
  license texts with a retrieval date. Maintenance/archival/advisory claims are left
  open rather than inferred from the crate name.

## 5. Technical assessment of `futures` use

- The production API needs exactly two items from the `futures` family:
  the `Stream` trait (equivalently `futures_core::Stream`) and
  `futures::task::AtomicWaker` (from `futures-task`). `Context`/`Poll` are `core::task`
  re-exports. Everything else (`futures::stream::empty`, `executor::block_on`,
  `channel::oneshot`, `FutureExt`, `StreamExt`) is test/example-side.
- Wake/cancellation correctness is observable and already documented in-source:
  `SampleStream::poll_next` registers the waker before the receive attempt to avoid a
  missed wake-up; `ReceiveFuture` polls the cancellation future first and releases the
  `ProxyEventManagerGuard` on completion/cancellation/error; `ServiceDiscoveryFuture`
  registers the waker before reading shared `Mutex` state. These are production
  concurrency obligations that any retain/reduce option must preserve.
- Safety relevance is a **human decision**. `AtomicWaker` is synchronization/FFI-adjacent
  (C++ callback thread wakes a Rust waker), so the crate is used in an API/runtime
  behavior path, not a build-only tool. It is not, by itself, evidence of a safety-relevant
  classification.

### Options (proposals only)

| Option | Compatibility / build impact | Provenance, license, maintenance | Qualification effort | Disposition |
| --- | --- | --- | --- | --- |
| **A. Retain `futures` as-is** | None. Public trait `impl futures::Stream` and `AtomicWaker` semantics unchanged; no lock change. | Requires resolved index + license/notice; otherwise unknown. | Enumerate resolved version/features/checksums, license, advisories; re-run listed checks. | **Recommended default** (no code/lock change in this assessment). |
| **B. Reduce to `futures-core` (`Stream`) + `futures-task` (`AtomicWaker`)** | `futures::stream::Stream == futures_core::Stream`, `futures::task::AtomicWaker == futures_task::AtomicWaker`, `Context`/`Poll == core::task`; production compiles unchanged. Mock/tests still need `futures`/`futures-executor`/channels. Changes dependency pins and lock. | Same upstream repo; smaller transitive closure, but new pins need provenance evidence. | BUILD/lock update + native approval + full re-run. | **Scoped follow-up proposal**, requires authorized decision; not implemented. |
| **C. Replace with internal code / `core` only** | `Stream` has no stable `core` trait at this MSRV; `AtomicWaker` would be reimplemented, duplicating a synchronization primitive. | Eliminates the dependency but adds maintenance and verification burden. | High; new unsafe/sync code and verification. | **Not recommended.** |

Required qualification artifacts if Option A is accepted: resolved `futures` version /
features / source / checksums from the `score_crates` 0.0.11 index; upstream license and
NOTICE texts; dated maintenance/advisory check; and the native component/library work
products governing the Rust COM API (IDs not discovered from this baseline — open).
`wp__tlm_plan` / `wp__tool_verification_report` (process pin
`98d1d5f42dad412a09a888ea25e59c62fa6371ce`, version 1, status `valid`) are type
definitions; a runtime library is not automatically a tool instance, so tool
qualification is **not** assumed and any instance/classification remains a human decision.

## 6. Requirements / design / verification impact

- Requirements / Architecture checkbox in the issue is checked "not affected"; nothing in
  this baseline contradicts that, but no Rust requirement/design IDs were found in-tree to
  trace against (open). No requirement IDs are invented.
- Design impact: `score/mw/com/rust/design/high_level_design_detail.md` documents the
  trait hierarchy but carries no requirement IDs and does not name `futures`. A retain
  decision leaves the design unaffected; a reduce/replace decision would touch the
  dependency/BUILD surface and require design/policy review.
- Verification impact: retain needs no new tests; reduce/replace would need the listed
  build/test/docs/lint checks re-run plus downstream compilation of `to_stream`,
  `receive`/`cancellable_receive` (wake/cancellation) and discovery futures.

## 7. Open items (must remain open)

1. Exact `futures` version, features, checksums, license/notice, advisories (index not vendored).
2. Whether the crate is safety-relevant and its applicable native work-product IDs.
3. Applied rustdoc/lint policy: `clippy_strict` (`score_rust_policies` 0.0.5) is a dev
   dependency; applicability confirmation pending.
4. `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` is tagged
   `manual` with a documented native-linking limitation; its doc-test coverage of the
   async API is not established.
5. QNX is out of scope; Rust tests are Linux-only per in-tree comment / issue #1278.
