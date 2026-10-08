# F005 implementation plan
## Technical context
Integration-owned Python3.10 campaign wrapper reuses the actual F003/F004 smoke and openDuT
Bench ownership API. No legacy Executor or native VIPER claim. JSON scenario definitions,
JUnit XML, JSONL timeline, immutable output directory and local input JSON.
## Constitution check
All twelve principles checked. Preserve bridge/original receiver source; hash versions/dirty
inputs/config/executables, truthful modes, scoped teardown, deterministic acceptance. No external
publication, installer or event-time creation. Control never awaits diagnostic HTTP.
## Design
contributions/shared/scripts/run_campaign.py validates explicit config/prerequisites before spawning the live test.
Missing environmental prerequisite = blocked2; selected assertion/cleanup failure = failed1.
Child result and exit code both required. Cleanup-failure mode expects exactly the injected
failure, verifies restore/capture/app cleanup and reports only that scenario as passed.
Child SIGINT/SIGTERM become an exception inside the owned smoke try/finally; parent forwards
signal and allows bounded graceful cleanup, then records failed interruption. A killed parent
cannot promise cleanup; documented recovery uses bench-owned resources only.
Declare F003 flatc/schema/image inputs through config; record actual digest/hash. Named scenarios
map stable assertion IDs. Evidence includes child requests/events/pcap summaries plus all input
hashes, repository provenance, target identity and result counts. JUnit blocked/skipped have
skipped elements and do not contribute to pass counts.
Real CARLA verification uses a separately owned server/actor and existing X-Verse StatusPublisher,
ZenohCommunicator, VehicleController plus VCU. Operator inputs are harness-generated; simulation
and wall monotonic clocks remain distinct. No new X-Verse features. Missing server/GPU/assets
is a blocked result, not a substituted fixture. Reuse core receiver deployment for the bounded
CARLA nominal return test if feasible. Fixture fault campaign remains explicit and independent.
## Touch points
contributions/shared/scripts/run_campaign.py; contributions/shared/tests/campaigns/{core.json,local.example.json}; contributions/shared/tests/test_campaign.py;
contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py; contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py --carla-config; contributions/shared/scripts/owned_carla.py;
contributions/shared/specs/005-campaign-evidence/{contracts/,quickstart.md,completion.md}; evidence/f005-*.
