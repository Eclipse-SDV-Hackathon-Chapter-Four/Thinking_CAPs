# Plan — issue #250: typed Rust `FindServiceSpecifier::Any` for LoLa (Linux only)

Status: **proposed engineering implementation only. Engineering acceptance is PENDING OFFLINE.**
This stage writes only this report. Source editing is not permitted in this stage (the run guard
blocks `shell`/`grep`/source edits); no source was modified and no build/tests were executed.
This document is the concrete implementation contract to be applied by the single source-correction
node, and it incorporates the mandatory lifetime refinement from
`.rust-queue/context/task.json` (`mandatory_lifetime_refinement`).

## 0. Run binding

| Item | Value |
| --- | --- |
| Issue | eclipse-score/communication #250 — "Improvement: COM-API FindServiceSpecifier::Any support" (label `rust-api`, state open) |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Platform | Linux only (LoLa/SHM) |
| Model / editor | DeepSeek Flash only (Codex read-only review, operator preparation) |
| Stage scope | read (max 200-line reads) + report only; source correction deferred to the single correction node |
| Source-correction budget | 1 correction node this run (`source_fix_nodes_this_run: 1`), charged on implementation entry |
| Historical corrections | #250 used `before_source_corrections_used: 1` of `source_corrections_max: 3`; original retries already exhausted elsewhere are unchanged |
| #1261 budget | must NOT be spent; public heterogeneous API must NOT be implemented here |
| Acceptance | `engineering_acceptance: pending_offline` — no automatic acceptance |
| Mandatory refinement | `mandatory_lifetime_refinement` (see §3.5) — deployment owner must outlive **all** retained builders/proxies after discovery drop |
| Compatibility constraint | existing `ConsumerDescriptor::get_instance_specifier` signature preserved; additive fallible accessor; Specific source compatibility required |
| API/async refinements | `mandatory_api_and_async_refinements` (see §3.1 one-shot async, §3.7 descriptor, §3.8 never-polled drop) |
| Discriminating regression | `mandatory_discriminating_regression`: ≥1 offered same-interface instance absent from consumer config; other interface actually offered; deterministic compatible binding/version/quality or explicit error |
| Decision authority | proposed decisions made within delegated authority; no approval/wait nodes; engineering acceptance still pending offline |

Protected inputs (`MODULE.bazel`, `MODULE.bazel.lock`, `Cargo.lock`, `LICENSE`, `NOTICE`,
`.bazelrc`) remain untouched. No toolchain, policy, lock or license changes. No new Cargo
scaffolding; changes stay in the native Bazel build.

## 1. Goal and scope

Deliver a **typed, same-interface wildcard discovery** on the Rust COM-API:

- `runtime.find_service::<I>(FindServiceSpecifier::Any)` must **not** panic and must return
  **all currently offered instances of interface `I`** (across all instance ids of `I`),
  excluding instances of other interfaces.
- Both `get_available_instances()` (sync snapshot) and `get_available_instances_async()` must
  work for `Any`. **Corrected semantics:** the existing async query is a **one-shot initial
  snapshot** — `ServiceDiscoveryFuture::poll` (consumer.rs:1031-1049) returns `Ready` on the
  **first** callback, even when the container is empty, and the future is then dropped/stopped.
  It is **not** a continuously updating stream and must not be claimed as one; observing services
  offered later requires starting a new search. A heterogeneous continuously-updating stream
  remains #1261.
- Each returned builder must continue to build a working consumer/proxy for that concrete
  instance **even after the discovery handle/future is dropped** (mandatory lifetime refinement).
- `FindServiceSpecifier::Specific(spec)` behaviour (results, errors, retry semantics,
  `get_instance_specifier` for real instances) must remain compatible.

Explicit non-goals / non-claims:

- This is **not** a system-wide, all-interface service stream. #250's 2026-03-30 comment
  ("all the available services on system should be returned as a list") is the #1261 scope.
  The typed `find_service::<I>(Any)` path only enumerates instances **of one interface `I`**.
  This plan records that ambiguity honestly and does not claim #250's broad interpretation is
  solved.
- #1261 (`find_all_services` / interface-independent `ServiceDescriptor` stream) is a separate
  follow-on; its public API and error-enum changes are **not** implemented here (see §11).

## 2. Grounded native evidence (inspected at baseline)

LoLa already implements genuine per-service find-any; only the Rust/FFI path is missing.

1. `score/mw/com/impl/bindings/lola/service_discovery/flag_file_crawler.cpp:169-199` — if the
   `EnrichedInstanceIdentifier` has no `LolaServiceInstanceId` (`instance_id_ == nullopt`), the
   crawler enumerates **all instance directories under the service directory** and watches each.
   Comment at :176 "We are in a find-any search".
2. `score/mw/com/impl/i_service_discovery.h:43-51` — `FindService`/`StartFindService` overloads
   take `InstanceSpecifier` and `InstanceIdentifier`; the `InstanceIdentifier` overload is the
   wildcard-capable path.
3. `score/mw/com/impl/service_discovery.cpp:325-335` — `FindService(InstanceIdentifier)` forwards
   the (possibly instance-id-less) `InstanceIdentifier` to the binding client. The
   `InstanceSpecifier` overload (:343-373) first `resolve()`s specifiers to identifiers.
