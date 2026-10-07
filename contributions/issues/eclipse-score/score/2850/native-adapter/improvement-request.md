# Improvement request draft — not submitted

Related issue: eclipse-score/score#2850. Requested destination: docs-as-code assurance
harness, coordinated with its existing draft PR #628.

Proposed tooling requirement text for maintainer assignment to native instances:

- Provide deterministic task-scoped context preserving Sphinx-needs IDs, status, links,
  source provenance and license metadata, with inert untrusted document text.
- Execute CR-001–005 and goal/support, solution/evidence and breakdown coverage checks
  against immutable before/after snapshots, retaining affected IDs and impact classes.
- Reuse the native coverage/gate/schema contract as the verdict oracle; generate complete
  deterministic traces, input/tool hashes, change diffs and index-first run summaries.
- Evaluate at least 20 public search scenarios in model-free Lane A CI, plus the native
  gate-test seeds, and support a separately selected held-out set.
- Validate candidates cheaply before evaluation and reject missing mandatory check tools.

No new native requirement IDs or accepted statuses are assigned by this draft. Maintainers
must confirm coverage by existing requirements or assign the new instances/qualification
route. The accompanying implementation provides 30 search and 10 held-out scenarios.

Acceptance evidence is the attached `review-packet.md` and `verification.md`. Requested
human decisions are in `impact-analysis.md` and `merge-checklist.md`. No content-review
issue, improvement-request PR or implementation PR has been published by this task.
