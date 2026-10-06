# F004 — Receiver timeout, upstream fault lifecycle and exposure
Prepared 2026-10-04. Native OpenSOVD /faults conditional; AAOS/FOTA deferred.

## User scenarios and testing
US1 P1: Observe startup/accepted-data loss/recovery using the receiver monotonic clock.
Independent test: explicit policy boundaries, actual interruption and return of accepted speed.
US2 P1: Retain attributed upstream fault evidence through recovery and real process restart.
Independent test: native reporter -> iceoryx2 -> DFM -> KVS -> diagnostic query, plus separate
OS-process write/reload/delete tests. Healthy recovery changes active flags, not history deletion.
US3 P2: Distinguish faults from diagnostic/collector unavailability.
Independent test: loss of source or query remains unknown/unavailable; never manufactures
transport silence, nominal integrity, automatic controller disengagement or re-engagement.

## Requirements
FR-001/REQ-006: Document startup grace, timeout, failure debounce, recovery hold, polling,
clock and measured baseline cadence/jitter; deterministic boundary tests and live assertions.
FR-002/REQ-007: Detect accepted-data timeout only with available actual receiver provenance;
recovery requires held fresh accepted data and preserves independently observed controller state.
FR-003/REQ-008: Reuse pinned fault-lib catalog/reporter, native IPC and DFM storage/query APIs;
retain fault identity, receiver/build/session attribution, status/counters/supported environment.
FR-004: Declare persistence semantics and verify OS-process reload and durable clear.
FR-005/REQ-009: Expose supported native data resource fallback, explicitly not native /faults;
no speculative route or duplicate implementation of the upstream native-fault owner work.
FR-006/REQ-004: Reporting/storage/query run outside control path; HTTP serves cached evidence.
FR-007/REQ-003: Startup/no source/query failures remain distinguishable from healthy/cleared.
FR-008/REQ-010: Preserve immutable traceable prepared/fixture/live evidence and configuration.

## Success criteria
SC001: Policy boundaries and unknown behavior pass meaningful tests.
SC002: Real receiver disturbance -> Failed report -> stored/query-visible fault -> held Passed
recovery with retained occurrence/environment history passes through deployed openDuT.
SC003: Separate OS-process restart/clear regression demonstrates selected persistence contract.
SC004: Data-only/native-fault limitations and upstream changes are reviewable/reproducible.

## Edge cases
No initial sample, repeated valid value without sequence support, receipt without acceptance,
receiver restart, collector silence, query/storage/report failure, IPC startup/catalog mismatch,
recovery oscillation, slow KVS, disk failure. No physical root cause is inferred from a timeout.
