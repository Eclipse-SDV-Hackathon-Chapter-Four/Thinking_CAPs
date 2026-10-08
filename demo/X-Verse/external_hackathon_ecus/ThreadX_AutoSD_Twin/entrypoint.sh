#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Runs the ThreadX zonal lighting twin inside the AutoSD container, as
# ThreadX/README.md does on a host, but on the container's own vcan0:
#
#   VCU Zenoh status → Zenoh2CAN → vcan0 0x1F1 → ThreadX zonal controller
#   CARLA lights    ← Zenoh2CAN ← vcan0 0x1F4 ← brake/reverse decisions
#
# The bridge starts first so it receives the controller's startup OFF frame.
# On stop, the controller stops first so its final OFF frame reaches the
# vehicle, then the bridge.
#
# Environment: ZENOH_ENDPOINT (required), INPUT_TIMEOUT_MS (default 0).

set -euo pipefail

: "${ZENOH_ENDPOINT:?ZENOH_ENDPOINT is required}"
BRIDGE_LOG=/run/bridge.log

log() { echo "[autosd-twin] $*"; }

# The container has its own network namespace, so this vcan0 is private to it.
ip link add dev vcan0 type vcan
ip link set dev vcan0 up

python3 /opt/twin/configure_bridge.py --interface vcan0 --endpoint "$ZENOH_ENDPOINT" \
    --output /run/bridge.json > /dev/null

: > "$BRIDGE_LOG"
python3 /opt/twin/bridge.py /run/bridge.json >> "$BRIDGE_LOG" 2>&1 &
bridge=$!
tail -n +1 -F "$BRIDGE_LOG" &
tail_pid=$!

for _ in $(seq 1 40); do
    grep -q "Zenoh-CAN Bridge running" "$BRIDGE_LOG" && break
    kill -0 "$bridge" 2>/dev/null || { log "bridge exited; is a Zenoh router reachable at $ZENOH_ENDPOINT?"; exit 1; }
    sleep 0.5
done
grep -q "Zenoh-CAN Bridge running" "$BRIDGE_LOG" || { log "bridge did not come up"; exit 1; }

threadx-zonal-lights --interface vcan0 --timeout-ms "${INPUT_TIMEOUT_MS:-0}" &
controller=$!
log "running: ThreadX controller PID $controller, bridge PID $bridge, Zenoh $ZENOH_ENDPOINT"

stop() {
    trap - TERM INT
    log "stopping"
    kill -TERM "$controller" 2>/dev/null || true
    wait "$controller" 2>/dev/null || true
    sleep 1
    kill -TERM "$bridge" 2>/dev/null || true
    wait "$bridge" 2>/dev/null || true
    kill "$tail_pid" 2>/dev/null || true
    exit 0
}
trap stop TERM INT

# If either process ends on its own, stop the other and fail.
wait -n "$controller" "$bridge" || true
log "controller or bridge exited unexpectedly"
kill -TERM "$controller" "$bridge" 2>/dev/null || true
kill "$tail_pid" 2>/dev/null || true
exit 1
