# Reproduce native checks

Use a disposable checkout of `eclipse-score/inc_someip_gateway` at
`f8a196c3b16d5172d898394ab99b0ed81346d63d`, then apply
`submission-with-dco.patch` with `git am`. Its source tree must match
`candidate-source-hashes.json` and `evidence/patch-verification.json`.
Follow the native README/devcontainer instructions and Bazel 8.6.0 pin.
Do not change the native lockfile, CI, lint configuration or tool launcher.

The portable native commands are:

```sh
pre-commit run --all-files
bazel test //:format.check
bazel build //...
bazel test //... --build_tests_only --nocache_test_results
bazel test //score/socom/test/unit:socom_test --features=asan --features=lsan --features=ubsan_clang --nocache_test_results
bazel test //score/socom/test/unit:socom_test --features=tsan --nocache_test_results
bazel test --config=clang-tidy //score/socom/... --nocache_test_results
bazel test //:unit_tests //:component_tests
bazel run //:docs
bazel run //:traceability_gate -- --metrics-json "$PWD/_build/metrics.json" --need-type=comp_req
bazel test --config=qemu-integration //quality/... //tests/integration_test/... --nocache_test_results
```

Each archived command additionally uses two jobs and task-private caches/temporary
paths. Exact argv, environment overrides, source hashes and tool binaries/versions
are recorded in `evidence/`. Replace machine-specific scratch paths with private
paths for a new run; do not treat an old cache result as a new measurement.
The archived collector scripts include this machine's managed-storage validation;
the native commands above can be run without Fabro or those collector scripts.

QEMU requires the native host tools and permissions documented by
`native-policy/.github/workflows/build_and_test_host.yml`. This local attempt
installed cloud-image-utils and genisoimage into task-private storage and passed
their path through explicit action/test environment flags. It preserved the
sandbox and all native check definitions. Four capture targets failed on the
host tcpdump credential change; a successful full integration run remains needed.
Do not disable capture tests or remove sandboxing to relabel the run as passing.

Formal trace coverage and the full sanitizer/platform/coverage/analyzer matrices
remain subject to `CI-applicability.md` and actual upstream reviewer decisions.
