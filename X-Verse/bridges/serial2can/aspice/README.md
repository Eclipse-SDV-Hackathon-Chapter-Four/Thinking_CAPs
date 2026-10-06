# ASPICE SWE evidence — X-COM Serial2CAN bridge

This folder holds demonstration work products for the Automotive SPICE
software engineering processes SWE.1–SWE.6 for the bridge in [`../src`](../src).
They demonstrate code quality and traceability; they are not an assessed
capability level.

| Process | Work products | Verification evidence |
| --- | --- | --- |
| SWE.1 Requirements | [system](swe1-requirements/system-requirements.md), [software](swe1-requirements/software-requirements.md) requirements | Consistency checks in the report |
| SWE.2 Architecture | [architecture.md](swe2-architecture/architecture.md), PlantUML [views](swe2-architecture/diagrams/) | Allocation checks |
| SWE.3 Detailed design | [detailed-design.md](swe3-detailed-design/detailed-design.md), [diagrams](swe3-detailed-design/diagrams/), [coding-guidelines.md](swe3-detailed-design/coding-guidelines.md), [ruff.toml](../ruff.toml) | ruff, mypy, complexity |
| SWE.4 Unit verification | [unit-verification.md](swe4-unit-verification/unit-verification.md) | pytest unit cases, coverage.py |
| SWE.5 Integration test | [integration-test.md](swe5-integration-test/integration-test.md) | Pseudo-terminal integration (run now), [AZ3166 run](../evidence/hardware-check/results.json) (recorded) |
| SWE.6 Qualification test | [qualification-test.md](swe6-qualification-test/qualification-test.md) | [Live X-Verse + CARLA run](../evidence/xverse-carla/results.json), analyses |

Open the report at [report/aspice-swe-report.html](report/aspice-swe-report.html).
`report/summary.json` holds the same data in machine-readable form.

## Regenerate

```bash
cd X-Verse/bridges/serial2can
.venv/bin/pip install -r requirements-dev.txt ruff==0.6.9 coverage==7.6.1 mypy==1.11.2 lizard==1.17.10
.venv/bin/python aspice/tools/generate_report.py   # needs java; PlantUML jar is SHA-1 checked
```

The generator does the following:

- re-executes the host test suite with JUnit and branch coverage, including the CLI child process
- runs ruff, mypy and lizard
- renders the PlantUML views locally
- checks that the recorded hardware and X-Verse evidence was made with the
  current sources ([evidence/manifest.json](../evidence/manifest.json))
- computes the bidirectional traceability

It exits non-zero on test failures or traceability issues.

## Current status

- 19 of 21 requirements verified
- 302 host tests pass
- 95% line / 90% branch coverage
- 0 ruff findings, mypy clean
- 15 of 15 integration cases pass
- 10 of 12 qualification cases pass
- no traceability issues

Open items:

- **SWR-011:** deployment on SocketCAN `vcan0` is not run (QTC-11).
  Creating the interface needs root.
- **SWR-008:** two physical serial ECUs on one bus is not run (QTC-12). The
  OpenBSW S32K148 firmware does not speak SLCAN yet. Fan-out is verified on
  the host (ITC-02).

**Defects found while building this evidence**, now fixed and covered by tests:

- token loss in the stream splitter during the handshake (ITC-01)
- under-counted disconnects after writer-detected link loss (ITC-07)
- test interference from a live `udp_multicast` bus on the same UDP port (ITC-04)
