# Integration decision — S-CORE #2850

The selected contribution is **the native adapter extending draft #628**, selected for a stacked follow-up. The initial PR base is **`eclipse-score/docs-as-code:harness`**, at `4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9`, and the local work branch is **`contrib/score-2850-native-mvp`**. The [existing adapter patch](../native-adapter/patches/0001-score-2850-assurance-harness.patch) is the sole selected implementation. This resolves the local choice; upstream adoption is not represented as approved.

| Consideration | Adapter on #628 — selected | Independent main-based patch — retained |
| --- | --- | --- |
| Native subsystem | Extends `score_harness/`, existing `AssuranceHarness` and dynamic candidate loader | Introduces `assurance/`, its own `AssuranceHarness` and Protocol/AST-screened loader |
| Existing flow | Retains baseline/rule candidates, four active native seed tasks, outer loop and query interface | Establishes an alternative runner, corpus and query CLI |
| Verification binding | 274 native cases; both candidates on 30 search + 10 held-out + four original seed tasks; exact selected source unchanged | Separate packet reports Python 3.12/3.14 native matrix and 40 baseline scenarios; its evidence is not combined with adapter results |
| Integration cost | Depends on #628; extends one proposed subsystem and preserves its contracts | Can apply to observed main but leaves an independent subsystem/design competing with #628 |
| Remaining check finding | 28 inherited repository typing warnings, requiring resolution or authorized disposition | Its packet reports passing pre-commit on its own baseline; those results do not apply to the selected branch |
| Local disposition | One canonical contribution path | Not selected for this contribution; source and evidence remain untouched |

The choice favors native interface/seed compatibility and avoids submitting two assurance systems. The alternative's passing matrix is useful evidence for that alternative; it does not establish adoption or make its implementation interchangeable with #628. No code, scenarios or check results were copied between alternatives.

## Measured branch preparation

The collector fetched current upstream `harness` and `main`, created a disposable local `contrib/score-2850-native-mvp` branch on `4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9`, applied the adapter with `git apply --index`, and passed `git diff --cached --check`. The original **185** implementation files still match the measured candidate exactly. The current patch contains **191** files after six baseline files received license comments. All **394** tracked files match the current archive-plus-patch source vector, and **nine** fixed contracts are unchanged; there are no unstaged tracked changes. The [license follow-up](license-audit/README.md) proves the comment-only delta and records the complete native header check. The staged tree is `7b063703ca3a524d14a29a412ba8c2c08eaf82c8`. No commit, sign-off, push or PR was created.

The patch's direct application to current main `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16` was rejected because the selected patch targets draft-only harness files. That expected compatibility failure is retained in [commands](evidence/commands.json) and [main applicability](evidence/direct-main-application.json); it is not a native test failure.

The recorded native test evidence predates the six baseline license-comment insertions. The 185 implementation files remain unchanged; no runtime tests were rerun for the comment-only follow-up. Current copyright/syntax/comment-insertion/patch checks are separately measured. See [complete source identity](evidence/binding-validation.json), [source binding](evidence/candidate-tree.json) and the original [native verification](../native-adapter/verification.md).

## Upstream prerequisite and final target

At [retrieval time](evidence/retrieval.json), [#628](https://github.com/eclipse-score/docs-as-code/pull/628) is open, draft and unmerged, with head `4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9`. The GitHub API reports `mergeable=false`, `mergeable_state=dirty` and `rebaseable=false`. This is a time-bound observation, not a permanent readiness decision. Main is `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16`. Both raw API responses are retained.

A draft PR may target `harness` for author/maintainer discussion. Before this contribution becomes ready for main: the #628 owner must resolve its integration with main; the selected work must be rebased/replayed onto the accepted resulting tree; all applicable native checks must run on that final revision; and impact/qualification, ECA/DCO, hosted CI and code-owner gates must be satisfied. Do not transfer the current test results to a changed base or claim #2850 closed before acceptance.

The independently maintained [main-based packet](../full-issue-fix-20261007/README.md) and its companion report are preserved and excluded from the parent hash scope. If maintainers explicitly reject #628 in favor of an independent design, revise this decision and verify the chosen alternative before changing the submission path. There is no automatic fallback to a second PR.
