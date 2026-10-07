# Issue selection

Selected: [eclipse-score/score #3115](https://github.com/eclipse-score/score/issues/3115),
“Evaluate AI SDLC / SpecKit Tooling.” Confirmed open on 2026-10-07. The user explicitly
selected this issue after the candidate search.

The issue asks for a decision record covering packaging (APM, Lola, OKIT), SDLC/harness
(Syspilot, BMAD, Spec Kit, Pharaoh) and evaluation (Harbor). `s-core_sw_fabric` provides
experience using Spec Kit to develop an integration around native S-CORE process,
Sphinx-Needs exports, deterministic validation, MCP context and bounded agent execution.
That experience is directly useful to a tooling evaluation without claiming the
implementation epic is complete.

## Existing work and review questions

The issue timeline identifies open, unmerged [PR #3140](https://github.com/eclipse-score/score/pull/3140).
Its captured head is `da32256d65692eef24c0bbb23d69016a83594239`, with a proposed
`docs/design_decisions/DR-010-infra.rst`. Its comments and reviews request:

- A clear motivation that acknowledges S-CORE's existing engineering process.
- Real use on S-CORE artifacts, rather than repository summaries alone.
- Loopbacks after changed or missing requirements, including nonfunctional obligations.
- Granular agents/skills and manageable context.
- Technical feasibility, qualified evidence and human review of understandable artifacts.
- Generation from the native metamodel and a derived sidecar graph instead of duplicate
  process/artifact authorities.

The contribution addresses these questions with an experience report and explicit gaps.
It supplements existing work. A comparison score is not fabricated for an untested tool.

## Alternatives considered

| Issue | Fit | Why it is secondary |
| --- | --- | --- |
| [score #3161](https://github.com/eclipse-score/score/issues/3161) | Broad AI harness integration: APM, SpecKit, MCP and marketplace | Requires integrated tools and a marketplace; the fabric does not establish completion |
| [score #2850](https://github.com/eclipse-score/score/issues/2850) | Docs-as-code assurance consistency harness | Requires its own rule catalog, corpus, harness interface, trace format and CI; adjacent work, not fulfilled by the fabric |
| [score #2851](https://github.com/eclipse-score/score/issues/2851) | Module/middleware evaluation harness | Requires at least 20 public scenarios and native structured evaluation/CI contracts; existing issue fixes are not that benchmark corpus |
| [process_description #805](https://github.com/eclipse-score/process_description/issues/805) | AI support within a safe process | A requirements-inspection pilot is already marked implemented through PR #809; remaining process and audit work has a different scope |

Original issue bodies and current statuses are under `evidence/upstream/`.
APM integration [PR #3188](https://github.com/eclipse-score/score/pull/3188) also remains
open and unmerged at capture; it cannot be treated as adopted infrastructure.