4. `score/mw/com/impl/configuration/lola_service_instance_deployment.h:66` —
   `std::optional<LolaServiceInstanceId> instance_id_`; a `ServiceInstanceDeployment` with it
   cleared is the genuine per-service ANY request.
5. `score/mw/com/impl/instance_identifier.h:135-136,155-183` — `InstanceIdentifier` stores
   **raw non-owning pointers** `const ServiceInstanceDeployment*` / `const ServiceTypeDeployment*`
   into the global `Configuration`; `:179-181` documents that deployments reconstructed from a
   serialized identifier are added to that configuration so the pointers stay valid.
   `make_InstanceIdentifier()` (:220-224) takes references; `InstanceIdentifierView` (:234-256)
   exposes `GetServiceInstanceId()`, `GetServiceInstanceDeployment()`, `GetServiceTypeDeployment()`.
6. `score/mw/com/impl/handle_type.h:41,101-117` + `score/mw/com/impl/handle_type.cpp:52-53` —
   `HandleType` embeds `InstanceIdentifier` **by value** plus a `ServiceInstanceId instance_id_`;
   the constructor stores the identifier as-is, so every handle copies the query's non-owning
   deployment pointers. The per-instance id discovered by ANY lives in `instance_id_`; there is
   **no producer `InstanceSpecifier`** on the handle for unconfigured providers.
7. `score/mw/com/impl/bindings/lola/service_discovery/known_instances_container.cpp:84-85`
   (mandated source) — wildcard results are built with
   `make_HandleType(enriched_instance_identifier.GetInstanceIdentifier(), ServiceInstanceId{...})`,
   i.e. every returned handle copies the **query** `InstanceIdentifier` and therefore points at the
   deployment owned by whoever supplied the query. This is the concrete mechanism behind the
   mandatory refinement.
8. `score/mw/com/impl/runtime.h:98` + `i_runtime.h:39-55` — `Runtime::getInstance()` returns
   `IRuntime&`; `IRuntime` exposes only `resolve(InstanceSpecifier)`, `GetBindingRuntime`,
   `GetServiceDiscovery`, tracing. `Configuration configuration_` is **private to `Runtime`**
   (`runtime.h:179`) and there is no `static_cast` bypass allowed.
9. `score/mw/com/impl/runtime.cpp:258-285` — `Runtime::resolve` builds
   `make_InstanceIdentifier(instance_deployment.value().get(), type_deployment.value().get())`
   from **Configuration-owned** deployments. This is the stable owner for the config-resolved
   path.
10. `score/mw/com/impl/configuration/configuration.h:83-87,131,153` — public:
    `AddServiceTypeDeployment`, `AddServiceInstanceDeployments`, `GetServiceTypeNames()`,
    `GetInstancesOfServiceType(name)`, `GetServiceTypeDeployment(id)`,
    `GetServiceInstanceDeployment(specifier)`. **Private** (confirmed): `GetServiceTypes()` (:160),
    `GetServiceInstances()` (:166), `ForEachServiceType/Instance` (:173-208). `MergeServiceEntries`
    extends configuration dynamically (`AddConfiguration`) and keeps prior generations alive in
    stable per-generation maps (`:249-271`), so existing pointers stay valid.
11. `score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h:644-717` — the FFI
    registry maps an **interface UID string** (e.g. `BigDataInterface`, from
    `BEGIN_EXPORT_MW_COM_INTERFACE`, :735-762) to `InterfaceOperations`
    (`CreateProxy`/`CreateSkeleton`, :561-639). This registry UID is **not** the native AUTOSAR
    service short-name path (`/score/adp/MapApiLanesStamped` in
    `score/mw/com/test/basic_rust_api/etc/config.json:4`). There is no ServiceTraits-style name
    mapping in the template (`AsProxy`) layer.
12. `registry_bridge_macro.cpp:395-525` — existing FFI find paths
    (`mw_com_start_find_service`, `mw_com_impl_find_service`) accept **only `InstanceSpecifier`**;
    there is no ANY entry point.
13. `score/mw/com/test/find_any_semantics/*` — native per-service ANY client uses
    `TestDataProxy::FindService(instance_specifier)` with a client config entry whose
    `instances[]` omits `instanceId` (`config/client/mw_com_config.json:31-44`), i.e. an
    `InstanceIdentifier` with `instance_id_ == nullopt`; two offered instances of the same
    service are returned.
14. `score/mw/com/impl/rust/com-api/com-api-runtime-lola/runtime.rs:40-52` — the current Rust
    `find_service` **panics** on `Any`; `consumer.rs:1070-1078` — `LolaConsumerBuilder::
    get_instance_specifier` **panics unconditionally**.
15. `score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs:74-86,406-413,458-463` — the
    mock runtime ignores the specifier; mock `get_instance_specifier` returns a stored specifier.
16. `score/mw/com/impl/runtime_mock.h:27-35` — `RuntimeMock : IRuntime` uses `MOCK_METHOD` for
    every current pure virtual.
17. `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs:857-1055` — discovery
    builders wrap `Arc<NativeHandleContainer>` (`LolaConsumerInfo`); the builder therefore keeps
    the native handle container alive, but the handle container's `HandleType`s still carry the
    non-owning deployment pointers, so the *deployment* owner (not the handle container) is what
    must outlive builders/proxies.
