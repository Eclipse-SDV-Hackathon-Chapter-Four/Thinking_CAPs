# Scope — eclipse-score/communication issue #1265

**Title:** Improvement: `paste` crate usage in the Rust COM API
**Mode:** reuse (assessment / draft + collector plan). No source repair allocated.
**Platform:** Linux only. QNX is out of scope. Reasoning model: DeepSeek Flash.

This report scopes the current baseline against the issue acceptance criteria and the
actual native build/verification obligations, and defines the Linux collector check plan
(`check-plan.json`). It makes no qualification or acceptance claim. Engineering acceptance
remains offline and pending. The agent drafts; deterministic commands measure.

## Binding

| Item | Value | Source |
| --- | --- | --- |
| Issue | `eclipse-score/communication#1265`, state `open` (observed 2026-10-04/05) | `.rust-queue/context/issue.json` |
| Task baseline (selected source) | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` | `.rust-queue/context/task.json` |
| Historical integration baseline | `8368bfb5b182ae6642d963b58ad4bac5dabc02c3` | `historical-README.md`, `historical-deterministic-review-checks.json` |
| Historical Rust unit/doctest baseline | `e3d126c2d7569345cf5f790310702eb00cd86b06` | `historical-README.md` |
| Reuse mode | `"mode": "reuse"`, `native_results_promoted_to_current_baseline: false`, `max_source_corrections: 0` | `.rust-queue/context/task.json` |
| Correction budget | historical native run used 3 of 3; remaining 0. Not reset; old run not rerun. | `historical-engineering-review.json`, `historical-qualification-checklist.md` |
| Permitted writes | this disposable workspace only | task envelope |
| Permitted actions | file tools; shell, delegation, publishing and acceptance tools blocked | task envelope |

Baseline note: the current workspace HEAD carries only the queue's `preflight`/`start`
commits over code baseline `381d43de`. The static subjects previously recorded by the
offline review were measured at `8368bfb5`; therefore that evidence is treated as
**historical** and is not promoted to this baseline (see `current-baseline-review-note.md`).

## Baseline reconciliation — the issue premise is stale

The issue prose says the interface macros "use the `paste!` procedural macro". At the
selected baseline the code already uses **`pastey`**, not `paste`:

- `score/mw/com/rust/score_com_concept/interface_macros.rs` contains four host-expansion
  blocks `score_com::pastey::paste! { ... }` (source lines 134, 146, 163, 195) with 22
  identifier-interpolation occurrences of four suffix patterns:
  `[<$id Interface>]`, `[<$id Consumer>]`, `[<$id Producer>]`, `[<$id OfferedProducer>]`.
- `score/mw/com/rust/score_com_concept/BUILD` declares the macro dependency as
  `proc_macro_deps = ["...", "@score_communication_crate_index//:pastey"]`.
- `MODULE.bazel` pins `score_crates` 0.0.11 as `score_communication_crate_index`
  (the crate-index module that resolves `pastey`).
- `score_com_concept/lib.rs` re-exports `pastey` (`#[doc(hidden)] pub use pastey;`) and
  `score_com.rs` forwards it (`pub use score_com_concept::pastey;`) with the comment
  `See eclipse-score/communication/issues/173 - pastey replaces paste`.

