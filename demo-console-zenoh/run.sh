#!/bin/bash
# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
# Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
# Created: 2026-10-06 · Latest version: 2026-10-07
# Goal: Start-up script: console, test vehicle, vehicle finder, checks, scenarios and tests.
#
# Start the v2 console in Ubuntu (WSL). Keep this window open while you demo.
#
#   ./run.sh                 cruise diag stand-in (Zenoh) + console on http://localhost:8080
#   VEHICLE_HOST=10.169.127.81 ./run.sh   same, with the real vehicle on that laptop (finds its Zenoh ports)
#   ./run.sh find            list the Zenoh nodes on the network (to get VEHICLE_HOST)
#   ./run.sh vehicle         test vehicle on tcp/127.0.0.1:7447 (only when the real one is NOT running)
#   ./run.sh check           the 13 checks
#   ./run.sh scenario        both scenarios against the test vehicle (automatic)
#   ./run.sh scenario-manual both scenarios against the real vehicle (you act, it waits)
#   ./run.sh test            unit + end-to-end tests
#
# Settings are environment variables (see config.py), e.g. ZENOH_CONNECT=tcp/127.0.0.1:7447 ./run.sh
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-$HOME/.venvs/demo-console-zenoh}"
PY="$VENV/bin/python"
LOGS="${LOGS:-/tmp/demo-console-zenoh}"
mkdir -p "$LOGS"

# ---- Python environment (once): a venv with eclipse-zenoh
if ! "$PY" -m pip --version >/dev/null 2>&1; then
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
export STATS_FILE="${STATS_FILE:-$LOGS/stats.json}"

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
    echo "port $port is still in use. Stop that program, or set CONSOLE_PORT / STANDIN_PORT to a free port."
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

case "${1:-console}" in
  console)
    free_port "${STANDIN_PORT:-7690}"
    free_port "${CONSOLE_PORT:-8080}"
    check_vehicle
    "$PY" "$DIR/score_app.py" > "$LOGS/standin.log" 2>&1 &
    STANDIN=$!
    trap 'kill $STANDIN 2>/dev/null || true' EXIT INT TERM
    for _ in $(seq 40); do   # up to 10 s: scouting for the vehicle takes a few seconds
      grep -q "stand-in v" "$LOGS/standin.log" 2>/dev/null && break
      kill -0 $STANDIN 2>/dev/null || break
      sleep 0.25
    done
    if ! kill -0 $STANDIN 2>/dev/null; then
      echo "the cruise diag stand-in did not start:"; tail -3 "$LOGS/standin.log"; exit 1
    fi
    head -3 "$LOGS/standin.log"
    echo "Demo Console: open http://localhost:${CONSOLE_PORT:-8080} in your Windows browser (Ctrl+C here stops it)"
    "$PY" "$DIR/server.py"
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
    sed -n '7,18p' "$0"
    exit 2
    ;;
esac
