#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# ctl.sh for the AutoSD digital twin of the ThreadX zonal lighting ECU.
#
# The twin runs the same ThreadX controller and the same Zenoh2CAN bridge
# profile as ThreadX/ (Linux port), inside an AutoSD container image, on the
# container's own vcan0. On Zenoh it does what the ThreadX ECU does:
#
#   vcu/control/*      → Zenoh2CAN → vcan0 0x1F1 → ThreadX zonal controller
#   vehicle/lights/*   ← Zenoh2CAN ← vcan0 0x1F4 ← brake/reverse decisions
#
# It publishes the same light commands as the AZ3166 board, so run one of them
# at a time: stop ThreadX/ctl.sh (the board's bridge) before `up`.
#
# Sources are only read from the ThreadX folder (THREADX_DIR) and the bridge checkout; build/ in
# this folder holds the staged Docker build context (ignored by Git).
#
# Environment overrides:
#   ZENOH_ENDPOINT  router as seen from the container
#                   (default tcp/host.docker.internal:7447, the host's router)
#   AUTOVERSE_ROOT  X-Verse checkout (default ../X-Verse if it has bridges/, else ~/autoverse)
#   CAN_BRIDGE_DIR  Zenoh2CAN bridge checkout ($AUTOVERSE_ROOT/bridges/can/can-zenoh-bridge-python)
#   AUTOSD_IMAGE    AutoSD base image (default: the pinned quay.io/centos-sig-automotive/autosd digest)

set -euo pipefail

if ( return 0 2>/dev/null ); then
  echo -e "\033[1;33mThis script is not meant to be sourced.\033[0m"
  exit 1
fi

TWIN_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# ThreadX sources: X-Verse's external_hackathon_ecus/ThreadX, synced next to this
# folder (demo/X-Verse), else ~/autoverse; THREADX_DIR overrides it.
if [[ -z "${THREADX_DIR:-}" ]]; then
    THREADX_DIR="$TWIN_DIR/../X-Verse/external_hackathon_ecus/ThreadX"
    [[ -d "$THREADX_DIR" ]] || THREADX_DIR="$HOME/autoverse/external_hackathon_ecus/ThreadX"
fi
THREADX_DIR="$(cd -- "$THREADX_DIR" && pwd)"

if [[ -z "${AUTOVERSE_ROOT:-}" ]]; then
    if [[ -d "$TWIN_DIR/../X-Verse/bridges" ]]; then
        AUTOVERSE_ROOT="$(cd -- "$TWIN_DIR/../X-Verse" && pwd)"
    else
        AUTOVERSE_ROOT="$HOME/autoverse"
    fi
fi
CAN_BRIDGE_DIR="${CAN_BRIDGE_DIR:-$AUTOVERSE_ROOT/bridges/can/can-zenoh-bridge-python}"
ZENOH_ENDPOINT="${ZENOH_ENDPOINT:-tcp/host.docker.internal:7447}"
AUTOSD_IMAGE="${AUTOSD_IMAGE:-quay.io/centos-sig-automotive/autosd@sha256:85b5718d7fc05c11794b379883578f0eaa59e5cf7ace1d0329ff332fbd0b3d2a}"

IMAGE="autosd-threadx-twin:latest"
CONTAINER="autosd-threadx-twin"
CONTEXT="$TWIN_DIR/build/context"

COMMAND="${1:-}"

usage() {
  cat <<EOF
Usage: $0 <command>
Runs the AutoSD digital twin of the ThreadX zonal lighting ECU in Docker.

Commands:
  up       Build the AutoSD twin image and start it (detached). Waits until
           the ThreadX controller is running and connected through the bridge.
  down     Stop the twin (the controller sends lights-off first), remove the
           container and the staged build context.
  status   Show the container state and its latest log lines.
  logs     Follow the twin's logs.
  help     Show this help message.

Examples:
  $0 up
  $0 status
  $0 down
EOF
  exit 0
}

log() { echo "[autosd-twin] $*"; }
die() { echo "[autosd-twin] $*" >&2; exit 1; }

lock_value() {
    python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d[sys.argv[2]][sys.argv[3]])' \
        "$THREADX_DIR/dependencies.lock.json" "$1" "$2"
}

# ---------------------------------------------------------------- helpers

