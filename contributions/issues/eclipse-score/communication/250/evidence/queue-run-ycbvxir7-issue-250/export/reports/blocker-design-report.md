# Blocker / design report — issue #250 `FindServiceSpecifier::Any`

Baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Linux only. No code change was made;
the two panics remain because the backend/FFI prerequisite is absent. This report is
source-bound, not measured by native build (command stages are outside agent authority).

## 1. What the issue asks vs. what the baseline provides

| # | Issue acceptance criterion | Native obligation / artifact | Baseline reality | Disposition |
| --- | --- | --- | --- | --- |
| AC1 | `find_service::<I>(FindServiceSpecifier::Any)` returns available instance(s) without panicking | `Runtime` (concept) + `com-api-runtime-lola` `Runtime::find_service`; design `high_level_design_detail.md` line 118 | `runtime.rs:43-46` panics; no ANY path exists below | **Blocked** — needs FFI/backend support |
| AC2 | A discovered ANY instance can be described and built into a `Consumer` | `ConsumerDescriptor::get_instance_specifier`; native `HandleType` | `consumer.rs:1074` panics; `HandleType` exposes no `InstanceSpecifier` and no FFI returns one | **Blocked** — needs FFI + contract decision |
| AC3 | Detailed design artifact stays accurate | `score/mw/com/rust/design/high_level_design_detail.md` | Already records `FindServiceSpecifier::Any` as unsupported `[ ]` | Satisfied for current state; update only when a decision changes support |

Requirements/Architecture: issue declares them unaffected, consistent with the absence of
any requirement/architecture artifact change in the proposed work.

## 2. Evidence trace (exact anchors)

- `score/mw/com/rust/score_com_concept/concept.rs:287-290`
  `pub enum FindServiceSpecifier { Specific(InstanceSpecifier), Any }` — no derives.
- `concept.rs:109-121` — `Runtime::find_service<I>(FindServiceSpecifier) -> Self::ServiceDiscovery<I>`;
  doc says "use `InstanceSpecifier::MATCH_ANY`", but no such constant exists (doc/stale design).
- `score/mw/com/impl/rust/com-api/com-api-runtime-lola/runtime.rs:40-52` — `Any => panic!(...)`;
  `LolaConsumerDiscovery { instance_specifier: <concept InstanceSpecifier> }` erases the
  `Any`/`Specific` distinction before discovery.
- `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs:857-861` — `LolaConsumerDiscovery`
  stores a concrete `InstanceSpecifier` only.
- `consumer.rs:880-907` / `917-980` — sync/async discovery convert the specifier to
  `bridge_ffi_rs::InstanceSpecifier` and call `find_service` / `start_find_service`; no ANY branch.
- `consumer.rs:1070-1078` — `get_instance_specifier` panics; in-code comment states it "should
  get InstanceSpecifier from FFI Call" if ANY were enabled.
- `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs:239-259` — FFIBridge
  `start_find_service(callback, InstanceSpecifier)` and `find_service(InstanceSpecifier)`.
- `com-api-ffi-lola/common.rs:37-55, 75-102` — `NativeInstanceSpecifier` create/clone/delete
  are the only service-identity FFI operations; no `InstanceIdentifier` marshalling.
- `com-api-ffi-lola/registry_bridge_macro.cpp:395-417` — `mw_com_start_find_service` calls
  `ServiceDiscovery::StartFindService(std::move(callable), std::move(*instance_spec))`.
- `registry_bridge_macro.cpp:507-525` — `mw_com_impl_find_service` calls
  `ServiceDiscovery::FindService(std::move(*instance_specifier))`.
- `score/mw/com/impl/i_service_discovery.h:43-51` and `service_discovery.h:50-57` — the C++
  interface also has `FindService(InstanceIdentifier)` and
  `StartFindService(handler, InstanceIdentifier)` (the any-instance entry points), but no FFI
  exposes them.
- `score/mw/com/impl/handle_type.h:82-104` — discovered `HandleType` exposes
  `GetInstanceIdentifier()` / `GetInstanceId()`; there is no specifier accessor.
- `score/mw/com/impl/bindings/lola/service_discovery/flag_file_crawler.cpp:168-205` — LoLa
  "find-any" watch behaviour (service directory + every instance directory); the branch is
  selected when the enriched identifier has no binding-specific instance id.
- `score/mw/com/test/find_any_semantics/BUILD` + `integration_test/BUILD` — native C++
  regression target `//score/mw/com/test/find_any_semantics/integration_test:test_find_any_semantics`
  (`cc_binary :service` / `:client` and a `pkg_application` filesystem).
