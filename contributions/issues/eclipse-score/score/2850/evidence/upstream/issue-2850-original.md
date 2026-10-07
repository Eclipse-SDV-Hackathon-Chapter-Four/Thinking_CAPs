## Goal

Define and implement an automated harness for maintaining ISO 26262 / ASPICE assurance arguments consistent with Sphinx-needs artifacts under continuous change.

## Why

Safety and process assurance arguments reference development artifacts (requirements, guidelines, tests, code links) as evidence. Every change to those artifacts can refute safety goals or invalidate process compliance. Currently, consistency checks between safety arguments and development artifacts are executed manually or not at all, blocking CI/CD in safety-critical contexts.

This issue establishes the OSS foundation for automated consistency checking in the docs-as-code domain, with an evolving harness that improves over time based on structured traces of prior runs.

## Domain Framing

- **Fixed component**: the Lane A gate contract (`traceability_gate.py`, `traceability_coverage.py`, evidence schema)
- **Variable component**: the harness context, retrieval, and check sequencing presented before and around agent execution
- **Base model**: any — the harness is model-agnostic; agent tooling choice is Lane B
- **Evaluation unit**: one change scenario — a specific RST or needs.json change with a known expected gate outcome

## Agent Roles

| Role | Responsibility |
|---|---|
| **Specifier** | Defines one task as a `spec.md` (input, fixed context, success criteria, expected gate verdict) |
| **Executor** | Applies the change given the harness context |
| **Validator** | Runs `traceability_gate.py` and all consistency checks; emits structured trace artifacts |
| **Distiller** | Outer loop script: extracts structured fields from raw outputs and writes per-task trace files |

The Distiller role is always deterministic Python — never an LLM. The outer-loop script owns distillation so the proposer never reads raw output.

## Repository Entry Strategy

- Keep the top-level agent instruction file short and navigational (map, not encyclopedia)
- Put domain detail in indexed files close to the code and artifacts they describe
- Make the public rule catalog and task corpus queryable by filename, rule ID, and task ID
- Prefer machine-enforced invariants over long prose when a rule matters repeatedly

## Artifact Metamodel

The Sphinx-needs metamodel in docs-as-code covers these artifact types that consistency rules may reference:

- `requirement` (tool_req, std_req, process_requirement)
- `guideline` (gd_guidl, gd_req)
- `test_link` (via `tests` field)
- `code_link` (via `implements` field)
- `evidence` (V&V results referenced in solutions)

## Consistency Rule Catalog

A machine-readable catalog of rules linking argument elements to artifact types and change scenarios. Initial rules to specify:

- `CR-001`: if a `complies` link target is renamed or removed, all linking elements are directly impacted
- `CR-002`: if a requirement type changes, all guidelines claiming compliance are indirectly impacted
- `CR-003`: if a test reference is broken, the linked requirement loses its test coverage evidence
- `CR-004`: if a `std_req` changes content, all `gd_guidl` elements that comply with it require re-review
- `CR-005`: if coverage drops below configured threshold, the gate verdict changes from pass to fail

The catalog is a public OSS artifact. Internal OEM rule extensions remain private.

## Change Impact Classification

Each trace artifact records impact class per affected element:

- `direct_recheck` — element is directly referenced by the changed artifact; must be rechecked immediately
- `indirect_propagation` — element is reachable via the argument graph from a directly impacted element
- `revision_required` — element's supporting evidence is invalidated and cannot be mechanically rechecked

## Reusable Checkable Building Blocks

Reusable argument-and-check fragments that can be instantiated for common patterns:

- **Checkable Goal referencing Requirements**: goal element linked to requirement with consistency rules for content change and status change
- **Checkable Solution referencing V&V Results**: solution linked to test output with rules for test result regression
- **Checkable Requirements Breakdown**: parent requirement with child requirement links and coverage threshold rules

Each block ships with a corresponding automated check that can run in Lane A CI.

## Public Task Corpus

A set of non-confidential change scenarios for evaluating harness candidates:

