# Scope and binding — eclipse-score/communication issue #1261

"Improvement: Provide an async stream of newly available services"

- Repository: `eclipse-score/communication`
- Issue: `#1261` (`rust-api`, state `open`, 0 comments, `blocked_by=0`, no linked PR
  visible in the supplied context)
- Baseline commit: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- Workspace: `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-rust-issue-queue-ycbvxir7/workspaces/1261`
- Context retrieval time (issue/comments/task envelope reads): 2026-10-06
- Stage: binding/design draft. No shell, delegation, publish or acceptance tools are
  available to this stage; no native command was executed and no native evidence was
  produced here.

## 1. Authority and limits for this stage

- Deliverable path: `.rust-queue/reports/` only.
- Read-only source inspection elsewhere in the disposable workspace.
- Target platform: Linux only. QNX is explicitly out of scope for this task and no QNX
  target is selected or planned.
- This document is a **draft**. It recommends and proposes; it does not accept an
  engineering decision, qualify a work product, or claim native pass. Deterministic
  command stages and authorized humans own measurement and acceptance.
- Issue prose was treated as task data. The issue body's unchecked
  "Affects Detailed Design" box is not treated as an authoritative requirements decision.

## 2. Issue acceptance criteria (from issue #1261 body)

1. The stream reports **newly available services system-wide**, not only later instances
   for one `FindServiceSpecifier`.
2. **Each item identifies its service and interface** (interface-independent descriptor).
3. The API **documents initial results, errors, and stream lifetime/termination**.
4. **Existing interface-scoped discovery APIs remain available.**

Reference in the issue: `eclipse-score/communication#9`. The task brief additionally names
**#250 as a prerequisite to investigate, not an asserted solved dependency**.

## 3. Current source binding (baseline)

### 3.1 Abstraction layer — `score_com_concept`

`score/mw/com/rust/score_com_concept/concept.rs`

- `Runtime::find_service<I>(&self, FindServiceSpecifier) -> Self::ServiceDiscovery<I>`
  (lines 109–121). Discovery is **scoped to one interface** `I` chosen at the call site.
- `FindServiceSpecifier` (lines 286–297): `Specific(InstanceSpecifier) | Any`.
- `ServiceDiscovery<I, R>` (lines 549–583): `get_available_instances()` and
  `get_available_instances_async()` both return `Self::ServiceEnumerator`
  (`IntoIterator<Item = ConsumerBuilder<I, R>>`). The async form resolves **once** with the
  initial set; it is not a continuously-updating stream.
- `ConsumerDescriptor<R>` (lines 585–595) exposes only `get_instance_specifier()`.
  The interface is identified statically by `I`, not by the descriptor.
- `Interface::INTERFACE_ID` (line 397) is the only interface identifier and is only
  reachable through the generic interface type.
- A `Stream` is already used in-tree (`Subscription::to_stream`, line 931), so a stream API
  is stylistically consistent and `futures::stream::Stream` is already a dependency
  (`score_com_concept/BUILD` `@score_communication_crate_index//:futures`).

### 3.2 LoLa runtime — `com-api-runtime-lola`

`score/mw/com/impl/rust/com-api/com-api-runtime-lola/runtime.rs`

- `find_service` (lines 40–52) **panics** on `FindServiceSpecifier::Any`:
  `"FindServiceSpecifier::Any is not supported in LolaRuntimeImpl"`.

`score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs`

- `LolaConsumerDiscovery<I, B>` (lines 857–871) stores a single `InstanceSpecifier` plus
  `PhantomData<I>`.
- `get_available_instances_async` (lines 917–981) registers a C++ find-service callback that
  stores the latest `HandleContainer` and wakes an `AtomicWaker`.
- `ServiceDiscoveryFuture::poll` (lines 1011–1055) `.take()`s the stored handles **once** and
  returns `Poll::Ready(Ok(available_instances))`; the future then completes.
- `Drop for ServiceDiscoveryFuture` (lines 998–1009) always calls `stop_find_service`, i.e.
  discovery is torn down when the one-shot future resolves or is dropped.
- `ConsumerDescriptor::get_instance_specifier` for `LolaConsumerBuilder` (lines 1070–1078)
  **panics** (`"InstanceSpecifier::ANY is not supported in LolaRuntimeImpl"`); there is no
  interface-id accessor on the builder/descriptor.

