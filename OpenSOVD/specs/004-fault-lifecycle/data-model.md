# F004 entities
MonitorPolicy: timeout, startup grace, debounce, recovery hold, poll and query budgets.
MonitorState: unknown/startup/healthy/pending_failure/failed/pending_recovery; last successful
published lifecycle stage, source session, condition-since monotonic ns. Unknown resets pending
holds, preserves last published fault activity; source restart restarts grace, never clears history.
FaultView: monitor assessment and timing, report acceptance/DFM confirmation separate, query
availability/cache age, actual DFM code/status/counters/timestamps/environment, storage mode,
native_faults false. NotTested/default bits alone never mean a healthy current receiver.
Environment: receiver identity, source/build/session, accepted/receipt ages, observation/time;
upstream metadata limits8 pairs64bytes require bounded keys/values and explicit identity hashes.
