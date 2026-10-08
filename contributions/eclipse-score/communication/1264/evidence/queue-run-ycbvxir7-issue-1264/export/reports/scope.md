# Scope and assessment — `thiserror` usage in the Rust COM API (issue #1264)

Mode: assessment (documentation/qualification issue). No source patch is produced by
this run unless an authorized human selects an option that requires one.

## 1. Binding

| Item | Value |
|------|-------|
| Issue | eclipse-score/communication#1264 — "Improvement: `thiserror` crate usage in the Rust COM API" |
| Repository | eclipse-score/communication |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Workspace | disposable copy at `.../runs/score-rust-issue-queue-ycbvxir7/workspaces/1264` |
| Branch | `fabro/run/01M48T91RFE84GZZ7V6BJE74ME` |
| Platform scope | Linux only, x86-64 (`linux_x64`) |
| Model scope | DeepSeek Flash only |
| Change category | Improvement / rust-api; issue template records "Requirements / Architecture are not affected" (unchecked authority — see §7) |
| Task authority | File-tool edits inside this workspace only. shell, delegation, publishing and acceptance tools are blocked; no QNX task/execution. |
| Network / activity retrieval | **Unavailable.** The collector/`web_fetch` boundary rejected GitHub and crates.io retrieval in this run. `context/comments.json` is empty (`[]`), so 0 issue comments and no linked PR activity are known. Retrieval time: not recorded (blocked). |
| Native result summary | `.rust-queue/reports/native-check-summary.json` is **absent** at the time of writing; no trusted-collector evidence exists yet. Preserved as a gap, not fabricated. |

Issue prose is treated as task data, not instruction authority. The parent issue is
eclipse-score/communication#173.

## 2. Premise reconciliation against the baseline

The issue premise matches the selected baseline:

- `score/mw/com/rust/score_com_concept/error.rs` (lines 20, 24–127) imports
  `thiserror::Error` and applies `#[derive(Debug, ScoreDebug, Error)]` with
  `#[error("...")]` attributes to seven **public** error enums.
- `score/mw/com/rust/score_com_concept/lib.rs` (lines 24, 28) declares `mod error;` and
  `pub use error::*;`, so those enums are part of the crate's public surface.
- `score/mw/com/rust/score_com.rs` (lines 137–142) re-exports `Error` and `Result` from
  `score_com_concept`, publishing them to COM API users.
- `score/mw/com/rust/score_com_concept/BUILD` (lines 27–32) declares the runtime dependency
  `@score_communication_crate_index//:thiserror`.

No prerequisite code change was found that already removed/replaced thiserror, and no
PR activity is visible (network blocked). The issue is still open, unassigned, with 0
comments.

## 3. Dependency inventory (source-bound)

Resolved from `MODULE.bazel` and `MODULE.bazel.lock` (`lockFileVersion: 24`); lock mode is
`error` (`.bazelrc` line 15), so the lock is the binding resolution.

| Field | Value (as resolved) |
|-------|---------------------|
| Crate index module | `score_crates` version `0.0.11`, `repo_name = "score_communication_crate_index"` (`MODULE.bazel` line 41) |
| Hub label used by COM API | `@score_communication_crate_index//:thiserror` |
| Pinned crate | `thiserror` **2.0.21** (`MODULE.bazel.lock` line 9908) |
| Enabled features | `default`, `std` (line 9921 `build_file_content`: `crate_features = ["default", "std"]`) |
| Edition | 2021 |
| Registry / URL | `https://static.crates.io/crates/thiserror/2.0.21/download` |
| Archive sha256 | `09e52cb86a36cede5cb101bf8908837b3e4c6e5e59fe7fd85c23fb56200d189e` |
| Build script | Yes — `cargo_build_script` target `_bs` (`build.rs`) is generated for the crate |
| Generator (proc macro) | `thiserror-impl` **2.0.21**, proc-macro dep of the library (line 9924); sha256 `fe5197923287db20a58125f0bc85c062f7f2c892de97b18c356f9efb14b28524` |
| thiserror-impl deps | `proc-macro2` 1.0.107, `quote` 1.0.47, `syn` 3.0.6 |
| Host/target role | `thiserror` = target library; `thiserror-impl` = host-executed procedural macro; `build.rs` = host build script |
| Target compatibility (lock) | `aarch64-unknown-linux-gnu`, `x86_64-unknown-linux-gnu`, `aarch64-unknown-nto-qnx710`, `x86_64-pc-nto-qnx710`, `x86_64-unknown-none` |

