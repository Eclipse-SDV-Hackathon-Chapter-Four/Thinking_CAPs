#!/usr/bin/env bash
set -euo pipefail
task_repo_root="$(cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/../../../.." && pwd)"
task_socket_dir="${SDV_DIAGNOSTIC_DIR:-${XDG_RUNTIME_DIR:-/tmp}/sdv-diagnostics-${UID}}"
mkdir -p "$task_socket_dir"
chmod 700 "$task_socket_dir"
exec cargo run --locked --manifest-path "$task_repo_root/contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/Cargo.toml" -- \
  --socket "$task_socket_dir/receiver.sock" \
  --listen "${SDV_DIAGNOSTIC_LISTEN:-127.0.0.1:7691}" \
  --base-uri "${SDV_DIAGNOSTIC_BASE_URI:-http://127.0.0.1:7691/sovd}" \
  --speed-timeout-ms "${SDV_SPEED_TIMEOUT_MS:-1000}" \
  --heartbeat-timeout-ms "${SDV_HEARTBEAT_TIMEOUT_MS:-500}"
