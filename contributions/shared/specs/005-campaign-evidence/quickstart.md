# F005 quickstart
Use /usr/bin/python3 with installed Zenoh/CARLA; copy contributions/shared/tests/campaigns/local.example.json to
ignored .local/campaign.json and adjust all paths. Build native F004 profile, deploy F003 bench.
Run contributions/shared/scripts/run_campaign.py --config .local/campaign.json --scenario core --output evidence/f005-my-run.
Run cleanup-failure to verify failure cleanup. Use a NEW output path each time. CARLA requires
its assets and owned server; never assume fixture success establishes simulation success.
