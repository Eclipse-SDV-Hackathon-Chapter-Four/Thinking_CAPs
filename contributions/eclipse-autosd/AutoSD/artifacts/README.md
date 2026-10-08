# AutoSD validation artifacts

The [vehicle-computer packet](vehicle-computer/results.json) records a real
AutoSD 10 QEMU/KVM guest deployment and implementation-agent self-reproduction
on 4 October 2026. The final run used a new guest overlay, a separate pinned
bridge clone and a new native Cargo target. The verified base-image cache and
Docker build layers were shared. This is not a new-computer or human-signoff claim.

| Evidence | What passed |
| --- | --- |
| [Preparation](vehicle-computer/prepare.json), [deployment](vehicle-computer/deploy.json), [build](vehicle-computer/build.json) | Dated image/compressed and expanded hashes, guest identity/kernel, bundle and executable identities |
| [Guest CAN contract](vehicle-computer/can-contract.json) | All 256 status values, malformed input rejection, held state and timer wall-clock behavior: 4 checks |
| [Optional input timeout](vehicle-computer/can-timeout.json) | Actual 200 ms timeout, journal activation and recovery/history: 3 checks |
| [Local CARLA/diagnostic test](vehicle-computer/carla/results.json) | 13 checks, including four actual light masks, individual VCU topic, native discovery, expiry, stop/restart and gateway recovery |
| [Managed CARLA/diagnostic test](vehicle-computer/managed-carla/results.json) | 16 checks, adding real GRE interruption, reachable management diagnostics and recovery |
| [Actual actor masks](vehicle-computer/managed-carla/carla-lights.json), [command/feedback observations](vehicle-computer/managed-carla/packets.json), [native HTTP responses](vehicle-computer/managed-carla/requests.json) | Actual CARLA actor, unchanged vehicle classes, real guest gateway/ThreadX/OpenSOVD; VCU inputs are labelled fixtures |
| [Guest interface setup](vehicle-computer/managed-configure.json), [GRE traffic](vehicle-computer/gre-path.json) | Second guest NIC routing/ping and captured actual encapsulated traffic |
| [Reboot](vehicle-computer/reboot.json) | Changed guest boot ID, active CAN/image/controller/gateway/diagnostic services, same executable identities and retained fault history without redeployment |
| [Guest shutdown](vehicle-computer/down.json), [relay removal](vehicle-computer/managed-removed.json), [bench removal](vehicle-computer/opendut-down/results.json), [cleanup](vehicle-computer/cleanup.json) | Owned actors, VM, test CARLA server, routers and enrolled bench resources removed/stopped; unrelated network retained |

[Provenance](vehicle-computer/provenance.json) identifies exact source hashes,
fixture boundaries, image/build reuse and tool identity.
[Manifest](vehicle-computer/manifest.json) hashes the retained public packet.
Private guest keys, enrollment strings, TLS keys, images, disks and workload
archives are not exported. Disposable/debug runs remain ignored under `runs/`.

Verify integrity from the repository root without starting anything:

```bash
python3 AutoSD/scripts/verify_artifacts.py
# Also check whether the currently checked-out application sources match the tested packet:
python3 AutoSD/scripts/verify_artifacts.py --sources
```

Hash verification does not rerun the native tests or grant engineering acceptance.
Fault history is an integration-owned observation journal exposed by native
OpenSOVD data resources; the existing native DFM pipeline and shared dashboard
remain separate. ThreadX/Linux, virtual CAN and fixture commands are explicit;
no physical CAN hardware, embedded timing or production qualification is claimed.
