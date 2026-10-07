# Independent supervisor report — issue #250: typed Rust `FindServiceSpecifier::Any` (Linux only)

Status: **audit only. Engineering acceptance remains PENDING OFFLINE.**
Supervisor did not source-edit, did not run anything (`shell`/`grep` blocked by the run guard),
did not spend the #1261 budget and wrote only this file.

| Item | Value |
| --- | --- |
| Issue | eclipse-score/communication #250 (label `rust-api`, state open) |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Platform | Linux (LoLa/SHM) only |
| Model / editor | DeepSeek Flash only |
| Reviewed artifacts | `.rust-queue/reports/plan.md`, `implementation.md`, `native-check-summary.json`, `regression-plan.json`, and the 19 changed sources |
| Check result under audit | `native_passed: false`, `checks: 1`, `changed_files: 19`, `positive_regression_gap: null`, `required_regression_plan_present: true` |
| Acceptance | not granted; no automatic acceptance; no source correction issued by this stage |

## 1. Verdict

The proposed implementation is **not buildable as committed**. The single executed check
(`//score/mw/com/test/basic_rust_api/consumer_any_apis/integration_test:test_com_api_any`) **failed to
build**, so the required native positive Any regression **did not execute at all**, and none of the
other planned checks (in-crate unit tests, `score_com_concept-test`, `runtime_test`, Specific
compatibility, `find_any_semantics`, clippy/build) ran. The claimed positive evidence in
`implementation.md` §4 is **proposed-only and unverified**; the implementation report itself admits
"No build, test, analyzer or integration run was executed in this stage".

The design (explicit registration metadata + configuration-resolved wildcard selector + runtime-owned
deployment) is coherent and matches the mandatory refinements **on inspection**, but no runtime
behavior is proven, and at least **two independent compile defects** block every check.

## 2. Confirmed blockers (build-failing)

### B1 — Rust: struct field / initializer mismatch in `consumer.rs` (CRITICAL)

`native-check-summary.json` records the authoritative failure:

```
error[E0560]: struct `ServiceDiscoveryFuture<_, _>` has no field named `find_guard`
    --> score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs:1018:17
    help: a field with a similar name exists: `_find_guard`
```

Independently reconfirmed in the current workspace source:

- `consumer.rs:1018` initializer uses `find_guard,`
- `consumer.rs:1059` declares the field as `_find_guard: FindServiceStopGuard<B>,`

`consumer.rs:1015` introduces the local `let find_guard = find_service_result?;`, but the struct field
was renamed with a leading underscore (apparently to silence a dead-code lint) without updating the
construction site. This aborts compilation of `//score/mw/com/impl/rust/com-api/com-api-runtime-lola`
(the exact crate the two new `FFIBridge` methods and the owning `FindServiceStopGuard` live in), which
is a dependency of the failing test. **No Rust Any code in this crate can be compiled, unit-tested, or
exercised natively until fixed.** Minimal class of fix: rename the initializer to `_find_guard` or
rename the field back to `find_guard` (a one-token correction; supervisor did not apply it).

### B2 — C++: malformed `BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER` macro (CRITICAL, independent)

The new 4-argument macro is missing the registration type at the "force instantiation" statement:

- Correct existing 3-arg macro, `registry_bridge_macro.h:782`:
  `id##_InterfaceRegistrationHelper id##_interface_reg_instance;`
- New 4-arg macro, `registry_bridge_macro.h:824`:
  `id##_interface_reg_instance;`  ← no type specifier

At namespace scope `some_identifier;` is not a declaration; this is ill-formed and will be rejected
whenever the macro is expanded. It is expanded **four times** in
`score/mw/com/test/basic_rust_api/bigdata_com_api_gen.cpp` (`BigDataInterface`,
`ConcreteSelectorInterface`, `MalformedSelectorInterface`, `EmptySelectorInterface`), a file that
`bigdata-consumer-any` depends on. Even after B1 is fixed, the requested test target will still fail
to build on the C++ side. This defect is **not visible** in the bounded check tail (the Rust error
surfaced first), so the recorder must not assume B1 is the only compile failure.

Both blockers are within the permitted source set and are one-line corrections, but they were not
present as a clean, compilable state in the artifact handed to the check stage.

