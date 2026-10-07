# Communication #1167 — additional Host verification

User authority: “go for the missing points, instead qnx which is skipped”. QNX remains excluded. [Upstream PR #1335](https://github.com/eclipse-score/communication/pull/1335) remains open; no merge or release is authorized.

The six missing Host checks are being executed using the unchanged native GitHub workflows in the contributor-owned fork. [Verification run](https://github.com/jnsagai/communication/actions/runs/37637574398) uses a real pull-request event, so all three linters use the project's `hold-the-line` strategy. This is measured fork evidence; it does not create or satisfy the upstream PR's required GitHub statuses.

The subject includes the newer upstream production code: base `c77751819b8885a902540dbef7f0fe25cf85d51c`, contribution head `a8e81c795b7f45e663d608a33c5e358cfd765ea9`, native proposed merge `0b48ccc1d195297ab9c5e7e19f5b2250fd2f43fe`. The fork runner checks out `20c2ab9ee7db6324de698015e3d8f2faa98e3cec`, independently verified to have the same source tree `9d2fa9bfc72bde6ae239e68baa559b99feb45741`. [Full source binding](subject.json) covers 2,940 tracked files and the nine contribution paths. [Execution plan](execution-plan.json) binds commands and 16 native controls. No source, workflow, toolchain or lint-policy changes were made.

The latest [job summary](runs/37637574398/1/summary.json) records current states. At this stage Ruff and clippy have passed; GCC15, clang-tidy, ASan/UBSan/leak and TSan are running. Terminal logs and native report artifacts will be exported before declaring these checks complete. The GCC15 workflow also builds the separate `module_integration_test` workspace.

## Copyright comparison

A fresh read-only comparison on the newer baseline and merge subject reports **204 identical normalized findings, zero additions or removals; both checks exit 1**. [Comparison](copyright/comparison.json), separate baseline/candidate logs and the two-string baseline checker-path overlay are retained under `copyright/`.

This executes the pinned `score_tooling` 2.3.1 Python checker directly using its already built Bazel Python 3.12/rapidfuzz runtime. It is explicitly supplemental direct-tool execution, rather than a fresh `bazel run` claim. New workspace storage was validated; the complete candidate source vector was verified before and after execution. No repair or waiver is recorded. The original measured-scope human decision and the separate inherited-header repair disposition remain unchanged.

## Remaining upstream actions

The native Host run [37633683021](https://github.com/eclipse-score/communication/actions/runs/37633683021) remains `action_required`, with no jobs. Maintainers must approve it so GitHub can supply the required upstream statuses. The authenticated contributor account lacks upstream write permission. Required code-owner approval, copyright handling and merge-queue entry remain maintainer decisions; the existing code-owner review requests are already present. No additional messages or comments were sent to reviewers.

The temporary [fork verification PR #1](https://github.com/jnsagai/communication/pull/1) is a draft used only to invoke the native workflow. Scheduled, QNX and unrelated workflows are disabled in the fork. Its Actions permission policy was restored to its original enabled/all state after workflow registration. [Registration](fork-actions-registration.json) and [workflow selection](fork-workflow-selection.json) preserve that setup. The original paid supervisor remains exhausted and untouched; no provider-model calls were added.

## Collection

Run `python3 collect_run.py 37637574398` from this directory for a status snapshot. Once terminal, run `python3 collect_run.py 37637574398 --final` once to retain all six raw job logs, native report artifacts, checkout validation, module-integration result, test summaries and file digests. Final evidence must retain failures rather than replace them with successful retries. Source drift requires a new subject binding and verification run.