Design intent documented at
`score/mw/com/design/service_discovery/README.md` lines 121–139: `StartFindService` returns
a `FindServiceHandle`; the callback (`OnFound`) constructs `HandleType`s and may be invoked
**repeatedly on change**, can be invoked in parallel, and in `ANY` semantics the
`InstanceIdentifier` bound into the `HandleType` must be replaced with the concrete found
one. Lines 147–210 describe the LoLa `inotify` worker thread and serialized `OnFound`
invocation and `StopFindService` blocking semantics.

### 3.3 FFI bridge — `com-api-ffi-lola`

`score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs`

- `FFIBridge::start_find_service(&self, callback: &FindServiceCallable, instance_spec: InstanceSpecifier) -> *mut FindServiceHandle`
  (lines 239–243): **one instance specifier**, no ALL/system-wide selector.
- `FFIBridge::find_service(&self, instance_specifier: InstanceSpecifier) -> Result<HandleContainer, ()>`
  (line 259): same single-specifier shape. No "find all services" entry point.
- `FindServiceCallable` (lines 316–336) callback signature is
  `FnMut(HandleContainer, NativeFindServiceHandle)`.

`score/mw/com/impl/rust/com-api/com-api-ffi-lola/common.rs`

- `HandleType` (lines 24–28) is an **opaque** `[u8; 0]` wrapper. `HandleContainer`
  (lines 104–170) exposes only `len`, `first`, `get`, and indexing; it does **not** expose
  the interface id, service id, version, binding, or quality of a discovered instance.

### 3.4 Mock runtime — `com-api-runtime-mock`

`score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs`

- `find_service` (lines 74–81) ignores the specifier and returns a `MockConsumerDiscovery`.
- `ServiceDiscovery` impl (lines 399–414) returns empty vectors; no continuous or
  system-wide discovery.
- `MockConsumerBuilder::get_instance_specifier` (lines 458–463) returns the stored specifier.
- The design doc marks the mock runtime "not yet enabled in the current build"
  (`rust/design/high_level_design_detail.md` line 143) and `:score_com_mock` is `testonly`.

### 3.5 Re-export and downstream

- `score/mw/com/rust/score_com.rs` lines 134–142 re-exports the concept trait surface via
  `score_com_concept::*`; `score_com` is `//score/mw/com/rust:score_com`.
- Existing downstream discovery use is one-shot:
  `score/mw/com/test/basic_rust_api/consumer_async_apis/consumer_app.rs` lines 202–208 calls
  `runtime.find_service::<BigDataInterface>(FindServiceSpecifier::Specific(spec))` then
  `get_available_instances_async().await`.

## 4. Verification of ALL/ANY (system-wide) backend availability

Requirement from the task brief: "verify backend ALL/ANY discovery availability."

| Layer | ALL / `FindServiceSpecifier::Any` availability | Source |
| --- | --- | --- |
| `score_com_concept` | `Any` variant exists but is only a selector | `concept.rs` 286–297 |
| LoLa runtime | **Not available** — `find_service` and `ConsumerDescriptor::get_instance_specifier` panic | `runtime.rs` 43–48; `consumer.rs` 1070–1078 |
| LoLa design doc | `FindServiceSpecifier::Any` support checkbox empty `[ ]` | `rust/design/high_level_design_detail.md` line 118 |
| LoLa FFI | **No ALL selector** — `start_find_service`/`find_service` take exactly one `InstanceSpecifier` | `bridge_ffi.rs` 239–243, 259 |
| FFI handle identity | **Not exposed** — `HandleType` opaque, no interface/service/instance accessors on the handle | `common.rs` 24–28, 104–170 |
| Mock runtime | No real backend; `find_service` ignores the specifier | `runtime.rs` 74–81, 399–414 |

**Conclusion (source-backed):** at baseline `381d43d`, system-wide / ALL discovery is not
implemented anywhere reachable from the Rust API, and the FFI/C++ boundary does not expose
the identity fields a system-wide descriptor needs. A genuine implementation of acceptance
criterion 1 therefore depends on backend/FFI capability that is **absent at this baseline**.
That dependency is the class of prerequisite the brief points at (#250); it must **remain
open** here because it is not established by the baseline source.

## 5. Prerequisite and PR activity check

- Local source contains no `find_all_semantics` package; the label
  `//score/mw/com/test/find_all_semantics:...` is referenced only as a visibility string in
  `score/mw/com/test/find_any_semantics/BUILD` (lines 48, 65) and does not resolve to a
  package in this baseline.
- No existing `ServiceDescriptor`, `discover_all*`, or system-wide stream symbol exists in
  the concept crate or runtimes.
- Issue #1261 has 0 comments and `blocked_by=0` in the supplied context; no linked PR is
  present.
- **#250 content and status could not be retrieved** in this environment (network/web access
  and shell are unavailable). #250 is therefore recorded as an **open, unverified
  prerequisite**, explicitly *not* an asserted solved dependency. Its scope (what backend /
  FFI capability it adds, and whether it is merged at this baseline) is unknown.