- `find_any_semantics/client.cpp:35-72` — one client `InstanceSpecifier` is passed to
  `TestDataProxy::FindService(...)`; the test then requires `size() == kNumberOfOfferedServices`
  (2) and builds a proxy per handle.
- `find_any_semantics/service.cpp:100-123` — two skeletons are offered under two distinct service
  specifiers.
- `find_any_semantics/integration_test/test_find_any_semantics.py:27-31` — the test docstring is
  "Test service discovery with FindService (any semantics)".
- `score/mw/com/design/service_discovery/README.md:135-138` — any-semantics requires binding the
  found `InstanceIdentifier` to a concrete instance id; later proxy construction depends on it.
- `score/mw/com/rust/score_com.rs:49` — public documentation already states `Any` is unsupported.
- `score/mw/com/rust/design/high_level_design_detail.md:117-118` — LoLa support matrix marks
  `FindServiceSpecifier::Any` as `[ ]`.

## 3. Why a Rust-only patch cannot satisfy AC1/AC2

1. **No data path for "any".** Every Rust discovery call funnels through
   `bridge_ffi_rs::InstanceSpecifier` (a concrete path). The concept enum's `Any` variant is
   converted to a panic before it can reach the bridge, and the runtime container has no field
   to carry the variant even if the panic were removed.
2. **No C++ entry point is bridged.** Although C++ SD supports any-instance discovery via
   `InstanceIdentifier`, the Rust FFI does not export that overload and Rust cannot build an
   `InstanceIdentifier` (it carries serialized deployment/configuration state).
3. **The result type is insufficient.** `ServiceDiscovery` yields `ConsumerBuilder`s whose
   `ConsumerDescriptor::get_instance_specifier()` returns `&InstanceSpecifier`. A found handle
   carries an `InstanceIdentifier`/instance id, not a specifier, and no FFI can surface one.
   Returning a fabricated specifier (e.g. the ANY sentinel) would be wrong and would later fail
   the proxy-construction note at README:135-138.
4. **Semantics are undecided.** The issue comment asks for "all the available services on
   system", which exceeds `find_service<I>` (typed to one interface). Choosing between
   "all instances of interface `I`" and "all services" is an engineering decision, not a model
   choice.

Refinement from the native `find_any_semantics` test: the C++ `FindService(InstanceSpecifier)`
overload that the Rust FFI *does* bridge already returns multiple instances when the deployment
resolves the specifier to an identifier without a concrete instance id (see §2). So the C++
capability is present at the specifier level too; the Rust gap is the API shape — `Any` carries
no specifier, and no FFI can request "any" for a bare interface id or retrieve a discovered
instance's identity. This strengthens rather than weakens the disposition: a Rust-only patch still
cannot satisfy AC1/AC2.

## 4. Draft implementation options (proposals only; not accepted)

| Option | Shape | Impact / effort | Decision authority |
| --- | --- | --- | --- |
| A. Keep unsupported (current) | Leave panics + design `[ ]` | None; honest failure | No new decision |
| B. Bridge `InstanceIdentifier` any-semantics | Add FFI to request any-instance discovery for an interface and return each found instance's identity; extend `ConsumerDescriptor` (or add a new accessor) to expose the discovered identity | Non-Rust backend/FFI + public Rust contract change; needs design update | Backend owner + Rust API owner |
| C. Redefine `Any` to "all instances of the same interface, specifier taken from the found handle" | Same FFI need as B; keep `get_instance_specifier` if a specifier can be derived | Requires a native specifier accessor or a mapping from `InstanceIdentifier` | Backend owner + Rust API owner |

Recommendation (proposal, not a decision): defer implementation until B/C is accepted; keep
Option A in the tree. Do not remove the panics or claim support in tests/docs.

## 5. Verification status

- No native commands were run (shell/collector are outside agent authority).
- `.rust-queue/reports/native-check-summary.json` is **absent** in this workspace; treated as
  missing evidence, not as a passing result.
- `check-plan.json` lists the BUILD-derived native targets and obligations that a future
  accepted implementation (and this assessment) must be measured against, including the
  source-discovered native any-semantics boundary
  `//score/mw/com/test/find_any_semantics/integration_test:test_find_any_semantics`.
- The implementation-stage record of changed paths and unresolved concerns is in
  `.rust-queue/reports/implementation.md` (no repository source changed).
