## 📌 Description

Implements the OSS MVP in eclipse-score/score#2850: a deterministic, task-scoped assurance harness that evaluates CR-001–CR-005 with the native traceability gate and writes schema-checked, selectively queryable evidence. Adds 30 public search scenarios and 10 heldout scenarios, task specifications, a single-file baseline candidate, native coverage extraction, reusable argument checks, provenance, immutable run directories, and index-first queries.

The native Python 3.12/3.14 CI jobs evaluate both splits and upload their trace stores. Requirements, gate thresholds, metamodel and dependency pins are preserved. Documentation inputs remain inert data; no model calls are required.

Targets main at `102aad30bd373295d275722c3942b392a8eb7149`. The patch also applies cleanly to observed main `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16`; complete native verification is bound to the former revision, with no test evidence transferred to the newer tree. Draft PR #628 is a parallel `score_harness` proposal; namespace and loader reconciliation needs maintainer agreement before adoption.

Phase 2 security architecture in the issue comment is post-MVP. The public cohorts are executable test-derived seeds, with ten native snapshot-extraction cases; they are not historical production incidents or evidence of real-agent quality.

## 🚨 Impact Analysis

The impact analysis and acceptance mapping are included below. A hash-bound local verification packet retains the complete raw evidence. Existing linkage/statistics requirements are reused. Coverage of the new change-impact/evolution capabilities by existing qualified tool requirements has not been established. The current native TVR remains unchanged (`evaluated`, v8.1.2). Qualification applicability and the parallel draft design need a maintainer disposition.

- [ ] This change does not violate any tool requirements and is covered by existing tool requirements
- [ ] This change does not violate any design decisions
- [ ] Otherwise I have created a ticket for new tool qualification

These impact boxes remain open deliberately. A local qualification-review ticket draft is supplied; no ticket or accepted decision is claimed.

## ✅ Checklist

- [x] Added/updated documentation for new or changed features
- [x] Added/updated tests to cover the changes
- [x] Followed project coding standards and guidelines

Local validation: full native Bazel test/build matrix on Python 3.12 and 3.14, complete pre-commit hooks, exact CI evaluation commands on both splits, and documentation rendering. Each baseline matches all 40 specified verdict/impact outcomes. Expected gate failures are regression scenarios, not failing harness tests. Raw logs, native XML, source/patch hashes, traces, failed attempts and fixture corrections travel with the review packet.

Upstream CI on the submitted revision, Eclipse ECA, and code-owner approval remain pending. This PR is intentionally a draft: the contributor will decide when it is ready for review. No native qualification, release or acceptance is claimed.


<details>
<summary>Acceptance mapping and detailed impact analysis</summary>

# Issue acceptance and native obligation mapping

