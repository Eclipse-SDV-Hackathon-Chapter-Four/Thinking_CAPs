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
