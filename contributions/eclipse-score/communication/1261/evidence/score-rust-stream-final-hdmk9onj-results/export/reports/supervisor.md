# Independent supervisor final audit — eclipse-score/communication #1261

Issue: "Improvement: Provide an async stream of newly available services" (label `rust-api`, state `open`,
0 comments, `blocked_by=0`). Baseline commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`, Linux only.

This is a **read-only** audit of the final allowed heterogeneous-discovery source correction. It was
produced from actual workspace source plus the machine-generated `.rust-queue/reports/native-check-summary.json`.
No source/control/ledger/pin/license file was edited, no native command was run, no model/subagent was
dispatched, no retry was queued and no human gate was used. Only this report was written. No runtime
steering/follow-up was or will be queued. Hashing/git/driver inspection were unavailable under the
file-tools-only constraint, so recorded hashes are cited as recorded, not independently recomputed.

## Verdict

**Not implemented; not accepted; no positive regression evidence.** The third and final authorized
source correction produced a substantially larger, more plausible candidate than correction 2, but it
**did not compile**, so nothing in it was executed. The authoritative `check` stage failed:

```json
{"native_passed": false, "checks": 1,
 "positive_regression_gap": "Required dedicated heterogeneous stream regression plan absent; compatibility tests cannot establish completion.",
 "required_regression_plan_present": false, "changed_files": 22}
```

The recorded native summary is `passed=false`, `exit_code=1`, `infrastructure_error=null`. The single
executed check is a `linux_x64` test group over
`com-api-runtime-lola-tests`, `configuration_test`, `runtime_test`, `score_com_concept-test`,
`score_com_concept-macros-unit-tests`; it **failed to build** and executed **0** tests:

```
score/mw/com/impl/runtime.cpp:355:1: error: expected unqualified-id before '{' token
...
//score/mw/com/impl:runtime_test                                FAILED TO BUILD
Executed 0 out of 5 tests: 1 fails to build and 4 were skipped.
```

`score_corrections_used = 3 / max = 3`. No retry, fix, or follow-up is authorized by this run.
Lifecycle success (`implementation` stage reported succeeded) is **not** engineering acceptance and
does not close the issue.

## Authority, binding and limits

- Run: current branch `fabro/run/01M49NSKAZEVSWHR4FZSYA3JDE`. Model/provider: DeepSeek Flash only
  (`deepseek-v4-flash`), no fallback; Codex role is read-only reviewer/operator.
- Source-correction budget: `1261 = 3/3 used` (exhausted). Issue `#250 = 3/3` and stopped — its source
  was **not** imported and is not fixed here. `#173` remains 2/3. The separate Codex `#560` allowance
  remains 1/3 and its exception is **not transferable** to #1261.
- `engineering_acceptance = pending_offline`. No requirement/design/safety IDs were supplied and none
  are invented. No QNX scope. No publication.
- The pinned codec empty-history/message-shape bug from the failed attempt remains unpatched; the
  fresh-context, no-follow-up control removes only the observed replay trigger and is **not** a proven
  transport repair. No token-cap repair is claimed.

## Actual source reviewed (current workspace, unbuilt)

