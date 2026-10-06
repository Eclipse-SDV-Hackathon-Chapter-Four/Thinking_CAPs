# ASPICE SWE evidence — OpenBSW zonal diagnostic gateway

This folder holds demonstration work products for the Automotive SPICE
software engineering processes SWE.1–SWE.6 for the
[OpenBSW zonal diagnostic gateway](../README.md). They show code quality and
traceability; they are not an assessed capability level.

| Process | Work products | Status |
| --- | --- | --- |
| SWE.1 Requirements | [system](swe1-requirements/system-requirements.md), [software](swe1-requirements/software-requirements.md) requirements | Draft for review |
| SWE.2 Architecture | [architecture.md](swe2-architecture/architecture.md), PlantUML [views](swe2-architecture/diagrams/) | Draft for review |
| SWE.3 Detailed design | — | Not started |
| SWE.4 Unit verification | — | Not started |
| SWE.5 Integration test | — | Not started |
| SWE.6 Qualification test | — | Not started |

The requirement and element tables use the same format as the
[Serial2CAN](../../X-Verse/bridges/serial2can/aspice/README.md) evidence. A
report generator in the same style can therefore parse them once
implementation starts.

## Render the diagrams

```bash
java -Djava.awt.headless=true -jar X-Verse/.cache/tools/plantuml-1.2024.7.jar \
  -tsvg OpenBSW/aspice/swe2-architecture/diagrams/*.puml
```

The PlantUML jar is the one the Serial2CAN report generator downloads and
checks with SHA-1.