check_prerequisites() {
    command -v docker > /dev/null || die "Docker is required."
    docker info > /dev/null 2>&1 || die "Docker is not reachable for this user."
    [[ -d /sys/module/vcan ]] || die "The host's vcan module is not loaded. Run once: sudo modprobe vcan"
    [[ -f "$CAN_BRIDGE_DIR/src/bridge.py" ]] || die "Zenoh2CAN bridge not found at $CAN_BRIDGE_DIR (set CAN_BRIDGE_DIR)."

    # Same pinned, unchanged bridge as ThreadX/dependencies.lock.json.
    local pinned actual
    pinned="$(lock_value bridge revision)"
    actual="$(git -C "$CAN_BRIDGE_DIR" rev-parse HEAD 2>/dev/null || true)"
    [[ "$actual" == "$pinned" ]] || die "Bridge checkout is at ${actual:-unknown}, expected pinned $pinned."
    git -C "$CAN_BRIDGE_DIR" diff --quiet HEAD -- src/bridge.py || die "Bridge source has local changes."

    if [[ "$ZENOH_ENDPOINT" == "tcp/host.docker.internal:7447" ]] \
            && ! (exec 3<> /dev/tcp/127.0.0.1/7447) 2> /dev/null; then
        die "No Zenoh router on host port 7447. Start X-Verse (it starts one) or:
  docker run -d --rm --name zenoh-router --network host eclipse/zenoh:1.3.4"
    fi
}

stage_context() {
    rm -rf "$CONTEXT"
    mkdir -p "$CONTEXT/threadx/tests" "$CONTEXT/threadx/scripts" "$CONTEXT/bridge" \
        "$CONTEXT/threadx/az3166/src" "$CONTEXT/threadx/az3166/tests"
    cp -r "$THREADX_DIR/src" "$CONTEXT/threadx/src"
    cp "$THREADX_DIR"/{CMakeLists.txt,requirements.txt,LICENSE,THREADX-LICENSE.txt} "$CONTEXT/threadx/"
    cp "$THREADX_DIR/tests/test_protocol.c" "$CONTEXT/threadx/tests/"
    # ThreadX's CMake build also runs the AZ3166 SLCAN codec host tests.
    cp "$THREADX_DIR"/az3166/src/slcan.{c,h} "$CONTEXT/threadx/az3166/src/"
    cp "$THREADX_DIR"/az3166/tests/test_slcan{,_edge}.c "$CONTEXT/threadx/az3166/tests/"
    cp "$THREADX_DIR/scripts/configure_bridge.py" "$CONTEXT/threadx/scripts/"
    cp "$CAN_BRIDGE_DIR/src/bridge.py" "$CONTEXT/bridge/"
    cp "$TWIN_DIR/entrypoint.sh" "$CONTEXT/"
}

container_state() {
    docker inspect -f '{{.State.Status}}' "$CONTAINER" 2> /dev/null || true
}

# ---------------------------------------------------------------- actions

do_up() {
    check_prerequisites
    if [[ "$(container_state)" == "running" ]]; then
        log "already running; use '$0 down' first to rebuild"
        return 0
    fi
    docker rm -f "$CONTAINER" > /dev/null 2>&1 || true

    log "staging sources from $THREADX_DIR and $CAN_BRIDGE_DIR"
    stage_context
    log "building $IMAGE on $AUTOSD_IMAGE ..."
    docker build -t "$IMAGE" --build-arg AUTOSD_IMAGE="$AUTOSD_IMAGE" \
        -f "$TWIN_DIR/Dockerfile" "$CONTEXT"

    log "starting $CONTAINER (Zenoh $ZENOH_ENDPOINT)"
    docker run -d --name "$CONTAINER" \
        --cap-add NET_ADMIN --cap-add SYS_NICE --ulimit rtprio=3:3 \
        --add-host host.docker.internal:host-gateway \
        -e ZENOH_ENDPOINT="$ZENOH_ENDPOINT" "$IMAGE" > /dev/null

    for _ in $(seq 1 60); do
        if docker logs "$CONTAINER" 2>&1 | grep -q '"event":"started"'; then
            log "twin is up; logs: $0 logs"
            return 0
        fi
        [[ "$(container_state)" == "running" ]] || break
        sleep 0.5
    done
    echo "Twin did not come up. Last log lines:" >&2
    docker logs --tail 20 "$CONTAINER" >&2 || true
    exit 1
}

do_down() {
    if [[ -n "$(container_state)" ]]; then
        log "stopping $CONTAINER ..."
        docker stop -t 15 "$CONTAINER" > /dev/null || true
        docker rm -f "$CONTAINER" > /dev/null 2>&1 || true
    fi
    rm -rf "$TWIN_DIR/build"
    log "stopped"
}

do_status() {
    local state
    state="$(container_state)"
    echo "container: $CONTAINER ${state:-not created}"
    echo "image:     $IMAGE"
    echo "zenoh:     $ZENOH_ENDPOINT"
    [[ -n "$state" ]] && docker logs --tail 5 "$CONTAINER" 2>&1 | sed 's/^/  /'
    [[ "$state" == "running" ]]
}

do_logs() {
    docker logs -f --tail 50 "$CONTAINER"
}

case "${COMMAND}" in
    up)     do_up ;;
    down)   do_down ;;
    status) do_status ;;
    logs)   do_logs ;;
    help|--help|-h|"") usage ;;
    *) echo "Unknown command: ${COMMAND}"; usage ;;
esac