So a migration from archived `paste` to `pastey` already exists at this baseline (tracked
under issue #173). No `paste` (archived original) usage was observed in the COM macro
surface. The open #1265 work is therefore an **assessment**: record the pin/features/usage,
review provenance/license/maintenance/safety relevance, document the retain/replace/internal
decision, and record qualification artifacts. The off-line engineering review
(`historical-engineering-review.json`) already recommends **retaining the locked
pastey 0.2.3** as a proposal, with formal adoption/qualification pending.

## Issue acceptance mapping (current baseline)

| Issue acceptance criterion | Current-baseline evidence | Status |
| --- | --- | --- |
| Record pinned crate version, enabled features and exact identifier-pasting patterns | `pastey 0.2.3`, edition 2018, MSRV 1.54; **no** resolved/declared features; no normal/build dependencies; 4 `paste!` blocks; 22 occurrences of the four suffix patterns (carried static facts, content-checked). Build/lock/feature resolution must be re-measured by the collector. | Carried static facts; fresh measurement pending |
| Review provenance, license, maintenance status and safety relevance | Both MIT/Apache-2.0 license texts and archive checksum `2ee67f10…` retained in the historical packet; provenance Git SHA `c377d07c…`. Dated maintenance observations only (no security clearance). Host macro execution is a build-time trust boundary; wrong-but-compilable identifiers are the residual failure mode. | Dated assessment; not security/safety clearance |
| Document retain vs `pastey` vs internal implementation | Historical review recommends retaining locked `pastey 0.2.3`; returning to archived `paste` adds cost without demonstrated benefit; an internal generator would inherit its own hygiene/diagnostics/qualification burden. | Proposal only; human decision pending |
| Record required qualification artifacts and validate any replacement against the generated API | Qualification/verification gaps recorded (R1–R6 in the historical review + `historical-qualification-checklist.md`). **No replacement was introduced**, so replacement-equivalence testing is inapplicable here; existing generated-API compatibility is exercised by the Linux consumer checks in `check-plan.json`. | Obligations recorded; actual qualification pending |

The `Requirements / Architecture` checkbox in the issue template is not treated as evidence
that those artifacts are unaffected; impact is assessed from source and the historical trace.

## Actual native obligations and open prerequisites (must remain open)

- **R1 — exact compiler qualification scope unestablished.** The supplied score-crates AoU
  `PasteyAoU.PasteyRustCompilerCertified@1` requires a safety-certified compiler (ASIL B).
  The only available version evidence is a rolling/nightly Ferrocene build (rustc
  `1.94.0-nightly (779fbed05)`, LLVM 21.1.5, `x86_64-unknown-linux-gnu`). No certificate/use-scope
  package is supplied. Open.
- **R2 — published classification ≠ communication adoption.** `doc__pastey_crate_comp_class`
  (status valid, ASIL_B, security NO, P2/C1/Q) and `doc__mod_pastey_architecture` are upstream
  facts; the Accepted change request, adapted safety plan and communication adoption are absent. Open.
- **R3 — upstream rationale statements need clarification** (compile-time env vs runtime
  configuration; hidden aliases vs entry-point complexity). Open; no reclassification performed.
- **R4/R5 — upstream requirement-linked tests are not executed here and some do not exercise
  the cited behavior; negative compile-fail results and LOBSTER-parser trace gaps need
  outcome-specific binding.** The score-crates targets `//docs/pastey/tests:pastey_*` were not
  run in this workflow. Open.
- **R6 — 204 historical copyright findings retain pending native dispositions.** No current
  checker run is claimed. Open.
- **Tool-management applicability is unresolved.** `wp__tlm_plan` and `wp__tool_verification_report`
  are version-1/status-valid **type definitions**, not communication instances. Whether the host
  procedural-macro generator is subject to tool management remains an open tailoring question.
- **Replacement/design prerequisites remain open:** no replacement is implemented; the
  retain/replace/internal choice and any design/backend impact are undecided outside this agent.

## Carrier and freshness rules applied

- Historical native results are **carried, not promoted**: six Linux integration cases at
  `8368bfb5` (sync/async `basic_rust_api`) and 33 passed / two ignored Rust unit/doctest cases
  at `e3d126c2`. These are historical evidence only.
- Static facts (paste patterns, dependency, BUILD/lock subjects) were **content-compared**
  against the current source before carrying; no agent recomputation of SHA-256 was possible
  (shell/collector blocked). Fresh hash measurement is delegated to the collector in
  `check-plan.json`.
- `native-check-summary.json` was **not present** under `.rust-queue/reports/` when this scope
  was drafted; its absence is preserved (see "Missing evidence").

## Missing / failed evidence (preserved, not resolved)

- `.rust-queue/reports/native-check-summary.json` — **absent** at draft time; collector output pending.
- Sealed historical native-verification packet (1,359 subjects, manifest
  `bb7972f2…`) and raw command/log evidence live outside agent authority.
- Exact-build compiler certificate package (R1); Accepted component change request and
  communication adoption records (R2); current-baseline copyright checker run (R6).
- QNX checks: unavailable and out of scope for this Linux-only task.

## Explicit non-claims

This is an agent-drafted scope and check plan. It does **not** qualify, certify, approve or
accept `pastey`, the compiler, the generated API, or the change; it does not alter any native
status/UID; and it does not close any safety/copyright finding. Tests, clean analyzers and
workflow success cannot supply a human engineering decision.

## Deliverables

- `check-plan.json` — Linux collector plan (native BUILD-derived targets only; no shell commands).
- `current-baseline-review-note.md` — current-vs-historical subject comparison and carrier rules.
