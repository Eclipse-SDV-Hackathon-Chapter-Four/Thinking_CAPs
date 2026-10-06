# AutoSD vehicle computer: ThreadX zonal lighting

AutoSD hosts the vehicle lighting gateway, the actual Eclipse ThreadX Linux
simulation port, and a native Eclipse OpenSOVD provider in a QEMU/KVM VM.
CARLA and the VCU remain on the host. The optional openDuT profile attaches a
second guest Ethernet interface to the managed testbench and tests interruption
and recovery. This is an integration and feature development contribution for
Eclipse SDV Hackathon Track 2.

```text
Host VCU / CARLA ↔ Zenoh ↔ AutoSD guest Zenoh2CAN gateway (avcan1)
                                      ↕ SocketCAN vxcan pair
                          ThreadX zonal lighting controller (avcan0)
                                      ↓ process observations
                          Native OpenSOVD lighting App / HTTP
```

The guest is **Automotive Stream Distribution 10**, using its automotive kernel
and Podman. ThreadX and the gateway are separate processes in separate containers.
The pinned kernel includes `vxcan` but not `vcan`: frames sent on one endpoint
arrive at the other. Host CAN interfaces are separate from these guest interfaces.
The [ThreadX CAN contract](../ThreadX/docs/can-lighting-contract.md) is unchanged:
standard eight-byte `0x1F1` VCU status requests and `0x1F4` light responses.

## 1. Install prerequisites and select a workspace

Use an x86_64 Linux host with accessible KVM, Docker Engine, Git, Python 3.10+,
OpenSSH clients, and Rust/Cargo 1.89+ (validated with Rust 1.98.1). The guest uses
4 GiB RAM and two vCPUs. Allow about 12 GiB free for the image, overlay, container
and build caches; CARLA and the other vehicle assets need additional resources.
A graphical desktop/GPU is only needed for the existing vehicle demonstration.
The X-Verse bridge checkout requires GitHub SSH access to its repository, as in
the baseline setup.

On Ubuntu/Debian, install the host tools:

```bash
sudo apt update
sudo apt install -y qemu-system-x86 qemu-utils ovmf openssh-client git \
  python3-venv build-essential pkg-config
```

