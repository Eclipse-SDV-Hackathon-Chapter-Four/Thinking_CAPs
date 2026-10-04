#!/usr/bin/env bash
# Run home-relative recipes in an SSD namespace without changing HOME.
set -euo pipefail
workspace="$(cd -- "$1" && pwd)"
shift
mkdir -p "$workspace/tmp/.X11-unix" "$workspace/runtime"
chmod 700 "$workspace/runtime"
bindings=(--ro-bind / / --bind "$workspace" "$workspace" --bind "$workspace" "$HOME"
          --bind "$workspace/tmp" /tmp --bind "$workspace/runtime" /run/user/1000)
if [[ -d /tmp/.X11-unix ]]; then
    bindings+=(--ro-bind /tmp/.X11-unix /tmp/.X11-unix)
fi
if [[ -n "${XAUTHORITY:-}" && -f "$XAUTHORITY" ]]; then
    bindings+=(--ro-bind "$XAUTHORITY" "$XAUTHORITY")
fi
exec bwrap "${bindings[@]}" --proc /proc --dev-bind /dev /dev --chdir "$HOME/autoverse" "$@"
