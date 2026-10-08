# Add opt-in write-through DFM storage and preserve catalog read errors

A new OS process can lose fault history after `KvsSovdFaultStateStorage::put`: the current
adapter updates the shared KVS cache without flushing, so its same-process restart tests do not
establish disk persistence. Add an explicit `new_write_through` constructor that flushes successful
put/delete/delete-all operations and propagates flush errors; retain the existing constructor's
flush behavior. Return non-KeyNotFound catalog-map errors instead of synthesizing absent state
or overwriting a malformed map.

Separate OS-process tests cover write/reload/delete/reload/clear/reload. Additional regressions
cover flush failure and corrupt-map preservation. The original constructor fails the new
process-restart regression; opt-in mode passes. Flush failure leaves the in-memory mutation
intact, and this contract does not promise hardware or power-loss durability.

Validation at nightly-2025-07-14:138 DFM tests,66 integration tests and one doctest pass;
one upstream doctest remains ignored. All-targets Clippy with warnings denied and formatting
check pass. A companion real Cruise Control/openDuT campaign verifies native reporter/IPC/DFM,
acknowledged storage, active-fault process restart and held recovery without deleting history.
Full upstream CI/Bazel/pre-commit are not claimed. This is a locally prepared PR description.
