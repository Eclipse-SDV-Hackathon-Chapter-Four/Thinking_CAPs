# F012 implementation plan and decisions

1. Pin an upstream developer regular image by dated URL and SHA-256; create an
   unchanged shared base and private QEMU overlay, OVMF firmware and key-only SSH.
2. Package the existing ThreadX application/bridge and native OpenSOVD lighting
   provider. Preserve source pins, licenses, toolchain and bundle file identities.
3. Provision guest systemd services and actual SocketCAN. The selected stock
   kernel lacks vcan but supplies vxcan; use opposite endpoints. Preserve SELinux.
4. Expose a separate lighting diagnostic App reading real process observations,
   with a bounded persistent journal and explicit freshness/boot provenance.
5. Attach a second guest NIC through an owned TAP relay to the existing real
   openDuT managed bridge; test routing, GRE disturbance and recovery.
6. Validate actual CARLA light masks through unchanged vehicle classes; retain
   fixture attribution and destroy only the test actor.
7. Correct the README using findings, then repeat on a fresh overlay, separate
   pinned bridge clone and new native Cargo target. Verify reboot and teardown.

Findings incorporated: UEFI is required; fixed PCI/boot ordering avoids PXE when
adding the managed NIC; AutoSD transient Podman storage requires a boot image-load
service; vxcan endpoints differ from a standalone host vcan bus; unchanged Zenoh
values are deduplicated; bridge checkout requires GitHub SSH access; locked Cargo
inputs require Rust 1.89+. A separate management subnet avoids disturbing unrelated
bench resources; default Cruise Control network addressing remains unchanged.
