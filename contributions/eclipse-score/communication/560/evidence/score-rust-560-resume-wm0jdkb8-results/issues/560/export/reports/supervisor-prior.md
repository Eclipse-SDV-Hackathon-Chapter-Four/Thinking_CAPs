# Supervisor review — issue eclipse-score/communication#560

**Issue**: "Improvement: Add Subscription State Change APIs Support on Rust API Lib"
(`rust-api`, type `Product Increment`, state `open`).
**Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
**Mode**: `implementation`; Linux only; no QNX.
**Review scope**: read-only independent review of `scope.md`, the applied patch, and the measured
native evidence (`native-check-summary.json` / `check-0`). This report is the only file edited.

---

## 1. Disposition (summary)

| Field | Value |
| --- | --- |
| Technical completion | **Not reached** — the patch does not compile. |
| Measured native outcome | **FAILED** (`check-0`, `kind: measured_native_command`, `passed: false`, exit 1) |
| Engineering acceptance | **pending** — no authorized human decision; tests/clean analyzers cannot supply it |
| Report class | **Design/attempt review with a hard compile blocker — NOT an implemented issue fix** |
| Recommended disposition | **Rework** the patch (see §6); do not carry the current `implementation.md` / `review-packet.md` claims as current |

`implementation.md` and `review-packet.md` were written before any native measurement and state the
patch is "applied in this disposable workspace" with tests added. The measured `check-0` now shows the
patch **fails to build**, so those two documents are **stale relative to measured evidence**. They are
preserved as history (nothing deleted) but must not be read as an implemented fix.

---

## 2. Measured evidence actually obtained

Source: `.rust-queue/reports/native-check-summary.json` and the driver output for `check 560 0`.

- `measured_subject_hashes_sha256`: `6df9b1928da0f11670b816898cfe98f29ce08415f36667e6ea9274278a69b1df`
- `native_result.sha256`: `2c1bb600dbae10ea796c9f78b2eb9d9bf5be5402cdb31fb8d9833688cd72d71a`
- `infrastructure_error`: `null`
- `engineering_acceptance`: `pending`

Only **two** build checks were actually executed (the run short-circuited at the first failure):

| # | kind | target | exit | result |
| --- | --- | --- | --- | --- |
| 1 | build | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | passed |
| 2 | build | `//score/mw/com/rust:score_com` | 1 | **failed** |

The failing check aborts with a deterministic Rust error:

```
error[E0596]: cannot borrow `handler` as mutable, as it is not declared as mutable
   --> score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs:724:54
724 |         let adapted = move |raw_state: u8| -> bool { handler(SubscriptionState::from(raw_state)) };
help: consider changing this to be mutable
721 |         mut handler: impl FnMut(SubscriptionState) -> bool + Send + 'static,
```

Independently confirmed in the working tree: `consumer.rs:719-724` still declares
`handler: impl FnMut(...)` **without `mut`**, and the `move` closure calls `handler(...)`. This is not
flaky — the source has not been corrected. The `fix1` stage is recorded as **failed**, and the tree
still contains the defect, so there is **no measurement after `fix1` and no basis to claim the patch
now builds**.

The `com-api-runtime-lola` crate is a dependency of `score_com`, so the Rust API change surface for the
runtime (and therefore the downstream consumers) is unbuilt.

---

## 3. Independent source review (what the patch actually contains)

Patched files read directly (bounded reads): `concept.rs`, `error.rs`, `score_com.rs`,
`bridge_ffi.rs`, `bridge_ffi_lola.rs`, `bridge_ffi_mock.rs`, `registry_bridge_macro.h`,
`registry_bridge_macro.cpp`, `com-api-runtime-lola/consumer.rs`, `com-api-runtime-mock/runtime.rs`.

Confirmed present and internally consistent in shape:

- `SubscriptionState` (`#[repr(u8)]`, discriminants 0/1/2) with `From<u8>` (`concept.rs:64-97`);
  unknown values map to `NotSubscribed`.
- Trait methods on `Subscription` (`concept.rs:968-1000`); `EventFailedReason::SubscriptionStateChangeHandlerFailed`
  (`error.rs:111-112`); public re-export (`score_com.rs:141`).
