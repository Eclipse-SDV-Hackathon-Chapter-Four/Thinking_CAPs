#!/usr/bin/env bash
# Run OpenBSW's own SIL suite (test/pyTest) against the S32K148EVB over Ethernet:
# UDS over DoIP (192.168.0.200), Ethernet and console tests. No CAN adapter is
# attached, so the target has no socketcan section and CAN-only tests are skipped
# or excluded (test_udsToolRDBI needs CAN). Results: <volume>/openbsw-sil/runs/board-<timestamp>/
#
#   contributions/eclipse-openbsw/OpenBSW/scripts/board-sil-test.sh [pytest paths...]   # default: uds enet
#
# ZGW_RTOS selects the reference app: THREADX (default, preset s32k148-threadx)
# or FREERTOS (preset s32k148-freertos); it is passed to the harness as --app.
#
# Needs: the reference app built with the matching preset, the PEmicro GDB
# server (scripts/board.sh server-start) and a route to 192.168.0.200.
set -euo pipefail
source "$(dirname "$0")/storage.sh"
BOARD="$(dirname "$0")/board.sh"

TOOLCHAIN="$OBSW_WORKSPACE/tools/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-eabi/bin"
app="${ZGW_RTOS:-THREADX}"; app="${app,,}"
ELF="$OBSW_SRC/build/s32k148-$app/executables/referenceApp/application/RelWithDebInfo/app.referenceApp.elf"
[[ -f "$ELF" ]] || { echo "error: $ELF not built (cmake --preset s32k148-$app)" >&2; exit 1; }
ping -c1 -W1 192.168.0.200 >/dev/null 2>&1 || echo "warning: 192.168.0.200 not reachable yet" >&2

"$BOARD" server-start > /dev/null
port="$("$BOARD" status | grep -o '/dev/ttyACM[0-9]*' | head -1)"

run="$OBSW_WORKSPACE/runs/board-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$run"
echo "$app" > "$run/rtos.txt"
# untracked target file: the pinned OpenBSW checkout keeps no tracked modification
cat > "$OBSW_SRC/test/pyTest/target_s32k148eth.toml" <<EOF
[serial]
port = "$port"
baudrate = 115200
write_byte_delay = 0.01
send_command_expected = "Console command succeeded"
send_command_timeout = 0.1
send_command_max_retries = 2

[eth]
ip_address = "192.168.0.200"

[$app.target_process]
command_line = "$TOOLCHAIN/arm-none-eabi-gdb -batch -x reset.gdb $ELF > /dev/null 2>&1"
wait_for_exit = true
skip_first = false

[boot]
started_str = "INFO: Run level 1"
complete_str = "DEBUG: Run level 9 done"
max_time = 1.5
EOF
cp "$OBSW_SRC/test/pyTest/target_s32k148eth.toml" "$run/"

# Flash once; the harness then resets the board before every test (target_process).
# Each reset drops the Ethernet link; the NetworkManager profile openbsw-board
# (autoconnect priority 100) restores 192.168.0.20 on enp67s0 after each drop.
"$BOARD" flash "$ELF" > "$run/flash.log" 2>&1
"$BOARD" reset "$ELF" > "$run/reset.log" 2>&1
for _ in $(seq 1 40); do ping -c1 -W1 192.168.0.200 >/dev/null 2>&1 && break; sleep 0.5; done
ping -c1 -W1 192.168.0.200 >/dev/null 2>&1 || { echo "error: board not reachable at 192.168.0.200" >&2; exit 1; }

tests=("$@"); [[ ${#tests[@]} -gt 0 ]] || tests=(uds enet --deselect uds/test_udsToolRDBI.py::test_rdbi)
cd "$OBSW_SRC/test/pyTest"
set +e
sg dialout -c "SERIAL_LOG_PATH='$run/serial.log' '$OBSW_VENV/bin/pytest' --target=s32k148eth --app=$app ${tests[*]} -q -p no:cacheprovider --junitxml='$run/junit.xml'" 2>&1 | tee "$run/pytest.txt"
status=${PIPESTATUS[0]}
set -e
echo "results: $run (pytest exit $status)"
exit "$status"
