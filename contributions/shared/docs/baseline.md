# Current X-Verse baseline — 2026-10-04

Source and configuration identities: [dependency lock](../config/dependencies.lock.json).
Read-only preflight: [manifest](../evidence/f001-local-preflight/manifest.json) and
[results](../evidence/f001-local-preflight/results.json). Runtime is preparation work.

## Reused assets
- Meta repo: `~/autoverse`; user-modified README, launcher, settings and untracked setup preserved.
- Controller: `~/autoverse/vecu/s-core`, remote `The-Xverse/adas_s-core`, branch `dev/sdv-hackathon-2026`.
- Existing bridge: `~/autoverse/bridges/someip/zenoh-someip-bridge`; source untouched.
- CARLA adapter: `~/carla-simulator-bridge`; Python API import works under `/usr/bin/python3`.
- Native OpenSOVD: `~/opensovd-core`; actual App/Component/data-provider API inspected.
- openDuT: `~/opendut`; two-peer runtime not provisioned.

## Existing commands
The current supervisor is `python3 ~/autoverse/run_autoverse.py --vuc-zenoh`.
Check its `--help` first: it deliberately stops stale processes, so it is not a read-only probe.
The option uses Zenoh VCU plus existing SOME/IP bridge and S-CORE, preserving the return path.
Do not select `--only-zenoh-modules` for S-CORE acceptance; that selects the Python controller.
Controller build/start: `source ./prepare.sh`, `./make.sh`, `./ctl.sh up` from the controller repo.
Existing containers: `docker_setup-adas_score-1` and `bridge-e2e`.

The controller's bazel-bin is a symlink into `/var/cache/bazel`, mounted through
`eclipse-s-core-bazel-cache`. Resolve binaries inside the existing Docker image/cache mount.
Read-only inspection found the cruise executable SHA-256
`555c319bc5ae7d9af03531bb9768169b49a1f374d26ec0ab1602619dec1eda48`.
Gateway and daemon artifacts also exist. Build identity is an executable hash; do not infer
an installed software version from a source commit alone.

## Verification and blockers
Preflight found no live CARLA RPC on 127.0.0.1:2000 and both function containers stopped.
Preflight exits 2 (blocked), while its four contract tests pass. These are different claims.
A bounded existing-container startup smoke is retained separately in
`evidence/f001-baseline-smoke/`; startup alone is not vehicle or bidirectional control acceptance.
The published hackathon README's 13/13 assertions have no executable demo/test artifacts
in this checkout and are historical, unverified claims.

Current networking uses host networking, 127.0.0.1 and shared /tmp vSOME/IP sockets.
It does not establish traffic across openDuT; see the deployment research before changing topology.
FOTA is deferred by the user; no AAOS target update is part of this implementation increment.