- `FFIBridge` raw surface `u8`/`bool` (`bridge_ffi.rs:229-247`), `LolaFFIBridge` wrappers
  (`bridge_ffi_lola.rs:869-897`), extern C decls (`bridge_ffi_lola.rs:422-451`).
- mockall and `SharedMockBridge` surface (`bridge_ffi_mock.rs:174-182`).
- C++ specialization + wrappers (`registry_bridge_macro.h:212-225`,
  `registry_bridge_macro.cpp:382-421`).
- `AtomicBool` flag, `Drop` unset-before-unsubscribe, four unit tests, mock runtime stubs
  (`consumer.rs:498-528, 708-765, 1492-1607`; `runtime.rs:341-356`).

So the *design* is source-backed against the C++ contract (`proxy_event_base.h`,
`subscription_state.h`, `SWS_CM_00310`). The problem is that it does not build, and several FFI/lifetime
properties below are asserted but not demonstrated.

---

## 4. Correctness / FFI / concurrency / trace / qualification gaps

### 4.1 Correctness — blocking
- **G1 (blocker, measured):** E0596 at `consumer.rs:724` — `handler` binding not `mut`. The crate and
  every dependent (public `score_com`, the LoLa unit tests, downstream binaries) cannot compile. This
  is the single cause of the measured failure; it is mechanical but fatal.

### 4.2 FFI / unsafe — needs correction or explicit proof
- **G2 (unsound transmute asymmetry):** the handler is boxed as
  `Box<dyn FnMut(u8) -> bool + Send + 'static>` (`consumer.rs:725`) and disposed with the matching
  `+ Send` type (`bridge_ffi_lola.rs:173`), but the **invocation** trampoline reconstructs
  `&mut dyn FnMut(u8) -> bool` **without `+ Send`** (`bridge_ffi_lola.rs:147`). Using a different
  trait-object type for the same allocation is not guaranteed by the language; the existing
  receive-handler trampoline (`bridge_ffi_lola.rs:35`) matches its box type. Make the three sites use
  the same trait-object type.
- **G3 (ownership on `false`/error):** `set_subscription_state_change_handler` reclaims the boxed
  closure when the FFI returns `false` (`consumer.rs:740-745`). The C++ wrapper takes the handler **by
  value** (`registry_bridge_macro.cpp:405-407`) and returns `result.has_value()`. If
  `SetSubscriptionStateChangeHandler` ever returns an error **after** consuming the callback, the C++
  temporary/parameter destructor disposes the Rust box and Rust then frees it again → **double free**.
  Today's LoLa binding is documented to always succeed (`scope.md` §4 cites
  `bindings/lola/proxy_event.cpp:155-165`), so the path may be unreachable, but the reclaim logic
  relies on an **unproven** "false ⇒ no ownership transfer" contract. This mirrors the pre-existing
  receive-handler pattern, so it is a noted residual risk rather than a new regression; it must be
  either proven or guarded.
- **G4 (null binding):** `ProxyEventBase::SetSubscriptionStateChangeHandler` dereferences `binding_`;
  the Rust path can only supply an event from a successful proxy, but the precondition is asserted by
  the middleware, not enforced by the new code. (Carried open item.)

### 4.3 Concurrency / lifetime — documented, not enforced
- **G5 (reentrancy → deadlock/abort):** the handler may run on a middleware thread under the
  state-machine lock. The Rust docs forbid calling back into the same subscription, but nothing
  enforces it. If the user does, `ProxyEventManager::get_proxy_event` either deadlocks on the C++ lock
  or panics (`consumer.rs:421-429`), and the trampoline turns any panic into
  `std::process::abort()` (`bridge_ffi_lola.rs:148-157`). So a documented misuse can abort the whole
  process. This is a contract, not a guard — acceptable only if explicitly accepted.
- **G6 (`false` self-unregister leaves stale Rust flag):** if the handler returns `false`, C++
  unregisters but the Rust `AtomicBool` stays `true`, so `Drop` issues a redundant
  `unset`. Likely harmless, but untested.
- **G7 (second `set` override):** re-registration silently replaces in C++; the Rust flag stays `true`.
  Consistent with the contract, but no test covers override disposal of the old box.

