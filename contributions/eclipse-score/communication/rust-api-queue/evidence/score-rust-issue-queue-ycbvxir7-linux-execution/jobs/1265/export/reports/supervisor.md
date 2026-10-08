# Supervisor review — eclipse-score/communication issue #1265

**Title:** Improvement: `paste` crate usage in the Rust COM API
**Issue state:** `open` (observed in `issue.json`; updated 2026-10-04T11:20:36Z)
**Reviewed task baseline:** `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
**Mode:** `reuse` — `native_results_promoted_to_current_baseline: false`, `max_source_corrections: 0`
**Platform:** Linux only. QNX excluded (out of scope, not run).
**Reviewer role:** independent, read-only supervisor. No shell/collector/acceptance authority.
**Reviewed artifacts:** `.rust-queue/reports/scope.md`, `check-plan.json`,
`current-baseline-review-note.md`, plus the actual source/BUILD/MODULE read directly.

This note is the supervisor's independent review of the scope, the (non-)patch and the
measured evidence. It grants no qualification, certification or engineering acceptance and
changes no native ID, UID, version or status.

## Verdict

**The deliverable is a source-consistent assessment/draft, not an implemented issue fix.**
The scope and the check-plan are technically sound and internally consistent with the
selected source. The issue remains **open** and the engineering decision remains
**pending human acceptance**. There is **no measured current-baseline native evidence in
this workspace** — `native-check-summary.json` is absent and `check-plan.json` is an
unexecuted plan. Workflow/scope success therefore cannot be read as issue closure.

| Dimension | Disposition |
| --- | --- |
| Scope correctness | Sound; issue premise correctly reconciled as stale (baseline uses `pastey`, not `paste`). |
| Patch | None. No production source change exists or is authorized (`max_source_corrections: 0`); the historical documentation patch is outside this workspace. |
| Measured evidence | **Missing.** Plan only; no collector summary; historical dynamic results carried, not promoted. |
| Acceptance | **Pending**; no authorized-human decision, no certification, no native status change. |
| Overall | Assessment-draft complete at agent level; not a fix; not qualified. |

## What I independently verified (read-only, bounded)

Confirmed by reading the selected source directly:

- `score/mw/com/rust/score_com_concept/interface_macros.rs` contains exactly four
  host-expansion blocks `score_com::pastey::paste! { ... }` at lines **134, 146, 163, 195**.
- The 22 interpolation occurrences match the recorded distribution:
  `[<$id Interface>]` ×6 (135,136,147,148,209,239), `[<$id Consumer>]` ×5
  (139,150,164,170,172), `[<$id Producer>]` ×7 (140,151,196,208,230,240,242),
  `[<$id OfferedProducer>]` ×4 (201,210,212,238).
- `score_com_concept/BUILD` declares `proc_macro_deps = [..., "@score_communication_crate_index//:pastey"]`;
  `rust_test :score_com_concept-test` is Linux-only; `:score_com_concept-macros-tests`
  (`rust_doc_test`) carries the `manual` tag and the documented LLD/native-linking limitation;
  `:score_com_concept-macros-unit-tests` runs `rust_unit_test` over `interface_macros.rs`.
- `score_com_concept/lib.rs` re-exports `pastey` (`#[doc(hidden)] pub use pastey;`);
  `score_com.rs` forwards it with the `#173 - pastey replaces paste` comment.
- `MODULE.bazel` pins `score_crates` 0.0.11 as `repo_name = "score_communication_crate_index"`
  (the index that resolves `pastey`).
- Every target label used in `check-plan.json` exists in the workspace BUILD files
  (`:score_com_concept`, `//score/mw/com/rust:score_com`, `:score-com-macros`,
  `:register_interface`, the three concept test/doc targets, `:score-com-macros-tests`, and both
  `basic_rust_api` integration targets). Labels are BUILD-derived; no QNX label is used.
- The macro deliberately rejects `Method<..>`/`Field<..>` via `compile_error!`; the four
  positive doctests plus two `compile_fail` doctests are present.

I could not recompute SHA-256 (shell/collector are outside agent authority), so I confirm
subjects by **content match**, exactly as the scope and review note state.

## Correctness / FFI / concurrency / trace / qualification gaps

