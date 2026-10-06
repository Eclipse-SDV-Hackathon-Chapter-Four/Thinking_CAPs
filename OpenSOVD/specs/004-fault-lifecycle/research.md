# F004 decisions
Use actual upstream Reporter/FaultApi/DiagnosticFaultManager/DirectDfmQuery and KVS.
Research agent established stable build, 66 integration tests and native IPC report/query.
Native HTTP faults absent at selected OpenSOVD pin: expose a labelled native data resource
without competing with #156 owner. See OpenSOVD/docs/fault-integration-research.md/upstream-status.md.
Default KVS keeps values in a process-global pool without flush. Separate-process regression
is necessary; select opt-in write-through constructor and error propagation over an invented
JSON fault service or a global performance policy change. Store failure/recovery transitions,
retain history and attribution, and report unavailable rather than clearing on query error.
No root cause certainty, sequence/E2E integrity or automatic controller reaction is claimed.
