# External Rust crate integration assessment refresh — eclipse-score/communication #173

Issue: *Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate)*
Repository: `eclipse-score/communication`
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Activity: **assessment refresh** (`task.json` mode `assessment`, `source_read_only: true`).
Platform: Linux only. Engine: DeepSeek Flash (`deepseek`, `fallbacks: []`). Zero source-fix
nodes; no dependency migration, BUILD, lock, lint or source change is made or authorized.
Original correction budget stays `2/3` used; `source_corrections_this_run: 0`.
Engineering acceptance and any retain/replace/internal decision remain **pending offline
authorized humans** (`pending_acceptance: "offline authorized humans"`).

External issue/PR/comment/artifact prose is treated as **data**, not as engineering
acceptance. No native identifier, status, license or confidence decision is invented here.

This document supersedes the previous `.rust-queue/context/previous-assessment/`
dependency assessment **only on claims that the newly retrieved evidence supports**
(§7). Historical claims that were not re-verified this run are retained as historical,
not re-asserted as fresh evidence.

---

## 1. Issue premise: the baseline uses `pastey 0.2.3`, not `paste`

Issue #173 (`open`, label `rust-api`, type `Task`, `sub_issues_summary total 3 / completed 0`,
created 2026-03-06, updated 2026-07-27) words the premise as *"COM-API currently utilizes the
external **paste** crate"*. At the pinned baseline this wording is **outdated**: the interface
macros already use `pastey`, not `paste`.

Confirmed source evidence (read at the baseline workspace):

- `score/mw/com/rust/score_com_concept/interface_macros.rs` — `interface_common!`,
  `interface_consumer!`, `interface_producer!` expand inside
  `score_com::pastey::paste! { ... }` at lines **134, 146, 163, 195**.
- `score/mw/com/rust/score_com_concept/BUILD:22` — `proc_macro_deps` includes
  `@score_communication_crate_index//:pastey` (with `deps` `futures`, `thiserror`).
- `score/mw/com/rust/score_com_concept/lib.rs:29-30` — `#[doc(hidden)] pub use pastey;`.
- `score/mw/com/rust/score_com.rs:144-146` — `#[doc(hidden)] // See
  eclipse-score/communication/issues/173 - pastey replaces paste ... pub use
  score_com_concept::pastey;`.

So the `paste`→`pastey` migration the issue references is **already implemented**. The
single issue comment (`communication-173-comments.json`, 2026-07-27) does not discuss the
premise; it only links `score-crates#42`. Issue #173's own **three sub-issues remain 0/3
completed**; they are not enumerated in this workspace, so their IDs/content stay unknown.

### 1.1 Exact paste operations actually used by COM-API

Only **suffix concatenation** is exercised inside `paste!`:

| Generated name | Patterns / locations |
| --- | --- |
| `{id}Interface` | `[<$id Interface>]` — 135, 147, 209, 239 |
| `{id}Consumer` | `[<$id Consumer>]` — 139, 150, 164, 170, 172 |
| `{id}Producer` | `[<$id Producer>]` — 140, 151, 196, 208, 230, 240, 242 |
| `{id}OfferedProducer` | `[<$id OfferedProducer>]` — 201, 210, 212, 238 |

No prefix composition, no case modifiers (`:lower`, `:snake`, `:camel`, …), no raw `#`
identifier, no `:replace`, no `env!`, and no `#[doc = ...]` concatenation are used by the
COM-API. Those broader surfaces are exercised only in the score-crates acceptance tests
(§5.3), so the crate's full qualification scope is wider than COM-API's observed use.
`interface!` also retains a legacy comma form (99-108) and explicitly rejects `Method`/`Field`
with `compile_error!` (110-122); `interface_consumer!`/`interface_producer!` carry
`compile_fail` doctests for the same rejection.

---

## 2. Score-crates artifacts bound to exact version

