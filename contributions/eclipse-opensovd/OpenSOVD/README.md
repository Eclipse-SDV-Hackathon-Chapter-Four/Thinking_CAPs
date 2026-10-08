# OpenSOVD

The native `sdv-receiver-diagnostics` provider exposes observations from the
instrumented S-CORE Cruise Control receiver through OpenSOVD App data resources.
Its optional fault profile uses the upstream reporter, DFM and patched storage
for fault activation, process restart and recovery history. Discovery starts at
`http://172.30.77.12:7691/sovd/v1` during a managed campaign. The dashboard follows
App discovery to `cc.observation` and the labelled `cc.fault-history` fallback.

## Development and artifacts

| Path | Purpose |
| --- | --- |
| [integration/diagnostics](integration/diagnostics/) | Rust source, tests, Cargo locks and optional native fault profile |
| [config/faults](config/faults/) | Cruise Control fault catalog |
| [patches](patches/) | Receiver instrumentation, fault-storage patch and adapter investigation notes |
| [scripts](scripts/) | Build, local provider startup and receiver container entrypoint |
| [tests](tests/) | Native HTTP fixture, receiver integration and dashboard diagnosis checks |
| [specs](specs/) | Receiver diagnostics and fault-lifecycle feature plans |
| [docs](docs/) | Fault integration research |
| [contributions/fault-storage-write-through](contributions/fault-storage-write-through/) | Preserved upstream contribution packet |
| [evidence](evidence/) | Preserved F002/F004 diagnostic/fault evidence and native dashboard diagnosis |
| [legacy](legacy/) | Earlier SOVD crate design scaffolding |
| `upstream/` | Local independent `opensovd`, `opensovd-core` clones and the `fault-lib-durability` development worktree; ignored by this repository |
| `.local/fault-build/` | Private native build inputs/cache; ignored |

Run commands from the repository root:

```sh
cargo test --locked --manifest-path contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/Cargo.toml
python3 contributions/eclipse-opensovd/OpenSOVD/scripts/build_fault_diagnostics.py --help
python3 contributions/eclipse-opensovd/OpenSOVD/tests/diagnostic_http_smoke.py --help
contributions/eclipse-opensovd/OpenSOVD/scripts/run_diagnostics.sh
```

The last command starts the default local provider on `127.0.0.1:7691`; it needs
receiver observations for live vehicle data. Use the [fault feature quickstart](specs/004-fault-lifecycle/quickstart.md)
for the native fault build. The shared [dashboard](../../shared/docs/dashboard.md),
[campaign/reproduction guide](../../shared/docs/reproduction.md) and
[OpenDuT testbench](../../eclipse-opendut/OpenDut/README.md) describe the connected CARLA environment.
Native `/faults`, E2E and VIPER capabilities remain conditional.

The separate [lighting provider](integration/lighting-diagnostics/) serves the
AutoSD guest's `zonal-lighting` App on `autosd-host`. It exposes actual ThreadX
observations and a labelled integration-owned fault journal. Build/deployment,
HTTP inspection and verification steps are in the [AutoSD README](../../eclipse-autosd/AutoSD/README.md).
This provider does not reuse the Cruise Control observation schema or native DFM.

Historical evidence bytes and provenance remain unchanged. Compatibility links
at the original paths preserve existing scripts and saved manifests. New output
specific to this component should go under `contributions/eclipse-opensovd/OpenSOVD/evidence/<new-run>/`;
shared physical campaigns remain under the root `evidence/`.
