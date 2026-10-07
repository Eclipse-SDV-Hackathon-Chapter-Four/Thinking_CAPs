# Native reproduction

Start with the pinned revisions listed in README.md, apply each repository patch
once, and use the native Ubuntu 24.04 environment, Bazel 8.7.0, module locks and
toolchains. The container image digest and measured executable hashes are in
environment-binding.json. Exact executed commands, environment mounts, source
hashes, times, exit codes and complete logs are in evidence/*.json/stdout/stderr.
The local measurement helper requires this machine's scratch allocation; the
native commands below can be run directly from a correctly prepared checkout.

```bash
bazel build --config=ci //...
bazel test --config=ci //... --build_tests_only
bazel run //:format.check
bazel run //:copyright.check
bazel test //tools/lint/buildifier:buildifier_lint_test
bazel run //tools/lint/buildifier:buildifier_lint -- --recursive
bazel test //quality/static_analysis:codeql_lint_test
bazel test //quality/visibility_guard:visibility_guard_test
bazel test //score/mw/com/dependability/safety_analysis/aou_forwarding_test:component_requirements_test
```

Fresh production extraction and the native default suite/reporting:

```bash
bazel run //quality/static_analysis:codeql_lint -- \
  --phase create-database --database-path /absolute/new/production-db \
  --production-targets --target //score/message_passing //score/mw/com
bazel run //quality/static_analysis:codeql_lint -- \
  --phase analyze-database --database-path /absolute/new/production-db \
  --output-dir /absolute/new/analysis-output
```

Choose a new database path after any failed extraction; the contribution rejects
nonempty retries. The fixture for the interpreter correction traces these labels:

```bash
bazel run //quality/static_analysis:codeql_lint -- \
  --phase create-database --database-path /absolute/new/helper-db \
  --target //score/mw/com/impl:error \
  //score/mw/com/impl/util/test:arithmetic_utils_addition_build_error_test \
  //score/mw/com/impl/util/test:arithmetic_utils_multiplication_build_error_test
```

Verify module integration from its native subdirectory:

```bash
cd module_integration_test
bazel build //...
bazel mod deps --lockfile_mode=update
```

The companion provider and complete index checks use a real **module** override,
not `--override_repository=score_communication`, which selects the wrong
canonical repository in this graph. From the patched Config Management root:

```bash
bazel build --override_module=score_communication=/absolute/patched/communication \
  //requirements/component_requirements/config_provider:component_requirements
bazel test --override_module=score_communication=/absolute/patched/communication \
  //requirements/component_requirements/config_provider:component_requirements_test
bazel build --override_module=score_communication=/absolute/patched/communication \
  //score/config_management/dependability:config_management_index
```

The last command currently fails on native legacy/placeholder safety records.
Fixing the records requires the decisions documented in engineering-decisions.md.
Hosted sanitizer/aspect/platform jobs must use the repository workflow commands
and event conditions. The local process-wrapper sandbox is not evidence of the
project's required Linux sandbox environment; no host security setting was
modified to claim equivalence.

License-specific verification on the final checkouts:

```bash
bazel run //:copyright.check
codeql resolve metadata --format=json \
  quality/static_analysis/query_overrides/TypeAliasesDeclaration.ql
```

Use the pinned CodeQL 2.21.4 binary. The MIT notice shares the first query comment
with its original metadata. A fresh database avoids cached result metadata from
older query headers; preserved failed runs document the cache refresh used here.
The final same-database comparison and fresh production analysis are separate
checks: `license-final-location-comparison.json` and
`license-final-suite-summary.json`. Portable final database/source archives and
reports are retained under `evidence/license-final-*`.
