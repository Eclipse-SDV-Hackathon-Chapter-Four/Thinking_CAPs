# Implementation — issue #250: typed Rust `FindServiceSpecifier::Any` (Linux only)

Status: **proposed engineering implementation only. Engineering acceptance is PENDING OFFLINE.**
No build, test, analyzer or integration run was executed in this stage (file-tool-only scope,
`shell`/`grep` blocked by the run guard). Nothing below is claimed as passing evidence.

Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Platform: Linux (LoLa/SHM). Model/editor: DeepSeek Flash only.
Source-correction nodes this run: 1, charged on implementation entry.
#1261 budget untouched; no public heterogeneous API implemented.

## 1. What was implemented

A typed, same-interface wildcard path:

- `runtime.find_service::<I>(FindServiceSpecifier::Any)` no longer panics. It returns a
  discovery object that enumerates **all currently offered instances of interface `I`** through a
  new native FFI path, excluding instances of other interfaces.
- The FFI cannot derive the native AUTOSAR service short-name from the registry UID
  (`BigDataInterface`). A new **explicit, backward-compatible registration macro** maps the
  registry UID to a configured find-any selector. The FFI does **not** trust the selector string:
  it resolves it through `IRuntime::resolve` and accepts it only when it maps to exactly one
  supported LoLa `InstanceIdentifier` whose instance id is unset
  (`InstanceIdentifierView.GetServiceInstanceId() == std::nullopt`). A selector that resolves to a
  concrete instance id (a misconfigured registration that would otherwise silently return Specific
  results under `Any`), an unsupported binding, an ambiguous match, a malformed string, or an
  unmapped interface is rejected with `nullptr` → `Err`. The validated wildcard
  `InstanceIdentifier` is what is delegated to the native `FindService` / `StartFindService`.
- Unknown / unmapped interfaces return `Err(ServiceError(ServiceNotFound))`; they never panic or
  `std::terminate`.
- The existing `Specific` path (results, errors, retry semantics) is preserved.

Non-goals explicitly not implemented: the #1261 system-wide, all-interface asynchronous stream and
its interface-independent `ServiceDescriptor` / `find_all_services` API. The typed
`find_service::<I>(Any)` path must not be read as satisfying #250's broad "all services on the
system" comment (2026-03-30) — that remains #1261 scope and is recorded here as unresolved.

## 2. Files changed

Library / FFI (all within permitted prefixes):

| File | Change |
| --- | --- |
| `score/mw/com/rust/score_com_concept/concept.rs` | Added additive, provided `ConsumerDescriptor::try_get_instance_specifier` (source-compatible; default forwards to `get_instance_specifier`). Legacy `get_instance_specifier` signature preserved. |
| `com-api-ffi-lola/bridge_ffi.rs` | Two new `FFIBridge` methods: `find_service_any(&str)`, `start_find_service_any(&FindServiceCallable, &str)`. |
| `com-api-ffi-lola/bridge_ffi_lola.rs` | `extern "C"` decls + impls for `mw_com_impl_find_service_any` / `mw_com_start_find_service_any`, wrapping the interface UID in `StringView`. |
| `com-api-ffi-lola/bridge_ffi_mock.rs` | `mock!` entries + `SharedMockBridge` forwarding for the two new methods. |
| `com-api-ffi-lola/registry_bridge_macro.h` | `InterfaceOperations` stores an explicit find-any selector (`Set/GetAnyInstanceSpecifier`, default empty = unsupported). New `BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER(id, proxy, skeleton, selector)`; the existing 3-arg macro is unchanged (empty selector). |
| `com-api-ffi-lola/registry_bridge_macro.cpp` | Implemented the two new `extern "C"` functions plus a shared `ResolveFindAnyIdentifier` validation helper. The helper looks up the registry selector, creates the `InstanceSpecifier`, resolves it through `IRuntime::resolve`, and accepts only a single supported LoLa identifier with an unset instance id. The validated `InstanceIdentifier` is delegated to the existing typed `FindService` / `StartFindService` (identifier overloads). Unknown/unmapped/concrete/unsupported/ambiguous/malformed selectors return `nullptr` (→ Rust `Err`). |
| `com-api-runtime-lola/runtime.rs` | `find_service` maps `Any` → `DiscoverySpecifier::Any` (panic removed) and `Specific` → `DiscoverySpecifier::Specific`. |
| `com-api-runtime-lola/consumer.rs` | `DiscoverySpecifier` enum; Any branches in sync/async discovery; builder identity; `try_get_instance_specifier` override; **owning stop guard** so a never-polled returned async future still stops the started search; new unit tests. |
| `score/mw/com/rust/score_com.rs` | Doc note updated; additive re-export of `ServiceFailedReason` so consumers can assert the exact propagated reason. |

