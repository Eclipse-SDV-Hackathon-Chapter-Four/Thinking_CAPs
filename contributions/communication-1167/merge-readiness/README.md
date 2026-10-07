# PR #1335 issue coverage and merge readiness — 2026-10-07

<!-- latest-non-qnx-follow-up -->
This audit is the retained 14:20 snapshot. The [final non-QNX follow-up](../non-qnx-verification/README.md) now supplies all six passing fork jobs and final-source evidence; native workflow approval and upstream acceptance remain pending. Raw historical gate records below are preserved.


The contribution implements the requested dedicated integration test for all five APIs within the reviewed observable-state interpretation. Complete closure is subject to maintainer assessment of that interpretation and the required verification. **The PR is not merge-ready:** GitHub reports `BLOCKED` and `REVIEW_REQUIRED`; the Host workflow reports `action_required` and has produced zero jobs. The measured local results are useful carried evidence, but do not supply the missing upstream checks.

Subject: [PR #1335](https://github.com/eclipse-score/communication/pull/1335), head `a8e81c795b7f45e663d608a33c5e358cfd765ea9`, base `c77751819b8885a902540dbef7f0fe25cf85d51c`. The published commit still has measured tree `1d790b6182be2fed1794bb287f8f9a868bde685f`. Raw snapshots and exact upstream source bindings are in this directory. [Machine assessment](audit-result.json) and [required-check inventory](required-checks.csv) preserve the audit time and states.

## Issue coverage

The [issue](https://github.com/eclipse-score/communication/issues/1167) requests one dedicated integration test for repeated OfferService, StopOfferService, StartFindService, Subscribe and Unsubscribe calls. It requests a test addition rather than an identified production defect repair.

| API | Implemented check | Assessment |
| --- | --- | --- |
| OfferService | Both results succeed; one configured service is discovered after the first offer; duplicate offer preserves its full discovered container. | Scoped observable-state coverage present. |
| StopOfferService | Absence checked after each stop, followed by successful re-offer and final cleanup. | Scoped observable-state and recovery coverage present. |
| StartFindService | Same callback and instance specifier used three times; every returned operation discovers the original service container; all operations are stopped. | Consistent with native distinct-operation handles and shared-watch behavior. Maintainers must agree this is the intended state-invariance interpretation. |
| Subscribe | Identical sample limit, subscribed state before/after duplicate, exact sample delivery and later resubscription. | Operational coverage present. Samples are sent after the duplicate, so survival of already queued unread samples is not independently demonstrated. |
| Unsubscribe | Repeated calls each produce kNotSubscribed from GetNewSamples; resubscription and exact second sample sequence succeed. | Scoped observable-state and recovery coverage present. |

The test has finite waits and requires application exit zero. It covers one QM shared-memory fixture; it does not establish exhaustive idempotence across every configuration, timing or internal resource invariant. The queued-sample observation above is a test-scope limitation, not evidence of a production defect or a separately stated issue requirement. [Technical review](../final-review/TECHNICAL-REVIEW.md) and [reviewer decision](../submission/HUMAN-DISPOSITION.md) record the adopted scope. The [published source](https://github.com/eclipse-score/communication/blob/a8e81c795b7f45e663d608a33c5e358cfd765ea9/score/mw/com/test/api_idempotency/main_api_idempotency.cpp) and native BUILD/Python/configuration files are in the PR.

## Required merge gates and current results

The active [main ruleset](https://github.com/eclipse-score/communication/rules/3981496) requires these nine status contexts. Their current observed states are:

| Required context | Observed result |
| --- | --- |
| eclipsefdn/eca | Success |
| GCC15 / Build & Test | Not reported |
| QCC - Build & Test | Completed, skipped |
| Address & Undefined Behavior Sanitizer / Build & Test | Not reported |
| Thread Sanitizer / Build & Test | Not reported |
| Linters / clang-tidy | Not reported |
| Linters / clippy | Not reported |
| Linters / ruff | Not reported |
| review-checklists | Success |

The same ruleset requires at least one approving review and code-owner review, dismisses stale approvals after pushes, and requires a merge queue. There are no submitted reviews in the captured snapshot. [CODEOWNERS](upstream/.github/CODEOWNERS) lists six default owners; review requests are already present in the PR. Jefferson’s recorded contributor assessment does not satisfy a required GitHub code-owner approval.

The [Host workflow run](https://github.com/eclipse-score/communication/actions/runs/37633683021) directly reports `action_required`; [job inventory](host-jobs.json) contains zero jobs. Fork workflow approval is the supported next step, inferred from that state and the [GitHub fork-run approval procedure](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks). A maintainer with write access can approve workflows to run. The documentation workflow also reports `action_required`; it is not a separate required context in the observed ruleset.

The [QNX workflow](upstream/.github/workflows/build_and_test_qnx.yml) deliberately skips fork PR execution unless the `test-qnx` label is present, then requires its workflow-approval environment. That label is absent here. A skipped result provides no QNX build/runtime evidence; it is not a reported test failure. The workflow also runs on merge-group events. Maintainers should decide whether to request the labeled pre-merge run and ensure applicable merge-queue checks complete. Do not equate the workflow’s successful precheck with successful QNX tests.

## Artifact inventory

| Work product or evidence | What is available | What remains |
| --- | --- | --- |
| Native patch and fixtures | Nine PR files: eight new native test/configuration/BUILD files and the root checker-path utility correction. Published tree equals measured tree. | Maintainer source review, including discovery interpretation and utility scope. |
| PR title, description and issue reference | Published; title/body and changed paths independently verified. | No missing PR template: none exists in the inspected complete base file index. |
| ECA | Official strict author/committer validation passed; actual GitHub eclipsefdn/eca status is success. | No current ECA gate gap. |
| Build, format and baseline tests | [Portable evidence](../acceptance-review/evidence-verification.json), full native logs/XML and source/control/product bindings. Build, format, focused tests 2/2, suite 503 passed/6 skipped on the pinned older baseline. | These are carried results, not the newer PR merge subject’s required CI results. |
| GCC15 CI and module integration | Native workflow exists; [GCC15 workflow](upstream/.github/workflows/_build_and_test_gcc15.yml) builds/tests root targets and separately builds module_integration_test. | Required upstream result is absent. The five local commands do not provide separate module_integration_test build evidence. |
| Sanitizers | Native ASan/UBSan/leak and TSan workflows/configurations are defined. | Required upstream sanitizer results absent; no equivalent local measured sanitizer evidence in this packet. |
| Static analysis | [Linter workflow](upstream/.github/workflows/_linter.yml) defines clang-tidy, clippy and Ruff jobs, raw logs, SARIF and findings artifacts. | All three required results absent. Formatting success is not static-analysis success. CI normally generates these reports after execution; separate hand-authored uploads are not prescribed. |
| Review checklists | Current native configuration is `checklists: []`; published review-checklists status succeeds. | Required code-owner review is still missing. No active checklist-specific document/acknowledgment is outstanding in this configuration. |
| Copyright | [204-file inventory](../acceptance-review/copyright-findings.csv), identical baseline/candidate raw messages, separate utility patch and accepted inherited-repair scope. | Checker remains exit 1, with no maintainer waiver/remediation. Copyright is documented by CONTRIBUTING, but is not its own required status context in the observed ruleset; do not claim it automatically blocks GitHub merge or that personal acceptance makes it pass. |
| Additional engineering work products | Technical review, source/command bindings, human disposition, source archive and native/OCI products are retained locally. | The inspected native contribution guide does not demand a separate Spec Kit spec/plan/tasks or a generic safety-document package for this test-only PR. Local fabric records are evidence, rather than additional native GitHub gates. |

Sources: exact pinned [CONTRIBUTING](upstream/CONTRIBUTING.md), [CI design](upstream/CI.md), [workflow files](source-bindings.json), [active branch rules](branch-rules.json), [PR/review state](pull-request-rollup.json) and [repository file index](repository-file-index.json). The old code-inspection pointer refers to a checklist directory absent from the inspected base; the active automated checklist configuration and successful status are recorded separately. Classic branch protection returned 404; the active ruleset was retrieved directly and supplies the requirements above.

## Concrete next steps

1. A maintainer approves the fork Host workflow to run, and the required GCC15, sanitizer and linter jobs complete. Address any new findings on their actual subject; preserve inherited findings explicitly.
2. A code owner reviews the patch and approves it if the issue interpretation, fixture scope and checker utility are acceptable. They also determine handling of the inherited copyright failure and whether additional QNX evidence is needed before queueing.
3. After required checks and approvals are satisfied, a maintainer uses the repository’s merge queue and verifies its merge-group checks. No merge or issue closure was performed by this audit.

This assessment made no source edits, native runs, paid calls, PR comments or remote changes. It answers readiness from current visible project requirements and measured evidence, while preserving maintainer authority.