18. `consumer.rs:1031-1049` — `ServiceDiscoveryFuture::poll` returns `Ready` on the **first**
    callback, even when the container is empty; the async query is therefore a one-shot initial
    snapshot, not a continuously updating stream.
19. `consumer.rs:953-965` vs `:966-979` — `get_available_instances_async` starts the native search
    before returning the outer `async move` block; the inner `ServiceDiscoveryFuture` (the only
    owner whose `Drop` calls `stop_find_service`, `:998-1009`) is constructed only on first poll
    (`:971`). `NativeFindServiceHandle` has no `Drop`, so a never-polled returned future leaks the
    started search (§3.8).

### Preserved unknowns / missing evidence (not resolved by this plan)

- The permitted-file list names `score/mw/com/impl/test/runtime_mock.{h,cpp}`, which **do not
  exist** at this baseline. Real mocks are `score/mw/com/impl/runtime_mock.{h,cpp}` and
  `score/mw/com/mocking/runtime_mock.{h,cpp}`. Recorded as a stale/unknown path; the recommended
  design avoids needing to edit files outside the permitted set (non-pure `IRuntime` virtual).
- Carried, unresolved native IDs (no status invented): `SWP-253124` (FFI error handling),
  `Ticket-238828`, `Ticket-234827`, `Ticket-219876`, `Ticket-173043`, `Ticket-219132`,
  `Ticket-184255`, `Ticket-169333`, `Ticket-214582`, plus `SWS_CM_*` ids referenced natively.
- No fresh native test/analyzer evidence was produced by this stage; missing historical
  supervisor reports and failed original attempts remain sealed and are not overwritten.

## 3. Proposed implementation contract

### 3.1 Rust public API semantics (typed, same-interface)

- `Runtime::find_service::<I>(FindServiceSpecifier::Any)` returns `I`'s `ServiceDiscovery<I>`
  without panicking.
- `ServiceDiscovery::get_available_instances()` on the Any handle returns `Ok(Vec<builder>)`
  with one builder per currently offered instance of `I`; `Ok(vec![])` when none are offered.
- `get_available_instances_async()` is a **one-shot initial snapshot**: it returns a future that
  resolves to the first native callback's container (which may be empty) and then stops the
  search. It does not keep delivering later updates; a later-offered service is only observed by
  starting a new search. Any use of the word "async stream" for this API is rejected.
- Dropping the discovery handle/future must **not** invalidate any already-returned builder, nor
  any consumer/proxy built from it (§3.5).
- The returned async future must **own/stop the native search even if it is never polled** (§3.8).
- `FindServiceSpecifier::Specific(spec)` keeps the current code path and observable behaviour.

### 3.2 FFI ABI additions

New C++ `extern "C"` (implemented in
`score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.cpp`, declared Rust-side
in `bridge_ffi_lola.rs`):

```c
// Sync wildcard find for a registered interface UID.
// Returns a heap ServiceHandleContainer<HandleType>* (owned by Rust, freed via
// mw_com_impl_handle_container_delete) or nullptr on failure/unknown interface/
// missing find-any registration.
ServiceHandleContainer<HandleType>* mw_com_impl_find_service_any(StringView interface_id);

// Async wildcard find. Callback FatPtr has the SAME erased signature already used by
// mw_com_start_find_service: void(ServiceHandleContainer<HandleType>, FindServiceHandle).
// Returns heap FindServiceHandle* (stopped+deleted via mw_com_stop_find_service) or nullptr.
void* mw_com_start_find_service_any(const FatPtr* callback, StringView interface_id);
```

No callback ABI change: reuse `RustBoxedCallable<void, std::vector<HandleType>, FindServiceHandle>`
(`registry_bridge_macro.h:172-190`) and `FindServiceCallable`. Reuse
`mw_com_impl_handle_container_delete|get_size|get_handle_at` and `mw_com_stop_find_service`.

Rust `FFIBridge` trait additions (`bridge_ffi.rs`):

```rust
fn find_service_any(&self, interface_id: &str) -> Result<HandleContainer, ()>;
fn start_find_service_any(
    &self,
    callback: &FindServiceCallable,
    interface_id: &str,
) -> *mut FindServiceHandle;
```

Implement in `bridge_ffi_lola.rs` (extern decls + `StringView::from(interface_id)`) and mirror in
`bridge_ffi_mock.rs` (add to the `mock!` block and forward in `SharedMockBridge`).

### 3.3 Registration metadata (backward compatible, explicit)

The FFI cannot derive the native AUTOSAR service short-name path from the registry UID. Add
**explicit, optional registration metadata** that maps interface UID → a configured find-any
`InstanceSpecifier` (a "wildcard selector" whose configuration instance entry omits `instanceId`):

- `InterfaceOperations` (registry) gains a stored `std::string_view any_instance_specifier_` with
  `SetAnyInstanceSpecifier` / `GetAnyInstanceSpecifier`. Default empty = find-any unsupported.
- New 4-argument macro `BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER(id, proxy, skeleton,
  any_instance_specifier)` alongside the existing 3-argument `BEGIN_EXPORT_MW_COM_INTERFACE`.
  Existing 3-arg users compile and behave exactly as today.
