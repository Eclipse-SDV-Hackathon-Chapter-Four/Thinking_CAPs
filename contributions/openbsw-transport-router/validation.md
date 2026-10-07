# Validation — transportRouter

All checks ran on 7 October 2026 in a git worktree of OpenBSW `main` at
`b0550871b7a44ae47bb9b7c68af84fb9115bfa77` with the module added, using
`OBSW_BASE=b0550871… OpenBSW/scripts/openbsw-pr.sh all` from this repository. Nothing
has been submitted publicly, and no maintainer approval or merge is claimed.

| Item | Value |
| --- | --- |
| Source of the change | `OpenBSW/contrib/libs/bsw/transportRouter` in this repository (the zonal gateway builds from the same files) |
| Commit on the PR branch | `08904a2031b6…` ([commit.txt](evidence/commit.txt)), author Jefferson Nascimento, `Signed-off-by`, `Assisted-by` |
| Patch | [0001-transport-router.patch](0001-transport-router.patch), 17 files, +2586 lines |
| Reproduce | `OpenBSW/scripts/bootstrap.sh`, `OpenBSW/scripts/openbsw-pr.sh tools`, then `OBSW_BASE=<main sha> OpenBSW/scripts/openbsw-pr.sh all` (needs the external build volume) |

| Check | Command (in the OpenBSW worktree) | Result | Evidence |
| --- | --- | --- | --- |
| Format | `treefmt --no-cache` twice, `git diff --exit-code` | clean | [treefmt.txt](evidence/treefmt.txt), [format-diff.txt](evidence/format-diff.txt) |
| Copyright | `tools/cr_checker/cr_checker.py` on the added and changed files | ok | [copyright.txt](evidence/copyright.txt) |
| Unit tests | `cmake --preset tests-posix-debug`; build `transportRouterTest` and `transportRouterSimpleTest`; `ctest -L transportRouter` | 46/46 (42 new, 4 existing) | [ctest.txt](evidence/ctest.txt), [junit.xml](evidence/junit.xml) |
| Build warnings | unit-test build log (`-Wall -Werror`) | 0 | [build-warnings.txt](evidence/build-warnings.txt) |
| Coverage | gcovr on `src/`, without the logger file, throw and unreachable branches | 100 % lines (397/397), 99.1 % branches (330/333), 100 % functions | [coverage.txt](evidence/coverage.txt), [coverage-summary.json](evidence/coverage-summary.json) |
| clang-tidy | repository `.clang-tidy` on the three sources | 0 findings | [clang-tidy.txt](evidence/clang-tidy.txt) |
| Bazel | `bazel test //libs/bsw/transportRouter/... //libs/bsw/transportRouterSimple/...` (bazelisk 1.29.0) | 2/2 | [bazel-test.txt](evidence/bazel-test.txt) |
| Documentation | `make html` in `doc/dev` (requirements of `doc/dev/requirements.txt`, Python 3.10, PlantUML 1.2024.7) | built, no warnings | [docs-build.log](evidence/docs-build.log) |
| Commit message | `gitlint` with the repository `.gitlint` | ok | [gitlint.txt](evidence/gitlint.txt) |
| Patch | `git format-patch -1`; `git am` onto a fresh `b0550871` worktree | applies; identical tree `c2f3e2f63d9a…` | [commit.txt](evidence/commit.txt) |

Tools: treefmt 2.1.0, clang-format 17.0.6, cmake-format 0.6.13, buildifier 8.5.1 (SHA-256
pinned as in OpenBSW's Dockerfile), GCC 11.4, CMake 4.4, gcovr, clang-tidy 19.1.7,
gitlint 0.19.1 ([tools.txt](evidence/tools.txt)).

## Unit tests and OpenBSW test guidelines

`doc/dev/guidelines/unittests.rst` is followed:

- Suite `TransportRouterTest`; test names in CamelCase that describe the behaviour.
- A Doxygen block before each of the 42 tests, with a brief and, for longer tests, a
  detailed description.
- No `if` in the tests. The fixture helpers keep one null check, so that a failed
  expectation does not crash the run.
- All mocks are `StrictMock`:
  - `AbstractTransportLayerMock` and `TransportMessageProcessedListenerMock` from
    `transport`
  - `LockMock` from `async`
  - the module's own `RouteObserverMock`, which is in `mock/gmock/include` with CMake
    target `transportRouterMock` and Bazel target `transport_router_mock`
- Tests are in an anonymous namespace.

## Use in an application

The same module source runs in the Thinking CAPs zonal diagnostic gateway (DoIP server,
DoCAN, OpenBSW UDS and the [doipClient](../openbsw-doip-client/README.md) for Ethernet
ECUs):

- **POSIX** (FreeRTOS, lwIP on TAP, `vcan0`): 44/44 integration tests on 7 October 2026
  after the changes above. Forwarding latency p95 was 1.9 ms (DoIP→CAN) and 0.9 ms
  (CAN→DoIP). Results in `OpenBSW/evidence/gateway-it/results.json`.
- **NXP S32K148EVB** (ThreadX 6.4.3, 100BASE-T1, no CAN adapter): 16/16 board tests
  with the image built from these sources. Results in
  `OpenBSW/evidence/board-gateway-it/results.json`.
- **ASPICE SWE.1–SWE.6 report:** `OpenBSW/aspice/report/aspice-swe-report.html`. The
  unit test cases UTC-01 to UTC-13 trace to the test names above.

## Limitations

- **CI differences:** the checks ran locally, not in OpenBSW's Docker CI.
  - clang-tidy was 19.1.7, while CI uses version 17.
  - The full `tests-posix-*` matrix and the clang/C++23 CI configurations were not run.

  The CI run on the pull request is authoritative.
- **Not yet done:** the feature issue is not filed. The commit and the PR description
  reference it as `#TBD`; before the PR, replace that with the issue number and
  regenerate the patch on the then-current `main`.
- **Design limits** (both listed in the PR description):
  - DoCAN STmin and block size are per transport layer.
  - The DoIP acknowledgement is sent when the router accepts the message.
