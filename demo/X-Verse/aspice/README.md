# ASPICE SWE evidence — X-Verse end-to-end demonstration

Demonstration work products for the Automotive SPICE software engineering processes
SWE.1–SWE.6, for the end-to-end flow started by `run_autoverse.py --enable-camera-display --vcu-zenoh`:

CARLA and the virtual vehicle → Zenoh VCU → Zenoh–SOME/IP bridge (`bridge-e2e`) → Eclipse
S-CORE cruise-control ECU, which sets DTC `CC.LostCommunication` and serves it over SOVD
through Eclipse inc_diagnostics PR #16 (`sovd_adapter`) → OTA vECU (certgen, EOL backend,
RTCU) updating the cluster app on the Android targets (Cuttlefish, Raspberry Pi).

They demonstrate code quality and traceability; they are not an assessed capability
level. Component-level packages exist in the OTA vECU (`vecu/ota/aspice`) and the
Serial2CAN bridge (`bridges/can/serial2can-bridge/aspice`).

| Process | Work products | Verification evidence |
| --- | --- | --- |
| SWE.1 Requirements | [system](swe1-requirements/system-requirements.md), [software](swe1-requirements/software-requirements.md) requirements | traceability checks in the report |
| SWE.2 Architecture | [architecture.md](swe2-architecture/architecture.md), PlantUML [views](swe2-architecture/diagrams/) (context, components, DTC and OTA sequences) | allocation of every requirement to an element |
| SWE.3 Detailed design | [detailed-design.md](swe3-detailed-design/detailed-design.md) (Zenoh keys, SOME/IP, SOVD, OTA units) | design reviewed against the running system |
| SWE.4 Unit verification | [unit-verification.md](swe4-unit-verification/unit-verification.md) | launcher (unittest), SOME/IP payload conversion, S-CORE cruise control (gtest), PR #16 `sovd_adapter`, OTA backend (JUnit) |
| SWE.5 Integration test | [integration-test.md](swe5-integration-test/integration-test.md) | [`tools/e2e_check.py`](tools/e2e_check.py) against the running system |
| SWE.6 Qualification test | [qualification-test.md](swe6-qualification-test/qualification-test.md) | supervisor logs, OTA campaign records, witnessed live dry run |

Open the report at [report/aspice-swe-report.html](report/aspice-swe-report.html);
[report/summary.json](report/summary.json) holds the same data in machine-readable form,
and `report/evidence/` the raw results.

## Regenerate

Start the system first (`python3 run_autoverse.py --enable-camera-display --vcu-zenoh`),
then from this checkout:

```bash
python3 aspice/tools/generate_report.py          # host suites + integration + qualification
python3 aspice/tools/generate_report.py --full   # also OTA (Maven container) and S-CORE / PR #16 (Bazel, devcontainer)
python3 aspice/tools/e2e_check.py                # integration checks only
```

The generator renders the PlantUML views with the `plantuml/plantuml` Docker image, runs
the unit suites, runs the integration checks (read-only: nothing is injected), reads the
qualification records (supervisor logs, OTA campaigns), computes bidirectional
traceability and exits non-zero on a failed test or a traceability gap. Without `--full`,
the container suites keep their last recorded results, marked as such in the report.

## Current status

- 11 of 11 software requirements verified, 24 of 24 test cases pass, no traceability gaps
- Unit: launcher 15 tests, SOME/IP payload conversion 213 checks, S-CORE cruise control
  15 gtest cases, PR #16 `sovd_adapter` test target, OTA backend 70 JUnit tests
- Integration: 13 of 13 checks against the running system (Zenoh, SOME/IP → S-CORE,
  SOVD/DTC, certgen PKI, mutual TLS, RTCU targets, campaigns, CARLA, Android)
- Qualification: one-command start/stop and OTA campaigns (Cuttlefish, Raspberry Pi,
  unreachable target) from records; driving with cruise control and the lost-speed-signal
  DTC witnessed in the live dry run (issue #44)

**Defect found while building this evidence:** none in the product. The first version of
ITC-09 misread TLS 1.3 behaviour (the device API rejects a missing client certificate
after the handshake, by closing the connection) and was corrected.
