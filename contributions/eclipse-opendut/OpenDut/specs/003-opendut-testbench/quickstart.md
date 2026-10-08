# F003 validation guide
Prerequisites: rootful Docker, outbound release/registry access, OpenSSL, Python3,
16GB initial free disk, kernel GRE and NET_ADMIN in owned containers. Do not use host sudo.
From repository root run `python3 OpenDut/scripts/opendut_testbench.py prepare --state .local/opendut --output evidence/f003-prepare`,
then `up` with a fresh output directory. Expect two peers/devices and bridge/GRE membership.
Use status to inspect actual addresses before application placement. Run receiver smoke only
on this deployment with pinned receiver binary and isolated baseline/worktree mounts.
Finally run down with fresh evidence directory. Every live gate and cleanup must pass;
ping alone proves only initial Ethernet, not vehicle integration or CARLA.

Receiver command (system Python3.10 with zenoh):
```sh
/usr/bin/python3 OpenDut/tests/opendut_receiver_smoke.py --state .local/opendut --binary /tmp/sdv-opensovd-research-target/debug/sdv-receiver-diagnostics --score-source /home/jefferson/sdv-score-diagnostics/cc_s-core --baseline-source /home/jefferson/autoverse/vecu/s-core/cc_s-core --bridge-source /home/jefferson/autoverse/bridges/someip/zenoh-someip-bridge --output evidence/f003-fresh-receiver
```
Current smoke reuses the audited Bazel cache's flatc compiler and gateway schema to generate
its network configuration. Those paths are host-specific and are a reproduction dependency;
F005/F008 will parameterize them. Application images are resolved once to actual IDs.
The two local subnets are checked against host and Docker routes before creation. All
positive gates, timeout/recovery, packet provenance and app cleanup must pass. Use a fresh
output directory for each run. The same state supports down/up redeployment; the script
removes its CARL data volume during down and enrolls the same identities into fresh state.
