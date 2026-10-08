#!/usr/bin/env bash
# Build the zonal gateway for the S32K148EVB, flash it and run the board
# integration tests (gateway/tests/test_board.py) over DoIP at 192.168.0.200.
# Results: <volume>/openbsw-sil/runs/board-it-<timestamp>/; a full run is
# recorded in contributions/eclipse-openbsw/OpenBSW/evidence/board-gateway-it/.
#
#   contributions/eclipse-openbsw/OpenBSW/scripts/board-it.sh [pytest args...]
#
# ZGW_RTOS selects the RTOS: THREADX (default) or FREERTOS. Each RTOS has its
# own build directory.
set -euo pipefail
source "$(dirname "$0")/storage.sh"
BOARD="$(dirname "$0")/board.sh"
export PATH="$OBSW_WORKSPACE/tools/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-eabi/bin:$OBSW_VENV/bin:$PATH"

rtos="${ZGW_RTOS:-THREADX}"
build="$OBSW_WORKSPACE/build/gateway-s32k148-${rtos,,}"
if [[ ! -f "$build/build.ninja" ]]; then
  CC=arm-none-eabi-gcc CXX=arm-none-eabi-g++ cmake -S "$OBSW_DIR/gateway" -B "$build" -G Ninja \
    -DOPENBSW_DIR="$OBSW_SRC" -DBUILD_TARGET_PLATFORM=S32K148EVB -DBUILD_TARGET_RTOS="$rtos" \
    -DCMAKE_TOOLCHAIN_FILE="$OBSW_SRC/cmake/toolchains/ArmNoneEabi.cmake" \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo "-DCMAKE_C_FLAGS_RELWITHDEBINFO=-g3 -O2 -DNDEBUG" \
    "-DCMAKE_CXX_FLAGS_RELWITHDEBINFO=-g3 -O2 -DNDEBUG" -DCMAKE_ASM_FLAGS_RELWITHDEBINFO=-g3 > /dev/null
fi
cmake --build "$build" --parallel "$(nproc)" > /dev/null

export ZGW_ELF="$build/app/application/openbsw-zonal-gw.elf"
export ZGW_IP=192.168.0.200
export ZGW_RESULTS="${ZGW_RESULTS:-$OBSW_WORKSPACE/runs/board-it-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$ZGW_RESULTS"
sha256sum "$ZGW_ELF" | cut -d' ' -f1 > "$ZGW_RESULTS/elf.sha256"
arm-none-eabi-size "$ZGW_ELF" > "$ZGW_RESULTS/size.txt"
echo "$rtos" > "$ZGW_RESULTS/rtos.txt"

"$BOARD" server-start > /dev/null
"$BOARD" flash "$ZGW_ELF" > "$ZGW_RESULTS/flash.log" 2>&1
"$BOARD" console 120 "$ZGW_RESULTS/console.log" &
console_pid=$!
trap 'kill "$console_pid" 2>/dev/null || true' EXIT

cd "$OBSW_DIR/gateway/tests"
set +e
pytest -v -p no:cacheprovider --junitxml="$ZGW_RESULTS/junit.xml" test_board.py "$@" 2>&1 | tee "$ZGW_RESULTS/pytest.txt"
status=${PIPESTATUS[0]}
set -e
echo "results: $ZGW_RESULTS (pytest exit $status)"
if [[ $# -eq 0 ]]; then
  python3 "$OBSW_DIR/scripts/record_it_evidence.py" "$ZGW_RESULTS" "$OBSW_DIR/evidence/board-gateway-it" || true
  cp "$ZGW_RESULTS/size.txt" "$ZGW_RESULTS/rtos.txt" "$ZGW_RESULTS/console.log" "$ZGW_RESULTS/board-latency.txt" \
     "$OBSW_DIR/evidence/board-gateway-it/" 2>/dev/null || true
fi
exit "$status"