## 3. Ownership / pointer-lifetime audit (mandatory refinement)

- `ResolveFindAnyIdentifier` (`registry_bridge_macro.cpp:60-100`) resolves the registered selector
  through `IRuntime::resolve` (`runtime.cpp:258-285`), which builds each `InstanceIdentifier` from
  `Configuration`-owned `ServiceInstanceDeployment`/`ServiceTypeDeployment` pointers
  (`runtime.cpp:261-273`). The value is copied out of the local `std::vector<InstanceIdentifier>`
  (`instance_identifier.h` stores non-owning deployment pointers), so **no pointer to the vector or
  any stack/local object escapes**. This is the stable `Runtime`-owned owner the mandate requires, and
  the design **does not synthesize** a wildcard deployment (no relocating-vector hazard).
- `HandleType` copies the identifier by value and carries the discovered `instance_id_`
  (`handle_type.h:41,101-104`, `handle_type.cpp:52-53`), so every emitted builder/proxy retains
  pointers into the process-lifetime `Runtime` singleton, independent of the discovery object or
  `StopFindService`. This satisfies `mandatory_lifetime_refinement` **by construction**.
- Native precedent exists: the unchanged C++ `score/mw/com/test/find_any_semantics/client.cpp:74-121`
  builds a `TestDataProxy` from each wildcard handle (client manifest omits `instanceId`) and
  subscribes/receives real samples, i.e. proxy construction for wildcard instances absent from the
  consumer config is a supported native behavior — not invented by this patch.
- The Rust builder additionally retains `Arc<NativeHandleContainer>` (`consumer.rs`), which is
  necessary-but-not-sufficient per the mandate; the sufficiency here comes from the `Runtime`
  singleton owner above.
- **Unverified:** the sync "drop discovery then build/use proxy" and async "drop future/discovery
  then receive real samples" regressions in `consumer_any_apis/consumer_app.rs:157-230` were never
  executed (blocked by B1/B2). Lifetime is a source-inspection conclusion, not measured evidence.

## 4. Async ownership / never-polled drop audit

- `get_available_instances_async` now creates `FindServiceStopGuard` **synchronously** on a non-null
  `start_find_service[_any]` result (`consumer.rs:992-1009`) and moves it into
  `ServiceDiscoveryFuture` (`consumer.rs:1017-1025,1053-1065`). The guard's `Drop`
  (`consumer.rs:1039-1051`) calls `stop_find_service` exactly once; `NativeFindServiceHandle` stays
  non-`Copy`, so exactly-once holds for (a) never-polled outer future drop, (b) polled-pending
  cancellation, (c) completion. This is the correct fix for the baseline start-before-poll leak and
  also applies to the pre-existing `Specific` path.
- **Unverified:** the three `#[cfg(test)]` guards (`consumer.rs:1565-1624`) and the async positive
  phase cannot compile/run because of B1.
- Minor observation: `test_any_async_never_polled_stops_native_search` relies on the eager start
  behavior; it is consistent with the implementation, but the implementation report frames it as
  eager-start deliberately, so a future deferred-start alternative must update this test. No defect.

## 5. Panic / unwind and error-path audit

- Both `Any` panics are removed (`runtime.rs:41-55` returns `DiscoverySpecifier::Any`;
  `LolaConsumerBuilder::get_instance_specifier` no longer panics unconditionally). The legacy
  accessor still `.expect(...)`s for the `Any` case (`consumer.rs:1131-1139`) but is documented as
  defined only for `Specific`; `try_get_instance_specifier` (`consumer.rs:1141-1145`) returns
  `Err(ServiceNotFound)`. No fabricated producer specifier. This matches D1 and the honesty mandate.
- FFI callback boundaries keep `catch_unwind(...) → std::process::abort()` for both find-service and
  sample callbacks (`bridge_ffi_lola.rs:99-128`), so no unwind crosses the C++ boundary.
- No new public error variant: `ServiceFailedReason` already contains `FailedToStartDiscovery`
  (`error.rs:34-35`) and `ServiceNotFound`; downstream exhaustive matches are preserved.
