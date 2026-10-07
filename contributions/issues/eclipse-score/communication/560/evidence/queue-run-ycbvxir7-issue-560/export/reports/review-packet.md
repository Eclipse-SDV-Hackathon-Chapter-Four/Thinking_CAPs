# S-CORE Rust issue review packet — communication#560

## Scope and binding

- **Issue/repository**: `eclipse-score/communication#560`, "Improvement: Add Subscription State
  Change APIs Support on Rust API Lib", open, label `rust-api`, type `Product Increment`.
  Issue retrieved 2026-06-18 (created `2026-06-18T10:32:29Z`, updated `2026-06-18T10:32:51Z`,
  0 comments). Timeline/linked-PR state **not retrieved** (network tool unavailable).
- **Source commit**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (from task envelope).
- **User authority / permitted writes**: this packet was first drafted in the scope stage, whose tool
  boundary permitted writes only under `.rust-queue/reports/`. In the implementation stage source
  writes were permitted (file tools only; shell/measurement remained blocked), so the patch is now
  **applied in this disposable workspace** and recorded in `implementation.md`. Native measurement
  stages are still outside agent authority.
- **Artifact destination**: `.rust-queue/reports/`.
- **Budget limits**: `max_source_corrections: 3` in the task envelope; 0 used. No byte/time ceiling
  granted for execution. No paid calls made.
- **Process/tailoring versions**: `.rust-queue/context/score-rust-workflow/SKILL.md` v1.0.0;
  references `issue-types.md`, `native-verification.md`. No AGENTS.md present in the repository.
- **Native IDs**: `SWS_CM_00310` (subscription state), `SWS_CM_00309` (event receive handler) —
  read from the C++ headers; no new IDs created.
- **Source/lock/tool/storage bindings**: no Bazel toolchain was executed. From static reads:
  `.bazelrc` default `linux_x64` → `linux_x64_gcc_15` (`@gcc_toolchain_x86_64`,
  `@score_toolchains_rust//toolchains/ferrocene:ferrocene_x86_64_unknown_linux_gnu`),
  `.bazelrc` imports `quality/static_analysis/static_analysis.bazelrc` (clippy_strict + clang-tidy
  aspects). `native-check-summary.json` is **missing**, so no tool/environment hashes are carried.
- **Final patch and digest**: patch applied to the 12 files listed in `implementation.md`; no
  baseline→patched digest computed (no hashing tool in session).
- **Technical completion status**: implementation applied; no native check executed or evidence
  collected. **Engineering acceptance status**: not accepted — requires authorized human decision.
- **Decision reference**: none (offline review pending).

## Acceptance and engineering trace

| Issue criterion | Native obligation / artifact ID and revision | Changed artifact | Required check | Evidence/hash | Gap or proposed disposition |
| --- | --- | --- | --- | --- | --- |
| Sync `GetSubscriptionState()` equivalent | `proxy_event_base.h` L90; `bindings/lola/proxy_event.cpp` L83-87; `SWS_CM_00310` | `concept.rs` (`SubscriptionState`, `Subscription::get_subscription_state`), `consumer.rs`, `bridge_ffi*.rs`, `registry_bridge_macro.*` | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`; C++ `...:proxy_event_subscription_test` | none (not run) | Planned; needs execution in measurement stage |
| Async `SetSubscriptionStateChangeHandler()` equivalent | `proxy_event_base.h` L110; `subscription_state_change_handler.h` L33 | `Subscription::set_subscription_state_change_handler`; trampoline + `RustBoxedCallable<bool, SubscriptionState>` | `com-api-runtime-lola-tests`; `...:subscription_state_machine_methods_test` | none (not run) | Planned; needs execution |
| `UnsetSubscriptionStateChangeHandler()` equivalent + "never called after unset" | `proxy_event_base.h` L117; handler header L114-116 | `Subscription::unset_subscription_state_change_handler`; `Drop` unset-before-unsubscribe | `com-api-runtime-lola-tests` | none (not run) | Planned; teardown test drafted |
| Return `false` unregisters handler | handler header L30-32 | handler `bool` return preserved through FFI trampoline | `...:subscription_state_machine_methods_test` | none (not run) | Planned |
| Handler may run under lock; no reentrant same-event calls | handler header L24-28 | doc contract + existing `ProxyEventManager` serialisation | `com-api-runtime-lola-tests` | none (not run) | Documented; residual deadlock risk if user calls same event (documented, not enforced) |
| Public API re-export | `score/mw/com/rust:score_com` | `score_com.rs` | build `//score/mw/com/rust:score_com` | none (not run) | Planned |
| Mock runtime compiles | `com-api-runtime-mock` | `runtime.rs` | build `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` | none (not run) | Planned |
| Docs / Detailed Design impact | issue category "Affects Detailed Design" | `user_facing_api_examples.md`, `high_level_design_detail.md` | `com-api-runtime-lola-doc-tests`; `score_com_concept-macros-tests` (manual) | none (not run) | Planned; manual doc-test enumerated and not assumed |
| Downstream compilation | public API change | consumers under `basic_rust_api` | build consumer binaries | none (not run) | Planned |

