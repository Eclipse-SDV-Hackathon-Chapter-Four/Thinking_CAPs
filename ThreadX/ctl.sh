#!/usr/bin/env bash

# ctl.sh for the ThreadX zonal lighting controller on the MXChip AZ3166 board.
#
# The board is the lighting ECU; it talks SLCAN over the ST-LINK USB serial
# port. This script runs the unchanged Zenoh2CAN bridge against it, like the
# other vECU control scripts (start / stop / down / status / logs).
#
#   VCU Zenoh status → Zenoh2CAN (slcan) → USB 0x1F1 → ThreadX on AZ3166
#   CARLA lights    ← Zenoh2CAN (slcan) ← USB 0x1F4 ← brake/reverse decisions
#
# `start` launches a detached watchdog that owns the bridge. The bridge cannot
# reopen the port by itself, so when the board drops off USB (the kernel then
# re-enumerates it, often as another ttyACMn) the watchdog stops the bridge,
# waits for the board and starts a fresh bridge.
#
# Environment overrides:
#   AZ3166_PORT     serial device (default: the ST-LINK /dev/serial/by-id path)
#   CAN_BRIDGE_DIR  Zenoh2CAN bridge checkout
#   ZENOH_ENDPOINT  Zenoh router (default tcp/127.0.0.1:7447)
#   PYTHON          interpreter with python-can 4.2.2, pyserial and zenoh

set -euo pipefail

# Check if the script is being sourced.
if ( return 0 2>/dev/null ); then
  echo -e "\033[1;33mThis script is not meant to be sourced.\033[0m"
  exit 1
fi

THREADX_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SELF="$THREADX_DIR/ctl.sh"

CAN_BRIDGE_DIR="${CAN_BRIDGE_DIR:-$HOME/autoverse/bridges/can/can-zenoh-bridge-python}"
ZENOH_ENDPOINT="${ZENOH_ENDPOINT:-tcp/127.0.0.1:7447}"
PYTHON="${PYTHON:-python3}"

RUN_DIR="$THREADX_DIR/build/run"            # build/ is ignored by Git
BRIDGE_CFG="build/bridge-az3166.json"       # relative: also the kill pattern
PID_FILE="$RUN_DIR/watchdog.pid"
LOG_FILE="$RUN_DIR/bridge.log"

COMMAND="${1:-}"

usage() {
  cat <<EOF
Usage: $0 <command>
Runs the Zenoh2CAN bridge for the ThreadX zonal lighting controller on the
MXChip AZ3166 board (SLCAN over USB), with a reconnect watchdog.

Commands:
  start    Start the bridge (detached) and wait until the board's channel
           is open. The board's Azure LED turns on and the OLED shows
           X-Verse online.
  stop     Stop the bridge. It closes the SLCAN channel, so the board turns
           its lamps off.
  down     Same as stop, and also removes the generated bridge profile.
  restart  stop + start.
  status   Show the watchdog, bridge and board state.
  logs     Follow the bridge log.
  help     Show this help message.

Examples:
  $0 start
  $0 status
  $0 down
EOF
  exit 0
}

log() { echo "[threadx] $*"; }

# ---------------------------------------------------------------- helpers

board_port() {
    if [[ -n "${AZ3166_PORT:-}" ]]; then
        echo "$AZ3166_PORT"
        return
    fi
    local ports=(/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_*-if02)
    [[ -e "${ports[0]}" ]] && echo "${ports[0]}" || echo ""
}

watchdog_pid() {
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        echo "$pid"
    fi
}

bridge_pids() { pgrep -f -- "bridge.py $BRIDGE_CFG" || true; }

# Some processes can open the port only through the dialout group: the
# group is listed in /etc/group right after usermod, but a session gets it
# only after the next login. sg applies it without a password then.
needs_sg() {
    local port="$1"
    [[ -r "$port" && -w "$port" ]] && return 1
    id -nG | tr ' ' '\n' | grep -qx dialout && return 1
    getent group dialout | cut -d: -f4 | tr ',' '\n' | grep -qx "$(id -un)" && return 0
    echo "No access to $port. Run once: sudo usermod -aG dialout $(id -un)  (then log in again)" >&2
    exit 1
}

# ---------------------------------------------------------------- watchdog

