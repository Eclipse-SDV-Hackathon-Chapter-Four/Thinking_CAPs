# Independent supervisor final audit — eclipse-score/communication #1261

Improvement: "Provide an async stream of newly available services" (`rust-api`, state `open`, 0 comments).

This is a **read-only** audit. It was produced from actual workspace source plus the
machine-generated `.rust-queue/reports/native-check-summary.json`. No source file was
edited, no native command was run, no model/subagent was dispatched, no retry occurred,
and no engineering decision or acceptance was granted. Only this report was written.

## Authority, binding and limits

- Baseline commit: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (Linux only; QNX explicitly out of scope).
- Run: `01M49MB1BWVT6CKAZ7WZ7JAYM2`, model DeepSeek Flash, provider `deepseek`.
- Source-correction budget: `source_corrections_max = 3`, recorded
  `source_corrections_used = 2` (one remaining). Implementation entry charged 2/3;
  no retry happened in this run. Issue #250 is exhausted at 3/3 and its source was **not**
  imported; nothing here fixes #250.
- File-tools only: shell, network, delegation, dispatch, publication, locks/pins/licenses
  and human-gate tools were unavailable, so no `git diff`, re-hash or re-execution was
  possible for this report.
- Engineering acceptance remains **pending offline**. Native requirement/design/safety IDs
  were never supplied and are not invented here. Unknowns stay explicitly unknown.

## Verdict

**Not accepted; not completion.** The run's `check` stage failed:
`{"native_passed": true, "checks": 4, "positive_regression_gap": "Required dedicated
heterogeneous stream regression plan absent; compatibility tests cannot establish
completion.", "required_regression_plan_present": false, "changed_files": 3}`.

The actual source is **API scaffolding only** (a provided trait method with a
`NotSupported` default, an owned descriptor type, a FFI container accessor helper and a
re-export). There is **no heterogeneous discovery backend, no continuous stream, no
per-handle identity across FFI, and no dedicated heterogeneous integration test**.
Consequently this cannot be described as a bounded configured-universe implementation
either, let alone unqualified system-wide completion. No engineering decision is accepted.

## Actual source reviewed (current workspace state)

| Artifact | Observed state |
| --- | --- |
| `score/mw/com/rust/score_com_concept/concept.rs` | `ServiceVersion{major,minor}`; owned `ServiceDescriptor`; provided `Runtime::find_all_services` returning `Err(NotSupported)`; 2 unit tests in `mod tests` |
| `score/mw/com/rust/score_com_concept/error.rs` | `ServiceFailedReason::NotSupported` variant present (message: "System-wide service discovery is not supported by this runtime backend") |
| `score/mw/com/rust/score_com.rs` | re-exports `ServiceDescriptor`, `ServiceVersion` |
| `score/mw/com/impl/rust/com-api/com-api-ffi-lola/common.rs` | `HandleContainer` gains `len`/`is_empty`/`first`/`get`/`Index`; `HandleType` remains an opaque `[u8;0]` with **no** identity accessors; unused `use crate::StringView;` at line 23 |
| `score/mw/com/impl/rust/com-api/com-api-runtime-lola/runtime.rs` | e.g. `find_service` still `panic!`s on `FindServiceSpecifier::Any`; `find_all_services` is **not** overridden |
| `score/mw/com/impl/rust/com-api/com-api-runtime-mock/runtime.rs` | `find_all_services` **not** overridden; `find_service` ignores the specifier |
| `score/mw/com/rust/design/high_level_design_detail.md` | §"System-wide discovery" (line ~123) states LoLa does not override `find_all_services`; but the trait table (line ~79) still describes `ServiceDescriptor` as "interface id + instance specifier" |
| `score/mw/com/test/basic_rust_api/...`, `score/mw/com/test/find_any_semantics/...` | existing scoped/C++ tests only; no new stream target/package |

**Recorded-changed-file inconsistency (preserved, not resolved).** The machine summary
records `changed_files = [common.rs, score_com.rs, concept.rs]` (3). Direct source reading
also finds #1261-specific content in `error.rs` and
`rust/design/high_level_design_detail.md`. Because `git diff`/hashing were unavailable
under the file-only read-only constraint, those edits cannot be attributed to this
implementation attempt with certainty; the discrepancy is recorded rather than asserted.

