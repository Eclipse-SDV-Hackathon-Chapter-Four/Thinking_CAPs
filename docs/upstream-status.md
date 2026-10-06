# Upstream readiness — F001

Observed **4 October 2026**, Europe/Lisbon. GitHub issue/PR state was refreshed through read-only API requests. Local source was inspected without changing upstream checkouts. This is a preparation audit. **AAOS FOTA and native update orchestration are deferred by the user's later instruction.**

The machine-readable snapshot, selected source hashes, probe commands and results are in [`config/upstream-observations.json`](../config/upstream-observations.json). Open issues identify dependencies; they do not establish that every remote branch lacks a capability.

## Decisions supported by the inspected sources

| Item | Refreshed state | Bounded implementation decision |
| --- | --- | --- |
| [Gateway CRC/E2E #289](https://github.com/eclipse-score/inc_someip_gateway/issues/289) | Open, unassigned; updated 14 September 2026 | Keep E2E conditional. Preserve the working bridge and gateway; do not claim a configuration toggle implements E2E. |
| [Gateway IPC PR #291](https://github.com/eclipse-score/inc_someip_gateway/pull/291) | Open, not draft, unmerged; head `913f77f3e8e91dbe020d68c2219dc5ae31411240` | Preserve the existing IPC. This migration is not a prerequisite. |
| [OpenSOVD faults #156](https://github.com/eclipse-opensovd/opensovd-core/issues/156) | Open, assigned to `akshaim`; updated 14 September 2026 | Use implemented data providers first. A native faults contribution requires a coordinated slice; no coordination was performed. |
| [OpenSOVD updates #195](https://github.com/eclipse-opensovd/opensovd-core/issues/195) / [PR #196](https://github.com/eclipse-opensovd/opensovd-core/pull/196) | Issue open, assigned to `LHThomasWitte`; PR open, draft, unmerged; head `ceaa9edf87cacac591671dfc79d979a0de557714` | Deferred with AAOS FOTA. The draft branch is not adopted. |
| [openDuT S-CORE image #547](https://github.com/eclipse-opendut/opendut/issues/547) | Open, unassigned | Place EDGAR outside the S-CORE image. Image support, service setup and kernel prerequisites remain separate work. |
| [openDuT Executor removal #575](https://github.com/eclipse-opendut/opendut/issues/575) | Open, assigned to `Dr-Eckig` | Use an independently runnable campaign. Do not default to the legacy Executor. |
| [openDuT VIPER containers #578](https://github.com/eclipse-opendut/opendut/issues/578) | Open, unassigned | VIPER remains optional until the exact CARL/EDGAR build and runtime are demonstrated. |
| [openDuT report transfer #576](https://github.com/eclipse-opendut/opendut/issues/576) | Open, unassigned | Record runner results independently. Do not assume EDGAR report content reaches CARL. |
| [openDuT CDA integration #427](https://github.com/eclipse-opendut/opendut/issues/427) | Open, unassigned | CDA is optional and has no evidence of working integration in this audit. |
| [openDuT latest published release](https://github.com/eclipse-opendut/opendut/releases/tag/v0.10.2) | `v0.10.2`, published 12 June 2026; tag ref `eb8d15df6a65719db4b77c4ef660695ce238cf03` | Candidate for matching CARL/EDGAR networking validation, not an installed or verified deployment. |

## Actual local revisions and compiler compatibility

| Source | Inspected revision | Source toolchain | Evidence here |
| --- | --- | --- | --- |
| `/home/jefferson/opensovd-core`, clean `main` | `e25fa30d1bdcb6726e3b4c4ec5d683b783e7c1af` | `nightly-2026-05-07` | Provider and server compile check passes with explicitly selected installed stable compiler. |
| `/home/jefferson/opendut`, clean `main` | `a2447d876905d3293577f360af877229ca989017` | `1.97.1` | Source inspection only; no build or networking deployment. |
| Temporary read-only-source clone `/tmp/sdv-fault-lib-research` | `12dac502616701734f90a61edca1326ae2ac6506` | `nightly-2025-07-14` | 66 upstream integration tests, example/binary builds and two-process IPC smoke pass with stable. |

The host has only `stable-x86_64-unknown-linux-gnu`: `rustc 1.98.1 (48a229cea 2026-09-01)` and `cargo 1.98.1 (797e8a9bc 2026-08-05)`. Each `rustup run <required-toolchain> cargo --version` returned exit 1 because the pinned toolchain is not installed. Explicit `+stable` probes establish alternate-compiler compatibility. They do not satisfy the repositories' pinned compiler, lint, coverage or complete CI gates. No source toolchain pins were changed.

The live `main` commits returned by GitHub matched the inspected OpenSOVD and openDuT local revisions. Gateway live `main` was `f8a196c3b16d5172d898394ab99b0ed81346d63d`; this audit does not substitute it for the existing vehicle's working gateway pin.

## OpenSOVD minimum diagnostic surface

At the inspected core revision, the router merges entity discovery, bulk-data and data routes under `v1`, plus version routes. It has no faults or updates route modules. `EntityCapabilities.faults` is a reserved optional link, not evidence of a working HTTP resource. See the pinned [router](https://github.com/eclipse-opensovd/opensovd-core/blob/e25fa30d1bdcb6726e3b4c4ec5d683b783e7c1af/opensovd-server/src/routes/mod.rs) and [discovery model](https://github.com/eclipse-opensovd/opensovd-core/blob/e25fa30d1bdcb6726e3b4c4ec5d683b783e7c1af/opensovd-models/src/discovery.rs).

The implemented asynchronous `DataProvider` exposes list/read/write with readable/writable metadata. This supports a read-only adapter for receiving-side observations. Mount path is configured separately; do not hardcode `/sovd` as the universal prefix. Fault snapshots exposed through data are **data-only diagnostics**, with integration-owned schema and provenance, rather than native SOVD fault collections. See the [provider trait](https://github.com/eclipse-opensovd/opensovd-core/blob/e25fa30d1bdcb6726e3b4c4ec5d683b783e7c1af/opensovd-core/src/data.rs).

The following command exited 0, without running an HTTP server:

```bash
cd /home/jefferson/opensovd-core
cargo +stable check --locked -p opensovd-providers -p opensovd-server \
  --target-dir /tmp/sdv-opensovd-research-target
```

## Fault-library reuse evaluation

**Decision: reuse the upstream reporter/DFM rather than implement a replacement fault manager.** Reporter, lifecycle processing, storage and query interfaces exist and were exercised locally. Integration with the actual Cruise Control receiver remains a separate feature.

The reporter transports records through iceoryx2. The DFM provides `DfmQueryApi`, including an in-process `DirectDfmQuery` and IPC `Iceoryx2DfmQuery`. `DiagnosticFaultManager::with_query_server` starts the query service. These are Rust/IPC interfaces; they do not add an HTTP faults route to `opensovd-core`. Adapt query output through its real data provider until native routing is independently implemented. See the pinned [query API](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/query_api.rs), [DFM](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/diagnostic_fault_manager.rs) and [reporter](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/fault_lib/src/reporter.rs).

Retain the lockfile: iceoryx2 is pinned to `eba5da4b8d8cb03bccf1394d88a05e31f58838dc`; the `rust_kvs` manifest tracks persistency `main`, while the inspected lockfile resolves `5d9f8225aa5622f52a31003bec937d5ef227dba7`. A refreshed lockfile could change the dependency baseline. See [workspace dependencies](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/Cargo.toml), [DFM dependencies](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/Cargo.toml) and [lockfile](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/Cargo.lock).

Local checks on this pin:

- `cargo +stable test --locked -p integration_tests test_report_and_query -- --test-threads=1`: **4 passed**.
- `cargo +stable test --locked -p integration_tests -- --test-threads=1`: **66 passed, 0 failed**. Includes lifecycle, same-process harness restart and six real iceoryx2 query/clear tests. These IPC tests seed faults through in-process record processing; they do not prove the full receiving-side reporter path or disk persistence across an OS-process restart.
- `cargo +stable build --locked -p dfm_lib --example dfm -p fault_lib --features testutils --example tst_app`: **passed**.
- `cargo +stable build --locked -p dfm_bin`: **passed**.
- Standalone `dfm_bin` with a temporary HVAC catalog/storage directory plus `tst_app`: **DFM ready, reporter exit 0, 21 successful event sends, 10 receiver log entries reporting a stored fault**. DFM remained alive until scoped cleanup terminated that process. This is an upstream HVAC fixture, not Cruise Control.

The sample `dfm` example performs queries and then exits on this source revision. For a long-running process, use `dfm_bin --catalog-dir <directory> --storage-dir <directory>`, which enables the query server and parks the main thread. The smoke process was started/stopped by a scoped subprocess harness. See the pinned [example](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/examples/dfm.rs) and [standalone binary](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_bin/src/main.rs).

Observe error semantics when adapting queries: `get_all_faults` warns and substitutes default state on a storage read error, whereas `get_fault` returns a storage error. Never infer receiving-side freshness or collector availability from the absence of an active DTC alone. Expose collector/fault-query health independently. See [SovdFaultManager](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/sovd_fault_manager.rs).

**Persistence limitation:** the upstream restart test explicitly reuses a process-global KVS pool. Storage `put` updates KVS without calling `flush`, and the standalone smoke left its storage directory empty. Disk/process-restart persistence remains unproved; do not advertise durable DFM history on this evidence. See the pinned [restart test](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/tests/integration/src/test_persistent_storage.rs) and [storage implementation](https://github.com/eclipse-opensovd/fault-lib/blob/12dac502616701734f90a61edca1326ae2ac6506/src/dfm_lib/src/sovd_fault_storage.rs). Further integration guidance is in [fault-integration-research.md](../OpenSOVD/docs/fault-integration-research.md).

## openDuT source limitations

The inspected checkout reports workspace version `0.11.0-alpha`, distinct from release `v0.10.2`. Its CARL crate has a `viper` feature, but the EDGAR manifest has only `integration_testing`, without a VIPER dependency or feature. EDGAR `TestRunReport` task resolution explicitly calls `todo!`. The issue text discusses later capabilities; it is not proof of capabilities in the selected checkout. See pinned [CARL manifest](https://github.com/eclipse-opendut/opendut/blob/a2447d876905d3293577f360af877229ca989017/opendut-carl/Cargo.toml), [EDGAR manifest](https://github.com/eclipse-opendut/opendut/blob/a2447d876905d3293577f360af877229ca989017/opendut-edgar/Cargo.toml) and [task resolver](https://github.com/eclipse-opendut/opendut/blob/a2447d876905d3293577f360af877229ca989017/opendut-edgar/src/service/tasks/runner/task_resolver.rs).

Use openDuT for meaningful endpoint networking, with matching CARL/EDGAR artifacts and separately captured runner evidence. Before claiming integration, deploy endpoints, record their network configuration and demonstrate selected SOME/IP traffic traversing that configuration while diagnostics remain reachable. Kernel/service resources, endpoint credentials and deployment topology have not been validated by this audit.

## Claim boundary and next executable work

This audit proves source availability, compatible component compilation, upstream DFM component tests and an upstream reporter/DFM fixture IPC run. It does **not** prove a combined CARLA/S-CORE/OpenSOVD/openDuT deployment, native faults, gateway E2E, native VIPER execution or second-person reproduction. FOTA remains deferred.

Next, use the F001 baseline audit to bind the actual receiving-side state to the OpenSOVD data provider. Then map real timeout/recovery observations to the pinned upstream reporter/DFM, with a declared history policy and independent collector health. Validate actual openDuT endpoint traffic as a separate gate. Preserve working gateway/bridge pins throughout.