Regression support:

| File | Change |
| --- | --- |
| `test/basic_rust_api/bigdata_com_api_gen.cpp` | `BigDataInterface` registered with the 4-arg macro using selector `/score/cp60/MapApiLanesStampedAny`; three synthetic test-only registrations (`ConcreteSelectorInterface` → a concrete configured instance, `MalformedSelectorInterface` → invalid string, `EmptySelectorInterface` → a valid never-offered service type) for selector-rejection and no-offer coverage. |
| `test/basic_rust_api/bigdata_com_api_gen.rs` | Matching `interface!` definitions for the three synthetic test-only interfaces. |
| `test/basic_rust_api/etc/config.json` | Added consumer-side find-any selector instance entries (BigData, no `instanceId`; plus a never-offered `/score/test/DummyAny` selector for the no-offer phase). |
| `test/basic_rust_api/etc/provider_config.json` (new) | Provider manifest offering two `BigDataInterface` instances (ids 1, 2) plus one `ComplexStructInterface` instance (id 13). |
| `test/basic_rust_api/etc/BUILD` | `config` filegroup now also ships `provider_config.json`. |
| `test/basic_rust_api/producer_app/producer_app.rs` | New `--config` option (default unchanged) and `-t find-any` case offering the two BigData instances and the ComplexStruct instance. |
| `test/basic_rust_api/consumer_any_apis/consumer_app.rs` (new) | Dedicated Any regression consumer. |
| `test/basic_rust_api/consumer_any_apis/BUILD` (new) | `bigdata-consumer-any` binary + `bigdata-com-api-any-pkg` package. |
| `test/basic_rust_api/consumer_any_apis/integration_test/BUILD` (new) | `test_com_api_any` integration target. |
| `test/basic_rust_api/consumer_any_apis/integration_test/com_api_any_api_test.py` (new) | Bounded producer/consumer supervision. |
| `.rust-queue/reports/regression-plan.json` (new) | Real added-target check plan. |

Not changed: `com-api-runtime-mock/runtime.rs` (the provided default keeps it compiling
unchanged); `impl/runtime.h`, `impl/i_runtime.h`, `impl/runtime.cpp`, `impl/runtime_test.cpp`,
`impl/BUILD`, `impl/test/runtime_mock.*` (the optional `IRuntime::resolve_any` hardening was **not**
needed, so no new virtual and no vtable ABI change). No protected file was touched.

## 3. Design decisions applied

- **D1 identity honesty.** `get_instance_specifier` keeps its exact signature. A new additive
  `try_get_instance_specifier` (provided default) returns `Err(ServiceNotFound)` when no producer
  specifier exists. `LolaConsumerBuilder` stores `Option<InstanceSpecifier>`: `Some` for `Specific`,
  `None` for `Any`. No producer specifier is fabricated. The legacy accessor is documented in code
  as defined only for the `Specific` path and may abort if used on an `Any` result; this limitation
  is recorded, not hidden. No blanket "all accessors are non-panicking" claim is made.
- **D2 explicit registration metadata.** The wildcard selector is per-interface, configured, and
  explicit. Unknown/unmapped interfaces return a documented `ServiceNotFound`. No
  `IRuntime::resolve_any` synthesis was added.
