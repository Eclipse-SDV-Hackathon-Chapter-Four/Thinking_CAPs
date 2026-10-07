# Implementation — communication#490 "Mock Runtime implementation of Rust COM-API"

Status: **implemented in the disposable copy; not measured; not accepted.**
This stage applied the source-derived change drafted in `.rust-queue/reports/proposed-change.md`.
Technical completion is reported separately from native engineering acceptance.
No shell/execution/network authority was available, so no check was executed and no hash was computed.

- Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- Issue: `eclipse-score/communication#490`, state `open`, label `rust-api`, 0 comments
- Platform scope: Linux only (no QNX task/execution)
- Evidence status: `.rust-queue/reports/native-check-summary.json` **absent** (missing evidence preserved);
  no raw logs, exit codes or subject hashes exist for this change.

## 1. Premise check (mock runtime already exists)

The issue premise ("mock runtime is not developed") is partially resolved at this baseline, so the
skeleton was completed rather than reimplemented:

- `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` existed
  (`runtime.rs`) but had `todo!()`/`unimplemented!()` in offer/stop, `SampleMut::send`,
  `try_receive`, `cancellable_receive`; `to_stream` was `stream::empty()`; discovery always
  returned no instances; the `#[cfg(test)]` module did not compile and was built by no target.
- `//score/mw/com/rust:score_com_mock` existed as a test-only re-export.
- `//score/mw/com/rust:score_com` (LoLa) existed and is fully implemented.

## 2. Actual changed paths

| # | Path | Change | Rationale / native obligation |
|---|------|--------|-------------------------------|
| 1 | `score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs` | Completed the mock: process-wide type-erased in-process bus; working `offer_service`/`stop_offer_service`, `SampleMut::send`, `try_receive`, `cancellable_receive`, `to_stream`, and `Specific`/`Any` discovery; replaced the stale non-compiling test module with two tests. License header, public type names and crate lint policy (`#![allow(dead_code)]`, `#![allow(clippy::needless_lifetimes)]`) preserved. | Implements the unchanged `score_com_concept` `Runtime`/`Publisher`/`Subscriber`/`Subscription`/`ServiceDiscovery` contracts. Rust library/API + communication-behavior obligations. |
| 2 | `score/mw/com/impl/rust/com-api/com-api-runtime-mock/BUILD` | Load `rust_test`/`rust_doc_test`; added `com-api-runtime-mock-tests` and `com-api-runtime-mock-doc-tests` (`target_compatible_with = ["@platforms//os:linux"]`), mirroring `com-api-runtime-lola/BUILD`. | Makes the `#[cfg(test)]` module build and gives the crate a rustdoc target; previously absent (regressions undetected). |
| 3 | `score/mw/com/rust/BUILD` | Updated the stale `score_com_mock` comment; issue URL retained. | Removes now-inaccurate "Mock Runtime is not yet ready" text; no target/dep change. |
| 4 | `score/mw/com/rust/design/high_level_design_detail.md` | Replaced "Mock runtime support is not yet enabled in the current build." with a note describing the test-only in-process mock reachable via `//score/mw/com/rust:score_com_mock`, production path LoLa. | Corrects documentation drift (design note). |

No changes to `score_com_concept`, `com-api-runtime-lola`, `score_com.rs`, MODULE pins/lock, lint
policy, features or the public `score_com` surface. No Cargo scaffolding; no dependency added,
removed or upgraded.

## 3. Corrections applied to the drafted proposal (before writing)

The draft in `proposed-change.md` was source-derived and never compiled. Three defects were corrected
while applying it, because the command stage would otherwise fail to build:

1. **Unused type parameter (E0392):** `MockSubscriberImpl<T>` had no field using `T`. Added
   `data: PhantomData<T>` to the struct and to its construction site in `subscribe`. Without this the
   crate does not compile.
2. **Trait not in scope (E0599):** the draft test calls `self.instance_info.offer_service()` inside
   `TestProducer::offer` but did not import `ProviderInfo`. Added `ProviderInfo` to the
   `score_com_concept` import list in `mod tests`.
3. **Field-name collision in the draft test:** `MockSample` exposed a private field `value: Box<T>`,
   so the draft's `sample.value` resolved to the `Box<T>` field instead of the `TestData::value`
   field through `Deref` (type mismatch). Renamed the `MockSample` internal field `value` → `inner`
   so `sample.value` auto-dereferences to `T::value`. Private field, no public-surface change.

