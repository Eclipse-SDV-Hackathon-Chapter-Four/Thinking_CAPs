#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Starts everything the demo needs and waits until it answers:
#   path B: ECU simulator (:8181) + CDA (:20002) via upstream docker compose
#   path A: the demo gateway (:7690), resources served by our adapter:
#           DEMO=hvac (default) the tested HVAC example,
#           DEMO=cruise cruise diag + the stand-in cruise control app, in process
#           DEMO=score  the full architecture: cruise diag -> cruise_bridge (mw::com) ->
#                       gatewayd -> someipd -> SOME/IP -> cruise ECU, in two containers
#                       (demo/score/, built with Bazel by demo/score/build.sh on first use)
#   live console (:8080): demo/live/server.py, the page for presenting
#
#   demo/start.sh          start both (DEMO=cruise demo/start.sh for cruise control)
#   demo/start.sh stop     stop both

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
COMPOSE="docker compose -f $ROOT/upstream/classic-diagnostic-adapter/testcontainer/docker-compose.yml"
DEMO=${DEMO:-hvac}
case $DEMO in
    hvac) GATEWAY_CRATE=opensovd-gateway ;;
    cruise|score) GATEWAY_CRATE=cruise-gateway ;;
    *) echo "DEMO must be hvac, cruise or score, not '$DEMO'" >&2; exit 2 ;;
esac
GATEWAY_BIN=$ROOT/demo/gateway/target/debug/$GATEWAY_CRATE
PIDFILE=$ROOT/demo/.gateway.pid
LOG=$ROOT/demo/.gateway.log
LIVE_PIDFILE=$ROOT/demo/.live.pid
LIVE_LOG=$ROOT/demo/.live.log
LIVE_PORT=${LIVE_PORT:-8080}

stop() {
    if [[ -f $PIDFILE ]] && kill "$(cat "$PIDFILE")" 2>/dev/null; then echo "gateway stopped"; fi
    rm -f "$PIDFILE"
    if [[ -f $LIVE_PIDFILE ]] && kill "$(cat "$LIVE_PIDFILE")" 2>/dev/null; then echo "live console stopped"; fi
    rm -f "$LIVE_PIDFILE"
    $COMPOSE down
    docker compose -f "$ROOT/demo/score/docker-compose.yml" down 2>/dev/null || true
}

wait_for() {
    local name=$1 url=$2
    for _ in $(seq 1 90); do
        if curl -s -o /dev/null -w '%{http_code}' "$url" | grep -q '^2'; then
            echo "  $name up: $url"
            return 0
        fi
        sleep 1
    done
    echo "  $name did not come up: $url" >&2
    return 1
}

if [[ ${1:-} == stop ]]; then
    stop
    exit 0
fi

echo "path B: CDA + ECU simulator"
SIM_CONTROL_PORT=8181 CDA_PORT=20002 $COMPOSE up -d
wait_for "ECU simulator" http://127.0.0.1:8181/
wait_for "CDA" http://127.0.0.1:20002/health/ready

if [[ $DEMO == score ]]; then
    echo "S-CORE nodes: vehicle computer + cruise ECU"
    [[ -x $ROOT/demo/score/out/bin/cruise_bridge ]] || "$ROOT/demo/score/build.sh"
    # always fresh containers: a stale LoLa state trips gatewayd (evidence/cruise-stage2/FINDINGS.md)
    started=$(date +%s)
    docker compose -f "$ROOT/demo/score/docker-compose.yml" up -d --force-recreate
    stats=$ROOT/demo/score/run/bridge.json
    subscribed() {  # written by this run's bridge, and subscribed
        [[ -f $stats && $(stat -c %Y "$stats") -ge $started ]] && grep -q '"subscribed":true' "$stats"
    }
    for _ in $(seq 1 30); do subscribed && break; sleep 1; done
    subscribed && echo "  cruise_bridge subscribed to the cruise ECU over SOME/IP" \
        || { echo "  cruise_bridge did not see the cruise ECU; see demo/score/run/*.log" >&2; exit 1; }
    export CRUISE_LINK=bridge
fi

echo "path A: demo gateway ($DEMO)"
if [[ -f $PIDFILE ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "  already running (pid $(cat "$PIDFILE"))"
else
    [[ -x $GATEWAY_BIN ]] || (cd "$ROOT/demo/gateway" && cargo build --bin "$GATEWAY_CRATE")
    HVAC_DEBOUNCE_FAILED_MS=${HVAC_DEBOUNCE_FAILED_MS:-5000} nohup "$GATEWAY_BIN" > "$LOG" 2>&1 &
    echo $! > "$PIDFILE"
fi
wait_for "gateway" http://127.0.0.1:7690/sovd/v1/components

echo "live console"
if [[ -f $LIVE_PIDFILE ]] && kill -0 "$(cat "$LIVE_PIDFILE")" 2>/dev/null; then
    echo "  already running (pid $(cat "$LIVE_PIDFILE"))"
else
    LIVE_PORT=$LIVE_PORT nohup python3 "$ROOT/demo/live/server.py" > "$LIVE_LOG" 2>&1 &
    echo $! > "$LIVE_PIDFILE"
fi
wait_for "live console" "http://127.0.0.1:$LIVE_PORT/"

echo
echo "ready - open http://127.0.0.1:$LIVE_PORT/  (traffic: tail -f demo/.live.log)"
echo "        or run: demo/run-demo.sh"
