# Implementation report — issue #250 `FindServiceSpecifier::Any`

Baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Linux only, DeepSeek Flash only.
Mode `implementation` (task.json). `scope.md` warrants the smallest issue-scoped change; the
issue-scoped change is a bound blocker/design assessment, not a source patch.

## Outcome

**No repository source change was made.** The backend/FFI prerequisite for a Rust-only
`FindServiceSpecifier::Any` implementation is absent at this baseline. Removing either panic
would either mis-route `Any` to a concrete-specifier search or expose a capability the FFI
cannot serve, and would falsely contradict the native detailed-design status. The two `panic!`
sites and the design `[ ]` marker therefore remain and are accurate for the current capability.

## Actual changed paths

None in the repository source tree. The following assessment artifacts were written/updated
under `.rust-queue/reports/` (disposable workspace only):

| Path | Change |
| --- | --- |
| `.rust-queue/reports/implementation.md` | Added (this report). |
| `.rust-queue/reports/blocker-design-report.md` | Updated: added native `find_any_semantics` evidence and the InstanceSpecifier-vs-InstanceIdentifier nuance. |
| `.rust-queue/reports/check-plan.json` | Updated: added the source-discovered native C++ any-semantics targets and the missing concept macro unit-test target. |
| `.rust-queue/reports/review-packet.md` | Updated: added the new native evidence and this report to the packet list. |

No source, BUILD, design, license, pin, lint-policy, native-ID or published-status file was
modified. No QNX configuration was touched.

## Source-bound verification of the premise (bounded reads; no native execution)

The task instruction requires verifying current LoLa ANY support and the discovery APIs
*before* removing the panic. Verified from source:

| Anchor | Observation |
| --- | --- |
| `score/mw/com/rust/score_com_concept/concept.rs:286-297` | `FindServiceSpecifier { Specific(InstanceSpecifier), Any }`; no derives and no `Any` handling beyond the enum. |
| `concept.rs:116-117` | `find_service` doc says to use `InstanceSpecifier::MATCH_ANY`, but **no such constant exists** (stale doc/design). |
| `.../com-api-runtime-lola/runtime.rs:40-52` | `Runtime::find_service` panics for `Any` and otherwise stores only the inner `InstanceSpecifier`; the variant kind is erased before discovery. |
| `.../com-api-runtime-lola/consumer.rs:857-861` | `LolaConsumerDiscovery` carries only a concrete `InstanceSpecifier` (no ANY state). |
| `consumer.rs:880-907` / `917-980` | Sync/async discovery build `bridge_ffi_rs::InstanceSpecifier::try_from(&str)` and call the concrete `find_service` / `start_find_service`; there is no ANY branch. |
| `consumer.rs:1065-1079` | `LolaConsumerBuilder` holds `LolaConsumerInfo`, which stores no instance specifier; `get_instance_specifier` panics unconditionally, with a comment anticipating an FFI call only when ANY is enabled. |
| `.../com-api-ffi-lola/bridge_ffi.rs:239-259` | The `FFIBridge` trait exposes only `start_find_service(callback, InstanceSpecifier)` and `find_service(InstanceSpecifier)`. |
| `.../com-api-ffi-lola/common.rs:37-55, 75-174` | `NativeInstanceSpecifier` create/clone/delete are the only service-identity FFI operations; the Rust `HandleType` is opaque and has no specifier/identifier accessor. No `InstanceIdentifier` is marshalled. |
| `.../com-api-ffi-lola/registry_bridge_macro.cpp:395-417, 507-525` | `mw_com_start_find_service` / `mw_com_impl_find_service` dispatch only to `StartFindService(handler, InstanceSpecifier)` / `FindService(InstanceSpecifier)`. |
| `score/mw/com/impl/i_service_discovery.h:43-51` | The C++ interface additionally declares `StartFindService(handler, InstanceIdentifier)` and `FindService(InstanceIdentifier)` (the any-instance entry points), but no FFI exposes them. |
| `score/mw/com/impl/handle_type.h:82-104` | A discovered `HandleType` exposes `GetInstanceIdentifier()` / `GetInstanceId()` only; no `InstanceSpecifier` accessor. |
| `.../bindings/lola/service_discovery/flag_file_crawler.cpp:168-205` | LoLa find-any watches the service directory and every instance directory; the branch is taken when no binding-specific instance id is present. |
| `score/mw/com/design/service_discovery/README.md:135-138` | On ANY semantics the found `InstanceIdentifier` must be bound to a concrete instance id/type, otherwise later proxy construction fails. |
| `score/mw/com/rust/design/high_level_design_detail.md:117-118` | Detailed design already records `FindServiceSpecifier::Specific` `[x]`, `FindServiceSpecifier::Any` `[ ]`. |
| `score/mw/com/rust/score_com.rs:43-49` | Public doc states the same: `FindServiceSpecifier::Any` is not yet supported. |

