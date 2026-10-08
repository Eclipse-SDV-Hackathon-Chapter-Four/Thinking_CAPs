# AutoSD deployment and integration notes

The initial proposal is implemented as a pinned AutoSD 10 QEMU/KVM development
VM, hosting ThreadX zonal lighting, the existing Zenoh2CAN gateway and a separate
native OpenSOVD lighting App. Follow the [README](../README.md) for installation,
local vehicle connection, verification and shutdown; the [managed profile](managed-network.md)
adds the actual openDuT Ethernet/GRE path.

The deployment uses the dated developer regular image, OVMF UEFI boot, an
unchanged verified base image and an owned writable overlay. A recorded workload
bundle supplies the container and native diagnostic binary. Services reload the
container on boot because AutoSD Podman storage is transient. ThreadX retains
its real RTOS threads/queue/timer through the Linux/GNU simulation port, using
FIFO priorities with guest container scheduling capability. SELinux stays enforcing.

The stock automotive kernel supplies vxcan rather than vcan. The controller and
gateway use opposite ends of a guest vxcan pair; all 256 status bytes and malformed
frames are checked through real SocketCAN. The message contract remains the
existing Zephyr BCM brake/reverse protocol. The default change-driven source
requires held state with no silence timeout; optional periodic-source timeout is
verified separately.

Native OpenSOVD discovery identifies `autosd-host` / `zonal-lighting`, with
`lighting.observation` and `lighting.fault-history` data resources. It reads actual
controller logs and a bounded persistent integration-owned fault journal. The
implementation/source belongs under OpenSOVD; guest provisioning belongs here.
It does not impersonate the S-CORE receiver or claim its native DFM fault pipeline.

The managed profile gives the guest a separate NIC at 192.168.123.103 and bridges
its actual Ethernet frames into peer B's openDuT-managed bridge. Zenoh then crosses
the real GRE path to peer A. Interrupting that link leaves management diagnostic
access available and holds the last light state; recovery restores command delivery.
CARLA checks use the existing subscriber/controller and the actor's measured masks.
VCU commands are labelled fixtures in automated tests.

[Artifacts](../artifacts/README.md) distinguish local/managed tests, image/kernel
identity, actual CARLA results, retained fault history, reboot and cleanup. The
existing physical Cruise Control campaign remains separate. Admission of lighting
to its shared dashboard/Test Manager and native DFM fault lifecycle is future work.
No physical CAN hardware or embedded ThreadX timing is claimed by this deployment.
