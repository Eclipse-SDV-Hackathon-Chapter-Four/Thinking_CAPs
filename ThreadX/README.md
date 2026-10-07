# ThreadX zonal lighting controller

This Linux emulator runs the actual Eclipse ThreadX RTOS using its GNU simulation
port. It replaces the Zephyr BCM's brake/reverse lighting function and uses the
existing Zenoh2CAN bridge to connect to the X-Verse vehicle. Application source,
configuration, tests and artifacts live in this folder.

```text
VCU Zenoh status → Zenoh2CAN → SocketCAN 0x1F1 → ThreadX zonal controller
CARLA lights    ← Zenoh2CAN ← SocketCAN 0x1F4 ← brake/reverse decisions
```

The [CAN contract](docs/can-lighting-contract.md) specifies standard eight-byte
frames, bit positions, startup/shutdown behavior and the optional input timeout.
Since version 1.1.0 the controller also answers UDS diagnostic requests on CAN
`0x7E1`/`0x7E9` (identification, lighting state, DTC `U0293` for a lost VCU status),
so the OpenBSW zonal diagnostic gateway (branch `feature/openbsw-diag-gateway`) can reach it as node
`0x1020`; see the contract's *Diagnostics* section.
The implementation uses two ThreadX threads, a bounded ThreadX queue, a timer and
event flags. It is Linux simulation; embedded deployment and hardware timing
are outside this implementation. The [AutoSD deployment](../AutoSD/README.md)
runs this controller and the gateway in a real guest, with a separate native
OpenSOVD lighting App and an optional managed openDuT Ethernet profile.
See the [integration plan](docs/integration-proposal.md).

**Real hardware:** the same controller also runs on an
[MXChip AZ3166 board](az3166/README.md) (STM32F412, ThreadX `cortex_m4/gnu`).
There, CAN frames are simulated over the board's USB UART with the SLCAN
protocol, and the unchanged Zenoh2CAN bridge connects it to X-Verse.

## Build on Linux

Use a Linux host with GCC, CMake 3.20+, Git, Python 3.10+ and SocketCAN support.
Docker is optional for running the controller and required for the isolated test
command below. The native binary uses the host architecture; no MCU emulator or
32-bit multilib toolchain is required.

```bash
sudo apt update
sudo apt install -y build-essential cmake git python3-venv can-utils iproute2
export SDV_WORKSPACE="${SDV_WORKSPACE:-$HOME}"
export THREADX_DIR="$SDV_WORKSPACE/eclipse_sdv_hackathon_2026/ThreadX"
export CAN_BRIDGE_DIR="$SDV_WORKSPACE/autoverse/bridges/can/can-zenoh-bridge-python"
cd "$THREADX_DIR"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 4
ctest --test-dir build --output-on-failure
./build/threadx-zonal-lights --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

CMake downloads [Eclipse ThreadX v6.5.1.202602a_rel](https://github.com/eclipse-threadx/threadx/tree/b91b03b9e75fa523b17127f9e0eca09dca916459)
at the immutable revision in [dependencies.lock.json](dependencies.lock.json).
It checks that the fetched ThreadX checkout matches that revision and has no
tracked modifications. ThreadX retains its MIT license; this application's
source follows the repository's Apache-2.0 license. Downloads and build products
are ignored by Git.

The upstream Linux port requires FIFO scheduling priorities 1–3. The native
run command below uses `sudo` for this requirement; a Docker run uses
`CAP_SYS_NICE` and an `rtprio` limit instead. The program reports a prerequisite
error if effective FIFO scheduling is unavailable.

## Connect to the vehicle

First provision X-Verse using the [Autoverse README](https://github.com/The-Xverse/autoverse/tree/dev/sdv-hackathon-2026).
Keep the Zenoh router on `tcp/127.0.0.1:7447` running. Start the controller and
bridge before the vehicle/VCU so they receive its initial state changes. Use
separate terminals and retain the environment variables above in each terminal.
Stop the Zephyr BCM and any other publisher of the same light commands.

1. Create the virtual CAN interface once:

   ```bash
   sudo modprobe vcan
   sudo ip link add dev vcan0 type vcan
   sudo ip link set dev vcan0 up
   ```

   If `vcan0` already exists, inspect it with `ip -details link show vcan0` and
   reuse it when appropriate. Do not recreate or delete an interface owned by
   another application. A configured physical SocketCAN interface can also be
   selected with `--interface`; physical CAN hardware has not been tested here.

2. Start the ThreadX lighting controller:

   ```bash
   cd "$THREADX_DIR"
   sudo ./build/threadx-zonal-lights --interface vcan0
   ```

   It logs JSON lines with component/version identity, accepted light states,
   heartbeat counters and shutdown. The default holds the latest state, matching
   the VCU's change-driven status publishing. Leave `--timeout-ms` at its default
   `0` for this integration. A periodic CAN source can use, for example,
   `--timeout-ms 1000`; timeout turns both lights off and valid input recovers.

3. Generate the lighting-only profile and run the existing bridge:

   ```bash
   cd "$THREADX_DIR"
   .venv/bin/python scripts/configure_bridge.py \
     --interface vcan0 --endpoint tcp/127.0.0.1:7447 \
     --output build/bridge.json
   .venv/bin/python "$CAN_BRIDGE_DIR/src/bridge.py" build/bridge.json
   ```

   This profile takes `vcu/control/reverse_sts` and `vcu/control/brake_sts` to CAN,
   then publishes the controller's `vehicle/lights/reverse_lights_cmd` and
   `vehicle/lights/brake_lights_cmd` as text booleans. It has no light-output
   subscriptions or CAN forwarding loop. The bridge source is unchanged.

4. Start the vehicle with the existing baseline command:

   ```bash
   cd "$HOME/autoverse"
   python3 run_autoverse.py --enable-camera-display --vcu-zenoh
   ```

   Apply the brake and toggle reverse in Vehicle Manual Control. The vehicle's
   existing subscribers update CARLA's brake and reverse light states. Observe
   the corresponding frames with `candump vcan0`. ThreadX and the bridge are
   separate services; this command does not supervise them.

For a direct CAN check without the vehicle, keep the controller running and send:

```bash
cansend vcan0 1F1#0600000000000000  # both lights → 1F4#0300000000000000
cansend vcan0 1F1#0200000000000000  # reverse only → 1F4#0100000000000000
cansend vcan0 1F1#0400000000000000  # brake only → 1F4#0200000000000000
cansend vcan0 1F1#0000000000000000  # both off
```

Stop ThreadX with Ctrl+C while the bridge is still running, allowing its final
lights-off frame to reach the vehicle. Then stop the bridge and the baseline.
Delete `vcan0` with `sudo ip link delete vcan0` only if you created it and no other
application uses it.

## Docker runtime and automated integration test

Build the controller image:

```bash
cd "$THREADX_DIR"
docker build -t threadx-zonal-lights:1.0 .
```

To run the controller on a previously prepared host `vcan0`, use this in place
of the native `sudo` command:

```bash
docker run --rm --init --network host --cap-add SYS_NICE \
  --ulimit rtprio=3:3 threadx-zonal-lights:1.0 \
  threadx-zonal-lights --interface vcan0