- New FFI functions look up the interface registry, read the wildcard selector, convert it with
  `InstanceSpecifier::Create(std::string{...})`, and delegate to the **existing** typed native
  paths `GetServiceDiscovery().FindService(instance_specifier)` /
  `StartFindService(handler, instance_specifier)`. Those resolve the selector through
  `Runtime::resolve` to an `InstanceIdentifier` whose `LolaServiceInstanceDeployment.instance_id_`
  is `nullopt`, yielding a single genuine per-service ANY query (not a per-instance loop).
- If an interface is registered with the 3-arg macro (no selector) or its selector is unknown to
  the loaded configuration, the ANY FFI returns `nullptr` → Rust `Err` (documented
  "unmapped-interface error"), never `panic!`/`std::terminate`.
- Update `score/mw/com/test/basic_rust_api/bigdata_com_api_gen.cpp` to use the new macro for
  `BigDataInterface` with the configured wildcard selector; other interfaces stay 3-arg.

**Alternative (hardening proposal, see §9 D2):** add a non-pure `IRuntime::resolve_any(
std::string_view service_type_name)` that synthesizes a wildcard deployment for a service type
even when no wildcard selector is configured. This is only needed for service types that have no
usable configured instance entry; it is not required for the recommended design and is deferred.

### 3.4 Where the wildcard deployment comes from

Two consistent options; both keep the deployment in **stable, process-lifetime, runtime-owned**
storage:

1. **Recommended — configuration-resolved selector** (no `Runtime` code change): the queried
   `InstanceIdentifier` is produced by `Runtime::resolve` from the configuration deployment of the
   registered selector. Its `ServiceInstanceDeployment`/`ServiceTypeDeployment` are owned by the
   `Runtime` singleton's `Configuration` (`runtime.cpp:258-285`,
   `configuration.h:249-271` generation maps keep old entries alive). Every handle copies the
   `InstanceIdentifier` (`handle_type.cpp:52-53`) and so points into that process-lifetime storage.
2. **Hardening — synthesized wildcard under Runtime ownership**: if metadata instead identifies a
   service type, `Runtime::resolve_any` copies a configured instance deployment, clears the Lola
   `instance_id_`, stores the copy in a `Runtime`-owned address-stable container
   (`std::deque<ServiceInstanceDeployment>` / `std::list` / heap node; **never** a relocating
   `std::vector`), and returns `make_InstanceIdentifier(*stored, type_deployment)`. `std::deque`
   reference stability on `push_back` guarantees the stored pointer never moves. This **allocates
   one deployment copy per service type on first query** unless it is explicitly initialized
   beforehand; it must not be described as zero-runtime-allocation.

In both options the returned `InstanceIdentifier` and every `HandleType`/builder/proxy derived
from it point at storage owned by the `Runtime` singleton, which outlives all of them.

### 3.5 Ownership / drop policy (MANDATORY lifetime refinement)

Mechanism (mandated): `known_instances_container.cpp:84-85` builds each wildcard result as
`make_HandleType(enriched_instance_identifier.GetInstanceIdentifier(), ...)`; `HandleType` stores
that `InstanceIdentifier` by value (`handle_type.cpp:52-53`); `InstanceIdentifier` holds
**non-owning** pointers to the query's `ServiceInstanceDeployment`/`ServiceTypeDeployment`
(`instance_identifier.h:135-136,179-181`). Therefore every handle returned by an ANY query points
at the deployment that was supplied to the query.

Required invariant:

- The deployment owner MUST remain alive through **all retained builders and proxies**, i.e. for
  the whole lifetime of every `ConsumerBuilder` produced from the query and every consumer/proxy
  built from those builders — **including after the discovery handle and, for async, the
  `ServiceDiscoveryFuture` have been dropped**.
- Ownership scoped only to the synchronous call, only to `StopFindService`, or only to the
  discovery object/future is **insufficient** and is rejected.
- Recommended: stable **runtime-owned** deployment storage (Configuration, or a Runtime-owned
  address-stable container), because it outlives every emitted handle/builder/proxy and requires
  no changes to `HandleType`/`InstanceIdentifier`.
- Acceptable alternative: shared ownership propagated through every emitted handle, builder and
  created proxy. This would require threading an owner (e.g. `std::shared_ptr`) through
  `HandleType`/`InstanceIdentifier` and the Rust builder/proxy types; because those are broad
  C++/ABI types, the runtime-owned route is preferred.
- Never return an identifier that points to a stack/local/relocated object.
- The Rust builder already retains `Arc<NativeHandleContainer>` (`consumer.rs:857-1055`), which
  keeps the native handle container alive; this is necessary but **not sufficient** — the
  *deployment* owner is what the mandate targets, so it is owned at the Runtime layer.

Drop/lifetime edges to enforce and test:

- Sync ANY: returned `HandleContainer` owns the native handle vector only; the deployment stays
  owned by `Runtime`.
- Async ANY: `ServiceDiscoveryFuture` captures the `find_handle` synchronously and its `Drop`
  calls `stop_find_service` (`consumer.rs:998-1009`); callbacks are quiesced before the handle is
  deleted. Deployment ownership is independent of this and survives the drop.
- Concurrency: if option 2 is used, `resolve_any` must synchronize its container with a mutex;
  the recommended option 1 relies on Configuration's existing atomic generation reads.

### 3.6 Error policy

- Do **not** add a new `ServiceFailedReason` variant: adding one breaks exhaustive downstream
  `match`es. Reuse existing variants (`ServiceNotFound`, `InstanceSpecifierInvalid`).