Baseline reconciliation: no prior implementation of these APIs exists anywhere in the baseline
(only the C++ middleware side). Semantic/link direction is Rust API → FFI bridge → C++ middleware;
no requirement IDs are added or modified. Safety assumptions: `Send + 'static` handler, single
boxed allocation freed exactly once (middleware dispose on unset/false/destruction; Rust reclaims
only when C++ reported it did not take ownership).

## Dependency and macro assessment (when applicable)

Not applicable: no crate is added, replaced, upgraded or vendored, and no proc-macro invocation
pattern changes. `CommData`/`Reloc` derive macros are untouched. Therefore the retain/replace/
internal option table is omitted with this sourced reason (SKILL: dependency assessment is
conditional).

## Verification and expected checks

All rows below are **planned obligations**, not results. No check was executed (shell blocked);
`native-check-summary.json` is missing, so no collector evidence exists.

| Check and native obligation/source | Command/config/tool/target/features | Subject hashes | Result/exit code | Raw evidence/hash | Limitation/disposition |
| --- | --- | --- | --- | --- | --- |
| Rust unit tests for new API | target `com-api-runtime-lola-tests` (config `linux_x64`) | unknown | not run | none | Planned; must be executed by collector |
| Concept crate tests | `score_com_concept-test` | unknown | not run | none | Planned |
| Macro unit tests | `score_com_concept-macros-unit-tests` | unknown | not run | none | Linux forwarding target |
| C++ state-machine methods | `bindings/lola:subscription_state_machine_methods_test` | unknown | not run | none | Planned |
| C++ state transitions | `...:subscription_state_machine_events_test`, `...:subscription_state_machine_states_test` | unknown | not run | none | Planned |
| C++ ProxyEvent subscription contract | `...:proxy_event_subscription_test` | unknown | not run | none | Planned |
| Concurrency stress | `...:subscription_state_machine_stress_test` | unknown | not run | none | Supplementary; short pass does not prove race absence |
| Integration (sync/async) | `.../consumer_sync_apis/integration_test:test_com_api_sync`, `.../consumer_async_apis/integration_test:test_com_api_async` | unknown | not run | none | Existing flows only; no new state-transition scenario |
| Rustdoc | `com-api-runtime-lola-doc-tests`; `score_com_concept-macros-tests` (**manual**, documented rules_rust linking limitation) | unknown | not run | none | Manual target explicitly enumerated, not claimed |
| Lint | clippy_strict aspect over changed Rust libs; clang-tidy aspect over `registry_bridge_macro_cpp` | unknown | not run | none | Exact invocation is a command-stage concern |
| Downstream build | `consumer_sync_apis:bigdata-consumer`, `consumer_async_apis:bigdata-consumer-async` | unknown | not run | none | Planned |
| Reverse-dependency / implementor query | `bazel query` over `//score/mw/com/rust:score_com` and concept crate | unknown | not run | none | Implementor set currently source-inspected (Lola + mock); full set open |

Generated-API compatibility on both baseline and candidate: **not measured** (no build executed).
Failed/unavailable checks are preserved as "not run"; nothing is marked pass.

## Offline decisions and portable evidence

- **Proposed engineering decisions requiring authorized review**:
  1. place the API on `Subscription` (post-subscribe) rather than also on `Subscriber`;
  2. expose `get_subscription_state()` as infallible, mapping an unknown raw value to
     `NotSubscribed`;
  3. use `u8` at the `FFIBridge` seam to avoid coupling `bridge_ffi_rs` to `score_com_concept`;
  4. unregister the state handler in `Drop` before `unsubscribe`.
  All four remain proposals until accepted.
- **Pending acceptance / gaps**:
  - no native check executed; `native-check-summary.json` missing;
  - no end-to-end provider stop-offer/re-offer integration scenario;
  - upstream issue/PR activity not retrieved;
  - C++ `binding_` null precondition is asserted by middleware, not newly enforced;
  - unknown raw state value mapped conservatively without error signalling;
  - no file hashes computed (no hashing tool in session).
- **Patch/native documents/logs location**: `.rust-queue/reports/implementation.md` (applied change
  record + deviations), `.rust-queue/reports/scope.md`, `.rust-queue/reports/check-plan.json`.
- **Manifest** (relative path; size/SHA-256 unknown — hashing tool unavailable):
  - `.rust-queue/reports/scope.md`
  - `.rust-queue/reports/check-plan.json`
  - `.rust-queue/reports/implementation.md`
  - `.rust-queue/reports/review-packet.md`
  - `.rust-queue/reports/probe.txt` — scratch file created during a tool-boundary probe, **excluded**
    from the packet's evidence set.
- **Source/tool/config identities sufficient to reproduce without Fabro**: commit `381d43d`;
  target labels in `check-plan.json`; `.bazelrc` config `linux_x64`; C++ contract files cited in
  `scope.md`; workflow `SKILL.md` v1.0.0.
- **Concrete next action**: an authorized operator runs the `check-plan.json` targets in a disposable
  Linux checkout of `381d43d` with this patch applied, under the native Ferrocene/Linux
  configuration, and returns the raw logs; human reviewers then decide the design questions above.

> Passing checks and completed execution do not supply a human decision. This packet is exported
> for offline review; no native work product is marked qualified, released or accepted.
