# Prepared draft — human review required

# Draft proposal — not submitted

Suggested title: **Propose pinned documentation retrieval foundation for #2850**

Related ticket: https://github.com/eclipse-score/score/issues/2850

The S-CORE Docs Assistant provides a local documentation index with source commit/file
provenance, exact Sphinx-needs ID lookup, cited answers and immutable snapshot comparison.
We propose reusing its prepared documentation data and provenance format for the context
retrieval portion of #2850.

Implementation baseline:
https://github.com/jnsagai/s-core_bot/tree/72c1fb2cab280e6835513b046013e5abea066c3a

The evidence packet includes the source and locks, design/traceability records, fresh
deterministic test logs, historical real-model evaluation, original release manifests,
SBOM/notices, and an acceptance mapping with open integration work.

The proposed first subtask is a deterministic, task-scoped adapter implementing
AssuranceHarness.get_context(). It would consume only authorized prepared artifacts,
preserve artifact IDs and provenance, emit stable context, and avoid model calls, HTTP,
external dependencies and writes during context creation. Native traceability coverage,
gate checks and evidence schema validation remain the acceptance oracle.

The current chatbot does not implement #2850's consistency rule catalog, native scenario
corpus, outer loop, trace store or Lane A gate integration. Historical human metrics are
blanket owner acceptances and do not establish per-claim accuracy or S-CORE approval.

Requested maintainer decision: whether this retrieval foundation is useful for #2850 and
which repository should host a scoped adapter subtask. No request to close the parent issue.

For a later native PR, follow the captured S-CORE request/template and review process.
This draft is a contribution discussion proposal; no native patch is ready to submit.



## AI assistance and review

- Historical authoring tools/extent require contributor confirmation; this compliance preparation uses OpenAI Codex.

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
