# Supervisor review (resumed) — issue eclipse-score/communication#560

**Issue**: "Improvement: Add Subscription State Change APIs Support on Rust API Lib"
(`rust-api`, type `Product Increment`, state `open`, 0 comments).
**Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (`.rust-queue/context/task.json`).
**Mode**: `implementation`; Linux only; no QNX. **Tool boundary**: file tools only — no native
command was executed by this review; raw evidence is read from
`.rust-queue/reports/native-check-summary.json`. **Only file written**: this report.
**Review scope**: independent read-only review of the *resumed* patch (correction 2 / measured
attempt 2), `correction-2.md`, `scope.md`, `implementation.md`, `check-plan.json`, the applied
source, and the bounded measured results. `supervisor-prior.md` (attempt-0/`fix1` failure) and the
pre-measurement `implementation.md` / `review-packet.md` are treated as **history, not current**.

---

## 1. Disposition (summary)

| Field | Value |
| --- | --- |
| Technical completion (patch) | **Measured build/test/lint/docs pass** for the enumerated checks (attempt 2) |
| Measured native outcome | **PASSED** (`attempt: 2`, `kind: measured_native_command`, `exit_code: 0`, `passed: true`) |
| Engineering acceptance | **PENDING** — `engineering_acceptance: "pending"`; no authorized human decision |
| New-callback end-to-end runtime | **NOT exercised** by any executed target (see §4) |
| Report class | Independent read-only review of a resumed patch whose bounded native run passed |
| Recommended disposition | Continue to offline human review of the design/lifetime proposals; do **not** mark qualified/accepted |

The prior `supervisor-prior.md` correctly recorded a hard compile blocker (E0596 at
`consumer.rs`, attempt 0) and "not reached". That evidence is retained as history. Correction 2 fixed
the measured defect and added typed-disposal symmetry; the bounded attempt-2 run now passes. The
issue is **not** qualified or accepted: several ownership/threading/integration obligations remain
open and unproven, and the human decisions are offline.

---

## 2. Measured evidence actually obtained (attempt 2)

Source: `.rust-queue/reports/native-check-summary.json` (present, attempt 2).

- `measured_subject_hashes_sha256`: `003291e718b3c937af1b0b28d7ae91c4d1b602f942ed37fbd55b8cd9acfc98e6`
- `native_result.sha256`: `66c022590bd956a8b12a658b53071051129c41e296bcf744fd951d079c71bf0e`
  (`.../jobs/560/execution/check-2/native-result.json`)
- `exit_code`: `0`; `passed`: `true`; `infrastructure_error`: `null`; `engineering_acceptance`: `pending`

Every enumerated `check-plan.json` obligation kind was executed:

| # | kind | targets | exit | result |
| --- | --- | --- | --- | --- |
| 1 | build | 11 (`score_com_concept`, `score_com`, `score_com_mock`, `com-api-runtime-lola`, `com-api-runtime-mock`, `bridge_ffi_rs`, `bridge_ffi_lola`, `bridge_ffi_mock`, `registry_bridge_macro_cpp`, `bigdata-consumer`, `bigdata-consumer-async`) | 0 | passed (1345 actions) |
| 2 | test | 10 (Rust mock unit tests, concept/macro tests, 5 C++ state-machine/proxy tests, 2 integration tests) | 0 | **10 / 10 passed** |
| 3 | doctest | 2 (`com-api-runtime-lola-doc-tests`, `score_com_concept-macros-tests`) | 0 | passed |
| 4 | lint (clippy) | 5 Rust libs | 0 | passed; 2 pre-existing warnings in `consumer.rs` (1027, 1241) + 1 in `bridge_ffi.rs` (283) |
| 5 | lint (clang-tidy) | `registry_bridge_macro_cpp` | 0 | passed |
| 6 | query | `score_com`, `score_com_concept` | 0 | passed |

The clippy warnings are in pre-existing lines (find-service transmute, `clone_on_copy`,
`result_unit_err`), **not** in the new subscription-state code; the lint check is exit 0 and no
suppression was added.

**Preserved failure history:** attempt 0 failed to build (`error[E0596]: cannot borrow 'handler' as
mutable` at the old `consumer.rs:724`); `fix1` is recorded failed. That failure is retained in
`supervisor-prior.md`; the current summary supersedes it with attempt 2, and `engineering_acceptance`
remains `pending` — no result was upgraded, invented, or marked accepted.

---

## 3. Independent source review — required axes

