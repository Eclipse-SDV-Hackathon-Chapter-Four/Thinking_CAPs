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
