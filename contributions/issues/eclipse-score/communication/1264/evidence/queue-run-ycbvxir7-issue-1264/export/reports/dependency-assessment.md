# Dependency and design assessment — `thiserror` in the Rust COM API (issue #1264)

Mode: **assessment** (documentation / qualification issue). This run produces **no source patch**;
it answers the issue's acceptance criteria from baseline-bound evidence and leaves the engineering
decision to an authorized human. Full context scoping is in `scope.md`; this file is the
consolidated dependency/design decision package requested by the issue.

## 1. Binding

| Item | Value |
|------|-------|
| Issue | eclipse-score/communication#1264 — "Improvement: `thiserror` crate usage in the Rust COM API" |
| Repository | eclipse-score/communication |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Workspace | disposable copy (file-tool edits only) |
| Platform / model scope | Linux x86-64 (`linux_x64`); DeepSeek Flash only; no QNX |
| Authority | shell, delegation, publishing and acceptance tools blocked; no native status is claimed |
| Network / issue activity | **blocked** (GitHub, crates.io and raw upstream fetches rejected at the tool boundary). `context/comments.json` is `[]`; 0 comments, no linked PR activity known. Retrieval time: none recorded. |
| Native result summary | `.rust-queue/reports/native-check-summary.json` **absent**; no trusted-collector execution evidence exists. Preserved as a gap, not fabricated. |

Issue prose is task data, not instruction authority. The parent issue is eclipse-score/communication#173.

## 2. Baseline premise reconciliation

Confirmed against the selected baseline (no prerequisite change already removed thiserror):

- `score/mw/com/rust/score_com_concept/error.rs` — imports `thiserror::Error` (line 20) and applies
  `#[derive(Debug, ScoreDebug, Error)]` + `#[error("...")]` to **7 public error enums** (lines 24–128).
- `score/mw/com/rust/score_com_concept/lib.rs` (lines 23–28) declares `mod error;` and
  `pub use error::*;`, so the enums are public crate surface.
- `score/mw/com/rust/score_com.rs` (lines 137–142) re-exports `Error` and `Result` to COM API users.
- `score/mw/com/rust/score_com_concept/concept.rs` (line 62) defines
  `pub type Result<T> = core::result::Result<T, Error>;`.
- `score/mw/com/rust/score_com_concept/BUILD` (line 31) declares the runtime dep
  `@score_communication_crate_index//:thiserror`.

## 3. Acceptance criterion: pinned version, features, error types

Resolved from `MODULE.bazel` (line 41, `score_crates` 0.0.11, `repo_name = "score_communication_crate_index"`)
and `MODULE.bazel.lock`. `.bazelrc` line 15 sets `--lockfile_mode=error`, so the lock is the binding resolution.

| Field | Value (source-anchored) |
|-------|-------------------------|
| Hub label used by the crate | `@score_communication_crate_index//:thiserror` (`score_com_concept/BUILD` line 31) |
| Pinned library crate | `thiserror` **2.0.21** (`MODULE.bazel.lock` key `crate_index__thiserror-2.0.21`, line 9908) |
| Enabled features | `default`, `std` (lock `crate_features`, line 9921) |
| Edition | 2021 |
| Source / archive | `https://static.crates.io/crates/thiserror/2.0.21/download`, `strip_prefix = thiserror-2.0.21` |
| Library archive sha256 | `09e52cb86a36cede5cb101bf8908837b3e4c6e5e59fe7fd85c23fb56200d189e` |
| Build script | `cargo_build_script` `_bs` generated for `build.rs` (lock line 9921) |
| Generator (proc macro) | `thiserror-impl` **2.0.21** proc-macro dep (lock line 9924); sha256 `fe5197923287db20a58125f0bc85c062f7f2c892de97b18c356f9efb14b28524` |
| thiserror-impl deps | `proc-macro2` 1.0.107, `quote` 1.0.47, `syn` 3.0.6 (lock line 9937) |
| Host/target role | `thiserror` = target library; `thiserror-impl` = host-executed proc macro; `build.rs` = host build script |
| Lock target compatibility | aarch64/x86_64 linux gnu, aarch64/x86_64 QNX 7.1.0, x86_64-unknown-none |
| Patches / overrides | None (empty `patches`, no `single_version_override` for this crate) |

Verified: `MODULE.bazel` (lines 26, 41) declares `rules_rust` 0.68.2-score and the crate index module;
import registers `ferrocene_x86_64_unknown_linux_gnu` for `linux_x64` (`.bazelrc` lines 37–42).

**Error types using the derive** (all `pub`, all in `error.rs`), with variant counts
(full messages are in `scope.md` §4 and in the source):