- **Lifetime (mandatory).** The selector resolves through `Runtime::resolve` to a deployment owned
  by the `Runtime` singleton's `Configuration`; every `HandleType` copies that `InstanceIdentifier`
  and therefore points at process-lifetime storage. Dropping the discovery object or the async
  future does not invalidate any returned builder/proxy. The consumer regression drops the
  discovery handle before building and using the proxy.
- **One-shot async (D4).** `get_available_instances_async` remains a first-callback snapshot; an
  empty first callback completes it. Later offers require a new search. No continuous-stream claim.
- **Async ownership (D5).** `FindServiceStopGuard` owns the native handle and calls
  `stop_find_service` exactly once on drop. It is created synchronously on a successful start and
  moved into `ServiceDiscoveryFuture`, so a returned future that is never polled still stops the
  search. This also fixes the pre-existing `Specific` leak. Applies to both paths.
- **No new error enum variant.** Existing `ServiceNotFound` / `InstanceSpecifierInvalid` variants
  are reused; downstream exhaustive matches are not broken.

## 4. Tests added

Native integration (`//score/mw/com/test/basic_rust_api/consumer_any_apis/integration_test:test_com_api_any`,
methods `test_com_api_any` and `test_com_api_any_no_offer`), actually exercising the new FFI path:

- multiple offered same-interface instances: the provider manifest offers **two**
  `BigDataInterface` instances, and the consumer asserts the wildcard returns exactly two;
- discriminating coverage: the second instance (`/score/cp60/MapApiLanesStampedSecond`) is **absent
  from the consumer configuration** (separate provider manifest), so two configured `Specific`
  instances could not produce this result;
- exclusion: a `ComplexStructInterface` instance is **actually offered** by a provider process and
  is not returned by the BigData wildcard query;
- error propagation / selector rejection — exact reason asserted, not `is_err`:
  - unmapped interface (3-arg registration, no selector) → `Err(ServiceError(ServiceNotFound))`;
  - **concrete-selector rejection:** `ConcreteSelectorInterface` is registered with a selector that
    resolves to `/score/cp60/MapApiLanesStamped` (a configured entry that has instance id 1); an
    `Any` query must return `Err(ServiceError(ServiceNotFound))` and must **not** silently return
    that Specific instance;
  - **malformed-selector rejection:** `MalformedSelectorInterface` is registered with the
    syntactically invalid selector `/bad//selector`; an `Any` query must return
    `Err(ServiceError(ServiceNotFound))`;
- `Specific` compatibility: the configured instance resolves and exposes its real specifier;
- identity honesty: each `Any` builder's `try_get_instance_specifier()` is `Err`;
- **sync lifetime:** the sync discovery handle is dropped, then a consumer/proxy is still built
  from a wildcard-discovered builder;
- **async one-shot snapshot:** `get_available_instances_async().await` on the same two-provider
  setup is asserted to return exactly two typed builders; the future and discovery are then dropped
  and a consumer built from an async-discovered builder subscribes and receives real samples
  (values asserted non-decreasing). This exercises the positive native Any async FFI path, which
  the mock cancellation tests do not.

A separate bounded **no-offer phase** (`test_com_api_any_no_offer`, no provider started) queries a
valid find-any selector for a service type that is never offered and asserts the documented native
outcome `Ok(empty)` with zero instances (`EmptySelectorInterface` → `/score/test/DummyAny`). It does
not assert an error, and it does not claim a continuous stream.

In-crate unit tests (`//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`,
`#[cfg(test)]` with `MockFFIBridge`):

- unmapped Any → `ServiceNotFound`, and the FFI receives the expected interface UID;
- never-polled Any discovery future drop → `stop_find_service` called exactly once;
- polled-pending Any discovery future cancellation → `stop_find_service` called exactly once.

The native C++ `//score/mw/com/test/find_any_semantics` remains the unchanged per-service ANY
reference. Bounded supervision reuses `pkg_application` / `integration_test` / `wrap_exec` with an
explicit `wait_timeout`; no unbounded sleeps or joins, no mocked-only pass.