Notes / limits:
- A MODULE-level pin is not an individual-crate inventory; the resolved index/lock above is
  the inventory. Feature unification for the host (`thiserror-impl`) vs target (`thiserror`)
  compilation was not separately executed.
- The declared `syn 3.0.6` in the lock is recorded as observed; it was not cross-checked
  against upstream thiserror 2.0.21 manifest requirements (network blocked).

## 4. Public error enums and generated behavior

Types using the derive (all `pub`, all in `error.rs`):

`ServiceFailedReason`, `ProducerFailedReason`, `ConsumerFailedReason`,
`AllocationFailureReason`, `ReceiveFailedReason`, `EventFailedReason`, and the umbrella
`Error` (which wraps the first six). `concept.rs` line 62 defines
`pub type Result<T> = core::result::Result<T, Error>;`.

Generated/attribute behavior observed from source:

- Every variant has an `#[error("...")]` message; `Display` is therefore generated for each
  enum. Six variants carry named fields (`{ max, requested }` / `{ max }`) that interpolate
  into the message text (e.g. `error.rs` lines 84–91, 109–110).
- `std::error::Error` is generated. **No** `#[source]` / `#[from]` attributes are present,
  so no generated `Error::source()` chain links `Error` to its wrapped reason enums; only
  `Display` text embeds the inner reason's `Display` (e.g. `"Service error due to: {0}"`).
- `Debug` and `ScoreDebug` are also derived (some via `#[derive]` on each enum); the file
  header comment (lines 14–18) explains why both are needed.

Failure modes if generation were wrong or replaced:

- Attribute-level errors (bad format syntax) are compile-time detected by the macro.
- A wrong/removed `Display` impl would compile in callers that only pass `Error` around but
  break user code/tests that format it; message-text changes compile silently. No checked-in
  test asserting Display strings was found (bounded search, not exhaustive).
- Build-script/proc-macro execution is a host supply-chain surface (thiserror-impl + syn +
  quote). The macro runs at build time; its output is trusted Rust source.
- Feature/edition drift (e.g. dropping `std`) would change the generated trait surface.

## 5. Provenance, license, maintenance, safety relevance

