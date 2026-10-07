The existing S-CORE Docs Assistant provides local documentation search, exact requirement lookup, cited answers and explicit snapshot comparison. This PR proposes a narrow Hephaestus documentation-assistance pilot and makes the candidate discoverable from the tooling catalog and documentation.

The review baseline is [72c1fb2](https://github.com/jnsagai/s-core_bot/tree/72c1fb2cab280e6835513b046013e5abea066c3a). The proposal describes safe ingestion, snapshot provenance, retrieval, local generation and server-owned citations; it links design and verification records and identifies the unvalidated Hephaestus corpus/metamodel integration. It starts the pilot with lexical search and exact IDs, then optional local answers evaluated against independently reviewed evidence.

Historical model results, blanket owner review, deterministic tests, preserved failures and unrun checks remain distinct. The existing 2026-10-07 implementation evidence is carried from a verified packet bound to the same source commit; application tests and real-model evaluations were not rerun for this documentation PR. No implementation, model weights or corpus bundles are imported.

Maintainer feedback requested on usefulness, target repository/ownership, corpus/export profile, acceptance cases and dependency/model/corpus license reviews.

Related: #11 (website content aligned with project scope), without closing the wider content review issue. The workflow-fabric proposal in #14 is independently reviewable; a disposable no-commit merge check preserved both proposals and documentation entries without conflict.

Validation:
- Hugo Extended 0.163.0 site build passed with the pinned theme submodule.
- Hugo inventory/shared navigation generation passed.
- Sphinx 8.2.3 / Sphinx-Needs 8.5.0: `python -m sphinx -b html docs public/docs -W` passed.
- Rendered catalog listing, catalog-to-proposal link and Sphinx documentation entry passed.
- All 18 pinned implementation references exist at the review baseline; `git diff --check` passed.

Three documentation files changed. New pages use the repository's Apache-2.0 header; the single issue-prefixed commit has Signed-off-by and Assisted-by trailers. Adoption and pilot implementation remain pending.

Assisted-by: Codex
