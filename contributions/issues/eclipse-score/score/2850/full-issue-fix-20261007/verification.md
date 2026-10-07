# Measured verification

Bound source: docs-as-code `102aad30bd373295d275722c3942b392a8eb7149` plus the complete patch. Every final test/build receipt binds the exact 614-file exported source vector and confirms it stayed unchanged during the check. Native gate/schema/metamodel/metric-function and dependency/configuration pins are preserved.

| Configuration | Native tests | Native build | Actual CI runner baseline |
| --- | --- | --- | --- |
| Python 3.12 (3.12.12) | 494 passed, 1 explicitly skipped testcase; 26 targets, 0 failures | 99 targets | 30/30 search + 10/10 heldout |
| Python 3.14 (3.14.2) | 494 passed, 1 explicitly skipped testcase; 26 targets, 0 failures | 99 targets | 30/30 search + 10/10 heldout |

The complete pre-commit suite passed: JSON/YAML/hygiene, Bazel tidy/lock, actionlint, Ruff, BasedPyright and Eclipse copyright. A subsequent RST-only spacing correction passed document hooks and native documentation rendering with warnings treated as errors. The complete native matrix was then executed again. The [reuse map](evidence/reuse-map.json) limits earlier code/CI results to unchanged subjects; no stale whole-source result is presented as final.

Native `bazel run //assurance:evaluate` executed both corpus splits on both interpreter versions. Scores, input/source hashes, raw output bindings and role/environment provenance travel in [3.12 traces](evidence/native-runs-py312/) and [3.14 traces](evidence/native-runs-py314/). All 40 specified verdict/impact outcomes match. Twenty gate failures per complete cohort are expected regressions and are successfully detected; they are not failing harness tests. Metric, score, impact and gate artifact schemas are validated during execution.

Exact commands, Docker/tool identities, timestamps, complete stdout/stderr and native XML are under [checks](evidence/checks/). Earlier import/lint/runtime failures, omitted cycle-node expectations, and the RST warning remain visible. The [fixture corrections](evidence/corpus-corrections/corrections.json) explain graph-reachability expectations; native verdict expectations were not changed. These public cohorts establish neither hidden-benchmark performance nor real-agent/production-incident quality.

The final source/patch replay matches the exported tree at the bound baseline. The patch also applies cleanly to later observed main `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16`; full tests are not transferred to that different tree. The [check inventory](expected-checks.json) records applicability, omissions and pending project gates. Submitted-revision CI, native impact/qualification and draft API decisions, ECA and code-owner approval remain pending. No PR is published and no native qualification/release/acceptance is claimed.
