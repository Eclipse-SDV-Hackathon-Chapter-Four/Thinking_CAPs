#!/usr/bin/env bash
# Run the OpenBSW POSIX build from the external build volume (Ctrl-C stops it).
# Needs vcan0 and tap0 from scripts/net-up.sh.
#
#   OpenBSW/scripts/run.sh [preset]
set -euo pipefail
source "$(dirname "$0")/storage.sh"

preset="${1:-$(lock "['openbsw']['preset']")}"
elf="$OBSW_SRC/build/$preset/executables/referenceApp/application/Release/app.referenceApp.elf"
[[ -x "$elf" ]] || { echo "error: $elf not built; run scripts/bootstrap.sh" >&2; exit 1; }
for itf in vcan0 tap0; do
  ip link show "$itf" >/dev/null 2>&1 || echo "warning: $itf missing; run: sudo $OBSW_DIR/scripts/net-up.sh" >&2
done
cd "$OBSW_WORKSPACE"
exec "$elf"