Patch surface re-read (bounded reads): `score_com_concept/{concept,error}.rs`, `score_com.rs`,
`com-api-ffi-lola/{bridge_ffi,bridge_ffi_lola,bridge_ffi_mock}.rs`,
`com-api-ffi-lola/registry_bridge_macro.{h,cpp}`, `com-api-runtime-lola/consumer.rs`,
`com-api-runtime-mock/runtime.rs`, the two changed docs.

### 3.1 Sync query (`GetSubscriptionState`)
- `SubscriptionState` (`#[repr(u8)]`, 0/1/2) + `From<u8>` at `concept.rs:64-97`; trait method at
  `concept.rs:968-972`; LoLa impl `consumer.rs:708-717` acquires the existing `ProxyEventManager`
  guard and returns the mapped value. The C++ enum (`subscription_state.h`, `SWS_CM_00310`) has the
  same discriminants; the C++ wrapper `registry_bridge_macro.cpp:385-392` returns `kNotSubscribed`
  for a null event. **Consistent.**

### 3.2 Mutable callbacks
- `set_subscription_state_change_handler(&self, mut handler: impl FnMut(SubscriptionState) -> bool
  + Send + 'static)` at `consumer.rs:719-750`. The `move` adapter invokes the captured handler as
  `FnMut`; the `mut handler` binding is the correction-2 fix for the measured E0596. The handler is
  boxed as `Box<dyn FnMut(u8) -> bool + Send + 'static>`. Captured-state mutation is pinned by
  `test_handler_observed_mapped_state_and_mutated_capture`. **Correct.**

### 3.3 State mapping
- `From<u8>` maps `0 → Subscribed`, `2 → SubscriptionPending`, and `1` or any out-of-contract value
  `→ NotSubscribed` (`concept.rs:83-97`). The C++ signature is infallible, so no error channel
  exists; unknown-value behaviour is a deliberate conservative mapping (open design item). Unit test
  `test_get_subscription_state_maps_raw_values` covers 0/1/2/255. **Consistent with the C++ enum.**

### 3.4 Cancellation (`false` return)
- The user `bool` return is preserved through `RustBoxedCallable<bool, SubscriptionState>::invoke`
  (`registry_bridge_macro.h:212-225`) and the trampoline returns it to the middleware
  (`bridge_ffi_lola.rs:140-163`). `test_handler_false_return_signals_cancellation` proves the adapter
  propagates `false`. The decision to unregister on `false` is the **C++ state machine's** and is
  covered only by the existing C++ `subscription_state_machine_*` tests, not by the Rust mock tests.
  **Surface correct; Rust runtime behaviour of the unregister decision untested.**

### 3.5 Ownership / single disposal
- Box created by `Box::into_raw`; on `false` the Rust side reclaims (`Box::from_raw`) because the
  C++ wrapper returns `false` only for a null argument before taking the callable
  (`registry_bridge_macro.cpp:398-408`). On success ownership transfers; disposal is via the **typed**
  dropper `mw_com_impl_delete_boxed_fnmut_subscription_state` (`bridge_ffi_lola.rs:176-180`) which
  reconstructs the *same* trait-object type as the box/invoke sites. Tests pin single disposal:
  `test_set_and_unset_disposes_captured_resource_exactly_once`,
  `test_set_handler_failure_drops_captured_resource`,
  `test_drop_unregisters_before_unsubscribe_and_disposes_once`. The correction-2 G2 asymmetry
  (invoke without `+ Send`) is **fixed** — invoke, box and dispose now use the identical type.
  **Sound for the current wrapper/LoLa contract, but see G3 (unguarded latent double-free).**

### 3.6 Unset / teardown / reentrancy
- `unset_subscription_state_change_handler` (`consumer.rs:752-766`) calls the FFI and clears the
  `subscription_state_handler_set` flag. `Drop` (`consumer.rs:498-528`) releases the receive handler,
  then unregisters the state handler **before** `unsubscribe_to_event` (flag-gated, single guard).
  Test `test_drop_unregisters_before_unsubscribe_and_disposes_once` asserts order
  `["unset","unsubscribe"]`. Reentrancy (handler must not call back into the same event) is a
  **documented contract** on the trait (`concept.rs:974-991`) and in the user doc; it is not
  enforced — a breach can deadlock on the C++ state-machine lock, and a panic is turned into
  `std::process::abort()` by the trampoline. **Not tested; open.**

