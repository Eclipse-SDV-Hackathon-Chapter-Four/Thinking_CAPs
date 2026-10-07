# Supervisor review — external Rust crate integration assessment refresh

Issue: *Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate)* —
`eclipse-score/communication` **#173** (open, label `rust-api`, type `Task`).
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Reviewed artifact: `.rust-queue/reports/assessment.md` (assessment stage, DeepSeek Flash).
Mode: `assessment`, `source_read_only: true`; `source_corrections_this_run: 0`; original
correction budget `2/3` used. `pending_acceptance: "offline authorized humans"`.

This review independently re-read the assessment's cited source, context, pinned
score-crates documents and the native collector summary. It makes no source edit, runs no
build/test, does not re-hash artifacts, and grants no engineering acceptance. Only this
file was written.

---

## 1. Verdict

**The assessment is reviewable.** Its central factual claims are supported by the source,
context and native evidence present in this workspace, it preserves the unresolved gaps,
and it correctly separates use-case compatibility evidence from qualification/acceptance.
No **material false claim** was found. A small number of citation/clarity defects are
recorded in §3; none changes the assessment's conclusion or its missing-evidence record.

Assessment **completion** is distinct from:
- **implementation** — none is required or authorized (zero source-fix nodes; no dependency,
  BUILD, lock, lint or source change);
- **qualification** — not established (see §4);
- **issue closure** — not warranted; `#173` remains `open` with `sub_issues_summary 3 / 0
  completed`.

The retain / replace / integrate / manual decision remains a **reviewable proposal** and is
**not** approved by this review.

---

## 2. What was independently re-verified as accurate

Source (baseline `381d43d…`):

- `score/mw/com/rust/score_com_concept/interface_macros.rs` — `interface_common!`,
  `interface_consumer!`, `interface_producer!` expand inside `score_com::pastey::paste!`
  at lines 134, 146, 163, 195; only suffix composition `[<$id Interface>]`,
  `[<$id Consumer>]`, `[<$id Producer>]`, `[<$id OfferedProducer>]` is used (lines
  135/147/209/239, 139/150/164/170/172, 140/151/196/208/230/240/242, 201/210/212/238).
  Legacy comma form is at 98–108 and `Method`/`Field` `compile_error!` at 110–122;
  `compile_fail` doctests for the same rejection exist for `interface!`,
  `interface_common!`, `interface_consumer!` and `interface_producer!` (e.g. 356–417,
  486–569, 601–651, 681–…). The assessment's §1/§1.1 characterisation is correct.
- `score/mw/com/rust/score_com_concept/BUILD:20–32` — `proc_macro_deps` includes
  `@score_communication_crate_index//:pastey`; `deps` are `futures`, `thiserror`; the
  `rust_doc_test` target keeps `tags = ["manual"]`; test target is
  `target_compatible_with = ["@platforms//os:linux"]`.
- `score/mw/com/rust/score_com_concept/lib.rs:29–30` — `#[doc(hidden)] pub use pastey;`.
- `score/mw/com/rust/score_com.rs:144–146` — `#[doc(hidden)] pub use
  score_com_concept::pastey;` with the issue-citing comment.
- `MODULE.bazel:41` — `bazel_dep(name = "score_crates", version = "0.0.11",
  repo_name = "score_communication_crate_index")`; `.bazelversion` = `8.7.0`.

Context / issue activity:

- `issue-173-current.json`: open, `sub_issues_summary total 3 / completed 0`, one comment.
- `communication-173-comments.json`: the single comment merely links `score-crates#42`.
- `score-crates-42.json`: Epic, `state_reason "completed"`, closed `2026-07-09T11:18:44Z`,
  label `documentation`, 8 comments; `score-crates-42-subissues.json` is `[]`.
- `crate-provenance-summary.json`: 12 named crates, all `archive_verified: true`, with
  archive sha256, license `MIT OR Apache-2.0`, edition, MSRV and declared features; the
  assessment's §3 table values match (e.g. `pastey 0.2.3` archive
  `2ee67f10…35b4`, license-text hashes `62c7a1e3…` / `23f18e03…`, edition 2018, MSRV 1.54).
- `.rust-queue/context/crate-builds/*.bazel`: `pastey` is a `rust_proc_macro`,
  edition 2018, `--cap-lints=allow`, no `crate_features`; `futures 0.3.34`
  `crate_features = [alloc, async-await, default, executor, futures-executor, std]`;
  `thiserror 2.0.21` `[default, std]`; `thiserror-impl 2.0.21` deps
  `proc-macro2 1.0.107`, `quote 1.0.47`, `syn 3.0.6`; `futures-util 0.3.34`
  `[alloc, async-await, async-await-macro, channel, futures-channel, futures-io,
  futures-macro, futures-sink, io, memchr, sink, slab, std]`. All match the assessment.