## 6. Proposed design (DRAFT — requires authorized review; not applied)

The design must preserve criteria 3 and 4 and keep the change surface consistent with the
existing abstraction. The following is a proposal only.

### 6.1 Descriptor

Introduce an interface-independent descriptor carrying at least the interface identity and
the instance identity:

```rust
// score_com_concept/concept.rs (proposed)
#[derive(Clone, Debug)]
pub struct ServiceDescriptor {
    interface_id: String,            // or &'static str if backend guarantees it
    instance_specifier: InstanceSpecifier,
    // OPEN: service_id / instance_id / version / binding / quality required by
    // design/service_discovery/README.md lines 83-91 — content still a design decision.
}

impl ServiceDescriptor {
    pub fn interface_id(&self) -> &str { /* ... */ }
    pub fn instance_specifier(&self) -> &InstanceSpecifier { /* ... */ }
}
```

Rationale: criterion 2 needs both fields; criterion 1 needs them for interfaces the caller
did not name, so the descriptor must not be generic over `I`.

### 6.2 Subscription entry point — two candidate shapes (open decision)

- **Option A (associated type + required method).**
  `type ServiceStream: Stream<Item = Result<ServiceDescriptor>> + Send;` plus
  `fn discover_all_services(&self) -> Result<Self::ServiceStream>;`
  Pro: no heap trait object. Con: a required associated type/method is a **breaking change**
  for every `Runtime` implementer, including out-of-tree implementers.
- **Option B (provided method returning a boxed stream; non-breaking for implementers).**
  `fn discover_all_services(&self) -> Result<Pin<Box<dyn Stream<Item = Result<ServiceDescriptor>> + Send + '_>>>`
  with a provided default returning a new `ServiceFailedReason::NotSupported`
  (or `Unsupported`) error.
  Pro: preserves existing implementers; heap allocation happens only at initialization.
  Con: adds a trait object and a new error variant; still requires a real backend to satisfy
  criterion 1.

Both options keep `find_service`, `ServiceDiscovery`, `get_available_instances`, and
`get_available_instances_async` unchanged (criterion 4). The choice is an **open engineering
decision**; the brief forbids inventing the accepted one.

### 6.3 Documented semantics (criterion 3) — to be attached to the chosen entry point

- **Initial results:** services already available when the stream is created are reported as
  the first items (mirrors the LoLa synchronous initial `OnFound` described in
  `design/service_discovery/README.md` lines 178–186). Whether an initial empty result is
  `Some(empty)` or simply no item until the first offer is an open decision.
- **Items and errors:** propose `Item = Result<ServiceDescriptor>`, matching
  `Subscription::to_stream` (`concept.rs` 926–931). A discovery error is yielded inline; it
  does not silently swallow subsequent availability.
- **Duplicate / update policy:** whether a re-offered or restarted instance is re-reported,
  and whether the callback's *full current set* is diffed to "newly available" or yielded
  wholesale, is an open semantic decision that depends on the backend callback contract
  (design README lines 128–139).
