# S-CORE #2850 — Native assurance harness contribution

**Integration choice resolved locally:** use the native adapter as a stacked follow-up to docs-as-code draft #628. The initial PR base is **`harness`** and the prepared local branch is **`contrib/score-2850-native-mvp`**. See the [decision and comparison](integration-20261007/decision.md) and [selected submission instructions](integration-20261007/reproduce.md).

The [native implementation](native-adapter/README.md) extends #628 at `4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9`. It includes a deterministic context candidate, CR-001–005 checks and reusable blocks, 30 search / 10 held-out public scenarios, complete trace evaluation, native gate/schema integration, index-first queries and Lane A CI. The staged patch applies cleanly to current `harness`; all 394 tracked files match the current source vector and nine fixed contracts are preserved. The [license audit](integration-20261007/license-audit/README.md) repaired six baseline header omissions without changing executable content. The 185 implementation files remain byte-identical; runtime evidence predates this header-only follow-up, and no native runtime tests were rerun.

The contribution is prepared for draft review. #628 is unmerged and currently reports a merge conflict. Before main adoption, its owner must integrate it, then this contribution must be rebased and verified on the resulting revision. The inherited whole-project typing findings and human ECA/DCO/impact/qualification/code-owner/CI gates remain pending. No new attributed/sign-off commit, push, PR, issue closure or approval is claimed.

- [Integration decision and prepared branch evidence](integration-20261007/README.md)
- [Selected PR description](integration-20261007/pr-description.md)
- [Native patch and candidate](native-adapter/README.md)
- [Acceptance mapping and review](native-adapter/review-packet.md)
- [Verification and raw evidence](native-adapter/verification.md)
- [Remaining merge checklist](native-adapter/merge-checklist.md)
- [Native check reproduction](native-adapter/reproduce.md)

The independent [main-based implementation](full-issue-fix-20261007/README.md) is preserved **but not selected for submission**. Its source, evidence and companion verification report remain independently maintained and excluded from this packet's integrity scope. No competing source trees or test evidence were combined. The decision may be revised only explicitly following maintainer direction, with verification of the resulting contribution.

The earlier chatbot retrieval foundation remains separately retained in `evidence/`: source `72c1fb2cab280e6835513b046013e5abea066c3a`, deterministic checks and labelled historical releases. It is background evidence, not the native implementation or an assurance approval. Prior reports and the manifest remain in the native packet's history. [Issue selection](issue-selection.md) preserves the original rationale.

The [parent manifest](artifact-manifest.json) binds the selected adapter packet, integration record and historical background. Original measured packet bodies are preserved; the selected PR body and integration decision above govern the submission path. Event eligibility and original release-owner assessments remain separate from native engineering acceptance.
