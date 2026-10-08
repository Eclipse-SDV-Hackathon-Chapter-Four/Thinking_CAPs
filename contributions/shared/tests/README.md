# Meaningful native verification
Run Python contract regressions with an interpreter that has the selected dependencies:

```sh
/usr/bin/python3 -m unittest discover -s tests -p 'test_*.py'
```

Native Rust cache/monitor/query-history tests and Clippy run through
`OpenSOVD/scripts/build_fault_diagnostics.py --check`. Native controller builds/unit target run through
`scripts/reproduce_core.py`. The upstream storage patch README documents its separate-process
persistence/clear/error regressions and pinned-nightly mandatory checks.

`opendut_receiver_smoke.py` runs actual receiving-side/controller/network evidence;
`run_campaign.py` maps it to named scenarios. `receiver_integration_smoke.py` is the earlier
host-network fixture; `diagnostic_http_smoke.py` uses native HTTP with synthetic observations.
Their achieved verification levels differ. Read [claim-evidence.md](../docs/claim-evidence.md)
and [reproduction.md](../docs/reproduction.md). No historical13/13 or skipped CARLA check is
reported as current native end-to-end success.

`test_reproduction_lifecycle.py` covers real process-group child termination,
captured partial output, helper SIGINT/SIGTERM failure manifests and invalid input.
Its controlled compiler-wait fixture is never presented as a successful native build.
Actual Docker timeout/ownership gates and native-build cancellation are recorded in
`evidence/f008-build-cleanup-after` and `evidence/f008-real-build-interrupted`;
the updated wrapper's cached-input native core regression is `f008-process-group-native`.

`test_dashboard.py` checks authoritative admission/cancellation, restart/cleanup
uncertainty, HTTP mutation boundaries and artifact integrity.
`dashboard_diagnosis_smoke.py` uses the actual native HTTP provider with synthetic
observations; `dashboard_browser_smoke.py` uses actual local Chromium.
`evidence/f010-live/probe.py` records the separate native/physical/cancellation
acceptance through the dashboard. See [dashboard.md](../docs/dashboard.md).
