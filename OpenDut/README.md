# OpenDuT

The integration deploys matched openDuT 0.10.2 CARL, EDGAR and CLEO components in
a local two-peer testbench. The managed Ethernet/GRE path carries the existing
Zenoh–SOME/IP bridge and real S-CORE receiver traffic. The campaign interrupts
and restores that path, then verifies controller behavior and native OpenSOVD
fault history. Fixture and physical CARLA inputs are labelled separately.

The collector-loss test abruptly stops the receiver container while the upstream
publisher continues. Graceful native diagnostic shutdown is checked separately;
stopping the whole middleware stack gracefully can produce another real stream
fault before the receiver exits.

The [AutoSD managed profile](../AutoSD/docs/managed-network.md) attaches a guest
Ethernet NIC to peer B's managed bridge and verifies ThreadX lighting over the
actual GRE path. `prepare --management-subnet <IPv4-/24>` can select a separate
management network for that bench; the existing S-CORE profile keeps its default.

## Development and artifacts

| Path | Purpose |
| --- | --- |
| [config/testbench](config/testbench/) | Release pins, peer Dockerfile and EDGAR entrypoint |
| [scripts/opendut_testbench.py](scripts/opendut_testbench.py) | Owned prepare, up, status and down lifecycle |
| [tests/opendut_receiver_smoke.py](tests/opendut_receiver_smoke.py) | Real receiver, network disturbance, recovery and optional CARLA checks |
| [specs/003-opendut-testbench](specs/003-opendut-testbench/) | Deployment requirements, plan and quickstart |
| [docs](docs/) | Deployment and release research |
| [evidence](evidence/) | Preserved F003 deployment/network artifacts and later bench lifecycle evidence |
| `upstream/opendut/` | Local independent upstream Git checkout; ignored by this repository |
| `.local/opendut*/` | Private CLEO downloads, deployment state, enrollment and TLS material; ignored |

Run from the repository root with a new state/output path for preparation:

```sh
python3 OpenDut/scripts/opendut_testbench.py prepare --state OpenDut/.local/my-bench --output OpenDut/evidence/my-prepare
python3 OpenDut/scripts/opendut_testbench.py up --state OpenDut/.local/my-bench --output OpenDut/evidence/my-up
python3 OpenDut/scripts/opendut_testbench.py status --state OpenDut/.local/my-bench --output OpenDut/evidence/my-status
python3 OpenDut/scripts/opendut_testbench.py down --state OpenDut/.local/my-bench --output OpenDut/evidence/my-down
```

Each output directory must be new. Preparation requires Docker, download access
and the tools listed in the [testbench quickstart](specs/003-opendut-testbench/quickstart.md).
Configure shared campaigns with this bench's state path and the
[OpenSOVD native binary](../OpenSOVD/README.md). The [reproduction guide](../docs/reproduction.md)
describes the source/image pins; the [web UI guide](../docs/dashboard.md) describes
Diagnosis and Test Manager. Shared `scripts/run_campaign.py` drives the relocated
receiver harness and preserves the shared CARLA evidence at the repository root.

Old paths remain compatibility links. Historical evidence retains its original
bytes and recorded paths; new testbench-specific runs belong in this folder.
