# F004 completion and convergence record
Prepared 4 October 2026. Selected receiver/fault data slice implemented and verified.
Native `/faults` remains conditional on separate owner work; AAOS/FOTA deferred.

| Intent | Implementation and verification |
| --- | --- |
| FR001–002, SC001: timing and provenance | `src/monitor.rs`, five monitor tests; six cache tests. Actual receiver timestamps measured before loss; median accepted gap 52.8ms, maximum 105.8ms, detector delay 418.1ms against 300ms timeout + 100ms debounce with declared polling allowance. These are engineering fixtures, not validated vehicle safety budgets. |
| FR003, SC002: actual native lifecycle | `src/faults.rs` uses native catalog/FaultApi/Reporter → iceoryx2 → DFM → KVS → get_fault. `contributions/shared/evidence/f004-receiver-signal-fix` passed all 40 checks across real two-peer openDuT Ethernet. Positive controller return, attributed Failed, acknowledged native storage, active-fault OS-process restart, recovered Passed with counter1/history retained, collector loss unknown. |
| FR004, SC003: selected persistence | Exported `contributions/eclipse-opensovd/OpenSOVD/patches/fault-storage/write-through.patch`. Unmodified constructor separate-process regression fails (`f004-unpatched-process-restart.txt`); patched write/read/delete/verify/clear/verify tests pass, with flush-error and malformed-map propagation. Fresh OS-process reload in the actual receiver campaign confirms retained native fault. No hardware/power-loss guarantee. |
| FR005–007: truthful exposure and separation | Native App read-data `cc.fault-history`, explicitly not `/faults`. Reporting, query and storage acknowledgments separate; last query retained with unavailable/stale health. HTTP cached reads; observation/control never awaits HTTP/storage. Source/session/clock guards and failed-query history test pass. |
| FR008, SC004: reproducibility | Optional profile uses explicit audited patch/private source copy/separate fault-build.lock. Default Git Cargo.lock stays pinned; build manifests hash inputs/binary. Final feature tests and Clippy pass (`f004-signal-fix-build`). Upstream pinned-nightly 138 DFM + 66 integration + one doctest pass, one upstream ignored; Clippy/fmt pass. Full upstream CI/Bazel not claimed. |

The first live attempt (`f004-receiver-fault-lifecycle`) failed at graceful shutdown after
passing actual detection/storage assertions. A separate probe confirmed HTTP remained alive
after SIGINT. Lazy native IPC signal initialization displaced the service handler. Initializing
that singleton before installing application SIGINT/SIGTERM streams fixes ownership; the
successful campaign verifies exit0/socket cleanup for both signals. Failed evidence retained.

Convergence: inspected spec, plan, tasks, contracts and implementation against all twelve
constitution principles. No remaining buildable gap in the selected F004 slice. Default behavior
of upstream storage constructor remains unchanged; read errors other than KeyNotFound now
propagate intentionally. No bridge source edits, native-fault routing imitation, FOTA, external
publication, eligibility claim or second-person reproduction claim. Larger CARLA campaign and
operator handover remain F005/F008. All work is prepared outside event time.
