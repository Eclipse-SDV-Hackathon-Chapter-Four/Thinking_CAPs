I have a working prototype for this and would like to confirm two design points before opening a PR.

**Approach.** `Runtime::find_all_services()` returns a `Stream<Item = Result<ServiceDescriptor>>`. Each descriptor carries the service type name, version, binding, service ID and instance ID. The LoLa backend starts one find-any watch per service type in the loaded configuration, including add-on configurations merged before the stream is opened, and accepts any concrete instance ID. Services already offered are yielded first. An item is yielded again when a withdrawn service is re-offered. The stream ends when it is dropped, which stops the watches. The existing interface-scoped `find_service` is unchanged.

On Linux (x86_64), the sync, async and FindAny integration tests and the unit tests pass, along with a new phased ITF test. That test covers an initial offer, a later offer of a second interface, a withdrawal and a re-offer, and asserts exact identities with no duplicates.

**Question 1: scope of "system-wide".** LoLa service discovery flag files carry only the numeric service ID, instance ID and quality. Interface names and versions come from the configuration, and a proxy can't be created for an unconfigured service anyway. The prototype therefore reports every service the process can address, meaning types known to its configuration, from any provider instance. Is that acceptable for this issue? If services outside the configuration are needed, would descriptors without a type name be useful, or should that be a follow-up?

This overlaps with #250, which uses the same find-any mechanism, so it may make sense to settle both together.

**Question 2: heap allocation in the operational phase.** The stream allocates when discovery callbacks run, as the existing Rust `find_service` path already does. Must the Rust API meet the "no heap allocation in the operational phase" goal shown by the C++ examples in #692? If so, the stream's structures can be sized up front at creation, since the configured set of services is known.

**Implementation notes, for transparency:**
- Pending items are coalesced: at most one item per currently offered service, dropped if the service is withdrawn before being polled. This keeps the backlog bounded and mirrors the full-list semantics of the C++ `StartFindService` handler, in line with #9's goal that the Rust and C++ APIs feel similar.
- `IRuntime` gains one virtual method, appended at the end with a default implementation, so mocks still compile.
- The find-service callback box is not reclaimed today: its `dispose` is empty in `registry_bridge_macro.h`, which also affects the existing `find_service`. I'd track that separately rather than in this issue.

cc @bharatGoswami8 @LittleHuba @darkwisebear
