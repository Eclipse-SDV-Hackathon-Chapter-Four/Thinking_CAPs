# ASPICE SWE evidence — OpenBSW zonal diagnostic gateway

This folder holds demonstration work products for the Automotive SPICE
software engineering processes SWE.1–SWE.6 for the
[OpenBSW zonal diagnostic gateway](../README.md). They show code quality and
traceability; they are not an assessed capability level.

| Process | Work products | Verification evidence |
| --- | --- | --- |
| SWE.1 Requirements | [system](swe1-requirements/system-requirements.md), [software](swe1-requirements/software-requirements.md) requirements | Consistency checks in the report |
| SWE.2 Architecture | [architecture.md](swe2-architecture/architecture.md), PlantUML [views](swe2-architecture/diagrams/) | Allocation checks |
| SWE.3 Detailed design | [detailed-design.md](swe3-detailed-design/detailed-design.md), [diagrams](swe3-detailed-design/diagrams/), [coding-guidelines.md](swe3-detailed-design/coding-guidelines.md) | Warning-free builds, OpenBSW format and copyright gates |
| SWE.4 Unit verification | [unit-verification.md](swe4-unit-verification/unit-verification.md) | GoogleTest in the OpenBSW unit-test build and Bazel, gateway GoogleTest, pytest; gcovr, coverage.py, cppcheck, clang-tidy, lizard |
| SWE.5 Integration test | [integration-test.md](swe5-integration-test/integration-test.md) | Recorded runs on the [Linux host](../evidence/gateway-it/results.json) and the [S32K148EVB](../evidence/board-gateway-it/results.json), each checked against the current image |
| SWE.6 Qualification test | [qualification-test.md](swe6-qualification-test/qualification-test.md) | Automated analyses; live campaigns recorded as not run |

Open the report at [report/aspice-swe-report.html](report/aspice-swe-report.html).
`report/summary.json` holds the same data in machine-readable form.

## Regenerate

```bash
OpenBSW/scripts/gateway-it.sh                     # refresh SWE.5 evidence after a code change
python3 OpenBSW/aspice/tools/generate_report.py   # runs every gate and analysis (a few minutes)
```

The generator does the following:

- re-runs the upstream gates of the contributed module (`scripts/openbsw-pr.sh`)
- runs the gateway and generator unit tests with coverage
- runs cppcheck, clang-tidy and lizard
- rebuilds the gateway and checks:
  - its symbols (no SOME/IP, Zenoh or middleware)
  - the pinned OpenBSW revision
  - the changed paths of the branch
- computes the bus load
- checks that the recorded SWE.5 run used the current executable
- computes the bidirectional traceability

## Current status

- **Requirements:** 28/37 verified, 7 partially verified, 1 failed (SWR-032 bus load), 1 not verified (SWR-026)
- **Unit tests:** 78/78; module 100% lines and 99.1% branches
- **Static analysis:** 0 open findings; 6 cppcheck style hints justified (DEV-02)
- **Integration tests:** 38/38: 28 on the Linux host and 10 on the NXP S32K148EVB, each against the current image
- **Qualification:** 12/16 pass, including the S32K148 build and the board baseline; 1 fails (QTC-06 bus load), 3 live campaigns are not run or open
- **Traceability:** one issue, SWR-026, which has no implementation

## Render the diagrams

```bash
java -Djava.awt.headless=true -jar X-Verse/.cache/tools/plantuml-1.2024.7.jar \
  -tsvg OpenBSW/aspice/swe2-architecture/diagrams/*.puml
```

The PlantUML jar is the one the Serial2CAN report generator downloads and
checks with SHA-1.