- **Correctness.** The observed behavior is the four type-name suffix patterns plus an
  interface-ID constant. The residual failure mode is a macro that produces
  *wrong-but-compilable* identifiers/associations, which only downstream compilation/use
  detects. No replacement was introduced, so baseline/candidate equivalence testing is
  correctly recorded as inapplicable; the live risk is that **no fresh current-baseline
  consumer check has been run**.
- **Issue-prose vs source.** The issue text cites "getter and setter" / "accessor" name
  generation. No accessor pasting exists in the observed macro surface; the scope's
  reconciliation is accurate and should not be "fixed" to match the prose.
- **FFI.** Generated Rust interface/consumer/producer types feed the C++ registration path
  (`:register_interface`). The plan builds that consumer but does **no ABI/layout proof**.
  That is acceptable only because no ABI-affecting change exists; it is not evidence of ABI
  compatibility and must not be reported as such.
- **Concurrency.** `paste!` is compile-time identifier concatenation only; it adds no
  synchronization semantics. The async integration cases exercise cancellation/streaming,
  but they are **historical** and do not isolate pasting behavior.
- **Trace.** The published classification acknowledges a LOBSTER parser limitation that
  omits Rust test results from requirement traces (R5). No outcome-bound requirement→result
  trace exists here.
- **Qualification.** R1–R6 remain open: exact-build compiler certificate/use-scope (R1),
  published classification ≠ communication adoption (R2), upstream rationale wording (R3),
  linked upstream tests not executed and partly non-exercising (R4), negative-check causality
  and trace binding (R5), 204 historical copyright dispositions (R6). Tool-management
  applicability for the host procedural-macro generator is unresolved.

## Agreement / divergence with the scope

I agree with the scope's core conclusions: stale `paste` premise, `pastey` at baseline,
assessment-only work, retain-locked-`pastey-0.2.3` as a *proposal*, and Linux-only framing.
Two plan-completeness observations (not defects):

1. Acceptance criterion 1 asks to record the **pinned version and enabled features**. The
   plan re-resolves `pastey` only transitively through building `:score_com_concept`; it has
   no explicit `query`/lock-inspection target for the crate-index resolution, so version
   `0.2.3` / edition 2018 / MSRV 1.54 / no-features currently rest on **carried historical**
   facts and cannot be freshly asserted from the plan alone.
2. The plan exercises generated-API compatibility but includes no explicit assertion of the
   generated `INTERFACE_ID` seed-suffix semantics (`module_path!() + stringify!($id)`) beyond
   the unit/doc targets; that is acceptable coverage, but the limitation should stay stated.

## Missing / failed evidence preserved (unresolved)

- `.rust-queue/reports/native-check-summary.json` — **absent** (reports dir contains only
  `check-plan.json`, `current-baseline-review-note.md`, `scope.md`). No collector result exists here.
- `check-plan.json` — **plan, unexecuted**. Eleven proposed checks, zero measured outcomes.
- Historical dynamic results carried, **not promoted**: six Linux integration cases at
  `8368bfb5` (sync/async `basic_rust_api`) and 33 passed / two ignored Rust unit+doctest cases
  at `e3d126c2`. These are historical evidence only.
- Sealed historical native-verification packet (1,359 subjects, manifest `bb7972f2…`) and raw
  command/log evidence live outside agent authority.
- R1 exact-build compiler certificate/use-scope package; R2 Accepted change request +
  communication adoption/safety-plan records; R6 current-baseline copyright checker run.
- QNX checks: unavailable and out of scope for this Linux-only task.
- Correction budget: the inherited native run consumed **3 of 3** corrective fixes
  (remaining 0); it is not reset and not rerun.

## Pending offline acceptance

The retain-locked-`pastey-0.2.3` recommendation remains a **proposal**. All R1–R6 gaps, the
compiler-certificate package, the Accepted change request and communication adoption/safety
plan, current-baseline copyright disposition, and the tool-management applicability
determination stay open for authorized humans. No qualification, certification, approval or
acceptance is asserted, and none can be supplied by tests, clean analyzers or workflow success.

## Concrete next action

1. Obtain authorized execution of `check-plan.json` on `381d43de` (Linux) and record outcomes
   in `native-check-summary.json`, binding current-baseline subject hashes; add an explicit
   pastey crate-index resolution check if fresh version/feature measurement is required.
2. Route R1–R6 with the exact-build compiler certificate and the Accepted change
   request/communication adoption records to the authorized native reviewers.
3. Keep the issue open and the decision pending until authorized offline acceptance; do not
   label this design/blocker assessment as an implemented issue fix.
