# Communication #1167 — native PR open

Latest [merge-readiness audit](merge-readiness/README.md): GitHub reports `BLOCKED` and `REVIEW_REQUIRED`. The Host run reports `action_required` with zero jobs; six required host/sanitizer/linter status contexts are not reported. ECA and review-checklists succeed. QNX build/test is skipped. Source still matches the measured tree.

[PR #1335](https://github.com/eclipse-score/communication/pull/1335) is open against `eclipse-score/communication:main`. Published head: `a8e81c795b7f45e663d608a33c5e358cfd765ea9`; exact measured tree: `1d790b6182be2fed1794bb287f8f9a868bde685f`. The nine changed files, source hashes, PR title/body and remote head were verified. See [publication receipt](submission/publication/result.json) and [publication record](submission/publication/README.md).

Jefferson Nascimento, Software Engineer, explicitly accepted the prepared rationale and four measured-scope dispositions, then authorized PR creation with “I agree, lets create the PR”. [Human disposition](submission/HUMAN-DISPOSITION.md) and [decision origin](acceptance-review/human-decision.json) are recorded. This is contributor engineering acceptance for the bound measured scope; upstream maintainer acceptance remains outstanding.

The official strict Eclipse ECA API passed for the actual publication commit, its author and committer. No agreement signature or Signed-off-by declaration was added. Account evidence and actual commit validation are preserved under `submission/publication/`. The original hackathon branch push is separate historical publication evidence.

Carried native run `01M4878Q65ENC6PJ5AEJ6NMWB3` passed build, formatting, focused tests 2/2 and all 503 executed suite tests; six skipped. Copyright remains exit 1 with 204 baseline-identical findings, zero additions/removals: 96 missing, 93 wrong-format, 14 preceded and one duplicate. Jefferson accepted classification and separate repair scope; no copyright waiver is claimed. [Evidence recheck](acceptance-review/evidence-verification.json) binds source, archive, patches, controls, logs and products. No new native run, paid call or supervisor retry occurred.

The patch applies cleanly to newer upstream `c77751819b8885a902540dbef7f0fe25cf85d51c`; current-main native execution was not performed locally. The PR explicitly limits native results to baseline `e3d126c2d7569345cf5f790310702eb00cd86b06`. At the captured CI check, precheck succeeded, Trigger apply stage was running, and QCC/approval checks were skipped; these are not fresh full-suite results.

A fresh independent publication checkout was allocated and storage-validated on the measured Linux volume now attached as loop4. Original native workspaces, logs, budgets and exhausted supervisor were preserved. Before future native work, validate its own saved storage binding. Dashboard availability was not remeasured.

Next action: a maintainer approves the fork Host workflow, the six unreported required checks execute, and a code owner reviews the patch. Maintainers determine copyright handling and QNX execution needs before the merge queue. No merge, release or issue closure occurred.
