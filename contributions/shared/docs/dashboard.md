# Vehicle Lab dashboard

The local browser UI provides OpenSOVD receiver diagnosis and a Test Manager for
project campaigns on the openDuT-managed bench. This is prepared work. The user's
4 October instruction defers second-contributor reproduction; it remains unattested
and does not stop current implementation. AAOS/FOTA remains deferred.

## Start

```sh
cd /home/jefferson/eclipse_sdv_hackathon_2026
cp config/dashboard/local.example.json .local/dashboard.json
/usr/bin/python3 scripts/run_dashboard.py --config .local/dashboard.json --port 8791
```

Open http://127.0.0.1:8791. The example identifies current verified native inputs
and registered historical physical/fixture reports; adjust absolute paths on another
host. Dashboard state and ledgers stay private in `.local/`. Configuration is an
operator file, never a browser-supplied command. Another server for the same bench
or state is rejected. The service binds only127.0.0.1; use SSH forwarding with the
same local port for remote access. It is a local demo service, not public hosting.

Deploy the existing owned bench before running native campaigns:

```sh
/usr/bin/python3 OpenDut/scripts/opendut_testbench.py up --state .local/opendut-f009 --output .local/dashboard-bench-up
```

Use new output directories. The dashboard does not provision/delete the bench.
When it is stopped, management is unavailable and a start records a blocked result.
Diagnostic applications exist during campaigns: unavailable diagnosis between runs
is expected, and retained values are labelled last observed. Startup/no first sample,
receiver freshness, diagnostic reachability and fault query state are separate.

## Diagnosis and campaigns

Diagnosis discovers actual OpenSOVD App resources. It shows speed/target/engagement,
units, ages and receiver source/session, plus native communication fault history
through the labelled App data fallback. Controller output and sample integrity
checks are unavailable in the current observation contract. Native `/faults` is not
claimed. Monitor assessment is separate from controller engagement policy.

Test Manager displays observed CLEO peers/devices, interfaces, local TLS profile
and disabled VPN/OIDC. Supported selections are `core` (fixture vehicle input with
real receiver/network/faults), `cleanup-failure` (expected deliberate failure with
actual restoration), and `carla` (real physical plant/harness operator requests).
This is project orchestration on openDuT, not an upstream test executor.

One authoritative UUID is persisted before launch and passed to the runner. Two
browsers, double-clicks, reloads and disconnects cannot create duplicate execution.
Closing a browser does not cancel. Cancellation stays pending until runner exit
and native cleanup/restoration are assessed. A cancelled run cannot pass; successful
restoration is shown separately. Missing/failed cleanup inhibits further starts.
Run control targets only the owned Popen process; campaign cleanup performs the
existing ownership-checked restoration. No direct actuation/delete/update actions.

Graceful service shutdown requests cancellation and waits up to70s for restoration.
If needed, only the owned process group is forcibly stopped; cleanup then remains
unknown. A SIGKILL/crash also cannot establish resource cleanup: restarted state
stays unknown and admission is inhibited. Preserve the ledger; inspect actual owned
containers/tunnel/capture processes and finalize evidence before creating fresh
state. Do not delete the ledger to bypass an unresolved run. CLI campaigns share
`campaign.lock`; the native child retains it through cleanup even if its parent dies.

## Evidence and verification

Original runner assertions/reasons remain authoritative. Historical results cannot
supply live health. The library exposes byte-exact allowlisted reports, manifests,
JUnit, timelines, observations and packet metadata. Packet payloads, credentials,
private files and arbitrary paths are excluded. Registered SHA256 mismatches and
missing artifacts are labelled independently of the original verdict. Saved replay
is hash checked and sandboxed; it remains a historical recording.

Current evidence:

- `evidence/f010-live/verification.json`:53 actual API/browser/download checks;
 42 native core assertions; cancellation during real managed-tunnel disturbance
 with cleanup acknowledged;46 physical CARLA assertions after an actual dashboard
 SIGSTOP/outage/resume. Two clients and reload retain the same UUID.
- `evidence/f010-native-diagnosis/verification.json`:8 actual native-provider/adapter
 checks using explicitly synthetic observations, including stale/new-session/outage.
- `evidence/f010-browser-acceptance/verification.json`: actual Chromium keyboard
 navigation, responsive rendering, historical downloads, text-injection and reconnect.
- `evidence/f010-keyboard-cancel/verification.json`: actual Chromium keyboard
 start/reload/cancel at both viewport widths, using an explicitly owned wait-process
 fixture. Missing native cleanup remains unknown and inhibits further starts.
- `tests/test_dashboard.py` (31 total project regressions): concurrent admission, unresolved restart, cleanup
 completeness, blocked runner, HTTP boundaries and artifact tamper/symlink tests.

These prove the current host slice, not a new-machine build, second human run,
hardware ECU/power-loss tolerance, event eligibility or awarded runtime bonuses.
ThreadX and AutoSD remain the proposals in `optional-runtime-integration.md`.
