# S-CORE Rust issue review packet — #1263

Assessment (no source patch). Fill gaps explicitly; unknown fields stay unknown.

## Scope and binding

- Issue/repository: eclipse-score/communication #1263; issue state at provided snapshot:
  open, 0 comments, 0 linked PRs; `updated_at` 2026-10-04T11:11:54Z. Live re-fetch
  unavailable (web/shell blocked) — carried snapshot only.
- Source commit: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
- User authority: disposable workspace; reports only under `.rust-queue/reports/`;
  shell, delegation, publishing and acceptance blocked. Linux only; QNX out of scope.
- Process/tailoring/requirement/design IDs: fabric process pin
  `98d1d5f42dad412a09a888ea25e59c62fa6371ce` (`wp__tlm_plan`,
  `wp__tool_verification_report` v1, status `valid` — type definitions, not instances);
  S-CORE Rust guideline `doc__rust_coding_guidelines` v1 `valid` (applicability unresolved).
  No in-tree Rust requirement/design IDs found → **unknown**, none invented.
- Source/lock/tool bindings: `MODULE.bazel` (rules_rust 0.68.2-score; score_crates 0.0.11;
  score_rust_policies 0.0.5; Ferrocene toolchain), `.bazelrc`, `MODULE.bazel.lock`
  (present; hashes not computed — shell blocked). Storage selection not exercised.
- Final patch / baseline-to-patched digest: **not applicable** (no patch authored).
  File-level digests unavailable to the agent (shell blocked); collector must hash.
- Technical completion: assessment complete for the discovered surface. Engineering
  acceptance: **pending** authorized human decision.

## Acceptance and engineering trace

| Issue criterion | Native obligation / artifact | Changed artifact | Required check | Evidence / hash | Gap or proposed disposition |
| --- | --- | --- | --- | --- | --- |
| Record pinned crate version, enabled features, direct COM API call sites | Dependency inventory (dependency-and-macros reference) | None (assessment) | Query: `//score/mw/com/rust/score_com_concept:score_com_concept` (+lola/mock) | Call sites recorded in scope.md §2; version/features **unknown** | Open until score_crates 0.0.11 index resolved; no version invented |
| Distinguish production vs mock/test-only use | Native build/coverage separation | None | Build concept/lola/mock; tests | scope.md §3 source lines | Production `Stream`+`AtomicWaker`; mock/test `stream::empty`+`block_on`; no executor imposed |
| Review provenance, license, maintenance, safety relevance | Component/library qualification artifacts (native process) | None | Query + archive/license inspection | **Not obtainable in-workspace** | Open; safety relevance is a human decision; `futures` not relabeled a tool |
| Document retain / reduce / replace and required qualification artifacts | Design/policy review; lock/pin change if any | scope.md §5 options | Build/test/docs/lint on any change | Options A/B/C recorded | Recommendation A (retain); B is a scoped follow-up; C rejected |

Baseline reconciliation: the issue premise matches the baseline source. Requirements /
Architecture checkbox "not affected" is consistent with a dependency assessment that
proposes no interface change; unaffected claim rationale = no public signature change in
Options A. No MISRA C++ policy transferred to Rust.

## Dependency and macro assessment

- Resolved crate version/features/roles: `futures` via
  `@score_communication_crate_index//:futures`; default features (no `crate_features`);
  production role = `stream::Stream` + `task::AtomicWaker` (+ `core::task` re-exports from
  `future`/`task`); mock/test role = `stream::empty` + `executor::block_on`; downstream role
  = `channel::oneshot`, `FutureExt`, `StreamExt`. **Exact version/checksums unknown.**
- Provenance/license/notice: **unknown** (index not vendored; no Cargo manifests). Must be
  taken from the resolved archive and NOTICE texts with retrieval date.
- Dated maintenance/advisory observations: **none recorded** — not inferred from the name.
- In-source invocation sites: enumerated in scope.md §2/§4 (concept.rs 57/931; lola
  consumer.rs 40-41/487/676-826/925/993/1016; mock runtime.rs 34/337-339/529; example
  consumer.rs 15-16; tests_using_tokio 41; basic_rust_api consumer_app.rs 31-32/182).
- Failure modes: `to_stream`/`ReceiveFuture` rely on `AtomicWaker` register-before-receive
  to avoid missed wake-ups; a wrong retain/reduce would compile while breaking wake/cancel
  behavior (not caught by type-checking alone) → covered by the runtime tests and tokio/SCT
  integration tests in the check plan. Residual unknown: whether these checks run on the
  collector (native-check-summary.json absent).

