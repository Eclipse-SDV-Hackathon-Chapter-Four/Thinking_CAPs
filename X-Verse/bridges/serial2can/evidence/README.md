# Serial2CAN evidence

Recorded on 6 October 2026 with python-can 4.2.2, pyserial 3.5 and Python 3.10.12.

| Run | Result | Content |
| --- | --- | --- |
| [hardware-check](hardware-check/results.json) | passed, 6/6 | Physical MXChip AZ3166 (ThreadX lighting firmware `cfa556a4…`) on `udp_multicast`; [bridge log](hardware-check/bridge.log) with final counters |
| [xverse-carla](xverse-carla/results.json) | passed, 6/6 steps | Full `run_autoverse.py --enable-camera-display --vcu-zenoh` stack; Manual Control keys → VCU → Zenoh2CAN (unchanged, `udp_multicast`) → Serial2CAN → AZ3166 → CARLA light state; [images](xverse-carla/images/), [Zenoh samples](xverse-carla/zenoh-samples.json), [Serial2CAN log](xverse-carla/serial2can.log), [Zenoh2CAN profile](xverse-carla/zenoh2can-udp.json) |

Source SHA-256 at test time are recorded in [manifest.json](manifest.json); the ASPICE report generator verifies them against the current sources.
