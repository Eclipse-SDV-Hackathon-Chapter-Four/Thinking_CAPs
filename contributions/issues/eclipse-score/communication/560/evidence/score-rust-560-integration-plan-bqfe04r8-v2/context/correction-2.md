# Source correction 2 — issue eclipse-score/communication#560

**Issue**: "Improvement: Add Subscription State Change APIs Support on Rust API Lib"
(`rust-api`, `Product Increment`, state `open`).
**Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
**Mode**: implementation, Linux only, no QNX. **Tool boundary**: file tools only; `shell`,
`grep`, delegation and measurement are refused in this workspace, so no native command was
executed here and no native result is claimed.
**Correction budget**: this is source correction **2 of lifetime max 3**. Correction 1 failed
transport and still counts; the budget is neither reset nor repeated.

This file is the authoritative record for the current correction. `implementation.md` and
`review-packet.md` predate the measured `check-0` failure and are preserved as history only;
`supervisor-prior.md` records the failed measurement. Neither is superseded by deletion.

---

## 1. Measured defect being corrected

`native-check-summary.json` (`attempt: 0`, `passed: false`, `engineering_acceptance: pending`)
retains the only executed native evidence: two build checks, the second failing with

```
error[E0596]: cannot borrow `handler` as mutable, as it is not declared as mutable
   --> score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs:724:54
```

The failing target was `//score/mw/com/rust:score_com` (which depends on
`com-api-runtime-lola`); the failing crate was
`//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola`. This is a real
source defect, not flakiness.

## 2. Actual changed paths in this correction

| # | Path | Change |
| --- | --- | --- |
| 1 | `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs` | `set_subscription_state_change_handler`: `handler` binding is now `mut handler` so the `move` adapter can invoke it as `FnMut` (fixes measured E0596). Test module: added handler capture/invoke/dispose helpers and `DropCounter`/`SendFatPtr` test-support types; `make_subscribed` now takes a teardown-order log and records the `unsubscribe` call; four tests were corrected and three new tests added (see §4). |
| 2 | `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_lola.rs` | `mw_com_impl_call_dyn_ref_fnmut_subscription_state` now reconstructs the handler as `*mut (dyn FnMut(u8) -> bool + Send + 'static)` — the same trait-object type used at the boxing site (`consumer.rs`) and by `mw_com_impl_delete_boxed_fnmut_subscription_state` — instead of the `Send`-less `&mut dyn FnMut(u8) -> bool`. |

**No BUILD, dependency, toolchain-pin, licence, lint-profile, requirement-ID or C++ change.**
The public `FFIBridge` surface, the C++ wrappers and the typed dropper are untouched; the C++
`RustBoxedCallable<bool, SubscriptionState>` contract still matches the box/invoke/drop type.

## 3. Rationale

1. **E0596 (blocking, measured).** `let adapted = move |raw: u8| -> bool { handler(...) }` invokes
   the captured handler through `FnMut`, so the binding must be mutable. The compiler's own
   suggestion (`mut handler`) is applied. This is the single cause of the measured failure; the
   crate and its dependents (`score_com`, LoLa tests, downstream binaries) could not compile.
2. **FatPtr ownership / vtable symmetry (supervisor G2).** A value boxed as
   `Box<dyn FnMut(u8) -> bool + Send + 'static>` must be invoked and dropped through the *same*
   trait-object type. The dispose trampoline already used `+ Send + 'static`; the invoke
   trampoline did not. Using a different trait-object type for the same allocation is not
   guaranteed by the language, so the invoke site now matches the box/dispose sites. The receive
   handler trampoline (`mw_com_impl_call_dyn_fnmut`) already matches its box type, so this aligns
   the new code with the existing correct pattern.

## 4. Regression coverage added (native: `com-api-runtime-lola-tests`)

All tests run through `MockFFIBridge`; the handler pointer is recorded at the FFI seam and is
reconstructed/invoked/dropped by the test harness using the exact production trait-object type.
A successful mock "set" **no longer leaks** the owned box: the recorded pointer is disposed
exactly once, either by the explicit-unset mock (which models the C++ middleware disposing the
callback it owns) or by the teardown mock. No test disposes a box twice.

