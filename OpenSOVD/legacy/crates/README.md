# SOVD Crates

## cruise-gateway
Runnable Axum prototype for the app-scoped faults collection. I1/I2 Unix-socket handover and upstream OpenSOVD wiring remain to be implemented.

## cruise_diag
Fault provider prototype. It stores producer-confirmed status events, preserves source timestamps and freeze frames, filters by status byte, and rejects requests when source liveness is stale. Detection and debounce belong in `cc-app`.

## cruise_sim
Planned in-process ECU simulator for testing without S-CORE.
