# Draft: Enforce buildifier lint diagnostics in host CI

The formatting check did not reject unused Starlark loads. Add a buildifier lint runner using the pinned native tool, fail on emitted diagnostics, and invoke it in host CI. Native positive/negative fixtures exercise a clean BUILD and an unused loaded symbol. Existing repository lint debt remains visible.

Related issue: https://github.com/eclipse-score/communication/issues/1236

Each exported patch also includes the documented common root BUILD correction: pass filesystem names BUILD and MODULE.bazel to the copyright checker rather than Bazel labels. This enables the scanner without changing its policy; it still reports existing debt.

Original Flash output is preserved in correction-response.txt. The canonical hunks, source-backed integration repairs, native formatting and bounded repair attempts have separate records; the final communication patch is cumulative.

Native source baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Final execution: `01M49EMYET5T45EG92X8BQ6HF2`. Engineering acceptance: pending offline review. No issue closure is claimed.

## Validation

- buildifier-regression: exit 0
- buildifier-target-discovery: exit 0
- buildifier-enforcement-0: exit 1
- copyright: exit 1
- format: exit 0
- build-all: exit 0
- test-all: exit 0

Existing global buildifier lint findings are not waived or silently corrected.

Copyright/format/build/test failures are retained in `verify-result.json` and full `evidence/` logs. Before submission, a reviewer must resolve remaining failures, verify contributor/commit identity and accept the engineering/API decisions outside Fabro.

## Artifacts

Patch: `communication-1236.patch`. Changed source, exact commands, source hashes, logs, native test products and analyzer products are stored in this folder. Full databases and original source/licenses are in the recovery directory. These artifacts do not grant publishing authority.
