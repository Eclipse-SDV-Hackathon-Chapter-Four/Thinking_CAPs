# Native integration scripts
- `audit_baseline.py`: read-only source/runtime audit; blocked2 is distinct from failure1.
- [contributions/eclipse-opendut/OpenDut/scripts/opendut_testbench.py](../../eclipse-opendut/OpenDut/scripts/opendut_testbench.py): owned prepare/up/status/down for the matched local release.
- [contributions/eclipse-opensovd/OpenSOVD/scripts/build_fault_diagnostics.py](../../eclipse-opensovd/OpenSOVD/scripts/build_fault_diagnostics.py): audited native storage patch/private feature build and checks.
- `reproduce_core.py`: clean frozen-source build, tests and actual native core campaign.
- `run_campaign.py`: named campaign, explicit manifest/results/JUnit/timeline/summary.
- [contributions/eclipse-opensovd/OpenSOVD/scripts/receiver_container_entrypoint.sh](../../eclipse-opensovd/OpenSOVD/scripts/receiver_container_entrypoint.sh): original gateway/daemon plus instrumented receiver in private IPC.
- `owned_carla.py`: optional owned server/actor harness reusing existing X-Verse/VCU classes.
- `render_campaign_replay.py`: source-hash-verified, standalone historical playback of a passed physical campaign; no live service access.
- `verify_contributions.py`: retained artifact hashes only; not upstream engineering acceptance.

Commands and exact prerequisites are in [reproduction.md](../docs/reproduction.md).
Use new evidence output directories. Build assets and credentials stay outside Git.
The old component script names in this directory are compatibility symlinks.

- `run_dashboard.py`: local OpenSOVD diagnosis and openDuT-managed project campaign UI; [setup](../docs/dashboard.md).
- `sync-xverse.sh`: sync `demo/X-Verse` with The-Xverse/autoverse `dev/sdv-hackathon-2026` in one commit; `--check` reports in sync, behind, or edited directly. `demo/X-Verse` is never edited here.
