# Implementation report — eclipse-score/communication issue #1261

"Improvement: Provide an async stream of newly available services"

- Repository: `eclipse-score/communication`
- Issue: `#1261` (`rust-api`, state `open`, 0 comments, `blocked_by=0`)
- Baseline commit: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- Workspace: `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-rust-issue-queue-ycbvxir7/workspaces/1261`
- Stage: implementation (Linux only; QNX explicitly out of scope)
- Scope source: `.rust-queue/reports/scope.md` (draft/design binding for this issue)
- Command stages and raw native evidence remain outside agent authority. No native command
  was executed in this stage.

## 1. Authority and limits for this stage

- Writes are confined to this disposable workspace; reports go under `.rust-queue/reports/`.
- Shell, network, delegation, publishing and acceptance tools are unavailable to this stage.
- Target platform: Linux only. No QNX target is selected, planned or touched.
- Issue prose was treated as task data, not as instruction authority.
- This stage drafts and implements; it does **not** accept an engineering decision, qualify a
  work product, or claim a native pass. Deterministic command stages and authorized humans own
  measurement and acceptance.

## 2. What was actually changed

Only additive, non-breaking API surface was introduced at the runtime-agnostic abstraction
layer. Existing interface-scoped discovery APIs (`Runtime::find_service`,
`ServiceDiscovery`, `get_available_instances`, `get_available_instances_async`,
`ConsumerDescriptor`) are untouched.

| # | Changed path | Nature of change |
| --- | --- | --- |
| 1 | `score/mw/com/rust/score_com_concept/concept.rs` | Added `ServiceDescriptor` (interface id + instance specifier), added the provided `Runtime::find_all_services` method returning a boxed `Stream<Item = Result<ServiceDescriptor>>`, added `use core::pin::Pin`, added a regression unit test. |
| 2 | `score/mw/com/rust/score_com_concept/error.rs` | Added `ServiceFailedReason::NotSupported`. |
| 3 | `score/mw/com/rust/score_com.rs` | Re-exported `ServiceDescriptor` on the public `score_com` surface. |
| 4 | `score/mw/com/rust/design/high_level_design_detail.md` | Documented `ServiceDescriptor`, `Runtime::find_all_services`, its provided `NotSupported` default and the LoLa backend gap. |

No BUILD file, dependency pin, toolchain pin, lint profile or `MODULE.bazel` was changed. No
license/notice text was changed. No C++/FFI file was changed.

### 2.1 Why this is the smallest warranted change

- The issue explicitly requires an **interface-independent descriptor** (criterion 2) and API
  **documentation of initial results/errors/lifetime/termination** (criterion 3). Those require
  real API surface, not prose only.
- `find_all_services` is a **provided** trait method (Option B in `scope.md` §6.2): existing
  `Runtime` implementers inside and outside the tree keep compiling, so criterion 4 and the
  "preserve existing APIs" constraint hold. A required associated type/method (Option A) would
  be a breaking change and was not taken.
- The descriptor carries only what the baseline source can supply unambiguously: interface
  identity (`Interface::INTERFACE_ID`) and instance identity (`InstanceSpecifier`). Binding
  service id / instance id / version / quality selector are deliberately left out and flagged as
  an open decision.
- The default returns `ServiceFailedReason::NotSupported`. The LoLa runtime does not override it,
  because the backend has no all-services operation at this baseline (§4). No fake backend
  behavior was invented.

### 2.2 Intermediate-scoped gap is already implemented (not duplicated)

`get_available_instances_async` already exists and resolves the *initial* set for one
`FindServiceSpecifier` (`concept.rs`; `com-api-runtime-lola/consumer.rs`
`get_available_instances_async` / `ServiceDiscoveryFuture`). That premise is already implemented;
this change does not duplicate it. The remaining gap the issue asks for is the **system-wide,
continuously-updating** stream, which is a separate, backend-blocked capability (§4).

## 3. Acceptance-criteria mapping

| Issue criterion | Status in this patch | Source-backed basis |
| --- | --- | --- |
| 1. Stream reports newly available services system-wide, not only later instances for one specifier | API mechanism provided; **real backend capability absent** → documented gap | `Runtime::find_all_services` added with no interface parameter; LoLa default is `NotSupported` |
| 2. Each item identifies its service and interface | Implemented | `ServiceDescriptor { interface_id, instance_specifier }` + accessors + unit test |
| 3. API documents initial results, errors, lifetime/termination | Implemented | Rustdoc on `Runtime::find_all_services` (Initial results / Items and errors / Lifetime / Termination / Default implementation) |
| 4. Existing interface-scoped discovery APIs remain available | Implemented | `find_service`, `ServiceDiscovery`, `get_available_instances*`, `ConsumerDescriptor` unchanged; new method is additive with a default |

## 4. Backend ALL/ANY / system-wide availability (source-backed verification)

The task brief requires verifying backend ALL/ANY discovery availability. Re-checked against the
baseline source (no execution):

