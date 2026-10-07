# Supervisor review — issue eclipse-score/communication#560 (resumed, correction 3)

**Issue**: "Improvement: Add Subscription State Change APIs Support on Rust API Lib"
(`rust-api`, type `Product Increment`, state `open`, 0 comments, no upstream timeline retrieved).
**Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (`.rust-queue/context/task.json`).
**Mode**: `implementation`; **Linux only**; QNX excluded (#1278). DeepSeek Flash only, no fallback.
**Tool boundary actually observed**: file tools only. `shell`, `grep`, `web_fetch`, delegation,
credentials and publication are refused by the workspace boundary
("Bound Rust workspace/file-tool boundary"); `glob` works only inside the workspace copy. No native
command was executed by this review and no native result is claimed. **Only file written: this report.**
**Review scope**: independent, read-only review of the correction-3 patch (attempt 3), `correction-3.md`,
the four new package artifacts, the attempted measurement in `native-check-summary.json`, the
integration plan, `check-plan.json`, and the carried (attempt-2) evidence. `correction-2.md`,
`implementation.md`, `review-packet.md`, `scope.md`, `supervisor-prior.md`, `probe.txt`,
`check-plan.json` and the carried summaries are treated as history/plan and are **not edited**.

---

## 1. Disposition (summary)

| Field | Value |
| --- | --- |
| Technical completion (patch) | **NOT met** — the new binary does not compile at the final tree |
| Last measured native outcome | **FAILED** `attempt: 3`, `kind: measured_native_command`, `exit_code: 1`, `passed: false` |
| Failing check | `build` of `//score/mw/com/test/basic_rust_api/subscription_state_apis:subscription-state-apis` (`linux_x64`) |
| Compile errors | 2 × `error[E0283]: type annotations needed for LolaRuntimeBuilderImpl<_>` at `subscription_state_app.rs:118:9` and `:125:9` |
| New production callback path (real LoLa) | **NEVER invoked** — no binary was produced; 0 of 5 new cases ran |
| Case-count denominator | **5 planned, 5 defined, 0 executed** (see §7) |
| Regression / lint / query obligations | **0 executed** (run stopped at the failed build) |
| Mocked-notification substitute used? | **No** — deps are real LoLa only; but nothing was measured (§6) |
| Correction budget | **3 of max 3 used** — final attempt consumed; no fourth correction, no source fix made here |
| Engineering acceptance | **PENDING**, offline, no authorized human decision |
| Recommended disposition | **Do not mark implemented/qualified/accepted.** Export failure history; treat the missing production callback evidence as an open obligation. |

The measured subject hash for attempt 3 is
`839b2589fcf094031ca952cc26e5cd3f3125db31723b7d1127e23812d8e5dbb4`, distinct from the carried
attempt-2 subject `003291e718b3c937af1b0b28d7ae91c4d1b602f942ed37fbd55b8cd9acfc98e6`, confirming the
new package changed the subject and **invalidating carried evidence for the new files**.

---

## 2. Freshly executed measurement (attempt 3) — the only new native evidence

Source: `.rust-queue/reports/native-check-summary.json` (this is the current measured summary, not the
carried one) and the bounded native summary captured in the stage output.

- `issue`: 560, `attempt`: 3, `baseline`: `381d43dec…`, `kind`: `measured_native_command`
- `exit_code`: `1`; `passed`: `false`; `timed_out`: `false`; `infrastructure_error`: `null`
- `engineering_acceptance`: `pending`
- `measured_subject_hashes_sha256`: `839b2589fcf094031ca952cc26e5cd3f3125db31723b7d1127e23812d8e5dbb4`
- `native_result.path`: `…/jobs/560/execution/check-3/native-result.json`
- `native_result.sha256`: `b466304ef8c93923bf9a8f73d45121eb1d8762de98f91a58add77a4f0cafd4ea`
- `bounded_native_summary.checks`: exactly **one** entry — the build above (`exit_code: 1`)
- Elapsed `604.981s`; `1248` processes; the build reached `[1,245 / 1,248] Linking score/mw/com/libruntime.a`
  before the new Rust bin failed. The dependency closure (including `score_com`,
  `com-api-runtime-lola` and the real LoLa FFI) **compiled**; only the new controller/provider binary failed.

Verbatim failure (bounded tail):

```
error[E0283]: type annotations needed for `LolaRuntimeBuilderImpl<_>`
   --> …/subscription_state_apis/subscription_state_app.rs:118:9
    = note: cannot satisfy `_: bridge_ffi_rs::FFIBridge`
help: the trait `bridge_ffi_rs::FFIBridge` is implemented for `bridge_ffi_lola::LolaFFIBridge`
note: required by a bound in `LolaRuntimeBuilderImpl`
help: consider giving `builder` an explicit type … `LolaRuntimeBuilderImpl<B>`
error[E0283]: type annotations needed for `LolaRuntimeBuilderImpl<_>`
   --> …/subscription_state_apis/subscription_state_app.rs:125:9
error: aborting due to 2 previous errors
ERROR: Build did NOT complete successfully
```

### 2.1 Root cause (confirmed by bounded source reads)

- `score_com.rs` re-exports the generic builder:
  `pub use com_api_runtime_lola::RuntimeBuilderImpl as LolaRuntimeBuilderImpl;`
- `com-api-runtime-lola/runtime.rs:59` declares
  `pub struct RuntimeBuilderImpl<B: FFIBridge = LolaFFIBridge>`.
- The new file writes, at `provider_entry` (line 118) and `controller_entry` (line 125):
  `let mut builder = LolaRuntimeBuilderImpl::new();`. `new()` takes no argument and the only later use
  is `&runtime` passed into the generic `provider_main<R: Runtime>` / `run_controller<R: Runtime>`,
  which does **not** pin `B`; inference therefore fails (E0283).
- The already compiling application uses the correct form:
  `consumer_sync_apis/consumer_app.rs:318` → `let mut runtime_builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();`.
- The bad pattern was almost certainly copied from the `ignore` Quick-Start block in
  `score_com.rs:59` / `:85`, which uses the *same* un-annotated `LolaRuntimeBuilderImpl::new()`.
  Because those examples are `ignore`, they are never compiled — this is an instance of the previously
  recorded gap **G9 (documentation/examples not compiled)**.

**This is a real, deterministic source defect, not flakiness.** Correcting it is a source edit that the
exhausted correction budget does not authorize here (see §11); it is recorded, not performed.

---

## 3. What did NOT run (omitted / failed checks — must stay explicit)

`check-plan.json` enumerates four obligation groups. Attempt 3 executed only the first, which failed;
the run stopped before the rest. Therefore:

| # | Planned obligation (`check-plan.json`) | Status in attempt 3 |
| --- | --- | --- |
| 1 | `build` `…:subscription-state-apis` (`linux_x64`) | **EXECUTED — FAILED (E0283)** |
| 2 | `test` five new cases + `test_com_api_sync` + `test_com_api_async` (uncached Linux Docker) | **NOT RUN** |
| 3 | `lint` native Clippy (`clippy_strict`) on `…:subscription-state-apis` | **NOT RUN** |
| 4 | `query` the two new labels | **NOT RUN** |

Consequently, **no** integration XML, Bazel BEP/events, callback trace, protocol trace, analyzer report,
or test-case count exists for attempt 3. A zero-case or absent target is **missing evidence**, not a
pass. The `pkg_application` target, the `etc:config` / `bigdata:logging.json` labels and the
`integration_test` target were **never resolved** by an executed check (Bazel analysis stopped at the
new bin's compilation; the failing check only requested the `rust_binary` label).
`etc:config` is confirmed to exist by a bounded read (`basic_rust_api/etc/BUILD`, `filegroup(name="config")`),
but label resolution for the other two remains **unmeasured**.

---

## 4. Carried evidence (attempt 2) — separate and still labelled carried

These are historical measurements of the earlier subject (`003291e7…`), supplied by the integration
plan and the carried supervisor. They are **not** fresh results for the correction-3 subject and do
**not** cover the new package.

| Carried item | Result | What it does NOT prove |
| --- | --- | --- |
| Six passing Linux command groups (build/test/doctest/lint/query), `exit_code: 0`, `passed: true` | PASSED (attempt 2) | Nothing about the new two-process binary |
| 12 LoLa Rust unit cases (`com-api-runtime-lola-tests`) over `MockFFIBridge` | passed | Rust-side contract only; **mock bridge is an inert double** |
| C++ state-machine / `proxy_event_subscription_test` | passed | C++ middleware only; does not cross the Rust FFI trampoline |
| `test_com_api_sync` + `test_com_api_async` | passed | Existing receive/async flows; **never call the new subscription-state API** |
| 17 doctest examples passed, 2 ignored | passed | Ignored examples add no coverage |
| Clippy (`clippy_strict`) on 5 Rust libs | passed (3 pre-existing warnings) | Library lint only; the new executable and test code untested |

Carried attempt-2 native result: `native_result.sha256` `66c022590bd956a8b12a658b53071051129c41e296bcf744fd951d079c71bf0e`,
`exit_code: 0`. Preserved as history; not upgraded, not treated as evidence for the new package.

---

## 5. Independent static review of the four new artifacts

All four carry the Apache-2.0 / Eclipse Foundation header (2026); no pin, dependency, feature,
lint-profile, requirement-ID, license or C++ source change is introduced. Writes are confined to the
new package and `.rust-queue/reports/`.

| # | Path | Static review |
| --- | --- | --- |
| 1 | `…/subscription_state_apis/BUILD` | `rust_binary(name="subscription-state-apis")`, deps `//score/mw/com/rust:score_com` + `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`, `features=["link_std_cpp_lib"]`, Linux `-no-pie`/`-lstdc++`. No mock dep. `pkg_application` packages the bin + `etc:config` + `bigdata:logging.json`. **Not validated by an executed check.** |
| 2 | `…/subscription_state_apis/subscription_state_app.rs` | Single binary, two roles. **Does not compile** (E0283, §2). |
| 3 | `…/subscription_state_apis/integration_test/BUILD` | `integration_test(name="test_subscription_state_apis")` over the existing Linux Docker fixture; `target_compatible_with` linux+x86_64. **Not analyzed.** |
| 4 | `…/subscription_state_apis/integration_test/test_subscription_state_apis.py` | 5 case functions, each `target.wrap_exec("bin/subscription-state-apis", ["--scenario", name], cwd="/opt/subscription-state-apis", wait_on_exit=True, wait_timeout=180)`. **Not executed.** |

### 5.1 Case-by-case review (all five: static review OK/intentional; **execution = NOT RUN**)

| Case | Scenario | Static review | Execution |
| --- | --- | --- | --- |
| `test_subscription_state_notifications` | `notifications` | Registers a retaining handler; `WITHDRAW` → awaits real `SubscriptionPending` observation **and** main-thread query; `OFFER` → awaits `Subscribed` **and** query on the *same* subscription; then a generation-marked `0x51` sample; explicit `unset` → requires disposal `== 1`, invocations `>= 2`, `send_failures == 0`; drops. Matches plan (ordered phase-specific assertions, no exact-total count). | **NOT RUN** |
| `test_subscription_state_handler_replacement` | `replacement` | `set` A then B; requires A disposal `== 1` immediately after B's setter returns (sync fence); WITHDRAW/OFFER drives B's pending/subscribed observations + query; requires A invocations `== 0`; `unset` B → B `== 1`; drop → A `== 1`, B `== 1`. Matches plan. | **NOT RUN** |
| `test_subscription_state_handler_unset` | `unset` | `set` A then `unset` while subscribed → A disposal `== 1`; WITHDRAW/OFFER with no handler → A invocations `== 0`; registers B and drives a **callback-observed** positive-control cycle; `unset` B → B `== 1`, invocations `>= 2`, A still `== 1`. Matches plan (positive control present). | **NOT RUN** |
| `test_subscription_state_handler_false_then_drop` | `false-then-drop` | `set` A returning `false`; WITHDRAW → pending observation; then awaits `DisposeProbe` destruction and uses a synchronous pending query as the state-lock fence (callback receipt is **not** treated as a disposal fence); OFFER → subscribed + `0x77` sample; requires A invocations `== 1`; drops the same subscription; requires disposal `== 1`, invocations `== 1`. Matches plan. | **NOT RUN** |
| `test_subscription_state_handler_drop_active` | `drop-active` | `set` A on stable subscribed, drop subscription directly → A disposal `== 1`, invocations `== 0`; fresh discovery/subscription + handler B drives a full WITHDRAW/OFFER cycle; `unset` B → `== 1`, invocations `>= 2`. Matches plan. | **NOT RUN** |

**Verdict**: the five cases are well-formed against the plan and each targets the intended obligation
(real callback path, replacement, unset, false-cancel, active drop). None ran, so **none is passing**
and the production Rust→C++→Rust callback path remains **unexercised (O12/G8 open)**.

### 5.2 Coordination, deadlines and process cleanup (static)

- Controller owns runtime/discovery/consumer/subscription and does **not** move native handles between
  threads; the provider is a separate process with its own runtime and offered producer (plan satisfied).
- Line protocol is prefix-tagged (`SSAPI-PROTO`) and phase-tagged; controller uses
  `recv_timeout` with absolute deadlines (`ACK 30s`, `EXIT 30s`, `DISCOVERY 60s`, `QUERY/CALLBACK/DISPOSAL/SAMPLE 30s`,
  `POLL 20ms`); EOF/disconnect, malformed, phase-, command- and status-mismatch are all rejected.
- Non-protocol stdout lines are retained as `diagnostics`; provider stderr is **inherited** (no unread pipe).
- `ProviderSession::drop` closes stdin, kills+waits its owned child and joins the reader thread; the
  read thread owns no native handles. Reader channel is unbounded, so it never blocks the controller.
- Design review found **no deadlock or leak path** in the harness itself, but this is **unverified by
  execution**; it is a static reading only.

### 5.3 Trait imports / lifetimes (static)

- The API in use matches the public trait: `get_subscription_state(&self) -> SubscriptionState`,
  `set_subscription_state_change_handler(&self, impl FnMut(SubscriptionState) -> bool + Send + 'static) -> Result<()>`,
  `unset_subscription_state_change_handler(&self) -> Result<()>` (`concept.rs:968-1000`; LoLa impl
  `consumer.rs:708-766`).
- The handler is `Send + 'static` and passive (atomic counters + unbounded channel send only; failure
  recorded in a test atomic); it never re-enters the subscription, matching the documented reentrancy
  contract (`concept.rs:980-984`). The `DisposeProbe` is genuinely captured and used by the closure.
- Samples are dropped inside `receive_marker` before returning; no sample is held across teardown.
- The un-annotated `LolaRuntimeBuilderImpl::new()` is a **type-inference** failure; it is the only
  compiler-reported defect. Whether the imports (`Producer`/`OfferedProducer`/`Publisher`/`Subscriber`/
  `SampleMaybeUninit`/`SampleMut`, needed for trait-method resolution) or any lifetimes would also warn
  or fail later **cannot be established** because compilation aborted at E0283 and the bounded tail is
  truncated.

---

## 6. Real-LoLa linkage vs. mocked substitute (static only)

- `BUILD` deps are `//score/mw/com/rust:score_com` and
  `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`; the binary links the real LoLa runtime
  via `LolaRuntimeBuilderImpl` and the generated C++ registration from `bigdata_com_api_gen_rs`
  (`alwayslink` `bigdata_com_api_gen_cpp`). **No** `bridge_ffi_mock` / `score_com_mock` is linked, so
  the *intent* is a real production path, not a mocked notification substitute.
- However, **no binary was produced and no case ran**, so there is **zero** freshly executed
  notification evidence of any kind. The carried mock unit tests and C++ tests are **explicitly not**
  substitutes for the production Rust→C++→Rust notification path.

---

## 7. Case-count denominator (verified)

- Integration plan: **5** proposed cases.
- `test_subscription_state_apis.py`: **5** test functions, names identical to the plan's five.
- Attempt 3 execution: **0 / 5** (build failed before the integration target was ever requested).
- The `check-plan.json` test group additionally names `test_com_api_sync` and `test_com_api_async`
  (the carried "six sample-exchange integration cases"): **0 executed** in attempt 3.
- A zero-case or skipped target is missing evidence; the denominator is **not** reducible by the build failure.

---

## 8. Open gaps retained (not closed, not upgradable)

1. **O12 / G8 (real callback integration)** — the real
   `set_subscription_state_change_handler → RustBoxedCallable<bool, SubscriptionState> → Rust trampoline`
   path is still **never invoked at runtime**; correction 3's attempt cannot close it (compile failure).
2. **G6 (`false`-then-teardown stale flag)** — now has a case, but unexecuted; the redundant native
   unset is ignored on the Rust side (`Drop` uses `let _ = …`), yet behaviour against the real
   middleware is unproven.
3. **G7 (second-`set` replacement disposal)** — now has a case, but unexecuted.
4. **Concurrency / reentrancy** — the handler may be invoked from a middleware thread under the
   state-machine lock; a user breach can deadlock or abort (panic-to-abort in the trampoline). No
   concurrency/stress proof; the C++ `subscription_state_machine_stress_test` is supplementary, not
   absence-of-race evidence.
5. **G3 (ownership-on-failure)** — the `false ⇒ no ownership transfer` reclaim relies on an unproven
   contract; a future binding erroring *after* consuming the by-value callback would double-free.
   Unreachable today, **not guarded**.
6. **Native trace** — `SWS_CM_00310` applicability/acceptance remains pending; the local scenarios
   supply no accepted native verification IDs.
7. **Qualification** — no Ferrocene/toolchain or environment-binding/qualification evidence exists;
   execution logs are not qualification. Do not mark qualified.
8. **Examples / docs** — documentation examples are `ignore` and not compiled (the Quick-Start snippet
   itself contains the non-compiling builder pattern); new Markdown examples are not executed.
9. **Downstream / trait-implementor enumeration** — only explicit labels were ever planned; full
   reverse-dependency and implementor coverage, `com-api-example`, the unbuilt
   `com-api-runtime-mock` `#[cfg(test)]` module (G10), and test-code Clippy coverage remain open.
10. **Upstream activity** — no issue/PR timeline was retrieved (no network tool).
11. **`check-plan.json` reason text** still names the pre-correction-2 test names (documentation lag;
    no obligation dropped).

---

## 9. Preserved identity, policy and notices

- Baseline pinned at `381d43dec900ab6a9076f3f30e7bfbdee019e26e`; native requirement ID `SWS_CM_00310`
  reused (no new IDs invented); task/issue/comment metadata preserved.
- No toolchain pin, dependency, feature, lint profile, license or C++ change in the new package; new
  files retain Eclipse Foundation Apache-2.0 notices.
- Protected/native/carried summaries (`native-check-summary.json` is the current measured summary;
  carried-correction-2.md, carried-native-check-summary.json, carried-supervisor.md, check-plan.json)
  were **not edited**. `supervisor-prior.md` (attempt-0 E0596 history) retained.
- Failed attempts retained: attempt-0 build failure (history), `fix1` failed, carried attempt 2 passed,
  attempt 3 build **failed**. No result was upgraded, invented or marked accepted.

---

## 10. Pending human engineering acceptance (offline)

`engineering_acceptance` is `pending`; deterministic tools and this review cannot supply it. Still
awaiting an authorized human (unchanged proposals):
1. API placement on `Subscription` (not also on `Subscriber`);
2. infallible `get_subscription_state()`, unknown raw value → `NotSubscribed`;
3. raw `u8`/`bool` at the `FFIBridge` seam;
4. `Drop` unregisters the state handler before `unsubscribe`;
5. dedicated typed dropper instead of the generic `dyn FnMut()` deleter.

---

## 11. Concrete next action (authorized operator — outside agent authority)

The correction budget is **exhausted (3/3)**; this stage performs **no source fix**. To make progress:

1. Export the failure history and the missing-production-evidence obligation unchanged.
2. If continuation is authorized, it requires a **new correction/reset decision** by an authorized
   operator (not available here). The minimal technical fix is to pin the builder type in
   `provider_entry`/`controller_entry`, e.g. `let mut builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();`
   (matching `consumer_app.rs:318`) — **proposed for review only; not applied.**
3. On any re-run: build the new binary under `linux_x64`, then execute
   `…/integration_test:test_subscription_state_apis` uncached and require **all five** cases in the
   XML with the WITHDRAW/OFFER phase observations; run the two regression targets, native Clippy on the
   new binary, and the query check. Return raw logs, exit codes and subject hashes.
4. Obtain the five human decisions in §10.

Until then the issue is **not implemented to acceptance, not qualified, and not accepted**.

---

## Review manifest

- **Inputs read (bounded ≤200 lines/call)**: `.rust-queue/context/task.json`;
  `score-rust-workflow/SKILL.md` and `references/native-verification.md`;
  `context/integration-plan/integration-plan.md`; `reports/correction-3.md`,
  `reports/carried-supervisor.md`, `reports/carried-correction-2.md`, `reports/scope.md`,
  `reports/native-check-summary.json`, `reports/check-plan.json`; the four new package files
  (`BUILD`, `subscription_state_app.rs`, `integration_test/BUILD`, `integration_test/test_subscription_state_apis.py`);
  and supporting source: `com-api-runtime-lola/runtime.rs`,
  `com-api-runtime-lola/consumer.rs` (state API + `Drop`), `rust/score_com.rs`,
  `score_com_concept/concept.rs` (Subscription trait), `score_com_concept/interface_macros.rs`
  (offer/unoffer), `consumer_sync_apis/consumer_app.rs`, `basic_rust_api/etc/BUILD`.
  `context/integration-plan/context/native/**` used as read-only source anchors.
- **Authority**: file tools only; no shell/grep/web/delegation/credentials/publication;
  no source edit and no native execution; **only file written: this report**.
- **Failures preserved**: attempt-0 (E0596) and `fix1` as history; carried attempt-2 pass as carried;
  attempt 3 build **FAILED**; all unexecuted obligations recorded as missing, not passed.
- **Report location**: `.rust-queue/reports/supervisor.md`.

> This supervisor report is an independent, offline, read-only assessment. It grants no authority to
> comment, publish, merge or release, and it marks no native work product qualified or accepted.
