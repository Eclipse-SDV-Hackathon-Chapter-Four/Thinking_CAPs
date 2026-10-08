# Reproduce and review

Offline integrity check (Python standard library only):

```bash
python3 contributions/eclipse-score/score/2850/full-issue-fix-20261007/verify.py
```

`source/baseline.tar.gz` contains the original native source, `source/current.tar.gz` contains the proposed source, and `source/native.patch` is the complete patch. Their file/hash vectors travel with them. The verifier executes no candidate, source archive or network call. It checks packet integrity, fixed-contract preservation, native XML receipts, expected outcomes, trace/raw-output bindings, and source provenance.

Native reproduction uses the repository's supported environment and pinned Bazel version. Apply the patch to `eclipse-score/docs-as-code` at `102aad30bd373295d275722c3942b392a8eb7149`, then run:

```bash
pre-commit run --all-files
bazel test --lockfile_mode=error --@rules_python//python/config_settings:python_version=3.12 //... --build_tests_only
bazel test --lockfile_mode=error --@rules_python//python/config_settings:python_version=3.14 //... --build_tests_only
bazel build --lockfile_mode=error --@rules_python//python/config_settings:python_version=3.12 //... -- -//src/tests/...
bazel build --lockfile_mode=error --@rules_python//python/config_settings:python_version=3.14 //... -- -//src/tests/...
bazel run //assurance:evaluate -- --validate-only
bazel run //assurance:evaluate -- --output runs/001/baseline
bazel run //assurance:evaluate -- --split heldout --output runs/002/baseline
bazel run //assurance:query -- --store runs --failed
bazel run //:docs
```

Use a new output iteration for every evaluation; existing directories are rejected. The native CI repeats both baseline evaluations on Python 3.12 and 3.14 and uploads trace stores. Each cohort contains expected gate failures that must be detected; evaluate success by matching declared verdicts and impacted IDs, rather than expecting every gate to pass.

The patch also applies cleanly to the later observed main `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16`. That is an application-compatibility check, with no full-test result transferred to that newer source tree. Final PR CI must use the actual submitted revision.

The recorded collector used an isolated writable SSD-backed native checkout inside the identified Docker image, with task-scoped caches. Commands, times, source vectors, tool identities, raw logs and native XML are under `evidence/checks/`. Local machine paths in those receipts are provenance, not a requirement for offline packet review.
