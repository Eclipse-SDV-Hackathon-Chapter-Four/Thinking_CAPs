# Implementation — Issue #782: Runtime implementation for Rust Method APIs

- **Repository / issue**: `eclipse-score/communication` — #782 "Improvement: Runtime implementation
  for Rust Method APIs" (`open`, label `rust-api`). Issue/task data:
  `.rust-queue/context/issue.json`, `.rust-queue/context/task.json`, `.rust-queue/context/comments.json`.
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (working tree also carries Fabro
  `start`/`preflight`/`scope` commits). No native source file was modified by this run.
- **Mode**: `implementation` (Linux native checkpoints, `max_source_corrections = 3`).
- **Authority**: DeepSeek Flash only; Linux only; no QNX; file tools only. Shell, network/web,
  search-by-content, delegation, publishing/acceptance and command stages were blocked in this
  environment, so no native command was executed and no raw collector evidence exists to reuse.
- **Report produced**: this file. `scope.md`, `check-plan.json`, `review-packet.md` were produced by
  the prior stage and are preserved unchanged.

## 1. Outcome and premise reconciliation

The issue asks to implement the LoLa Runtime backend for the Rust Method APIs following the design
traits (PR #777 / the #818 trait-macro-type-state layer) and to implement the matching FFI APIs, in
line with the existing Event backend.

**The premise does not hold at the selected baseline.** The Rust Method API surface — the design
traits, the `interface!` Method arm, the Method error contract, the `com-api-runtime-lola/method.rs`
runtime module and the Method FFI symbols — is **not present** at `381d43d`. The design is owned by
PR #777 / PR #818, whose merge state cannot be retrieved offline (network blocked), and prerequisite
#781 cannot be bound offline.

Therefore the smallest issue-scoped change that is *warranted and source-faithful* is **no source
change**. Implementing any part of the Method trait/type-state/FFI contract here would require
inventing the API/ABI owned by the open design and would violate the workflow constraint that models
must not invent accepted engineering decisions or native evidence.

This run therefore delivers the **dependency/design assessment** (the alternative the task permits)
plus the verified, preserved check plan. The implementation remains blocked/pending, not accepted.

## 2. Actual changed paths

**None.** No native artifact (Rust, C++, BUILD, MODULE, license, pin, lint/CI policy, design doc) was
edited. Baseline-to-working-tree source digest is unchanged by this run.

Files written by this run (reports only):

| Path | Role |
|---|---|
| `.rust-queue/reports/implementation.md` | This implementation report + design/dependency assessment |
| `.rust-queue/reports/scope.md` | Carried from scope stage (unchanged) |
| `.rust-queue/reports/check-plan.json` | Carried from scope stage (unchanged; labels re-verified) |
| `.rust-queue/reports/review-packet.md` | Carried from scope stage (unchanged) |

No hashes are claimed for these files: hashing requires a shell, which was blocked in this
environment. The absence is preserved rather than fabricated.

## 3. Source-bound assessment — what exists and what is missing

Verified at `381d43d` with bounded file reads and filename globs:

| Surface | Exact location | Observation |
|---|---|---|
| Abstraction traits | `score/mw/com/rust/score_com_concept/concept.rs` | Event/lifecycle traits only (`Runtime`, `Producer`, `OfferedProducer`, `Consumer`, `Publisher`, `Subscriber`, `Subscription`, `Sample*`, `CommData`, …). No Method/Caller/Handler trait. |
| Interface macro | `score_com_concept/interface_macros.rs:110-115` | `Method<$event_type>` arm emits `compile_error!("Method definitions are not supported in this macro version. …")`. |
| Macro negative test | `interface_macros.rs:356-386` | `compile_fail` doctest `interface_macro_with_Method` asserts the Method arm still rejects. |
| Error contract | `score_com_concept/error.rs:113-128` | `Error` variants are Service/Producer/Consumer/Event/Allocate/Receive only. No Method failure reason. |
| Runtime modules | `score/mw/com/impl/rust/com-api/com-api-runtime-lola/lib.rs:28-34` | Modules `consumer`, `producer`, `runtime` only; exports Event-side types only. No `method.rs` / `LolaMethodCaller` / `LolaMethodHandler`. `glob **/*method*.rs` returns nothing. |
| Runtime BUILD | `com-api-runtime-lola/BUILD:16-53` | `rust_library` srcs do not list a method module; test/doc-test targets are Linux-only (`@platforms//os:linux`, #1278). |
| FFI trait | `com-api-ffi-lola/bridge_ffi.rs:86-…` | `FFIBridge` methods are allocatee/sample/skeleton-event/proxy/skeleton/service-discovery only. No method-call FFI. |
| FFI `extern "C"` | `com-api-ffi-lola/bridge_ffi_lola.rs:130-…` | Declares `mw_com_proxy_event_subscribe`, `mw_com_get_event_from_proxy/skeleton`, `mw_com_skeleton_send_event`, create/destroy proxy/skeleton, etc. No `mw_com_*method*` symbol. |
| Callback trampolines (Event pattern) | `bridge_ffi_lola.rs:32-128` | Rust→C++-invoked callbacks (`mw_com_impl_call_dyn_fnmut`, `..._sample`, `..._find_service`, `mw_com_impl_delete_boxed_fnmut`) are `#[unsafe(no_mangle)] extern "C"`, wrap the call in `std::panic::catch_unwind(AssertUnwindSafe(...))`, and `std::process::abort()` on panic to prevent unwind across the C++ boundary. |
| C++ registry | `com-api-ffi-lola/registry_bridge_macro.h` | `MemberOperation` (`:486-506`) exposes only `GetProxyEvent`/`GetSkeletonEvent`/`GetTypeOps`; `RegisterMemberOperation` comments say "Currently used for events" (`:576-597`); macros are `BEGIN_EXPORT_MW_COM_INTERFACE` and `EXPORT_MW_COM_EVENT` (`:735-798`) plus `EXPORT_MW_COM_TYPE` (`:806-822`). There is **no** method registration macro or method member operation, although comments anticipate methods/fields. |
| C++ Method backend (counterpart) | `score/mw/com/impl/methods/{proxy_method*,skeleton_method*}`, `bindings/lola/{proxy_method*,skeleton_method*}`, `plumbing/*method_binding_factory*` | Backend call/handler model exists (`ProxyMethodBase` — call queue size fixed to 1, in-arg/return-value buffer lifetime, `InitializeInArgsAndReturnValues`; `SkeletonMethodBase` holds a `SkeletonMethodBinding`). It is not reachable from Rust. |
| Public re-exports | `score/mw/com/rust/score_com.rs:137-142` | Re-exports Event/lifecycle types only; no Method types. |
| Design doc | `score/mw/com/rust/design/high_level_design_detail.md:99-118` | "Supported score_com_concept Traits by LoLa Runtime" table lists no Method/Caller/Handler trait. |
| Design artifacts | glob `score/mw/com/rust/design/**`, `**/*777*`, `**/*method*.md` | No Method design document, sequence diagram or PR #777 artifact in the baseline tree. |

Conclusion: the only Method API behavior observable at baseline is the deliberate `compile_error!`
rejection (and its `compile_fail` test). The C++ Method backend exists but has no Rust-facing FFI or
registration entry point.

## 4. Dependency and macro assessment

Applying `references/dependency-and-macros.md`:

- **New crate/dependency**: none is introduced by this scoped change. No crate replacement,
  substitution or qualification decision is applicable at baseline. Existing pins are untouched:
  `rules_rust 0.68.2-score`, `score_crates 0.0.11`, `score_baselibs 0.2.14`, Ferrocene toolchain via
  `.bazelrc` `linux_x64`; lint via `quality/static_analysis/static_analysis.bazelrc`
  (`clippy_strict` aspect). These were read, not changed.
- **Macro failure modes**: the affected generator surface is the `interface!` declarative macro. A
  future Method arm must (a) generate correct accessor/Method member names and (b) keep rejecting
  unsupported syntax. At baseline the compiler/test detects the unsupported arm through
  `interface_macros.rs:110-115` and the `compile_fail` doctest at `:356-386`. A wrong arm could
  compile while exposing wrong member names or a missing Method member; only the design (#818) fixes
  the expected expansion, so no generation change is drafted here.
- **Generated API compatibility**: downstream generated interfaces
  (`com-api-gen`, `bigdata_com_api_gen_rs`) and the `score_com` re-export set must be re-checked once
  the Method design lands; the exact Method type/trait names are unknown at baseline and must not be
  guessed.
- **Process work products**: fabric pins `wp__tlm_plan` / `wp__tool_verification_report` are version
  1 / status `valid` type definitions. No new tool/qualification instance is created here; no
  confidence/classification decision is supplied.

## 5. Unsafe / FFI, ownership, callback, teardown, error and unwind assessment

Applying `references/issue-types.md` (unsafe/FFI and concurrency branches) — the *contract* a future
implementation must satisfy, not an implementation:

- **Representation / ABI**: the Rust-facing Method ABI does not exist. A future design must bind the
  opaque C++ base pointers (equivalent to `ProxyMethodBase` / `SkeletonMethodBase`), the in-arg and
  return-value buffer layout, and the callback `FatPtr` encoding. The Event pattern uses `#[repr]`-free
  opaque pointer types (`ProxyBase`, `ProxyEventBase`, `SkeletonBase`, `SkeletonEventBase`) plus
  `FatPtr { vtbl, data }` (`registry_bridge_macro.h:95-99`) and a Rust `StringView`
  (`bridge_ffi.rs:62-65`); a Method contract must specify the analogous types.
- **Allocation / deallocation owner**: `ProxyMethodBase` stores the in-arg/return value in a
  type-erased binding buffer created once at proxy setup (`InitializeInArgsAndReturnValues`) and uses
  a fixed call-queue of size 1 with an `is_return_type_ptr_active_` flag
  (`proxy_method_base.h:69-103`). Rust must not assume ownership of that buffer; the Rust side owns
  only the boxed `FnMut` handler and the Rust-constructed argument storage.
- **Callbacks / reentrancy**: the Event backend hands Rust closures to C++ as `Box<dyn FnMut + Send>`
  erased to `FatPtr`, invokes them via `catch_unwind`, and disposes them through
  `mw_com_impl_delete_boxed_fnmut` (`bridge_ffi_lola.rs:24-54`). A Method handler/caller contract must
  state reentrancy, `Send`, and single-dispose guarantees; registry registration comments currently
  say member operations are used for events only.
- **Teardown / Drop**: runtime types follow a shared-pointer / explicit-manual-cleanup C++-object
  lifecycle (`producer.rs`/`consumer.rs` use `Arc`, `ManuallyDrop`, `NonNull` and instance-manager
  wrappers; `producer.rs:32-63` shows the imports and `LolaProviderInfo` wrapper). A Method runtime
  must mirror that lifecycle.
- **Errors**: the Rust `Error` enum has no Method variant (`error.rs:113-128`); the exact Rust error
  mapping from C++ `MethodError`/binding construction is undefined in Rust.
- **Panic / unwind boundary**: existing trampolines abort on caught panic
  (`bridge_ffi_lola.rs:37-41, 79-85, 114-127`). Any Method callback trampolines must preserve this
  abort-instead-of-unwind behavior. Whether a Method call is sync or real-async (issue #767 / maintainer
  2026-09-08 comment) is undecided and changes the ownership/queue model.
- **Rust and C++ users**: Rust consumers are the `score_com` re-export set and generated interface
  crates; C++ users are the existing `impl/methods/*` backend and its tests. No Rust Method consumer
  exists to compile against at baseline.

## 6. Prerequisite / PR activity binding

- **PR #777** — "Rust Method APIs design", referenced by the issue body. Network retrieval blocked →
  head/base/merge status **UNKNOWN** offline.
- **PR #818** — trait/macro/type-state design. Maintainer comment 2026-08-31: design "still under
  review". Contributor 2026-08-28 reports `LolaMethodCaller`/`LolaMethodHandler` in
  `com-api-runtime-lola/method.rs` are `todo!()` placeholders — that file is **not present** at
  `381d43d`, so it belongs to an unmerged branch. Status **UNKNOWN**.
- **Prerequisite #781** — **UNKNOWN / not retrievable offline**. No local reference exists in the
  supplied snapshot. This remains an open prerequisite and blocks an implementation readiness claim.
- **Milestone exclusions (recorded, not acted on)**: E2E protection for Rust Methods/Fields is out of
  scope for milestone 1 (issue comments; tracked as #1062). QNX test enablement is tracked separately
  (#1278) and is excluded here.

## 7. Verification status and preserved evidence

- `.rust-queue/reports/native-check-summary.json` is **absent** in this workspace (confirmed by
  globbing `.rust-queue/reports/*`, which returned only the three carried reports `check-plan.json`,
  `review-packet.md`, `scope.md` before this report was written). The promised native-collector
  summary and raw logs are unavailable; no evidence was carried.
- No Bazel `query`/`build`/`test`/`docs`/`lint` command was executed (command stages are outside
  agent authority in this environment). All 19 planned checks remain **unmeasured**, not passing.
- `check-plan.json` is preserved unchanged. Its labels were re-verified against the actual BUILD
  files at `381d43d`: `//score/mw/com/rust:score_com`,
  `//score/mw/com/rust/score_com_concept:score_com_concept`, `...:score_com_concept-test`,
  `...:score_com_concept-macros-unit-tests`, `...:score_com_concept-macros-tests` (tag `manual`),
  `//score/mw/com/impl/rust/com-api/com-api-ffi-lola:{bridge_ffi_rs,bridge_ffi_lola,registry_bridge_macro_cpp}`,
  `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:{com-api-runtime-lola,com-api-runtime-lola-tests,com-api-runtime-lola-doc-tests}`,
  `//score/mw/com/example/com-api-example:{com-api-example-tokio-integration-test}`,
  `//score/mw/com/example/com-api-example/com-api-gen:com-api-gen`,
  `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`,
  `//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync`,
  `//score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test:test_com_api_async`,
  `//score/mw/com/rust/score_com_macros:score-com-macros-tests`. All use `config = linux_x64`; no QNX
  target is present.
- Evidence classes: everything in the plan is a **proposed check**, not trusted collector evidence,
  direct local execution, or carried evidence.

## 8. Unresolved concerns

1. **Design/interface ownership** — the Method trait/type-state surface (#818) and design (#777) are
   not admitted to the baseline; the correct Rust API/ABI cannot be derived from source.
2. **Prerequisite #781 status** — unknown offline; must be confirmed by a maintainer.
3. **FFI contract** — no Rust Method `extern "C"` symbols and no C++ method registration entry point
   (`EXPORT_MW_COM_METHOD`-equivalent) exist; layout/ABI, ownership, callback reentrancy, teardown,
   error mapping and unwind boundaries are all undefined in Rust.
4. **Sync vs async dispatch** — undecided (issue #767 guidance); changes queue/ownership design.
5. **Downstream coverage** — no Rust Method test resources or generated Method members exist; the
   Method regression set is unknown.
6. **Hashing/raw evidence** — no shell and no collector summary, so file hashes and raw logs cannot be
   produced or bound; preserved as missing.

## 9. Concrete next action

An authorized human must (a) land or admit the #818 Method design and the #777 design at an
authorized revision and (b) confirm prerequisite #781 status. Then this issue can be re-scoped and
implemented against the landed design (expected surfaces: `score_com_concept` Method trait/type-state
+ `interface!` arm + error reason; `com-api-runtime-lola/method.rs`; `com-api-ffi-lola` FFI trait and
`extern "C"` symbols with `catch_unwind`+abort trampolines; C++ registry method macro), and the
preserved `check-plan.json` executed through the trusted Linux collector.

## 10. Acceptance boundary

- **Technical status**: assessment delivered; implementation **blocked/pending** at `381d43d`.
- **Engineering acceptance**: **none claimed**. This packet is exported for offline human review.
  Passing checks or a successful run cannot supply the required human decision, and no native work
  product is marked qualified/accepted/released.
