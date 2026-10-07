# Issue selection — agent assessment, 2026-10-07

Selected: [eclipse-score/score#2850](https://github.com/eclipse-score/score/issues/2850),
**Agent Harness — Docs-as-code / Assurance Consistency Automation**. Observed open,
labelled `community:ai`, with one comment and no assignee in the retrieved snapshot.

The issue separates context/retrieval from deterministic assurance gates and asks for
queryable artifact IDs, task history, and change scenarios. The chatbot's Sphinx-needs
ingestion, exact-ID navigation, pinned evidence and snapshot comparison provide relevant
building blocks. This supports a scoped retrieval contribution, subject to maintainer
agreement and a new task-scoped adapter; it does not establish acceptance or solve the epic.

| Candidate | Relationship | Decision |
| --- | --- | --- |
| score#2850 | Documentation context/retrieval around native assurance checks | Primary existing issue for a scoped foundation proposal |
| [score#3115](https://github.com/eclipse-score/score/issues/3115) | Evaluate listed AI SDLC tools and produce a decision record | Separate workstream; chatbot does not satisfy this decision record |
| [score#3161](https://github.com/eclipse-score/score/issues/3161) | APM, Spec Kit, MCP and marketplace integration | Broader tooling work; not the current chatbot interface |
| [score#1768](https://github.com/eclipse-score/score/issues/1768) | Onboard inference engine contribution call | Local documentation assistance has no in-vehicle inference integration |
| [process_description#805](https://github.com/eclipse-score/process_description/issues/805) | AI-assisted safety requirements inspection pilot; pilot implementation already linked to PR#809 | Adjacent process work; chatbot is read-only and does not inspect or approve safety requirements |
| [mcp-servers#31](https://github.com/eclipse-score/mcp-servers/issues/31) | Extend Graphify with GitHub issue overlay data | Adjacent provenance/knowledge graph work; no Graphify or MCP adapter exists in the chatbot |
| [score#2827](https://github.com/eclipse-score/score/issues/2827) | Wider harness rollout | Background only; direct documentation domain issue #2850 is more precise |

Repository-wide issue searches included chatbot, chat bot, chat, bot, RAG, LLM,
knowledge, generative, documentation with AI, and the main repository's community:ai label.
The bounded results are retained in [discovery.json](evidence/upstream/discovery.json);
search results are not an exhaustive backlog export. Selected issues were fetched
individually to confirm their bodies and states.

[Issue comments](evidence/upstream/comments-2850.json) add a Phase 2 security proposal:
untrusted inputs, independently executed checks, path constraints and recovery.
No linked PR appeared in the recorded #2850 PR search. That search is not proof that
no related implementation exists elsewhere.

Recommended next action: use the [draft proposal](upstream-proposal.md) to request a
scoped subtask under #2850 for a deterministic documentation context adapter. Confirm the
target repository with the issue owner before preparing its native integration patch.

