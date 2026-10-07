# Independent supervisor report — issue #250: typed Rust `FindServiceSpecifier::Any`, FINAL authorized correction

Status: **audit only. Engineering acceptance remains PENDING OFFLINE. No automatic acceptance.**
The supervisor did not edit any source, did not run a build/test/analyzer (`shell`/`grep` blocked by the
run guard), did not spend the #1261 budget, and wrote only this file. Every native statement below is a
reading of the trusted `native-check-summary.json`; no agent test-passed claim is made.

| Item | Value |
| --- | --- |
| Issue | eclipse-score/communication #250 (`rust-api`, open) |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Platform | Linux (LoLa/SHM) only; QNX excluded |
| Model / editor | DeepSeek Flash only, no fallback |
| Correction node | #250 correction **3/3 (final)**; charged on implementation entry, budget now exhausted |
| Other budgets | #1261 stays **1/3**; #560 Codex allowance stays **1/3** — untouched |
| Reviewed artifacts | `.rust-queue/context/task.json`, `previous-attempt/{supervisor-source-review.md, native-check-summary.json, implementation.md}`, current `.rust-queue/reports/{implementation.md, native-check-summary.json, regression-plan.json}`, and the actual changed sources |
| Check result under audit | `native_passed: true`, `checks: 6`, `changed_files: 5`, `positive_regression_gap: null`, `required_regression_plan_present: true`, `infrastructure_error: null`, `source_corrections_used: 3`, `source_subject_vector_sha256: 03e8f54bd3455c73c126a9c80e16890c2e45ae68c22e8df1a9db08c11ea646e8` |

## 1. Verdict

All **six** planned native checks executed and passed (every `exit_code: 0`; the summary's top-level
`exit_code: 0`, `passed: true`, `infrastructure_error: null`). Zero checks failed and zero were
unexecuted. Both blockers raised by the prior source review (S1 Rust E0560; S2 malformed C++ markup
macro) are **confirmed fixed in the current source**, and the two coverage/honesty priorities (S5, S6/S7)
are reflected in the sources actually present. No remaining compile blocker was found by this audit and
none is recorded by the native measurement.

This is nonetheless a **native-measurement outcome, not engineering acceptance**. The design limits from
the prior review are preserved and are restated honestly in §7. The selection of this candidate as
acceptable, the #250 broad-comment question, #1261 heterogeneous streaming, qualification/trace/
applicability, and external downstream compatibility remain human/offline decisions. Because this was the
**third and final** correction, the #250 source budget is now exhausted: there is no further retry or
repair source node.

## 2. Confirmed compile status (the two prior blockers)

- **S1 — Rust initializer/field mismatch: FIXED.** `com-api-runtime-lola/consumer.rs` now constructs
  `ServiceDiscoveryFuture { _find_guard: find_guard, .. }` (line 1020) against the declared field
  `_find_guard: FindServiceStopGuard<B>` (line 1061). The guard was **moved, not deleted** (line 1015,
  `let find_guard = find_service_result?;`), so the cancellation guarantee is preserved. The prior
  failure (`error[E0560] … no field named find_guard`) cannot recur from this construction.
- **S2 — C++ registration macro: FIXED.** `registry_bridge_macro.h` line 824 now reads
  `id##_InterfaceRegistrationHelper id##_interface_reg_instance;` in the 4-argument
  `BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER` macro, matching the 3-argument macro at line 782.
  The macro is expanded four times in `bigdata_com_api_gen.cpp` (BigData + Concrete/Malformed/Empty
  selector test interfaces, lines 20–76), so this was a live blocker and is now resolved.
- All six native groups passed, including the dedicated regression target, the in-crate unit tests, the
  C++ `runtime_test` and concept tests, sync/async Specific compatibility, `find_any_semantics`, the
  gcc_15 doctest, and the clippy lint build. Therefore the changed sources **compile and link** in the
  measured `linux_x64`/`linux_x64_gcc_15` configurations.
- **Lint is not clean:** the clippy group exits 0 but emits 4 warnings — 2× `clippy::result_unit_err`
  on the new `find_service_any` (`bridge_ffi.rs:270`) and `find_service_any`-adjacent APIs, plus
  `clippy::missing_transmute_annotations` (`consumer.rs:989`) and `clippy::clone_on_copy`
  (`consumer.rs:1234`). This is a passing build with warnings, **not** a clean-analyzer result.