## Required-obligation review (C1–C7)

- **C1 — full native interface identity via an explicit API: NOT MET.** No public
  enumeration of configured service types was added; `Runtime`/`IRuntime` are otherwise
  unchanged. `ServiceDescriptor` (below) is never populated from native configuration.
- **C2 — real wildcard deployment ownership: NOT IMPLEMENTED.** No wildcard/search
  universe exists; LoLa `find_service(Any)` still panics; no synthetic wildcard instance
  records exist to own.
- **C3 — owned descriptors with observed identity: PARTIAL, AND NOT OBSERVED.**
  `ServiceDescriptor{ service_type_name: String, version: ServiceVersion(u32,u32),
  binding: String, service_id: u32, instance_id: u32 }` is owned (no `&'static` leak) and
  derives `Clone, Debug, PartialEq, Eq` (equality exists; **no `Hash`**). There is no
  quality field (deferred as an open decision), and **no native source populates these
  fields**: the only construction is the unit test with hard-coded constants. FFI exposes
  no `GetInstanceId`/version/binding extraction, and `HandleType` is opaque, so the
  "observed native identity" claim in its rustdoc is aspirational, not implemented.
- **C4 — honest universe scoping: DOCUMENTED, NOT IMPLEMENTED.** `find_all_services`'s
  provided default is `Err(ServiceFailedReason::NotSupported)`; neither LoLa nor Mock
  overrides it. Even the bounded configured-universe enumeration is absent, so the issue's
  literal system-wide criterion is untouched.
- **C5 — complete snapshots, membership, dedup/re-offer: NOT IMPLEMENTED.** No stream, no
  set-diffing, no seen-set/refcount, no remove/re-offer handling, no initial-vs-later
  distinction. The rustdoc asserts initial results, inline errors, borrow lifetime and
  drop-termination, but there is no implementing code behind those claims.
- **C6 — own every watch / partial-start failure: NOT IMPLEMENTED.** No multi-watch
  handling and no partial-start cleanup exist.
- **C7 — callback reclamation / ownership: N/A TO THE STREAM (unchanged scoped path).**
  The existing scoped async discovery in `consumer.rs` still uses `Arc<HandleContainer>`
  + `handle_index`, stores the `start_find_service` return handle synchronously, ignores
  the callback's `find_handle`, and calls `stop_find_service` in `Drop`. This change adds
  no callback payload, lock or destructor. New `common.rs` accessors only borrow `&self`
  and add no native identity; `HandleType` stays opaque. `HandleContainer` retains its
  pre-existing `unsafe impl Send/Sync` and pointer-owning `Drop`.

### Synchronization / FFI ownership / Drop / partial-error

- No new synchronization primitive, FFI function, callback or ownership transfer was
  introduced by this change (recorded `changed_files` contains no FFI bridge, runtime or
  consumer source). The stream has no error-partiality, cancellation or drop semantics to
  audit because it never yields a stream on any in-tree backend.
- The newly added `HandleContainer::first/get/Index` return references tied to `&self`;
  `Index` bounds-asserts before the FFI call and `.expect("nullptr received as handle")`.
  No new unsafe `Send`/`Sync` was added.
- Lint regression surfaced as a warning (not an error) in the clippy check:
  `unused import: crate::StringView` at `com-api-ffi-lola/common.rs:23`.

## Actual regression evidence (from `native-check-summary.json`, unmodified)

Overall summary: `passed = true`, `exit_code = 0`, `required_regression_plan_present = false`.
The driver-level `check` stage nonetheless **failed** on the missing dedicated plan, so the
green native run must not be read as completion.

| # | Kind / config | Targets | Exit | Wrapper cases | Child suite cases (raw XML) |
| --- | --- | --- | --- | --- | --- |
| 0 | test / `linux_x64` | `com-api-runtime-lola-tests`, `configuration_test`, `runtime_test`, `score_com_concept-test`, `score_com_concept-macros-unit-tests` | 0 | 5/5 pass | lola-tests 1; configuration 2+21+2+5=30; runtime 1+4+12=17; concept-test `tests="1"`; macros-unit `tests="1"` (Σ=50) |
| 1 | test / `linux_x64` | `test_com_api_sync`, `test_com_api_async`, `test_find_any_semantics` | 0 | 3/3 pass | sync 3; async 3; find_any 1 (Σ=7) |
| 2 | doctest / `linux_x64_gcc_15` | `score_com_concept-macros-tests` | 0 | 1/1 pass | macros-tests 1 |
| 3 | lint / clippy `linux_x64` | concept, `score_com`, lola, `bridge_ffi_rs`, `bridge_ffi_lola` | 0 | — | warnings only: unused `StringView` (common.rs:23); `result_unit_err` (bridge_ffi.rs:259); `missing_transmute_annotations`+`clone_on_copy` (consumer.rs:950/1164) |

