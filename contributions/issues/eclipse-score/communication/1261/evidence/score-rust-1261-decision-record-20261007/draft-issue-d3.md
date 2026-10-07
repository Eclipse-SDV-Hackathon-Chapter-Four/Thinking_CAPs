**Title:** Bug: Rust COM-API find-service callback boxes are never reclaimed

### What

The Rust find-service path passes a boxed closure to native `StartFindService` through `FindServiceCallable`. In `score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h`, the `RustBoxedCallable` specialization for the find-service handler has an empty `dispose`:

```cpp
static void dispose(FatPtr) noexcept {}
```

The `RustBoxedCallable<void>` receive-handler specialization does call back into Rust to drop its box. The find-service specialization does not, so every `find_service` call, through `consumer.rs` → `FindServiceCallable::new(...)`, leaks its closure and everything the closure captures. In the current consumer that includes `Arc`-shared discovery state and a waker. A process that repeatedly starts and stops discovery therefore grows its memory without limit.

### How

Add a Rust FFI delete function typed for the find-service closure (`dyn FnMut(HandleContainer, NativeFindServiceHandle)`) and call it from the find-service specialization's `dispose`. The existing `mw_com_impl_delete_boxed_fnmut` is typed for `dyn FnMut()` and must not be reused for this trait object.

`dispose` runs from the `RustFnMutCallableBase` destructor. `ServiceDiscovery` owns the handler through a `shared_ptr` that `StopFindService` erases, and bindings only hold a `weak_ptr`. The destructor, and therefore the reclamation, should therefore happen after the last in-flight invocation. That should be confirmed with a test that stops discovery while a handler invocation is in progress, and one that drops a Rust discovery future before its first callback.

### Estimates for realization

_Unknown_

### Category

- [x] Affects Detailed Design

### Requirements / Architecture

- [ ] Requirements / Architecture are not affected by this change?
