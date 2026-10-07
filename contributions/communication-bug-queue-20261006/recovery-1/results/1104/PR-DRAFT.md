# Draft: Preserve unknown CodeQL locations without invalid file-root URIs

Some native SARIF related locations contain file:/ and a reordered artifact table contains a stale location index. Keep the complete raw report, remove invalid placeholder physical locations and artifact locations, and retain messages, IDs and explicit unknown-location metadata. Preserve valid paths. This is a bounded normalization workaround; it cannot reconstruct a file path that the analyzer did not provide.

Related issue: https://github.com/eclipse-score/communication/issues/1104

Each exported patch also includes the documented common root BUILD correction: pass filesystem names BUILD and MODULE.bazel to the copyright checker rather than Bazel labels. This enables the scanner without changing its policy; it still reports existing debt.

Original Flash output is preserved in correction-response.txt. The canonical hunks, source-backed integration repairs, native formatting and bounded repair attempts have separate records; the final communication patch is cumulative.

Native source baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Final execution: `01M49EMYET5T45EG92X8BQ6HF2`. Engineering acceptance: pending offline review. No issue closure is claimed.

## Validation

- analysis-regressions: exit 0
- codeql-create-nightly-projection: exit 0
- codeql-analyze: exit 0
- format: exit 0
- codeql-create: exit 1
- copyright: exit 1
- build-all: exit 0
- test-all: exit 0
- fresh-native-sarif-preservation-and-schema: exit 0

Exact impl/... extraction failure remains a failed check. The nightly projection is supplemental evidence. Lost analyzer paths remain unknown.

Copyright/format/build/test failures are retained in `verify-result.json` and full `evidence/` logs. Before submission, a reviewer must resolve remaining failures, verify contributor/commit identity and accept the engineering/API decisions outside Fabro.

## Artifacts

Patch: `communication-1104.patch`. Changed source, exact commands, source hashes, logs, native test products and analyzer products are stored in this folder. Full databases and original source/licenses are in the recovery directory. These artifacts do not grant publishing authority.

Fresh full build and tests pass (502 passed,6 skipped); supplemental SARIF preserves1625 findings with0 schema errors/placeholders. Completed analyzer evidence is explicitly carried with source/Git/log hashes. Exact impl extraction remains failed and lost paths remain unknown.
