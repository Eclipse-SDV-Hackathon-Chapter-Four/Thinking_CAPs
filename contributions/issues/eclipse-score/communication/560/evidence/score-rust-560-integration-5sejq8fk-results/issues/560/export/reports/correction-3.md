# Source correction 3 — issue eclipse-score/communication#560

**Issue**: "Improvement: Add Subscription State Change APIs Support on Rust API Lib"
(`rust-api`, `Product Increment`, state `open`).
**Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
**Mode**: implementation, Linux only, no QNX. **Tool boundary**: file tools only; `shell`, `grep`,
delegation and native measurement are refused in this workspace, so **no native command was
executed here and no native result is claimed**.
**Correction budget**: this is source correction **3 of lifetime max 3**, the final attempt.
Correction 1 failed transport and still counts; correction 2 fixed the measured build defect and
its bounded native run passed. The budget is neither reset nor repeated; no fourth correction is
authorized.

This file is the authoritative record for the current correction. `implementation.md`,
`review-packet.md`, `scope.md`, `supervisor-prior.md`, `correction-2.md`,
`check-plan.json`, `native-check-summary.json` and the carried summaries are **preserved
unchanged** as history/plan and were not edited.

---

## 1. Scope of this correction

Correction 2 closed the measured Rust-side defect and the library/mock contract. The supervisor
report for that run left the production path open:

- **G8 / O12** — no executed target ever invoked the real
  `mw_com_proxy_event_set_subscription_state_change_handler` -> `RustBoxedCallable<bool,
  SubscriptionState>` -> Rust trampoline path at runtime.
- **G6** — a `false`-returning handler followed by teardown was untested.
- **G7** — a second `set` (silent replacement) was untested.

This correction adds a dedicated, Linux-only production integration package that exercises the
real LoLa runtime and the generated C++ registration through a two-process (controller + provider
child) scenario harness. It adds **no** production-source change: existing library sources
(including correction 2's `consumer.rs` / `bridge_ffi_lola.rs` fixes already present at this
baseline) are untouched.

## 2. Actual new paths in this correction

| # | Path | Content |
| --- | --- | --- |
| 1 | `score/mw/com/test/basic_rust_api/subscription_state_apis/BUILD` | `rust_binary(name = "subscription-state-apis")` (deps `//score/mw/com/rust:score_com`, `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`, `link_std_cpp_lib`, preserved Linux `-no-pie`/`-lstdc++` flags) plus `pkg_application(name = "subscription-state-apis-pkg", app_name = "subscription-state-apis")` packaging the binary and the existing `etc/config.json` + `bigdata/logging.json`. |
| 2 | `score/mw/com/test/basic_rust_api/subscription_state_apis/subscription_state_app.rs` | Single Rust binary with controller (default) and provider-child (`--provider`) roles, the prefixed/phase-tagged protocol, deadline-bounded reads, owned child cleanup and the five cases. |
| 3 | `score/mw/com/test/basic_rust_api/subscription_state_apis/integration_test/BUILD` | `integration_test(name = "test_subscription_state_apis", ...)` over the existing Linux Docker fixture, constrained to `@platforms//os:linux` + `@platforms//cpu:x86_64`. |
| 4 | `score/mw/com/test/basic_rust_api/subscription_state_apis/integration_test/test_subscription_state_apis.py` | pytest wrapper with the five named cases; each case launches one fresh controller process (which spawns its own provider child). |

**No BUILD, dependency, toolchain-pin, feature, license, lint-profile, requirement-ID or C++ source
change outside the new package.** `check-plan.json` obligations are preserved in full and
unchanged; exactly the two new labels it already lists are declared:
`//score/mw/com/test/basic_rust_api/subscription_state_apis:subscription-state-apis` and
`//score/mw/com/test/basic_rust_api/subscription_state_apis/integration_test:test_subscription_state_apis`.

## 3. Source-derived design decisions

All decisions below are derived from the inspected baseline sources (`score/mw/com/impl/...`,
`score/mw/com/rust/...`), including the copies bound under
`.rust-queue/context/integration-plan/context/native/`:

1. **Registration promises no initial callback.** `SubscriptionStateMachine::SetSubscriptionStateChangeHandler`
   only stores the handler under `state_mutex_` and never invokes it. The controller therefore
   establishes the initial `Subscribed` state through the synchronous query *before* registering a
   handler (and never waits for an initial notification).