### 4.4 Trace / coverage — open
- **G8:** no end-to-end provider stop-offer/re-offer transition test (O12 open). All four new Rust
  tests use `MockFFIBridge`; the real trampoline, `RustBoxedCallable<bool, SubscriptionState>`, typed
  dropper and actual C++ `SetSubscriptionStateChangeHandler` crossing are **never exercised** by any
  executed or planned Rust test. C++ contract tests are enumerated in `check-plan.json` but were not
  run.
- **G9:** `check-0` executed 2 of the ~30 obligations in `check-plan.json` (short-circuit). Tests,
  docs, lint and all C++/integration targets remain **unrun**, not passed.
- **G10:** `com-api-runtime-mock` `#[cfg(test)] mod test` is not built by any test target
  (pre-existing); the new mock methods are only library-compiled.

### 4.5 Qualification
- **G11:** no tool/toolchain hashes, no Ferrocene qualification evidence, and no environment binding
  are carried. `native-check-summary.json` contains only the two bounded build tails above. Nothing
  native is qualified or accepted.

### 4.6 Trace / policy preserved (no violation found)
- Licenses/headers preserved on all touched files; no BUILD/dependency/pin/lint-profile change claimed
  or observed; no new requirement IDs created (`SWS_CM_00310` re-used from the C++ header); no QNX
  target or execution touched; the documented typed-dropper deviation (`implementation.md` §5) is
  present in source. No source suppression was added.

---

## 5. Failed / missing evidence preserved

| Evidence | Status | Treatment |
| --- | --- | --- |
| `check-0` build evidence | **present, FAILED** | preserved; quoted above; do not overwrite |
| `fix1` stage | **failed** | no post-fix measurement; defect still in tree |
| `com-api-runtime-lola-tests` result | **missing** (not run) | unrun, not passed |
| `score_com_concept-test` / macro tests | **missing** (not run) | unrun, not passed |
| all C++ `subscription_state_machine_*` / `proxy_event_subscription_test` | **missing** (not run) | unrun, not passed |
| integration tests (sync/async) | **missing** (not run) | unrun, not passed |
| lint (clippy / clang-tidy) | **missing** (not run) | unrun, not passed |
| docs / rustdoc targets | **missing** (not run) | unrun, not passed |
| upstream issue/PR timeline | **not retrieved** | unavailable in session |
| manual application of the build-fix | **not done** | outside this stage's authority |

No native result is invented, upgraded, or marked passed. The failed `check-0` is retained as-is.

---

## 6. Pending offline acceptance and concrete next action

**Pending authorized human decisions (unchanged, still proposals):**
1. API placement on `Subscription` rather than additionally on `Subscriber`.
2. `get_subscription_state()` infallible; unknown raw value → `NotSubscribed`.
3. raw `u8`/`bool` at the `FFIBridge` seam.
4. `Drop` unregisters the state handler before `unsubscribe`.
5. dedicated typed dropper vs. reuse of the `dyn FnMut()` deleter.

**Required before any acceptance can be considered:**
1. Fix G1 (`mut handler`) and re-run the *build* check for
   `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` and
   `//score/mw/com/rust:score_com` (config `linux_x64`).
2. Reconcile G2 (single trait-object type across box/invoke/drop) and G3 (prove or guard the
   "false ⇒ no ownership" contract).
3. Run the enumerated obligations from `check-plan.json` (Rust unit tests, C++ state-machine and
   `proxy_event_subscription_test`, docs, lint, downstream builds) and retain raw logs.
4. Obtain the design decisions above from authorized humans.

**Concrete next action:** an authorized operator fixes the `mut` binding (and addresses G2/G3), then runs,
under the native Linux/Ferrocene configuration, the build/test/lint/doc targets already enumerated in
`.rust-queue/reports/check-plan.json` and returns the raw logs; human reviewers then decide the design
questions. Until then this issue is **not implemented and not accepted**.

> This supervisor report is an independent, offline, read-only assessment. It grants no authority to
> comment, publish, merge or release, and it does not mark any native work product qualified or accepted.

---

### Review manifest
- Reviewed inputs: `.rust-queue/context/issue.json`, `task.json`, `comments.json`; `scope.md`,
  `implementation.md`, `review-packet.md`, `check-plan.json`, `native-check-summary.json`;
  the 12 patched source files and the cited C++ contract headers.
- Failures preserved: `check-0` (failed), `fix1` (failed); all unrun checks recorded as missing.
- Report location: `.rust-queue/reports/supervisor.md`.
