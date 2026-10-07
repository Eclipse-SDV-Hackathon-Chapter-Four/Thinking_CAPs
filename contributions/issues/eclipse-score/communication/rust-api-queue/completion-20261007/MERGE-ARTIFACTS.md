# Merge artifact and acceptance inventory

The captured Communication main-branch rules (`evidence/planning/upstream/rules.json`, retrieval metadata alongside it) require one approving review, code-owner review, dismissal of stale approvals after pushes, and extra approval for unattributed changes. The merge queue uses ALLGREEN. Accepted merge methods are merge, squash and rebase. Recheck rules and issue activity when submitting; this is a dated observation.

The required hosted contexts are:

- `eclipsefdn/eca`
- `GCC15 / Build & Test`
- `QCC - Build & Test`
- `Address & Undefined Behavior Sanitizer / Build & Test`
- `Thread Sanitizer / Build & Test`
- `Linters / clang-tidy`
- `Linters / clippy`
- `Linters / ruff`
- `review-checklists`

| Required or useful work product | Supplied artifact | Acceptance remaining |
| --- | --- | --- |
| Concrete source subject | Full Git bundle, integrated baseline-bound patch, source archive, changed-file hashes and source identity | Maintainer reviews the exact submitted head; rebases require new checks |
| PR title, behavior, issue references and scope | PR-TITLE.txt and PR-BODY.md | Publish through the contributor's fork when authorized; broader #1261 stays open |
| Applicable verification and exclusions | CHECKS.md, expected-checks.json, raw commands/logs, build events, XML and analyzer reports | Resolve every failed/unavailable applicable check; hosted statuses on final head |
| Supported QCC target | Read-only availability observation and explicit omission | Run in licensed project environment |
| Manual targets and test-code analyzer coverage | Manual inventory, explicit macro/doctests and Clippy action query | Review ignored/excluded cases under the native plan |
| Native requirement/design trace | ACCEPTANCE-TRACE.md, changed detailed design and user-facing examples | Native owner accepts impacts and applicability; no invented requirement IDs |
| API/ABI and callback ownership | API-ABI-REVIEW.md, structural comparison and regressions | Platform ABI, concurrency, reentrancy, lifetime and allocation acceptance |
| Contributor agreement and contribution rights | Preserved historical ECA account evidence, authorship/provenance, AI disclosure | Official ECA bot status for final commit and human rights attestation |
| IP review for contribution size | IP-SUBMISSION.md, patch/source/provenance/dependency identities | Native IP review reference and clearance |
| Human engineering and code-owner review | HUMAN-IP-REVIEW.md and native CODEOWNERS | Named approving reviewer, reviewed head, rationale and required checklist |
| Qualification | Pinned tool/compiler/policy identities and measured environment | Applicable version/target/use qualification remains unknown |
| Portable integrity | artifact-manifest.json, sidecar SHA-256 and verify.py | Integrity verification does not confer engineering approval |

The local commit is unsigned and contains no invented Signed-off-by, human approval, ECA clearance or safety acceptance. No PR, IP request, upstream comment, merge or release was sent by this task. This packet makes the contribution concrete and reviewable; it cannot manufacture the external approvals required to merge it.