# Runs detached (see do_start). Owns exactly one bridge at a time.
watchdog() {
    local bridge="" dev="" port
    echo $$ > "$PID_FILE"

    stop_bridge() {
        [[ -n "$bridge" ]] || return 0
        kill -TERM "$bridge" 2>/dev/null || true
        for _ in $(seq 1 25); do
            kill -0 "$bridge" 2>/dev/null || break
            sleep 0.2
        done
        kill -KILL "$bridge" 2>/dev/null || true
        wait "$bridge" 2>/dev/null || true
        bridge=""
    }
    trap 'log "watchdog stopping"; stop_bridge; rm -f "$PID_FILE"; exit 0' TERM INT

    while true; do
        port="$(board_port)"
        if [[ -z "$port" || ! -e "$port" ]]; then
            sleep 2 & wait $!
            continue
        fi
        dev="$(readlink -f "$port")"

        cd "$THREADX_DIR"
        if ! "$PYTHON" scripts/configure_bridge.py --bus-type slcan --interface "$port" \
                --bitrate 500000 --endpoint "$ZENOH_ENDPOINT" --output "$BRIDGE_CFG" > /dev/null; then
            log "could not generate $BRIDGE_CFG; retrying"
            sleep 5 & wait $!
            continue
        fi
        log "starting bridge on $port ($dev)"
        "$PYTHON" "$CAN_BRIDGE_DIR/src/bridge.py" "$BRIDGE_CFG" &
        bridge=$!

        # Healthy while the bridge runs, the board is still the same device
        # node, and the bridge is not stuck on a dead port.
        while kill -0 "$bridge" 2>/dev/null \
                && [[ -e "$port" && "$(readlink -f "$port")" == "$dev" ]] \
                && ! tail -n 3 "$LOG_FILE" | grep -q "Could not read from serial device"; do
            sleep 2 & wait $!
        done

        log "board disconnected or bridge exited; restarting when the board is back"
        stop_bridge
        sleep 2 & wait $!
    done
}

# ---------------------------------------------------------------- actions

do_start() {
    local pid port mark
    pid="$(watchdog_pid)"
    if [[ -n "$pid" ]]; then
        log "already running (watchdog PID $pid)"
        return 0
    fi

    port="$(board_port)"
    if [[ -z "$port" || ! -e "$port" ]]; then
        echo "AZ3166 board not found. Plug it in, or set AZ3166_PORT." >&2
        exit 1
    fi
    [[ -f "$CAN_BRIDGE_DIR/src/bridge.py" ]] || {
        echo "Zenoh2CAN bridge not found at $CAN_BRIDGE_DIR (set CAN_BRIDGE_DIR)." >&2
        exit 1
    }

    # A bridge left over from an older run would hold the port.
    pkill -TERM -f -- "bridge.py $BRIDGE_CFG" 2>/dev/null || true

    mkdir -p "$RUN_DIR"
    mark=1
    [[ -f "$LOG_FILE" ]] && mark=$(( $(wc -l < "$LOG_FILE") + 1 ))
    log "starting bridge for $port ..."
    if needs_sg "$port"; then
        setsid -f sg dialout -c "exec $(printf %q "$SELF") _watchdog" >> "$LOG_FILE" 2>&1 < /dev/null
    else
        setsid -f "$SELF" _watchdog >> "$LOG_FILE" 2>&1 < /dev/null
    fi

    # Wait until the bridge has opened the board's channel.
    for _ in $(seq 1 40); do
        if tail -n +"$mark" "$LOG_FILE" | grep -q "Zenoh-CAN Bridge running"; then
            log "bridge is up (watchdog PID $(watchdog_pid)); log: $LOG_FILE"
            return 0
        fi
        sleep 0.5
    done
    echo "Bridge did not come up within 20 s. Last log lines:" >&2
    tail -n 15 "$LOG_FILE" >&2
    do_stop > /dev/null
    exit 1
}

do_stop() {
    local pid
    pid="$(watchdog_pid)"
    if [[ -n "$pid" ]]; then
        log "stopping (watchdog PID $pid) ..."
        kill -TERM "$pid" 2>/dev/null || true
        for _ in $(seq 1 50); do
            kill -0 "$pid" 2>/dev/null || break
            sleep 0.2
        done
    fi
    # Also a bridge without a watchdog (e.g. started by hand).
    if [[ -n "$(bridge_pids)" ]]; then
        pkill -TERM -f -- "bridge.py $BRIDGE_CFG" 2>/dev/null || true
        sleep 1
        pkill -KILL -f -- "bridge.py $BRIDGE_CFG" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    log "stopped"
}

do_down() {
    do_stop
    rm -f "$THREADX_DIR/$BRIDGE_CFG"
}

do_status() {
    local pid port
    pid="$(watchdog_pid)"
    port="$(board_port)"
    echo "watchdog: ${pid:-not running}"
    echo "bridge:   $(bridge_pids | tr '\n' ' ')"
    if [[ -n "$port" && -e "$port" ]]; then
        echo "board:    $port -> $(readlink -f "$port")"
    else
        echo "board:    not connected"
    fi
    echo "log:      $LOG_FILE"
    [[ -f "$LOG_FILE" ]] && tail -n 5 "$LOG_FILE" | sed 's/^/  /'
    [[ -n "$pid" ]]
}

do_logs() {
    tail -n 50 -F "$LOG_FILE"
}

case "${COMMAND}" in
    start)     do_start ;;
    stop)      do_stop ;;
    down)      do_down ;;
    restart)   do_stop; do_start ;;
    status)    do_status ;;
    logs)      do_logs ;;
    _watchdog) watchdog ;;
    help|--help|-h|"") usage ;;
    *) echo "Unknown command: ${COMMAND}"; usage ;;
esac