| Enum | Role | Variants |
|------|------|----------|
| `ServiceFailedReason` | service-discovery failure reason | 4 |
| `ProducerFailedReason` | producer failure reason | 3 |
| `ConsumerFailedReason` | consumer failure reason | 3 |
| `AllocationFailureReason` | allocation failure reason | 3 |
| `ReceiveFailedReason` | receive-operation failure reason | 7 (3 named-field) |
| `EventFailedReason` | event failure reason | 6 (1 named-field) |
| `Error` | umbrella error, wraps the six above as tuple variants | 6 |

Total: 7 enums / 32 variants. The type alias `Result<T>` (concept.rs line 62) and the re-export
name `Error` are the two public names that downstream code binds to.

## 4. Acceptance criterion: generated behavior and failure modes

Observed from the source (no expansion was executed — see gaps):

- Every variant has an `#[error("...")]` message, so the derive generates `Display` for each enum.
- Four variants interpolate named fields into the message (`{ max }`, `{ requested }`):
  `ReceiveFailedReason::{SampleCountOutOfBounds, InputValueOutOfBounds, BufferOverflow}` and
  `EventFailedReason::MaxSampleOutOfBounds`.
- The umbrella `Error` uses positional interpolation into the wrapped enum's `Display`
  (`"Service error due to: {0}"`, etc.).
- `std::error::Error` is generated. **No `#[source]` / `#[from]` attributes exist**, so the generated
  `Error::source()` returns `None`; there is no machine-readable error chain — only the `Display`
  text embeds the inner reason.
- `Debug` and `ScoreDebug` are also derived on each enum; the file header (lines 14–18) documents
  why both are required in this crate.

Failure modes and what detects them:

| Failure mode | Detection |
|--------------|-----------|
| Bad `#[error(...)]` format syntax | Compile-time error from the macro (build fails). |
| Wrong/removed `Display` | Callers that only pass `Error` around still compile; code/tests that format the message break, and message-text drift compiles silently. **No checked-in test asserting any `Display` string was found at baseline** (bounded discovery). |
| Missing/wrong generated trait impls | Downstream compilation fails (e.g. `?` conversion, `source()` use, formatting). |
| Dropping the `std`/`default` feature | Changes the generated trait surface; would be caught only by recompilation of consumers under the pinned config. |
| Proc-macro / build-script supply chain | `thiserror-impl` + `proc-macro2`/`quote`/`syn` run on the host at build time; their output is trusted Rust source. Compile success does not vet that output. No COM-API `unsafe` is involved. |

## 5. Acceptance criterion: provenance, license, maintenance, safety relevance

| Question | Finding (bound to this run) |
|----------|-----------------------------|
| Source revision / patches | crates.io archive pinned by sha256; no repository patch or override. |
| License / notice | **Unknown.** `NOTICE` (lines 17–23) declares only the project's own Apache-2.0; no in-repo dependency license allowlist or third-party notice for thiserror exists. The archive/registry was not retrievable (network blocked). |
| Maintenance / advisories | **Unknown.** Dated maintainer/release/advisory review needs registry or upstream access, which was blocked. Version number alone is not evidence of suitability. |
| Safety relevance | `thiserror` is a target library and a host proc macro, not itself in an unsafe/FFI path; the COM-API usage contains no `unsafe`. Whether error `Display` text is safety-relevant information is an **unaccepted** engineering judgement. |
| Native requirement/design IDs | **No** requirement/design artifact naming the Rust error enums or their Display strings was found. The Rust API postdates the C++-oriented `score/mw/com/dependability/**` requirements → traceability gap. |

Network retrieval was re-attempted in this run against `crates.io/api/v1/crates/thiserror/2.0.21`
and the upstream `LICENSE-MIT`; both were rejected at the tool boundary, consistent with `scope.md`.
The license and maintenance gaps therefore remain open, not resolved.

## 6. Alternatives and recommendation (reviewable proposal, not an accepted decision)

