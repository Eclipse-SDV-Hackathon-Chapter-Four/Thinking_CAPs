# S-CORE Rust issue review packet — communication#490 mock runtime

Draft. Unknown fields are explicitly unknown. Technical completion is reported separately from
native engineering acceptance; this packet grants no authority to accept, publish or merge.

## Scope and binding

- Issue/repository: `eclipse-score/communication` #490 "Improvement: Mock Runtime implementation of
  Rust COM-API", state `open`, label `rust-api`, 0 comments. Local context read from
  `.rust-queue/context/issue.json`, `task.json`, `comments.json` (empty).
  Retrieval time of upstream state: **unknown** — network blocked, upstream re-fetch required.
- Source commit: baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`; working tree assumed equal
  (`.git` reads blocked, no hash reconciliation possible here).
- User authority / permitted writes: repository source **read-only**; only `.rust-queue/reports/`
  writable; shell, delegation, publishing, acceptance and web tools blocked. Artifact destination:
  `.rust-queue/reports/`. Budgets: no operational budget supplied; no paid calls attempted.
- Process/tailoring/requirements/design/safety/policy: `score-rust-workflow` SKILL v1.0.0 and its
  `issue-types.md`, `native-verification.md` references; native design
  `score/mw/com/rust/design/high_level_design_detail.md`; native test BUILD rules
  (`quality/unit_testing/unit_testing.bzl`); lint policy
  `quality/static_analysis/static_analysis.bazelrc`. Native requirement/design/safety IDs: **unknown**
  (not present in the fetched context).
- Source/lock/tool/environment bindings: `MODULE.bazel` declares Bazel `8.7.0`, `rules_rust`
  `0.68.2-score`, `score_crates` `0.0.11`, `rules_cc` `0.2.17`; default config `linux_x64_gcc_15`
  (Ferrocene `ferrocene_x86_64_unknown_linux_gnu`). Exact tool hashes: **not measured**.
- Final patch and digest: **none applied** (source read-only). Draft in `proposed-change.md`.
- Technical completion status: draft / proposed. Engineering acceptance status: **pending human decision**.

## Acceptance and engineering trace

The issue supplies no explicit acceptance criteria; obligations are derived from the native design and
verification guidance.

| Issue criterion (derived) | Native obligation/artifact | Changed artifact | Required check | Evidence/hash | Gap/disposition |
| --- | --- | --- | --- | --- | --- |
| Mock runtime implements the `Runtime` contract | `high_level_design_detail.md` §Mock runtime; `score_com_concept` traits | `com-api-runtime-mock/runtime.rs` (draft) | build `…:com-api-runtime-mock`; lint clippy_strict; test `…-tests` | none | unexecuted; command stage owns execution |
| Applications testable without a backend | verification table "Communication behavior" | `runtime.rs`, `score_com_mock` | build `//score/mw/com/rust:score_com_mock` | none | unexecuted |
| Runtime-independent semantics preserved | Rust library/API row | none (no edits) | build `//score/mw/com/rust:score_com`; test `score_com_concept-test` | none | unexecuted |
| Lola runtime unaffected | existing Lola test/doc targets | none | test `com-api-runtime-lola-tests`; docs `com-api-runtime-lola-doc-tests` | none | unexecuted |
| Testable entry point | design doc note | BUILD comment + design note (draft) | docs `…-doc-tests` (proposed) | none | text change pending review |
| Requirements/architecture impact | unchecked template box grants no authority | scope.md/review packet | — | — | **pending human decision** |

Baseline reconciliation: a mock-runtime skeleton already exists at the baseline (see `scope.md` §3); the
issue premise "not developed" is partially resolved, so the draft completes the skeleton instead of
reimplementing from scratch. Native statuses (`valid/released/accepted`) are untouched; the mock remains
test-only and LoLa remains the default. Requirements/design/interface/safety impact: **unassessed /
unknown** pending reviewer input.

## Dependency and macro assessment

Not applicable as a dependency-substitution task. The draft consumes existing resolved deps
(`score_com_concept`, `@score_communication_crate_index//:futures`) and the existing `CommData`/`Reloc`
derive macros. No crate added, removed, upgraded or pinned; no license/notice change; no Cargo
scaffolding introduced.

## Verification and expected checks

No checks were executed by this agent. `native-check-summary.json` was absent at authoring time; no raw
logs or exit codes exist. See `check-plan.json` for the full list.

| Check and native obligation/source | Command/config/tool/target/features (targets only; execution owned by command stage) | Subject hashes | Result/exit code | Raw evidence/hash | Limitation/disposition |
| --- | --- | --- | --- | --- | --- |
| Mock library build — Rust library/API row | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock`, config `linux_x64` | not measured | not run | none | pending |
| Mock re-export build — downstream compilation | `//score/mw/com/rust:score_com_mock`, config `linux_x64` | not measured | not run | none | pending |
| Default API regression build | `//score/mw/com/rust:score_com`, config `linux_x64` | not measured | not run | none | pending |
| Mock unit test — Communication behavior row | `…/com-api-runtime-mock:com-api-runtime-mock-tests` (PROPOSED, `@platforms//os:linux`) | not measured | not run | none | target absent at baseline; proposed |
| Concept unit test | `//score/mw/com/rust/score_com_concept:score_com_concept-test`, Linux-only | not measured | not run | none | pending |
| Lola unit test regression | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`, Linux-only | not measured | not run | none | pending |
| Mock rustdoc — Rust library/API docs | `…:com-api-runtime-mock-doc-tests` (PROPOSED, Linux-only) | not measured | not run | none | target absent at baseline; proposed |
| Abstraction-layer rustdoc | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | not measured | not run | none | tagged `manual`; must be enumerated explicitly |
| Clippy strict on mock | `…:com-api-runtime-mock` under `@score_rust_policies//clippy:linters.bzl%clippy_strict`, config `clippy`/`linux_x64` | not measured | not run | none | pending |

Generated-API compatibility was **not** measured on baseline or candidate. Excluded/unavailable checks:
upstream PR reconciliation, QNX variants (out of scope), sanitizer/Miri runs (not required by supplied
obligations), and any integration test needing a real backend.

## Offline decisions and portable evidence

- Proposed engineering decisions and required authorized reviewers/roles: (a) adopt the in-process bus
  model for the mock runtime; (b) define `cancellable_receive` semantics for a notification-free mock;
  (c) decide whether the mock enforces `max_num_samples`; (d) approve the design-doc/BUILD text updates.
  Required roles: Rust COM-API maintainers / requirements and architecture owners.
- Pending acceptance, safety/qualification gaps and missing platform checks: native Linux execution not
  run; requirements/design IDs unknown; upstream PR state unknown; no qualification claim for the
  toolchain or the mock.
- Patch/documents/logs location: this reports directory. Drafted artifacts:
  `.rust-queue/reports/scope.md`, `.rust-queue/reports/check-plan.json`,
  `.rust-queue/reports/proposed-change.md`, `.rust-queue/reports/review-packet.md`.
- Manifest: SHA-256 hashes **not computed** — no shell/hashing authority in this workspace. Sizes
  unknown. External raw-evidence paths: none produced.
- Source/tool/config identities sufficient to reproduce: repository commit above, Bazel `8.7.0`,
  `.bazelrc` config `linux_x64`, `MODULE.bazel` pins listed above, and the BUILD labels in
  `check-plan.json`.
- Concrete next action: re-fetch #490/PRs with network; apply `proposed-change.md` in a disposable copy;
  run the Linux checks in `check-plan.json`; publish `native-check-summary.json`; return for human review.
