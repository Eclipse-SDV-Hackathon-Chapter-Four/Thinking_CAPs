# Software qualification test (SWE.6)

## Strategy

The bridge is qualified in its operational environment: the complete X-Verse
stack started with `run_autoverse.py --enable-camera-display --vcu-zenoh`. It
contains:

- CARLA 0.9.15, the VCU, S-CORE and the SOME/IP bridge
- Vehicle Manual Control, the virtual vehicle and Cuttlefish
- `zenohd`
- the unchanged Zenoh2CAN bridge on `udp_multicast`

Serial2CAN connects the bus to the physical AZ3166 ECU. The test presses brake
(S) and reverse (Q) in Manual Control. Expected results are the actor's
`carla.VehicleLightState` bits. Procedure:
[ThreadX/az3166/tests/xverse_carla_live.py](../../../../../ThreadX/az3166/tests/xverse_carla_live.py).
Results: [evidence/xverse-carla](../../evidence/xverse-carla/results.json).

Constraints are qualified by analysis. Configurations not available on this
machine are recorded as open.

## Qualification test cases

The report generator parses this table: ID | Source | Test case | Method | Verifies.
The source is `step:<name>` (live X-Verse run), `auto:<check>` (computed by
the generator) or `manual:<status>`.

| ID | Source | Test case | Method | Verifies |
| --- | --- | --- | --- | --- |
| QTC-01 | step:brake | Brake pressed → CARLA brake lamp (8) via VCU, Zenoh2CAN, Serial2CAN and the ECU | Test | SWR-005, SWR-006, SWR-009, SWR-032 |
| QTC-02 | step:brake-released | Brake released → lamps off (0) | Test | SWR-005, SWR-006, SWR-032 |
| QTC-03 | step:reverse | Reverse engaged → reverse lamp (64) | Test | SWR-005, SWR-006, SWR-032 |
| QTC-04 | step:reverse-and-brake | Brake in reverse → both lamps (72) | Test | SWR-005, SWR-006, SWR-032 |
| QTC-05 | step:reverse-brake-released | Brake released in reverse → reverse lamp (64) | Test | SWR-005, SWR-006, SWR-032 |
| QTC-06 | step:reverse-off | Reverse disengaged → lamps off (0) | Test | SWR-005, SWR-006, SWR-032 |
| QTC-07 | auto:end-to-end-latency | Every step: (key → CARLA lamp) − (key → VCU status) ≤ 100 ms | Test | SWR-031 |
| QTC-08 | auto:udp-multicast-in-x-verse | The live run used `udp_multicast` with echo suppression and no transmit errors | Analysis | SWR-009, SWR-011 |
| QTC-09 | auto:evidence-source-identity | Evidence was recorded with the current `serial2can_bridge.py`, `slcan.py` and configuration | Analysis | SWR-032 |
| QTC-10 | auto:dependency-alignment | python-can pin equals the X-Verse lock (`ThreadX/dependencies.lock.json`); tests run on Python 3.10 | Analysis | SWR-033 |
| QTC-11 | manual:not-run | SocketCAN `vcan0` deployment (needs root to create the interface) | Test | SWR-011 |
| QTC-12 | manual:not-run | Two physical serial ECUs on one bus (the S32K148 OpenBSW firmware lacks SLCAN) | Test | SWR-008 |

## Pass criteria

- All `step:` and `auto:` cases pass.
- `manual:` cases are reported as open qualification gaps.
