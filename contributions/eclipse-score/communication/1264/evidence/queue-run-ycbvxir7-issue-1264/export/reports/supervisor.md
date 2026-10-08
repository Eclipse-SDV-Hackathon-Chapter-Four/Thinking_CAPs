# Supervisor review — issue #1264 (`thiserror` usage in the Rust COM API)

Independent, read-only review of the scope, patch and measured evidence produced for
eclipse-score/communication#1264. This file is the **only** artifact written by this
review; no source, BUILD, lock, CI, lint-policy or other report was modified.

Status: **assessment / design package reviewed — NOT an implemented issue fix.**
Engineering acceptance remains **pending an authorized human**; this review grants none.

## Binding

| Item | Value |
|------|-------|
| Issue | eclipse-score/communication#1264 — "Improvement: `thiserror` crate usage in the Rust COM API" |
| Repository | eclipse-score/communication |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Task mode | `assessment` (`task.json`), `max_source_corrections = 3` |
| Platform / model scope | Linux x86-64 (`linux_x64`); DeepSeek Flash only; **no QNX** |
| Review authority | File tools only inside this disposable workspace; shell/delegation/publishing/acceptance blocked; source reads bounded to 200 lines; content search (grep) unavailable in this run |
| Latest measured evidence | `native-check-summary.json` — **attempt 3**, `passed: false`, `infrastructure_error: null`, subject hash `3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`, raw `jobs/1264/execution/check-3/native-result.json` sha256 `e2c1c25476a45766cfbcdc5f6b2e3b090c9e2a5fecc605e0879e356f29bafe97` |
| Report artifacts reviewed | `scope.md`, `dependency-assessment.md`, `implementation.md`, `check-plan.json`, `review-packet.md`, `correction-1/2/3.md`, `native-check-summary.json`, `native-result.json` |
| Issue/PR activity | Not retrievable (network blocked); `context/comments.json` = `[]`; no retrieval time recorded |

## 1. Deliverable disposition

The issue asks for four documentation/qualification outcomes (record pin/features/error
types; review generated behavior/provenance/license/maintenance/safety; document
retain-vs-implement-directly; record qualification artifacts and API/maintenance impact).
It is an **assessment**, and `task.json` sets `"mode": "assessment"`.

The produced package is a **design/assessment report, not a source fix**. `implementation.md`
correctly states no source patch exists and only `.rust-queue/reports/` artifacts changed.
This review confirms that framing: **#1264 is not implemented or closed**, and the reports do
not claim it is. The engineering decision (retain / replace / hand-implement `thiserror`)
remains open and may only be taken by an authorized human (codeowner of `score/mw/com/rust`,
plus the safety/qualification role as applicable). Passing builds/tests and pipeline success
supply **no** acceptance.

## 2. Scope verification (source-confirmed)

Independently re-read at the baseline; all material scope claims hold:

- `score/mw/com/rust/score_com_concept/error.rs` (128 lines, read in full): imports
  `thiserror::Error` (line 20) and derives `#[derive(Debug, ScoreDebug, Error)]` with
  `#[error("...")]` on **7 `pub` enums** — `ServiceFailedReason` (4), `ProducerFailedReason` (3),
  `ConsumerFailedReason` (3), `AllocationFailureReason` (3), `ReceiveFailedReason` (7),
  `EventFailedReason` (6), `Error` (6). Total **32 variants**. Confirmed.
- **No `#[from]` / `#[source]`** attributes exist in `error.rs`; generated `Error::source()`
  therefore returns `None` and there is no machine-readable error chain — only `Display`
  text embeds the inner reason. Confirmed by full read.
- `lib.rs` (line 24 `mod error;`, line 28 `pub use error::*;`) makes the enums public surface.
- `score/mw/com/rust/score_com.rs` lines 137–142 re-export `Error` and `Result`; `concept.rs`
  line 62 defines `type Result<T> = core::result::Result<T, Error>`. Confirmed.
- `score_com_concept/BUILD` line 31 declares `@score_communication_crate_index//:thiserror`
  (runtime `deps`); the proc-macro dep list is separate (`score-com-macros`, `pastey`).
  Confirmed.
- Only **one** `error.rs` exists under `score/mw/com/**` (glob), so the thiserror-using enums
  are confined to `score_com_concept`. Downstream crates (e.g. `com-api-runtime-lola`)
  consume them transitively via `//score/mw/com/rust/score_com_concept` and the `score_com`
  re-export. Confirmed.

