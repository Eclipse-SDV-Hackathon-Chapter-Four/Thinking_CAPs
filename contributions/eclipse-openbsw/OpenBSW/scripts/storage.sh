#!/usr/bin/env bash
# Sourced by the other scripts. Resolves the OpenBSW SIL workspace on the
# external build volume and refuses to fall back to the internal disk.
#
# Override with OBSW_WORKSPACE=/path; the path must not be on the same
# filesystem as /.

OBSW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OBSW_LOCK="$OBSW_DIR/dependencies.lock.json"

lock() { python3 -c "import json,sys; d=json.load(open('$OBSW_LOCK')); print(d$1)"; }

OBSW_VOLUME_UUID="$(lock "['storage']['filesystem_uuid']")"
OBSW_SUBDIR="$(lock "['storage']['workspace_subdir']")"

if [[ -z "${OBSW_WORKSPACE:-}" ]]; then
  mount_point="$(findmnt -rn -S "UUID=$OBSW_VOLUME_UUID" -o TARGET | head -n1)"
  if [[ -z "$mount_point" ]]; then
    echo "error: build volume UUID=$OBSW_VOLUME_UUID is not mounted." >&2
    echo "       See contributions/eclipse-openbsw/OpenBSW/README.md#virtual-environment-sil to attach and mount it." >&2
    return 1 2>/dev/null || exit 1
  fi
  OBSW_WORKSPACE="$mount_point/$OBSW_SUBDIR"
fi

mkdir -p "$OBSW_WORKSPACE"
if [[ "$(stat -c %d "$OBSW_WORKSPACE")" == "$(stat -c %d /)" ]]; then
  echo "error: $OBSW_WORKSPACE is on the internal root filesystem; refusing." >&2
  return 1 2>/dev/null || exit 1
fi

export OBSW_DIR OBSW_LOCK OBSW_WORKSPACE
export OBSW_SRC="$OBSW_WORKSPACE/openbsw"
export OBSW_VENV="$OBSW_WORKSPACE/venv"
# Keep a sourced ROS 2 environment from leaking packages into the venv.
unset PYTHONPATH
# Keep caches and compiler temporaries off the internal disk too.
export PIP_CACHE_DIR="$OBSW_WORKSPACE/cache/pip"
export TMPDIR="$OBSW_WORKSPACE/tmp"
mkdir -p "$PIP_CACHE_DIR" "$TMPDIR"
