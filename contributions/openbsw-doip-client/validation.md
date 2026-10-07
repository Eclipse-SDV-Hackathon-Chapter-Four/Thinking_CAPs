# Validation — doipClient

All checks ran on 7 October 2026 in a git worktree of OpenBSW `main` at
`b0550871b7a44ae47bb9b7c68af84fb9115bfa77` with the module added, using
`OBSW_BASE=b0550871… OpenBSW/scripts/doip-client-test.sh all` from this repository.

| Check | Command (in the OpenBSW worktree) | Result | Evidence |
| --- | --- | --- | --- |
| Format | `treefmt --no-cache` twice, `git diff --exit-code` | clean | [treefmt.txt](evidence/treefmt.txt), [format-diff.txt](evidence/format-diff.txt) |
| Copyright | `tools/cr_checker/cr_checker.py` on the added and changed files | ok | [copyright.txt](evidence/copyright.txt) |
| Unit tests | `cmake --preset tests-posix-debug`; build `doipClientTest`; `ctest -L doipClient` | 20/20 | [ctest.txt](evidence/ctest.txt), [junit.xml](evidence/junit.xml) |
| Build warnings | unit-test build log (`-Wall -Werror`) | 0 | [build-warnings.txt](evidence/build-warnings.txt) |
| Coverage | gcovr on `src/`, without the logger file, throw and unreachable branches | 94.6 % lines, 83.8 % branches, 97.2 % functions | [coverage.txt](evidence/coverage.txt), [coverage-summary.json](evidence/coverage-summary.json) |
| clang-tidy | repository `.clang-tidy` on the three sources | 0 findings | [clang-tidy.txt](evidence/clang-tidy.txt) |
| Bazel | `bazel test //libs/bsw/doipClient/... //libs/bsw/doip/...` (bazelisk 1.29.0) | 2/2 | [bazel-test.txt](evidence/bazel-test.txt) |
| Documentation | `make html` in `doc/dev` (requirements of `doc/dev/requirements.txt`, Python 3.10, PlantUML 1.2024.7) | built, no warnings | [docs-build.log](evidence/docs-build.log) |
| Commit message | `gitlint` with the repository `.gitlint` | ok | [gitlint.txt](evidence/gitlint.txt) |
| Patch | `git format-patch -1`; `git am` onto a fresh `b0550871` worktree | applies, identical tree | [commit.txt](evidence/commit.txt) |

Tools: treefmt 2.1.0, clang-format 17.0.6, cmake-format 0.6.13, buildifier 8.5.1 (SHA-256
pinned as in OpenBSW's Dockerfile), GCC 11.4, CMake 4.4.4, gcovr, clang-tidy 19.1.7,
gitlint 0.19.1.

## Use in an application

The same module source (in `OpenBSW/contrib/libs/bsw/doipClient` of this repository) runs
in the Thinking CAPs zonal diagnostic gateway, where `transport::TransportRouter` routes
tester requests to it:

- POSIX (FreeRTOS, lwIP on TAP): 14 DoIP integration tests against a simulated Ethernet
  ECU (`OpenBSW/gateway/tests/test_doip_routing.py`), part of 42/42 —
  `OpenBSW/evidence/gateway-it/results.json`.
- NXP S32K148EVB (ThreadX 6.4.3, 100BASE-T1): 5 DoIP tests, part of 15/15; routed round
  trip p95 4.1 ms — `OpenBSW/evidence/board-gateway-it/results.json`.

## Limitations

- The checks ran locally, not in OpenBSW's Docker CI; clang-tidy was 19.1.7, while CI uses
  version 17. The CI run on the pull request is authoritative.
- Not covered by the unit tests (94.6 % lines, 83.8 % branches): failed `sendMessage`
  calls on a connection that is not active, the queue of expected acknowledgements being
  full, a second request while a connection is still being set up, aborting a stale socket
  before reconnecting, the release of the alive check response, and the release of a
  partly received message when the connection closes.
- Related findings in existing OpenBSW code are reported separately in
  [related-issues/](related-issues/), with reproduction tests on `main`.
