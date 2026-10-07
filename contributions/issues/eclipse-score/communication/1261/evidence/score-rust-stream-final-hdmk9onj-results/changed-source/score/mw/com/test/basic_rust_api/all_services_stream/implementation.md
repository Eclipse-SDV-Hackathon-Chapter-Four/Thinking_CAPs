# #1261 heterogeneous LoLa discovery stream — implementation notes

Status: source implementation only. **Not compiled and not executed** in this stage (the stage had file tools only,
no shell/build/network). No test result, ABI finding, qualification or engineering acceptance is claimed. The native
integration and unit targets in `../regression-plan.json` are the intended measurements; a trusted checker must run
them later.

## What was implemented

A concrete, continuously updating, interface-independent service-availability stream for the LoLa backend, bounded to
the **configured** LoLa universe.

### Native (C++)

* `score/mw/com/impl/i_runtime.h` — new virtual `GetConfiguredServiceWildcardIdentifiers()`, default `{}`. Mockable and
  source-compatible for existing implementers; **not** binary (vtable) compatible (explicit ABI disposition below).
* `score/mw/com/impl/runtime.{h,cpp}` — the real `Runtime` builds, at most once, one wildcard (`FindAny`)
  `InstanceIdentifier` per distinct configured `ServiceIdentifierType`. Enumeration uses only public `Configuration`
  accessors (`GetServiceTypeNames`, `GetInstancesOfServiceType`, `GetServiceInstanceDeployment`,
  `GetServiceTypeDeployment`); grouping is by full `ServiceIdentifierType`, so types sharing `ToString()` name but
  differing in version are not collapsed. Wildcard deployments (instance id removed) and their type deployments are
  copied into Runtime-owned `std::deque` members, whose element pointers stay valid across later insertions, so the
  identifiers survive every watch and callback. A configured service type that has no configured instance cannot yield
  a wildcard deployment and is therefore skipped (also documented as a limitation).
* `.../com-api-ffi-lola/registry_bridge_macro.cpp` — three native entry points:
  * `mw_com_impl_enumerate_service_types` (owned opaque list + size/get/delete accessors) returning full identity
    (name, major, minor, binding, binding service id);
  * `mw_com_impl_start_find_service_any(name, major, minor, callback)` starting one wildcard watch for a configured
    type (nullptr when the type is not configured or start fails);
  * `mw_com_impl_handle_get_identity(handle, ...)` extracting the observed identity from a discovered `HandleType`
    (`InstanceIdentifierView`/`ServiceIdentifierTypeView`/`ServiceVersionTypeView`, LoLa service id and the concrete
    `HandleType::GetInstanceId()`).

### Rust

* `com-api-ffi-lola/bridge_ffi.rs`, `common.rs`, `bridge_ffi_lola.rs`, `bridge_ffi_mock.rs` — `FFIBridge` gains
  `enumerate_service_types`, `start_find_service_any` and `unsafe handle_identity`, with owned
  `NativeServiceType`/`NativeServiceIdentity` values, plus Lola and mock implementations.
* `com-api-runtime-lola/service_stream.rs` — `LolaAllServicesStream`:
  * shared state and per-watch ownership are established **before** the first watch starts, so a callback firing
    synchronously during start is handled and never dropped;
  * each native complete snapshot is diffed against that watch's previous membership; global refcounts deduplicate
    across overlapping watches; an empty withdrawal snapshot clears membership so a re-offer re-emits;
  * the stream stays pending on an initially empty universe (native suppresses empty initial notifications);
  * partial start failure stops all earlier watches; `Drop` stops every watch after taking them out of the watch mutex
    (no native stop is called while holding the callback membership mutex);
  * `LolaRuntimeImpl::find_all_services` overrides the concept default and returns `Ok(Box::pin(stream))`.

### Tests

* Rust unit tests in `service_stream.rs` cover full-identity dedup (distinct interfaces sharing an instance id),
  unchanged-snapshot suppression, empty-withdrawal + re-offer, cross-watch dedup, immediate/never-polled `Drop`,
  partial-start rollback and pending-on-empty-universe (FFIBridge mock).
* `score/mw/com/test/basic_rust_api/all_services_stream/` — dedicated provider/consumer apps, two distinct manifests
  (consumer `BigDataInterface` instance id 1, provider id 2), a Python integration case and BUILD rules asserting two
  interfaces, pre-existing + delayed offers, an absent provider instance id and withdrawal/re-offer.

## Contract obligations (codex C1–C7)

* **C1** enumerated through a mockable `IRuntime` extension; full name+version kept; no private-helper call, no
  downcast/private shortcut.
* **C2** wildcard deployments are Runtime-owned and address-stable; no stack/vector-element pointers back handles.
* **C3** owned descriptor identity (name, version, binding, service id, concrete instance id) with equality as dedup
  identity.
* **C4** the universe is the configuration loaded at first enumeration; **unknown/unconfigured interfaces are not
  discovered**, and `AddConfiguration` after the first enumeration is **not** reflected. This is an explicit limitation
  against the issue's literal system-wide criterion, not an accepted universe.
* **C5** complete snapshots, per-watch membership + global refcount, empty withdrawal clears membership, unchanged
  snapshots deduplicated.
* **C6** guards published before returning a never-polled stream; earlier watches rolled back on partial start; stops
  taken out of the callback state mutex before calling native stop.
* **C7** the inherited find-service callable has an empty dispose; the native callback closure (and the `Arc` it holds)
  is therefore **leaked per opened stream**. No Box/`Arc` reclamation or failed-stop quiescence is claimed. Running-phase
  allocation is bounded by the configured universe and currently offered instances; no capacity policy is proven.

## Explicitly unresolved / not claimed

* Compilation, formatting, clippy, doctests and native execution were **not** run here.
* Descriptor source compatibility: the descriptor already had an owned 5-field shape in the baseline; this stage did
  not change it and does **not** claim non-breaking status for external implementers.
* Provider quality is not part of the observed identity because native `HandleType` does not carry it; watch selection
  uses the configured instance's ASIL level.
* Native trace/ABI/downstream/error-enum compatibility, applicability and qualification remain open. Offline human
  acceptance remains pending. No #250 work was imported or repaired; the #560 exception was not used.
