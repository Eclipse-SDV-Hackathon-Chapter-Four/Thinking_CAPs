# Offline engineering review report

Review subject: US21 report/exit placement and bounded P704 worker binding proof.
Human decisions remain pending and separate from execution.

| Evidence | Baseline | Optimized |
| --- | --- | --- |
| Actual native API run | 01M437XNXAVCZ44KGEJ3R8552E | 01M437Y5ARMVN670FNJ2AHK5NW |
| Workflow completion | succeeded: report exported | succeeded: report exported |
| Human nodes/handler visits | 0 / 0 | 0 / 0 |
| Original source files initialized | 740 | 740 |
| Historical candidate application | local replay, exact scope | local replay, exact scope |
| Cross-run/arm probes | refused | refused |
| Fresh lightweight collector receipt | failed | failed |
| Required native XML | missing (deliberate probe) | missing (deliberate probe) |
| Actual native feedback route | exact sealed record | exact sealed record |
| Provider guard | refused | refused |
| Provider requests/tokens | 0 / 0 | 0 / 0 |
| Worker hook witnesses | 9 | 9 |
| Owned worker/server state | stopped | stopped |
| Reviewer decision | null | null |

## Changes for review

The current graphs replace human nodes with a deterministic report command and exit.
Expected failure/refusal paths also reach report export. AGENTS.md and current
benchmark/spec/plan/contract controls require offline review. Historical graphs and
packets are unchanged. Reports hash-bind all eight operation records to native run,
arm and worker binding. Each source-binding supplement links the unchanged archive,
740-file original manifest, context digest and native IDs. The raw run report has a
null native baseline field because the runtime binding stores source/archive/context
identity; the supplement explicitly retains the original context's native baseline.

The fabric checkpoint fix allows only measured native Git metadata outside source
inventory, pins config and run-specific HEAD and refuses active hooks, links and
source tampering. The accompanying patch is relative to immutable US19 exports.
The historical P704 patch is a labeled replay; this phase changes no target semantics.

## Measurements and limits

The earlier unchanged fabric code passed 138 scoped tests, including 36 worker
binding tests, Ruff, mypy (150 source files), frozen sync, foundation, pinned Spec Kit
prerequisites and package build. Current graph conformance, actual terminal execution
and report/hash/worker/feedback checks are fresh measurements. Full native tests are
not executed in these report runs. Earlier two 113-case replays remain historical.
The lightweight collector does not establish native check coverage. Provider usage
is zero; observed provider-result/meter binding and actual agent prompt consumption
are not exercised. No model savings measurement exists for this pair.

## Offline review questions

- Does report/exit placement and preserved refusal/failure evidence satisfy the owner's
  execution preference for this exact graph/source subject?
- What is P704's complete native impact and required-check scope, including any QNX
  applicability, before a live trial can be admitted?
- Which separately bound provider observer/agent-transmission evidence is required
  before a future DeepSeek trial?

Native engineering acceptance and T033 remain pending. Publishing the existing PR
packet remains deferred. Run completion grants no engineering or publication authority.