`score_communication_crate_index` is resolved by the communication MODULE:
`MODULE.bazel:41` → `bazel_dep(name = "score_crates", version = "0.0.11", repo_name =
"score_communication_crate_index")` (`.bazelversion = 8.7.0`).

Pinned score-crates artifacts (`score-crates-artifacts.json`):

- Source **commit `ee5f1a4f02dcfaa01d7a5e23ec68fd51590a66f8`**, 18 artifacts with
  `git_blob_sha` + `sha256` (docs/test/metadata); e.g. `MODULE.bazel`
  `sha256 1c182542afeab03a944533246c8bac47d963c38a6cf9c11979a69871011c1708`,
  `docs/pastey/docs/component_classification.rst`
  `sha256 44752338f613d939114a02aa404cfb4224b5a081ff487f2b7a876079a1392a85`.
- The snapshot's own `module(name = "score_crates", version = "0.0.7")` field differs from
  the published **0.0.11** consumed by the baseline. `pinned-index-applicability.md` records
  that the exact v0.0.11 archive was downloaded and matched registry integrity
  `9ef61b3c1d2f400b8c73f722b9959a7deebe0626d3943b990aaa00580bafbd77`, and that all 18
  pastey documentation/test artifacts match commit `ee5f1a4f…` **byte-for-byte**; the
  registry metadata version patch accounts for the MODULE version difference. This binding
  does **not** establish compiler certification, downstream adoption acceptance or trace
  report generation.
- Raw binding/evidence is reported outside agent write scope under
  `run-root/context/pinned-index-registry` and `pinned-index-documentation-binding.json`.
  Those raw files are **not present in this workspace** (only `pinned-index-applicability.md`
  is); missing raw evidence is preserved, not fabricated.

### 2.1 Epic `score-crates#42` closure and its meaning

`score-crates-42.json`: **Epic**, **closed 2026-07-09T11:18:44Z**, `state_reason
"completed"`, label `documentation`, 8 comments, sub-issues API returns `[]`. Its
Acceptance (DoD) is: *"Pastey crate qualification related all the artifact should be
reviewed and present on score-crate repo."*

The decisive comment (id `4741408526`, aschemmel-tech, 2026-06-18) states:

> "S-CORE does not qualify platform components, but prepares all necessary artefacts for
> a distributor/integrator to be able to qualify the components as part of his safety
> element."

Comment `4765266558` (2026-06-22) lists the delivered artifacts (Requirements, Design,
Coverage report pointing at **upstream** CI, Component Classification, Traceability via
Lobster `BUILD`, Safety Analysis incl. AoU/RCA); comment `4924508218` (2026-07-09) says
*"All the required artifacts created and updated."* Epic closure therefore means the
**artifact set exists**, not that `pastey` is a **qualified component** and not that a
human accepted the retain/replace/internal approach. This matches the workflow rule that
S-CORE prepares integrator-qualification artifacts; acceptance stays offline.

---

## 3. Inventory: archive / license / edition / MSRV / features vs enabled Bazel features

`crate-provenance-summary.json` records `archive_verified: true` for all 12 named crates.
Archive SHA-256, license, edition and MSRV are **metadata**; "enabled features" below are
what the **generated Bazel files** actually pass to `rust_library`/`rust_proc_macro`
(`crate-builds/*.bazel`). They are distinct from declared feature tables.

