# S-CORE #2850 — Documentation chatbot contribution evidence

This packet proposes the [S-CORE Docs Assistant](https://github.com/jnsagai/s-core_bot)
as a reusable documentation retrieval foundation for
[Agent Harness — Docs-as-code / Assurance Consistency Automation](https://github.com/eclipse-score/score/issues/2850).
The assistant already provides pinned documentation ingestion, exact requirement lookup,
cited local answers, immutable snapshots, and explicit version comparison.

| Field | Record |
| --- | --- |
| Local branch | `contrib/score-chatbot-2850-evidence` |
| Upstream observation | Open, retrieved 2026-10-07 |
| Chatbot baseline | `72c1fb2cab280e6835513b046013e5abea066c3a`, clean source checkout |
| Earlier local release | `v1.0.0` at `027f18b257a28893c25d45407c2553d6d37a2cf2` |
| Local contribution status | Evidence collected; scoped integration proposal |
| Upstream PR / acceptance | Pending; no submission or maintainer acceptance |
| Event status | Preparation; eligibility and event delta not established |

Issue selection is an agent assessment. No issue specifically requesting a documentation
chatbot appeared in the recorded searches. #2850 explicitly includes context retrieval
over Sphinx-needs artifacts, making it the closest issue in the main S-CORE repository.
The chatbot is not a completed implementation of that issue.

The contribution still needs a deterministic, task-scoped adapter to the issue's
`AssuranceHarness.get_context()` interface. Model-generated chat and semantic search
cannot be substituted for its deterministic Lane A checks. See the
[acceptance mapping](acceptance-mapping.md) for every remaining obligation.

## Review the packet

- [Issue selection](issue-selection.md): alternatives, rationale and current issue activity.
- [Review packet](review-packet.md): architecture, provenance, checks, licensing and gaps.
- [Verification](verification.md): fresh check results and historical evidence limits.
- [Reproduce and verify](reproduce.md): offline integrity checks and test commands.
- [Upstream proposal draft](upstream-proposal.md): concrete scoped contribution request.
- [Evidence folder](evidence/): current source archive, readable project documents,
  original upstream issue/comments/guidance, raw check logs and historical release records.
- [Artifact manifest](artifact-manifest.json): SHA-256 hashes of the packet files.

No model weights or corpus bundles are included. Existing design records and notices
travel with the source; historical failures and review limitations remain visible.

