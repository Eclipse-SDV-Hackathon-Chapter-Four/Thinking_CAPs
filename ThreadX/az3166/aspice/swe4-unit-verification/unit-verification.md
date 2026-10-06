# Software unit verification (SWE.4)

## Strategy

| Unit | Verification method |
| --- | --- |
| DD-06 SLCAN codec, DD-07 Lights protocol | **Unit tests** on the host. The units are target-independent pure C, built with GCC `--coverage`. Target: 100% statement and branch coverage. |
| DD-01 … DD-05, DD-08 … DD-11 (hardware or ThreadX dependent) | **Static analysis** (compiler, cppcheck, MISRA baseline, complexity) plus **review** against the [coding guidelines](../swe3-detailed-design/coding-guidelines.md). Dynamic behaviour is verified on the target by the SWE.5 integration tests (a planned host harness on the ThreadX Linux port is out of scope for this slice). |

The tests are plain C programs registered in CTest, in the Linux build in
`ThreadX/CMakeLists.txt`. A program exits non-zero on the first failed check,
naming the source line.

## Unit test cases

The report generator parses this table: ID | Test case | Unit | Verifies | Executable.

| ID | Test case | Unit | Verifies | Executable |
| --- | --- | --- | --- | --- |
| UTC-01 | All 256 values of status byte 0 (other bytes 0xFF) give the expected `0x1F4` payload, other bytes zero | DD-07 | SWR-001, SWR-002 | test_lights_protocol |
| UTC-02 | DLC 0–15: only DLC 8 is accepted | DD-07 | SWR-003 | test_lights_protocol |
| UTC-03 | Neighbouring IDs, the own output ID, and extended, RTR and error flags are rejected without modifying the output | DD-07 | SWR-003 | test_lights_protocol |
| UTC-04 | `lights_off` produces the all-zero `0x1F4` frame | DD-07 | SWR-002, SWR-007 | test_lights_protocol |
| UTC-05 | Format→parse round trip for all 256 status bytes; exact `t1F48…` encoding | DD-06 | SWR-001, SWR-014 | test_slcan |
| UTC-06 | Extended data frame and remote frame encoding; capacity and range refusals | DD-06 | SWR-014 | test_slcan |
| UTC-07 | Command parsing: `O`, `C`, `V`, `N`, `F`, `Z0`, `S6`, `s031C` | DD-06 | SWR-011 | test_slcan |
| UTC-08 | 23 malformed lines (length, hex, DLC, ID range, unsupported commands) are rejected | DD-06 | SWR-011, SWR-013 | test_slcan |
| UTC-09 | Boundary characters around each hex range in ID, data and BTR; bitrate digit range; extended remote formatting; 29-bit overflow | DD-06 | SWR-013, SWR-014 | test_slcan_edge |

## Pass criteria

- All test programs pass.
- 100% line and branch coverage of `slcan.c` and `lights_protocol.c`.
- No open static analysis findings outside the justified deviations.
