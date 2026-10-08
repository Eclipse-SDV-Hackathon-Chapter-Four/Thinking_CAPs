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

## #1104 — exact-scope reproduction and root cause (added later 2026-10-07)

Evidence: [1104-root-cause-20261007/](1104-root-cause-20261007/) (SHA256SUMS), `../evidence4-results/`, [storage incident](storage-incident-20261007.json).

- **Exact-scope baseline database:** built with `--target "-- //score/mw/com/impl/... -<2 build_error tests>"` on the unmodified baseline (`baseline-check`, commit 381d43d; only root BUILD scanner-input line differs). Exit 0.
- **Full native analysis is still incomplete.** Attempt 1 hit my script's 3600 s bound at 215/218 (exit 137). The rerun died on the Lexar USB disconnect (exit 135). Attempt 2, after reattachment to loop1, is running the last query, `RULE-8-7-1/PointerArithmeticFormsAnInvalidPointer`. Its recursive `srcSinkLengthMap` predicate passed 5.4 M iterations at this scope. All failure records are retained.
- **Supplemental exact-scope SARIF for the affected rule:** pinned CodeQL 2.21.4 `bqrs interpret` of the already-evaluated `RULE-6-9-1/TypeAliasesDeclaration.bqrs`, so the native `codeql_lint` post-processing was not applied. It has 501 results and **280 related locations with `file:/`** (221 `Result`), plus 0 primary placeholders. This reproduces the issue's snippet at its own scope.
- **Projection of the candidate #1104 normalizer** (method validated on nightly scope): 281 → 0 placeholders, 501 results preserved in order. All 281 become `score.artifactLocationUnavailable`, so **no location is restored**.
- **Root cause** (read-only queries on the finalized baseline nightly DB): the query selects `TypedefType t` as a `$@` link. For alias-template instances such as `score::Result<T>` (`expected<T, Error>`), the database has `TypedefType`s with **no `type_decls`/declaration entry and no location**: 88 `Result`, 1 `FindServiceHandler`, 1 `expected_blank`, 262 `iterator`. CodeQL serializes such link targets as `file:/`, line 0. The `.bqrs` already carries `file:/` for every `Result` link (80/80). The `TypedefType`s that do have locations (e.g. `score/result/result.h:34`) are never the ones linked.
- **Fix options (none applied; each needs authority):**
  1. Query-level fix in `cpp/misra/type-aliases-declaration`: link a located element, e.g. the alias declaration or the decl's type mention, or drop the link when `t` has no location. Upstream is github/codeql-coding-standards; communication already patches that pack via `third_party/codeql/codeql_coding_standards_misra.patch`. Exact QL is not yet drafted or verified.
  2. Current candidate: SARIF post-processing that removes the placeholders. The output is valid, but locations stay lost. Reviewers should decide whether that satisfies "uri should not be an empty path".
  3. Possibly report the extractor behaviour (no declaration entries for alias-template instances) upstream to CodeQL. That behaviour is not verified as a bug.
- **Side effects:** the read-only diagnosis queries add evaluation cache files to the nightly database's cache. No source, results or relations changed.
