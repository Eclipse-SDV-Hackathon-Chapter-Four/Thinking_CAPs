# Offline engineering and IP review

The user selected “Configured LoLa types; present it as a scoped contribution”. This sets the local contribution scope; it does not constitute upstream acceptance, contributor rights attestation or code-owner approval.

The [Eclipse Project Handbook](https://www.eclipse.org/projects/handbook/#genai), consulted 2026-10-07, requires human review before merging AI-assisted commits. The contributor remains accountable for the contribution, licenses and required disclosure. The commit and PR draft identify Codex assistance. The combined patch exceeds 1,000 added lines, so the handbook requires IP Team review. No IP Team clearance is asserted.

The existing ECA account lookup is retained as evidence; the final unpublished commit has no ECA bot status. Account eligibility does not attest contribution rights. Existing license notices are preserved, and native notice checking is reported separately from rights review.

| Subject | Required reviewer decision | Current disposition |
| --- | --- | --- |
| Scope | Accept the configured LoLa discovery scope, including one selected deployment/quality level per type, and typed same-interface Any as the proposed contribution | User-selected proposal; upstream acceptance pending; broader #1261 remains open |
| ABI/API | Assess unchanged IRuntime and Runtime layout plus additive FFI symbols; assess FindServiceError migration for internal bridge implementations | Source comparison and legacy-runtime regression supplied; native acceptance pending |
| Callback ownership | Review rejection, synchronous callback, replacement, false return, deferred native deletion, cancellation and destruction | Native guards, units and production checks supplied; human review pending |
| Concurrency | Confirm native callbacks are serialized and observe native reentrancy/lifetime restrictions | Tests and source trace supplied; accepted analysis pending |
| Allocation | Adopt the applicable Rust/FFI allocation profile and evaluate bounded queues, callback allocations and configuration-cache lifetime | Guarded callback transfer/disposal supplied for Specific, Any and configured discovery; profile applicability and acceptance pending |
| Requirements and safety | Accept native-to-Rust subscription state mapping, get/set/unset errors and requirement/design impacts | Proposed trace supplied; safety classification and acceptance not invented |
| Qualification | Confirm tool/version/target/use qualification evidence under the adopted verification plan | Exact identities supplied; qualification unknown |
| Contributor/IP | Verify rights, authorship, provenance, AI disclosure and the final commit’s ECA validation | Pending human/official validation |
| Merge | Approving review, code-owner review, checklist and all protected contexts on the final PR/merge-group head | No publication or approval asserted |

Reviewers should record their names, reviewed commit, date, decision and rationale in the native review system. Blank or pending entries do not count as approval.
