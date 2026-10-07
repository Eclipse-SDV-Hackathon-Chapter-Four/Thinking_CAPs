#!/bin/bash
# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: stand-in or Rust gateway of PR #40, three scenarios)
# Goal: Start-up script: console with the gateway stand-in or the Rust gateway, test vehicle, vehicle finder, checks, scenarios and tests.
#
# Start the v2 console in Ubuntu (WSL). Keep this window open while you demo.
#
#   ./run.sh                 gateway stand-in (PR #40 contract) + console on http://localhost:8080
#   VEHICLE_HOST=10.169.127.81 ./run.sh   same, with the real vehicle on that laptop (finds its Zenoh ports)
#   GATEWAY_BIN=~/sdv/review/cargo-pr40/target/debug/opensovd-gateway ./run.sh rust
#                            the real opensovd-gateway binary of feature/16-sovd-adapter-dataprovider + console
#   ./run.sh docker          gateway, this console, CDA + ECU simulator as containers (= ../OpenSOVD/ctl.sh up)
#   SOVD_URL=http://127.0.0.1:7690 ./run.sh   console only: a gateway you started yourself (Bazel or Cargo build)
#   ./run.sh find            list the Zenoh nodes on the network (to get VEHICLE_HOST)
#   ./run.sh vehicle         test vehicle on tcp/127.0.0.1:7447 (only when the real one is NOT running)
#   ./run.sh check           the 13 checks
#   ./run.sh scenario        the three scenarios against the test vehicle (automatic)
#   ./run.sh scenario-manual the three scenarios against the real vehicle (you act, it waits)
#   ./run.sh test            unit + end-to-end tests
#
# Settings are environment variables (see config.py), e.g. ZENOH_CONNECT=tcp/127.0.0.1:7447 ./run.sh
# Demo debounce of the gateway (stand-in and Rust binary, same variables as the Rust code):
#   CRUISE_DEBOUNCE_FAILED_MS (default here 1500; the Rust default is 5000) and CRUISE_DEBOUNCE_PASSED_MS (1000; Rust 2000).
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-$HOME/.venvs/demo-console-zenoh}"
PY="$VENV/bin/python"
LOGS="${LOGS:-/tmp/demo-console-zenoh}"
mkdir -p "$LOGS"
export CRUISE_DEBOUNCE_FAILED_MS="${CRUISE_DEBOUNCE_FAILED_MS:-1500}"
export CRUISE_DEBOUNCE_PASSED_MS="${CRUISE_DEBOUNCE_PASSED_MS:-1000}"
export SCORE_GATEWAY_ADDRESS="${SCORE_GATEWAY_ADDRESS:-127.0.0.1:7690}"
GW_PORT="${SCORE_GATEWAY_ADDRESS##*:}"

# ---- Python environment (once): a venv with eclipse-zenoh
if ! "$PY" -m pip --version >/dev/null 2>&1 && ! python3 -c "import ensurepip" >/dev/null 2>&1 \
   && python3 -c "import zenoh" >/dev/null 2>&1; then
  PY=python3   # no venv support, but the system Python already has eclipse-zenoh
elif ! "$PY" -m pip --version >/dev/null 2>&1; then
  if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
    echo "Python cannot create virtual environments yet. Run this once (it asks for your password):"
    echo "    sudo apt-get install -y python3-venv"
    exit 1
  fi
  rm -rf "$VENV"
  python3 -m venv "$VENV"
fi
if ! "$PY" -c "import zenoh" >/dev/null 2>&1; then
  echo "installing eclipse-zenoh into $VENV ..."
  "$PY" -m pip install -q --disable-pip-version-check -r "$DIR/requirements.txt"
fi

cd "$DIR"

