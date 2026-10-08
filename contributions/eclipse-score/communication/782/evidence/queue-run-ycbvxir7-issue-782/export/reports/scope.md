# Scope — Issue #782: Runtime implementation for Rust Method APIs

## 1. Binding

- **Repository / issue**: `eclipse-score/communication` — issue **#782** "Improvement: Runtime
  implementation for Rust Method APIs" (state `open`, label `rust-api`, author
  `bharatGoswami8`). Source: `.rust-queue/context/issue.json`.
- **Baseline commit**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (working tree also carries the
  Fabro `start`/`preflight` commits `4a3e24e`, `5b254e9`; no source edits by this run).
- **Task envelope**: `.rust-queue/context/task.json` — mode `implementation`, single issue,
  `max_source_corrections = 3`, Linux native checkpoints. Retrieval time for context: from the
  supplied snapshot only (2026-09-08 issue update; comments 2026-08-28 … 2026-09-08).
- **Authority limits honoured**: DeepSeek Flash only; Linux only; no QNX task/execution;
  file tools only (shell, network/web, delegation, publishing and acceptance tools were blocked
  in this environment). Command stages and raw evidence remain outside agent authority.
- **Retrieved context is a snapshot, not live**: PR/issue network state could not be re-fetched,
  so PR #777 / #818 / issue #781 statuses below are recorded as reported, not re-verified.

## 2. Requested outcome (issue prose, treated as data)

The issue asks, per its "What"/"How":