## 3. Ownership / callback / drop audit (mandatory lifetime + never-polled drop)

- **Owning stop guard is correct (P1 fixed).** `get_available_instances_async` computes
  `find_service_result` **synchronously** (consumer.rs:992–1009): on a non-null `start_find_service[_any]`
  it immediately builds `FindServiceStopGuard { handle: Some(NativeFindServiceHandle::new(raw_handle)),
  bridge }`, and the `async move` block captures that result and stores it in `_find_guard`
  (lines 1015–1026). A returned outer future that is **never polled** therefore still owns and drops the
  guard. `FindServiceStopGuard::drop` (1041–1053) takes the handle once and calls `stop_find_service`
  exactly once; `NativeFindServiceHandle` is not `Copy`, so the guard is the single owner. This also
  applies to the pre-existing `Specific` path.
- The native callback passes a `FindServiceHandle` argument that the Rust closure deliberately ignores
  (`_find_handle`, consumer.rs:977); the synchronous return value remains the sole owner, eliminating a
  double-write races. No other `stop_find_service` call site exists in `consumer.rs`.
- **Lifetime of returned builders/proxies is runtime-owned, not discovery-owned.** The FFI delegates a
  validated `InstanceIdentifier` (`registry_bridge_macro.cpp:60–100`) resolved through
  `IRuntime::resolve`; per `instance_identifier.h:176–183` the `ServiceTypeDeployment`/
  `ServiceInstanceDeployment` behind it are owned by the process-lifetime `Runtime` `Configuration`
  (not by the local `std::vector`), and `HandleType` copies the identifier. The Rust builder additionally
  retains an `Arc<HandleContainer>`. `consumer_app.rs` drops `sync_discovery` (line 316) and
  `async_discovery` (line 358) **before** building, subscribing and receiving from the returned
  builders, and the measured positive regression passes. This satisfies `mandatory_lifetime_refinement`
  for the measured path; it remains an inspection-level conclusion for paths not exercised.
- **Inherited callback-allocation gap is preserved, not overclaimed (S7).** The find-service
  `RustBoxedCallable` specialization has an empty `dispose` (`registry_bridge_macro.h:190`) and the
  erased `FindServiceCallable` has no `Drop`, so the exactly-once native **stop** proof does **not**
  imply every boxed callback/closure is reclaimed. `implementation.md` records this explicitly. No
  unreviewed destructor was added.

## 4. Selector typing and concrete identity

- `ResolveFindAnyIdentifier` (`registry_bridge_macro.cpp:60–100`) accepts a selector **only** when the
  interface is registered, the selector string is non-empty, `InstanceSpecifier::Create` succeeds, and
  `IRuntime::resolve` yields **exactly one** identifier with `BindingType::kLoLa` and
  `InstanceIdentifierView::GetServiceInstanceId() == std::nullopt`. Concrete-id, malformed, unsupported-
  binding, ambiguous, and unmapped selectors all return `std::nullopt → nullptr → Err`. The **resolved
  identifier** (not the untrusted string) is forwarded to native `FindService`/`StartFindService`. This
  closes the "silently return Specific under Any" risk. The synthetic registrations in
  `bigdata_com_api_gen.cpp` exercise each rejection class (`/score/cp60/MapApiLanesStamped` concrete,
  `/bad//selector` malformed, no selector for `ComplexStructInterface`), and the regression passed.
- **Concrete native ids are not exposed as identity.** `try_get_instance_specifier`
  (`consumer.rs:1144–1148`) returns `Err(ServiceNotFound)` for any `Any` result; the legacy
  `get_instance_specifier` still `.expect(...)`s for `Any` and is documented as `Specific`-only
  (`consumer.rs:1132–1142`; `concept.rs:592–625`). The provided `try_get_instance_specifier` default
  merely forwards to the legacy accessor, so absence-as-error is not universal across third-party
  implementors — documented, not hidden.
- **`Specific` alias is a query alias, not authenticated producer identity.** The identity-semantics
  docs (`concept.rs:595–611`) state that a native `Specific` query may itself reference a configured
  wildcard and return several handles sharing the caller alias; the regression asserts only that the
  `Specific` builder echoes the caller specifier (`consumer_app.rs:304–310`), which is consistent with
  that statement. No fabricated producer name is produced from the registry UID.
