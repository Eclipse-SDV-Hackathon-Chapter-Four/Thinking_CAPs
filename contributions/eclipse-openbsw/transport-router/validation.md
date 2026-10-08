# Validation record — OpenBSW transportRouter contribution

Prepared on 6 October 2026. Nothing has been submitted publicly, and no
maintainer approval or merge is claimed.

| Item | Value |
| --- | --- |
| Upstream | <https://github.com/eclipse-openbsw/openbsw>, base `432b9be6098d99570ab8ebc32a7cbb895ca7bb63` |
| Source of the change | `OpenBSW/contrib/libs/bsw/transportRouter` in this repository (the zonal gateway builds from the same files) |
| Commit on the PR branch | `evidence/commit.txt` (author Jefferson Nascimento, `Signed-off-by`) |
| Patch | `0001-transport-router.patch`, 16 files, +2353 lines; SHA-256 in `artifact-manifest.json` |
| Reproduce | `OpenBSW/scripts/bootstrap.sh`, then `OpenBSW/scripts/openbsw-pr.sh all` (needs the external build volume) |

## Checks performed

All checks ran on the PR branch: a git worktree of the pinned OpenBSW with the
module added and the two registration lines.

| Check | Tool and version | Result | Evidence |
| --- | --- | --- | --- |
| Unit tests | OpenBSW `tests-posix-debug`, GoogleTest/gMock, GCC 11.4, CMake 4.4 | 46/46 passed (42 new, 4 existing `TransportRouterSimple`) | `ctest.txt`, `junit.xml` |
| Build warnings (unit-test build) | GCC 11.4 | 0 | `build-warnings.txt` |
| Coverage | gcovr 7.2, `--exclude-throw-branches --exclude-unreachable-branches` | 100% lines (394/394), 99.1% branches, 100% functions | `coverage.txt`, `coverage-summary.json` |
| Format gate (OpenBSW `.ci/format.py`) | treefmt 2.1.0, clang-format 17.0.6, cmake-format 0.6.13, buildifier 8.5.1 | clean (empty second-pass diff) | `treefmt.txt`, `format-diff.txt` |
| Copyright check | OpenBSW `tools/cr_checker` | ok | `copyright.txt` |
| clang-tidy | clang-tidy 19.1.7 with the repository `.clang-tidy` | 0 findings in the module | `clang-tidy.txt` |
| Bazel | bazelisk 1.29.0 (SHA-256 as in the OpenBSW Dockerfile), Bazel from `.bazelversion` | 2/2 tests passed | `bazel-test.txt` |
| Commit message | gitlint 0.19.1 with the repository `.gitlint` | ok | `gitlint.txt` |
| Patch applies | `git am` on a clean worktree at the base | ok; tree identical to the verified branch (`38f6764325b1…`) | this record |

Tool binaries were verified against the SHA-256 sums in OpenBSW's development
Dockerfile, where it pins them (treefmt, buildifier, bazelisk).

## Integration in the zonal gateway

The same module runs in the Thinking CAPs zonal diagnostic gateway: POSIX,
DoIP over lwIP/TAP, DoCAN on `vcan0`, OpenBSW UDS. The module uses no RTOS API
directly, only OpenBSW's `async`; it was tested with both RTOS bindings.

- **Integration tests:** 28/28 passed on FreeRTOS and on ThreadX (the gateway's
  current default). See `OpenBSW/evidence/gateway-it/results.json`, which
  records the executable hash of the ThreadX run.
- **NXP S32K148EVB (ThreadX and FreeRTOS):** 10/10 board tests. See
  `OpenBSW/evidence/board-gateway-it/results.json`.
- **ASPICE SWE.1–SWE.6 report:** `OpenBSW/aspice/report/aspice-swe-report.html`.

## Not done / limitations

- **CI differences:** the checks ran locally, not in OpenBSW's Docker CI.
  - clang-tidy was 19 instead of CI's 17.
  - The full `tests-posix-*` matrix and the clang/C++23 CI configurations were not run.
  - The Sphinx documentation build was not run.
- **Prerequisites for submission:** opening the issue and agreeing on the
  approach with the maintainers, and the Eclipse Contributor Agreement for the
  author's email. Both are pending; CONTRIBUTING.md asks for them before a PR.
- **Design limits** (both listed in the PR description):
  - DoCAN STmin and block size are per transport layer.
  - The DoIP acknowledgement is sent when the router accepts the message.
