# Reproduce Communication #781

Use a disposable clone with the native Ubuntu 24.04 prerequisites from CONTRIBUTING.md. The following commands do not publish anything. Obtain baseline `c77751819b8885a902540dbef7f0fe25cf85d51c` from upstream and import the portable branch:

```bash
git fetch /absolute/path/to/communication/781/feature-781-method-in-arg-ptr-ownership.bundle feature/781-method-in-arg-ptr-ownership:refs/heads/feature/781-method-in-arg-ptr-ownership
git checkout feature/781-method-in-arg-ptr-ownership
git diff --check c77751819b8885a902540dbef7f0fe25cf85d51c HEAD
```

Alternatively create a branch at that baseline and run `git am /absolute/path/to/communication/781/communication-781.patch`. source-binding.json records a clean cached-index patch replay with the same final tree, plus bundle verification.

Selected native verification:

```bash
bazel test --config=linux_x64 --cache_test_results=no --test_output=errors \
  //score/mw/com/impl/plumbing/rust:method_in_arg_ptr_test_rs \
  //score/mw/com/impl/plumbing/rust:method_in_arg_ptr_doc_test \
  //score/mw/com/impl/plumbing/rust:sample_ptr_test_rs \
  //score/mw/com/impl/plumbing/rust:sample_allocatee_ptr_test_rs \
  //score/mw/com/impl/methods:method_signature_element_ptr_test

bazel build --config=clippy \
  //score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs \
  //score/mw/com/impl/plumbing/rust/test_support:test_helper_size_ffi_rs

```

Use --config=clippy exactly once and do not add the same aspect explicitly. MODULE.bazel/lock and .bazelrc select native dependencies/toolchains; do not add Cargo scaffolding or upgrade them. The mock generated-interface target is explicitly selected, and the native manual macro doc-test target is explicitly selected when applicable. Inspect raw logs for individual ignored cases.

Raw original environment commands (bubblewrap, measured Noble library overlay and owned Bazel roots) are in checks/*/result.json. execution/run_check.py is the captured collector, requiring the recorded score_sw_fabric.storage module and original validated run-root layout; it is provenance, not a turnkey script for another host. Standard native commands above are the portable reproduction route. Imported runtime/tool binary path/hash records are retained, but large tool binaries/caches are not distributed.

Before merge, run the full repository and all official required CI configurations. Local reproduction does not create server-side status checks or human approvals. See merge-readiness.md.