- Mapping:
  - unknown interface UID / no ANY metadata → FFI `nullptr` → `Err(ServiceError(ServiceNotFound))`.
  - interface mapped but selector/service type absent from configuration (unmapped-interface
    error) → `Err(ServiceError(ServiceNotFound))`.
  - no offered instances → `Ok(empty)` (sync) / initial callback with empty container (async).
  - underlying binding failure → `Err(ServiceError(ServiceNotFound))` (current FFI error surface;
    proper propagation is `SWP-253124`, carried unresolved).
- Remove both `panic!`s on the Any path (`runtime.rs:43`, `consumer.rs:1074`).

### 3.7 Identity / descriptor policy (no fabricated producer specifier)

Operator compatibility constraint applied: **the existing public
`ConsumerDescriptor::get_instance_specifier(&self) -> &InstanceSpecifier` signature is preserved;
it is not replaced with `Result`.** Decisions below are made within delegated authority (no
approval/wait nodes).

Native handles expose an `InstanceIdentifier` + actual `instance_id`, but **no producer
`InstanceSpecifier`** for unconfigured providers. Contract:

- `LolaConsumerBuilder` stores the identity explicitly: `Specific(InstanceSpecifier)` (the
  discovery object already holds it) or `Any` (wildcard discovery).
- `get_instance_specifier` keeps its signature and returns the concrete specifier for the
  `Specific` path (this also removes the current *unconditional* panic by storing the resolved
  specifier on the builder).
- **Additive fallible accessor with a provided default** (source-compatible for existing
  implementors):
  ```rust
  pub trait ConsumerDescriptor<R: Runtime + ?Sized> {
      fn get_instance_specifier(&self) -> &InstanceSpecifier;

      /// Returns the instance specifier when the COM API can name one for this instance.
      ///
      /// Returns `Err(ServiceError(ServiceFailedReason::ServiceNotFound))` when the discovered
      /// instance has no producer instance specifier known to this process (e.g. a find-any
      /// result for an instance that is not in the local configuration).
      fn try_get_instance_specifier(&self) -> Result<&InstanceSpecifier> {
          Ok(self.get_instance_specifier())
      }
  }
  ```
  The LoLa builder overrides `try_get_instance_specifier`: `Ok(spec)` for `Specific`,
  `Err(ServiceFailedReason::ServiceNotFound)` for `Any`.
- **Legacy-accessor limitation is explicit** and must be stated in implementation docs and in the
  final gaps report: `get_instance_specifier` cannot truthfully name an `Any` result that has no
  producer specifier. It remains defined only for the `Specific` path; callers on the Any path
  must use `try_get_instance_specifier`. This plan does **not** claim all accessors are
  non-panicking — the legacy accessor may panic/abort if used on an Any builder with no producer
  specifier, and that limitation is documented rather than hidden.
- **No fabricated producer specifier:** `Any` results are never assigned an invented
  `InstanceSpecifier`.
- **Concrete identity access "if needed":** a caller needing the concrete discovered identity
  requires explicit access over native `InstanceIdentifier`/`actualInstanceId`. The Rust FFI
  currently exposes neither, so adding it needs a new FFI accessor. Decision: it is added only if
  a concrete requirement needs it; nothing is fabricated now. (Not required for the #250 typed
  path.)
- `Specific` API source compatibility is required and preserved. Downstream caller audit for the
  additive accessor and the documented legacy limitation is an implementation-stage obligation.

### 3.8 Async ownership: never-polled future must not leak the native search

Baseline defect (`consumer.rs:953-965` vs `:966-979`): `get_available_instances_async` calls
`start_find_service` **before** it returns the outer `async move` block. The inner
`ServiceDiscoveryFuture` — whose `Drop` (`consumer.rs:998-1009`) calls `stop_find_service` — is
constructed only on the **first poll** (`:971`). `NativeFindServiceHandle` has no `Drop` of its
own. Therefore a returned future that is never polled drops the outer block (and the captured
`find_service_result` handle) without ever constructing the owner, leaking the already-started
native search. This applies to the new Any path as much as to `Specific`.

Required fix (apply to both paths):

- **Immediate owning stop guard on start (recommended):** as soon as
  `start_find_service[_any]` returns a non-null handle, wrap it in an RAII guard that
  unconditionally calls `stop_find_service` on drop (mirroring `ServiceDiscoveryFuture::Drop`).
  Move the guard into the inner `ServiceDiscoveryFuture` so normal completion/drop stops exactly
  once; a never-polled outer future still stops via the guard's `Drop`. Exactly-once must hold
  (guard is moved, never copied; `NativeFindServiceHandle` stays non-`Copy`).
- **Alternative — deferred start with ownership at first poll:** do not call
  `start_find_service[_any]` until the first poll; start and immediately take ownership in the
  same poll. Must still handle a synchronous first callback and stop on first-poll-pending
  cancellation.
- Both options preserve the existing `ServiceDiscoveryFuture` behaviour (first callback → `Ready`,
  including an empty container) and must not double-stop. Dropping while polled-pending
  (`Poll::Pending`) must stop and quiesce callbacks before deleting the handle (native
  `StopFindService` guarantee).

Tests (§5.1): never-polled drop; polled-pending cancellation; completed (empty) first callback.

## 4. Files to change (all within permitted paths)