Child-count caveat preserved from the summary note: "XML wrappers differ from Rust child
cases." `score_com_concept-test`'s XML reports `tests="1"` while `concept.rs` source defines
2 `#[test]` cases (`test_instance_specifier_validation`,
`test_service_descriptor_identifies_service_and_interface`); the raw Rust case count is not
recoverable under the read-only/file-only constraint and is left explicit, not rounded.

Also preserved: `score_com_concept-macros-tests` (rust_doc_test) carries
`tags = ["manual"]` in `score_com_concept/BUILD`, so check 2 only ran because it was named
explicitly; it is normally excluded.

### Which issue criteria the evidence actually exercises

1. **System-wide newly available services** — not exercised anywhere; the only in-tree
   stream is the feature's `NotSupported` default. **Absent.**
2. **Item identifies service and interface** — exercised only by a unit test constructing
   `ServiceDescriptor` from hard-coded values; no native identity path. **Not established.**
3. **Documents initial results/errors/lifetime/termination** — rustdoc/design prose exists
   for the default-only method; there is no implementing behavior to validate. **Prose only.**
4. **Existing scoped APIs remain** — compatibility argued by additivity and covered by the
   existing sync/async/`find_any` runs; no baseline-vs-candidate generated-API compat
   measurement was recorded. **Partially covered.**

`basic_rust_api` sync/async tests use `find_service::<BigDataInterface>(Specific)` and event
receive; `find_any_semantics` is a C++ per-`InstanceSpecifier` wildcard. Neither is a
heterogeneous Rust stream test, and no `regression-plan.json` / dedicated target exists
(`required_regression_plan_present = false`).

## Preserved failures, gaps and unknowns (not fabricated, not filled)

- Run-level `check` stage **failed**; `implementation` stage **failed** (DeepSeek Flash).
  The green native compatibility run does not override these outcomes.
- Missing required deliverable: a dedicated heterogeneous two-interface stream regression
  plan/target; its absence is the recorded `positive_regression_gap`.
- Native identity, all-services FFI selector, continuous initial/later/dedup/re-offer,
  removal/re-offer, partial-start and Drop-quiescence semantics remain **unimplemented and
  unexecuted**.
- `ServiceDescriptor` rustdoc claims are unverified by any implementation.
- Requirements/design/safety IDs are unknown; the issue-template "Affects Detailed Design"
  box is unchecked and was not treated as an authoritative decision.
- #250 contract (typed wildcard vs system-wide) is unresolved and was not imported.
- No QNX checks (out of scope). No collector or directly executed evidence beyond the
  recorded native summary; report hashes could not be recomputed here.
- Recorded source-subject vector hash: `97e10c3b295cf690779cf89db4f72cd478e9b767693dd860209b254aabcda652`
  (as recorded in `native-check-summary.json`; not independently recomputed).

## Pending offline decisions (not accepted here)

1. Accept/reject the provided-`NotSupported` trait shape and the 5-field descriptor.
2. Decide descriptor quality/selector inclusion and equality/dedup identity (`Hash`).
3. Decide whether/how a bounded configured-universe backend is authorized, and how it is
   labelled against the issue's literal "system-wide" criterion.
4. Decide initial-empty vs first-offer semantics, re-offer/dedup policy, and
   partial-start/Drop-quiescence contract.
5. Resolve the `ServiceDescriptor` documentation inconsistency (design table vs actual
   fields) and the `NotSupported` enum-variant exhaustiveness impact on downstream matches.

## Concrete next action

Authorized reviewers must decide (1)–(5) offline. Any further implementation must add a
real two-interface native stream path with observed per-handle identity, honest
universe/qualification scope, and a dedicated heterogeneous regression target, then be
re-measured; this run supplies neither that source nor that acceptance.