| Artifact | Observed state |
| --- | --- |
| `score/mw/com/impl/runtime.cpp` | New `Runtime::GetConfiguredServiceWildcardIdentifiers()` builds, once and lazily, one wildcard `InstanceIdentifier` per distinct configured `ServiceIdentifierType` from public `Configuration` accessors, copying instance/type deployments into runtime-owned `std::deque` members. **Line 355 is an orphaned `{`**: the signature of `Runtime::MergeAdditionalConfiguration(const Configuration&) noexcept` (declared `runtime.h:162`) is missing, so the function body that calls `configuration_.MergeServiceEntries(...)`/`Validate()` sits at namespace scope. This is the recorded build failure. |
| `score/mw/com/impl/runtime.h` | Declares the override at `:140`, the `std::mutex discovery_identifiers_mutex_`, and the address-stable `std::deque<ServiceInstanceDeployment>` / `std::deque<ServiceTypeDeployment>` members (`<deque>` included). |
| `score/mw/com/impl/i_runtime.h` | Adds virtual `GetConfiguredServiceWildcardIdentifiers()` with a `{}` default at `:59–62`; rustdoc states the configured-only universe and an explicit non-binary-compatible vtable change. |
| `com-api-ffi-lola/registry_bridge_macro.cpp` | Adds native `mw_com_impl_enumerate_service_types` (+ list size/get/delete), `mw_com_impl_start_find_service_any(name,len,major,minor,callback)`, and `mw_com_impl_handle_get_identity(handle,...)`. Identity = handle type name + version + binding + LoLa service id + `HandleType::GetInstanceId()`; quality intentionally omitted. |
| `com-api-ffi-lola/bridge_ffi.rs` | Trait gains `enumerate_service_types`, `start_find_service_any`, `unsafe handle_identity`; owned `NativeServiceType` / `NativeServiceIdentity` (`:297–327`). |
| `com-api-ffi-lola/bridge_ffi_lola.rs` | Lola implementations copy native strings into owned `String`s and marshal list/identity accessors. |
| `com-api-ffi-lola/bridge_ffi_mock.rs` | `mock!` mirrors the three new methods so the unit tests can compile. |
| `com-api-ffi-lola/common.rs` | Only pre-existing `HandleContainer` helpers; the prior `use crate::StringView;` is now **absent**, so that carried clippy warning may no longer apply (unverified — lint did not run). |
| `com-api-runtime-lola/service_stream.rs` | `LolaAllServicesStream` with `StreamState{queue,members,watches,waker,finished}`, `apply_snapshot` per-watch diff + global refcount, `build_all_services_stream` publishing guards before returning, `Drop` stopping watches outside the callback mutex; 8 `#[cfg(test)]` unit cases (dedup/re-offer, empty withdrawal, cross-watch dedup, same-instance-id-different-interface, never-polled Drop, partial-start rollback, pending-on-empty-universe). |
| `com-api-runtime-lola/runtime.rs` | `LolaRuntimeImpl::find_all_services` overrides the concept default and returns `Box::pin(build_all_services_stream(...)?)`. |
| `score_com_concept/concept.rs` | `ServiceVersion` and 5-field owned `ServiceDescriptor` (+ accessors, `PartialEq/Eq`); provided `Runtime::find_all_services` default `Err(NotSupported)`. |
| `score_com_concept/error.rs` | `ServiceFailedReason::NotSupported` variant present. |
| `test/basic_rust_api/all_services_stream/` | Provider offers BigData (provider manifest instance id **2**) then MixedPrimitives (delayed), unoffers and re-offers BigData; consumer opens one stream and exits 0 only on two interface types, delayed offer, provider id 2, and `big>=2`/re-offer; two manifests (consumer BigData id **1**); Python integration target and `pkg_application`. `regression-plan.json` names the dedicated target. |

## Contract obligation assessment (as proposed; none executed)

- **C1 full identity via explicit API — PARTIAL.** Enumeration is exposed through `IRuntime` and uses
  only public `Configuration` accessors (`configuration.h:98,101,131,153` verified public); grouping by
  full `ServiceIdentifierType` avoids collapsing versions that share `ToString()`. The native list
  returns name+version+binding+service id. Not executed, so not proven.
- **C2 wildcard deployment ownership — DESIGNED.** Deployments are copied into runtime-owned
  `std::deque`s whose element addresses survive later insertions; `InstanceIdentifier` stores `const
  ServiceInstanceDeployment*`/`const ServiceTypeDeployment*` (default copy copies the pointers), so the
  by-value vector copies in both the getter and `start_find_service_any` reference deque-owned storage.
  Plausible, but unverified and dependent on `make_InstanceIdentifier` forwarding those references.
- **C3 owned observed descriptors — DESIGNED.** 5 owned fields, equality as `IdentityKey`; quality is
  omitted with an open question. Values are populated from native handle identity rather than literals,
  which is a real improvement over correction 2 — but never executed.
- **C4 universe honesty — DOCUMENTED, NOT ACCEPTED.** Configured-only set at first enumeration;
  unconfigured/unknown interfaces and post-enumeration `AddConfiguration` additions are explicitly out
  of scope; a configured type with no configured instance yields no wildcard and is skipped. This is
  recorded as a limitation against the issue's literal "system-wide" criterion, not an accepted universe.
- **C5 snapshots/membership/dedup/re-offer — DESIGNED.** Complete-snapshot diff, per-watch membership,
  global refcount, empty-withdrawal clears membership, unchanged snapshots suppressed. Unit cases exist
  but did not compile.
