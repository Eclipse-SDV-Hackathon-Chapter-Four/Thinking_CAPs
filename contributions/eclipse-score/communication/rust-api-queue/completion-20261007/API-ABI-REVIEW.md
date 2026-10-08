# API and ABI disposition

The integrated candidate resolves the competing discovery bridge names: typed same-interface Any uses `start_find_service_any`; discovery across configured LoLa deployments uses `start_find_service_type`. The public `Runtime::find_all_services` documentation states the selected configured scope and its provider-instance, initial-result, coalescing, withdrawal, error and lifetime semantics. Broader system-wide enumeration is outside this contribution.

`IRuntime` is byte-identical to current-main baseline. Removing the proposed virtual extension avoids calling a slot absent from an older implementation. The `Runtime` header is identical after removing the new static method declaration; no fields, virtual methods or existing declarations change. Discovery caches are held outside the object. They are initialized before the production singleton so referenced deployments outlive native discovery teardown. An injected legacy runtime produces an empty universe without a cast or forced production initialization. The packet includes a deterministic structural comparison and an executed native legacy-runtime regression; it does not assert a qualified ABI-tool verdict for every platform.

The new native functions and callback deleter are additive. Existing exported baseline callback functions keep their semantics. Specific, typed Any and configured discovery callbacks transfer their boxes only on successful registration. Failed calls retain caller ownership; accepted callbacks are released after native teardown, including deferred teardown. Subscription registration uses the same rejection/success guard principle. The updated Rust Specific-discovery bridge uses the additive `mw_com_start_find_service_owned` symbol and the same guarded transfer/deletion path. The original `mw_com_start_find_service` export remains unchanged for existing native callers.

| Caller or implementer | Migration/review |
| --- | --- |
| Existing Rust Runtime implementer | `find_all_services` has a provided default; no new associated type is required |
| Existing Rust Subscription implementer | Added state methods have provided defaults; assess supported behavior before overriding |
| Internal FFIBridge implementation | Both synchronous discovery methods now return `FindServiceError`; replace unit-error results and update mock signatures |
| Internal Specific/typed Any bridge | Accepted registration owns its unique boxed callback; rejected registration leaves caller ownership. A FindServiceCallable may be used for at most one successful registration |
| Internal callback constructor | `FindServiceCallable::new` is now unsafe. Its pointer must originate from `Box::into_raw` on the exact documented `dyn FnMut(HandleContainer, NativeFindServiceHandle) + Send + 'static` box, with unique ownership and at most one successful registration |
| Public error enum matches | Added error variants require reviewing exhaustive matches; no universal Rust source-compatibility claim is made |
| Native IRuntime implementer or mock | No new virtual method; configured enumeration through the static extension is empty for injected runtimes |
| Cross-platform/FFI adopter | Validate pinned compiler trait-object representation, target widths, native callback serialization, reentrancy and lifetime assumptions |

Allocation remains an engineering review subject. Pending identities are coalesced and withdrawn identities are removed; tests exercise repeated flapping and distinct interfaces. Callback boxes for updated Specific, typed Any and configured discovery are reclaimed. Configuration deployments remain address-stable and retained across add-on merges, and hash-map/vector capacity may retain a high-water mark. The applicable operating-phase allocation profile, bounds and acceptance must be established by the native owner.