Scope: the issue-body OSS MVP of [S-CORE #2850](https://github.com/eclipse-score/score/issues/2850). The source is pinned to docs-as-code `102aad30bd373295d275722c3942b392a8eb7149`. Phase 2 is explicitly post-MVP in the issue comment.

| Published criterion | Native implementation / artifact | Verification |
| --- | --- | --- |
| CR-001 through CR-005 machine-readable | `assurance/rules.json`, `impact.py`, unchanged native gate | Per-rule scenarios, graph/rename/cycle checks; impact classes validated |
| At least 20 public search tasks | 30 search scenarios, 10 separately identified heldout scenarios; `corpus/index.json` and 40 `spec.md` files | All 40 expected verdicts and impact-ID lists match in each native Python baseline |
| End-to-end outer loop | `runner.py`: candidate validation → coverage → native gate → schema-checked traces → evolution index | Native `bazel run //assurance:evaluate` on both splits, Python 3.12 and 3.14 |
| Executable repository-native seeds | Threshold/broken-reference/type-scoped gate seeds; ten additional native snapshot-extraction cases | Source attribution to native gate tests and native metric functions; no production-incident claim |
| Evaluated baseline, grep-able traces | Single-file `candidates/baseline.py`; meta/score/diff/impact/gate artifacts, raw outputs | `evidence/runs/` and both `evidence/native-runs-py*` stores |
| Index-first history queries | `query.py`: ranking, failed tasks, indexed run comparison | Query unit/integration checks and retained CLI query receipts |
| CI without LLM | Existing native Bazel suite includes harness test; Python matrix evaluates both splits and uploads trace stores | Native full tests/builds on 3.12/3.14; actionlint; exact CI runner commands |
| Short top-level navigation | New `AGENTS.md`, linked domain guide, rule/task/block indexes | Source review; native format/copyright checks |
| Mandatory Lane A extraction/gate/schema/trace/smoke sequence | New coverage CLI calls existing native metric functions or validates prepared schema-v2 exports; gate unchanged | Native end-to-end checks, invalid-metric rejection, score/impact/gate schema validation |
| Candidate restrictions | Descriptor-relative no-follow reads, explicit input allowlist, special-file/size/UTF-8 checks, stable inert JSON; stdlib only | Read-only/network guard, traversal/symlink/FIFO/oversize/injection/unsafe-import tests |
| Reusable argument-and-check fragments | `blocks.json` + `blocks.py`: goal/requirements, solution/V&V, requirements breakdown | Lane A unit checks for missing support, failed evidence, and insufficient native coverage |

The seed expectations initially omitted reachable nodes in requirement/test evidence cycles. Original expectations and the unsuccessful runs are retained under `evidence/corpus-corrections/` and `evidence/history/`. Corrections follow graph reachability; native verdict expectations were not changed. Both splits are public test cohorts and provide no hidden-benchmark or real-agent quality claim.

Native applicability: `tool_req__docs_test_linkage_metrics@1` and `tool_req__docs_test_link_testcase@1` cover reused metric/link capabilities. New change-impact/evolution applicability requires the maintainer disposition described in `impact-analysis.md`; the existing evaluated TVR is not adoption of this patch.

# Impact analysis for S-CORE #2850

Target: `eclipse-score/docs-as-code` main at `102aad30bd373295d275722c3942b392a8eb7149`. This is a proposed OSS MVP, with no model dependency or automatic adoption/engineering acceptance.

The change adds an opt-in assurance scenario evaluator, public CR-001–CR-005 catalog, task-scoped baseline candidate, three reusable checks, trace validation and selective queries. CI exercises these through the native Bazel test suite. The native gate, thresholds, requirement metamodel, compiler/dependency pins and existing work-product statuses are preserved. Coverage extraction calls the existing native calculation functions.

`tool_req__docs_test_linkage_metrics@1` covers native linkage statistics and type filtering; its recorded `implemented` value is `YES`. `tool_req__docs_test_link_testcase@1` covers requirement/test links. The new change-impact catalog and harness evolution are specified by issue #2850; complete coverage by existing qualified tool requirements has not been established. `tool_req__docs_req_attr_testcov@1` has explicit `status: invalid`, and is not used as a valid obligation.

The authoritative native TVR, `doc_tool__score_docs_as_code@3`, records `status: evaluated`, tool version `v8.1.2`, and `security_affected: YES`. That record is not qualification or approval of this new harness. Native source: `docs/internals/requirements/tool_verification.rst`. The relevant tool-management guidance is `docs/how-to/perform_tool_verification.md`.

Potential malfunctions in the proposed use include incorrect change-impact classification, accepted inconsistent metrics, omitted tasks, fabricated or stale traces, and reading input outside the declared scope. Measures in this patch include independently specified expectations, old/new graph checks, native metric/gate execution, local schema validation, immutable per-run output, input/source hashes, explicit file allowlists, POSIX no-follow reads, special-file rejection, and retained raw results. Static candidate screening is not a sandbox; candidate Python remains reviewed program code.

Maintainer dispositions required before adoption: determine requirement/TVR applicability for the new capabilities; reconcile the parallel namespace and loader in draft PR #628; assess the bounded seed corpus and intended deployment scope. No tool-qualification ticket has been filed, no native acceptance is asserted, and no requirement/design IDs or statuses are fabricated. A ticket draft is included for the project to use if qualification is required.

Phase 2 in the issue comment explicitly proposes post-MVP injection sanitization, causal verification, capability tokens and adaptive rollback. This contribution does not claim those extensions.

</details>

<details>
<summary>Measured verification and qualification applicability proposal</summary>

# Measured verification

Bound source: docs-as-code `102aad30bd373295d275722c3942b392a8eb7149` plus the complete patch. Every final test/build receipt binds the exact 614-file exported source vector and confirms it stayed unchanged during the check. Native gate/schema/metamodel/metric-function and dependency/configuration pins are preserved.

| Configuration | Native tests | Native build | Actual CI runner baseline |
| --- | --- | --- | --- |
| Python 3.12 (3.12.12) | 494 passed, 1 explicitly skipped testcase; 26 targets, 0 failures | 99 targets | 30/30 search + 10/10 heldout |
| Python 3.14 (3.14.2) | 494 passed, 1 explicitly skipped testcase; 26 targets, 0 failures | 99 targets | 30/30 search + 10/10 heldout |

The complete pre-commit suite passed: JSON/YAML/hygiene, Bazel tidy/lock, actionlint, Ruff, BasedPyright and Eclipse copyright. A subsequent RST-only spacing correction passed document hooks and native documentation rendering with warnings treated as errors. The complete native matrix was then executed again. The [reuse map](evidence/reuse-map.json) limits earlier code/CI results to unchanged subjects; no stale whole-source result is presented as final.

Native `bazel run //assurance:evaluate` executed both corpus splits on both interpreter versions. Scores, input/source hashes, raw output bindings and role/environment provenance travel in [3.12 traces](evidence/native-runs-py312/) and [3.14 traces](evidence/native-runs-py314/). All 40 specified verdict/impact outcomes match. Twenty gate failures per complete cohort are expected regressions and are successfully detected; they are not failing harness tests. Metric, score, impact and gate artifact schemas are validated during execution.

Exact commands, Docker/tool identities, timestamps, complete stdout/stderr and native XML are under [checks](evidence/checks/). Earlier import/lint/runtime failures, omitted cycle-node expectations, and the RST warning remain visible. The [fixture corrections](evidence/corpus-corrections/corrections.json) explain graph-reachability expectations; native verdict expectations were not changed. These public cohorts establish neither hidden-benchmark performance nor real-agent/production-incident quality.

The final source/patch replay matches the exported tree at the bound baseline. The patch also applies cleanly to later observed main `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16`; full tests are not transferred to that different tree. The [check inventory](expected-checks.json) records applicability, omissions and pending project gates. Submitted-revision CI, native impact/qualification and draft API decisions, ECA and code-owner approval remain pending. No native qualification/release/acceptance is claimed.

# Proposed qualification applicability review: docs-as-code assurance harness

Assess whether the new #2850 scenario evaluator/change-impact capabilities require an extension of the existing Docs-as-Code TVR and tool requirements. Bind the review to the final source manifest and measured checks in this packet. The current native TVR is evaluated for v8.1.2; no new evaluated/qualified/released status is inferred.

Review intended use: evaluate prepared public change scenarios and expose deterministic traces in CI, without approving engineering changes. Examine potential incorrect impacts, metrics/schema errors, missing checks, stale evidence, and unauthorized reads. Decide required requirements, verification evidence, usage restrictions, safety/security measures and responsible reviewer. Reconcile draft PR #628 before selecting the implementation namespace and loader.

This is a local ticket draft. It has not been filed and does not satisfy the PR template checkbox asserting that a qualification ticket exists.

</details>

Evidence links under `evidence/` refer to the portable local review packet, not files in this PR. This PR includes the executable corpus, checks, documentation, and CI trace upload configuration; complete raw local logs are retained separately.
