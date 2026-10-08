# Reproduce the selected native core
Prepared 4 October 2026. The reference host is Linux x86_64 with Docker, Python3.10.12,
Zenoh1.3.4 and rustc1.98.1 (48a229cea2026-09-01). Upstream fault-lib gates use its pinned
nightly-2025-07-14. A source-clean self-run shares the host/images/LLVM cache; this is not a
second contributor's acceptance. See the actual reproduction record linked in handover.md.

## Existing reference assets
Freeze the [dependency audit](../config/dependencies.lock.json),
[testbench release pins](../../eclipse-opendut/OpenDut/config/testbench/versions.json), Cargo locks and exported patches.
Local native Score/bridge/build images are identified by immutable IDs in
[local.example.json](../tests/campaigns/local.example.json). These local IDs are not pullable
registry names. Use the existing images on this machine, or acquire/build the corresponding
assets on a suitable new machine and record/test its actual IDs before claiming compatibility.

The controller pin is93f8ea1e6f76714496c092902e00c9b91c58cdc8 in The-Xverse/adas_s-core;
bridge repository pin0d53a2af8b37121e54d742c6cefd0297dd9e4b92, with implementation inside
its `zenoh-someip-bridge/` subdirectory. The native build base Dockerfile uses the upstream
S-CORE devcontainer v1.11.0. The runtime Dockerfile is in
`cc_s-core/deployment/xverse/docker_setup/`; use the bridge repository's documented image build.
The local self-run verifies these existing immutable images, not a cold image rebuild.

Python dependencies are [requirements-core.txt](../requirements-core.txt). Optional real CARLA
requires [requirements-carla.txt](../requirements-carla.txt) and the existing server assets.
No GPU/driver or system-package change is performed by the campaign. Keep large images,
compiler archives and CARLA assets outside Git. Native Bazel acquisition needs substantial
free space, including its LLVM toolchain; the reference run reuses the explicit8.2GB LLVM
repository while compiling into a fresh output base.

## Prepare and deploy openDuT
Run from the integration repository, with Docker access and NET_ADMIN available inside its
owned peer containers. The local profile reserves172.30.77.0/24 management and
192.168.123.0/24 DUT networking; preparation rejects overlapping existing networks.
Use fresh private state and new evidence output directories:

```sh
python3 contributions/eclipse-opendut/OpenDut/scripts/opendut_testbench.py prepare --state .local/opendut-next --output evidence/my-bench-prepare
python3 contributions/eclipse-opendut/OpenDut/scripts/opendut_testbench.py up --state .local/opendut-next --output evidence/my-bench-up
cp contributions/shared/tests/campaigns/local.example.json .local/campaign.json
```

Update `state` in the private JSON to `.local/opendut-next`'s absolute path and all source/image/tool
inputs for your environment. Certificates expire after seven days; use new state for later runs.
Secrets/enrollment/captures stay under private ignored state. VPN/OIDC are disabled; networking
is actual local CARL-managed GRE, with no distributed-site/VPN claim.

## Build and run
To preserve original checkouts and rebuild the selected frozen sources:

```sh
/usr/bin/python3 contributions/shared/scripts/reproduce_core.py --config .local/campaign.json --state .local/my-clean-sources --output evidence/my-reproduction
```

The helper freezes the current committed integration HEAD (or explicit `--integration-revision`),
then clones that revision, Score and bridge pins into new state without hardlinks,
verifies clean source, applies exactly the exported receiver patch and compiles the controller,
unmodified gateway/daemon/config/flatc targets. It runs the existing controller unit target,
builds/tests/Clippy-checks the native fault profile using the explicit storage patch/separate lock,
and executes the real core campaign. It records commands, source subdirectories, binary hashes
and shared assets. Default Rust builds and fault profile builds must use separate target folders.
`expected_rustc` rejects compiler drift. For a cold native Bazel acquisition, omit
`llvm_repository`; that acquisition path is prepared but has not been verified on another machine.

For already validated binaries/builds:

