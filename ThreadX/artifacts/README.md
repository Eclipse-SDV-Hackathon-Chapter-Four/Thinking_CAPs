# ThreadX validation artifacts

The [Linux zonal lighting run](linux-zonal-lights/results.json) passed on
4 October 2026. It uses the actual ThreadX Linux/GNU simulation port, real
SocketCAN, the existing Zenoh2CAN bridge and an actual CARLA 0.9.15 vehicle actor.
VCU status inputs are fixtures. Physical CAN hardware, embedded deployment,
AutoSD and OpenSOVD/openDuT target admission were not exercised.

- [Build identity and source hashes](linux-zonal-lights/build.json): pinned RTOS
  revision, compiler, runtime image and application/configuration/test hashes.
- [Native protocol test](linux-zonal-lights/test-protocol.txt): all 256 status-byte
  values, DLC/ID/flag rejection, zeroed unused bytes and lights-off behavior.
- [Integration verdicts](linux-zonal-lights/results.json): 13 passed checks,
  including actual CAN transport, timer timing, timeout/recovery, signal cleanup,
  Zenoh round trip, vehicle lamp states and owned-resource cleanup.
- [CAN packets](linux-zonal-lights/bridge-packets.json) and
  [actual CARLA light masks](linux-zonal-lights/carla-lights.json): reverse `64`,
  brake `8`, both `72`, off `0`, through the existing vehicle controller.
- [Native ingress log](linux-zonal-lights/direct.jsonl),
  [timeout log](linux-zonal-lights/timeout.jsonl),
  [bridge/controller log](linux-zonal-lights/bridge-threadx.jsonl) and
  [bridge log](linux-zonal-lights/bridge.log).
- [Cleanup](linux-zonal-lights/cleanup.json): test actor/interface removed and
  the separately owned test server stopped.
- [Minimal Docker image test](linux-zonal-lights/minimal-image-results.json):
  the documented image without optional CARLA packages also passed all 11
  SocketCAN/Zenoh checks.

Generate new results with the [test instructions](../README.md#docker-runtime-and-automated-integration-test).
Disposable runtime outputs under `runs/` are ignored. Saved evidence establishes
the recorded execution, rather than the state of a currently running vehicle.

## AZ3166 hardware run

The [AZ3166 UART-CAN run](az3166-uart-can/results.json) passed all 11 checks on
6 October 2026. It used a physical MXChip AZ3166 running the ThreadX
`cortex_m4/gnu` port. CAN frames travelled as SLCAN over the ST-LINK USB UART.
VCU status inputs are fixtures, and CARLA was not running.

- [Build identity](az3166-uart-can/build.json): pinned ThreadX revision,
  toolchain, firmware/ELF hashes (reproduced from a clean build directory), the
  unchanged bridge's hash, and the hashes of the application, configuration and
  test sources.
- [Host unit tests](az3166-uart-can/test-host.txt): the shared lighting protocol
  and the SLCAN codec (256 status-byte round trips, extended/RTR frames,
  commands and 23 malformed lines).
- [Integration verdicts](az3166-uart-can/results.json):
  - the raw Lawicell dialogue
  - all 256 status bytes (USB+UART+ThreadX round trip: median 3.5 ms)
  - 13 rejected frame kinds
  - 1 s ThreadX heartbeat and held state
  - OLED health and zero transport losses
  - lamps off on channel close
  - a four-state Zenoh round trip through the unchanged Zenoh2CAN bridge (about 10 ms)
  - the individual VCU boolean topic
  - clean bridge shutdown
- [SLCAN frames](az3166-uart-can/slcan-frames.json),
  [heartbeat diagnostics](az3166-uart-can/diagnostics.json),
  [Zenoh samples](az3166-uart-can/zenoh-samples.json),
  [bridge profile](az3166-uart-can/bridge.json) and [bridge log](az3166-uart-can/bridge.log).

Not exercised: a physical CAN transceiver, the Linux `slcand` SocketCAN path,
a CARLA actor, and electrical lamp timing. The board LEDs and OLED were not
inspected visually; the OLED's health comes from its I2C acknowledgements.
Regenerate with the [hardware test](../az3166/README.md#hardware-test).