| Crate | Archive sha256 | License | Edition | MSRV | Declared features | Enabled `crate_features` (generated Bazel) |
| --- | --- | --- | --- | --- | --- | --- |
| `pastey 0.2.3` | `2ee67f1008b1ba2321834326597b8e186293b049a023cdef258527550b9935b4` | MIT OR Apache-2.0 | 2018 | 1.54 | none (`{}`) | **none** (no `crate_features` attr) |
| `thiserror 2.0.21` | `09e52cb86a36cede5cb101bf8908837b3e4c6e5e59fe7fd85c23fb56200d189e` | MIT OR Apache-2.0 | 2021 | 1.77 | `default`, `std` | `default`, `std` |
| `thiserror-impl 2.0.21` | `fe5197923287db20a58125f0bc85c062f7f2c892de97b18c356f9efb14b28524` | MIT OR Apache-2.0 | 2021 | 1.77 | none (`{}`) | none (proc-macro; deps `proc-macro2`, `quote`, `syn 3.0.6`) |
| `futures 0.3.34` | `9a31d2a3fbaaeb2af2368bbdd904aa8e812d3c04a1ee10d3171f52d556e5d0a3` | MIT OR Apache-2.0 | 2018 | 1.71 | `alloc`, `async-await`, `bilock`, `cfg-target-has-atomic`, `compat`, `default`, `executor`, `io-compat`, `spin`, `std`, `thread-pool`, `unstable`, `write-all-vectored` | `alloc`, `async-await`, `default`, `executor`, `futures-executor`, `std` |
| `futures-util 0.3.34` | `0d50a92467f8ba5dd6e3ee5d4bd04d73ab2e4e1c44474a0674821dfce14b79bc` | MIT OR Apache-2.0 | 2018 | 1.71 | (see provenance) | `alloc`, `async-await`, `async-await-macro`, `channel`, `futures-channel`, `futures-io`, `futures-macro`, `futures-sink`, `io`, `memchr`, `sink`, `slab`, `std` |

Other futures-rs pieces (`futures-channel/-core/-executor/-io/-macro/-sink/-task 0.3.34`)
are recorded with the same license/provenance family; all are Rust 2018.

Notes distinguishing metadata from enabled configuration:

- `futures-executor`, `futures-channel`, `futures-io`, `futures-macro`, `futures-sink`,
  `memchr`, `slab` in the generated Bazel files are **optional-dependency feature names**,
  not entries in the Cargo `[features]` table. Do not read them as declared features.
- `pastey` and `thiserror-impl` compile with **no enabled features**; the generated pastey
  target is a `rust_proc_macro`, `edition = "2018"`, `--cap-lints=allow`.
- License texts are present and hashed: `pastey` `LICENSE-APACHE`
  `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` and `LICENSE-MIT`
  `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`; the same hashes
  apply to `thiserror`/`thiserror-impl`. The archive has **no NOTICE file** (the crate's
  `include` list is CHANGELOG/LICENSE-APACHE/LICENSE-MIT/README/Cargo.toml/src).
- `.cargo_vcs_info.json` for `pastey 0.2.3` records git `sha1
  c377d07c9d1a418e9922af59dc932736752a95cc`. Fork/provenance relationship to upstream
  `paste` is asserted in crate prose ("Successor of paste") but was **not** code-diffed here.

### 3.1 Index entries are not runtime dependencies

`crate-provenance-summary.json` and the score-crates `MODULE.bazel` `crate.spec(...)` list
many crates that the COM-API does not use. In particular `paste 1.0.15` **is in the index**
(`score-crates/MODULE.bazel` `crate.spec(package = "paste", version = "1.0.15")`) but is
**not referenced by the inspected COM-API BUILD** (`score_com_concept/BUILD` uses
`pastey`, `futures`, `thiserror`). An index entry is **not** evidence of a runtime or
build-time dependency. The prior assessment's claim that no COM-API BUILD references
`paste` is retained as **historical** (content search is bounded this run, so it was not
re-derived across every downstream BUILD).

### 3.2 Transitive closure is not fully inventoried

`crate-provenance-summary.json` covers the 12 named crates. Generated Bazel shows further
transitive inputs not covered by that provenance summary (e.g. `memchr 2.8.3`,
`pin-project-lite 0.2.17`, `slab 0.4.12`, `proc-macro2 1.0.107`, `quote 1.0.47`,
`syn 3.0.6`, and whatever `proc-macro2`/`syn` pull). The **complete transitive dependency
closure** therefore remains **unknown**; it must be resolved from the lock/index before any
"all licenses/notices present" claim.