Install [Docker Engine](https://docs.docker.com/engine/install/) with access for
your normal user and [Rust through rustup](https://rustup.rs/) if absent.
On Fedora, the equivalent firmware package is `edk2-ovmf`.

Run subsequent commands from the companion repository root:

```bash
export SDV_WORKSPACE="${SDV_WORKSPACE:-$HOME}"
cd "$SDV_WORKSPACE/eclipse_sdv_hackathon_2026"
export AUTO_SD_STATE="AutoSD/.local/my-lighting-vm"
export AUTO_SD_BUNDLE="AutoSD/.local/my-workload.tar"
export AUTO_SD_RUN="AutoSD/artifacts/runs/lighting-$(date +%Y%m%d-%H%M%S)"
docker info >/dev/null
rustc --version
cargo --version
test -r /dev/kvm && test -w /dev/kvm
```

State and bundle paths must be new for a first installation. Keep the same
variables in subsequent terminals. Caches, VM disks, SSH keys and disposable
runs are ignored by Git. No host CAN interface, privileged host network setup,
or global SELinux change is required.

## 2. Prepare the pinned image and build the workload

[config/deployment.json](config/deployment.json) pins the dated AutoSD image URL
and SHA-256, guest resources, forwarded ports, bridge revision and Zenoh endpoint.
Preparation verifies the compressed image, expands it once, records the expanded
hash, and creates a private writable overlay and SSH key. It copies OVMF firmware
into the state directory. Internet access is required on first preparation/build.

```bash
python3 AutoSD/scripts/vm.py prepare --state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/prepare.json"
```

Use a separate pinned bridge checkout so an existing working tree need not be
changed. If the following source directory already exists, verify its revision
instead of cloning over it:

```bash
git clone --no-checkout git@github.com:The-Xverse/zenoh2can_bridge.git \
  AutoSD/.local/zenoh2can-source
git -C AutoSD/.local/zenoh2can-source checkout --detach \
  087c5f8a2e63e01c4213cd33161b64e50ffd047d
export AUTO_SD_BRIDGE="AutoSD/.local/zenoh2can-source/can-zenoh-bridge-python"
python3 AutoSD/scripts/build_workload.py --bridge-source "$AUTO_SD_BRIDGE" \
  --output "$AUTO_SD_BUNDLE"
```

The builder compiles the pinned ThreadX kernel/application, runs its C protocol
checks, packages the unchanged Zenoh2CAN bridge, and builds the native OpenSOVD
lighting provider using its [Cargo.lock](../OpenSOVD/integration/lighting-diagnostics/Cargo.lock). The bundle records
source, toolchain, container and file hashes. Both the transfer hash and the
bundle's file hashes are checked before guest provisioning.

Install host test dependencies:

```bash
/usr/bin/python3 -m venv AutoSD/.local/client
AutoSD/.local/client/bin/python -m pip install -r ThreadX/requirements.txt
```

## 3. Start the router, VM and guest services

The bridge connects from the guest to `tcp/10.0.2.2:7447`; QEMU user networking
maps that address to the host. Reuse the X-Verse router if it already listens on
host port 7447. Otherwise start a router in a separate terminal and leave it running:

```bash
docker run --init --rm --name autosd-lighting-router --network host \
  eclipse/zenoh:1.3.4 --listen tcp/127.0.0.1:7447
```

In the repository terminal:

```bash
python3 AutoSD/scripts/vm.py up --state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/up.json"
python3 AutoSD/scripts/vm.py deploy --state "$AUTO_SD_STATE" \
  --bundle "$AUTO_SD_BUNDLE" --output "$AUTO_SD_RUN/deploy.json"
python3 AutoSD/scripts/vm.py status --state "$AUTO_SD_STATE"
```

The first boot replaces the sample image's login keys with the generated key and
disables SSH password login. SSH is forwarded only on `127.0.0.1:2223`; diagnostics
on `127.0.0.1:7692`. The owned guest services are:

| Service | Purpose |
| --- | --- |
| `sdv-can` | Creates and raises the guest `avcan0`/`avcan1` pair |
| `sdv-image` | Loads the bundle into AutoSD's transient Podman storage on each boot |
| `sdv-zenoh-can` | Runs the lighting-only gateway on `avcan1` |
| `sdv-threadx` | Runs ThreadX on `avcan0` with FIFO scheduling capability |
| `sdv-lighting-diagnostics` | Exposes actual controller observations through OpenSOVD |

SELinux remains enforcing. The controller retains the latest light state because
the existing VCU publishes changes. Its default input timeout is `0`; silence
alone is not a fault. A restarted controller starts with lights off: change/reissue
VCU state, or restart the gateway before reissuing an identical deduplicated value.

## 4. Verify the guest and connect the existing vehicle

Run the automated fixture test with the interactive vehicle stopped:

```bash
AutoSD/.local/client/bin/python AutoSD/tests/lighting_smoke.py \
  --state "$AUTO_SD_STATE" --output "$AUTO_SD_RUN/smoke"
```

It checks four lighting states over host/guest Zenoh and real guest SocketCAN,
the VCU's individual text-boolean topic, native OpenSOVD discovery/observations,
controller shutdown/restart with retained fault history, and gateway interruption
and recovery. It temporarily stops only the guest lighting services, restores
them, and leaves lights off. The VM/router remain running.

For the interactive demonstration, provision X-Verse using its
[README](https://github.com/The-Xverse/autoverse/tree/dev/sdv-hackathon-2026), stop
other lighting controllers/publishers, then start the baseline after AutoSD:

```bash
cd "$HOME/autoverse"
python3 run_autoverse.py --enable-camera-display --vcu-zenoh
```

Brake and toggle reverse in Vehicle Manual Control. The existing CARLA
subscribers receive the guest's `vehicle/lights/brake_lights_cmd` and
`vehicle/lights/reverse_lights_cmd`. The baseline command does not supervise this
VM. Use the local-router profile for this interactive command.

For an automated check against an **already running** CARLA 0.9.15 server, install
its optional client packages and pass its actual RPC endpoint:

```bash
AutoSD/.local/client/bin/python -m pip install carla==0.9.15 pygame==2.6.1 numpy==2.2.6
export TEST_CARLA_HOST="${TEST_CARLA_HOST:-127.0.0.1}"
export TEST_CARLA_PORT="${TEST_CARLA_PORT:-2000}"
AutoSD/.local/client/bin/python AutoSD/tests/lighting_smoke.py \
  --state "$AUTO_SD_STATE" --output "$AUTO_SD_RUN/carla" \
  --carla-host "$TEST_CARLA_HOST" --carla-port "$TEST_CARLA_PORT" \
  --vehicle-module "$SDV_WORKSPACE/autoverse/bridges/carla/examples/virtual_vehicle.py" \
  --signals "$SDV_WORKSPACE/autoverse/bridges/carla/examples/signals_config.json"
```

This uses the unchanged vehicle controller/subscribers and reads the actor's
actual CARLA light masks: reverse 64, brake 8, combined 72 and off 0. Inputs are
VCU topic fixtures. It destroys only its own actor and leaves world settings and
the server unchanged. Do not run it alongside an interactive lighting producer.

## 5. Inspect diagnostics, CAN and logs

Start native discovery in a browser or with curl:

```bash
curl -fsS http://127.0.0.1:7692/sovd/v1 | python3 -m json.tool
curl -fsS http://127.0.0.1:7692/sovd/v1/apps/zonal-lighting/data/lighting.observation | python3 -m json.tool
curl -fsS http://127.0.0.1:7692/sovd/v1/apps/zonal-lighting/data/lighting.fault-history | python3 -m json.tool
python3 AutoSD/scripts/vm.py ssh --state "$AUTO_SD_STATE" \
  --command 'journalctl -u sdv-threadx -u sdv-zenoh-can --no-pager -n 40'
python3 AutoSD/scripts/vm.py ssh --state "$AUTO_SD_STATE" \
  --command 'podman exec sdv-zenoh-can candump avcan1'
```

The separate `zonal-lighting` App belongs to `autosd-host`; it does not replace
the S-CORE `cruise-control` App. Observations contain actual ThreadX identity,
light state and heartbeat counters. A stopped/expired observation is reported as
unavailable. Fault history is a bounded, persistent **integration-owned journal**
for controller availability and optional CAN input timeout, exposed through the
native OpenSOVD data provider. It is not the existing native DFM `/faults` pipeline.
The current shared web dashboard's Cruise Control/Test Manager views remain
specific to the S-CORE campaign; this lighting App is inspected through its own
OpenSOVD resources and saved test results.

Direct CAN and the all-256-values check use the gateway endpoint:

```bash
python3 AutoSD/scripts/vm.py ssh --state "$AUTO_SD_STATE" \
  --command 'podman exec sdv-zenoh-can cansend avcan1 1F1#0600000000000000'
python3 AutoSD/scripts/vm.py ssh --state "$AUTO_SD_STATE" \
  --command 'podman exec sdv-threadx python3 can_probe.py'
```

The probe also checks malformed frames, held state and timer timing, then sends
lights off. Run it only with fixture/interactive VCU publishers stopped.

For a separate periodic-CAN-source deployment, copy the deployment JSON, set
`lighting.timeout_ms` to a positive value, and pass that file through
`vm.py prepare --config <file>`. The retained optional-timeout check used `200`
and `podman exec sdv-threadx python3 can_probe.py --timeout`. Keep timeout `0`
for the existing change-driven VCU.

## 6. Stop and resume

Stop the interactive baseline in its terminal first. Shut down the owned AutoSD
services and VM while the router can still carry the controller's final OFF frame:

```bash
python3 AutoSD/scripts/vm.py down --state "$AUTO_SD_STATE" \
  --output "$AUTO_SD_RUN/down.json"
```

Then stop the router you started, with Ctrl+C in its terminal. The overlay and
fault journal are retained. To resume, start the same router and use `vm.py up`
with the same state; no preparation or deployment is needed. Use a new receipt
output path if requested. A fresh replication uses a new state directory and
bundle output, sharing only the verified base-image cache.

The [openDuT managed profile](docs/managed-network.md) adds the second Ethernet
interface and a real GRE interruption test. [Validation artifacts](artifacts/README.md)
record image identity, guest behavior, actual CARLA light masks and cleanup.
[Deployment notes](docs/integration-proposal.md) explain the current boundaries.

## Troubleshooting

| Symptom | Check/action |
| --- | --- |
| KVM/firmware prerequisite fails | Enable virtualization, grant your user KVM access, install OVMF; run `prepare` with a new state |
| Image download fails | Retry using the pinned dated URL/cache; if upstream retires it, supply a reviewed replacement config and revalidate its digest/deployment |
| Port already in use | Reuse the router or stop the instance you own; ports 2223/7692 must be free before VM startup |
| Bridge cannot connect | Keep the router running; inspect guest journal and the configured endpoint |
| `modprobe vcan` fails | This image uses the shipped `vxcan` pair; do not substitute the standalone host `vcan0` instructions |
| Services fail after reboot | Inspect `sdv-image` and its bundle archive, then the individual service logs |
| Same VCU value after a restart produces no command | The bridge deduplicates unchanged input; change state, or restart the gateway and reissue current state |
| Test output already exists | Choose a new output directory; receipts/evidence are never overwritten |

Image workflow references: [AutoSD sample images](https://sigs.centos.org/automotive/autosd-10/getting-started/autosd-sample-images.html)
and [AutoSD quick start](https://sigs.centos.org/automotive/autosd-10/getting-started/quick-start-guide.html).