### 3.7 Thread guarantees
- The handler is `Send + 'static`; it may be invoked from a middleware thread. The trampoline
  `catch_unwind`s and aborts rather than unwinding across FFI. The flag uses `Acquire`/`Release`
  atomics; because `set`/`unset`/`Drop`/receive all serialise through the single `ProxyEventManager`
  guard, the atomic ordering is defensive rather than load-bearing. There is **no proof** that the
  middleware never invokes the handler concurrently and no concurrency/stress test on the Rust side;
  the existing C++ `subscription_state_machine_stress_test` passes but is explicitly recorded as
  supplementary, not absence-of-race evidence.

### 3.8 FFI ABI / trait-object symmetry
- Rust extern decls (`bridge_ffi_lola.rs:434-456`) match the C++ signatures in
  `registry_bridge_macro.h:151-166` (`const FatPtr*`, `std::uint8_t`, `bool`, `noexcept`). The C++
  `RustFnMutCallable` move semantics null the moved-from `FatPtr.data`, so the temporary destructor
  does not double-dispose; the typed deleter matches the box. **ABI/ownership shape is consistent
  with the existing receive-handler pattern and compiled/linked in attempt 2.**

---

## 4. Test coverage — what each category actually proves

| Category | Executed evidence | What it proves |
| --- | --- | --- |
| **Rust/FFI mock unit tests** (`com-api-runtime-lola-tests`, passed) | 6 subscription-state tests + helpers (`consumer.rs:1493-1852`) over `MockFFIBridge` | Rust-side contract: raw→typed mapping, `FnMut` capture mutation, `false` propagation, failure reclaim, explicit-unset single disposal, teardown order. They reconstruct and dispose the **same trait-object type** the production trampoline uses, but the mock bridge is an inert double. |
| **Existing C++ state-machine tests** (`subscription_state_machine_{methods,events,states,stress}_test`, `proxy_event_subscription_test`, passed) | C++ middleware | Legal state transitions, override, unset-never-called-again, `false` unregister at the **C++** layer. They do **not** cross the Rust FFI trampoline. |
| **Unchanged consumer integration flows** (`test_com_api_sync`, `test_com_api_async`, passed) | End-to-end producer/consumer binaries | That the pre-existing receive/async flows still work after the public-API extension. They **do not call** any new subscription-state API. |
| **Actual new-callback integration** | **NONE** | The real `mw_com_proxy_event_set_subscription_state_change_handler` → `RustBoxedCallable<bool, SubscriptionState>` → `mw_com_impl_call_dyn_ref_fnmut_subscription_state` path is compiled/linked (build/lint passed) but **never invoked at runtime** by any executed target. O12 / G8 stays open. |

---

## 5. Omissions and open gaps (must remain open)

Numbering continues `supervisor-prior.md`; G1/G2 are closed by correction 2.

1. **G3 (latent double-free, unguarded).** If a future binding ever returns an error *after*
   consuming the by-value callback, the C++ temporary destructor disposes the box and Rust then frees
   it again. True for the current wrapper/LoLa binding (always success), so unreachable today, but
   the reclaim relies on an **unproven** "false ⇒ no ownership transfer" contract. Not guarded.
2. **G4 (`binding_ == nullptr`).** Asserted by the middleware, not newly enforced by Rust.
3. **G5 (reentrancy).** Documented deadlock/abort hazard; not enforced and not tested.
4. **G6 (`false`-then-teardown stale flag).** After a `false` self-unregister, C++ disposes but the
   Rust `AtomicBool` stays `true`, so `Drop` issues a redundant `unset`. Harmless in the mock, not
   proven harmless against the real middleware; untested.
5. **G7 (second `set` override).** Re-registration silently replaces/disposes in C++; the Rust flag
   stays `true`. No test covers override disposal of the old box.
6. **G8 / O12 (no real new-callback integration).** See §4. No provider stop-offer / re-offer
   transition test exercises the real trampoline.
7. **G10 (mock-runtime tests not built).** `com-api-runtime-mock`'s `#[cfg(test)] mod test` is not
   built by any test target (pre-existing); the new mock methods are only library-compiled.
8. **Test code is not linted.** The clippy aspect runs on library targets; the new `#[cfg(test)]`
   module (and its `unsafe` test helpers) is not clippy-covered. Not a regression, but the lint pass
   does not cover it.
9. **Docs are not compiled.** The new snippets live in `doc/user_facing_api_examples.md` (markdown,
   not `include_str!`-ed into rustdoc), so O10 is "documented, not compiled"; the `ignore` blocks in
   `score_com.rs` likewise add no coverage.
10. **Query is label-only.** The `query` check enumerated two explicit labels; reverse dependencies
    and the full trait-implementor set were not measured. The `com-api-example` crate is not in the
    build list (it uses, but does not implement, `Subscription`).