```sh
/usr/bin/python3 contributions/shared/scripts/run_campaign.py --config .local/campaign.json --scenario core --output evidence/my-core
/usr/bin/python3 contributions/shared/scripts/run_campaign.py --config .local/campaign.json --scenario cleanup-failure --output evidence/my-cleanup-check
/usr/bin/python3 contributions/shared/scripts/run_campaign.py --config .local/campaign.json --scenario carla --output evidence/my-carla-gate
```

Core uses fixture vehicle inputs with real native receiver/network/fault processing. CARLA
selection never substitutes fixtures; F009 verified the actual world/actor/control path after
fixing startup retries. It generates pedal/engagement and waypoint steering requests through
the existing input topics. Native
OpenSOVD `/faults`, AAOS/FOTA, E2E and VIPER are not selected acceptance checks.
Exit0 selected checks passed; exit1 failure/cleanup error; exit2 missing prerequisite. Conditional
and unselected checks are skipped. Inspect results/JUnit/summary, native requests and timeline;
startup-only results and skipped checks are not vehicle E2E passes.

## Teardown and interruption recovery
The child restores only its observed GRE link/capture/application resources on failure and
SIGINT/SIGTERM. SIGKILL cannot guarantee finalization. Inspect resources bearing the exact
run label from private `deployment.json`, and verify any leftover `sdv-net-*` application belongs
to that run before removal. Do not remove original baseline containers or global processes.

```sh
python3 contributions/eclipse-opendut/OpenDut/scripts/opendut_testbench.py down --state .local/opendut-next --output evidence/my-bench-down
```

Teardown verifies ownership labels before removing peers/CARL/network/data volume. Preserve
private state/evidence for inspection, or archive/delete only your own files after reviewing them.
The original `docker_setup-adas_score-1`, `bridge-e2e` and Cuttlefish containers are outside this
profile. Native builds remain in explicit owned cache locations for subsequent runs.

The reproduction helper also finalizes its build subprocesses. Each command has a
separate owned process group; timeout or graceful interruption terminates that group
and preserves captured output. The build and ownership-repair containers have exact
run labels, and cleanup verifies their immutable IDs/labels before removal. A missing
container is reconciled; an unavailable Docker daemon or ownership mismatch is a
cleanup failure, never successful absence. SIGINT/SIGTERM write failed/interrupted
manifests (normally exit130/143); cleanup failure takes precedence with exit1. Further
graceful signals are ignored during bounded finalization. SIGKILL cannot guarantee cleanup.
The [actual native-build cancellation](../evidence/f008-real-build-interrupted/verification.json)
and [timeout/ownership probes](../evidence/f008-build-cleanup-after/verification.json)
verify these boundaries without claiming a completed build from a cancelled attempt.

## Actual second-contributor signoff
[reproduction-signoff.json](reproduction-signoff.json) is pending. A real contributor records
name, time/environment, integration revision, config hash, campaign artifact path/verdict and
interpretation of fixture/native/blocked boundaries. The implementation agent's self-run cannot
fill this requirement. No event-time contribution or eligibility is inferred from preparation.

The initial F008 clean-source self-run froze6d7bef9 and rebuilt native components successfully.
Later audit found its overlay setup shadowed the configured compiler/schema variables, so
configuration generation still used baseline cached tools. Preserve that historical record;
F009 fixes the input selection and verifies actual execution of the fresh compiler/schema
in both physical and fixture campaigns. A complete new-machine/cold-build reproduction is
still unverified. The reproduction helper defaults to the latest committed fix for future runs.

The current helper records observed host/platform/Python identity. Supply `--operator`
with your actual attribution and declare `--shared-host` if using this original host,
or `--no-shared-host` when using a different host. Omitted operator and host-sharing
remain unknown; running the helper never attests independent human reproduction.
For example, the implementation agent's reference-host self-run would add
`--operator 'implementation agent self-run' --shared-host`. A real contributor supplies
their own attribution and separately completes the signoff record after inspecting
the actual campaign result. Historical self-run manifests retain their measured identity.

The user subsequently instructed: skip contribution reproduction for now and
continue implementation. The second-contributor signoff is therefore deferred,
remains unattested, and does not gate current F010 development. This does not
convert agent self-runs into human reproduction. See [dashboard.md](dashboard.md).
