# PR and merge obligations

This checklist distinguishes prepared engineering artifacts from human acceptance.
Sources: the pinned native PR template, CODEOWNERS, tooling verification page, native
workflows/pre-commit config, and captured umbrella CONTRIBUTION.md.

| Obligation | Artifact / disposition |
| --- | --- |
| Concrete native implementation | `candidate/` and `patches/0001-score-2850-assurance-harness.patch` (exported after final verification) |
| Issue acceptance mapping | `review-packet.md`; full MVP criteria, not a chatbot-completion claim |
| Requirements/design/qualification impact | `impact-analysis.md`; applicability and approval remain pending |
| Feature and contract documentation | native RST concept, subsystem README, corpus index/spec.md files |
| Regression and requirements-derived cases | native Bazel adapter and assurance tests, 30 search + 10 held-out scenarios, original gate seeds |
| Verification report | `verification.md`, raw commands/logs/JUnit/traces and baseline/config/subject hashes |
| Complete trace and query evidence | `evidence/runs/`, index-first query log, baseline and candidate scores |
| License/copyright and coding checks | Current full-tree audit passes 164 supported native files and 15 packet scripts; six native and eleven packet omissions repaired. Original notices/bytes retained, no dependency upgrades. See ../integration-20261007/license-audit/README.md |
| Portable reproduction and integrity | `reproduce.md`, baseline archive, source binding, offline verifier and manifest |
| Correct native PR body | `pr-description.md`, native template structure and honest unchecked impact approvals |
| Draft baseline prerequisite | Draft #628 is unmerged; coordinate with its author/maintainers or rebase after merge, then rerun checks |
| Accepted improvement request | Not established; obtain maintainer decision under the umbrella contribution process |
| Commit message | `commit-message.txt` is a draft message; contributor must add their real sign-off when creating commits |
| ECA and DCO | Contributor must confirm ECA and sign their actual commits. No identity or sign-off is fabricated |
| Code-owner/content review | Pending authorized infrastructure reviewers; no review is represented as granted |
| Native whole-project typing | 28 warnings remain in unchanged files (101 on pristine baseline); changed-code strict checks pass. Resolve/disposition before full pre-commit readiness |
| Native hosted CI and branch protection | Workflow is implemented and local commands measured; GitHub run and required-status configuration remain pending |
| Tool requirements/design coverage or qualification ticket | Pending human applicability decision required by native PR template |
| Publish/merge | No PR has been submitted, no issue closed, no merge/release performed |

The packet is for review. Local success cannot replace these pending decisions.
