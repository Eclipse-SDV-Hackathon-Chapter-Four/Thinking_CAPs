# Software qualification test (SWE.6)

## Strategy

Qualification shows that the integrated software meets its requirements in
its operational environment: the complete X-Verse stack started with
`run_autoverse.py --enable-camera-display --vcu-zenoh`. The stack contains:

- CARLA 0.9.15 (Town10HD) and the X-Verse VCU
- S-CORE ADAS and the Zenoh↔SOME/IP bridge
- Vehicle Manual Control, the virtual vehicle and Cuttlefish
- `zenohd` 1.10.1 and the unmodified Zenoh2CAN bridge over SLCAN to the board

The inputs come from the driver's controls, not fixtures. The test presses the
Manual Control keys, and the real VCU produces the status. Expected results
are the `carla.VehicleLightState` bits of the actor (Brake = 8, Reverse = 64).
Requirements that cannot be tested black-box are qualified by analysis (AN) or
inspection (RV).

Procedure: [`az3166/tests/xverse_carla_live.py`](../../tests/xverse_carla_live.py).
Recorded results: [`artifacts/az3166-xverse-carla/`](../../../artifacts/az3166-xverse-carla/results.json).

## Qualification test cases

The report generator parses this table: ID | Source | Test case | Method | Verifies.
The source is `step:<name>` (live X-Verse run), `auto:<check>` (computed by
the generator) or `manual:<status>` (inspection record).

| ID | Source | Test case | Method | Verifies |
| --- | --- | --- | --- | --- |
| QTC-01 | step:brake | Brake pedal (S held) → CARLA brake lamp on | Test | SWR-001, SWR-002, SWR-050 |
| QTC-02 | step:brake-released | Brake released → CARLA lamps off | Test | SWR-001, SWR-002, SWR-050 |
| QTC-03 | step:reverse | Reverse toggle (Q) → VCU engages reverse → CARLA reverse lamp on | Test | SWR-001, SWR-002, SWR-050 |
| QTC-04 | step:reverse-and-brake | Brake while in reverse → both lamps on (mask 72) | Test | SWR-001, SWR-002, SWR-050 |
| QTC-05 | step:reverse-brake-released | Brake released in reverse → reverse lamp only | Test | SWR-001, SWR-002, SWR-050 |
| QTC-06 | step:reverse-off | Reverse toggled off → lamps off | Test | SWR-001, SWR-002, SWR-009, SWR-050 |
| QTC-07 | auto:end-to-end-latency | For every step, (key → CARLA lamps) − (key → VCU status) ≤ 100 ms | Test | SWR-041 |
| QTC-08 | auto:resource-budget | `arm-none-eabi-size` of the release ELF: flash ≤ 64 KiB, static RAM ≤ 32 KiB | Analysis | SWR-042 |
| QTC-09 | auto:threadx-pinned | CMake pins the ThreadX revision; the fetched source is clean at that revision | Analysis | SWR-060 |
| QTC-10 | auto:shared-protocol-identity | `lights_protocol.c` SHA-256 equals the Linux controller's evidence | Analysis | SWR-061 |
| QTC-11 | auto:firmware-identity | Current build `.bin` SHA-256 equals the image used in SWE.5/SWE.6 | Analysis | SWR-060 |
| QTC-12 | manual:open | Board LEDs follow the four lamp states; Wi-Fi LED blinks at 1 Hz; Azure LED shows the link | Inspection | SWR-004, SWR-022 |
| QTC-13 | manual:reviewed | Review of fault paths: `require_tx`, stack error notify, vector table, `board_fault` | Inspection | SWR-030, SWR-031 |
| QTC-14 | manual:not-run | Timeout build (`-DZONAL_TIMEOUT_MS=1000`): lamps off after 1 s without input, then recovery | Test | SWR-006 |

## Pass criteria

- All automated and step cases pass.
- Manual cases record their inspection status.
- Open cases are listed as qualification gaps in the report.
