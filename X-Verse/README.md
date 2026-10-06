# X-Verse integration components

This folder holds the Thinking CAPs additions to **X-Verse**, Capgemini
Engineering's vehicle simulation and integration environment. They connect
new devices and middleware to the X-Verse baseline (CARLA, the Zenoh VCU,
S-CORE) without modifying it. The baseline itself lives in the separate
`autoverse` workspace; see the [repository README](../README.md).

## X-COM communication bridges

| Bridge | Purpose | Status |
| --- | --- | --- |
| [Serial2CAN](bridges/serial2can/README.md) | Serial (SLCAN) ECUs ↔ X-Verse CAN bus (SocketCAN `vcan0` or rootless `udp_multicast`) | Tested with the ThreadX AZ3166 ECU on hardware and in live X-Verse + CARLA |

The X-COM layer also includes the Zenoh↔CAN, Zenoh↔SOME/IP and Zenoh↔ROS 2
bridges from the X-Verse baseline. Serial2CAN follows their conventions:

- `src/` with the bridge
- JSON configs in `config/`
- a `launch/bridge_launch.py` that prepares `vcan0`
- `tests/`
- a README

```text
             X-Verse (CARLA, VCU, S-CORE, Manual Control)
                              |
                            Zenoh
                              |
        Zenoh2CAN  |  Zenoh2SOME/IP  |  Zenoh2ROS 2      <- X-COM
              |
          CAN bus (vcan0 | udp_multicast)
              |
          Serial2CAN                                      <- this folder
              |
     serial ECUs: ThreadX AZ3166, OpenBSW S32K (planned)
```
