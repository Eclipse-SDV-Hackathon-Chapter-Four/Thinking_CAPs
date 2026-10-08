# Implementation record — subscription state query and change notification

**Issue**: eclipse-score/communication#560 — "Improvement: Add Subscription State Change APIs
Support on Rust API Lib" (label `rust-api`, type `Product Increment`).
**Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
**Stage outcome**: the source change is **applied in this disposable workspace**. Native checks are
**not executed** (shell/measurement tools remain outside agent authority); no result is claimed.

This file supersedes the earlier proposal-style `implementation.md` from the scope stage. The prior
`scope.md` design and the four proposed engineering decisions remain reviewable proposals; only the
mechanical patch has moved from "proposed" to "applied".

---

## 1. Actual changed paths

| # | Path | Change |
| --- | --- | --- |
| 1 | `score/mw/com/rust/score_com_concept/concept.rs` | `SubscriptionState` enum (`#[repr(u8)]`, discriminants 0/1/2) + `From<u8>`; three required methods added to the `Subscription` trait (`get_subscription_state`, `set_subscription_state_change_handler`, `unset_subscription_state_change_handler`). |
| 2 | `score/mw/com/rust/score_com_concept/error.rs` | `EventFailedReason::SubscriptionStateChangeHandlerFailed`. |
| 3 | `score/mw/com/rust/score_com.rs` | Re-export `SubscriptionState`. |
| 4 | `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs` | Three raw methods on `FFIBridge`: `get_subscription_state -> u8`, `set_subscription_state_change_handler(&FatPtr) -> bool`, `unset_subscription_state_change_handler -> bool`. Raw `u8` keeps `bridge_ffi_rs` independent of `score_com_concept`. |
| 5 | `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_lola.rs` | `extern "C"` declarations for the three C++ wrappers; Rust→C++ trampoline `mw_com_impl_call_dyn_ref_fnmut_subscription_state`; typed box dropper `mw_com_impl_delete_boxed_fnmut_subscription_state`; `LolaFFIBridge` impls. |
| 6 | `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_mock.rs` | `mock!` declarations and `SharedMockBridge` forwarding for the three methods. |
| 7 | `score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h` | `extern "C"` declarations of the invocation trampoline and the typed dropper; `RustBoxedCallable<bool, SubscriptionState>` specialization. |
| 8 | `score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.cpp` | C++ wrappers `mw_com_proxy_event_get_subscription_state`, `..._set_subscription_state_change_handler`, `..._unset_subscription_state_change_handler`, delegating to `ProxyEventBase::GetSubscriptionState` / `SetSubscriptionStateChangeHandler` / `UnsetSubscriptionStateChangeHandler`. |
| 9 | `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs` | `subscription_state_handler_set: AtomicBool` field; three trait impls on `LolaSubscriberImpl`; `Drop` unregisters the state handler before `unsubscribe_to_event`; four unit tests + `make_subscribed` helper. |
| 10 | `score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs` | Three trait impls on `MockSubscriberImpl` (`get` → `NotSubscribed`, `set`/`unset` → `Ok(())`). |
| 11 | `score/mw/com/rust/doc/user_facing_api_examples.md` | New "Subscription State Query and Change Notification" section. |
| 12 | `score/mw/com/rust/design/high_level_design_detail.md` | LoLa "Key features" bullet for subscription-state observation ("Affects Detailed Design" category). |

**BUILD files: unchanged.** No new crate/rule/dependency is introduced: `u8`/`bool` at the FFI seam,
`score_com_concept`/`score_log`/`futures` already present, and the new tests live in the existing
`//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` target (which
already depends on `bridge_ffi_mock` + `mockall`). No lint profile, toolchain pin or feature set was
changed, and no source correction was needed beyond the max-source-corrections budget (0 used).

## 2. Source-backed contracts used

- `score/mw/com/impl/subscription_state.h`: `enum class SubscriptionState : std::uint8_t`
  `{ kSubscribed = 0, kNotSubscribed = 1, kSubscriptionPending = 2 }` (`SWS_CM_00310`) → mirrored
  exactly by the Rust `#[repr(u8)]` enum.
- `score/mw/com/impl/subscription_state_change_handler.h`:
  `using SubscriptionStateChangeHandler = score::cpp::callback<bool(SubscriptionState)>`, whose
  `bool` return unregisters the handler when `false`.
- `score/mw/com/impl/proxy_event_base.h`: `GetSubscriptionState() const noexcept` (always callable),
  `Result<void> SetSubscriptionStateChangeHandler(...) noexcept`,
  `Result<void> UnsetSubscriptionStateChangeHandler() noexcept`; documented override + "never called
  after unset" semantics.

## 3. Obligation coverage

