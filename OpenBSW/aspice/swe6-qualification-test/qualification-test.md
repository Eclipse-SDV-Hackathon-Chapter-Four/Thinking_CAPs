# Software qualification test (SWE.6)

## Strategy

Qualification shows that the integrated gateway meets its requirements in its
operational environment. Here that environment is:

- the X-Verse vehicle network (CAN `vcan0`, CARLA, cruise control)
- the OpenSOVD diagnostic path (OpenSOVD gateway → CDA → DoIP)

It is qualified in three ways:

- **Automated analyses (`auto:`).** The report generator computes them on every run from the build, the configuration and the recorded integration evidence.
- **Live campaigns (`manual:`).** These need the X-Verse stack, the CDA with an MDD for the gateway, or target hardware. Each one records its status: `not-run`, `open` or `reviewed`.
- **Inheritance.** The platform underneath is the unmodified, pinned OpenBSW, qualified by its own SIL suite (`auto:sil-baseline`).

## Qualification test cases

The report generator parses this table: ID | Source | Test case | Method | Verifies.

| ID | Source | Test case | Method | Verifies |
| --- | --- | --- | --- | --- |
| QTC-01 | auto:sil-baseline | OpenBSW SIL suite (uds, enet, docan) on the pinned revision: 104/104 | Test | SWR-050 |
| QTC-02 | auto:upstream-gates | Contributed module in the unmodified pinned OpenBSW: format gate, copyright check, unit tests, Bazel tests | Test | SWR-053 |
| QTC-03 | auto:openbsw-pinned | The OpenBSW checkout is at the locked revision without tracked modifications | Analysis | SWR-053 |
| QTC-04 | auto:no-vehicle-middleware | The gateway executable contains no SOME/IP, middleware or Zenoh symbols | Analysis | SWR-031 |
| QTC-05 | auto:no-dynamic-memory | Gateway and module sources contain no `new`, `malloc`, `throw` or `dynamic_cast` | Analysis | SWR-043 |
| QTC-06 | auto:bus-load | Worst-case gateway CAN load from the routing table (classic CAN, 500 kbit/s) and the measured 1 s peak in SWE.5 are below 10 % | Analysis | SWR-032 |
| QTC-07 | auto:configuration-consistency | `routing.yaml` is valid (all CAN identifiers in `0x7DF`–`0x7EF`, so the DoCAN filter accepts and the gateway sends nothing else) and every Serial2CAN profile forwards each route's request and response IDs together (or neither) | Analysis | SWR-030, SWR-033, SWR-052 |
| QTC-08 | auto:latency | Recorded forwarding latency p95 ≤ 10 ms per direction | Test | SWR-060 |
| QTC-09 | auto:observability | Recorded gateway logs contain the start-up identity with the current routing-table hash and a statistics line | Analysis | SWR-054 |
| QTC-10 | auto:baseline-untouched | The branch changes only `OpenBSW/` and `contributions/`: no X-Verse, ThreadX, S-CORE, OpenSOVD or CARLA file | Inspection | SWR-033 |
| QTC-11 | manual:reviewed | DoIP generic header handling is the unmodified OpenBSW `doip` module (covered by its unit tests); no gateway change | Inspection | SWR-040 |
| QTC-12 | manual:not-run | Live X-Verse + CARLA: cruise-control demonstration (`DEMO=cruise`, 13 assertions) passes with the gateway running and with it stopped; candump shows only diagnostic IDs from the gateway | Test | SWR-030, SWR-033 |
| QTC-13 | manual:not-run | OpenSOVD → CDA → gateway: SOVD client reads `0x1010` identification and `0x1020` data, lists and clears U0140 | Test | SWR-001, SWR-012, SWR-021, SWR-025 |
| QTC-14 | manual:open | ThreadX rear lighting ECU with a UDS-on-CAN server answers through the gateway (OP-2) | Test | SWR-012, SWR-024 |
| QTC-15 | manual:not-run | Gateway application built for the S32K148 platform | Analysis | SWR-051 |

## Pass criteria

- All automated cases pass.
- Live campaigns record their status.
- Cases that are not run, and failed analyses, are listed as qualification gaps in the report.
