# Reproduction contract
contributions/shared/scripts/reproduce_core.py --config LOCAL_JSON --state NEW_DIR --output NEW_DIR
Must refuse replacing existing state/output. Freeze integration/controller/bridge pins, apply
only exported patch; compile native inputs and execute actual core. Capture commands/outputs.
Results distinguish source/build/native tests from independent-person acceptance. No simulated
update or CARLA fallback can be presented as real vehicle/simulation acceptance.

Timeout/SIGINT/SIGTERM must produce explicit failure/interruption and cleanup evidence.
Terminate only the command's own process group. Build-container cleanup must check
the exact immutable container ID and run ownership label before deletion; unavailable
Docker and mismatched ownership cannot be reported as successful cleanup. Preserve
partial command output and do not allow a cleanup error to leave a successful run verdict.
SIGKILL cannot guarantee finalization. No unrelated source/container/network may be restored.
