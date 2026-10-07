# Draft: Extract and audit production sources in the CodeQL nightly database

The baseline nightly extraction omitted proxy_binding_factory_impl.cpp. Select configured C/C++ targets with testonly=0 from the dependency closure of the supplied production roots, including implementation_deps, and build them under tracing; audit the finalized source archive for explicitly required production files. A SARIF finding is not required for a source to be included in the database.

Related issue: https://github.com/eclipse-score/communication/issues/751

Each exported patch also includes the documented common root BUILD correction: pass filesystem names BUILD and MODULE.bazel to the copyright checker rather than Bazel labels. This enables the scanner without changing its policy; it still reports existing debt.

Original Flash output is preserved in correction-response.txt. The canonical hunks, source-backed integration repairs, native formatting and bounded repair attempts have separate records; the final communication patch is cumulative.

Native source baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Final execution: `01M49EMYET5T45EG92X8BQ6HF2`. Engineering acceptance: pending offline review. No issue closure is claimed.

## Validation

- analysis-regressions: exit 3
- codeql-create: exit 0
- named-production-source-extracted: exit 0
- copyright: exit 1
- format: exit 0
- build-all: exit 0
- test-all: exit 3

Production coverage is proven only for the measured source/archive, not every possible target or platform.

Copyright/format/build/test failures are retained in `verify-result.json` and full `evidence/` logs. Before submission, a reviewer must resolve remaining failures, verify contributor/commit identity and accept the engineering/API decisions outside Fabro.

## Artifacts

Patch: `communication-751.patch`. Changed source, exact commands, source hashes, logs, native test products and analyzer products are stored in this folder. Full databases and original source/licenses are in the recovery directory. These artifacts do not grant publishing authority.

Remaining regression: `test_parse_production_targets_filters_external` expects the earlier order while the parser returns sorted deduplicated labels. 10 cases pass and this1 fails. No further source repair was made after the3/3 limit. See `../../phases/repair-3/751-regression-diagnosis.json`.