| Test | Axis covered |
| --- | --- |
| `test_get_subscription_state_maps_raw_values` | Raw-state mapping for the sync query (0/1/2/255). |
| `test_handler_observed_mapped_state_and_mutated_capture` | **FnMut captured-state mutation** + **raw-state mapping**: raw `2` is delivered as `SubscriptionPending`, raw `7` (out of contract) as `NotSubscribed`; the captured `Vec` observes both in order. |
| `test_handler_false_return_signals_cancellation` | **Callback false return / cancellation**: the adapter/trampoline propagates `false`. (The unregister-on-false decision itself is the C++ state machine's; see gaps.) |
| `test_set_handler_failure_drops_captured_resource` | **Registration failure dropping captured resources**: on `false`, the runtime reclaims the box and the captured `DropCounter` is dropped exactly once. This pins the documented `false ⇒ no ownership transfer` contract for the only false case the C++ wrapper can produce (null argument; Rust never passes null). |
| `test_set_and_unset_disposes_captured_resource_exactly_once` | **Explicit unset / single disposal**: explicit `unset` disposes the resource once; a subsequent `Drop` does not unset again (`times(1)`). |
| `test_drop_unregisters_before_unsubscribe_and_disposes_once` | **Teardown order + single disposal**: recorded order is exactly `["unset", "unsubscribe"]`; the handler is disposed exactly once. |

The two existing tests were renamed to match their strengthened bodies
(`test_handler_observed_mapped_state_and_mutated_capture`,
`test_drop_unregisters_before_unsubscribe_and_disposes_once`); no obligation was removed.

## 5. Ownership / concurrency statements (not over-claimed)

- The tests exercise the Rust-side contract with real trait-object reconstruction, not the actual
  `mw_com_impl_*` trampoline symbols (they are private to `bridge_ffi_lola`, which the test target
  does not depend on). The invoke/dispose helpers are byte-for-byte the same reconstruction the
  trampoline performs.
- `false ⇒ no ownership transfer` is source-backed: the C++ wrapper
  (`mw_com_proxy_event_set_subscription_state_change_handler`) returns `false` only when
  `event_ptr == nullptr || boxed_handler == nullptr`, before constructing/taking the callable.
  The Rust side always passes non-null, and the LoLa binding
  (`bindings/lola/proxy_event.cpp:155-165`) always returns success. The reclaim path remains a
  contract, not a runtime assertion (see gaps).
- Reentrancy, cross-thread handler invocation and real provider state transitions are **not**
  exercised here. No test claims they prove safety.

## 6. Preserved evidence and prior checks

- `native-check-summary.json` is **untouched**: the failed `check-0` build evidence and
  `engineering_acceptance: pending` remain exactly as measured. No result was upgraded, invented
  or marked passed.
- `check-plan.json` obligations are **preserved in full and unchanged**. Native labels were
  re-verified against the baseline BUILD files:
  `//score/mw/com/rust:score_com` and `:score_com_mock`
  (`score/mw/com/rust/BUILD`); `score_com_concept`, `score_com_concept-test`,
  `score_com_concept-macros-tests`, `score_com_concept-macros-unit-tests`
  (`score_com_concept/BUILD`); `com-api-runtime-lola` + `com-api-runtime-lola-tests`
  (`com-api-runtime-lola/BUILD`); `bridge_ffi_rs`, `bridge_ffi_lola`, `bridge_ffi_mock`,
  `registry_bridge_macro_cpp` (`com-api-ffi-lola/BUILD`); `proxy_event_subscription_test`,
  `subscription_state_machine_{events,methods,states,stress}_test`
  (`impl/bindings/lola/BUILD`); `bigdata-consumer` + `test_com_api_sync`
  (`consumer_sync_apis/.../BUILD`); `test_com_api_async`
  (`consumer_async_apis/integration_test/BUILD`). No obligation was dropped to obtain a passing
  check; the query entry still enumerates only explicit labels.
- `scope.md`, `implementation.md`, `review-packet.md`, `supervisor-prior.md` and `probe.txt` are
  retained unchanged as history.

## 7. Open gaps (must remain open)

1. **No native evidence in this correction.** Shell/measurement are denied in this workspace, so
   the corrected build, the new tests, C++ contract tests, docs, lint and downstream builds were
   **not executed here**. Only the earlier failed `check-0` is measured; `fix1` remains failed.
2. **Reentrancy / concurrency untested.** The "handler may run under the state-machine lock and
   must not call back into the same event" rule is a documented contract; nothing enforces it. A
   user breach can deadlock or abort (panic-to-abort in the trampoline). Neither the new tests nor
   any native run proves absence of races/deadlocks.
3. **Production integration untested.** No end-to-end provider stop-offer / re-offer transition
   test exercises the real C++ `SetSubscriptionStateChangeHandler` through the FFI trampoline;
   O12 stays open.
4. **`false`-then-teardown stale flag (G6).** If a handler returns `false`, C++ unregisters it but
   the Rust `AtomicBool` stays `true`, so `Drop` issues a redundant `unset`. Untested here.
5. **Second `set` override (G7).** Re-registration silently replaces in C++ (disposing the old
   callback); the Rust flag stays `true`. Not covered by a test.
6. **Ownership guard (G3).** The reclaim-on-`false` path assumes "false ⇒ the middleware did not
   take ownership". True for the current wrapper/LoLa binding; a future binding that errors after
   consuming the by-value callback would double-free. Unreachable today; not guarded.
7. **`binding_ == nullptr` (G4)** is asserted by the middleware, not newly enforced by Rust.
8. **Unknown raw state value** is mapped to `NotSubscribed` because the C++ signature is
   infallible; no error channel exists.
9. **Mock runtime** `set`/`unset` are inert doubles; the `com-api-runtime-mock` `#[cfg(test)]`
   module is not built by any test target (pre-existing, G10).
10. **Upstream activity** (linked PRs/comments) remains unretrieved; no network tool.
11. **Engineering acceptance is offline and pending.** No authorized human decision has been
    recorded; deterministic tools cannot supply it.

## 8. Concrete next action (authorized operator)

In a disposable Linux checkout of `381d43d` with this patch applied, run the enumerated
`check-plan.json` obligations under the native Ferrocene/Linux configuration — first the build
targets `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` and
`//score/mw/com/rust:score_com`, then `com-api-runtime-lola-tests`, then the C++ state-machine and
`proxy_event_subscription_test` targets, docs and lint — and return the raw logs with exit codes
and subject hashes. Human reviewers then decide the placement/ownership/lifetime proposals. Until
then this issue is **not implemented, not qualified and not accepted**.

> This correction report is an offline, bounded engineering change record. It grants no authority
> to comment, publish, merge or release, and marks no native work product qualified or accepted.