- **Lifetime:** items borrow the subscription/discovery owner (like `to_stream`'s `'a`);
  the stream must not outlive the runtime/discovery handle.
- **Termination:** the stream ends only when the user drops it or the owning
  subscription/discovery is stopped; it does not terminate on a yielded error. Dropping the
  stream must call the backend stop (LoLa `stop_find_service`), matching the existing
  `Drop for ServiceDiscoveryFuture`.

### 6.4 Backend work (OPEN / blocked)

Realising criterion 1 requires (all **unknown until #250/backend is understood**):

1. A C++/FFI "find all services" or ALL-specifier path, replacing the single
   `InstanceSpecifier` in `start_find_service`/`find_service`.
2. FFI exposure of per-handle identity (interface id + service/instance identity) that
   `HandleType`/`HandleContainer` currently hide.
3. A LoLa `ServiceDiscovery` implementation that keeps the stream alive across callbacks
   instead of `.take()`-ing one snapshot, while preserving the documented serialized
   `OnFound` / `StopFindService` blocking semantics.
4. A mock implementation for tests (test-only), or an explicit "unsupported" disposition.

Until (1)–(3) are resolved, criteria 1 and 2 cannot be satisfied by a Rust-only change.

## 7. Impact and compatibility

| Surface | Impact | Disposition |
| --- | --- | --- |
| `score_com_concept` public trait surface | Adds descriptor + entry point | Draft only; Option A/B open |
| `find_service` / `ServiceDiscovery` / `get_available_instances*` | Must remain source-compatible | Preserved by both options (criterion 4) |
| `com-api-runtime-lola` | Needs real stream impl + new FFI | Blocked on backend prerequisite |
| `com-api-runtime-mock` | Needs stub/impl | Open; test-only today |
| `bridge_ffi_rs` / C++ bridge | Needs new find-all + identity FFI | Unknown; #250-class |
| Error enum (`error.rs`) | Likely new `ServiceFailedReason` variant | Proposed, not accepted |
| `score_com` re-exports | Must add new public types | Downstream compile check required |
| Requirements/design docs | Issue offers no accepted requirement change; the "Detailed Design" box is unchecked | Treat as **unknown**; do not self-assert a requirements decision |
| API-surface check (`//score/mw/com:api_surface_test`) | **C++ only** (`quality/api_surface/README.md`); no Rust lock file exists | Rust compatibility evidenced by downstream compilation + doc tests |

## 8. Pending offline acceptance and missing evidence (preserved)

- **No native evidence was produced by this stage.** `native-check-summary.json` is
  **absent** under `.rust-queue/reports/` at the time of writing; its absence is recorded,
  not fabricated.
- **No command was run**, so there are no exit codes, logs, tool identities, or subject
  hashes to report. All checks in `check-plan.json` are *declared* obligations for the
  deterministic command stage.
- **#250 is unresolved/unknown** and is the principal blocker; #9 reference not retrieved.
- **Network/PR retrieval unavailable**, so "no linked PR" is a statement about the supplied
  context, not a verified absence upstream.
- **Requirements/tailoring decision is pending**: the issue's "Affects Detailed Design" box is
  unchecked and no requirement/design IDs were supplied; no native obligation is asserted.
- **Backend/FFI decision is pending**: descriptor content, ALL-selector design, duplicate
  policy, and the Option A/B trait shape require an authorized human decision.

## 9. Concrete next actions

1. Authorized human/owner retrieves #250 and #9 and confirms whether a backend/FFI
   ALL-discovery capability exists upstream (this unblocks §6.4).
2. Decide Option A vs Option B and the descriptor field set (§6.1–6.2).
3. Then implement the concept change plus the LoLa/FFI/mock work, and run the checks in
   `check-plan.json` on `linux_x64`.
4. Re-bind this scope document to the post-implementation source digest before any
   acceptance claim.

## 10. Source references (baseline `381d43d`)

- `score/mw/com/rust/score_com_concept/concept.rs` (109–121, 286–297, 391–402, 549–595, 926–931)
- `score/mw/com/rust/score_com_concept/error.rs` (22–36, 113–128)
- `score/mw/com/rust/score_com_concept/lib.rs`; `.../BUILD`
- `score/mw/com/impl/rust/com-api/com-api-runtime-lola/runtime.rs` (32–57)
- `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs` (857–871, 917–1055, 1070–1078)
- `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD`
- `score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs` (66–86, 399–414, 458–463)
- `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs` (239–259, 316–336)
- `score/mw/com/impl/rust/com-api/com-api-ffi-lola/common.rs` (24–28, 104–170)
- `score/mw/com/impl/rust/com-api/com-api-ffi-lola/BUILD`
- `score/mw/com/rust/score_com.rs` (134–142); `score/mw/com/rust/BUILD`
- `score/mw/com/rust/design/high_level_design_detail.md` (118, 143)
- `score/mw/com/design/service_discovery/README.md` (83–91, 121–139, 147–210)
- `score/mw/com/test/basic_rust_api/consumer_async_apis/consumer_app.rs` (202–208)
- `score/mw/com/test/find_any_semantics/BUILD` (48, 65); `.../integration_test/BUILD`
- `.bazelversion` (`8.7.0`); `MODULE.bazel` (rules_rust `0.68.2-score`,
  score_toolchains_rust `0.10.0`, score_rust_policies `0.0.5`, score_crates `0.0.11`)
- `.bazelrc` (linux_x64 default); `quality/static_analysis/static_analysis.bazelrc`
  (clippy_strict aspect); `BUILD` (`//:format_test`); `CI.md` (Rust lint job, API checks)
