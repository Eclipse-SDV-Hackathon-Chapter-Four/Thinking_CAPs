# Native engineering review packet

Latest license follow-up: [audit and raw evidence](../integration-20261007/license-audit/README.md). The current patch contains 191 files: the 185 runtime-measured implementation files are unchanged, and six inherited native files received license comments. The pinned checker passes all 164 supported native files and 15 packet scripts. The 274-case runtime evidence below predates that comment-only follow-up; no runtime tests were rerun. Original headerless collector bytes, previous patch/bindings and all failed checks are retained.

## Scope and binding

Issue: [eclipse-score/score#2850](https://github.com/eclipse-score/score/issues/2850).
Native destination: eclipse-score/docs-as-code. Baseline: draft
[PR #628](https://github.com/eclipse-score/docs-as-code/pull/628), commit
`4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9`. Current issue/comments and PR snapshots,
retrieval times and native guidance are retained under `evidence/upstream/`.
The implementation requires that draft's API; main has not incorporated it.

User authorized the scoped adapter, then explicitly selected completing all #2850
criteria. Work occurred in a storage-guarded disposable checkout; reference repos
and unrelated user changes were preserved. No paid/model calls, publishing, merge
or release were performed. Final patch, every changed file, unchanged contracts,
source archive, locks and policies are hash-bound in `evidence/source/binding.json`.

## Acceptance and native trace

| Issue criterion / obligation | Native changed artifact | Measured check / evidence | Disposition |
| --- | --- | --- | --- |
| AssuranceHarness interface and mandatory context restrictions | `harness/pinned_context_harness.py`; native base, loader and validator | 32 native boundary/interface/determinism tests; real CLI validation; actual built-export preservation | Implemented; arbitrary Python candidate loading remains trusted code |
| Machine-readable CR-001–005 | prepared `consistency_rules.json`, existing native YAML | exact YAML/JSON equivalence; requested rule selection; rule-derived scenarios | Implemented; catalog IDs preserved |
| Executable change impacts and classes | `consistency.py` | exact impacted IDs/rules/classes for all 40 scenarios; cycles, fan-out, content/type/status/link/test/threshold changes | Implemented; impacts require human review |
| Goal, solution and breakdown blocks | goal/solution/breakdown checks in `consistency.py` | supporting requirement change, invalid V&V evidence and child-coverage scenarios | Implemented; no assurance approval inferred |
| At least 20 public search scenarios | `corpus/search/`, 30 scenarios | static spec.md + JSON oracles + immutable before/after snapshots | Implemented; public synthetic data, not field-defect claims |
| Held-out split, 10–15 recommended | `corpus/heldout/`, 10 combined scenarios | disjoint IDs/snapshots; separately selected and recorded CLI runs | Implemented; public reproducibility split, not concealed model evaluation |
| Native gate-test seeds | original `spec/task_002–004`, fixture JSONs | baseline and candidate 3/3 original seeds; native gate tests | Preserved and executable |
| Build-backed seed | original active `task_005`; updated native `outer_loop.py` | actual native Sphinx build; both candidates 4/4 active native tasks, inactive example excluded explicitly | Implemented; schema-valid extraction avoids raw exporter metadata incompatibility |
| Lane A metrics and fixed gate | `coverage.py`, `evaluate.py`, native seed runner | unchanged native metric calculation; fixed gate/schema validation, including actual built needs | Implemented; original raw generated metrics retained and schema rejection recorded |
| Lightweight validation before evaluation | native `validate_candidate.py` | actual CLI with pinned Ruff/BasedPyright, missing-tool fail-closed regressions | Implemented; interface unit tests separate external tool invocation from Bazel runfiles |
| Harness → gate → deterministic distillation → index | `evaluate.py`, updated native seed runner | 30/30 search and 10/10 held-out per candidate; JSON score schema | Implemented, model-free snapshot replay |
| Complete traces and provenance | meta/run score, task gate/impacts/score/diff, contexts, metrics and separate logs | trace-schema validation, environment/tool/input hashes, roles and coverage delta | Implemented; native fixture replay records an empty diff and explicit executor mode |
| Evaluated grep-able baseline | native BaselineHarness | complete baseline trace stores and summaries | Implemented; no retrieval-effectiveness claim from fixture scores |
| Index-first queries | native `query_runs.py` | summary/top/failed-task/candidate-diff CLI | Implemented; no replay required |
| Lane A CI without LLM | existing required native test workflow | actionlint; local execution of workflow build/validation/evaluation commands | Implemented; hosted run/branch protection pending |
| Short indexed guidance | native existing AGENTS map, subsystem README, concept RST, corpus index | native documentation check | Implemented; top-level AGENTS stays short |
| Native contribution and qualification obligations | native PR template, impact analysis, improvement request and merge checklist | source-bound requirements IDs, retained guide/CODEOWNERS, coding/test/doc evidence | Human applicability/acceptance pending |

## Requirements, design, safety and dependencies

See `impact-analysis.md` for exact native requirement IDs and current dispositions.
No new requirement IDs or accepted statuses were assigned. Native gate, metrics schema,
metric calculation, MODULE/requirements locks and lint policy are unchanged byte-for-byte.
Existing candidates/loader/validator/query were annotated where needed for native checks.
No new runtime dependency was introduced. The candidate uses stdlib/repo-local modules;
verification uses the native locked jsonschema-rs and native pinned tooling.

Native concept RST documents scope, file limits, graph/block semantics, executor modes,
provenance and interpretation. Linux/Python 3.12 were measured. Tool qualification,
ISO 26262/ASPICE argument validity and platform deployment acceptance are not inferred
from tests. Native tool-instance/qualification applicability remains unknown pending
maintainer assignment. Phase 2 security controls are explicitly post-MVP upstream.

## Verification and decisions

[verification.md](verification.md) inventories passing, failed, historical, excluded and
human checks. All 274 native cases passed with no skips; all full CLI outcomes matched.
The final repository-wide type check remains nonzero: 28 warnings in unchanged source,
compared with 101 on pristine baseline in the same native IDE environment. Changed-code
strict typing is clean; no policy relaxation was made. This prevents claiming fully clean
pre-commit/merge readiness until maintainers resolve or disposition the baseline findings.

Review artifacts are ready; upstream engineering acceptance is not granted. Required
review decisions: draft dependency/integration, native requirement/design and qualification
coverage, remaining baseline typing findings, ECA/DCO, code-owner review and hosted CI.
Use the native PR body and merge checklist. No issue or PR has been published/closed.

An independently maintained sibling `full-issue-fix-20261007/` was discovered during
final inventory, marked in progress and based on native main. Its files were preserved;
no measurement or acceptance of that alternative is claimed by this packet. Reconcile
namespace/baseline strategy with maintainers before choosing a submission.
