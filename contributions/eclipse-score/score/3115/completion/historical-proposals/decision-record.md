# Proposed decision-record supplement: AI tooling within the S-CORE process

Status: **proposed for maintainer review**. Relates to
[#3115](https://github.com/eclipse-score/score/issues/3115) and the existing proposed
`dec_rec__infra__ai_sdlc_tooling` in [PR #3140](https://github.com/eclipse-score/score/pull/3140).
This is an evaluation contribution, not an accepted tooling or safety decision.

## Context

S-CORE already defines its engineering process, work products, metamodel, traceability
and review responsibilities. The problem to solve is how AI assistance can operate
inside those rules while retaining understandable artifacts, measured verification and
human accountability. Introducing another authoritative requirements/process store would
add synchronization work and obscure ownership.

Review of PR #3140 asks for real experience, clear motivation, lifecycle loopbacks,
manageable context and qualification evidence. The fabric is one exploratory integration
with implementation and historical measurements against pinned S-CORE artifacts.
It is not a comparative benchmark of every candidate or a community-scale rollout.

## Proposed decision

Evaluate capabilities by layer and use a bounded native-process pilot before selecting
an organization-wide toolchain:

1. Keep native S-CORE artifacts, IDs, metamodel and accepted tailoring authoritative.
   Generate or derive agent context from pinned native sources. Derived graphs must
   remain rebuildable views rather than a second requirements database.
2. Use Spec Kit for development of the integration itself. Evaluate adapted procedures
   for S-CORE tasks without requiring native products to become Spec Kit documents.
3. Evaluate packaging separately from workflow execution. APM is a candidate consistent
   with the issue's existing packaging proposal; the fabric does not establish APM
   installation, distribution, upgrade or governance suitability at organization scale.
4. Use deterministic tools to measure required checks. Agents may draft and critique;
   required engineering judgments remain with authorized humans outside unattended runs.
5. Admit only source-bound tasks with explicit write paths, check scope, context, tools,
   attempts and budgets. Refresh impact and evidence when subjects change; preserve failures.
6. Retain portable native evidence. A successful orchestration run must not hide failed
   compilation, missing lint evidence, unsupported platforms or pending engineering review.

Fabro is the fabric pilot's pinned execution candidate. It is not one of #3115's listed
frameworks and this proposal does not select it for S-CORE. Its observed resume limitation
is part of the assessment.

## Alternatives considered

All repository claims below come from captured primary sources; see
[candidate identities](evidence/candidates/index.json). Documentation support is not
proof of behavior. Numeric rankings and unsupported negative claims are deliberately absent.

| Candidate | Documented purpose / relevant capability | Experience available here | Evaluation disposition |
| --- | --- | --- | --- |
| [APM](https://github.com/microsoft/apm) | Manifest-based agent context packaging, locks, policy and MCP integration | Pinned S-CORE APM/MCP package inspection and disposable MCP probes; no APM CLI distribution pilot | Test packaging reproducibility, drift, upgrade/rollback and destination controls before selection |
| [Lola](https://github.com/LobsterTrap/lola) | Cross-assistant skill/context packages and declarative installation | Primary-source research only | Compare the same S-CORE package/install cases with APM; keep an alternative |
| [OKIT](https://github.com/Mumme-IT/okit) | Installs skills/agents to configured providers and records source commits | Primary-source research only | Test provenance, provider writes, upgrades and isolation; no unsupported maturity ranking |
| [Syspilot](https://github.com/enthali/syspilot) | Sphinx-Needs links and focused change context; README labels early research | Primary-source research only | Evaluate native metamodel/loopback behavior and reproducibility with the shared pilot |
| [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) | Skills and workflows for AI-assisted development and explicit planning/learning loops | Primary-source research only | Test native artifact adaptation and requirement-change loopbacks; do not assume their absence |
| [Spec Kit](https://github.com/github/spec-kit) | Specification-driven workflow | Fabric developed with pinned `v1.0.12` / `e77daa9021d20db26b878f7dfa5640fe5a42d04e` | Retain this concrete development experience; native-task adoption needs a separate pilot |
| [Pharaoh](https://github.com/useblocks/pharaoh-skills) | Sphinx-Needs analysis encoded in skills/agent instructions | Primary-source research only; requested URL redirects; repository archived | Assess reusable concepts and successor maintenance separately; no new dependency selection |
| [Harbor](https://github.com/harbor-framework/harbor) | Agent benchmarks and evaluation environments | Primary-source research only | Evaluate as a test driver for an agreed public corpus; engineering acceptance remains native |

The current source captures are dated 2026-10-07. The fabric's older locked versions
and toolchain remain separate; present-day README capabilities are not transferred to
the historically measured versions.

## Evidence from the fabric pilot

| Question | Retained experience | Limit |
| --- | --- | --- |
| Native ownership and traceability | Locked process/docs sources; native export/import, artifact indexing, expected-set trace, drift and impact implementations (001–004) | Production mapping/profile review and broader native compatibility remain open |
| Lifecycle loopbacks | Old/new reverse impact, stale-subject rejection, changed-relation regression and bounded correction/evidence-refresh modes (011) | Demonstrates implementation checks; not complete real B1–B5 engineering qualification |
| Agent context and granular procedures | Pinned MCP discovery/probes (007), baseline-bound manifests, selected skills, bounded summaries/retrieval and call limits (011) | Unsupported tools and unknown usage block relevant stages; APM rollout is untested |
| Deterministic validation | Historical 011 full regression: 2,056 passed, 22 skipped; affected scope: 139 passed. Initial failed run retained | These logs belong to historical subjects; no current dirty-worktree pass or full native readiness claim |
| Context measurement | Synthetic byte estimates: 86.94–95.12%; first live rendering proxy: 30.46–30.63%; later tool-projection proxy: 66.32–66.60% | Controlled fixtures with expected outputs; no proven real-task 60–80% savings, semantic quality, billing or runtime advantage |
| Native use | Lifecycle #704 packet retains a scoped implementation with 113 native cases; source/export and additional issue packets retained in Thinking_CAPs | Native source revisions, selected checks and pending review apply per packet; no universal process compliance |
| Failure transparency | A historical DeepSeek Communication #1261 attempt retains compilation failure, 0/5 executed tests and incomplete quality checks even when orchestration finished; the later Claude correction retains passing selected Linux checks | Runtime completion cannot be acceptance; failed history and later corrections are distinct, with native qualification/acceptance still pending |
| Trust and human review | Fixture assurance gate and stale/unauthorized refusal cases (005); explicit offline engineering review records | Protected production trust roots and acceptance authority are not provisioned; no ASIL-B qualification |
| Runtime suitability | Pinned Fabro disposable register/run/status/cancel/export probes (006) | Same-run checkpoint resume was unavailable on the candidate; no runtime selection |

Historical evidence is labelled carried. Raw development/JUnit logs and benchmark
records travel in this packet; native implementation packets remain at their existing
repository paths. Some deep 011 source/build/tool payloads are only inventoried and must
be recovered for full replay. The [evidence map](evidence-map.md) names the exact scope.

## Consequences

This proposal retains a single native engineering authority and makes tool choices
separable. It adds integration, compatibility and evidence-retention work. Spec Kit
artifacts for developing the fabric must not become mandatory duplicate artifacts for
all S-CORE development. Native-version drift, platform applicability and complete
check denominators require explicit treatment. Agents and generated code remain
understandable and reviewable by the people responsible for them.

## Justification and remaining decisions

The fabric gives PR #3140 real experience for architectural boundaries, selective context,
negative outcomes and native verification. It supports testing these integration patterns;
it does not establish superiority over unexecuted candidates or qualification of tools.

Before #3115 is considered done, maintainers need to agree the decision scope and evidence
threshold, reconcile this supplement with the existing DR, decide which comparative pilots
are required, and review the native document through its CI and ownership rules. Native
process applicability, qualification, production trust and organization-scale behavior
remain explicitly undecided. No acceptance date, accepting person or approval is invented.