Pinned score-crates documents (treated as data) — the assessment's §4 UIDs/attributes are
verbatim correct:

- `component_classification.rst` — `doc__pastey_crate_comp_class`, `valid`, `ASIL_B`,
  `security NO`, `realizes wp__sw_component_class`; P=2, C=1, **CLAS_OUT = Q**; activity
  selection applies only "As soon as the change request containing this is in status
  'Accepted'"; the Ferrocene / 100 % coverage / `std::env` statements are prose.
- `architecture/index.rst` — `doc__mod_pastey_architecture`, `valid`, `ASIL_B`,
  `security NO`, `realizes wp__component_arch`.
- `feature_requirements.trlc` — `PasteyFeatReq.FEAT_PASTEY_001@1` ←
  `RustCrateSysReq.ASR_RUST_CRATE@1`, `ASIL_B`.
- `component_requirements.trlc` — `REQ_COMP_PASTEY_001`…`_015`, v1, `ASIL_B`, each
  `derived_from PasteyFeatReq.FEAT_PASTEY_001@1`.
- `aou.trlc` — `PasteyAoU.PasteyRustCompilerCertified` v1, `mitigates
  UncertifiedRustCompiler`; `failure_modes.trlc` — `PasteyFailureModes.UncertifiedRustCompiler`
  v1, `UnintendedFunction`, `interface "pastey_pub.paste_macro"`.
- `docs/pastey/docs/BUILD` — `dependable_element pastey`, `integrity_level = "B"`,
  AoU + feature requirements + architectural design + component + dependability analysis +
  tests.
- `score-crates/MODULE.bazel` (snapshot commit `ee5f1a4f`, `module version 0.0.7`) declares
  `crate.spec(package = "paste", version = "1.0.15")` (lines 414–417) and
  `crate.spec(package = "pastey", version = "0.2.3")` (lines 442–445), supporting the
  assessment's index-vs-dependency distinction (§3.1).

Native collector — `reports/native-check-summary.json` is present; stage `check` returned
`{"native_passed": true, "checks": 4, "source_unchanged": true}`;
`source_subjects: 2878`; `source_subject_vector_sha256:
0ef301a348a177d1615221543a6cc4573c838c75ae8f72e6616dd504d73f9b11`;
`acceptance: "pending_offline"`. The assessment's §5 table reproduces the four checks,
configs, logs and pass counts exactly (check 1 `linux_x64` test 2/2; check 2
`linux_x64_gcc_15` doctest 1/1; check 3 `linux_x64` integration 2/2 with 3 cases each;
check 4 `clippy` lint success).

---

## 3. Findings (none material)

**F1 — citation, not a falsehood.** §5 states "no carried test evidence was used
(`carried_test_evidence_used: false`)". `native-check-summary.json` contains **no**
`carried_test_evidence_used` field; the same conclusion is supported only by its `note`
("Newly measured tests; no carried test evidence."). The substance is correct; the named
field does not exist. This is a trace-citation defect and should not be quoted as a JSON
key.

**F2 — §4 wording nuance.** §4 describes the `dependable_element pastey` build trace as
"AoU + feature/component reqs + design + component + FMEA + tests". The pinned BUILD's
`requirements` attribute lists only `//docs/pastey/docs/requirement:feature_requirements`;
the `REQ_COMP_PASTEY_001`…`_015` component requirements exist as documents but are not
directly named in that BUILD rule. The artifact set is real; the attribute-level mapping
is slightly overstated.

**F3 — version provenance clarity (version/trace gap).** The pinned `score-crates`
snapshot in the workspace is `module version 0.0.7` at commit `ee5f1a4f`, and its
`crate.spec` entries are **caret/minimum** requirements (`futures = "0.3.31"`,
`thiserror = "2.0.18"`, `proc-macro2 = "1.0"`, `quote = "1.0"`, `syn = "2.0"`). The §3
inventory instead lists **resolver-resolved lock** versions (`futures 0.3.34`,
`thiserror 2.0.21`, `proc-macro2 1.0.107`, `quote 1.0.47`, `syn 3.0.6`) taken from the
generated `crate-builds/*.bazel`. Both sets are individually verified above, but the
assessment does not spell out that these are spec-versus-locked resolutions rather than
values authored at `ee5f1a4f`. It also omits the direct `syn 2.0.119` used by
`score_com_macros`, present in the prior assessment. This should be read as a trace
clarification, not as a contradiction.