---

## 4. Qualification artifacts: actual UIDs and statuses (external prose, preserved)

From the pinned score-crates documents (treated as data):

| Artifact | Native UID / target | Status / attributes |
| --- | --- | --- |
| Component classification | `doc__pastey_crate_comp_class` (`component_classification.rst`) | status `valid`; safety `ASIL_B`; security `NO`; `realizes: wp__sw_component_class` |
| Architecture | `doc__mod_pastey_architecture` (`architecture/index.rst`) | status `valid`; safety `ASIL_B`; security `NO`; `realizes: wp__component_arch` |
| Feature requirement | `PasteyFeatReq.FEAT_PASTEY_001` v1 | safety `ASIL_B`; `derived_from RustCrateSysReq.ASR_RUST_CRATE@1` |
| Assumed system requirement | `RustCrateSysReq.ASR_RUST_CRATE` v1 | safety `ASIL_B` |
| Component requirements | `PasteyComReq.REQ_COMP_PASTEY_001` … `_015` v1 | safety `ASIL_B`; each `derived_from PasteyFeatReq.FEAT_PASTEY_001@1` |
| Assumption of use | `PasteyAoU.PasteyRustCompilerCertified` v1 | safety `ASIL_B`; `mitigates UncertifiedRustCompiler` |
| Failure mode | `PasteyFailureModes.UncertifiedRustCompiler` v1 | safety `ASIL_B`; guideword `UnintendedFunction`; `interface pastey_pub.paste_macro` |
| FTA root cause | `root_causes/uncertified_rust_compiler_fta.puml` | references the two UIDs above |
| Build trace | `dependable_element pastey` (`docs/pastey/docs/BUILD`) | `integrity_level = "B"`; AoU + feature/component reqs + design + component + FMEA + tests |

Classification outcome: **P = 2, C = 1 → CLAS_OUT = Q** ("Follow the processes for
qualification of software components in a safety context"). The document itself adds that
activity selection applies *"As soon as the change request containing this is in status
'Accepted'"* — i.e. the classification is `valid` prose but the downstream qualification
path is conditional on a human-accepted change request. Prose claims such as "built and
tested using the certified Ferrocene toolchain", 100% function/line/branch coverage via an
upstream CI link, and the `std::env` "same certified toolchain" argument are **external,
not independently verified here**; compiler/target/use-case applicability remains a human
decision (§7).

---

## 5. Executed compatibility evidence (native collector)

`reports/native-check-summary.json` is **present** this run; stage `check` returned
`{"native_passed": true, "checks": 4, "source_unchanged": true}`. `acceptance:
"pending_offline"`; `source_unchanged: true`; `source_subjects: 2878`, vector
`0ef301a348a177d1615221543a6cc4573c838c75ae8f72e6616dd504d73f9b11`.

| # | Kind / config | Targets | Result |
| --- | --- | --- | --- |
| 1 | test `linux_x64` (log `d0ac830e…`) | `//score/mw/com/rust/score_com_concept:score_com_concept-test`, `:score_com_concept-macros-unit-tests` | PASS (2/2); exit 0 |
| 2 | doctest `linux_x64_gcc_15` (log `18c3c312…`) | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | PASS (1/1); exit 0 |
| 3 | test `linux_x64` (log `22e2de9d…`) | `//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync`, `.../consumer_async_apis/integration_test:test_com_api_async` | PASS (2/2, 3 cases each); exit 0 |
| 4 | lint `clippy` (log `2d7d5b31…`) | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/rust:score_com` | success; exit 0 |

These are **real Linux compilation/test/lint runs on the unchanged baseline** (concept +
generated-macro unit cases; the real LoLa producer/consumer integration through generated
Rust APIs; the manual doctest target executed under GCC to work around its documented LLVM
native-link limitation **without** changing BUILD/toolchain pins; pinned Clippy aspect).
The collector's own `native_obligation` is explicit: *"compatibility checks are use-case
evidence, not qualification or human acceptance."* The collector note also states
*"Unexecuted checks are not passed."*

Aggregate: **4 planned, 4 executed, 4 passed, 0 failed**. No failed check is hidden; no
carried test evidence was used (`carried_test_evidence_used: false`). Generated-API
compatibility was measured **only on the baseline** (`pastey`); **no candidate**
(`paste`, integrated or manual implementation) was built, so there is no old/new comparison.

### 5.1 Unexecuted / unavailable checks preserved

- QNX variants and sanitizer variants: excluded by Linux-only task policy — recorded
  unavailable, **not** evaluated, **not** passed.
- Broader inventory present in the previous review packet but not in this run's
  `planned_checks` (dependency-inventory queries, extra build targets,
  `//quality/dependency_compatibility_checker/...` tests, `//score/mw/com:api_surface_test`,
  rustfmt `//:format_test`, `score_com_macros` doctests) remains **planned/unrun** and must
  not be reported as passing.
