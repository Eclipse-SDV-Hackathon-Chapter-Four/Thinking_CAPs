# Zonal lighting CAN contract

This component replaces the two-light behavior of
`zephyr-vecu/apps/can-bcm-vecu/src/main.c`. Dependency revisions are in
[dependencies.lock.json](../dependencies.lock.json).

| Frame | Classic standard CAN ID | DLC | Byte 0 |
| --- | --- | --- | --- |
| VCU status input | `0x1F1` | 8 | Bit 1 reverse status; bit 2 brake status |
| BCM light command output | `0x1F4` | 8 | Bit 0 reverse light; bit 1 brake light |

Only the two input bits affect output. Engagement bit 0 and other bytes are
ignored; unused output bits/bytes are zero. Extended-ID, RTR, error, unrelated-ID
and non-eight-byte inputs do not cause actuation. This profile uses classic CAN,
not CAN FD. Brake and reverse can be active independently or together.

The startup frame turns both lights off. Each accepted input produces a command
frame. By default, state is held until the next input, matching Zephyr and the
Python VCU's change-driven publishers. `--timeout-ms N` optionally turns both
lights off once input has been absent for N milliseconds, measured with the
Linux monotonic clock. A subsequent valid frame recovers immediately. Enable
this option only when the source sends periodic status; the existing bridge
deduplicates unchanged Zenoh samples.

SIGINT/SIGTERM sends a final lights-off frame and exits successfully. Startup
failures, invalid interfaces and CAN write failures return nonzero. Forceful
termination cannot send a final command. This is a demonstration policy.

Two actual ThreadX threads process SocketCAN ingress and lighting decisions
through a bounded 32-frame ThreadX queue. The ingress thread drains at most 32
frames per tick and yields. A ThreadX timer sets an event flag once per second;
the controller logs a heartbeat. SocketCAN and stdout use nonblocking host I/O.
Queue/log overflow is counted; CAN send failure is explicit. The upstream
simulation scheduler is pinned to one CPU from the process's allowed CPU set
and requires Linux FIFO scheduling priorities 1–3.

The dedicated bridge profile sends only `0x1F1` from Zenoh and publishes only
`0x1F4` back to Zenoh. It does not subscribe to light-output topics for CAN
transmission, avoiding a loop and competing control of the lamps.

| Zenoh input | CAN bit |
| --- | --- |
| `vcu/control/reverse_sts` | `0x1F1` byte 0 bit 1 |
| `vcu/control/brake_sts` | `0x1F1` byte 0 bit 2 |
| `vcu/control/cc_engage_sts` | `0x1F1` byte 0 bit 0, ignored by lighting |

| Zenoh output | CAN bit |
| --- | --- |
| `vehicle/lights/reverse_lights_cmd` | `0x1F4` byte 0 bit 0 |
| `vehicle/lights/brake_lights_cmd` | `0x1F4` byte 0 bit 1 |

Outputs use textual `true`/`false`, matching the existing CARLA subscribers.
The aggregate input `vcu/control/status` accepts the bridge's named-signal JSON
object. Aggregate output `vehicle/lights/frame` contains both named light values.