- **Observed inconsistency (low/medium):** the sync `Any` path maps an unmapped/unsupported interface
  to `Err(ServiceError(ServiceNotFound))` (`consumer.rs:905-907`), but the async path maps a null
  start handle to `Err(ServiceError(FailedToStartDiscovery))` (`consumer.rs:1001-1002`). The plan's
  error table (§3.6) states unmapped interfaces should surface `ServiceNotFound`. There is no test for
  the async unmapped case, so this divergence is untested. It is a semantic ambiguity the reviewer
  should resolve (either align the reason or document that the async start-null maps to
  `FailedToStartDiscovery` deliberately).

## 6. Mapping-typing audit (registry UID vs native service path)

- The implementation correctly refuses to treat the registry UID (`BigDataInterface`) as the AUTOSAR
  service short-name path. Instead it adds explicit, backward-compatible metadata
  (`InterfaceOperations::Set/GetAnyInstanceSpecifier`, `registry_bridge_macro.h:600-623`) and a new
  opt-in macro; the 3-arg macro keeps an empty selector (`registry_bridge_macro.h:756-783`), so
  existing users are unaffected.
- `ResolveFindAnyIdentifier` validates that the selector resolves to exactly one identifier, binding
  `kLoLa`, with `GetServiceInstanceId()` unset (`registry_bridge_macro.cpp:80-99`); concrete,
  unsupported-binding, ambiguous, malformed and unmapped selectors return `nullopt → nullptr → Err`.
  This prevents silently returning `Specific` results under `Any` (a real risk the design closes).
- Rust side is thin and sound: `find_service_any`/`start_find_service_any` are declared in
  `bridge_ffi.rs:261-277`, implemented in `bridge_ffi_lola.rs:922-954` (correct `StringView` usage,
  null → `Err`), and mirrored in `bridge_ffi_mock.rs:201-207,423-429`.
- **Documented limitation (acceptable, but must stay explicit):** there is no general
  deterministic cross-record binding/version/quality resolver; only single-record resolution is
  supported and non-single maps to an error. The implementation report §5 records this honestly.
- **Unverified:** selector rejection, error reasons, exclusion and identity honesty are asserted by
  `consumer_app.rs:89-108,156-192` but were never executed.

## 7. Regression coverage audit (design vs mandate)

On inspection, the added regression is **discriminating by construction**:

- Provider manifest `etc/provider_config.json` offers two `BigDataInterface` instances
  (`/score/cp60/MapApiLanesStamped` id 1 and `/score/cp60/MapApiLanesStampedSecond` id 2) plus one
  `ComplexStructInterface` instance id 13 (`etc/provider_config.json:80-227`).
- Consumer manifest `etc/config.json` contains only the wildcard selector
  `/score/cp60/MapApiLanesStampedAny` (no `instanceId`, lines 120-145); it does **not** list
  `/score/cp60/MapApiLanesStampedSecond`. Two configured `Specific` instances therefore cannot produce
  the asserted "2 instances" result — it requires a genuine native wildcard.
- The exclusion case actually offers `ComplexStructInterface` from a provider process
  (`producer_app.rs:234-240`) and asserts it is not returned for the BigData Any query.
- `test_com_api_any_no_offer` asserts the documented `Ok(empty)` for a never-offered service type.
- Async is treated as one-shot; no continuous-stream claim; #1261 is explicitly out of scope.

**But none of it ran**, so `positive_regression_gap` is effectively "present but unexecuted/failed".
`native-check-summary.json` shows only 1 of the planned checks attempted; the enumeration in
`regression-plan.json` (unit tests, `runtime_test`, concept tests, sync/async Specific integration,
`find_any_semantics`, clippy/build) is entirely unexecuted.

## 8. API-compatibility audit (unchanged / additive)

On inspection the compatibility constraints hold:

- `ConsumerDescriptor::get_instance_specifier` signature is preserved; `try_get_instance_specifier`
  is additive with a provided default (`concept.rs:592-616`), so the mock runtime
  (`com-api-runtime-mock/runtime.rs`, untouched) and external implementors still compile.
- `score_com.rs:142-147` additively re-exports `ServiceFailedReason`.
- `FFIBridge` is internal; both implementors (`LolaFFIBridge`, `MockFFIBridge`/`SharedMockBridge`) are
  updated, and the mock forwards the two new methods (`bridge_ffi_mock.rs:201-207,423-429`).