```

Run the test on a private virtual CAN bus and isolated local Zenoh endpoint:

```bash
export TEST_RUN="socketcan-$(date +%s)"
mkdir -p "$THREADX_DIR/artifacts/runs"
docker run --rm --init --network none \
  --cap-add NET_ADMIN --cap-add SYS_NICE --ulimit rtprio=3:3 \
  -v "$CAN_BRIDGE_DIR:/bridge:ro" \
  -v "$THREADX_DIR/artifacts/runs:/results" \
  threadx-zonal-lights:1.0 python3 tests/socketcan_smoke.py \
  --binary /usr/local/bin/threadx-zonal-lights \
  --interface txvcan0 --create-interface --bridge-source /bridge/src/bridge.py \
  --output "/results/$TEST_RUN"
```

The test checks all 256 status values over real SocketCAN, ignored malformed
frames, ThreadX heartbeat timing, held state, optional timeout/recovery, both
shutdown signals, and the actual bridge's four-state Zenoh round trip. It removes
only its own CAN interface. Results, binary/source hashes, CAN packets and logs
are preserved in the new output directory. This command does not start CARLA.

For an optional actual CARLA actor check, start a CARLA 0.9.15 server reachable
from Docker, then run:

```bash
cd "$THREADX_DIR"
docker build --build-arg WITH_CARLA=1 -t threadx-zonal-lights:1.0-carla .
export TEST_RUN="carla-$(date +%s)"
export TEST_CARLA_PORT="${TEST_CARLA_PORT:-2000}"
docker run --rm --init --add-host host.docker.internal:host-gateway \
  --cap-add NET_ADMIN --cap-add SYS_NICE --ulimit rtprio=3:3 \
  -v "$CAN_BRIDGE_DIR:/bridge:ro" \
  -v "$SDV_WORKSPACE/autoverse/bridges/carla:/vehicle:ro" \
  -v "$THREADX_DIR/artifacts/runs:/results" \
  threadx-zonal-lights:1.0-carla python3 tests/socketcan_smoke.py \
  --binary /usr/local/bin/threadx-zonal-lights \
  --interface txvcan0 --create-interface --bridge-source /bridge/src/bridge.py \
  --output "/results/$TEST_RUN" \
  --carla-host host.docker.internal --carla-port "$TEST_CARLA_PORT" \
  --vehicle-module /vehicle/examples/virtual_vehicle.py \
  --signals /vehicle/examples/signals_config.json
```

This verifies the existing vehicle controller/subscribers against a spawned
CARLA actor's actual light masks. The test removes its actor, leaves the server
running and does not change world settings. VCU status inputs are test fixtures.
See [validation artifacts](artifacts/README.md) for the recorded results.
