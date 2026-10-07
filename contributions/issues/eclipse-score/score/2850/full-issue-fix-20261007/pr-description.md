## 📌 Description

Implements the OSS MVP in eclipse-score/score#2850: a deterministic, task-scoped assurance harness that evaluates CR-001–CR-005 with the native traceability gate and writes schema-checked, selectively queryable evidence. Adds 30 public search scenarios and 10 heldout scenarios, task specifications, a single-file baseline candidate, native coverage extraction, reusable argument checks, provenance, immutable run directories, and index-first queries.

The native Python 3.12/3.14 CI jobs evaluate both splits and upload their trace stores. Requirements, gate thresholds, metamodel and dependency pins are preserved. Documentation inputs remain inert data; no model calls are required.

Targets main at `102aad30bd373295d275722c3942b392a8eb7149`. The patch also applies cleanly to observed main `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16`; complete native verification is bound to the former revision, with no test evidence transferred to the newer tree. Draft PR #628 is a parallel `score_harness` proposal; namespace and loader reconciliation needs maintainer agreement before adoption.

Phase 2 security architecture in the issue comment is post-MVP. The public cohorts are executable test-derived seeds, with ten native snapshot-extraction cases; they are not historical production incidents or evidence of real-agent quality.

## 🚨 Impact Analysis

See the attached impact analysis, acceptance mapping and verification packet. Existing linkage/statistics requirements are reused. Coverage of the new change-impact/evolution capabilities by existing qualified tool requirements has not been established. The current native TVR remains unchanged (`evaluated`, v8.1.2). Qualification applicability and the parallel draft design need a maintainer disposition.

- [ ] This change does not violate any tool requirements and is covered by existing tool requirements
- [ ] This change does not violate any design decisions
- [ ] Otherwise I have created a ticket for new tool qualification

These impact boxes remain open deliberately. A local qualification-review ticket draft is supplied; no ticket or accepted decision is claimed.

## ✅ Checklist

- [x] Added/updated documentation for new or changed features
- [x] Added/updated tests to cover the changes
- [x] Followed project coding standards and guidelines

Local validation: full native Bazel test/build matrix on Python 3.12 and 3.14, complete pre-commit hooks, exact CI evaluation commands on both splits, and documentation rendering. Each baseline matches all 40 specified verdict/impact outcomes. Expected gate failures are regression scenarios, not failing harness tests. Raw logs, native XML, source/patch hashes, traces, failed attempts and fixture corrections travel with the review packet.

Upstream CI on the submitted revision, Eclipse ECA, and code-owner approval remain pending. This text is a local PR description draft; no PR has been published and no issue has been closed.