1. Implement the LoLa Runtime backend for the Rust Method APIs following the designed interface
   traits (design referenced as PR #777 / the `#818` trait-macro-type-state layer).
2. Align with the existing Event backend implementation pattern and behaviour.
3. Implement the required FFI APIs so Rust Method APIs interoperate with the C++ runtime.

Milestone boundary established by the maintainer in the issue comments:
- E2E protection for Rust Methods/Fields is **out of scope** for milestone 1 (recommended as a
  separate improvement ticket; the task notes the E2E exclusion as #1062).
- `Runtime` layer is backend-specific and invokes bridge FFI that maps to C++ (comment
  2026-09-08); a Rust-only sync/async bridge is not the root-cause fix (issue #767 is the C++
  backend concern).

## 3. Baseline source findings (bounded reads, exact locations)

**Finding A — the Rust Method API surface does not exist at the baseline.** There is no
`score_com_concept` Method trait, no macro arm, no error variant, no `com-api-runtime-lola`
method module and no Method FFI binding:

| Evidence | Location (baseline) | Observation |
|---|---|---|
| Trait surface | `score/mw/com/rust/score_com_concept/concept.rs` (read 1–987) | Defines `Runtime`, `ProviderInfo`, `Builder`, `Interface`, `Producer`, `OfferedProducer`, `Consumer`, `Publisher`, `Subscriber`, `Subscription`, `Sample*`, `CommData`, `PlacementDefault`. No Method/Caller/Handler trait. |
| Interface macro | `score/mw/com/rust/score_com_concept/interface_macros.rs:110-122` | `Method<$event_type>` arm emits `compile_error!("Method definitions are not supported in this macro version. …")`; same for `Field<T>`. |
| Macro negative test | `…/interface_macros.rs:356-386` | `compile_fail` doctest `interface_macro_with_Method` asserts Method rejection. |
| Error contract | `score/mw/com/rust/score_com_concept/error.rs:113-128` | `Error` variants: Service/Producer/Consumer/Event/Allocate/Receive only. No `MethodFailedReason`. |
| LoLa runtime crate | `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD:16-53`; `lib.rs:28-34` | Modules are `consumer`, `producer`, `runtime` only (no `method.rs`); exports are Event-side types only. No `LolaMethodCaller`/`LolaMethodHandler`. |
| FFI bridge trait | `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs:80-266` | `FFIBridge` methods are event/proxy/skeleton/service-discovery only; no method-call FFI. |
| FFI `extern "C"` | `…/bridge_ffi_lola.rs:130-399` | Declares only event/skeleton/proxy/find-service FFI symbols; no `mw_com_*method*` symbol. |
| Runtime design table | `score/mw/com/rust/design/high_level_design_detail.md:99-118` | "Supported score_com_concept Traits by LoLa Runtime" lists no Method trait. |

**Finding B — the C++ Method backend already exists, but is not reachable from Rust.** The
method implementation, bindings, factories and tests are present under:
`score/mw/com/impl/methods/{proxy_method*,skeleton_method*}`,
`score/mw/com/impl/bindings/lola/methods/*`,
`score/mw/com/impl/bindings/{lola,mock_binding}/*_method*`,
`score/mw/com/impl/plumbing/*method_binding_factory*`,
`score/mw/com/test/methods/*`, `score/mw/com/test/move_semantics/*method*`.
The `ProxyMethodBase`/`SkeletonMethodBase` abstractions (read headers) confirm the backend
call/handler model, callback/queue/in-arg/return-value lifetime machinery that any Rust FFI must
mirror. There is currently **no** Rust `extern "C"` / registry entry for it
(`registry_bridge_macro.cpp/h`, `register_interface.*` remain event-oriented at baseline).

## 4. Prerequisite / PR activity (as reported; not re-verifiable offline)

- **PR #777** — "Rust Method APIs design". Referenced by the issue body as the delivered design.
  Network retrieval blocked → head/base/merge status **unknown** offline.
- **PR #818** — "method design (trait/macro/type-state layer)". Maintainer comment 2026-08-31:
  *"The design proposed in …/pull/818 is still under review."* Contributor 2026-08-28 reports
  `LolaMethodCaller`/`LolaMethodHandler` in `com-api-runtime-lola/method.rs` are `todo!()`
  placeholders — that file/state is **not present at the selected baseline**, so it must live on
  the #818 branch. Merge status **unknown**.
- **Prerequisite #781** — required status: **UNKNOWN / not retrievable offline**. No local
  reference to 781 exists in the supplied snapshot; this remains an open prerequisite.
- **#1062 / #1278 / #767 / #490** are referenced from issue text / BUILD comments; only their
  stated exclusions are used (E2E out of scope; QNX test enablement tracked separately;
  C++-side backend concern; mock runtime not ready).

## 5. Acceptance-criteria → native-obligation mapping

| Issue criterion | Native obligation (source) | Status at baseline |
|---|---|---|
| LoLa Runtime backend implements designed Method traits | Design PR #777 + #818 trait/macro/type-state layer | **Blocked / open** — design not in baseline; cannot be source-bound without inventing it |
| Alignment with Event backend pattern | Event runtime/FFI pattern in `com-api-runtime-lola` + `com-api-ffi-lola` | Pattern observable; Method application unknown until design lands |
| Required FFI APIs for external runtime interop | C++ Method backend + `registry_bridge_macro`; ABI/callback/teardown/error/unwind contract | **Open** — no Rust Method FFI symbols; contract not defined in Rust |
| Linux-only verification | BUILD `target_compatible_with = ["@platforms//os:linux"]`; QNX tracked by #1278 | Observable in BUILD; Method tests do not exist yet |
| E2E protection excluded | Milestone decision in issue comments (#1062) | Excluded from scope |

## 6. Proposed (contingent) change plan — not executed

Implementation is **gated on the design prerequisite**. No source patch is produced by this run
because doing so would require inventing the Method trait/type-state/FFI contract that #818 owns.
When the design lands at an authorised baseline, the smallest change set is expected to touch:

1. `score_com_concept` — Method trait(s)/type-state + `interface!` macro arm replacing the
   `compile_error!`, and `error.rs` Method failure reason(s), per #818.
2. `com-api-runtime-lola` — new `method.rs` implementing the Method traits against `FFIBridge`,
   mirroring `producer.rs`/`consumer.rs` ownership (`Arc` proxy/skeleton managers,
   `ManuallyDrop` + `Drop` cleanup of C++ objects).
3. `com-api-ffi-lola` — extend `FFIBridge` + `bridge_ffi_lola.rs`/`bridge_ffi_mock.rs` with
   Method call/handler FFI, plus `registry_bridge_macro.{h,cpp}` registration, preserving
   `catch_unwind`/abort error-unwind boundary used by existing callbacks.
4. `score_com.rs` re-exports; `com-api-example` + `basic_rust_api` Method downstream usage.
5. BUILD updates must keep the Linux-only test constraint and add no QNX work.

Required design questions that MUST be answered by the design owner before coding (remain open):
sync vs real-async dispatch (issue #767 / maintainer guidance), callback reentrancy and
cancellation, in-arg/return-value queue and lifetime ownership across FFI, and the exact Rust
error mapping.

## 7. Out of scope

- E2E protection for Rust Methods/Fields (separate ticket; #1062 exclusion).
- QNX build/execution for Rust tests (#1278) and any QNX task.
- Changing the C++ Method backend semantics, the Event backend, toolchain pins, lint policy,
  license headers or published native IDs/statuses.

## 8. Native evidence status (preserved, not fabricated)

- **Missing**: `.rust-queue/reports/native-check-summary.json` is **absent** in this workspace;
  the promised native-collector summary and raw logs are not available to this agent. All
  executed/omitted check results therefore remain **unmeasured**, not passing.
- No Bazel build/test/query/lint command was executed (command stages are outside agent
  authority in this environment).
- The proposed checks are recorded in `check-plan.json`; obligations that depend on the open
  design are explicitly marked unknown.

## 9. Conclusion

**Technical status**: implementation cannot proceed at baseline `381d43d` — the Rust Method API
design/contract (#777/#818) and prerequisite #781 are unresolved and not present in the source.
This run delivers a source-bound scope and check plan and keeps the design prerequisite open.

**Engineering acceptance**: none claimed. Offline, authorised reviewers must (a) land/admit the
#818 design, (b) confirm #781 status, then (c) re-scope the runtime/FFI implementation against
that design.
