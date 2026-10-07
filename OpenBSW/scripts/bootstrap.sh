#!/usr/bin/env bash
# Prepare the OpenBSW SIL workspace on the external build volume and build
# the POSIX reference application. Runs as the normal user; no sudo.
#
#   OpenBSW/scripts/bootstrap.sh [preset]     # default: preset from the lock file
set -euo pipefail
source "$(dirname "$0")/storage.sh"

repo="$(lock "['openbsw']['repository']")"
rev="$(lock "['openbsw']['revision']")"
preset="${1:-$(lock "['openbsw']['preset']")}"

echo "workspace: $OBSW_WORKSPACE"

# 1. Build tools in a venv on the volume.
if [[ ! -x "$OBSW_VENV/bin/cmake" ]]; then
  python3 -m venv "$OBSW_VENV"
fi
"$OBSW_VENV/bin/pip" install -q -r "$OBSW_DIR/requirements-build.txt"
export PATH="$OBSW_VENV/bin:$PATH"

# 2. OpenBSW at the pinned revision, unmodified.
if [[ ! -d "$OBSW_SRC/.git" ]]; then
  git init -q "$OBSW_SRC"
  git -C "$OBSW_SRC" remote add origin "$repo"
fi
if [[ "$(git -C "$OBSW_SRC" rev-parse -q --verify HEAD 2>/dev/null)" != "$rev" ]]; then
  git -C "$OBSW_SRC" fetch -q --depth 1 origin "$rev"
  git -C "$OBSW_SRC" checkout -q --detach FETCH_HEAD
fi
if [[ "$(git -C "$OBSW_SRC" rev-parse HEAD)" != "$rev" ]]; then
  echo "error: OpenBSW checkout is not at $rev" >&2; exit 1
fi
if [[ -n "$(git -C "$OBSW_SRC" status --porcelain --untracked-files=no)" ]]; then
  echo "error: OpenBSW checkout has tracked modifications" >&2; exit 1
fi

# SIL test clients exactly as OpenBSW pins them (pytest suite and udsTool).
"$OBSW_VENV/bin/pip" install -q -r "$OBSW_SRC/test/pyTest/requirements.txt" \
  -r "$OBSW_SRC/tools/UdsTool/requirements.txt"

# 3. Configure and build (build tree stays inside the checkout on the volume).
cd "$OBSW_SRC"
cmake --preset "$preset"
cmake --build --preset "$preset" --parallel "$(nproc)"

elf="$OBSW_SRC/build/$preset/executables/referenceApp/application/Release/app.referenceApp.elf"
test -x "$elf"
echo "built: $elf"
