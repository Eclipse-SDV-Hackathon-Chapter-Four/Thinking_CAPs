#!/usr/bin/env bash
# Isolated diagnostic integration smoke: original gateway/daemon + patched receiver.
set -euo pipefail
export SCORE_GATEWAY_CONFIG="${SCORE_GATEWAY_CONFIG:-/home/baseline/bazel-bin/tests/integration/cruise_control_someip_config.bin}"
export SCORE_GATEWAY_MANIFEST=/home/source/score/cruise_control/config/mw_com_config.json
export SCORE_SOMEIP_MANIFEST="$SCORE_GATEWAY_MANIFEST"
export SCORE_GATEWAYD_BIN=/home/baseline/bazel-bin/tests/integration/gatewayd/gatewayd.exe
export SCORE_SOMEIPD_BIN=/home/baseline/bazel-bin/tests/integration/someipd/someipd.exe
export VSOMEIP_CONFIGURATION="${VSOMEIP_CONFIGURATION:-/home/source/deployment/xverse/docker_setup/vsomeip.json}"
export MW_LOG_CONFIG_FILE=/home/source/score/cruise_control/config/logging.json
task_pids=()
cleanup() {
  for task_pid in "${task_pids[@]}"; do kill -TERM "$task_pid" 2>/dev/null || true; done
  wait || true
}
trap cleanup EXIT
trap 'exit 0' INT TERM
/home/baseline/tests/integration/run_gateway.sh gatewayd > /tmp/gatewayd.txt 2>&1 &
task_pids+=("$!")
sleep 3
/home/baseline/tests/integration/run_gateway.sh someipd > /tmp/someipd.txt 2>&1 &
task_pids+=("$!")
sleep 3
/home/source/bazel-bin/score/cruise_control/cruise_control_main \
  --service_instance_manifest "$SCORE_GATEWAY_MANIFEST" > /tmp/receiver.txt 2>&1 &
task_pids+=("$!")
wait -n "${task_pids[@]}"