11. **`check-plan.json` reason text is stale (documentation, not a dropped obligation).** It still
    names the attempt-1 tests `test_set_and_unset_subscription_state_change_handler`,
    `test_set_handler_failure_is_reported_and_box_reclaimed`,
    `test_drop_unregisters_registered_state_handler`, which correction 2 renamed (and it does not name
    `test_handler_observed_mapped_state_and_mutated_capture` /
    `test_handler_false_return_signals_cancellation`). Targets/obligations are unchanged; only the
    descriptive names lag. `implementation.md`/`review-packet.md` similarly describe the attempt-1
    test set and remain history.
12. **Upstream activity** (linked PRs/comments) remains unretrieved (no network tool).

### Trace / policy — preserved (no violation found)
Licenses/headers preserved on all touched files; no BUILD, dependency, toolchain pin, feature set,
requirement ID, or lint-profile change; `SWS_CM_00310` reused, no new IDs; no suppression added; no
QNX target touched; the documented typed-dropper deviation (`implementation.md` §5) is present in
source and is the correct vtable-symmetry choice.

---

## 6. Failed / missing evidence preserved

| Evidence | Status | Treatment |
| --- | --- | --- |
| attempt-0 build (`check-0`) E0596 | **FAILED (history)** | retained in `supervisor-prior.md`; not overwritten |
| `fix1` stage | **failed (history)** | retained |
| attempt-2 build/test/doctest/lint/query | **present, PASSED** | quoted in §2 from `native-check-summary.json` |
| real Rust↔C++ subscription-state callback invocation | **missing (not exercised)** | recorded as unrun, not passed |
| reentrancy / concurrency on the Rust handler | **missing (not tested)** | recorded |
| upstream issue/PR timeline | **not retrieved** | recorded |
| tool/toolchain qualification hashes | **not carried** in the summary | qualification pending |

No native result is invented, upgraded, or marked accepted.

---

## 7. Pending native trace / qualification / human decisions

- **Qualification**: no Ferrocene/toolchain hashes, no environment binding, and no qualification
  evidence are in `native-check-summary.json`; the bounded logs are execution evidence, not
  qualification. Do not mark qualified.
- **Human engineering acceptance is offline and pending.** Proposed decisions still awaiting an
  authorized human (unchanged, still proposals):
  1. API placement on `Subscription` rather than also on `Subscriber`;
  2. `get_subscription_state()` infallible, unknown raw value → `NotSubscribed`;
  3. raw `u8`/`bool` at the `FFIBridge` seam;
  4. `Drop` unregisters the state handler before `unsubscribe`;
  5. dedicated typed dropper instead of reusing the `dyn FnMut()` deleter.

---

## 8. Concrete next action (authorized operator)

1. Add at least one test that exercises the **real** Rust→C++→Rust callback path (a provider
   stop-offer / re-offer transition through `mw_com_proxy_event_set_subscription_state_change_handler`
   and the trampoline) to close O12/G8.
2. Decide or guard the `false ⇒ no ownership transfer` assumption (G3) and the reentrancy contract
   (G5); add a `false`-self-unregister + teardown and a second-`set` override test (G6/G7).
3. Refresh the stale descriptive test names in `check-plan.json` (G11) so the plan matches the
   current `correction-2.md` test set.
4. Obtain the five design/lifetime decisions in §7 from authorized humans. Tests and clean analyzers
   cannot supply them.

Until then the issue is **not implemented to acceptance, not qualified, and not accepted**.

> This supervisor report is an independent, offline, read-only assessment. It grants no authority to
> comment, publish, merge or release, and it marks no native work product qualified or accepted.

---

### Review manifest
- Reviewed inputs: `.rust-queue/context/{task,issue,comments}.json`;
  `score-rust-workflow/SKILL.md`, `references/native-verification.md`;
  `.rust-queue/reports/{scope,implementation,correction-2,review-packet,check-plan,native-check-summary,supervisor-prior}.json|md` and `probe.txt`;
  the changed source listed in §3 plus `score_com_concept/lib.rs`, `com-api-runtime-lola/lib.rs`,
  `consumer.rs` (test module), and the two changed docs. No `AGENTS.md` present; no `correction-3.md`.
- Authority: file tools only; no shell, delegation, publication, or acceptance performed.
- Failures preserved: attempt-0/`fix1` (history); all unexercised obligations recorded as missing.
- Report location: `.rust-queue/reports/supervisor.md` (the only file written).
