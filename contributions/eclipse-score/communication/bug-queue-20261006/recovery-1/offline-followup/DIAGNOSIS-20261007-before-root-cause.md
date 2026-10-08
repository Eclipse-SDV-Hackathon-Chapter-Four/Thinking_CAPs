# Offline diagnosis — 2026-10-07

Bound record: [diagnosis-20261007.json](diagnosis-20261007.json). No source change, native Fabro run, paid call or acceptance. Candidate trees were inspected read-only.

## #1104 — extraction failure explained

- The failing action is the dev-only `cc_build_error_test` at `score/mw/com/impl/util/test/BUILD:57`. `rules_build_error` 0.11.0 runs `bash -c '"$@"' '' try_build.bash …`. The script has no shebang and starts with `set -euo pipefail`.
- In the pinned devcontainer image `/bin/sh` is dash. A minimal repro with pinned CodeQL 2.21.4 ([repro](1104-tracer-shell-repro-20261007/)) shows the difference. Without tracing, bash interprets the script and exits 0. Under the tracer, dash interprets it and exits 2 with the identical `set: Illegal option -o pipefail`.
- It occurs only when the traced target set contains `cc_build_error_test` targets: two under `//score/mw/com/impl/...`, which is #1104's own reproduction pattern. The nightly-shaped `//score/message_passing //score/mw/com` projection succeeded (exit 0).
- Consequence: #1104's reported `file:/` locations have **not** been reproduced on the pristine baseline. Evidence that the fix removes them is still missing.

Proposals (none applied; each needs separate authority):
1. Upstream `rules_build_error`: add `#!/usr/bin/env bash` to `try_build.bash`, `check_each_message.bash` and `check_emptiness.bash`, or invoke them with `bash`. This is an external project with its own LICENSE (preserved in `1104-native-dependency/`).
2. communication: trace only production targets. #751's `--production-targets` already excludes tests, so this needs coordination with the #751 patch.
3. Measurement-only (unverified syntax): rerun the pristine-baseline create/analyze with `--target "-- //score/mw/com/impl/... -//score/mw/com/impl/util/test:arithmetic_utils_addition_build_error_test -//score/mw/com/impl/util/test:arithmetic_utils_multiplication_build_error_test"`. This would produce the baseline SARIF needed to check for `file:/` URIs. It is a fresh native run with zero model cost and needs your go-ahead.

## #751 — 1,659 → 1,658 archive delta explained

- The old database directory was initialized twice: first by the failed repair-2 attempt (16:49), then by the measured run (18:39, same command). `build-tracer.log` spans both sessions.
- `score_baselibs+/…/thread_local_guard.cpp` was compiled only at 16:56, in the failed session. Neither measured session (old 18:39, new 21:03) compiled it, although both compiled the other `mw/log/detail/*.cpp` sources. The old finalize imported the 16:56 TRAP tarball. Scanned TRAP totals differ by 3 (187,655 vs 187,652).
- Conclusion: the delta is leftover data in the old archive, not a source the latest candidate lost. Still unproven: why the failed session compiled that file, whether production closure should include it, and complete external dependency coverage.

Unchanged open items: #751 full query-analysis/SARIF phase and QNX unmeasured; copyright failure (204 baseline-identical subjects) not waived; #1236 27 baseline-identical buildifier warnings; #1031 production integration unmeasured; contributor identity/ECA and human acceptance pending.