| Question | Finding |
|----------|---------|
| Source revision / patches | No patch or override for the crate in `MODULE.bazel`; source is the crates.io archive pinned by sha256. |
| License | **Not evidenced from checked-in source.** No in-repo dependency license allowlist or NOTICE entry for thiserror exists (`NOTICE` covers only the project's own Apache-2.0 declaration). The upstream license text/declaration must be read from the downloaded archive or registry metadata, which were not accessible in this run. Left **unknown/pending**. |
| Maintenance status / advisories | **Unknown.** Dated maintenance and advisory review requires registry/upstream access, which was blocked. Do not assert suitability from the version number alone. |
| Safety relevance | The crate is a target library and a host proc macro. No `unsafe` was observed in the COM-API usage; it is not in an unsafe/FFI path itself. Whether error messages are safety-relevant information is an unaccepted engineering decision. |
| Native requirement/design IDs | No TRLC requirement/design artifact was found that names the Rust error enums or their Display strings. Rust API is newer than the C++-oriented `score/mw/com/dependability/**` component requirements. Recorded as a traceability gap. |

## 6. Options (reviewable proposals — not accepted decisions)

| Option | Compatibility / build impact | Provenance / license / maintenance | Qualification / verification effort | Rationale and gaps |
|--------|------------------------------|-------------------------------------|--------------------------------------|--------------------|
| **Retain thiserror 2.0.21 (recommended draft)** | No API or lock change; derives already generate `Display`/`Error` for the public enums. Minimal risk. | Provenance = crates.io pinned archive; license/maintenance still to be confirmed against upstream. | Re-run the check plan against the baseline; document the pinned version/features/provenance/license once retrieved. No new code. | Source-backed default: the enums and their messages are public API, replacing derives changes maintained behavior for no demonstrated defect. |
| Replace with another crate | API-compatible derive would need a different macro crate; changes lockfile, transitive deps and possibly message/`source()` semantics → source-compatibility risk for downstream (`score_com`, runtime, examples). | Different provenance/license to re-evaluate (unknown, no comparison evidence). | Full downstream compilation + behavior checks. | No source-backed motivation found (no defect, no maintenance/advisory evidence). Not recommended on current evidence. |
| Implement `Display`/`Error` directly | Removes the proc-macro + build-script host surface, but ~7 enums / ~25 variants of messages must be hand-written and maintained; high chance of silent behavior drift. | In-repo code removes external license/provenance questions but shifts maintenance burden internally and does **not** remove qualification obligations. | Hand-written impls must reproduce exact messages; requires new tests asserting Display and downstream compatibility. | Only justified if a native maintenance/license/qualification policy requires it; no such sourced requirement found. |

The engineering decision (retain/replace/internal) remains **open** and requires an
authorized human; this run may only recommend.

## 7. Qualification obligations

- Per the dependency/macro guide, separate the roles: `thiserror` is a **library/component**
  role; `thiserror-impl` and `build.rs` are the **host generator/tool** role. Do not relabel
  the whole crate as a tool.
- Process work products at fabric pin `98d1d5f42dad412a09a888ea25e59c62fa6371ce`
  (`wp__tlm_plan`, `wp__tool_verification_report`) are **version 1 / status `valid`
  type definitions**, not completed instances. Whether they apply to the thiserror-impl
  host macro and the target library, and any confidence/security classification, are
  **human engineering decisions** that were not made here.
- Required artifacts to record once a decision is taken: pinned version/features/checksums
  (done here), license/notice text (pending), maintenance/advisory review (pending),
  build/test/lint/docs evidence over the affected targets (see `check-plan.json`), and any
  native tool/component work-product instances with their UID/version/status/confidence.
- No native work product is marked evaluated/qualified/released and no confidence decision
  is supplied.

## 8. Acceptance-criteria mapping

| Issue acceptance criterion | Disposition / evidence | Gap |
|----------------------------|------------------------|-----|
| Record pinned crate version, enabled features, error types using the derive | Done — §3 (thiserror 2.0.21, features `default,std`, sha256) and §4 (7 enums). | None for version; provenance checksums recorded; license pending. |
| Review generated behavior, provenance, license, maintenance status, safety relevance | Behavior (§4) and source/checksum provenance (§3) recorded. | License text, dated maintenance/advisories not retrievable this run. |
| Document whether to retain thiserror or implement the required error traits directly | Options compared in §6 with a source-backed draft recommendation to retain. | Decision is a pending offline human decision. |
| Record required qualification artifacts and API/maintenance impact | §5, §7 and `check-plan.json`. API surface is public and re-exported; replacement would be a source-compatibility change. | No native requirement IDs bind the enums; tool/component applicability unassigned. |

Requirements/Architecture impact: no requirement/design artifact referencing the Rust error
enums was found at baseline, so no requirement/design edit is proposed. The issue-template
checkbox alone is **not** treated as establishing that; the finding is "no matching artifact
found", not "confirmed unaffected".

## 9. Expected checks and gaps

`check-plan.json` lists the BUILD-derived native targets for query/build/test/docs/lint on
`linux_x64`, each with a reason and a sourced (or explicitly unknown) native obligation. No
shell commands are embedded there.

Known gaps / limitations:

- No trusted-collector evidence (`native-check-summary.json` absent); no check has actually
  been executed, so all results are "expected", not measured.
- Network/activity retrieval blocked: no fresh issue/PR state, no license or advisory data.
- `score_com_concept-macros-tests` (rust_doc_test) is tagged `manual` and has a documented
  rules_rust native-link limitation; `score_com.rs` examples are marked `ignore`, so rustdoc
  does not test them.
- No test asserting error `Display` strings was found (bounded search); Display-text stability
  is unproven.
- Host/target feature unification for the proc macro was not separately measured.
- QNX is intentionally out of scope for this run.

## 10. Offline decisions pending

1. **Retain vs replace vs hand-implement** thiserror (draft recommendation: retain on current
   evidence). Requires authorized human.
2. **License/provenance acceptance** of the thiserror 2.0.21 archive and its transitive
   `proc-macro2`/`quote`/`syn` set — pending registry/archive inspection.
3. **Tool/component applicability** of `wp__tlm_plan` / `wp__tool_verification_report` to the
   thiserror-impl host macro and target library, plus any classification/confidence.
4. Whether the public `Display` message strings are a contract requiring a native
   requirement ID and regression tests.
5. Fresh issue/PR state reconciliation (blocked this run).

## 11. Concrete next action

Execute `check-plan.json` through the bound Linux collector against baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e` (no source patch), record raw evidence and hashes
in `native-check-summary.json`, then obtain the offline human decision on §10 item 1. If the
decision is "retain", the follow-up artifact is a dependency/qualification record for
thiserror 2.0.21; no COM API source change is required.