# Stop whatever still listens on a port we need (an old console, the v1 fakes from hello_sdv.sh, ...).
free_port() {
  local port=$1 pids
  pids=$(ss -ltnpH "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2 | sort -u || true)
  for pid in $pids; do
    echo "port $port is used by: $(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null | cut -c1-90) -> stopping it"
    kill "$pid" 2>/dev/null || true
  done
  [ -n "$pids" ] && sleep 0.5
  if ss -ltnH "sport = :$port" 2>/dev/null | grep -q .; then
    echo "port $port is still in use. Stop that program, or set CONSOLE_PORT / SCORE_GATEWAY_ADDRESS to a free port."
    exit 1
  fi
}

# Warn early when the vehicle endpoint does not answer (the console still starts; the page shows 'connecting').
check_vehicle() {
  local ep host port
  if [ -n "${VEHICLE_HOST:-}" ] && [ -z "${ZENOH_CONNECT:-}" ]; then
    echo "looking for the vehicle's Zenoh endpoints on $VEHICLE_HOST (multicast scouting, a few seconds) ..."
    return 0
  fi
  local endpoints=${ZENOH_CONNECT:-tcp/127.0.0.1:7447}
  for ep in ${endpoints//,/ }; do
    host=${ep#*/}; port=${host##*:}; host=${host%:*}
    if ! timeout 2 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
      echo "warning: nothing answers at $ep. Is the vehicle running, and is this PC on the same network?"
      echo "         (this PC: $(hostname -I 2>/dev/null | cut -d' ' -f1); Windows side: ipconfig). Test vehicle: ./run.sh vehicle"
    fi
  done
}

# Wait until the gateway (stand-in or Rust) answers version-info.
wait_gateway() {
  local url="${SOVD_URL:-http://127.0.0.1:$GW_PORT}/sovd/version-info" i
  for i in $(seq 40); do
    if "$PY" -c "import sys,urllib.request; urllib.request.urlopen(sys.argv[1], timeout=1).read()" "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

start_console() {
  echo "Demo Console: open http://localhost:${CONSOLE_PORT:-8080} in your Windows browser (Ctrl+C here stops it)"
  "$PY" "$DIR/server.py"
}

case "${1:-console}" in
  console)
    free_port "${CONSOLE_PORT:-8080}"
    check_vehicle
    if [ -n "${SOVD_URL:-}" ]; then
      echo "SOVD_URL=$SOVD_URL set: not starting the stand-in, the console uses that gateway"
      wait_gateway || echo "warning: $SOVD_URL does not answer version-info yet (the page shows the gateway as down until it does)"
    else
      free_port "$GW_PORT"
      "$PY" "$DIR/score_app.py" > "$LOGS/standin.log" 2>&1 &
      STANDIN=$!
      trap 'kill $STANDIN 2>/dev/null || true' EXIT INT TERM
      for _ in $(seq 20); do
        grep -q "stand-in v" "$LOGS/standin.log" 2>/dev/null && break
        kill -0 $STANDIN 2>/dev/null || break
        sleep 0.25
      done
      if ! kill -0 $STANDIN 2>/dev/null; then
        echo "the gateway stand-in did not start:"; tail -3 "$LOGS/standin.log"; exit 1
      fi
      head -2 "$LOGS/standin.log"
    fi
    start_console
    ;;
  rust)
    # The real opensovd-gateway of PR #40. Build it in the inc_diagnostics checkout with
    #   bazel build //score/opensovd-gateway:opensovd-gateway    (needs the CR-13 fix of the Bazel dependency)
    # or with a Cargo workspace over the same sources (opensovd-core at rev 29e806f), then cargo build -p opensovd-gateway.
    : "${GATEWAY_BIN:?set GATEWAY_BIN=/path/to/opensovd-gateway (built from feature/16-sovd-adapter-dataprovider)}"
    [ -x "$GATEWAY_BIN" ] || { echo "GATEWAY_BIN=$GATEWAY_BIN is not an executable file"; exit 1; }
    free_port "${CONSOLE_PORT:-8080}"
    free_port "$GW_PORT"
    check_vehicle
    export SOVD_URL="${SOVD_URL:-http://127.0.0.1:$GW_PORT}"
    RUST_LOG="${RUST_LOG:-info}" "$GATEWAY_BIN" > "$LOGS/gateway.log" 2>&1 &
    GATEWAY=$!
    trap 'kill $GATEWAY 2>/dev/null || true' EXIT INT TERM
    if ! wait_gateway; then
      echo "the Rust gateway did not answer on $SOVD_URL:"; tail -5 "$LOGS/gateway.log"; exit 1
    fi
    echo "opensovd-gateway (Rust, PR #40) on $SOVD_URL - debounce failed $CRUISE_DEBOUNCE_FAILED_MS ms / passed $CRUISE_DEBOUNCE_PASSED_MS ms (log: $LOGS/gateway.log)"
    start_console
    ;;
  docker)
    # The whole OpenSOVD vECU in containers (gateway + this console + CDA + ECU simulator):
    # same as ../OpenSOVD/ctl.sh up, which run_autoverse.py also uses.
    exec "$DIR/../OpenSOVD/ctl.sh" up
    ;;
  vehicle)
    exec "$PY" "$DIR/vehicle_sim.py" "${@:2}"
    ;;
  find)
    exec "$PY" "$DIR/discover.py" "${@:2}"
    ;;
  check)
    exec "$PY" "$DIR/runner.py" "${@:2}"
    ;;
  scenario)
    exec "$PY" "$DIR/runner.py" --scenario all --sim-url "${SIM_CONTROL_URL:-http://127.0.0.1:7449}"
    ;;
  scenario-manual)
    exec "$PY" "$DIR/runner.py" --scenario all
    ;;
  test)
    exec "$PY" -m unittest discover -s "$DIR/tests" -v
    ;;
  *)
    sed -n '7,21p' "$0"
    exit 2
    ;;
esac
