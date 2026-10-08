#!/usr/bin/env bash
# Build the zonal diagnostic gateway and run its integration tests (SWE.5) against
# simulated zonal ECUs on vcan0 and a DoIP tester on tap0.
# Results: <volume>/openbsw-sil/runs/it-<timestamp>/ (JUnit, pytest log, gateway logs, candumps)
#
#   contributions/eclipse-openbsw/OpenBSW/scripts/gateway-it.sh [pytest args...]
#
# ZGW_RTOS selects the RTOS: THREADX (default) or FREERTOS.
set -euo pipefail
source "$(dirname "$0")/storage.sh"
export PATH="$OBSW_VENV/bin:$PATH"

for itf in vcan0 tap0; do
  ip link show "$itf" >/dev/null 2>&1 || { echo "error: $itf missing; run: sudo $OBSW_DIR/scripts/net-up.sh" >&2; exit 1; }
done

build="$OBSW_WORKSPACE/build/gateway"
rtos="${ZGW_RTOS:-THREADX}"
cmake -S "$OBSW_DIR/gateway" -B "$build" -G Ninja -DOPENBSW_DIR="$OBSW_SRC" -DBUILD_TARGET_RTOS="$rtos" \
  -DCMAKE_BUILD_TYPE=Release > /dev/null
cmake --build "$build" --parallel "$(nproc)" > /dev/null

export ZGW_ELF="$build/app/application/openbsw-zonal-gw.elf"
export ZGW_RESULTS="${ZGW_RESULTS:-$OBSW_WORKSPACE/runs/it-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$ZGW_RESULTS"
sha256sum "$ZGW_ELF" | cut -d' ' -f1 > "$ZGW_RESULTS/elf.sha256"
echo "$rtos" > "$ZGW_RESULTS/rtos.txt"

cd "$OBSW_DIR/gateway/tests"
set +e
# the PC test modules; test_board.py runs through scripts/board-it.sh
tests=("$@"); [[ ${#tests[@]} -gt 0 ]] || tests=(test_routing.py test_lifecycle.py)
pytest -v -p no:cacheprovider --junitxml="$ZGW_RESULTS/junit.xml" "${tests[@]}" 2>&1 | tee "$ZGW_RESULTS/pytest.txt"
status=${PIPESTATUS[0]}
set -e
echo "results: $ZGW_RESULTS (pytest exit $status)"
# a full run (no pytest arguments) is recorded as SWE.5 evidence in the repository
if [[ $# -eq 0 ]]; then
  python3 "$OBSW_DIR/scripts/record_it_evidence.py" "$ZGW_RESULTS" "$OBSW_DIR/evidence/gateway-it"
  cp "$ZGW_RESULTS/rtos.txt" "$OBSW_DIR/evidence/gateway-it/"
fi
exit "$status"
