# F004 — reporter and DFM integration research

Researched **4 October 2026**. This records actual APIs and proposed integration decisions, not implemented Cruise Control integration. AAOS FOTA is deferred.

## Pins and reusable artifacts

Fault-library source: `/tmp/sdv-fault-lib-research`, revision `12dac502616701734f90a61edca1326ae2ac6506`. Preserve its `Cargo.lock`, which pins iceoryx2 `eba5da4b8d8cb03bccf1394d88a05e31f58838dc` and persistency `5d9f8225aa5622f52a31003bec937d5ef227dba7`. The temporary clone must become a reproducibly fetched pinned dependency before handover. Never put a `/tmp` path in a committed production dependency.

Built artifacts are `/tmp/sdv-fault-lib-research/target/debug/dfm_bin` and `/tmp/sdv-fault-lib-research/target/debug/examples/tst_app`. The installed stable Rust 1.98.1 successfully compiled these and passed 66 upstream integration tests. The required upstream nightly remains uninstalled. OpenSOVD check artifacts are `/tmp/sdv-opensovd-research-target`. See [upstream-status.md](../../docs/upstream-status.md) for the exact evidence boundary.

An integration crate needs `common`, `fault_lib` and `dfm_lib`, all from the same pinned repository revision. For Git dependencies, Cargo can select each package from its workspace using the same `git` URL and `rev`. Keep an integration lockfile; no direct iceoryx2 dependency is needed solely to use the public reporter/query interfaces.

## Catalog and reporter setup

Use catalog ID `cruise_control` and `FaultId::Text` value `CC.LostCommunication` as **integration-owned identifiers**. They are proposals, not an upstream standardized naming convention.

Build the identical catalog separately for reporter and DFM. Use `common::catalog::{FaultCatalogBuilder, FaultCatalogConfig}` and `cfg_struct(config)?.try_build()?`, or `json_file(path)?.try_build()?`. The DFM registry's catalog ID must equal the string passed to `Reporter::publish`; an arbitrary HTTP entity path will not automatically resolve to that catalog. Catalog hashing validates agreement during reporter startup. See [catalog source](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/common/src/catalog.rs).

Recommended initial descriptor:

- `id`: `FaultId::Text(to_static_short_string("CC.LostCommunication")?)`.
- `name`: `to_static_short_string("LostCommunication")?`.
- `category`: `FaultType::Communication`; `severity`: `FaultSeverity::Error`.
- `summary`: a bounded receiving-side flow description.
- `compliance`: empty; do not assert certification or regulatory qualification.
- `reporter_side_debounce`, `reporter_side_reset`, `manager_side_debounce`, `manager_side_reset`: `None` initially. The receiver already applies its declared timeout/recovery budget; additional debounce must have independent acceptance evidence.

Initialize **one** long-lived `FaultApi::try_new(catalog)?` in the reporter process. It is a process-wide singleton; a second successful initialization returns `AlreadyInitialized`, and dropping the handle does not reset the singleton. Keep it alive for the reporter lifetime. It checks catalog hash before committing its global state, so start the DFM first and retry bounded startup failures. See [FaultApi](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/fault_lib/src/api.rs).

Import `fault_lib::reporter::{Reporter, ReporterApi, ReporterConfig}`; the trait provides the associated constructor and methods. `ReporterConfig` contains `SourceId`, `LifecyclePhase::Running` and `MetadataVec` defaults. Describe the actual receiving application in `SourceId`, with `entity`, optional `ecu`, `domain`, `sw_component`, `instance`. Construct `Reporter::new(&fault_id, config)?`, then `create_record(stage)` and `publish("cruise_control", record)?`. Record transport failures separately. `publish` success is not a synchronous DFM storage acknowledgement, and configured debounce can suppress an event while returning success. See [reporter source](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/fault_lib/src/reporter.rs).

Metadata supports at most eight `(ShortString, ShortString)` pairs, each string at most 64 bytes. Catalog/publish path supports 128 bytes. Put compact source sequence, receiver timestamp, flow identity and timeout values into the event; retain detailed observations in integration evidence. `create_record` captures wall-clock Unix time; freshness detection must continue to use the receiver's declared monotonic clock and explicitly record both clock domains. See [IPC types](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/common/src/types.rs).

## DFM and query setup

Public APIs, with exact source paths relative to the pinned checkout:

| Concern | Actual API | Source |
| --- | --- | --- |
| Registry | `fault_catalog_registry::FaultCatalogRegistry::new(vec![catalog])` | `src/dfm_lib/src/fault_catalog_registry.rs` |
| KVS-backed state | `OpenSOVD/legacy_fault_storage::KvsSovdFaultStateStorage::new(&path, instance_id)` | `src/dfm_lib/src/sovd_fault_storage.rs` |
| DFM same process | `diagnostic_fault_manager::DiagnosticFaultManager::new(storage, registry)` | `src/dfm_lib/src/diagnostic_fault_manager.rs` |
| In-process query handle | `dfm.query_api()` → `DirectDfmQuery` | `src/dfm_lib/src/diagnostic_fault_manager.rs` |
| External IPC query service | `DiagnosticFaultManager::with_query_server(storage, registry)` | `src/dfm_lib/src/diagnostic_fault_manager.rs` |
| External IPC client | `query_ipc::Iceoryx2DfmQuery::with_timeout(Duration)` | `src/dfm_lib/src/query_ipc.rs` |
| Common query trait | `query_api::DfmQueryApi::{get_all_faults,get_fault,delete_fault,delete_all_faults}` | `src/dfm_lib/src/query_api.rs` |

Keep the DFM handle alive. For a separate process, `dfm_bin --catalog-dir <directory> --storage-dir <directory>` loads catalog JSON and starts the IPC query server. It is preferable to the short-lived `dfm` example. Use a bounded readiness retry. Running reporter and DFM across containers requires proven shared IPC resources and compatible permissions; the temporary same-host smoke does not establish that deployment. See [standalone DFM](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_bin/src/main.rs) and [query client](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/query_ipc.rs).

Call `get_fault("cruise_control", "CC.LostCommunication")` to obtain `(SovdFault, SovdEnvData)`. `SovdFault` contains `typed_status`, counters and occurrence timestamps; it does not implement Serde serialization at this pin, so explicitly map the fields into the integration data schema. Prefer typed flags to the string map. Expose query failure/collector freshness separately: listing can substitute default fault state on a storage read error. OpenSOVD's supported `DataProvider` serves this as data-only fault evidence, not a native `/faults` collection. See [fault manager model](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/sovd_fault_manager.rs).

## Timeout, recovery and history semantics

Suggested mapping, subject to actual receiver contracts:

| Receiver observation | Report | Expected active status |
| --- | --- | --- |
| Startup/collector unavailable | `NotTested`, with independent unknown/unavailable state | Never infer healthy from an unreported fault's default clear status. |
| Fresh, valid sample | `Passed` | `test_failed=false`. |
| Declared receiver timeout reached | One `Failed` at transition | `test_failed=true`, `confirmed_dtc=true`, `pending_dtc=false`. |
| Required recovery sample(s) accepted | One `Passed` at transition | `test_failed=false`; with no aging policy, `confirmed_dtc=false`. |

Upstream processing retains `test_failed_since_last_clear`, occurrence counters/timestamps and failure environment data after `Passed`. Recovery must not call delete/clear. Without an aging policy, confirmed status clears on recovery; historical status still exists. Repeated `Failed` records increment the occurrence counter repeatedly, so transition-based publication avoids claiming each poll is a new incident. A `NotTested` report does not erase prior failure flags. No test-completed flag-clearing assumption should be added without verifying the source. See [record processor](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/fault_record_processor.rs).

## Persistence gap and bounded contribution candidate

**Disk persistence needs additional work.** `KvsSovdFaultStateStorage::put` calls `Kvs::set_value` without `flush`; delete operations likewise do not flush. Its KVS field is private, and the storage trait has no flush method. The standalone smoke stored faults in memory but left its selected disk directory empty. The upstream restart test explicitly reuses the same process-global pool, so passing it does not prove a newly started OS process restores history. See [storage implementation](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/sovd_fault_storage.rs) and [restart test](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/tests/integration/src/test_persistent_storage.rs).

The underlying persistency API supplies `KvsApi::flush()`. A bounded local contribution candidate is to make the DFM storage's selected durability policy explicit, flush writes/clears appropriately, propagate flush failures and verify restoration using separate OS processes. This reuses the existing DFM. Account for write latency and batching policy; do not change the control loop to wait for disk persistence. See the pinned [KVS API](https://github.com/eclipse-score/persistency/blob/5d9f8225aa5622f52a31003bec937d5ef227dba7/src/rust/rust_kvs/src/kvs_api.rs) and [implementation](https://github.com/eclipse-score/persistency/blob/5d9f8225aa5622f52a31003bec937d5ef227dba7/src/rust/rust_kvs/src/kvs.rs). No patch or external coordination was performed in this research.

Until that gate passes, claim process-lifetime DFM history only. Durable integration event logs can independently retain evidence, but their presence must not be presented as durable DFM fault-state restoration.