| File | Change |
| --- | --- |
| `score/mw/com/impl/rust/com-api/com-api-runtime-lola/runtime.rs` | `find_service` Any → `LolaConsumerDiscovery` in Any mode (no panic) |
| `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs` | `DiscoverySpecifier` enum; Any branches in `get_available_instances[_async]`; **async owning stop guard so a never-polled returned future cannot leak the started search**; builder identity; remove unconditional panic; regression unit tests (incl. never-polled drop + polled-pending cancellation) |
| `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs` | 2 new `FFIBridge` methods |
| `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_lola.rs` | extern decls + impl for the 2 new methods |
| `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_mock.rs` | `mock!` entries + `SharedMockBridge` forwarding |
| `score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h` | `InterfaceOperations` ANY-selector metadata; new `BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER` |
| `score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.cpp` | 2 new `extern "C"` functions delegating to the existing typed find paths |
| `score/mw/com/rust/score_com_concept/concept.rs` | fallible descriptor accessor (§3.7) |
| `score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs` | adapt mock `ConsumerDescriptor` impl to the chosen accessor |
| `score/mw/com/test/basic_rust_api/bigdata_com_api_gen.cpp` | use the 4-arg registration macro for `BigDataInterface` |
| `score/mw/com/test/basic_rust_api/etc/config.json` | add the wildcard selector instance + second BigData instance + other-interface instance for exclusion coverage |
| `score/mw/com/test/basic_rust_api/*` (`producer_app`, `consumer_sync_apis`, `consumer_async_apis`, `integration_test/*.py`, `BUILD`) | ANY consumer mode + the use-after-discovery-drop regression |

Notes:
- Option-2 hardening additionally touches `score/mw/com/impl/{i_runtime.h,runtime.h,runtime.cpp,
  runtime_test.cpp}` (all in the permitted set). It is not required by the recommended design.
- `score/mw/com/rust/score_com_cpp_bridge/register_interface.h` only includes the registry header
  and is **not** in the permitted prefixes; it needs no change.
- No change to `i_service_discovery.h`, `configuration.*`, or `score_com.rs` unless an
  implementation-time discovery shows the recommended route insufficient; such a change would be
  an explicit, separately-reviewable deviation.

## 5. Issue-to-test mapping

Rust positive coverage MUST exercise the new FFI path (not mocked wrappers) and cover:
multiple offered same-interface instances, exclusion of other interfaces, empty/no offer,
callback/drop lifetime, Specific compatibility, error propagation. Native C++ ANY integration
(`score/mw/com/test/find_any_semantics`) stays the unchanged reference and is run to prove the
underlying per-service ANY semantics.

| #250 requirement | Change | Check |
| --- | --- | --- |
| `Any` does not panic | `runtime.rs`, `consumer.rs` | Rust unit test with `MockFFIBridge` (Any → `find_service_any`, no panic); `score_com_concept-test` |
| all instances of `I` returned | FFI any path + LoLa crawler | new `basic_rust_api` integration: producer offers **two** `BigDataInterface` instances → ANY returns exactly 2 |
| excludes other interfaces | config gains an instance of another interface (e.g. `ComplexStructInterface`) | same integration: ANY for `BigDataInterface` returns only BigData handles |
| empty / no offer | native returns empty container | integration: ANY before any offer → `Ok(empty)` sync; async ANY → first callback empty → `Ready` (one-shot snapshot). A later-offered service is observed only by a **new** search, tested separately — not claimed as continuous updates |
| async ownership / drop | `ServiceDiscoveryFuture` + new owning guard (§3.8) | unit (mock): (a) never-polled returned future is dropped → `stop_find_service` called (no leak); (b) poll once → `Pending`, then drop → exactly one `stop_find_service`, no double-stop; (c) first callback (incl. empty) → `Ready`, drop → one stop |
| proxy construction per instance | builder `build()` for a discovered Any handle | integration: subscribe/receive on an Any-discovered BigData instance |
| Specific unchanged | keep `Specific` path | existing `test_com_api_sync` / `test_com_api_async` unchanged + a mixed Specific+Any test |
| error propagation | FFI `nullptr` → `Err` | unit: unknown interface UID / unmapped selector → `Err(ServiceNotFound)`, no abort |
| no fabricated identity; legacy limitation explicit | descriptor policy §3.7 | unit: `try_get_instance_specifier` → `Err(ServiceNotFound)` for Any; `get_instance_specifier` → real specifier for Specific; legacy Any-path limitation documented (no all-non-panic claim) |
| native semantics reference | unchanged | run `//score/mw/com/test/find_any_semantics/integration_test:...` |
| **use-after-discovery-drop (mandatory)** | §3.5 ownership | see dedicated regression below |

### 5.1 Mandatory real use-after-discovery-drop regression

Positive regression proving the deployment owner outlives builders/proxies after discovery drop,
and proving a **genuine** native wildcard (mandatory discriminating regression):

1. Provider offers **two** instances of `BigDataInterface` and publishes samples. **At least one
   offered same-interface instance is absent from the consumer configuration** (a separate provider
   config is acceptable). Two configured `Specific` instances cannot distinguish a genuine native
   wildcard, so the consumer config must not list the second instance.
2. The exclusion case must **actually offer** another interface from a provider process (e.g.
   `ComplexStructInterface`), not merely list it in configuration.
