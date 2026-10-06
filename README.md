# Eclipse SDV hackathon — native Cruise Control diagnostics

Prepared 4 October 2026 using Spec Kit0.14.0 and the existing X-Verse/S-CORE environment.
The verified core connects the actual C++ receiver to native OpenSOVD App data resources,
real two-peer openDuT Ethernet and the upstream fault reporter/DFM/KVS lifecycle.

The [final fixture campaign](evidence/f005-core-final/results.json) passed all42 native checks:
startup, nominal state/control return, measured communication timeout, fault attribution/storage,
active-fault process restart, held recovery retaining history, diagnostic stall and collector loss.
That campaign uses fixture vehicle inputs. The [real CARLA campaign](evidence/f009-carla-native-final/results.json)
also passes all46 native/physical checks, including measured native-to-VCU-to-actor throttle
correlation. Its operator pedal/engagement and waypoint steering inputs are harness-generated.
AAOS/FOTA is deferred.
Native `/faults`, E2E and VIPER remain conditional. Second-person signoff is pending.

## Component folders

Development and component-specific artifacts live in four folders:

| Folder | Contents | Status |
| --- | --- | --- |
| [OpenSOVD](OpenSOVD/README.md) | Native diagnostic provider, fault catalog, receiver/storage patches, build scripts, tests, feature specifications, contribution packet and diagnostic evidence | Implemented and exercised |
| [OpenDut](OpenDut/README.md) | Two-peer deployment, release pins, peer image, receiver/network test harness, specifications and testbench evidence | Implemented and exercised |
| [ThreadX](ThreadX/README.md) | Linux-simulated zonal controller for brake/reverse lights over SocketCAN and the existing Zenoh2CAN bridge | Implemented; Linux simulation |
| [AutoSD](AutoSD/README.md) | Pinned QEMU/KVM vehicle-computer deployment, ThreadX/Zenoh2CAN guest services, native OpenSOVD lighting resources and optional managed openDuT Ethernet | Implemented; guest/CARLA/network checks exercised |

The shared dashboard remains in `integration/dashboard/`; CARLA ownership,
campaign orchestration and reproduction remain in `scripts/`, with shared
campaign evidence in `evidence/`. Each component README links to these shared
entry points. [component-layout.json](component-layout.json) maps every relocated
path and records hashes of preserved artifacts. Old paths are compatibility
symlinks, with Markdown redirects for moved research documents, so saved manifests
and existing commands still resolve. New development
belongs in the component folders. Private `.local/` state and local `upstream/`
Git checkouts are ignored; those checkouts retain their own Git history.

Start with [setup and reproduction](docs/reproduction.md), then the [handover](docs/handover.md).
The [claim/evidence map](docs/claim-evidence.md) distinguishes code, tests, actual integration and
pending acceptance. The [current objective audit](docs/completion-audit.md) records the remaining
human-signoff requirement. Native paths and exact assets are configured explicitly:

```sh
cp tests/campaigns/local.example.json .local/campaign.json
# Adjust paths/image IDs to your validated environment; deploy the documented openDuT bench.
/usr/bin/python3 scripts/run_campaign.py --config .local/campaign.json --scenario core --output evidence/my-core-run
```

Output directories must be new. During the bounded campaign, discover the real provider at
`http://172.30.77.12:7691/sovd/v1`; application discovery links lead to `cc.observation` and the
labelled native fault-data fallback `cc.fault-history`. Applications are removed when the test ends.

- [Spec Kit feature backlog](docs/feature-backlog.md) and [constitution](.specify/memory/constitution.md)
- [Native diagnostic implementation](OpenSOVD/integration/diagnostics/) and [test campaigns](tests/campaigns/)
- [Receiver instrumentation patch](OpenSOVD/patches/receiver-diagnostics/) and [native storage patch](OpenSOVD/patches/fault-storage/)
- [Local openDuT profile](OpenDut/config/testbench/README.md)
- [Prepared contribution records](contributions/README.md) and [new storage contribution packet](OpenSOVD/contributions/fault-storage-write-through/README.md)

The original S-CORE implementation is `~/autoverse/vecu/s-core/cc_s-core/score/cruise_control`.
The isolated instrumentation checkout is `~/sdv-score-diagnostics`. The bridge source is preserved.

The [offline recorded replay](evidence/f009-recorded-replay-final/index.html) visualizes
a saved physical campaign; open the file in a browser. It is historical evidence.
The [live dashboard](docs/dashboard.md) provides OpenSOVD diagnosis and Test Manager
through openDuT; its [specification](specs/010-diagnosis-test-dashboard/spec.md)
defines the implemented interface and acceptance criteria.
The [ThreadX zonal lighting controller](ThreadX/README.md) implements brake/reverse
lighting through CAN and Zenoh2CAN using the ThreadX Linux simulation port.
The [AutoSD vehicle computer](AutoSD/README.md) hosts that controller and its gateway
in a real AutoSD VM. Its separate native OpenSOVD lighting App and
[managed openDuT profile](AutoSD/docs/managed-network.md) provide observation,
controller restart, network interruption and recovery checks. The existing web
dashboard remains specific to the S-CORE campaign. See the
[original runtime feasibility research](docs/optional-runtime-integration.md) for historical planning.
License: Apache-2.0; affected upstream notices remain in the exported patches.
