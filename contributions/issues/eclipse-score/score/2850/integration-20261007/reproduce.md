# Prepare the selected branch

The already prepared disposable checkout is `/tmp/score-2850-integration-gnmi8weg/native`. Branch `contrib/score-2850-native-mvp` contains a staged patch on #628's `4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9`. It has no new commit, attributed identity or sign-off. Temporary paths are provenance, not a portability requirement.

To reproduce in a new disposable checkout, set `score_packet` to the absolute path of the native-adapter packet, then run:

```bash
git clone --no-checkout https://github.com/eclipse-score/docs-as-code.git
cd docs-as-code
git fetch origin harness
git rev-parse origin/harness
# Verify the head matches the measured revision before carrying any evidence:
git checkout -b contrib/score-2850-native-mvp 4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9
git apply --check "$score_packet/patches/0001-score-2850-assurance-harness.patch"
git apply --index "$score_packet/patches/0001-score-2850-assurance-harness.patch"
git diff --cached --check
git write-tree
```

Expected staged tree: `7b063703ca3a524d14a29a412ba8c2c08eaf82c8`. If upstream head changed, reassess/rebase instead of describing stale measured code as current. Review the diff and use your actual contributor identity/ECA and DCO sign-off when creating commits. Publication needs separate authorization.

Initial draft PR base: **`eclipse-score/docs-as-code:harness`**. Use [this PR body](pr-description.md), the [native title](../native-adapter/pr-title.txt) and [native impact artifacts](../native-adapter/impact-analysis.md). Link #628 as a dependency; the source-only PR diff must be the selected adapter patch. The large offline packet is review evidence, not native production source.

After #628 is accepted/integrated with main, rebase onto the accepted tree, retarget to main as agreed, resolve conflicts and rerun the [native checks](../native-adapter/reproduce.md). Final hosted CI, baseline typing disposition, impact/qualification, ECA/DCO and code-owner approval are pending. No current measurement is transferred to a different tree.

Offline packet integrity:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 contributions/issues/eclipse-score/score/2850/native-adapter/verify_native_packet.py
PYTHONDONTWRITEBYTECODE=1 python3 contributions/issues/eclipse-score/score/2850/verify_packet.py
```

The [license follow-up](license-audit/README.md) is included in the current patch and source bindings. The original runtime test evidence predates its six proven comment-only native edits; current copyright/syntax/patch checks are separate.

The parent manifest binds this integration decision/evidence and the selected adapter packet. It excludes the independently maintained alternative and companion report. Integrity does not rerun native tests or grant engineering acceptance.