**F4 — binding rests on absent raw evidence.** The `module 0.0.7` ↔ published `0.0.11`
and "18 artifacts match `ee5f1a4f` byte-for-byte" binding is asserted only in
`.rust-queue/context/pinned-index-applicability.md`. The raw files it cites
(`run-root/context/pinned-index-registry` and `pinned-index-documentation-binding.json`)
are **not present** in this workspace. The assessment explicitly preserves this (§2, §8.7)
and does not fabricate the missing raw evidence; the binding is therefore not independently
re-derivable here (see §5).

**F5 — Linux-only framing.** §5.1 correctly records QNX and sanitizer variants as
excluded/unavailable, not passed. The Linux-only scope is stated in the task envelope and
echoed by the `BUILD` "Linux only until QNX" comment; it is not a native sign-off.

---

## 4. Actual compatibility outcomes (as measured)

- **4 planned, 4 executed, 4 passed, 0 failed**, all on the **unchanged baseline**
  (`source_unchanged: true`): two `linux_x64` unit/concept test targets, one explicit
  `manual` `rust_doc_test` executed under `linux_x64_gcc_15`, and the pinned Clippy aspect
  on `score_com_concept` + `score_com`; plus a `linux_x64` LoLa producer/consumer
  integration pair (3 cases each).
- No **candidate** (`paste`, integrated logic, or manual implementation) was built, so
  there is **no old/new comparison**. Generated-API compatibility is baseline-only.
- The wider previously-planned inventory (dependency-inventory queries, additional build
  targets, `//quality/dependency_compatibility_checker/...` tests,
  `//score/mw/com:api_surface_test`, rustfmt `//:format_test`, `score_com_macros`
  doctests), QNX variants and sanitizer variants remain **unexecuted / unavailable** and
  must not be reported as passing. The assessment preserves this.
- Per the collector's `native_obligation`, these are **use-case compatibility checks, not
  qualification or human acceptance**; "Unexecuted checks are not passed."

---

## 5. Preserved missing evidence and unresolved obligations

1. **Human acceptance** of the retain/replace/integrate/manual approach and of the
   score-crates qualification artifacts (repository `codeowners` +
   `score-crates`/process owners) — pending, offline.
2. **Compiler/target/use-case applicability** of the certified-toolchain claim: no
   `wp__tool_verification_report` / `wp__tlm_plan` project **instance** exists; the
   Ferrocene certification is external prose; the classification's own trigger is a
   change request in status "Accepted".
3. **Advisories / upstream maintenance** for `pastey`, `thiserror`, `futures` — not checked
   (no retrieval date).
4. **Full transitive dependency closure** — unknown; provenance covers only the 12 named
   crates, while generated builds reference further inputs (`memchr 2.8.3`,
   `pin-project-lite 0.2.17`, `slab 0.4.12`, `proc-macro2 1.0.107`, `quote 1.0.47`,
   `syn 3.0.6`, and the direct `syn 2.0.119`) and their own closures; license/notice
   coverage over that closure is not established.
5. **Rust API-surface lock** — none; no negative/API-surface test was run.
6. **Raw binding evidence absent** — `pinned-index-registry/` and
   `pinned-index-documentation-binding.json` are not in the workspace; the
   `ee5f1a4f`/`0.0.11` byte-for-byte binding is carried only as the applicability note.
7. **`#173` sub-issues (3/0)** are not enumerated in the workspace, so their IDs/content
   stay unknown.
8. **Qualification status** — `score-crates#42` closure means the integrator-facing
   artifact set exists; it does **not** establish that `pastey` is a qualified component,
   that a distributor/integrator qualified it, or that any human accepted an option.
   S-CORE prepares artifacts; qualification is an integrator/human action.

---

## 6. Review conclusion and instruction

- **Assessment deliverable:** complete for this refresh scope and **reviewable** as-is.
  Its §7 reconciliation of the prior (superseded) claims is accurate; the prior
  "summary missing / 0 executed" and "`score-crates#42` unreachable" claims are correctly
  marked superseded only on newly supported points, and unverified historical claims are
  retained as historical.
- **Implementation:** none, correctly (no source/dependency change; correction budget
  unchanged at 2/3).
- **Qualification:** **not** established; no automated approval, no `valid`/`qualified`
  upgrade of external prose.
- **Issue closure:** **not** warranted; keep `eclipse-score/communication#173` open.
- **Next action:** export this refreshed assessment with the collector summary and F1–F4
  noted, and route to offline authorized humans for the decisions in §5.1–§5.3. No
  dependency migration or source change is authorized by this review.
