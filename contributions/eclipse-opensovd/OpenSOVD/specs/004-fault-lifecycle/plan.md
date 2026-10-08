# F004 implementation plan
Branch contributions/eclipse-sdv-hackathon; 2026-10-04; [spec](spec.md).
## Technical context
Rust2024, native OpenSOVD at e25fa30d1bdcb6726e3b4c4ec5d683b783e7c1af and
fault-lib at12dac502616701734f90a61edca1326ae2ac6506. iceoryx2 at
 eba5da4b8d8cb03bccf1394d88a05e31f58838dc and rust_kvs5d9f8225aa5622f52a31003bec937d5ef227dba7.
Optional Cargo fault-lifecycle feature, native catalog/report/DFM query and cached native App
 data resource cc.fault-history. Linux monotonic detector, upstream wall timestamps in storage.
## Constitution check
All twelve principles checked before/after design. No bridge/control-policy changes. Native
report/IPC/storage reuse; explicit data-only fallback. Unknown never healthy. Isolated upstream
patch, prepared evidence and no external outreach. Reporting/query run outside controller path.
## Design and research
Native KVS adapter does not flush at selected pin. Introduce opt-in new_write_through constructor
in an isolated fault-lib worktree: default new retains existing behavior; explicit mode flushes
successful mutations and propagates backend errors. Verify separate OS-process write/reload/delete
and write failure. Feature-enabled builds require that exported patch through explicit Cargo
config override; unpatched default receiver diagnostics remain buildable. No silent durability claim.
Watchdog startup grace starts with first actual receiver heartbeat. Only available receiver data
may drive accepted-data timeout; collector loss becomes unknown. Report lifecycle transitions,
not every poll; recovery requires held freshness. Native DFM status/history is separately cached.
Initial policy: timeout300ms, startup2000ms, debounce100ms, recovery150ms, monitor25ms,
query50ms. Declare and measure baseline before timing acceptance; no safety certification.
## Structure
contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/src/{monitor.rs,faults.rs}; contributions/eclipse-opensovd/OpenSOVD/config/faults/cruise-control.json;
contributions/eclipse-opensovd/OpenSOVD/patches/fault-storage/{write-through.patch,README.md}; contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py --fault-lifecycle;
contributions/eclipse-opensovd/OpenSOVD/scripts/build_fault_diagnostics.py; contributions/eclipse-opensovd/OpenSOVD/specs/004-fault-lifecycle/; evidence/f004-*.
