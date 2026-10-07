# Acceptance mapping

The full MVP implementation and exact criterion/check mapping are in
[native-adapter/review-packet.md](native-adapter/review-packet.md).
The prior chatbot-only mapping is preserved in
[native-adapter/evidence/history/prior-acceptance-mapping.md](native-adapter/evidence/history/prior-acceptance-mapping.md).

Native artifacts cover the deterministic adapter, CR-001–005, checkable blocks,
30 public search / 10 held-out scenarios, native fixture/build seeds, full traces,
baseline evaluation, index-first queries, guidance and model-free Lane A CI.
Technical verification is local; integration of the unmerged native draft, project-wide
typing debt and authorized engineering/contributor acceptance remain pending.
The upstream Phase 2 security comment is explicitly post-MVP.

[The integration choice](integration-20261007/decision.md) is resolved locally: the adapter is selected as a stacked follow-up to #628, with initial PR base `harness`. Upstream adoption, #628/main conflict resolution and final-revision checks remain pending.
