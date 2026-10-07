# Scope and binding — issue eclipse-score/communication#560

## 1. Task identity and authority

| Field | Value | Source |
| --- | --- | --- |
| Issue | `eclipse-score/communication#560` | `.rust-queue/context/issue.json` |
| Title | Improvement: Add Subscription State Change APIs Support on Rust API Lib | issue.json |
| State / labels | `open`; label `rust-api`; type `Product Increment` | issue.json |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` | `.rust-queue/context/task.json` |
| Task mode | `implementation` | task.json |
| Max source corrections | 3 | task.json |
| Runtime revision | Linux native checkpoints and verification launcher | task.json |
| Issue retrieval time | 2026-06-18T10:32:29Z (created) / 2026-06-18T10:32:51Z (updated) | issue.json |
| Comments | empty (`[]`) | `.rust-queue/context/comments.json` |
| Cross-referenced PRs / timeline | **not retrieved** — no network tool available in this session | tool boundary |

Authority limits actually observed in this workspace:

- `shell`, `grep`, `web_fetch`, `update_plan` and all source-tree writes are refused by the
  file-tool boundary ("Bound Rust workspace/file-tool boundary").
- Only `.rust-queue/reports/` is writable. Therefore the proposed implementation is exported as a
  reviewable patch/spec, **not applied** to the source tree. No native check can be executed from
  this session; command stages and raw evidence are outside agent authority.
- Source reads were kept to <=200 lines per call; content search was only possible via
  `glob` (filenames) because `grep` is refused.

## 2. Missing / failed evidence preserved

| Item | Expected location | Status |
| --- | --- | --- |
| Native result summaries | `.rust-queue/reports/native-check-summary.json` | **MISSING** (file not found) |
| Issue comments | `.rust-queue/context/comments.json` | present, empty |
| Upstream timeline / linked PRs | GitHub API | **not retrieved** (network blocked) |
| Applied source patch | source tree | **not applied** (source writes blocked) |
| Executed native checks | Bazel | **not run** (shell blocked) |

No native evidence is invented. Every check in `check-plan.json` is a *planned* obligation; none
is claimed as passed.

## 3. Requested outcome (issue prose treated as task data)

> C++ offers `GetSubscriptionState()` (sync) and `SetSubscriptionStateChangeHandler()` (async) to
> get the current subscription state of a subscribed event. Implement the same API support in the
> Rust COM-API lib.

Category field marks "Affects Detailed Design"; the "Requirements / Architecture are not affected"
box is left unchecked, so requirements/design impact is treated as *possible* and the design doc is
updated (docs obligation), while requirement IDs are left untouched.

## 4. Actual C++ contract (source of truth)

`score/mw/com/impl/subscription_state.h` (requirement `SWS_CM_00310`):

```cpp
enum class SubscriptionState : std::uint8_t
{
    kSubscribed,          // 0
    kNotSubscribed,       // 1
    kSubscriptionPending, // 2
};
```

`score/mw/com/impl/proxy_event_base.h`:

```cpp
SubscriptionState GetSubscriptionState() const noexcept;                       // always callable
Result<void> SetSubscriptionStateChangeHandler(SubscriptionStateChangeHandler) noexcept;
Result<void> UnsetSubscriptionStateChangeHandler() noexcept;
```

`score/mw/com/impl/subscription_state_change_handler.h`:

```cpp
using SubscriptionStateChangeHandler = score::cpp::callback<bool(SubscriptionState new_state)>;
```

Documented handler semantics that the Rust API must preserve:

- may be invoked while the internal state-machine lock is held → the handler must be short and
  must not call other methods on the same event (would deadlock);
- returning `false` unregisters the handler (supported alternative to unsetting from inside);
- an already-registered handler is silently overridden by a new registration;
- after `UnsetSubscriptionStateChangeHandler()` returns, the handler is guaranteed neither active
  nor callable again.

`score/mw/com/impl/proxy_event_base.cpp` (L154-182) delegates both calls to the binding;
`score/mw/com/impl/bindings/lola/proxy_event.cpp` (L155-165) moves the handler into the
`SubscriptionStateMachine` and always returns success.

## 5. Baseline Rust implementation observed

- `score/mw/com/rust/score_com_concept/concept.rs` — runtime-agnostic `Subscription<T, R>` trait
  (unsubscribe / try_receive / receive / cancellable_receive / to_stream); no subscription-state API.
- `score/mw/com/rust/score_com_concept/error.rs` — `EventFailedReason` / `Error`.
- `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs` — `LolaSubscriberImpl<T,B>`
  implements `Subscription`; owns `event: ProxyEventManager`, an `async_init_status: OnceLock<()>`,
  and a `Drop` that clears the receive handler then unsubscribes.
- `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs` — `FFIBridge` trait (raw FFI
  surface: subscribe/unsubscribe/receive-handler/…).
- `.../bridge_ffi_lola.rs` — `extern "C"` declarations + `LolaFFIBridge` impl + Rust→C++ closure
  trampolines (`mw_com_impl_call_dyn_*`, `mw_com_impl_delete_boxed_fnmut`).
- `.../bridge_ffi_mock.rs` — mockall `MockFFIBridge` + `SharedMockBridge`.
- `.../registry_bridge_macro.h/.cpp` — C++ `extern "C"` wrappers and `RustBoxedCallable<>`
  specializations used to invoke Rust callbacks (receive handler, find-service).
- `.../com-api-runtime-mock/runtime.rs` — `MockSubscriberImpl` implements `Subscription`.
- Existing native checks: `com-api-runtime-lola-tests` (mock-bridge unit tests),
  `score_com_concept-test`, doc-test targets, and basic_rust_api integration tests.

No prerequisite implementation of subscription-state APIs was found anywhere in the baseline.

## 6. Proposed design (smallest source-backed change)

### 6.1 Abstraction layer (`score_com_concept`)

1. Add `#[repr(u8)] pub enum SubscriptionState { Subscribed = 0, NotSubscribed = 1,
   SubscriptionPending = 2 }` plus `impl From<u8>` (unknown → `NotSubscribed`) so the numeric
   discriminants stay ABI-locked to the C++ enum.
2. Extend `Subscription` with three methods:
   - `fn get_subscription_state(&self) -> SubscriptionState` (sync, mirrors C++, infallible);
   - `fn set_subscription_state_change_handler(&self, handler: impl FnMut(SubscriptionState) -> bool + Send + 'static) -> Result<()>`;
   - `fn unset_subscription_state_change_handler(&self) -> Result<()>`.
   The `bool` return of the user handler keeps the C++ "return false to unregister" contract.
3. Add `EventFailedReason::SubscriptionStateChangeHandlerFailed`.

### 6.2 FFI bridge (`com-api-ffi-lola`)

- Trait: `get_subscription_state -> u8`, `set_subscription_state_change_handler(&FatPtr) -> bool`,
  `unset_subscription_state_change_handler -> bool` (raw `u8` keeps `bridge_ffi_rs` free of a
  `score_com_concept` dependency; no BUILD change).
- `LolaFFIBridge`: declare the three C++ functions and add the trampoline
  `mw_com_impl_call_dyn_ref_fnmut_subscription_state(ptr, u8) -> bool` (transmutes the `FatPtr`
  back to `&mut dyn FnMut(u8) -> bool`, `catch_unwind` → abort like the existing trampolines).
- `bridge_ffi_mock`: add the three methods to `mock!` and forward them in `SharedMockBridge`.

### 6.3 C++ bridge (`registry_bridge_macro.*`)

- Add `RustBoxedCallable<bool, SubscriptionState>` (invoke → trampoline; dispose →
  `mw_com_impl_delete_boxed_fnmut`, reusing the existing box-drop path).
- Add `mw_com_proxy_event_get_subscription_state`,
  `mw_com_proxy_event_set_subscription_state_change_handler` (wraps
  `RustFnMutCallable<RustBoxedCallable, bool, SubscriptionState>` into the
  `score::cpp::callback<bool(SubscriptionState)>` exactly as the receive-handler wrapper does),
  and `mw_com_proxy_event_unset_subscription_state_change_handler`.

### 6.4 LoLa runtime (`consumer.rs`)

- Add `subscription_state_handler_set: AtomicBool` to `LolaSubscriberImpl`; init `false` in
  `subscribe`.
- Implement the three trait methods. `set` boxes the handler as
  `Box<dyn FnMut(u8) -> bool + Send + 'static>` (typed→raw adapter maps `u8` to
  `SubscriptionState`), converts to `FatPtr`, calls the FFI. On `false` (null-pointer rejection
  only, since C++ never consumes the handler in that path) it reclaims the box; otherwise it marks
  the flag. All event access goes through the existing `ProxyEventManager` guard, preserving the
  "no concurrent access to one event" rule.
- `Drop`: if the flag is set, call the raw bridge unset **before** `unsubscribe_to_event` so the
  handler cannot fire during teardown; then keep the existing receive-handler clear + unsubscribe.
- `unset` calls the FFI and clears the flag.

### 6.5 Mock runtime

- `MockSubscriberImpl`: implement `get_subscription_state` → `NotSubscribed`,
  `set`/`unset` → `Ok(())` (in-memory test double; no native callback machinery).

### 6.6 Docs

- Add a "Subscription State Query and Change Notification" section to
  `score/mw/com/rust/doc/user_facing_api_examples.md` (sync query, async registration, return
  `false` to unregister, reentrancy warning) and note the API in the design doc feature table.

### 6.7 BUILD impact

None expected: no new crate dependency is introduced (`u8`/`bool` at the FFI seam; `score_log`,
`futures`, `score_com_concept` already present). Tests are added to the existing
`com-api-runtime-lola-tests` target, which already depends on `bridge_ffi_mock` + `mockall`.

## 7. Obligations and coverage

| # | Obligation | Source | Disposition |
| --- | --- | --- | --- |
| O1 | Sync state query returns current C++ state | proxy_event_base.h L90 | implemented in proposal |
| O2 | Async change notification registered/unregistered | proxy_event_base.h L110/L117 | implemented in proposal |
| O3 | `false` return unregisters handler | subscription_state_change_handler.h L30-32 | implemented (bool return preserved) |
| O4 | Handler may run under lock; no reentrant same-event calls | handler header L24-28 | documented + guarded |
| O5 | Overriding registration silently replaces | header L107 | FFI re-register replaces |
| O6 | After unset, handler never called | header L114-116 | C++ binding guarantee + Drop unset |
| O7 | Lifetime: handler `Send + 'static`; box freed exactly once | ownership trace | proposed; needs native test |
| O8 | Teardown must not invoke handler after drop | Drop ordering | proposed; needs native test |
| O9 | Mock runtime stay compilable | runtime-mock | implemented |
| O10 | Docs/examples compiled where not `ignore` | docs obligation | proposed |
| O11 | No new lint/format/CI exceptions | SKILL | preserved (no suppress added) |
| O12 | Integration coverage on real service transitions | issue-type "concurrency/async" | **open** (not added) |

## 8. Open / unknown items (must remain open)

1. **Design placement** — the C++ API lives on the event object, which exists before `Subscribe`.
   In Rust the event is created by `Subscriber::subscribe`, so the proposal places the API on
   `Subscription`. Placing `get_subscription_state` on `Subscriber` too is a plausible alternative
   that is **not decided here**; it needs the owning design/API decision.
2. **Integration test scenario** — no native end-to-end test exercising a real
   provider-offer/stop-offer state transition is added; O12 stays open.
3. **Native evidence** — `native-check-summary.json` is missing and no check was executed.
4. **Upstream activity** — linked PRs/commits for #560 were not retrievable; reuse history unknown.
5. **`binding_ == nullptr`** — C++ `ProxyEventBase::SetSubscriptionStateChangeHandler` dereferences
   `binding_`; the Rust FFI can only obtain a valid event from a successfully created proxy, but
   this precondition is asserted by C++, not enforced newly here.
6. **Unknown raw enum value** — mapped conservatively to `NotSubscribed`; strict error signalling
   is not available through the C++ infallible signature.
7. **QNX** — out of scope per task ("No QNX task/execution"); the new methods must not introduce
   Linux-only Rust constructs beyond the existing target-compatibility tags.