Dependency pin (lock, `lockfile_mode=error` per `.bazelrc` line 15 — re-read and confirmed):

| Field | Value (source-anchored, re-verified) |
|-------|---------------------------------------|
| Crate index module | `score_crates` `0.0.11`, `repo_name = "score_communication_crate_index"` (`MODULE.bazel` line 41) |
| Library crate | `thiserror` **2.0.21** (`MODULE.bazel.lock` line 9908), sha256 `09e52cb86a36cede5cb101bf8908837b3e4c6e5e59fe7fd85c23fb56200d189e` |
| Features / edition | `default`, `std`; edition 2021 (lock line 9921) |
| Generator | `thiserror-impl` **2.0.21** proc macro (lock line 9924), sha256 `fe5197923287db20a58125f0bc85c062f7f2c892de97b18c356f9efb14b28524`; deps `proc-macro2` 1.0.107, `quote` 1.0.47, `syn` 3.0.6 (lock line 9936) |
| Build script | `cargo_build_script` `_bs` (`build.rs`) generated (lock line 9921) |
| Patches/overrides | None for this crate |
| Target compatibility | linux gnu (x86_64/aarch64), QNX 7.1.0 (x86_64/aarch64), x86_64-unknown-none |

`NOTICE` re-read: declares only the project's own Apache-2.0; **no third-party `thiserror`
license/notice** is checked in. The license/maintenance finding of "unknown" is accurate —
the crate archive is fetched externally and is not in the source tree, and network was blocked.

## 3. Patch verification

No product patch exists (assessment mode). The only changed paths are the agent-authored
report artifacts under `.rust-queue/reports/`. `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelrc`,
`quality/static_analysis/static_analysis.bazelrc`, CI workflows, `BUILD` files and all `score/`
sources are unmodified. Because there is no candidate patch, **baseline↔candidate generated-API
compatibility could not and was not measured** — correctly recorded, not claimed.

Consequently the issue's third acceptance criterion ("document whether to retain or implement
directly") is answered by **options + a draft recommendation only**; it does not itself
implement or remove `thiserror`.

## 4. Measured evidence review

Command stages and raw evidence are outside agent authority. This review checks the supplied
bounded summary for internal consistency and hash binding.

Sequence of determinations (subject hash identical across all measured attempts,
`3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`):

| Attempt | Stage | Result | Evidence of record |
|---------|-------|--------|--------------------|
| — | check0 | collector `AssertionError` (check-plan schema: external `@...//:thiserror` label in `targets[]`) | `correction-1.md` |
| 1 | check1 | `passed: false`; 7/8 checks exit 0; `lint` exit 1 | `correction-2.md`, raw `check-1/native-result.json` sha256 `3af57aac77cf53a810c89c5b37d8fd23731022ab8b275c267994e54f057cb26c` |
| 2 | check2 | identical to attempt 1 | `correction-3.md`, raw `check-2/native-result.json` sha256 `d08e07d5f9c76b431848b59975448cd7a62d8732bf46f67a9739579679e28c1b` |
| 3 | check3 | identical to attempts 1–2 | `native-check-summary.json` (binding), raw `check-3/native-result.json` sha256 `e2c1c25476a45766cfbcdc5f6b2e3b090c9e2a5fecc605e0879e356f29bafe97` |

Re-verified from the binding summary (attempt 3): 8 checks — query×2 exit 0, build (crate +
`score_com`) exit 0, build (runtime / generated interface / example lib) exit 0, test (unit)
exit 0 (`3/3 pass`), test (integration/example) exit 0 (`3/3 pass`), docs exit 0, **lint exit 1**.
Overall `passed: false`, `infrastructure_error: null`. Attempt 1's raw tail shows the pinned
edge genuinely compiling (`Compiling Rust proc-macro thiserror_impl v2.0.21`,
`Compiling Rust rlib thiserror v2.0.21`); attempts 2–3 were served from cache (unchanged
subject), which is consistent, not contradictory.

