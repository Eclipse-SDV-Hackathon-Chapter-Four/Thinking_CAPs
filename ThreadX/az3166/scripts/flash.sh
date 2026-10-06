#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Flashes the AZ3166 through the ST-LINK USB mass-storage (drag-and-drop)
# programmer. Usage: flash.sh [firmware.bin] [mount point]
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
image="${1:-$here/../build-az3166/threadx-zonal-lights-az3166.bin}"
mount="${2:-$(findmnt -rn -S LABEL=AZ3166 -o TARGET 2>/dev/null | head -1 || true)}"
[[ -f "$image" ]] || { echo "Firmware image not found: $image" >&2; exit 1; }
[[ -n "$mount" && -f "$mount/DETAILS.TXT" ]] || {
    echo "AZ3166 ST-LINK drive not mounted (expected a volume labelled AZ3166)" >&2; exit 1; }
# The ST-LINK rewrites its FAT image after each programming cycle; a kernel
# mount that survived the re-enumeration holds stale FAT state and turns
# read-only on the next copy. Remount for a fresh view (no root needed).
device="$(findmnt -rn -T "$mount" -o SOURCE)"
if command -v udisksctl >/dev/null; then
    udisksctl unmount -b "$device" >/dev/null
    mount="$(udisksctl mount -b "$device" | sed -n 's/^Mounted .* at //p')"
fi
size=$(stat -c %s "$image")
echo "Flashing $image ($size bytes, sha256 $(sha256sum "$image" | cut -c1-16)) via $mount"
cp "$image" "$mount/"
sync
# The ST-LINK programs the MCU, then re-enumerates the drive; it reports a
# failure by exposing FAIL.TXT after the remount.
sleep 2
for _ in $(seq 1 30); do
    remount="$(findmnt -rn -S LABEL=AZ3166 -o TARGET 2>/dev/null | head -1 || true)"
    if [[ -n "$remount" && -f "$remount/DETAILS.TXT" ]]; then
        if [[ -f "$remount/FAIL.TXT" ]]; then
            echo "ST-LINK reported a programming failure:" >&2
            cat "$remount/FAIL.TXT" >&2
            exit 1
        fi
        echo "Flashed; the board has restarted the new firmware."
        exit 0
    fi
    sleep 1
done
echo "AZ3166 drive did not reappear within 30 s; check the USB connection." >&2
exit 1
