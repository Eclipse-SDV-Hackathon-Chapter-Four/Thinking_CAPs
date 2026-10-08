# AutoSD on the openDuT managed Ethernet path

This optional profile adds a second virtio Ethernet interface to the AutoSD VM.
The host CARLA/test client connects to a Zenoh router in peer A. The guest gateway
connects to that router through peer B's managed Ethernet bridge and the real
openDuT GRE link. SSH and native OpenSOVD HTTP retain their separate QEMU
management path.

```text
Host CARLA / fixture client → peer A Zenoh router (192.168.123.101:7447)
                              ↕ openDuT-managed GRE
                           peer B br-opendut ↔ owned TAP/Ethernet relay
                                              ↕ QEMU virtio NIC
                                      AutoSD guest 192.168.123.103
                                              ↕ Zenoh2CAN / ThreadX
Host OpenSOVD client → localhost:7692 → separate guest management NIC
```

The guest is an end station attached to peer B's managed bridge. CARL/EDGAR/CLEO
remain the real matched openDuT 0.10.2 components from the existing bench. The
Ethernet relay uses QEMU's framed socket transport and a nonpersistent TAP in
peer B's namespace; it transports actual Ethernet frames. This local profile
uses GRE with VPN/OIDC disabled; no remote-site VPN behavior is claimed.

## Bring up the managed profile

First complete the [AutoSD README](../README.md) through its local lighting test,
keeping the same `AUTO_SD_STATE`, `AUTO_SD_RUN`, `SDV_WORKSPACE` variables and
repository working directory. Keep interactive VCU/lighting publishers stopped.
The host needs Docker and `/dev/net/tun`; the helpers have `NET_ADMIN` only in the
selected peer namespace. Host network interfaces are not modified by the relay.

Choose an unused management subnet. The commands select `172.30.78.0/24`; the
existing S-CORE bench defaults to `172.30.77.0/24`. Preparation/up refuses route
or Docker subnet overlap. The DUT network remains `192.168.123.0/24` inside the
peer/guest namespaces.

```bash
export AUTO_SD_BENCH="AutoSD/.local/my-opendut"
python3 OpenDut/scripts/opendut_testbench.py prepare \
  --management-subnet 172.30.78.0/24 --state "$AUTO_SD_BENCH" \
  --output "$AUTO_SD_RUN/opendut-prepare"
python3 OpenDut/scripts/opendut_testbench.py up --state "$AUTO_SD_BENCH" \
  --output "$AUTO_SD_RUN/opendut-up"
python3 AutoSD/scripts/vm.py down --state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/before-managed-down.json"
python3 AutoSD/scripts/managed_network.py up \
  --bench-state "$AUTO_SD_BENCH" --vm-state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/managed-attach.json"
```

The attachment receipt reports `qemu_endpoint` and `host_zenoh_endpoint`. With
this selected subnet they are `172.30.78.12:19092` and `tcp/172.30.78.11:7447`.
Use the values in your receipt if you selected another subnet:

```bash
python3 AutoSD/scripts/vm.py up --state "$AUTO_SD_STATE" \
  --dut-endpoint 172.30.78.12:19092 --output "$AUTO_SD_RUN/managed-vm-up.json"
python3 AutoSD/scripts/managed_network.py configure \
  --bench-state "$AUTO_SD_BENCH" --vm-state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/managed-configure.json"
```

Configuration gives the second NIC `192.168.123.103/24` without a default route,
connects the guest gateway to `tcp/192.168.123.101:7447`, and checks the actual
route and guest-to-peer ping. No route to this peer is supplied by the management
NIC. The fixed PCI slots keep the boot disk stable when the second NIC is added.

## Test interruption and recovery

```bash
AutoSD/.local/client/bin/python AutoSD/tests/lighting_smoke.py \
  --state "$AUTO_SD_STATE" --endpoint tcp/172.30.78.11:7447 \
  --bench-state "$AUTO_SD_BENCH" --output "$AUTO_SD_RUN/managed-smoke"
```

The test runs the normal lighting/diagnostic/restart checks, then disables the
actual peer A GRE interface. A changed input cannot reach the controller; the
last CAN state is held. The management OpenSOVD resource stays reachable and
shows the controller heartbeat. Restoring the tunnel and sending current state
recovers lighting. The default change-driven CAN contract does not clear lights
or raise a CAN timeout merely because no command arrives.

To include the real CARLA actor check, use an existing 0.9.15 server and the
optional Python packages installed in the AutoSD README:

```bash
AutoSD/.local/client/bin/python AutoSD/tests/lighting_smoke.py \
  --state "$AUTO_SD_STATE" --endpoint tcp/172.30.78.11:7447 \
  --bench-state "$AUTO_SD_BENCH" --output "$AUTO_SD_RUN/managed-carla" \
  --carla-host "$TEST_CARLA_HOST" --carla-port "$TEST_CARLA_PORT" \
  --vehicle-module "$SDV_WORKSPACE/autoverse/bridges/carla/examples/virtual_vehicle.py" \
  --signals "$SDV_WORKSPACE/autoverse/bridges/carla/examples/signals_config.json"
```

The existing vehicle subscriber connects to peer A, and actual actor light masks
are checked. The fixture test restores the tunnel and services and removes only
its own actor. It leaves the VM, helper containers and bench running.

## Restore the local profile and clean up

While the VM is running, return the gateway to the host router from the AutoSD
README. Keep that router running for this step:

```bash
python3 AutoSD/scripts/managed_network.py local \
  --bench-state "$AUTO_SD_BENCH" --vm-state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/local-restored.json"
python3 AutoSD/scripts/vm.py down --state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/managed-vm-down.json"
python3 AutoSD/scripts/managed_network.py down \
  --bench-state "$AUTO_SD_BENCH" --vm-state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/managed-removed.json"
python3 OpenDut/scripts/opendut_testbench.py down --state "$AUTO_SD_BENCH" \
  --output "$AUTO_SD_RUN/opendut-down"
```

The helper checks ownership labels before removing its containers; closing the
TAP descriptor removes that interface. The bench removes only its own enrolled
resources. The guest overlay/fault history remain available for a normal local
`vm.py up`. Stop only the host router you started, after the guest shuts down.

For a managed-only shutdown, omit `local`: shut down the VM, remove the helpers,
then remove the bench. Its saved guest state retains the managed endpoint. On
resume, redeploy that bench and its helpers **before** starting the VM, then
check `configure`/ping and use new evidence output paths. Enrollment certificates
expire after seven days; prepare a new bench after expiry.

## Validation boundaries

Saved [artifacts](../artifacts/README.md) include real guest OS/kernel identity,
CAN/light state, native OpenSOVD responses, guest routing and GRE traffic,
interruption/recovery, actor cleanup and owned resource teardown. Controller
fault history is the integration-owned journal described in the AutoSD README.
Admission to the shared S-CORE dashboard campaign and its native DFM fault
pipeline remains separate work.
