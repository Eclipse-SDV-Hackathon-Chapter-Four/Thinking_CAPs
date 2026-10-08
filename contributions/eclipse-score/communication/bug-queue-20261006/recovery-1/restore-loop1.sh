#!/usr/bin/env bash
set -euo pipefail

# Restore the existing registered image attachment. This does not format or repair it.
[[ ${EUID} -eq 0 ]] || { echo 'Run this script with sudo.' >&2; exit 1; }
task_image=/media/jefferson/Lexar/.s-core-build/build-volume-v1.ext4
[[ $(findmnt -rn -T "$task_image" -o UUID) == 002B-CE31 ]] || {
    echo 'The expected Lexar backing volume is not mounted.' >&2; exit 1;
}
if findmnt -rn -S /dev/loop1 >/dev/null; then
    echo 'loop1 is already mounted; inspect it before changing its attachment.' >&2
    exit 1
fi
python3 - "$task_image" <<'PY'
import pathlib, sys, uuid
image = pathlib.Path(sys.argv[1])
if image.stat().st_size != 1099511627776:
    raise SystemExit('Unexpected registered image size')
with image.open('rb') as source:
    source.seek(1080)
    if source.read(2) != b'\x53\xef':
        raise SystemExit('Unexpected ext4 signature')
    source.seek(1128)
    if str(uuid.UUID(bytes=source.read(16))) != '11c42dee-73a3-4c2b-ab42-a0440011d9e0':
        raise SystemExit('Image UUID differs')
PY
task_backing=$(cat /sys/block/loop1/loop/backing_file)
[[ "$task_backing" == /.s-core-build/build-volume-v1.ext4 || "$task_backing" == "$task_image" ]] || {
    echo 'loop1 has an unexpected backing image; stop and inspect.' >&2; exit 1;
}
losetup --detach /dev/loop1
losetup /dev/loop1 "$task_image"
echo 'Existing image reattached as loop1. Mount it as your normal user:'
echo 'udisksctl mount -b /dev/loop1 --no-user-interaction'
