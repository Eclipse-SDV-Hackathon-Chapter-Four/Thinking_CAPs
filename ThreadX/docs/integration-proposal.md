# ThreadX zonal lighting integration

The implemented first slice is a Linux-simulated zonal control unit for brake
and reverse lights, requested on 4 October 2026. It replaces the earlier generic
sensor/liveness application proposal. The application runs the actual Eclipse
ThreadX Linux/GNU port and preserves the existing Zephyr BCM CAN protocol.

See the [CAN lighting contract](can-lighting-contract.md),
[build/run instructions](../README.md) and [validation records](../artifacts/README.md).

The current path is VCU Zenoh status → Zenoh2CAN → SocketCAN → ThreadX lighting
controller → SocketCAN → Zenoh2CAN → existing CARLA vehicle light subscribers.
It can replace the Zephyr BCM for these two lights. Run a single lighting
controller and a single producer of its output Zenoh topics at a time.

The [AutoSD guest deployment](../../AutoSD/README.md) now runs this application
and Zenoh2CAN over a guest vxcan pair. The native OpenSOVD `zonal-lighting` App
belongs to `autosd-host` and exposes actual process observations and a labelled
integration-owned fault journal. The [managed Ethernet profile](../../AutoSD/docs/managed-network.md)
attaches a guest NIC to the openDuT bridge and tests real GRE interruption/recovery.
These do not replace the S-CORE diagnostic receiver or its native DFM pipeline.
Admission to the existing dashboard campaigns remains separate work.

Linux simulation establishes application and communication behavior. It does
not establish embedded hardware timing or production vehicle deployment.
