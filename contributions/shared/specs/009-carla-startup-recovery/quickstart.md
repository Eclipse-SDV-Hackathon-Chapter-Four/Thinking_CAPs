# F009 quickstart
Deploy a fresh F003 owned bench; set its absolute state path in a private campaign config.
Use `/usr/bin/python3` with actual CARLA0.9.15/Zenoh1.3.4 and the existing server/NVIDIA ICD.
Run `contributions/shared/scripts/run_campaign.py --config LOCAL_JSON --scenario carla --output NEW_DIR`.
Inspect all native results plus physical samples and actual applied return control before
claiming success. Teardown only the owned bench/server/actor. Existing F008 reproduction
freeze6d7bef9 predates the readiness fix and only proves the native fixture core.
