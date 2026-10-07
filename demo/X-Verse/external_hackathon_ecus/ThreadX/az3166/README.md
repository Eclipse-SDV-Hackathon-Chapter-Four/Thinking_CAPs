# ThreadX zonal lighting controller on the MXChip AZ3166

This is the [Linux zonal lighting controller](../README.md) ported to real
hardware: an MXChip AZ3166 board (STM32F412RG, Cortex-M4). It runs Eclipse
ThreadX's `cortex_m4/gnu` port, pinned to the same revision as the Linux build.
It uses the same `lights_protocol.c` and the same CAN IDs and bits.

The board has no CAN transceiver, so CAN frames travel over the ST-LINK USB
serial port as SLCAN (Lawicell) lines. X-Verse connects with the unchanged
Zenoh2CAN bridge using python-can's `slcan` interface. See the
[UART-CAN transport contract](docs/uart-can-transport.md).

```text
VCU Zenoh status → Zenoh2CAN (slcan) → UART "t1F1…" → ThreadX on AZ3166 → LEDs + OLED
CARLA lights    ← Zenoh2CAN (slcan) ← UART "t1F4…" ← brake/reverse decisions
```

## On the board

| Indicator | Meaning |
| --- | --- |
| RGB LED red | Brake light |
| User LED | Reverse light |
| Azure LED | X-Verse link up (SLCAN channel open) |
| Wi-Fi LED | ThreadX heartbeat, toggles every second |
| RGB LED blue | Fault stop (stack overflow, CPU fault, failed ThreadX call); lamps off |
| OLED | Link state, brake, reverse, frame counters, uptime |

ThreadX objects: three threads (control priority 10, SLCAN ingress 11, OLED 20),
a 256-entry byte queue fed by the USART6 interrupt, a 32-frame CAN queue, a
1 s timer with event flags, and two mutexes. The board layer is register-level C
with no vendor HAL. The only fetched dependency is ThreadX.

## Build

Requires the GNU Arm Embedded toolchain (`arm-none-eabi-gcc`, tested with
10.3-2021.07), CMake 3.20+, Ninja and Git.

```bash
sudo apt install -y gcc-arm-none-eabi cmake ninja-build git python3-venv
export THREADX_DIR="$HOME/autoverse/external_hackathon_ecus/ThreadX"
cd "$THREADX_DIR"
cmake -S az3166 -B build-az3166 -G Ninja -DCMAKE_BUILD_TYPE=MinSizeRel \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/az3166/cmake/arm-none-eabi.cmake"
cmake --build build-az3166
```

This produces `build-az3166/threadx-zonal-lights-az3166.{elf,bin,map}`, about
16.5 KB of flash and 16 KB of static RAM. CMake fetches ThreadX at the pinned
revision and refuses a modified checkout, as the Linux build does. Optional:
`-DZONAL_TIMEOUT_MS=1000` enables the input timeout, for periodic sources only.

