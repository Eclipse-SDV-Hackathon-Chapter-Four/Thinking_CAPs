# Reproduce Communication #490

Use a disposable clone with the native Ubuntu 24.04 prerequisites from CONTRIBUTING.md. The following commands do not publish anything. Obtain baseline `c77751819b8885a902540dbef7f0fe25cf85d51c` from upstream and import the portable branch:

```bash
git fetch /absolute/path/to/communication/490/feature-490-mock-runtime-verified.bundle feature/490-mock-runtime-verified:refs/heads/feature/490-mock-runtime-verified
git checkout feature/490-mock-runtime-verified
git diff --check c77751819b8885a902540dbef7f0fe25cf85d51c HEAD
```

Alternatively create a branch at that baseline and run `git am /absolute/path/to/communication/490/communication-490.patch`. source-binding.json records a clean cached-index patch replay with the same final tree, plus bundle verification.

Selected native verification:

```bash
bazel test --config=linux_x64 --cache_test_results=no --test_output=errors \
  //score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock-tests \
  //score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock-doc-tests \
  //score/mw/com/impl/rust/com-api/com-api-runtime-mock:generated-interface-test \
  //score/mw/com/rust/score_com_concept:score_com_concept-test \
  //score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests \
  //score/mw/com/rust/score_com_concept:score_com_concept-macros-tests

bazel build --config=clippy \
  //score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock \
  //score/mw/com/rust/score_com_concept:score_com_concept

```

Use --config=clippy exactly once and do not add the same aspect explicitly. MODULE.bazel/lock and .bazelrc select native dependencies/toolchains; do not add Cargo scaffolding or upgrade them. The mock generated-interface target is explicitly selected, and the native manual macro doc-test target is explicitly selected when applicable. Inspect raw logs for individual ignored cases.

Raw original environment commands (bubblewrap, measured Noble library overlay and owned Bazel roots) are in checks/*/result.json. execution/run_check.py is the captured collector, requiring the recorded score_sw_fabric.storage module and original validated run-root layout; it is provenance, not a turnkey script for another host. Standard native commands above are the portable reproduction route. Imported runtime/tool binary path/hash records are retained, but large tool binaries/caches are not distributed.

Before merge, run the full repository and all official required CI configurations. Local reproduction does not create server-side status checks or human approvals. See merge-readiness.md.