## 5. Remaining gaps and preserved unknowns

- **No execution.** Tests were written but not run (board/guard scope). No check is claimed passed;
  engineering acceptance remains `pending_offline`.
- **One configured selector per interface.** A single find-any selector resolves to one configured
  entry. The selector is validated at query time to be a genuine LoLa wildcard (exactly one
  identifier, LoLa binding, unset instance id); concrete, unsupported, ambiguous, malformed or
  unmapped selectors are rejected explicitly. The design still does not implement a general
  deterministic binding/version/quality resolver across multiple compatible records, and is not
  claimed as one.
- **Empty/no-offer.** The sync native outcome is `Ok(empty)`
  (`ServiceDiscoveryClient::FindService` returns `GetKnownHandles(...)`, which is a successful empty
  container when the wildcard crawl finds no instances — `service_discovery_client.cpp:912-931`).
  The `test_com_api_any_no_offer` phase asserts exactly that. The *async* no-offer case is
  deliberately not awaited: the native `StartFindService` only invokes the handler when known
  handles are non-empty (`service_discovery_client.cpp:767-775`), so a no-offer async query stays
  pending until an offer; hence the no-offer phase is sync-only and the one-shot async snapshot is
  exercised only in the two-provider positive phase.
- **Legacy accessor limitation.** `get_instance_specifier` on an `Any` result without a producer
  specifier is not non-panicking; callers must use `try_get_instance_specifier`. This is documented
  and recorded here.
- **#250 broad-comment ambiguity.** The 2026-03-30 "all available services on system" expectation is
  not solved by the typed path; it is #1261 scope and was not implemented.
- **#1261 budget untouched**, no public heterogeneous API, no `ServiceDescriptor`, no new error-enum
  variant.
- **Unresolved native IDs preserved** (no status invented): `SWP-253124` (FFI error handling),
  `Ticket-238828`, `Ticket-234827`, `Ticket-219876`, `Ticket-173043`, `Ticket-219132`,
  `Ticket-184255`, `Ticket-169333`, `Ticket-214582`, plus the `SWS_CM_*` ids referenced natively.
- **Stale permitted paths preserved**: `score/mw/com/impl/test/runtime_mock.{h,cpp}` do not exist at
  this baseline; no attempt was made to edit them.
- Historical failed attempts, patches and missing supervisor reports remain sealed and are not
  retroactively accepted or overwritten.

## 6. Reviewer follow-up applied in the same source stage

A live source audit raised two points. Both were fixed in this same admitted source stage (no new
correction node consumed):

1. A registration string resolving to a configured entry with an `instanceId` could silently return
   Specific results under `Any`. `registry_bridge_macro.cpp` now resolves the selector through
   `IRuntime::resolve` and accepts it only when it yields exactly one `InstanceIdentifier` whose
   deployment binding is `kLoLa` and whose `InstanceIdentifierView::GetServiceInstanceId()` is
   `std::nullopt`. The validated `InstanceIdentifier` (not the specifier) is delegated to
   `FindService` / `StartFindService`. Concrete, unsupported-binding, ambiguous, malformed and
   unmapped selectors are rejected with `nullptr` → `Err`.
2. The regression was sync-only and the error assertions were weak. `test_com_api_any` now also
   awaits the **async** one-shot Any snapshot on the same two-provider setup and asserts it returns
   exactly two typed results and remains usable after completion/drop (real samples received);
   rejection assertions now match the exact `ServiceError(ServiceNotFound)` reason; a deterministic
   bounded **no-offer** phase (`test_com_api_any_no_offer`) asserts the documented native
   `Ok(empty)` for a never-offered service type. New test-only registrations:
   `ConcreteSelectorInterface`, `MalformedSelectorInterface`, `EmptySelectorInterface`.

## 7. Explicit non-claims

No work product is marked qualified, released or accepted; no safety finding is closed. A green
future run of the listed tests would not supply engineering acceptance. No comment/PR/merge/release
authority is exercised.