The SLCAN codec has a host unit test in the Linux build. Run
`ctest --test-dir build` after the [Linux build](../README.md#build-on-linux).

## Flash

Connect the board's micro-USB port. The on-board ST-LINK appears as a USB drive
labelled `AZ3166` and as a serial port.

```bash
az3166/scripts/flash.sh            # default: build-az3166/threadx-zonal-lights-az3166.bin
```

The script copies the image to the drive and checks the ST-LINK's `FAIL.TXT`
report. It remounts the drive first with `udisksctl`. Without this, a second
flash in the same session can fail: the kernel's stale FAT view marks the drive
read-only. To do it by hand, copy the `.bin` to the drive.

## Connect to X-Verse

Find the serial port. Prefer the stable by-id path:

```bash
ls /dev/serial/by-id/ | grep STLink   # e.g. usb-STMicroelectronics_STM32_STLink_<serial>-if02
export AZ3166_PORT=/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_<serial>-if02
```

Your user needs access to the port (the `dialout` or `plugdev` group). Stop any
terminal using it, then follow the [Linux instructions](../README.md#connect-to-the-vehicle)
with these changes. No `vcan0` and no ThreadX process are needed; the
controller is the board.

1. Install the bridge's Python dependencies plus `pyserial`. The python-can
   `slcan` driver needs it.

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r az3166/requirements.txt
   ```

2. Generate the SLCAN bridge profile and start the unchanged bridge:

   ```bash
   .venv/bin/python scripts/configure_bridge.py --bus-type slcan \
     --interface "$AZ3166_PORT" --bitrate 500000 \
     --endpoint tcp/127.0.0.1:7447 --output build/bridge-az3166.json
   .venv/bin/python "$CAN_BRIDGE_DIR/src/bridge.py" build/bridge-az3166.json
   ```

   The Azure LED turns on, and the bridge publishes the board's current light
   state to Zenoh.

3. Start the vehicle as before (`python3 run_autoverse.py --enable-camera-display --vcu-zenoh`)
   and stop the Zephyr BCM. Brake and reverse now switch the LEDs on the board
   and the lights on the CARLA vehicle.

Stopping the bridge closes the channel. The board turns its lamps off and the
Azure LED goes dark.

**SocketCAN alternative (not tested here: needs root):**
`sudo slcand -o -c -s6 "$AZ3166_PORT" slcan0 && sudo ip link set slcan0 up`.
This exposes the board as `slcan0`. The original SocketCAN profile then works
with `--interface slcan0`, and `candump slcan0` / `cansend slcan0 1F1#06…`
behave as with `vcan0`.

For a direct check without X-Verse, use a serial terminal at 115200 8N1 with
CR line endings: send `O`, then `t1F180600000000000000`. The board replies
`z`, then `t1F480300000000000000`, and both lamps light.

## Hardware test

```bash
export TEST_RUN="az3166-$(date +%s)"
.venv/bin/python az3166/tests/hardware_smoke.py --port "$AZ3166_PORT" \
  --firmware build-az3166/threadx-zonal-lights-az3166.bin \
  --bridge-source "$CAN_BRIDGE_DIR/src/bridge.py" \
  --output "artifacts/runs/$TEST_RUN"
```

The test drives the real board through python-can's `slcan` driver, the code
path the bridge uses. It checks the raw Lawicell dialogue, all 256 status
bytes, 13 malformed or unrelated frames, ThreadX heartbeat timing and held
state, OLED health, the close fail-safe, and a four-state Zenoh round trip
through the unchanged bridge. Results go to the output directory. The
[recorded run](../artifacts/README.md#az3166-hardware-run) passed 11 of 11 checks.

## Live X-Verse + CARLA test

This test drives the complete X-Verse environment, with the board as its
lighting controller:

```text
Vehicle Manual Control (keys) → X-Verse VCU → Zenoh → Zenoh2CAN (slcan) → AZ3166/ThreadX
  → Zenoh2CAN → Zenoh → X-Verse virtual vehicle → CARLA actor light state
```

1. Start the Zenoh router: `zenohd -l tcp/127.0.0.1:7447`.
2. Start the bridge with the SLCAN profile, as in [Connect to X-Verse](#connect-to-x-verse).
3. Start X-Verse with `cd ~/autoverse && /usr/bin/python3 run_autoverse.py --enable-camera-display --vcu-zenoh`.
   Use an interpreter that has the CARLA 0.9.15 client, pygame, numpy, zenoh and evdev.
   X-Verse does not start the Zephyr BCM or a CAN bridge, so the board is the only lighting controller.
4. When the vehicle and the *Vehicle Manual Control* window are up, run:

   ```bash
   python3.10 -m venv .venv-carla
   .venv-carla/bin/pip install carla==0.9.15 pygame numpy python-xlib==0.33 -r az3166/requirements.txt
   .venv-carla/bin/python az3166/tests/xverse_carla_live.py --role-name ego_vehicle \
     --output "artifacts/runs/xverse-carla-$(date +%s)"
   ```

The test presses brake (`S`) and the reverse toggle (`Q`) in the Manual
Control window through X11 XTEST. It only types while that window has focus.
It walks through brake, reverse and both, and for each step requires all of the following:

- the VCU status on Zenoh
- the board's command on `vehicle/lights/frame`
- the matching `carla.VehicleLightState` bits on the actor (Brake 8, Reverse 64)

It also saves a rear-camera image for each step and then removes its camera.
It needs an X11 session; Wayland does not allow synthetic input.

## ASPICE evidence

[aspice/](aspice/README.md) contains SWE.1–SWE.6 work products:

- requirements, PlantUML architecture and detailed design, and coding guidelines
- unit, integration and qualification test specifications
- a generator for an HTML report with traceability, coverage and static analysis results

## Limitations

- CAN is simulated over UART. There is no CAN bit timing, arbitration, ACK
  slot or bus-off behaviour, and the SLCAN bitrate setting is nominal. A real
  CAN transceiver is outside this slice.
- The core runs from the internal HSI RC oscillator (±1%; measured about 0.6%
  fast). Running the PLL from the AZ3166's external HSE was tried: HSE reported
  ready, but the system did not come up from it, and a capture of HSE/26 saw no
  edges. This needs a debugger to resolve, so the crystal is not used.
- The lamps are the board's LEDs. Lamp timing is not measured electrically.
- No OpenSOVD/openDuT integration on this target yet; the Linux/AutoSD path keeps those.
- The live test operates Manual Control's keyboard. Steering, throttle and
  cruise control are not exercised, and S-CORE/SOME-IP run but are not checked.