**Lint failure diagnosis — independently corroborated.** The failure is a Bazel *analysis-phase*
option error (`aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than
once`; `configs ... expanded more than once: [_lint]`), before any clippy action runs, so no
source-facing diagnostic was produced. `.github/workflows/_linter.yml` (lines 79–125, re-read)
shows the native route is `aspect lint --bazel-flag=--config=ci --bazel-flag=--config=clippy …`
and its inline comment explicitly states the aspect is deliberately **not** passed via
`--aspect=` because "Bazel rejects the same aspect being registered twice." This supports the
corrections' conclusion that the collector's lint invocation double-registered the pinned
aspect (an invocation/backend prerequisite), **not** a source, test, BUILD, lock, CI or
lint-policy defect. The disposition is therefore source-backed.

## 5. Findings

| # | Severity | Finding |
|---|----------|---------|
| F1 | High (integrity) | **Packet is stale w.r.t. the binding evidence.** `native-check-summary.json` is now **attempt 3** (`check-3`), but `review-packet.md` labels the summary "attempt 2" and its measured-outcomes table says "attempt 1 and attempt 2 identical", and `correction-3.md` states the evidence of record is attempt 2. The outcome and subject hash are unchanged, so the conclusion stands, but "a stale report is not fresh evidence": the packet must be re-pointed to attempt 3 (`check-3`) before offline review. Recorded, not rewritten (edit scope = this file only). |
| F2 | Medium (correctness) | `scope.md` §4 says "**Six** variants carry named fields"; the actual count is **4** (`ReceiveFailedReason::{SampleCountOutOfBounds, InputValueOutOfBounds, BufferOverflow}` + `EventFailedReason::MaxSampleOutOfBounds`). `dependency-assessment.md` §4 states "Four …" correctly. The two reports disagree; the correct value is 4. |
| F3 | Medium (evidence strength) | The two `query` checks are the same in-repo target and both emit only `rust_library rule //score/mw/com/rust/score_com_concept:score_com_concept`. Neither native query output independently evidences the **pinned version/features**; that fact comes from the agent's source read of `MODULE.bazel.lock`. The acceptance criterion "record pinned version/features" therefore rests on source evidence, with the native query merely confirming the owning target resolves. This is a limitation of the collector schema (external `@...//:thiserror` labels are rejected), which is why the second query degenerates to the first. Correctly flagged as a non-blocking plan-quality observation in the corrections; retained here. |
| F4 | Low (doc hygiene) | `implementation.md` retains an early bullet "`.rust-queue/reports/native-check-summary.json` is **absent**; no check … executed" while later update bullets state it was measured (attempts 1–2). Self-clarifying via the update notes but internally contradictory on first read; the newest binding summary is attempt 3. |
| F5 | Low (freshness) | `correction-3.md`, `implementation.md` and `review-packet.md` do not reference attempt 3 / `check-3`. Same root cause as F1. |
| F6 | Info | `check-plan.json` conforms to the required schema `{"checks":[{"kind","targets","reason","native_obligation","config"}]}`: 8 entries, kinds `query|query|build|build|test|test|docs|lint`, every `targets[]` value a `//package:target` label with no `\n\r;\`$`, `config = "linux_x64"`. All labels verified against BUILD files (`score_com_concept`, `score_com`, `com-api-runtime-lola{,-tests,-doc-tests}`, `bigdata_com_api_gen_rs`, `com-api-example-lib`, `com-api-example-tokio-integration-test`, `test_com_api_sync`, `test_com_api_async`). The check0 schema defect is genuinely resolved. |
| F7 | Info | No source/API/lock/lint-policy weakening was performed to make a check pass. Checks were neither removed, merged nor downgraded; the blocked `lint` check remains in the plan (no passing lint evidence claimed). Consistent with the SKILL's "do not suppress lints" rule. |

## 6. Gap assessment (correctness / FFI / concurrency / trace / qualification)

- **Correctness:** Generated behavior is described from source and is accurate (all variants
  have `#[error]` `Display`; no `source()` chain; named-field interpolation in 4 variants).
  Failure modes (silent `Display` drift, trait-surface changes, host proc-macro/build-script
  supply chain) are identified. **No test asserts any `Display` string** — a real behavior-drift
  coverage gap, correctly recorded as unresolved (bounded discovery; this review could not run a
  repo-wide content search because the grep tool is unavailable).
- **FFI/unsafe:** Not applicable as a defect surface — `thiserror` is a target library plus a
  host proc macro, and the COM-API usage (`error.rs`) contains no `unsafe`. The reports do not
  over-claim safety relevance; whether `Display` text is safety-relevant is left as an unaccepted
  human judgement.