Conclusion: the issue premise is only **partially** accurate. LoLa/C++ service discovery *does*
implement any-instance semantics, but at the `InstanceIdentifier`/configuration level, and the
Rust-facing FFI does not expose it. A Rust-only change cannot satisfy the acceptance criteria.

## New native evidence (not captured by the earlier assessment)

A source-discovered native integration test already exists that exercises C++ any-semantics:

- `score/mw/com/test/find_any_semantics/BUILD` — `cc_binary :service`, `cc_binary :client`,
  `cc_library :test_datatype`, `pkg_application :service-pkg` / `:client-pkg`.
- `score/mw/com/test/find_any_semantics/integration_test/BUILD` —
  `integration_test(name = "test_find_any_semantics", srcs = ["test_find_any_semantics.py"], ...)`.
- `.../find_any_semantics/client.cpp:35-72` — creates one client `InstanceSpecifier` and calls
  `TestDataProxy::FindService(instance_specifier)`, then requires
  `lola_proxy_handles.size() == kNumberOfOfferedServices` (2) and builds a proxy per handle.
- `.../find_any_semantics/service.cpp:100-123` — offers two skeletons under two distinct
  service specifiers.
- `.../find_any_semantics/integration_test/test_find_any_semantics.py:27-31` — docstring
  "Test service discovery with FindService (any semantics)".

This shows the C++ `FindService(InstanceSpecifier)` overload already returns multiple instances
when the deployment resolves the specifier to an identifier without a concrete instance id
(the `flag_file_crawler.cpp` find-any branch). It does **not** close the Rust gap: Rust's
`FindServiceSpecifier::Any` carries no specifier, the FFI exposes only `InstanceSpecifier`
overloads, and no FFI returns a discovered instance's identity. It is the natural native
regression boundary for a future Rust `Any` and is now recorded in `check-plan.json`.

## Unresolved concerns

1. **Semantics are undecided.** "All instances of interface `I`" (maps to `InstanceIdentifier`
   any-instance) vs. "all services on the system" (no supporting C++ public API found). This is
   an engineering decision, not a model choice.
2. **Backend/FFI extension required.** Rust must be able to request any-instance discovery and
   to retrieve each discovered instance's identity. Today `i_service_discovery.h` declares the
   `InstanceIdentifier` overloads but no FFI bridges them, and no `InstanceIdentifier` is
   marshalled across the boundary.
3. **`ConsumerDescriptor` contract change required.** `get_instance_specifier()` must return
   `&InstanceSpecifier`, but a discovered handle exposes an `InstanceIdentifier`/instance id, and
   no FFI surfaces a specifier; per `README.md:135-138` the identifier must first be bound to a
   concrete instance, or proxy construction fails.
4. **`get_instance_specifier` is unconditionally panicking, including for `Specific`.** The
   `LolaConsumerBuilder` does not store the input specifier, so even a `Specific` descriptor
   cannot be described today. This is an independent pre-existing gap (not fixed here because it
   is outside the issue's `Any` scope and would need its own native obligation/regression case).
5. **Stale public doc/design reference.** `concept.rs:116-117` refers to
   `InstanceSpecifier::MATCH_ANY`, which does not exist.
6. **Missing / unverifiable evidence (preserved, not fabricated).**
   `.rust-queue/reports/native-check-summary.json` is absent in this workspace; `web_fetch` is
   blocked by the file-tool boundary, so issue/PR activity after the two supplied comments
   (issue `updated_at` 2026-07-15) is unverified; no native command was executed and no file
   hashes could be computed (hashing requires a shell outside agent authority).
7. **Pending offline acceptance.** Implementation must not start until the three human decisions
   in `blocker-design-report.md` §4 / `review-packet.md` are made (semantics, FFI/backend
   extension, `ConsumerDescriptor`/design change). This report claims technical assessment only,
   not native engineering acceptance.

## Next action

Obtain the pending human decisions. On approval, add an FFI path for any-instance discovery
plus discovered-identity retrieval, update the `ConsumerDescriptor` contract and the detailed
design artifact, then implement `Any` with regression cases in
`//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` and the
`basic_rust_api` integration tests, measured against the targets in
`.rust-queue/reports/check-plan.json` (including the native `find_any_semantics` boundary).