- **C6 watch ownership / partial failure — DESIGNED.** Shared state before first start; reverse-order
  stop of already-started watches on failure; `Drop` takes watches out under the watch lock then calls
  native stop outside the callback membership mutex.
- **C7 callback reclamation — EXPLICIT LIMITATION.** The inherited find-service dispose is empty, so the
  native callback closure (and its `Arc`) is leaked per opened stream; no Box/`Arc` reclamation or
  failed-stop quiescence is claimed. Exactly-one-stop counters alone do not establish native safety.

## Regression obligations: what actually ran

- **No native stream regression ran.** The dedicated provider/consumer integration target exists in
  source and is named in `basic_rust_api/regression-plan.json`, but it was never built or executed. The
  executed check failed at an earlier C++ compile, and 4 of the 5 selected unit targets were skipped.
- **All 4 planned groups were unexecuted.** `planned_checks` (unit/compat, existing sync/async/`find_any`
  integration, GCC15 macro doctest, 5-library Clippy) contains **no** dedicated all-services-stream
  target, and the single executed group produced no XML child records at all (`test_records: []`).
- **Discrepancies preserved (unresolved):**
  1. `regression-plan.json` **is present** in-tree at `score/mw/com/test/basic_rust_api/regression-plan.json`
     and names the dedicated target, yet the authoritative driver recorded
     `required_regression_plan_present = false`. The expected path/schema is unknown under file-only
     constraints; the disagreement is recorded, not reconciled.
  2. The recorded `changed_files` (22) omits `concept.rs`, `score_com.rs` and `error.rs`, although
     `service_stream.rs` depends on the 5-field `ServiceDescriptor` and `NotSupported`, and correction 2
     reported `concept.rs` among its changes. Source-level dependency vs the recorded delta cannot be
     reconciled without hashing/git; this provenance gap is preserved.
- **Carried evidence (historical, from the prior failed attempt, not re-measured here):** compatibility
  groups passed 94 child cases / 2 ignored doctests with 4 clippy warnings (`bridge_ffi.rs:259`
  `result_unit_err`; `consumer.rs:950` `missing_transmute_annotations`; `consumer.rs:1164`
  `clone_on_copy`; and `common.rs:23` `unused_imports`, which the current source appears to have removed).
  The summary note that "XML wrappers differ from Rust child cases" stands and is preserved.

## Gaps not resolved by this run

- No genuine heterogeneous backend was ever measured: no two-interface stream, no accepted
  initial/later/dedup/withdraw/re-offer behavior, no observed native identity, no cancellation/partial-
  start/Drop quiescence, no missing-provider-instance id observed.
- Universe boundary remains configured-only and unaccepted; the literal "system-wide" criterion is unmet.
- Allocation policy is unproven (per-callback queue/membership maps bounded only by universe and offered
  instances; owned `String`s per identity).
- ABI: adding a virtual method to `IRuntime` is a documented vtable (binary) break; not accepted.
- `ServiceFailedReason::NotSupported` remains an exhaustive-match compatibility concern.
- `common.rs` `use crate::StringView;` removal is unconfirmed as a lint fix (lint group did not run).

## Pending offline decisions (not accepted here)

1. Whether a bounded configured-only universe may be labeled against the issue's literal criterion, and
   how to disposition the issue's system-wide comment (and the unrelated `#250` typed-wildcard contract).
2. Descriptor equality/dedup identity, quality/selector inclusion and version serialization.
3. Initial-empty vs first-offer semantics, re-offer and partial-start/Drop-quiescence contracts.
4. ABI/compatibility disposition for the `IRuntime` virtual addition and the `NotSupported` variant.
5. Whether any further source correction is admitted — **this run's allowance is exhausted (3/3)**.

## Concrete next action

No further source work is authorized under this run. Authorized reviewers must decide (1)–(5) offline.
Any future attempt must first restore the lost `Runtime::MergeAdditionalConfiguration(...)` signature
(the direct cause of the recorded build failure), then be re-built and re-measured — a real
two-interface native stream with observed per-handle identity, an honest universe/qualification scope and
a dedicated regression target that the driver actually recognizes. Nothing in this run supplies that
source, that passing regression evidence, qualification, issue closure or human acceptance.