- **Concurrency:** No concurrency surface is introduced by the derive usage; correctly not raised.
- **Trace:** **Open gap** — no native requirement/design artifact names the Rust error enums or
  their `Display` strings; the issue-template "Requirements/Architecture not affected" checkbox
  is correctly *not* treated as evidence. Finding is "no matching artifact found", not "confirmed
  unaffected".
- **Qualification:** **Open gap** — fabric pin `98d1d5f42dad412a09a888ea25e59c62fa6371ce`
  work products `wp__tlm_plan` / `wp__tool_verification_report` are v1/status `valid` type
  definitions; their applicability to the `thiserror-impl` host macro and/or the target library,
  and any confidence/security classification, are unassigned human decisions. No native work
  product is marked evaluated/qualified/released. The library/component vs host generator/tool
  role split is correctly preserved.

## 7. Preserved failed / missing evidence and pending acceptance

- **Failed evidence preserved, not reset:** check0 traceback (`correction-1.md`); attempt 1
  (`correction-2.md`); attempt 2 (`correction-3.md`); attempt 3 (`native-check-summary.json`).
  No counter reset, no failing check deleted, no passing lint evidence fabricated.
- **Missing evidence preserved:** upstream `thiserror` license/notice text and dated
  maintenance/advisory data (network blocked; not in-repo); host/target feature unification for
  `thiserror-impl` not separately measured; S-CORE `syn 3.0.6` not cross-checked upstream; no
  fresh issue/PR state; packet file digests/sizes not computed (hashing outside authority).
- **Unresolved obligations:** pinned-lint obligation is **measured-blocked** (F1/lint), so the
  "preserve lint/CI policy" obligation is not yet demonstrated by a passing lint run.
- **Pending offline acceptance (unchanged, must not be treated as granted):** (1) retain vs
  replace vs hand-implement `thiserror`; (2) license/provenance acceptance of the `thiserror`
  2.0.21 archive and `thiserror-impl`/`proc-macro2`/`quote`/`syn` set; (3) tool/component
  applicability of `wp__tlm_plan` / `wp__tool_verification_report`; (4) whether public `Display`
  strings are a contract requiring a native requirement ID and regression tests; and (5) fresh
  issue/PR reconciliation.

## 8. Disposition

- The assessment package is **technically coherent, source-bound and internally consistent on
  its central claims**; its draft recommendation (retain `thiserror` 2.0.21 on current evidence)
  is source-backed, and the no-source-patch decision is appropriate to `mode = assessment`.
- It is **not** an implemented issue fix and **cannot close #1264**. The engineering decision and
  all qualification items remain pending authorized humans.
- Measured native evidence is **partial by design and by blocker**: 7/8 checks exit 0 on an
  unchanged subject across attempts 1–3; the `lint` obligation is blocked at the collector's
  invocation layer and is **not** satisfied by any measured result.
- F1/F2/F3 are report-quality issues that do not change the technical conclusion but do affect
  the packet's freshness and evidence strength; they should be resolved before hand-off.

**Recommendation:** accept the assessment as an intermediate, source-bound decision package;
do **not** record it as an implemented/fixed issue; carry it to offline human review after the
packet is refreshed to attempt 3 and the F2 count is corrected. The `thiserror` retain/replace
decision and the license/qualification items remain with authorized humans.

## 9. Concrete next action

1. **Collector/operator:** fix the lint invocation so the pinned
   `@score_rust_policies//clippy:linters.bzl%clippy_strict` aspect and `_lint` config are applied
   exactly once (native route: `aspect lint --bazel-flag=--config=ci --bazel-flag=--config=clippy
   -- //...`), then re-run the deterministic `check` stage on the unchanged `check-plan.json`
   against baseline `381d43d…`. Do not remove or weaken the lint check if it remains blocked.
2. **Report refresh (next authorized writer):** update `review-packet.md` (and resume notes) to
   cite **attempt 3 / `check-3`** and hash `e2c1c254…`, correct `scope.md` §4 "Six" → "Four"
   named-field variants, and make `implementation.md`'s verification section internally
   consistent.
3. **Offline human review:** decide retain/replace/hand-implement, accept/reject the
   license/provenance evidence, assign tool/component applicability and confidence, and decide
   whether `Display` strings require a requirement ID plus regression tests.
