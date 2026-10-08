# Improvement

## Description

Add a proposed, evidence-backed AI tooling decision record for #3115, offered for incorporation into #3140. It follows the current infrastructure layout and native template, retaining `dec_rec__infra__ai_sdlc_tooling`, version 2 and `proposed` status.

Explain how AI assistance can operate within S-CORE's existing process, with native artifact ownership, lifecycle loopbacks, bounded context, deterministic checks and accountable human review. Cover all eight issue-listed tools, separating implemented Spec Kit/fabric experience from research on the alternatives. Historical failures, fixture limits and pending qualification remain explicit.

Update the branch with current main `f42e760912e5f99e0db993de717155cc85679f6c`. Upstream commit `612246278900b74218e099d4549600f9f8f16be2` repairs the lifecycle Report Running trace link that blocked the original documentation build. The PR diff against current main still contains only the proposed decision record.

## Related ticket

Relates to #3115 and #3140. Maintainers determine the decision scope, reconciliation with #3140 and required comparative pilots. No issue closure requested.

## Validation

Fresh local checks in an isolated checkout with pinned Bazel 8.6.0 and docs-as-code 8.3.0; policy/tool locks unchanged:

- Current main and candidate `bazel run //:docs_check`: pass, zero documentation/schema warnings.
- Candidate `bazel run //:docs`: pass; HTML rendered.
- `bazel run //:copyright-check` and `git diff --check`: pass. The native copyright target's configured scope is retained; the RST includes the native Apache-2.0 header.
- Native export comparison: one proposed decision record added; all 925 existing needs unchanged; none removed.

[Fresh verification, exact commands, hashes and raw logs](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/tree/contrib/score-ai-sdlc-3115-evidence/contributions/issues/eclipse-score/score/3115/review-preparation). [Original preparation and retained failures](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/tree/contrib/score-ai-sdlc-3115-evidence/contributions/issues/eclipse-score/score/3115/upstream-preparation).

Hosted CI is tracked in the PR checks separately from these local results. Ready for maintainer review; native engineering acceptance, tool selection and qualification remain pending.
