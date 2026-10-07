# Unit verification — X-Verse end-to-end demonstration

Unit-level test suites of the elements in the end-to-end chain. The report generator runs
them and records the results; suites that need a container (OTA backend, S-CORE, PR #16)
run in the same containers the components are built in.

| ID | Suite | Element | How it runs | Verifies |
| --- | --- | --- | --- | --- |
| UT-LAUNCHER | `tests/test_run_autoverse.py` (Python unittest) | Launcher | `python3 -m unittest tests.test_run_autoverse` | SWR-01 |
| UT-SOMEIP | `tests/payload/test_convert.cpp` (`test_convert`) | SOME/IP bridge | built test binary `build/test_convert` | SWR-05 |
| UT-SCORE | `score/cruise_control/tests/cruise_control_test.cpp` (gtest) | Cruise-control app | `bazel test --nocache_test_results //score/cruise_control/...` in the S-CORE devcontainer (always executed, never a cached result) | SWR-06 |
| UT-PR16 | `//score/mw/diag/sovd_adapter:all` (inc_diagnostics, PR #16) | Diagnostics server | `bazel test --config=score_diag_x86_64_linux --nocache_test_results` in the S-CORE devcontainer (always executed) | SWR-07 |
| UT-OTA | `backend/java/src/test` (JUnit 5, Spring Boot) | OTA backend | `mvn test` in `maven:3.9-eclipse-temurin-21` | SWR-09 |

Pass criterion: every test case of the suite passes. Elements without a unit suite (virtual
vehicle, manual control, VCU, RTCU, certgen) are verified at integration and qualification
level.