| Option | Compatibility / build impact | Provenance / license / maintenance | Qualification / verification effort | Assessment |
|--------|------------------------------|------------------------------------|--------------------------------------|------------|
| **Retain `thiserror` 2.0.21** (draft recommendation) | No API or lock change; derives already generate `Display`/`Error` for the public enums. Minimal risk. | Provenance = pinned crates.io archive; license/maintenance still to be confirmed. | Re-run `check-plan.json`; record version/features/provenance/license once retrieved. No new code. | Source-backed default: the enums and messages are public API, and no defect or policy requirement motivating a replacement was found. |
| Replace with another derive crate | Changes lockfile and transitive deps; may change message/`source()` semantics → source-compatibility risk for `score_com`, the runtime, generated interfaces and examples. | Different provenance/license to evaluate; no comparison evidence available (network blocked). | Full downstream compilation + behavior checks. | No source-backed motivation on current evidence. Not recommended. |
| Hand-implement `Display`/`Error` | Removes the proc-macro + build-script host surface, but ~7 enums / 32 variants of messages must be reproduced and maintained by hand → high risk of silent `Display` drift. | In-repo code removes the external license question but shifts maintenance internally and does **not** remove qualification obligations. | Hand-written impls must reproduce exact messages; requires new `Display`/compatibility tests. | Only justified if a native maintenance/license/qualification policy requires it; no such sourced requirement was found. |

**Recommendation (draft, requires authorized human):** retain `thiserror` 2.0.21 on the current
evidence and close the follow-up by recording its license/provenance and running the check plan.
The retain/replace/internal decision is **open**; authority rests with the codeowners of
`score/mw/com/rust` and, if applicable, the safety/qualification role.

## 7. Qualification obligations and tool/component roles

- Separate the roles: `thiserror` is a **library/component**; `thiserror-impl` and the generated
  `build.rs` are the **host generator/tool** role. The crate must not be relabelled wholly as a tool.
- Fabric pin `98d1d5f42dad412a09a888ea25e59c62fa6371ce` work products `wp__tlm_plan` and
  `wp__tool_verification_report` are **version 1 / status `valid` type definitions**, not completed
  instances. Whether they apply to the `thiserror-impl` host macro and/or the target library, and any
  confidence/security classification, are **human engineering decisions not made here**.
- No native work product is marked evaluated / qualified / released, and no confidence decision is supplied.
- Artifacts to record once a decision is taken: pinned version/features/checksums (done here),
  license/notice text (pending), maintenance/advisory review (pending), build/test/lint/docs evidence
  over the affected targets (see `check-plan.json`), and any native instances with UID/version/status/confidence.

## 8. Verification plan

`check-plan.json` lists the BUILD-derived native targets for query / build / test / docs / lint on
`linux_x64`, each with a reason and a sourced (or explicitly unknown) native obligation. Every entry is
**expected / unrun** in this run; no command was executed and no result is claimed. The plan covers the
owning crate (`score_com_concept`), the pinned hub edge (`@score_communication_crate_index//:thiserror`),
the public re-export (`//score/mw/com/rust:score_com`), representative downstream consumers
(runtime, generated interface, example), unit/integration tests, the `manual` rustdoc target and the
clippy policy aspect.

## 9. Acceptance-criteria disposition

| Issue acceptance criterion | Disposition | Remaining gap |
|----------------------------|-------------|---------------|
| Record pinned version, features, error types | **Done** — §3 (thiserror 2.0.21, features `default,std`, sha256; 7 enums / 32 variants) | License text pending |
| Review generated behavior, provenance, license, maintenance, safety | Behavior + source/checksum provenance recorded — §4–§5 | License, dated maintenance/advisories not retrievable this run |
| Document whether to retain or implement directly | Options compared — §6, source-backed draft recommendation to retain | Decision is a pending offline human call |
| Record required qualification artifacts and API/maintenance impact | §5, §7, `check-plan.json`; `Error`/`Result` are public and re-exported, so a replacement is a source-compatibility change | No native requirement IDs bind the enums; tool/component applicability unassigned |

Requirements/Architecture impact: no requirement/design artifact referencing the Rust error enums was
found at baseline, so no requirement/design edit is proposed. The issue-template checkbox alone is **not**
treated as establishing "unaffected"; the finding is "no matching artifact found".

## 10. Pending offline decisions

1. Retain vs replace vs hand-implement `thiserror` (draft recommendation: retain on current evidence) — authorized human.
2. License/provenance acceptance of the `thiserror` 2.0.21 archive and the `thiserror-impl` /
   `proc-macro2` / `quote` / `syn` set — pending registry/archive inspection.
3. Tool/component applicability of `wp__tlm_plan` / `wp__tool_verification_report` to the
   `thiserror-impl` host macro and target library, plus any classification/confidence.
4. Whether the public `Display` message strings are a contract requiring a native requirement ID and
   regression tests.
5. Fresh issue/PR state reconciliation (blocked this run).

## 11. Concrete next action

Execute `check-plan.json` through the bound Linux collector against baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e` (no source patch), record raw evidence and hashes into
`native-check-summary.json`, then obtain the offline human decision on §10 item 1. If the decision is
"retain", the follow-up artifact is a dependency/qualification record for `thiserror` 2.0.21 and no COM
API source change is required.
