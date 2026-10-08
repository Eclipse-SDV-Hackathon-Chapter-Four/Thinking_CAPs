# Implementation — issue #250 final authorized correction: typed Rust `FindServiceSpecifier::Any`

Status: **proposed engineering implementation only. Engineering acceptance remains PENDING OFFLINE.**
No build/test/analyzer ran in this stage (file-tool-only scope). Nothing here is claimed as passing
evidence; compiling or lifecycle success is not test success. Model/editor: DeepSeek Flash only.

Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Platform: Linux (LoLa/SHM).
This is source-correction #3/3 for #250 (charged on entry). #1261 source budget stays 1/3 and the
separate #560 Codex allowance 1/3; no #1261 source edit was made.

## 1. Exact repairs in this stage

1. **Rust E0560 field mismatch (S1).** `com-api-runtime-lola/consumer.rs` constructed
   `ServiceDiscoveryFuture { find_guard, .. }` while the field is `_find_guard`. Now initialized as
   `_find_guard: find_guard,`. The owning `FindServiceStopGuard` is created synchronously on a
   successful start and moved into the outer future, so the never-polled-drop / polled-pending
   cancellation guarantee is preserved (no guard was removed).
2. **C++ macro declaration (S2).** `com-api-ffi-lola/registry_bridge_macro.h` line ~824 declared
   `id##_interface_reg_instance;` at namespace scope in the new 4-argument macro. It now matches the
   3-argument macro: `id##_InterfaceRegistrationHelper id##_interface_reg_instance;`. The 4-arg macro
   is live (BigData + three selector-test registrations), so this was a real build blocker.
3. **Discriminating per-instance regression (S5).** The producer's find-any case now sends a
   *distinct per-provider marker* in `MapApiLanesStamped::x` (`MARKER_FIRST*1000 + i` vs
   `MARKER_SECOND*1000 + i`). The consumer builds, subscribes and receives from **both** returned
   builders (sync and async), and asserts the **unordered** marker sets: each builder maps to exactly
   one provider, the two differ, and their union is `{1, 2}`. This exercises the instance absent from
   the consumer configuration and cannot pass if the same instance is returned twice or if handle
   order is relied on.
4. **Other-interface readiness barrier (S5).** Before asserting the BigData wildcard excludes the
   offered `ComplexStructInterface`, the consumer positively observes that instance via a real
   `Specific` discovery (bounded loop + deadline), instead of a sleep. The exclusion is therefore not
   vacuous under scheduling.
5. **Identity documentation (S6).** `ConsumerDescriptor::get_instance_specifier` /
   `try_get_instance_specifier` docs and the LoLa impl comment now state that a `Specific` result
   carries the **caller-supplied query alias**, not an authenticated unique producer identity; that
   `Any` results for non-local instances have no producer specifier; that the fallible accessor is the
   supported path for `Any`; and that the provided default merely forwards to the legacy accessor
   (it cannot guarantee error-on-absence for third-party implementors).
6. **Stop-guard honesty (S6/S7).** The exactly-once native stop guard is retained and required, but
   no full callback-allocation reclamation is claimed: the baseline find-service
   `RustBoxedCallable` specialization has an empty `dispose` and the erased `FindServiceCallable` has
   no `Drop`, so the exactly-once `stop_find_service` proof does **not** imply every boxed
   callback/closure is freed.

Also inspected for further compile blockers (no code change needed): the 4-arg macro call sites in
`bigdata_com_api_gen.cpp`; `Runtime::getInstance().resolve(InstanceSpecifier)`, the
`FindService(InstanceIdentifier)` / `StartFindService(handler, InstanceIdentifier)` overloads,
`InstanceIdentifierView::GetServiceInstanceId()` / `GetServiceInstanceDeployment().GetBindingType()`,
`BindingType::kLoLa`, `InterfaceOperations::Set/GetAnyInstanceSpecifier`, and the mock/`SharedMockBridge`
forwarders for `find_service_any` / `start_find_service_any` all exist with matching signatures.

## 2. What the implementation does (unchanged design)

- `runtime.find_service::<I>(Any)` is a typed, same-interface wildcard. The FFI resolves the
  interface registry UID to its explicitly registered configured selector
  (`BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER`), validates via `IRuntime::resolve` that it maps
  to exactly one LoLa `InstanceIdentifier` with unset instance id, and forwards that identifier to the
  native `FindService` / `StartFindService`. Concrete-id, malformed, ambiguous, unsupported-binding and
  unmapped selectors return `nullptr` → `Err(ServiceNotFound)` (never a silent Specific result, never
  `std::terminate`). `Specific` is preserved.
- Runtime-owned configuration lifetime: the resolved `InstanceIdentifier` points at the Runtime
  singleton's stable `Configuration`, so dropping discovery/async future never invalidates returned
  builders or proxies.
- Async is a one-shot first-callback snapshot (empty first callback completes it); later offers need a
  new search. This is distinct from #1261's heterogeneous updating stream.

## 3. Tests (written; not run — no pass is claimed)

- `//score/mw/com/test/basic_rust_api/consumer_any_apis/integration_test:test_com_api_any`
  (`test_com_api_any`, `test_com_api_any_no_offer`): exact unmapped / concrete-selector /
  malformed-selector `ServiceNotFound`; ComplexStruct readiness barrier; sync wildcard = exactly two
  offered BigData instances (second absent from consumer config); both sync builders built/subscribed
  and both markers observed; Specific compatibility; no fabricated Any specifier; sync lifetime after
  discovery drop; async one-shot snapshot = two builders with both markers after future/discovery
  drop; separate no-offer phase asserting documented `Ok(empty)`.
- `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`: unmapped Any →
  `ServiceNotFound`; never-polled future drop → `stop_find_service` exactly once; polled-pending
  cancellation → `stop_find_service` exactly once (mock stop counter, not real callback quiescence).
- All waits are bounded by explicit deadlines; the integration test also supervises both processes via
  `wait_timeout`.

## 4. Source / API tradeoffs and unmeasured limitations

- **One configured selector per interface.** The design validates a single registered selector; it is
  not a general binding/version/quality resolver over multiple compatible records, and never invents a
  producer name from a registry UID. A misconfigured selector that resolves to several identifiers is
  rejected rather than resolved.
- **`Specific` alias is not identity.** Native `Specific` queries may themselves reference a
  configured wildcard and return several handles carrying the same caller alias; concrete native ids
  remain inside the handle and are not asserted by the new Rust regression.
- **Legacy accessor.** `get_instance_specifier()` on an `Any` result for a non-local instance is not
  non-panicking; callers must use `try_get_instance_specifier()`. The provided default of the fallible
  accessor forwards to the legacy method, so absence-as-error is not universal across implementors.
- **ABI.** No new `IRuntime` virtual was added here, so no vtable change is claimed or made. Earlier
  private fields / mandatory `FFIBridge` methods (`find_service_any`, `start_find_service_any`) still
  leave external source-compatibility for downstream implementors unproven by in-repo builds.
- **Callback allocation.** Exactly-once native stop is proven only for the stop path; boxed
  callback/closure reclamation is not proven (inherited empty find-service `dispose`).
- **Unmeasured.** No native build, test, doctest, lint or analyzer result exists for this source.
  #250's broad "all services on the system" comment, #1261 heterogeneous stream, qualification/trace/
  applicability and authorized offline acceptance remain open.

## 5. Non-claims

No work product is marked qualified, released or accepted; no safety finding is closed. A green future
run of these tests would not supply engineering acceptance. No protected module/lock/license/policy
file was modified. Historical failed attempts, patches and missing reports remain sealed.
