# F004 validation guide
Prepared 4 October 2026. From the integration repository:

```sh
python3 contributions/eclipse-opensovd/OpenSOVD/scripts/build_fault_diagnostics.py --target-dir /tmp/sdv-fault-profile --output evidence/f004-my-build --check
/usr/bin/python3 contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py --state .local/opendut --binary /tmp/sdv-fault-profile/debug/sdv-receiver-diagnostics --score-source /home/jefferson/sdv-score-diagnostics/cc_s-core --baseline-source /home/jefferson/autoverse/vecu/s-core/cc_s-core --bridge-source /home/jefferson/autoverse/bridges/someip/zenoh-someip-bridge --output evidence/f004-my-run --fault-lifecycle
```
Use a NEW output directory and deployed F003 state. Omit --fault-source to acquire the pinned
upstream clone and apply the exported storage patch in private state; an explicit source must
match that patch exactly. Keep default and feature builds in separate target directories so a
later default build cannot replace the executable intended for the native fault campaign.
Actual timing, identities and verdicts are recorded in the run manifest/results. Expect startup
unknown, held Passed nominal, one Failed loss occurrence, active-fault OS-process reload, held
Passed recovery retaining history, and collector loss unknown. Both SIGINT/SIGTERM exit cleanly.
Native `/faults` remains absent. See completion.md and the upstream patch README for exact tests.