| # | Obligation | Disposition |
| --- | --- | --- |
| O1 | Sync state query returns current C++ state | Implemented; unit-tested for raw 0/1/2/255 mapping. |
| O2 | Async change notification registered/unregistered | Implemented; unit-tested register/unregister. |
| O3 | `false` return unregisters handler | Preserved end-to-end (`bool` return through `RustBoxedCallable<bool, SubscriptionState>` and the trampoline); the unregister decision itself lives in C++. No Rust runtime test invokes the trampoline. |
| O4 | Handler may run under lock; no reentrant same-event calls | Documented contract on the trait + user-facing doc. Not enforced (would deadlock rather than error). |
| O5 | Overriding registration silently replaces | C++ `SetSubscriptionStateChangeHandler` contract; the FFI re-registers (no guard rejects a second set). |
| O6 | After unset the handler is never called | C++ binding guarantee + `Drop` unset before unsubscribe. |
| O7 | Lifetime: handler `Send + 'static`; box freed exactly once | Implemented: box ownership transfers to middleware; `Drop`/`false`-failure path reclaims only when C++ reports it did not take ownership. |
| O8 | Teardown must not invoke handler after drop | `Drop` unregisters (flag-guarded) before `unsubscribe_to_event`; covered by mock test `test_drop_unregisters_registered_state_handler`. |
| O9 | Mock runtime stays compilable | Implemented in `com-api-runtime-mock`. |
| O10 | Docs/examples compiled where not `ignore` | Docs updated (`.md`, not rustdoc-tested). |
| O11 | No new lint/format/CI exceptions | No suppression added; no BUILD/pin change. |
| O12 | Integration coverage of real provider transitions | **Still open** — no end-to-end stop-offer/re-offer scenario added. |

## 4. Regression tests added (`com-api-runtime-lola-tests`)

- `test_get_subscription_state_maps_raw_values` — sync query, mapping 0→Subscribed,
  1/255→NotSubscribed, 2→SubscriptionPending.
- `test_set_and_unset_subscription_state_change_handler` — async register then explicit unregister;
  `unset` expectation bounded to `times(1)`.
- `test_set_handler_failure_is_reported_and_box_reclaimed` — FFI refusal returns
  `EventError(SubscriptionStateChangeHandlerFailed)` and the boxed closure is reclaimed (no unset is
  expected on teardown).
- `test_drop_unregisters_registered_state_handler` — teardown unregisters exactly once before
  `unsubscribe_to_event`.

Verification axes requested by the task: sync transition (test 1), async registration/cancellation
surface (tests 2–3), lifetime/box-ownership (tests 2–4), teardown ordering (test 4), reentrancy
(documented + serialised through the existing `ProxyEventManager`). Cancellation-via-`false` is a
C++ state-machine behaviour and is covered by the C++ tests enumerated in `check-plan.json`, not by a
Rust unit test.

## 5. Deviation from `scope.md` (documented)

`scope.md` §6.3 proposed reusing `mw_com_impl_delete_boxed_fnmut` for disposal. That function
reconstructs a `Box<dyn FnMut() + Send>`, while this handler's box is
`Box<dyn FnMut(u8) -> bool + Send>`; dropping it through the wrong trait-object type is not a
guaranteed-correct use of Rust's unspecified vtable layout. The implementation instead adds a
**typed** dropper `mw_com_impl_delete_boxed_fnmut_subscription_state`, and
`RustBoxedCallable<bool, SubscriptionState>::dispose` calls it. This is the only deviation.

## 6. Unresolved concerns / open items (must remain open)

1. **Placement** — the API is on `Subscription` (post-subscribe). Placing `get_subscription_state`
   on `Subscriber` too remains an undecided design/API question.
2. **No native evidence** — no Bazel/toolchain was executed in this session and
   `.rust-queue/reports/native-check-summary.json` is still **missing**; nothing is marked passed.
3. **No end-to-end transition test** — O12 open.
4. **Upstream activity** — linked PRs/commits for #560 were not retrievable (network out of scope).
5. **`binding_ == nullptr`** — C++ `SetSubscriptionStateChangeHandler` dereferences `binding_`; the
   Rust path can only supply an event from a successfully created proxy, but this precondition is
   asserted by the middleware, not newly enforced here.
6. **Unknown raw state value** — mapped conservatively to `NotSubscribed`; the C++ signature is
   infallible, so no error signal is available.
7. **Reentrancy not enforced** — the documented deadlock hazard if the user calls back into the same
   event is a contract, not a runtime guard.
8. **`com-api-runtime-mock` unit tests** — the `#[cfg(test)] mod test` in `runtime.rs` is not built
   by any test target (pre-existing), so the new mock methods are only compile-checked as part of the
   library.
9. **QNX** — out of scope per task; no QNX target or execution was touched. Rust test targets keep
   their existing `@platforms//os:linux` compatibility tags.

## 7. Reviewable decisions (pending authorized human acceptance)

1. API placement on `Subscription` rather than additionally on `Subscriber`.
2. `get_subscription_state()` infallible, unknown raw value → `NotSubscribed`.
3. Raw `u8`/`bool` at the `FFIBridge` seam (avoids coupling `bridge_ffi_rs` to `score_com_concept`).
4. `Drop` unregisters the state handler before `unsubscribe_to_event`.
5. Adding a dedicated typed dropper instead of reusing the `dyn FnMut()` deleter.

None of these are marked accepted; tests/clean analyzers cannot supply that decision.
