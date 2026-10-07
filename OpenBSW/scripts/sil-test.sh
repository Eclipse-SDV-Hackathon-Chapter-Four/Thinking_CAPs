#!/usr/bin/env bash
# Run OpenBSW's own SIL suite (test/pyTest, --target=posix) against the POSIX
# build: UDS over CAN and DoIP, Ethernet and DoCAN. Captures vcan0 with candump.
# Results go to <volume>/openbsw-sil/runs/sil-<timestamp>/.
#
# The suite transmits on many CAN IDs (0x7DF, 0x7E0/0x7E1, 0x600/0x601,
# 29-bit 0x18DAxxxx...). Do not run it while X-Verse uses vcan0.
#
#   OpenBSW/scripts/sil-test.sh [pytest paths...]     # default: uds enet docan
#
# ZGW_RTOS selects the reference app: THREADX (default, preset posix-threadx) or
# FREERTOS (preset posix-freertos); it is passed to the harness as --app.
set -euo pipefail
source "$(dirname "$0")/storage.sh"

for itf in vcan0 tap0; do
  ip link show "$itf" >/dev/null 2>&1 || { echo "error: $itf missing; run: sudo $OBSW_DIR/scripts/net-up.sh" >&2; exit 1; }
done

app="${ZGW_RTOS:-THREADX}"; app="${app,,}"
elf="$OBSW_SRC/build/posix-$app/executables/referenceApp/application/Release/app.referenceApp.elf"
[[ -x "$elf" ]] || { echo "error: $elf not built (scripts/bootstrap.sh posix-$app)" >&2; exit 1; }

run="$OBSW_WORKSPACE/runs/sil-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$run"
echo "$app" > "$run/rtos.txt"
export PATH="$OBSW_VENV/bin:$PATH"   # the suite's udsTool test calls a bare python3

candump -L vcan0 > "$run/vcan0.candump" &
dump_pid=$!
trap 'kill "$dump_pid" 2>/dev/null || true' EXIT

tests=("$@"); [[ ${#tests[@]} -gt 0 ]] || tests=(uds enet docan)
cd "$OBSW_SRC/test/pyTest"
set +e
SERIAL_LOG_PATH="$run/serial.log" pytest --target=posix --app="$app" "${tests[@]}" \
  -q -p no:cacheprovider --junitxml="$run/junit.xml" 2>&1 | tee "$run/pytest.txt"
status=${PIPESTATUS[0]}
set -e

awk '{split($3,a,"#"); print a[1]}' "$run/vcan0.candump" | sort | uniq -c | sort -rn > "$run/can-ids.txt"
echo "results: $run (pytest exit $status)"
exit "$status"