- **Residual (minor, untested) divergence:** the sync `Any` path maps an unmapped/unsupported selector to
  `ServiceError(ServiceNotFound)` (`consumer.rs:899–907`), while the async path maps a `null` start
  handle to `ServiceError(FailedToStartDiscovery)` (`consumer.rs:1001–1002`). `implementation.md` §2
  states unmapped interfaces generally return `ServiceNotFound`; that is exact for sync but **not** for
  the async-start-null case, which has no unit test. This is a documentation/consistency gap, not a
  measured failure, and is recorded here rather than repaired.

## 5. Readiness and per-provider regression (S5)

- **Discriminating configuration.** `etc/provider_config.json` offers two `BigDataInterface` instances
  (`/score/cp60/MapApiLanesStamped` id 1, `/score/cp60/MapApiLanesStampedSecond` id 2) plus one
  `ComplexStructInterface` instance id 13. `etc/config.json` (consumer) contains only
  `/score/cp60/MapApiLanesStamped` (id 1) and the wildcard entry `/score/cp60/MapApiLanesStampedAny`
  (no `instanceId`, lines 120–145); it does **not** list `/score/cp60/MapApiLanesStampedSecond`. Two
  configured `Specific` instances therefore cannot produce the asserted two-instance result.
- **Both builders are exercised with distinct per-provider markers.** `producer_app.rs:250–269` sends
  `x = MARKER * 1000 + i` with `MARKER_FIRST=1`/`MARKER_SECOND=2` from the two instances.
  `consumer_app.rs:313–345` (sync) and `357–388` (async) build, subscribe and drain **both** returned
  builders, then `assert_marker_sets` (156–175) requires each builder to map to exactly one distinct
  marker and the union to equal `{1, 2}`, independent of handle order. This is a genuine
  per-provider/absence-discriminating assertion, not an order artifact.
- **Exclusion is rendered non-vacuous by a real readiness barrier.** Before the BigData wildcard is
  asserted to exclude the other interface, `consumer_app.rs:216–248` loops on a genuine `Specific`
  discovery of the offered `ComplexStructInterface` until it is observed (bounded by
  `DISCOVERY_TIMEOUT`), then asserts the wildcard returns exactly two BigData instances (280–284). A
  leaked `ComplexStruct` handle would make the count three and fail.
- **No-offer phase is synchronous and bounded.** `test_com_api_any_no_offer` uses
  `EmptySelectorInterface → /score/test/DummyAny` (a valid LoLa wildcard for a never-offered service
  type) and asserts the documented `Ok(empty)` with zero instances (`consumer_app.rs:179–188`). The async
  no-offer case is deliberately not awaited (native `StartFindService` only fires the handler on
  non-empty handles); this is the documented one-shot limitation, distinct from #1261's updating stream.

## 6. Executed / unexecuted / failed native checks and real child cases

All counts below are read from `native-check-summary.json`.

| # | Planned group | Kind / config | Result | XML child cases (suites) |
| --- | --- | --- | --- | --- |
| 0 | `//score/mw/com/test/basic_rust_api/consumer_any_apis/integration_test:test_com_api_any` | test / linux_x64 | **PASSED** (10.9 s, exit 0) | 2 (`ITF`) |
| 1 | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | test / linux_x64 | **PASSED** (exit 0) | XML reports 1 (see note) |
| 2 | `//score/mw/com/impl:runtime_test`, `…:score_com_concept-test`, `…:score_com_concept-macros-unit-tests` | test / linux_x64 | **3/3 PASSED** (exit 0) | runtime_test 1+4+12=17; concept 1; macros-unit 1 |
| 3 | `…/consumer_sync_apis/…:test_com_api_sync`, `…/consumer_async_apis/…:test_com_api_async`, `…/find_any_semantics/…:test_find_any_semantics` | test / linux_x64 | **3/3 PASSED** (exit 0) | 3; 3; 1 |
| 4 | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | doctest / linux_x64_gcc_15 | **PASSED** (exit 0) | 1 |
| 5 | clippy `build` on the five touched Rust targets | lint / clippy | **exit 0** (4 warnings, 0 errors) | n/a (build) |

- **Executed: 6/6 planned groups. Unexecuted: 0. Failed: 0.** Top-level `exit_code: 0`,
  `passed: true`, `infrastructure_error: null`.
