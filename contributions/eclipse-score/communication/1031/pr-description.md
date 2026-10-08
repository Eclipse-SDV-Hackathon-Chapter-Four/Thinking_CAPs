# Draft: Expose the Communication AoU target to external consumers

Publish an alias for the existing AoU target, preserve its underlying native providers and safety-analysis dependency, update the public-target golden file, and document pinned tooling forwarding semantics. Test a component requirement derived from the existing AoU. Actual Config Management production integration and FMEA/LOBSTER non-duplication remain pending cross-repository review.

Related issue: https://github.com/eclipse-score/communication/issues/1031

Each exported patch also includes the documented common root BUILD correction: pass filesystem names BUILD and MODULE.bazel to the copyright checker rather than Bazel labels. This enables the scanner without changing its policy; it still reports existing debt.

Original Flash output is preserved in correction-response.txt. The canonical hunks, source-backed integration repairs, native formatting and bounded repair attempts have separate records; the final communication patch is cumulative.

Native source baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Final execution: `01M49EMYET5T45EG92X8BQ6HF2`. Engineering acceptance: pending offline review. No issue closure is claimed.

## Validation

- aou-target: exit 0
- visibility: exit 0
- external-consumer-lock: exit 0
- external-aou-trlc-validation: exit 0
- copyright: exit 1
- format: exit 0
- build-all: exit 0
- test-all: exit 0

The isolated external module checks visibility/provider and TRLC resolution only; it is not the production Config Management integration.

Copyright/format/build/test failures are retained in `verify-result.json` and full `evidence/` logs. Before submission, a reviewer must resolve remaining failures, verify contributor/commit identity and accept the engineering/API decisions outside Fabro.

## Artifacts

Patch: `communication-1031.patch`. Changed source, exact commands, source hashes, logs, native test products and analyzer products are stored in this folder. Full databases and original source/licenses are in the recovery directory. These artifacts do not grant publishing authority.