- `rust_doc_test` `score_com_concept-macros-tests` keeps its `manual` tag in source; it was
  explicitly executed under the GCC config this run.

---

## 6. Options comparison (reviewable proposal — not accepted)

Precise bounded functionality: COM-API needs only compile-time **suffix concatenation** of
one identifier with a fixed type-name suffix, inside proc-macro-generated public items.

| Option | Compatibility / build impact | Provenance / license / maintenance | Qualification & verification effort | Notes |
| --- | --- | --- | --- | --- |
| **Retain `pastey 0.2.3`** | None; already compiled, re-exported and now covered by 4 executed Linux checks. Archive + license/edition/MSRV verified. | MIT OR Apache-2.0, hashed license texts; edition 2018, MSRV 1.54. Advisories/maintenance activity **not** checked. | Reuse existing native checks; score-crates classification/AoU/FMEA artifacts exist and provide an integrator-facing basis. Tool-verification instance still missing. | Lowest churn; matches baseline; blocked on advisories, compiler/target applicability and human acceptance. |
| **Replace with `paste 1.0.15`** | BUILD + `lib.rs`/`score_com.rs` re-export edits; index entry exists. | Upstream suitability unestablished; would re-introduce the state the issue describes. | Full positive/negative macro + downstream re-verification. | Contradicts the already-completed migration; **not** recommended without new evidence. |
| **Integrate into repo** (issue option 1) | Vendor/import macro logic; new in-tree maintained code; touches all `interface_*` macros. | Removes one external proc-macro provider; moves license/notice + maintenance burden in-tree. | Design/maintenance ownership + full verification. | Maps to issue option 1; no authority here. |
| **Manual implementation** (issue option 2) | Reimplement only the four suffix operations; internal code still carries qualification obligations. | Removes `pastey`; internal macro hygiene/diagnostics become project-owned. | Reproduce hygiene/diagnostics + all macro tests/doctests + downstream. | Maps to issue option 2; feasible in principle; no authority here. |

**Candidate recommendation (reviewable, not accepted):** retain `pastey 0.2.3` at this
baseline; route the integrate-vs-manual policy through the now-closed `score-crates#42`
artifact set and the native tool/qualification work products. Rationale: the baseline
already depends on `pastey`, only a narrow well-covered suffix capability is exercised, and
this task holds no authority to change dependencies or accept a qualification. All options
remain open pending authorized humans.

---

## 7. Reconciliation with the previous dependency assessment