- **Distinct test XMLs: 9.** XML-reported child cases total **30** (2 + 1 + 1 + 1 + 17 + 1 + 1 + 3 + 3).
  The dedicated Any integration XML records exactly the two intended methods (`test_com_api_any`,
  `test_com_api_any_no_offer`) with 0 failures / 0 errors.
- **Rust child-case caveat (honest count):** the `com-api-runtime-lola-tests` XML reports `tests="1"`,
  while `consumer.rs` alone defines **7** `#[test]` functions (4 pre-existing + 3 new Any tests:
  `test_any_discovery_unmapped_interface_returns_error`, `test_any_async_never_polled_stops_native_search`,
  `test_any_async_pending_cancellation_stops_native_search`). The summary note states the XML wrappers
  differ from Rust child cases and the raw log is authoritative; the raw log is outside this supervisor's
  read scope. The Rust child-case count is therefore **under-reported** by the preserved XML and is not
  inflated here.
- `regression-plan.json` names the two dedicated Any targets and the driver adds the four compatibility
  groups; `required_regression_plan_present: true` and `positive_regression_gap: null`.

## 7. Preserved gaps, residual findings, and non-claims

- **Callback/closure allocation reclamation is unproven** (inherited empty find-service `dispose`); the
  exactly-once stop proof must not be read as full resource reclamation.
- **No general deterministic binding/version/quality resolver**: only single-record resolution is
  supported; multi-record/ambiguous selectors are rejected rather than resolved. Native `FindService`
  performs its own compatibility filtering, but the patch is not claimed to be such a resolver.
- **Legacy accessor still aborts for `Any`** without a specifier; only `try_get_instance_specifier` is
  the supported path, and its provided default does not guarantee error-on-absence for third-party
  implementors.
- **External downstream source/ABI compatibility is unproven** by in-repo builds (new mandatory
  `FFIBridge` methods and a private `LolaConsumerBuilder` field); no `IRuntime` virtual was added, so no
  vtable change is claimed or made.
- **Async unmapped error reason differs from sync** (§4) and is untested.
- **One-shot async only**; empty first callback completes it, later offers need a new search. Not a
  continuous/heterogeneous stream.
- **#250 broad-comment ambiguity (2026-03-30, "all available services on system") is not solved** by this
  typed same-interface path; it remains #1261 scope. #1261 budget stays 1/3; no heterogeneous API, no
  interface-independent `ServiceDescriptor`, no new error enum variant was added.
- **QNX excluded; no qualification, trace, applicability or safety finding is closed or inferred.**
- **Protected names untouched:** none of `MODULE.bazel`, `MODULE.bazel.lock`, `Cargo.lock`, `LICENSE`,
  `NOTICE`, `.bazelrc` appears in the changed set. The 5 subjects this correction changed
  (`registry_bridge_macro.h`, `consumer.rs`, `concept.rs`, `consumer_app.rs`, `producer_app.rs`) all lie
  in the authorized prefixes; the cumulative candidate still carries the prior 19-file implementation
  (FFI/registration/runtime wiring/tests) as verified in the workspace. `changed_files: 5` is the delta of
  this correction against the `03e8f54b…` subject vector.
- **Preserved unknown native IDs** (no status invented): `SWP-253124` (FFI error handling),
  `Ticket-238828`, `Ticket-234827`, `Ticket-219876`, `Ticket-173043`, `Ticket-219132`, `Ticket-184255`,
  `Ticket-169333`, `Ticket-214582`, plus the `SWS_CM_*` ids.
- **Stale permitted paths preserved**: `score/mw/com/impl/test/runtime_mock.{h,cpp}` do not exist at this
  baseline; no attempt was made to edit them. Historical failed attempts, patches and missing reports
  remain sealed and are not retroactively accepted.

## 8. Disposition

The final authorized #250 correction is **native-green** (6/6 measured checks passed, 0 failed,
0 unexecuted) with both prior compile blockers fixed and the regression materially strengthened, while
the honest design limits are preserved rather than overclaimed. This supervisor **grants no engineering
acceptance**, closes no issue and issues no new retry; the #250 source budget is exhausted (3/3) and, if
any of the recorded limits were judged unacceptable, source work must stop rather than continue. The
remaining authority for acceptance is the authorized offline engineering decision.