2. **Withdrawal drives the auto-reconnect transition.** `SubscribedState::StopOfferEvent()` sets the
   instance unavailable and calls `TransitionToState(SUBSCRIPTION_PENDING_STATE)`;
   `SubscriptionPendingState::ReOfferEvent()` returns to `SUBSCRIBED_STATE`. `TransitionToState`
   invokes the stored handler with the new public state, so `WITHDRAW` -> `SubscriptionPending` and
   `OFFER` -> `Subscribed` are the real Rust -> C++ -> Rust observations.
3. **Never withdraw while pending.** `SubscriptionPendingState::StopOfferEvent()` writes `LogFatal`
   and calls `std::terminate()`. The protocol therefore only ever withdraws from a subscribed
   state; after a re-offer the provider is `Subscribed` again before any further withdrawal.
4. **`false` disposes once.** `TransitionToState` resets the handler when the handler returns
   `false`; `UnsetSubscriptionStateChangeHandler` and a replacement `Set...` reset/dispose the
   previous callable. `RustBoxedCallable<bool, SubscriptionState>::dispose` drops the boxed
   closure, which owns the captured `DropProbe`. Disposal is recorded by `DropProbe::drop` exactly
   once.
5. **Callback receipt is not a disposal fence.** The handler sends its observation *before*
   returning, so the controller can receive a callback before C++ disposes it (notably for
   `false`). The `false` case therefore awaits the `DropProbe` destruction atomic and then uses a
   synchronous state query as the fence before re-offer. For replacement/unset, the returning
   native setter/unsetter is the synchronization boundary and the disposal count is snapshotted
   after it returns.
6. **The handler is passive.** It captures a unique handler ID, an unbounded (non-capacity-blocking)
   observation `Sender`, and a `DropProbe`; it performs only atomic reads/increments and a channel
   `send` (failures recorded in a test-owned atomic), never calls back into the subscription, never
   does I/O, never waits and never panics.
7. **Generated C++ registration is linked, not mocked.** The binary depends on
   `bigdata_com_api_gen_rs` (whose `bigdata_com_api_gen_cpp` dependency is `alwayslink`), so the
   `MixedPrimitivesInterface` registration is present and the real LoLa runtime is used. No
   trampoline is called directly and no `bridge_ffi_mock` / `score_com_mock` is linked.
8. **Two runtime processes.** The controller owns its runtime, discovery, consumer and
   subscription and does not move native handles between threads. The provider child owns a separate
   LoLa runtime and the offered producer, and retains the `Producer` returned by `unoffer()` so the
   *same* provider is re-offered (`offer()`/`unoffer()` from the interface macro).
9. **Deadline-bounded, flushed, ordered protocol.** Controller -> provider commands (`OFFER`,
   `WITHDRAW`, `SEND <marker>`, `FINISH`) and provider -> controller acknowledgements are tagged with
   a monotonic phase and a unique `SSAPI-PROTO` prefix. A reader thread forwards every provider
   stdout line through an unbounded channel; the controller uses `recv_timeout`, rejects EOF,
   malformed prefixed lines, phase/command mismatch and provider failure, and retains non-prefixed
   native diagnostics separately. The child stderr is inherited (no unread pipe). On any failure the
   owned child is killed and waited and the reader thread is joined (`ProviderSession::drop`).
10. **Sample hygiene.** `MixedPrimitivesPayload.u32_val` is the generation marker; every received
    sample is released (`pop_front` + drop) before any unoffer/drop, and the test never holds a
    sample across teardown.

## 4. Case-to-obligation mapping

