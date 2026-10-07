# AutoSD digital twin of the ThreadX zonal lighting ECU

This folder runs a digital twin of the [ThreadX zonal lighting controller](../../ThreadX/README.md)
in an AutoSD container. It does what the ThreadX ECU does: it takes the VCU
status from Zenoh, decides the brake and reverse lights, and publishes the light
commands that CARLA's vehicle subscribes to.

```text
vcu/control/*     → Zenoh2CAN → vcan0 0x1F1 → ThreadX zonal controller
vehicle/lights/*  ← Zenoh2CAN ← vcan0 0x1F4 ← brake/reverse decisions
                 (inside the autosd-threadx-twin container)
```

The twin uses the same sources and contract as `ThreadX/`, without changing them:

- the ThreadX controller (`ThreadX/src`), built against the pinned Eclipse ThreadX revision
- the [CAN lighting contract](../../ThreadX/docs/can-lighting-contract.md) (`0x1F1` in, `0x1F4` out)
- the bridge profile generator `ThreadX/scripts/configure_bridge.py`
- the Zenoh2CAN bridge at the revision pinned in `ThreadX/dependencies.lock.json`

The image is built in two stages. The controller is compiled on CentOS Stream 9.
It runs on the CentOS Automotive SIG's AutoSD container image
`quay.io/centos-sig-automotive/autosd`, together with Python, the bridge and its
pinned `eclipse-zenoh`/`python-can` packages. That image is CentOS Stream 9 with
the AutoSD automotive package repositories, and is pinned by digest. Its only
published tag is `latest`, from July 2025. The container creates its own
`vcan0` in its own network namespace, so the host needs no CAN interface.

## Prerequisites

- Docker, usable by your user.
- The host's `vcan` kernel module, loaded once with `sudo modprobe vcan`. The container
  creates its interface but cannot load kernel modules.
- A Zenoh router on host port 7447 that listens on all interfaces. X-Verse starts
  one (`eclipse/zenoh:1.3.4` on the host network). Without X-Verse, run:
  `docker run -d --rm --name zenoh-router --network host eclipse/zenoh:1.3.4`.
  A router started with `-l tcp/127.0.0.1:7447` is not reachable from containers.
- The Zenoh2CAN bridge checkout at the pinned revision. It is found as in `ThreadX/ctl.sh`:
  `demo/X-Verse/bridges/...`, else `~/autoverse/bridges/...`. Set `CAN_BRIDGE_DIR` to override.
- Internet access for the first build: base images, ThreadX sources and Python packages.

## Use

```bash
demo/autosd-twin/ctl.sh up       # build the image and start the twin
demo/autosd-twin/ctl.sh status   # container state and latest log lines
demo/autosd-twin/ctl.sh logs     # follow the controller and bridge logs
demo/autosd-twin/ctl.sh down     # stop (lights off first) and remove the container
```

The twin publishes the same light commands as the AZ3166 board. Run only one of
them: stop the board's bridge (`ThreadX/ctl.sh down`) before `up`. Then start
X-Verse as usual, and brake or toggle reverse in Vehicle Manual Control. The
CARLA vehicle's lights follow the twin's decisions.

`ctl.sh up` stages the sources into `build/` (ignored by Git) and builds
`autosd-threadx-twin:latest`. It then starts the `autosd-threadx-twin` container
and waits for the ThreadX controller's `started` event. `down` stops the
controller before the bridge, so its final lights-off command reaches the vehicle.

| Variable | Default | Purpose |
| --- | --- | --- |
| `ZENOH_ENDPOINT` | `tcp/host.docker.internal:7447` | Zenoh router, as seen from the container |
| `AUTOVERSE_ROOT` / `CAN_BRIDGE_DIR` | as in `ThreadX/ctl.sh` | Bridge checkout |
| `AUTOSD_IMAGE` | `quay.io/centos-sig-automotive/autosd@sha256:85b5…3d2a` | AutoSD base image |

## Limits

- The container provides AutoSD's user space: packages, C library and Python.
  It runs on the host's kernel, not the AutoSD automotive kernel. For a full AutoSD
  guest with its own kernel, see [AutoSD/](../../AutoSD/README.md).
- The controller is the ThreadX Linux simulation port, so its timing is not the
  AZ3166 board's. Board-only parts (UART/SLCAN, LEDs, OLED) are not modelled.