3. Consumer calls `runtime.find_service::<BigDataInterface>(FindServiceSpecifier::Any)`,
   `get_available_instances()` → both offered `BigDataInterface` instances (including the one not
   in consumer config), and **no** `ComplexStructInterface` instance.
4. Consumer selects one builder and **explicitly drops the discovery handle** before building the
   consumer/proxy; then builds, subscribes and receives ≥ 1 sample (value correctness asserted).
5. Async variant: obtain builders via `get_available_instances_async().await`, then drop the
   future (and discovery object) before building/using the proxy. A **never-polled** async query
   is separately dropped and asserted to stop its search (§3.8).
6. Runtime compatibility decision: the wildcard selector must be resolved to a **compatible**
   binding and version/quality deterministically. If no compatible deployment exists, return an
   explicit error — never silently use the first incompatible record.

A supplementary in-crate `MockFFIBridge` test (Linux) asserts that after dropping the
`LolaConsumerDiscovery`, `builder.build()` still invokes `create_proxy` with the retained handle
container — a structural guard for the derived-handle lifetime. It does not replace the native
regression above; only the native test can prove the deployment pointer stays valid.

Deterministic bounded supervision: reuse `pkg_application` + `integration_test` +
`wrap_exec(..., cwd=..., wait_on_timeout)` with explicit `wait_timeout`, as in
`consumer_sync_apis/integration_test/com_api_sync_api_test.py` and
`consumer_async_apis/integration_test/com_api_async_api_test.py`. No unbounded sleeps/joins; no
mocked-only pass.

## 6. Safety / design impacts

- **Unsafe/FFI:** two new `extern "C"` symbols; pointer ownership rules documented in §3.2/§3.5.
  Rust closure callbacks keep the existing `catch_unwind` → `abort` discipline
  (`bridge_ffi_lola.rs:99-128`); no unwind across FFI.
- **Lifetimes (mandatory):** the deployment owner outlives every emitted handle/builder/proxy,
  independent of discovery/`StopFindService` lifetime (§3.5). Runtime-owned stable storage is
  required; stack/discovery-scoped ownership is rejected as unsound.
- **Concurrency:** recommended design relies on Configuration's atomic generation reads; option-2
  hardening must guard synthesis with a mutex. LoLa worker-thread and `StopFindService` quiescence
  are delegated unchanged to native `ServiceDiscovery`
  (`service_discovery/README.md:199-211`).
- **Allocations:** the recommended design adds no deployment copy (it points at the existing
  configuration deployment parsed at configuration time). Option 2 allocates one deployment copy
  per service type **on first query** (unless explicitly initialized beforehand); this is a
  runtime allocation and must not be asserted as zero. No new dependencies.
- **ABI:** the two new `extern "C"` symbols are additive; existing `mw_com_*` signatures and the
  find callback ABI are unchanged. The optional hardening adds a virtual method to `IRuntime`.
  This **changes the C++ vtable ABI even though the provided default keeps source-compatible
  mocks compiling**: any `IRuntime` implementor/derived mock and any prebuilt object linking
  against `IRuntime` must be rebuilt against the new vtable. Do **not** assert additive binary
  compatibility for that change; it is source-compatible only.
- **Error enums:** no new public variant (exhaustive-match compatibility preserved).
- **Panic policy:** the Any discovery paths remove `panic!`. The legacy
  `get_instance_specifier` retains a documented Any-path limitation (it can panic/abort when no
  producer specifier exists); callers on the Any path use `try_get_instance_specifier`. No blanket
  "all accessors are non-panicking" claim is made.

## 7. Compatibility analysis

- `Specific` Rust behaviour: unchanged path, unchanged results/errors.
- Rust `FFIBridge` is an internal (`com-api-ffi-lola`) trait; adding methods requires updating the
  mock and any external implementors. In-repo implementors observed: `LolaFFIBridge`,
  `MockFFIBridge`/`SharedMockBridge` (all updated).
- `ConsumerDescriptor` source compatibility is preserved: `get_instance_specifier` keeps its
  exact signature; the fallible `try_get_instance_specifier` is additive with a provided default.
  The legacy accessor's Any-path limitation is explicit in implementation docs and final gaps
  (§3.7); no blanket "all accessors are non-panicking" claim is made. Only two in-repo impls exist
  (`LolaConsumerBuilder`, mock `MockConsumerBuilder`) and in-crate tests do not call the accessor;
  downstream callers require an audit for the additive method.
- No `Cargo.lock`/`MODULE.bazel`/policy/lint/toolchain edits.

## 8. Expected checks (to be executed in the implementation/verification stage; enumerated explicitly)

- `//score/mw/com/rust/score_com_concept:score_com_concept-test` (Linux)
- `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests`
- `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` (`manual`; expected
  omission unless explicitly run)
- `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` (in-crate
  mock tests, including the discovery-drop structural guard)
- `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests`
- `//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync`
- `//score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test:test_com_api_async`
- new `basic_rust_api` ANY integration target (sync + async, incl. §5.1 regression)
- `//score/mw/com/test/find_any_semantics/integration_test:...` (native reference)
- Rust build/rustdoc + `clippy_strict` on the touched crates, from `.bazelrc`; C++ warnings profile
  for touched `cc_library` targets
- Enumerate `manual`, target-incompatible (non-Linux/QNX), filtered and unrun checks; do not
  count a wildcard success as coverage of them.