| Pytest case (target `test_subscription_state_apis`) | Scenario | Observation |
| --- | --- | --- |
| `test_subscription_state_notifications` | `notifications` | register retaining handler; WITHDRAW stops the provider; receive real `SubscriptionPending`; verify query; OFFER; receive `Subscribed` on the same subscription; verify query; receive a fresh `0x51` sample; explicit unset -> exactly one disposal. |
| `test_subscription_state_handler_replacement` | `replacement` | set A then B; A disposed exactly once after B returns; WITHDRAW/OFFER under B's phase acknowledgements; B observes pending/subscribed; A never invoked; unset B -> one disposal; drop subscription -> both counts remain one. |
| `test_subscription_state_handler_unset` | `unset` | set A then unset while subscribed -> one disposal; WITHDRAW/OFFER with the handler removed -> no A invocation; register B and drive a callback-observed pending/subscribed cycle; unset B -> one disposal each. |
| `test_subscription_state_handler_false_then_drop` | `false-then-drop` | set A to return `false`; WITHDRAW -> pending observed, A disposed once, pending query; OFFER -> subscribed + fresh `0x77` sample, no further A invocation; drop the same subscription (still-true Rust flag -> redundant native unset then unsubscribe) -> disposal count remains exactly one. |
| `test_subscription_state_handler_drop_active` | `drop-active` | set A on a stable subscribed service and drop the subscription with A still registered -> one disposal, no callback; create a fresh consumer/subscription with positive-control handler B and drive a verified WITHDRAW/OFFER cycle; unset B -> one disposal. |

Each scenario ends by sending `FINISH`, verifying the provider acknowledgement and child exit, and
reporting success. Each pytest case launches a fresh binary/runtime pair so that SHM state or global
runtime state from another scenario cannot satisfy it.

## 5. Structured status

| Field | Value |
| --- | --- |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Correction | 3 of lifetime max 3 (final) |
| Source writes in scope | only `score/mw/com/test/basic_rust_api/subscription_state_apis/` and `.rust-queue/reports/` |
| New/changed paths | 4 new files (§2) |
| Existing production source writes | none |
| Dependency / policy / pin / license changes | none |
| `check-plan.json` | unchanged; all obligations preserved |
| `native-check-summary.json` / carried summaries | unchanged |
| Native checks executed **here** | none (measurement authority not available in this workspace) |
| Claimed native results | none |
| Engineering acceptance | offline, pending |
| QNX | excluded (#1278) |
| Blockers | none for the implementation; see §6 for unmeasured limits |

## 6. Unmeasured limits (must remain open)

1. **No native evidence in this correction.** The new binary was not built, the integration target
   was not run and no lint/format/query check was executed here. Only correction 2's carried build
   and mock-test evidence exists; the production callback path is still **unmeasured**.
2. **Compile inference risk.** The new Rust file was reviewed by reading (ownership, trait bounds,
   lifetimes, protocol state machine), but it was not compiled. Areas flagged for the first native
   build: the generic `S: Subscription<MixedPrimitivesPayload, R>` scenario functions, the
   `discover_and_subscribe -> impl Subscription<...>` return, and inference of the provider's
   `offered`/`unoffered` locals.
3. **Lint applicability.** The native Clippy aspect's exact rule set and whether it analyzes the new
   executable are unmeasured; no suppression was added.
4. **Runtime latency/timing.** The controller uses bounded deadlines (20 ms polls; 30-60 s deadlines)
   but the actual notification latency under Docker is unmeasured.
5. **Python/format checks.** Native Python formatting/lint obligations for the new pytest wrapper
   were not discovered or run.
6. **Platform coverage.** Linux x86_64 only; ARM and QNX are unmeasured.
7. **Native requirement trace.** `SWS_CM_00310` applicability and acceptance remain pending; the
   local scenarios supply no accepted native verification IDs.
8. **Human design decisions.** API placement, infallible unknown-state mapping, `u8`/`bool` FFI seam,
   `Drop` unset-before-unsubscribe ordering and the typed dropper remain proposals awaiting an
   authorized human.

## 7. Concrete next action (authorized operator)

In a disposable Linux checkout of `381d43dec...` with this package added, run the preserved
`check-plan.json` obligations: (1) build
`//score/mw/com/test/basic_rust_api/subscription_state_apis:subscription-state-apis` under
`linux_x64`; (2) execute
`//score/mw/com/test/basic_rust_api/subscription_state_apis/integration_test:test_subscription_state_apis`
uncached through the Linux Docker launcher and require all five cases in the XML with the
WITHDRAW/OFFER phase observations; (3) run the two existing sync/async sample integration targets as
regressions; (4) run the native Clippy aspect on the new binary; (5) repeat the carried
library/test/doctest/query checks whose subjects changed. Return the raw logs with exit codes and
subject hashes. Then obtain the pending human decisions in §6.8.

> This correction report is an offline, bounded engineering change record. It grants no authority
> to comment, publish, merge or release, and marks no native work product qualified or accepted.
