# Software integration test (SWE.5)

## Strategy

Integration is bottom-up, on the target:

1. The platform layers (ARC-01 … ARC-05) and ThreadX are integrated into the
   firmware image. The image builds warning-free and boots, which the SLCAN
   version reply confirms.
2. The protocol units and the application threads are integrated. They are
   tested through the external interface IF-01, using python-can's `slcan`
   driver, the same driver the bridge uses.
3. The unmodified Zenoh2CAN bridge and an isolated Zenoh peer are added
   (IF-08).

**Test environment:**

- physical MXChip AZ3166 flashed with the release image
- host Python 3.13, python-can 4.2.2, pyserial 3.5, eclipse-zenoh 1.3.4
- Zenoh2CAN bridge revision `087c5f8`

Procedure: [`az3166/tests/hardware_smoke.py`](../../tests/hardware_smoke.py).
Recorded results: [`artifacts/az3166-uart-can/results.json`](../../../artifacts/az3166-uart-can/results.json).
The generator confirms that the recorded firmware hash matches the current
build.

## Integration test cases

The report generator parses this table: ID | Check | Test case | Interfaces | Verifies.

| ID | Check | Test case | Interfaces | Verifies |
| --- | --- | --- | --- | --- |
| ITC-01 | raw-lawicell-dialogue | Close, version, serial, status/frame refusal while closed, bitrate/timestamp only while closed, 6 malformed lines, open, status | IF-01 | SWR-010, SWR-011, SWR-012, SWR-013 |
| ITC-02 | open-reports-current-command | python-can open: the first `0x1F4` is all-off | IF-01, IF-05 | SWR-007, SWR-008 |
| ITC-03 | all-256-status-bytes | Every status byte round-trips through UART, ISR, queues and both threads; p95 latency ≤ 20 ms | IF-01, IF-02, IF-03, IF-04 | SWR-001, SWR-002, SWR-014, SWR-040 |
| ITC-04 | malformed-and-unrelated-frames-ignored | 13 frame kinds produce no `0x1F4`; the rejected counter in `0x1F5` rises by 13 | IF-01, IF-03 | SWR-003, SWR-012 |
| ITC-05 | threadx-heartbeat-and-held-state | `0x1F5` interval 0.8–1.2 s with uptime +1 s; held state, with no `0x1F4` re-emission for 5 s | IF-06 | SWR-005, SWR-020 |
| ITC-06 | oled-status-display | OLED flag set in `0x1F5` (I2C init and flushes acknowledged) | IF-07 | SWR-023 |
| ITC-07 | no-transport-losses | Loss flag clear after the 256-frame burst | IF-02, IF-03, IF-04 | SWR-021, SWR-031 |
| ITC-08 | close-turns-lamps-off | Close then re-open reports all-off | IF-01, IF-05 | SWR-009 |
| ITC-09 | zenoh-bridge-az3166-roundtrip-four-light-states | Aggregate `vcu/control/status` → board → `vehicle/lights/*` for four states | IF-08 | SWR-050 |
| ITC-10 | individual-vcu-boolean-topic | `vcu/control/brake_sts` text boolean → brake on | IF-08 | SWR-050 |
| ITC-11 | bridge-clean-shutdown | Bridge exits 0; its close leaves the board in the safe state | IF-01, IF-08 | SWR-009, SWR-050 |

## Pass criteria

- All checks pass, using the same firmware image as the current build.