These are mechanical corrections required to make the proposed behavior compilable; they do not
change the proposed public types or semantics.

## 4. Semantics preserved / added (runtime-independent)

- `score_com_concept` trait/type signatures are untouched; `score_com` (LoLa) is untouched.
- The mock capability is additive and reachable only through the test-only `score_com_mock` re-export.
- `Sample<T>` remains `Send + Ord + Debug`; `MockSample` uses owned `Box<T>` plus
  `PhantomData<&'a ()>` (not `&'a T`) so it does not require `T: Sync`, which `Reloc` does not provide.
- `try_receive` with `max_samples == 0` returns `Error::ReceiveError(SampleCountOutOfBounds)`;
  ordering is by reception id.
- Discovery supports both `FindServiceSpecifier::Specific` and `Any` (Lola supports only `Specific`).

## 5. New regression/consumer cases

`com-api-runtime-mock-tests` compiles and runs the crate's `#[cfg(test)]` module (via `crate =`):

- `offer_publish_discover_receive_roundtrip`: offer → discover (`Specific`) → subscribe → publish →
  `try_receive` → assert sample value, then unoffer.
- `manually_injected_data_is_received`: backend-free direct injection through `add_data` then receive.

Note: the checked-in tests are the crate-internal unit tests, not a separate consumer target.
No `basic_rust_api` consumer was changed; the test-only `score_com_mock` target remains the intended
downstream entry point.

## 6. Verification status (not executed here)

No commands were run: shell/execution and delegation are blocked in this workspace, and command
stages own raw evidence. `native-check-summary.json` is absent. The check set to run is
`.rust-queue/reports/check-plan.json` (unchanged scope artifact). The two `proposed: true` checks
(`com-api-runtime-mock-tests`, `com-api-runtime-mock-doc-tests`) now point at targets that **do
exist** in the patched BUILD and are therefore runnable; the remaining checks reference baseline
targets.

Expected Linux checks (targets only; execution owned by the command stage):

| Kind | Target | Obligation |
|------|--------|------------|
| build | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` | Rust library/API compile against unchanged contracts |
| build | `//score/mw/com/rust:score_com_mock` | downstream compilation of the test-only re-export |
| build | `//score/mw/com/rust:score_com` | LoLa/default public-surface regression |
| test | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock-tests` | mock producer/consumer round-trip |
| test | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | unchanged abstraction tests |
| test | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | LoLa regression |
| docs | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock-doc-tests` | mock rustdoc compile |
| docs | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | abstraction rustdoc (`manual`, enumerate explicitly) |
| lint | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` | pinned `clippy_strict` policy |

## 7. Unresolved concerns (must remain open)

- **Registry model is a design decision:** the in-process shared bus vs. per-subscription injection.
  This implementation follows the draft's shared-bus proposal; it is **not** an accepted architecture
  decision.
- **`cancellable_receive` contract:** the mock has no async notification channel, so the future
  makes one probe, waits for cancellation, makes a second probe and returns `Ok(added)` (never
  `Cancelled`). Correct semantics for a notification-free mock are unresolved.
- **`max_num_samples` enforcement:** subscribe capacity is recorded but publisher overflow is not
  rejected; whether the mock must enforce it is unresolved.
- **Requirements/architecture impact:** the issue's template box is unchecked and grants no
  authority; impact remains **pending human decision**.
- **Upstream reconciliation:** PR/issue activity for #490 could not be fetched (network blocked), so
  this change is source-derived, not reconciled with a merged upstream implementation.
- **No measured evidence / no hashes:** compilability and tests are asserted from source reading only.
  A command stage must execute the checks above and produce raw logs plus a new
  `native-check-summary.json`; this report is not fresh evidence until then.

## 8. Next action

Apply nothing further here. A network-enabled/execution-authorized stage should: re-fetch #490 and
linked PRs; run the checks in `check-plan.json` (the two mock targets now exist); publish raw logs and
`native-check-summary.json`; then authorized reviewers decide the registry model,
`cancellable_receive` semantics, `max_num_samples` enforcement and the documentation/BUILD text.
Until then, technical completion is unverified and engineering acceptance is pending.