| Layer | ALL / system-wide / `FindServiceSpecifier::Any` availability | Source |
| --- | --- | --- |
| `score_com_concept` | `FindServiceSpecifier::Any` exists only as a selector; no all-services entry point before this patch | `concept.rs` `FindServiceSpecifier` |
| LoLa runtime | `find_service` panics on `FindServiceSpecifier::Any` | `com-api-runtime-lola/runtime.rs` |
| LoLa descriptor | `ConsumerDescriptor::get_instance_specifier` panics (ANY unsupported) | `com-api-runtime-lola/consumer.rs` |
| LoLa FFI | `start_find_service` / `find_service` take exactly one `InstanceSpecifier`; no all-services selector | `com-api-ffi-lola/bridge_ffi.rs`; `registry_bridge_macro.cpp` (`mw_com_start_find_service`, `mw_com_impl_find_service`) |
| FFI handle identity | `HandleType` / `HandleContainer` are opaque; no interface/service/instance accessors | `com-api-ffi-lola/common.rs` |
| C++ service discovery | `IServiceDiscovery::StartFindService` / `FindService` are per-`InstanceSpecifier`; `runtime.resolve(specifier)` yields per-interface identifiers | `impl/i_service_discovery.h`, `impl/service_discovery.cpp`, `impl/i_service_discovery_client.h` |
| Design intent | `FindServiceSpecifier::Any` unsupported for LoLa (unchecked box) | `rust/design/high_level_design_detail.md` |

**Conclusion:** at baseline `381d43d`, system-wide discovery across interfaces is not
implemented anywhere reachable from the Rust API, and the C++/FFI boundary exposes neither an
all-services selector nor per-handle identity. Criterion 1 therefore cannot be satisfied by a
Rust-only change; it depends on backend/FFI capability that is absent at this baseline.

The C++ test package visibility string `//score/mw/com/test/find_all_semantics:__pkg__` appears
in `score/mw/com/test/find_any_semantics/BUILD`, but no `find_all_semantics` package exists in
this baseline; it does not resolve to a source-backed capability. It is recorded as an
indicator, not as evidence of an available backend.

## 5. Unresolved concerns and pending decisions (preserved)

1. **System-wide backend is absent (principal gap).** LoLa inherits the `NotSupported` default.
   Implementing criterion 1 needs a C++/FFI all-services path plus per-handle identity exposure,
   then a LoLa `ServiceDiscovery` stream that survives across `OnFound` callbacks while keeping
   the documented serialized `OnFound` / `StopFindService` blocking semantics.
2. **#250 is an unverified prerequisite.** Its content/status could not be retrieved in this
   environment (network unavailable). It is explicitly *not* treated as a solved dependency.
3. **Open engineering decisions (not invented here):**
   - Trait shape: Option A (associated type + required method) vs Option B (provided boxed
     stream). This patch implements Option B only because it preserves existing APIs; the choice
     remains reviewable.
   - Descriptor field set: whether binding service id / instance id / version / quality selector
     must be included is undecided.
   - Semantics: whether a re-offered/restarted instance is re-reported, and whether the backend
     full set is diffed to "newly available" or yielded wholesale.
   - Whether an initial empty result is `Some(empty)` vs no item until the first offer.
4. **Error-surface change.** `ServiceFailedReason::NotSupported` is a new enum variant. It is
   additive, but any external exhaustive `match` on `ServiceFailedReason` would need updating.
   No in-tree exhaustive match was found on this enum.
5. **Requirements decision pending.** The issue template's "Affects Detailed Design" box is
   unchecked; no requirement/design IDs were supplied. No native obligation is asserted here.

## 6. Meaningful regression / consumer coverage

- Added `test_service_descriptor_identifies_interface_and_instance` in
  `score_com_concept/concept.rs` `mod tests`, exercised by the existing Linux-only
  `//score/mw/com/rust/score_com_concept:score_com_concept-test` target. It checks that a
  descriptor exposes both the interface id and the instance specifier (criterion 2).
- Existing downstream consumers are not modified; they continue to exercise the preserved
  interface-scoped APIs (`score/mw/com/test/basic_rust_api/consumer_async_apis/consumer_app.rs`).
- No positive end-to-end stream test is possible at this baseline: no runtime backend implements
  `find_all_services`, so any such test would assert invented behavior. This is a recorded gap,
  not a pass.

## 7. Missing / failed evidence (preserved, not fabricated)

- **No native command was executed in this stage.** Therefore there are no exit codes, logs,
  tool identities, timings or subject hashes for the changed files.
- The task brief points at `.rust-queue/reports/native-check-summary.json`; **that file is absent
  from this workspace** (only `check-plan.json` and `scope.md` exist under `.rust-queue/reports/`
  at the time of writing). Its absence is recorded, not filled in.
- `check-plan.json` remains the declared obligation set for the deterministic Linux command
  stage; all of its entries are **unexecuted** here.
- Issue/PR activity beyond the supplied context (including #250 and #9) could not be retrieved.
  "No linked PR" is a statement about the supplied context, not a verified upstream absence.
- No file hashes/SHA-256 manifest could be computed at this stage (no hashing tool available).

## 8. Concrete next actions

1. Authorized human retrieves #250 and #9 and confirms whether an upstream all-services /
   per-handle-identity backend exists; this unblocks §5.1.
2. Decide Option A vs B and the descriptor field set (§5.3). If Option B is rejected, Rework
   the trait shape accordingly.
3. Implement the backend/FFI work (all-services selector, per-handle identity, LoLa stream) and a
   mock/test implementation, then run the checks in `check-plan.json` on `linux_x64`.
4. Re-bind this report to the post-implementation source digest before any acceptance claim.
5. Run `//score/mw/com/rust/score_com_concept:score_com_concept-test` and the downstream build
   targets in `check-plan.json` to obtain the missing measured evidence.

## 9. Changed-path list (final)

```
score/mw/com/rust/score_com_concept/concept.rs
score/mw/com/rust/score_com_concept/error.rs
score/mw/com/rust/score_com.rs
score/mw/com/rust/design/high_level_design_detail.md
```