- Sourced from historical CI gate failures in the docs-as-code repository
- Seeded now with executable `metrics.json` fixtures derived from existing `traceability_gate.py` tests
- Initial runnable scenarios cover threshold failure, broken testcase references, and need-type-scoped pass behavior
- These seed scenarios already exist to make the outer loop and candidate validation runnable before full docs-snapshot tasks are added
- Each scenario: RST or needs.json snapshot + expected gate verdict + expected impacted element list
- Search set: 30-50 scenarios; held-out test set: 10-15 cleanly separated
- No field defects or confidential product data (those stay in the OEM internal file)

## Trace Store Schema

Per-run trace artifacts written by the Distiller (outer loop), readable by proposer via grep/cat:

```
runs/
  <iteration>/
    <candidate>/
      meta.json                  # hypothesis, expected outcome, what changed
      score.json                 # gate pass/fail, coverage delta, provenance
      traces/
        <task_id>/
          gate_output.json       # structured gate result (not raw stdout)
          impacted_elements.json # impacted need IDs, impact class, rule ID
          score.json             # expected verdict vs observed, provenance metadata
          agent_diff.patch       # what the agent changed
evolution_summary.jsonl          # one line per candidate, all iterations
```

**Provenance fields** (per task `score.json`):
- `execution_timestamp`: ISO 8601 timestamp
- `python_version`: Python interpreter version
- `environment_hash`: stable hash of execution environment
- `gate_script_version`: traceability gate version
- `responsible_role`: who is accountable for this outcome (default: `pr_creator`)
- `escalation_role`: who to escalate gate failures to (default: `harness_maintainer`)
- `waiver_authority`: who can approve waivers (default: `release_approver`)

The proposer must start from `evolution_summary.jsonl`, then inspect only the
relevant candidate and task traces. The trace store is designed for selective
navigation, not monolithic prompt packing.

## Harness Interface

Every candidate harness must satisfy this interface (Python):

```python
class AssuranceHarness:
    def get_context(self, task_spec: dict) -> str:
        """Return context to present to the agent before it acts."""
        ...
    def post_process(self, agent_output: str, task_spec: dict) -> dict:
        """Optional: transform or validate agent output before gate runs."""
        ...
```

Candidates are single Python files. The outer loop loads and evaluates them without modification.

**Safety restrictions** (mandatory for all candidates):
- File scope: read only files in `task_spec["input_path"]` or referenced by `consistency_rules`
- No network access: no HTTP, DNS, or external services
- No side effects in `get_context()`: must be read-only
- Deterministic: same inputs → same context
- Tool safety: stdlib and repo-local modules only, no `eval()`/`exec()`

## Lightweight Validation Before Full Evaluation

Before any expensive benchmark run, each candidate must pass a cheap validation step:

- import candidate harness module
- instantiate the harness class
- call `get_context()` on one tiny task spec
- verify trace artifact filenames and JSON serialization shape
- expose a small run-history query surface so agents can inspect failed tasks and candidate deltas without replaying whole histories

That lightweight layer should stay simple and deterministic: one validation entrypoint for candidate loading and one query helper over `runs/` for top candidates, failed tasks, and candidate diffs.

This catches malformed candidates before they consume benchmark time.

## Frameworks Used

- **Spec Kit** (`specify`): bootstrap task specs in `spec.md` format per change scenario
- **Meta-Harness pattern**: outer loop reads trace filesystem, proposes next candidate (Lane B)
- **Sphinx-needs + traceability_gate.py**: Lane A verdict (already exists)

## Lane A Checks (mandatory)

1. Run `traceability_coverage.py --json-output` to extract metrics
2. Run `traceability_gate.py` to produce pass/fail verdict
3. Validate evidence artifact schema
4. Write structured trace artifacts to `runs/`
5. Run lightweight candidate validation before the full task set

## Done When

- Consistency rule catalog (at least CR-001 through CR-005) is defined and machine-readable
- At least 20 public task scenarios exist in the search set
- Outer loop runs end-to-end: harness → gate → distilled trace → `evolution_summary.jsonl`
- Seed corpus includes executable repo-native scenarios sourced from existing gate tests
- One baseline harness candidate is evaluated and its trace is grep-able
- Agents can inspect prior runs through a small index-first query surface
- Lane A checks run in CI without LLM dependency
- Top-level agent guidance stays short and delegates to indexed domain docs

Parent: https://github.com/eclipse-score/score/issues/2850