| Previous claim (historical) | Refresh status |
| --- | --- |
| `native-check-summary.json` **missing**; all checks planned, 0 executed | **Superseded**: summary present; 4 checks executed and passed (§5). |
| `score-crates#42` unreachable; scope/status/sub-issues unknown | **Superseded**: epic fetched; closed `completed` 2026-07-09; comment clarifies S-CORE prepares integrator artifacts, not qualified components (§2.1). Note #173's own 3 sub-issues remain 0/3. |
| `pastey`/`thiserror`/`futures` license, edition, MSRV, provenance **unknown** | **Partly satisfied**: archives verified, license/edition/MSRV/declared-vs-enabled features and source-text hashes inventoried (§3). |
| Advisories / upstream maintenance activity unknown | **Still unknown** (not checked). |
| Transitive dependency closure | **Still unknown** (provenance covers only named crates) (§3.2). |
| No tool-qualification instance; applicability unknown | **Still unknown**: score-crates provides classification/AoU/FMEA, but no `wp__tool_verification_report`/`wp__tlm_plan` project instance; Ferrocene certification remains prose. |
| No Rust API-surface lock; only downstream compilation | **Still true** (not re-verified for change). |
| `//quality/dependency_compatibility_checker` covers Bazel modules, not Rust crates | Retained as **historical** source claim, not re-verified this run. |
| QNX / sanitizer variants excluded | **Still excluded** (Linux-only policy). |
| Premise "uses `paste`" outdated; uses `pastey` | **Re-confirmed** at the baseline (§1). |
| `paste 1.0.15` in index but unreferenced by COM-API | Retained as **historical**; index-vs-dependency distinction re-stated (§3.1). |

**What is satisfied:** premise reconciliation; exact COM-API paste operations and re-export
locations; score-crates commit/document binding to v0.0.11; epic-closure semantics;
inventory of archive/license/edition/MSRV/features vs enabled Bazel features; four executed
Linux compatibility cases on the unchanged baseline.

**What remains unknown:** current advisories; full transitive closure; compiler/target/
use-case applicability of the Ferrocene certification claim; a tool-verification project
instance; Rust API-surface lock; and human acceptance of the retain/replace/internal
decision and of the qualification artifacts.

**Actual executed compatibility cases:** the four Linux cases in §5 (2 unit/system test
targets, 1 manual doctest under GCC, 1 Clippy lint) — use-case evidence only, never a
qualification or acceptance.

---

## 8. Conclusion

**Assessment deliverable: complete for this refresh scope.** The dependency/design
assessment, premise reconciliation, provenance inventory, artifact UIDs/statuses, executed
compatibility evidence and historical-reconciliation record are consolidated here and bound
to baseline `381d43d…` and score-crates commit `ee5f1a4f…` / module 0.0.11.

**Engineering issue closure: NOT warranted.** Issue #173 remains `open` with 0/3
sub-issues completed; its substance is a policy/qualification decision, and the epic's
closure establishes only that the integrator-facing **artifact set exists**, not that
`pastey` is a qualified component or that a human accepted any option. No source/dependency
change is authorized or made.

### Concrete unresolved obligations

1. **Human acceptance** of the retain/replace/internal approach and of the score-crates
   qualification artifacts (repository `codeowners` + `score-crates`/process owners).
2. **Compiler/target/use-case applicability** of the certified-toolchain claim — resolve
   against the actually selected compiler/target and obtain the applicable tool-verification
   work product; no `wp__tool_verification_report` instance exists.
3. **Advisories and upstream maintenance** for `pastey` (and `thiserror`/`futures`), with a
   retrieval date, before any retain justification is final.
4. **Complete transitive dependency closure** with license/notice coverage (named-crate
   provenance is insufficient).
5. **Rust API-surface compatibility/negative tests**: there is no Rust API-surface lock and
   no candidate build; generated-API compatibility is baseline-only.
6. **Broader check coverage** if the project requires it: QNX and sanitizer variants were
   not run (Linux-only), and the wider previously-planned inventory remains unexecuted.
7. **Preserve missing evidence**: `pinned-index-registry/` and
   `pinned-index-documentation-binding.json` referenced by `pinned-index-applicability.md`
   are not in this workspace; the three #173 sub-issues are not enumerated.

**Next action:** export this refreshed assessment with the collector summary and obtain the
offline human decisions above; keep #173 open. No dependency migration or source change.