- `impl/runtime.{h,cpp}`, `i_runtime.h`, `runtime_test.cpp`, `impl/BUILD` and the stale
  `impl/test/runtime_mock.*` paths were **not** touched, so no `IRuntime` vtable ABI change.
- **Unverified:** the Specific-compatibility and concept-mock tests never ran (blocked), so
  "unchanged behavior" is source-inspection only.

## 9. Preserved gaps, unknown IDs and ambiguity (retained, not resolved)

- **#250 broad-comment ambiguity:** the 2026-03-30 comment ("all available services on system")
  describes the #1261 system-wide heterogeneous stream, **not** this typed same-interface path. The
  implementation/plan record this honestly; the typed path must not be presented as solving it.
- **#1261 budget untouched:** no `find_all_services`, no interface-independent `ServiceDescriptor`, no
  new error enum. Confirmed in the diff surface.
- **Legacy accessor limitation:** `get_instance_specifier` on an `Any` result without a producer
  specifier is not non-panicking; callers must use `try_get_instance_specifier`. Documented in code
  (`consumer.rs:1131-1139`, `concept.rs:595-602`) and in the implementation report.
- **No general binding/version/quality resolver** across multiple compatible records (single-record
  only; rejected otherwise).
- **Async no-offer not awaited** (native `StartFindService` only fires the handler on non-empty known
  handles), so the async no-offer case is sync-only by design; documented in `implementation.md §5`.
- **Configuration dynamic-membership semantics not explicitly documented:** `Runtime` can extend
  configuration at runtime (`runtime.cpp:287-304`); the wildcard selector is re-resolved per query, so
  membership is a per-query snapshot, but this was not written down as a contract. Minor doc gap.
- **Preserved unknown native IDs** (no status invented): `SWP-253124` (FFI error handling),
  `Ticket-238828`, `Ticket-234827`, `Ticket-219876`, `Ticket-173043`, `Ticket-219132`,
  `Ticket-184255`, `Ticket-169333`, `Ticket-214582`, plus `SWS_CM_*`.
- **Stale permitted path preserved:** `score/mw/com/impl/test/runtime_mock.{h,cpp}` do not exist at
  this baseline (real mocks are `impl/runtime_mock.*` and `mocking/runtime_mock.*`).
- **Counter discrepancy (record only):** `task.json` states `before_source_corrections_used: 1`,
  `source_corrections_max: 3`, `source_fix_nodes_this_run: 1`; `native-check-summary.json` reports
  `source_corrections_used: 2`. The supervisor does not reconcile or retroactively accept any attempt.
- Historical failed attempts, patches and missing earlier supervisor reports remain sealed.

## 10. Failed / missing / unexecuted checks (explicit inventory)

| Planned check | Status |
| --- | --- |
| `.../consumer_any_apis/integration_test:test_com_api_any` | **FAILED TO BUILD** (E0560 B1; plus B2) |
| `.../com-api-runtime-lola:com-api-runtime-lola-tests` | not executed (blocked by B1) |
| `//score/mw/com/impl:runtime_test` | not executed |
| `//score/mw/com/rust/score_com_concept:score_com_concept-test` | not executed |
| `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests` | not executed |
| `.../consumer_sync_apis/integration_test:test_com_api_sync` | not executed |
| `.../consumer_async_apis/integration_test:test_com_api_async` | not executed |
| `.../find_any_semantics/integration_test:test_find_any_semantics` | not executed |
| `score_com_concept-macros-tests` (`manual`, gcc_15 doctest) | not executed / expected-omitted |
| clippy/build on the five touched crates | not executed |
| §5.1-use-after-discovery-drop and never-polled-drop regressions | written, **never run** |

No execution evidence exists for any planned check other than the one recorded build failure.

## 11. Required next action (recommendation only)

1. Apply the single remaining source correction to remove **B1** and **B2** (one line each).
2. Re-run the exact `test_com_api_any` target and the in-crate unit tests; then the Specific
   compatibility, `runtime_test`, concept tests and `find_any_semantics` targets.
3. If green, an authorized human decides engineering acceptance offline; this supervisor neither
   grants acceptance nor edits source.

No work product is qualified, released or accepted; no safety finding is closed; no comment/PR/merge
authority is exercised.
