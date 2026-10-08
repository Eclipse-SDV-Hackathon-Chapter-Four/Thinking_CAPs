# Reproduce

Check out baseline `f8a196c3b16d5172d898394ab99b0ed81346d63d` in a fresh clone.
Apply `submission.patch`, or `git am submission-with-dco.patch` for both signed
off commits. From the existing full f9d4694 revision, `requirement-mapping.patch`
applies only the mapping/header additions. Never apply both plain and mail patches.

Run native `pre-commit run --all-files`, `bazel test //:format.check`,
`bazel build //...`, `bazel test //score/socom/test/unit:socom_test`,
`bazel test --config=clang-tidy //score/socom/...`, `bazel run //:docs`,
then `bazel run //:traceability_gate -- --metrics-json "$PWD/_build/metrics.json"
--need-type=comp_req`. Exact task cache/output arguments, hashes and timings
are retained in evidence. The helper scripts use task-specific managed paths;
standard native commands do not require that local infrastructure.