Evidence handling: bind commands/configs/tool identities/inputs/exit codes/raw logs to the exact
final baseline+patch hash; keep failed/outdated evidence as history; preserve missing reports.
No execution was performed in this stage (stage scope), so no check is claimed as passed.

## 9. Preserved gaps and pending decisions

- Engineering acceptance: `pending_offline`; this plan and any later patch are proposals only.
- Decisions are made within delegated authority; no approval/wait nodes are used; they remain
  reviewable proposals until engineering acceptance is granted offline.
- Decision D1 (made): preserve `get_instance_specifier`'s signature; add the additive fallible
  `try_get_instance_specifier` with a provided default; document the legacy Any-path limitation.
  Specific API source compatibility is preserved. No fabricated producer specifier.
- Decision D2 (made): the recommended design uses a configured wildcard selector entry per
  interface (native ANY pattern); unknown/unmapped interfaces return a documented
  `ServiceNotFound` error. `IRuntime::resolve_any` synthesis is optional hardening, not required
  for #250.
- Decision D3 (made): if synthesis is added, runtime-owned address-stable storage
  (`std::deque`/`std::list`/heap node) is required; a relocating `std::vector` is rejected.
  Synthesis allocates on first query unless explicitly initialized beforehand.
- Decision D4 (made): the async discovery API is a **one-shot initial snapshot**; an empty first
  callback completes it. No continuous-update/stream claim; later offers need a new search.
  Heterogeneous continuous stream remains #1261.
- Decision D5 (made): fix the async start/poll ownership ordering with an **immediate owning stop
  guard** on successful start (deferred-start alternative allowed); a never-polled returned future
  must stop its search. Covered by never-polled-drop and polled-pending-cancellation tests.
- Decision D6 (made): the discriminating regression requires ≥1 offered same-interface instance
  absent from consumer configuration and another interface **actually offered**; the runtime must
  pick a compatible binding/version/quality deterministically or return an explicit error.
- Decision D7 (made): the optional `IRuntime` virtual changes the vtable ABI; no additive binary
  compatibility claim is made (source-compatible only).
- Missing/unknown: `score/mw/com/impl/test/runtime_mock.{h,cpp}` do not exist; carried native
  ticket ids above are unresolved; no fresh native evidence exists for this stage.

## 10. #1261 follow-on obligations (do NOT implement / do NOT spend budget)

- System-wide, all-interface async stream of newly available services with interface identification.
- Interface-independent `ServiceDescriptor`, `find_all_services` API, initial-results/error/
  termination/lifetime documentation.
- `ServiceDescriptor` error-enum/API shape (breakage analysis required).
- Cross-interface positive coverage (≥2 distinct interfaces), newly offered services, identity,
  restart/re-offer, error/termination and stream-drop callback quiescence.
- These remain unimplemented; the typed `find_service::<I>(Any)` delivered here must not be
  presented as satisfying #1261 or #250's broad "all services on system" comment.

## 11. One-source-correction note

Entering implementation charges the single source-correction node of this run
(`source_fix_nodes_this_run: 1`; #250 history `1/3`). The run guard blocked source edits during
this report stage, so no correction was consumed here; the contract above is ready to apply. A
source edit attempted after the operator instruction to proceed to source was **again rejected by
the run guard** (same block as `shell`/`grep`), so the correction node remains unspent and no
source is modified. All original retries already exhausted elsewhere stay unchanged; no original
report is retroactively accepted or overwritten. If the correction is spent without a clean
bounded result, stop and report the residual gaps rather than looping.

## 12. Explicit non-claims

No native work product is marked qualified/released/accepted; no safety finding is closed; tests,
clean analyzers and a green run cannot supply engineering acceptance. No comment/PR/merge/release
authority is exercised.

## 13. Reviewed-constraint addendum (final, concise)

Authoritative constraints reviewed at plan close; no further broad research is required.

1. **Positive wildcard test is discriminating.** It MUST actually offer at least one matching
   same-interface instance that is **absent from the CONSUMER configuration** (a separate provider
   configuration is fine). Two configured instances cannot distinguish a genuine native wildcard
   from `Specific` enumeration, so the consumer config must not fully cover the offered set.
2. **Exclusion test must actually offer** another-interface service from a provider process; a
   configuration-only entry is vacuous.
3. **Deterministic compatibility.** Where multiple configured versions/bindings/qualities exist,
   the runtime must resolve deterministically to a compatible one or return an explicit error;
   never silently take the first incompatible record.
4. **Async is one-shot.** First callback (even empty) completes the search; no continuous-update
   claim. A never-polled returned future must still own/stop the started search (§3.8); later
   offers require a new search. Heterogeneous stream stays #1261.
5. **Identity honesty.** Existing `ConsumerDescriptor::get_instance_specifier` signature is
   preserved; the additive fallible accessor `try_get_instance_specifier` (with a default) reports
   absence. No fabricated producer specifier; no blanket "all accessors are non-panicking" claim;
   the legacy Any-path limitation is recorded in implementation docs and final gaps.
6. **Lifetime remains mandatory.** Runtime-owned stable deployment storage must outlive all
   retained builders/proxies after discovery drop (§3.5); allocation occurs at first query unless
   explicitly initialized.
7. **Acceptance remains pending offline.** This plan does not assert qualification, release,
   safety closure or additive binary compatibility (the optional `IRuntime` virtual changes the
   vtable ABI).