| Option | Compatibility / build impact | Provenance, license, maintenance | Qualification / verification effort | Proposed rationale and gaps |
| --- | --- | --- | --- | --- |
| Retain | None | Unknown until index resolved | inventory + checks re-run | Recommended; no lock/API change |
| Replace (crate) | New pins, lock update | Same upstream repo | full re-run + approval | No benefit identified over reduce |
| Internal | Reimplement `AtomicWaker`; `Stream` not in `core` | Removes dependency | High; new sync code | Not recommended |
| Reduce (`futures-core`+`futures-task`) | BUILD/lock change; same trait identity | New pins need evidence | BUILD/lock + approval + full re-run | Scoped follow-up (Option B) |

- Proposed recommendation: **retain** (`futures`) with **no code change in this
  assessment**; record Option B as a reviewable follow-up. Authority required: repository
  codeowner/authorized reviewer for any dependency/BUILD/lock change.
- Applicable work products: component/library requirement, architecture and verification
  artifacts for the Rust COM API — native instance IDs **unknown** (not discovered).
  Tool work products `wp__tlm_plan`/`wp__tool_verification_report` are definitions only; no
  tool instance asserted.

## Verification and expected checks

Structured obligations: `.rust-queue/reports/check-plan.json` (kinds build/test/docs/lint/
query, BUILD-derived labels, config `linux_x64`). No check has been executed by the agent;
raw evidence and exit codes are collector-owned.

| Check group | Native obligation/source | Target/config | Subject hashes | Result | Evidence | Limitation |
| --- | --- | --- | --- | --- | --- | --- |
| Build | Rust library/API; production vs mock separation | see check-plan build entries; linux_x64 | unavailable (shell blocked) | **not run** | pending collector | mock runtime marked test-oriented |
| Test | Rust unit + communication integration | score_com_concept-test, macros-unit-tests, lola-tests, tokio integration, test_com_api_async/sync; linux_x64 | unavailable | **not run** | pending collector | QNX excluded (#1278); tokio test sanitizer-incompatible |
| Docs | rustdoc/examples | com-api-runtime-lola-doc-tests; macros-tests (manual) | unavailable | **not run** | pending | `manual` target covers async docs partially |
| Lint | CI Rust clippy / `clippy_strict` | score_com_concept, lola, mock (+ re-export/example); linux_x64 | unavailable | **not run** | pending | policy applicability pending |
| Query | Dependency inventory | concept/lola/mock; linux_x64 | unavailable | **not run** | pending | exact version/features unknown until resolved |

Include executed, failed, unavailable, manual/excluded, applicable-unrun: currently all
applicable checks are **unrun**; `score_com_concept-macros-tests` is manual/excluded.
Generated-API compatibility measured on baseline and candidate: **not applicable** (no
candidate; assessment only). No fixtures offered as production evidence.

## Offline decisions and portable evidence

- Proposed decisions: (1) retain `futures`; (2) do not change pins/lock in this task;
  (3) consider Option B (`futures-core`+`futures-task`) as a separate, human-approved change.
  Required reviewers: repository codeowners / authorized dependency reviewer.
- Pending acceptance / gaps: crate version+features+license+advisory evidence; safety
  relevance and native work-product applicability; lint policy applicability; native check
  execution (`native-check-summary.json` absent); QNX excluded by scope.
- Packet location: `.rust-queue/reports/` — this `review-packet.md`, `scope.md`,
  `implementation.md`, `check-plan.json`. Raw evidence (if produced) lives with the collector.
- Manifest: size/SHA-256 must be computed by the deterministic collector; the agent cannot
  hash files (shell blocked). Contents are text and reproducible from the baseline commit.
- Reproducibility identities: baseline `381d43de…`; `MODULE.bazel`/`MODULE.bazel.lock`,
  `.bazelrc`, `quality/static_analysis/static_analysis.bazelrc`, and the BUILD files named
  in `check-plan.json`.
- Concrete next action: run the collector against `check-plan.json` on `linux_x64`; resolve
  the `score_crates` 0.0.11 crate index to record the exact `futures` version/features,
  license/notice and advisory status; then route the retain-vs-reduce proposal to an
  authorized reviewer. Evidence collection can proceed within known scope; with the
  dependency inventory unknown and no native results yet, no readiness/qualification claim
  is made.

Do not embed credentials. Passing checks and completed execution do not supply a human
decision. Review occurs outside the workflow.
