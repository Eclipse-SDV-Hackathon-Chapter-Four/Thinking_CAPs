# Impact analysis for S-CORE #2850

Target: `eclipse-score/docs-as-code` main at `102aad30bd373295d275722c3942b392a8eb7149`. This is a proposed OSS MVP, with no model dependency or automatic adoption/engineering acceptance.

The change adds an opt-in assurance scenario evaluator, public CR-001–CR-005 catalog, task-scoped baseline candidate, three reusable checks, trace validation and selective queries. CI exercises these through the native Bazel test suite. The native gate, thresholds, requirement metamodel, compiler/dependency pins and existing work-product statuses are preserved. Coverage extraction calls the existing native calculation functions.

`tool_req__docs_test_linkage_metrics@1` covers native linkage statistics and type filtering; its recorded `implemented` value is `YES`. `tool_req__docs_test_link_testcase@1` covers requirement/test links. The new change-impact catalog and harness evolution are specified by issue #2850; complete coverage by existing qualified tool requirements has not been established. `tool_req__docs_req_attr_testcov@1` has explicit `status: invalid`, and is not used as a valid obligation.

The authoritative native TVR, `doc_tool__score_docs_as_code@3`, records `status: evaluated`, tool version `v8.1.2`, and `security_affected: YES`. That record is not qualification or approval of this new harness. Native source: `docs/internals/requirements/tool_verification.rst`. The relevant tool-management guidance is `docs/how-to/perform_tool_verification.md`.

Potential malfunctions in the proposed use include incorrect change-impact classification, accepted inconsistent metrics, omitted tasks, fabricated or stale traces, and reading input outside the declared scope. Measures in this patch include independently specified expectations, old/new graph checks, native metric/gate execution, local schema validation, immutable per-run output, input/source hashes, explicit file allowlists, POSIX no-follow reads, special-file rejection, and retained raw results. Static candidate screening is not a sandbox; candidate Python remains reviewed program code.

Maintainer dispositions required before adoption: determine requirement/TVR applicability for the new capabilities; reconcile the parallel namespace and loader in draft PR #628; assess the bounded seed corpus and intended deployment scope. No tool-qualification ticket has been filed, no native acceptance is asserted, and no requirement/design IDs or statuses are fabricated. A ticket draft is included for the project to use if qualification is required.

Phase 2 in the issue comment explicitly proposes post-MVP injection sanitization, causal verification, capability tokens and adaptive rollback. This contribution does not claim those extensions.
