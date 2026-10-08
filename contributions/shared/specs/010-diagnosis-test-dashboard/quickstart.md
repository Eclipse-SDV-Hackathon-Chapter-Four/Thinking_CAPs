# Dashboard validation

Create a private local config from contributions/shared/config/dashboard/local.example.json; point
campaign_config at the current verified reproduction inputs and state_dir at a
new .local/dashboard directory. Use /usr/bin/python3 for native campaigns.

```sh
/usr/bin/python3 contributions/shared/scripts/run_dashboard.py --config .local/dashboard.json --port 8787
```

Open http://127.0.0.1:8787. Diagnosis remains unknown/unavailable with services
stopped. To admit campaigns, deploy the existing owned bench using documented
contributions/eclipse-opendut/OpenDut/scripts/opendut_testbench.py up; browser does not provision or remove the bench.
Inspect peers, select core/CARLA and start once. Reload and a second browser must
show the same ID. Cancel during interruption; verify termination and native cleanup
before another run is allowed. Inspect/download reports and verify original hashes.

Run `python3 -m unittest discover -s tests -p 'test_*.py'`; actual browser driver is
contributions/shared/tests/dashboard_browser_smoke.py. Historical results and replay remain labelled;
unavailable services do not invalidate historical runner verdicts. Graceful dashboard
shutdown cancels owned active execution and awaits restoration; SIGKILL cannot
guarantee cleanup and restart admission stays inhibited until evidence is reconciled.

Feature verification must cover fresh/stale/unknown/restart/outage, two-client starts,
blocked prerequisites, cancellation, failed cleanup, artifact tamper/missing files,
keyboard/responsive use and real control during dashboard loss. Independent-person
reproduction remains pending/deferred, not a gate for current user-authorized work.
