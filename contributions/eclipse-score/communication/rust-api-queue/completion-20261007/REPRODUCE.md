# Reproduce and review

Run `python3 verify.py` to verify every retained packet file and changed source byte. This verifies artifact integrity only.

The full Git bundle contains the candidate branch and its baseline history. On an offline machine:

```sh
git clone communication-integrated.bundle communication-review
cd communication-review
git checkout feature/rust-discovery-subscription-complete
git diff cef680454e8586daca9f953084dca33fb3759d0c HEAD
```

The baseline-bound `communication-integrated.patch` and the changed files under `source/` are alternative review inputs. `source-identity.json` records the exact baseline, candidate, patch and file identities. The source archive provides the complete candidate tree without Git. Neither changing files nor rebasing preserves applicability of the recorded checks automatically.

Native checks require the project's toolchain/dependency downloads or populated native caches, Docker, and the supported host setup from the preserved CONTRIBUTING/CI sources. Use the recorded .bazelversion, MODULE and lock, compiler and policy pins. This packet supplies source and evidence for offline review; it does not carry every build dependency or create a qualified build environment.

The expected-check inventory and each `native-result.json` preserve exact commands, configurations, environment, exit status, timings and raw-log hashes. The local collector used a disposable clone, a storage-bound external Linux run, a private rootless Docker daemon and read-only Ubuntu library overlays. Its host-specific namespace paths are evidence of execution, not a portable setup command. On the project's Ubuntu host, invoke the corresponding native Bazel commands directly after the documented setup. The collector scripts and tool/storage identities are retained for inspection.

The protected host workflow requires `bazel build --config=ci //...`, `bazel test --config=ci //... --build_tests_only`, and the nested module integration build/dependency check. Sanitizer and analyzer configurations come from the preserved native workflow files. Explicit manual Rust macro/doctest targets and strict cfg(test) analysis are recorded separately. The original serial production targets are run with one local test job to avoid shared test resources.

QCC needs the project's licensed QNX environment. Official protected statuses, merge-group execution, reviewer checklists, code-owner approval, ECA validation and IP clearance must refer to the submitted final head. The supplied PR and IP documents are drafts for those actions; none has been published by this local task.
