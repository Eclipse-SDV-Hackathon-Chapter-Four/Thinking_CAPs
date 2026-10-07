# ASPICE SWE evidence — AZ3166 zonal lighting controller

This folder holds demonstration work products for the Automotive SPICE
software engineering processes SWE.1–SWE.6. They cover the ThreadX lighting
controller in [`../src`](../src) and the shared [`../../src/lights_protocol.c`](../../src/lights_protocol.c).
They demonstrate code quality and traceability; they are not an assessed
capability level.

| Process | Work products | Verification evidence |
| --- | --- | --- |
| SWE.1 Software requirements analysis | [system-requirements.md](swe1-requirements/system-requirements.md), [software-requirements.md](swe1-requirements/software-requirements.md) | Consistency checks in the report |
| SWE.2 Software architectural design | [architecture.md](swe2-architecture/architecture.md), PlantUML [views](swe2-architecture/diagrams/) | Allocation checks in the report |
| SWE.3 Detailed design and unit construction | [detailed-design.md](swe3-detailed-design/detailed-design.md), [diagrams](swe3-detailed-design/diagrams/), [coding-guidelines.md](swe3-detailed-design/coding-guidelines.md) | `-Werror` firmware build |
| SWE.4 Software unit verification | [unit-verification.md](swe4-unit-verification/unit-verification.md) | Host unit tests, gcov coverage, cppcheck, MISRA baseline, lizard complexity |
| SWE.5 Integration and integration test | [integration-test.md](swe5-integration-test/integration-test.md) | [On-target run](../../artifacts/az3166-uart-can/results.json) |
| SWE.6 Software qualification test | [qualification-test.md](swe6-qualification-test/qualification-test.md) | [Live X-Verse + CARLA run](../../artifacts/az3166-xverse-carla/results.json), automated analyses |

Open the report at [report/aspice-swe-report.html](report/aspice-swe-report.html).
It contains:

- key indicators
- every work product with its rendered diagrams
- test and analysis results
- the bidirectional traceability matrix SYS → SWR → ARC → DD → UT/IT/QT/AN/RV
- the remaining gaps

`report/summary.json` holds the same data in machine-readable form.

## Regenerate

```bash
cd ThreadX
# prerequisites: gcc, cppcheck, java, the arm-none-eabi toolchain, a configured
# build-az3166/ (see ../README.md), and .venv with gcovr and lizard:
.venv/bin/pip install gcovr lizard==1.17.10
.venv/bin/python az3166/aspice/tools/generate_report.py
```

The generator does the following:

- parses the Markdown tables and requirement headings in this folder
- renders the PlantUML views with a pinned, SHA-1-checked PlantUML 1.2024.7 jar
  (fetched into `.cache/tools/`; nothing is sent to a PlantUML server)
- builds and runs the unit tests with coverage
- runs cppcheck, the MISRA addon and lizard
- rebuilds the firmware without warnings and checks its size budget, the
  pinned ThreadX revision and the shared-protocol hash
- checks that the recorded SWE.5/SWE.6 runs used the same firmware binary as
  the current build

Rerun the [hardware test](../README.md#hardware-test) and the
[live X-Verse test](../README.md#live-x-verse--carla-test) to refresh
integration and qualification evidence after a firmware change.

## Current status

The generated report shows:

- 23 of 26 requirements verified
- 100% line and branch coverage of the host-testable units
- no open static analysis findings (three justified deviations)
- 11 of 11 integration tests passed
- 12 of 14 qualification cases passed
- no traceability inconsistencies

Open items:

- **SWR-004, SWR-022:** visual inspection of the board LEDs is not recorded (QTC-12).
- **SWR-006:** the input-timeout variant needs a separate build and test (QTC-14).
