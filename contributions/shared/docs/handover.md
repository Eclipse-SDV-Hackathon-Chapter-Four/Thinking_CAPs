# Overnight implementation handover

Prepared on 4 October 2026 in `contributions/eclipse-sdv-hackathon`. AAOS/FOTA is
deferred by the user. The verified slice runs the actual S-CORE receiver and control
return, native OpenSOVD App data, native fault reporter/DFM/KVS and a two-peer local
openDuT network. Both fixture and actual CARLA campaigns are verified. The physical run
uses explicit harness pedal/engagement and waypoint steering requests through existing
topics; native Cruise Control/VCU supplies throttle. AAOS/FOTA and second-contributor signoff are deferred by the user; no successful update or human signoff is claimed.

## Results to inspect first

- [Current committed-source reproduction](../evidence/f009-reproduction-current/verification.json):
  frozen `0b8a67e`, new source/native build directories, fresh compiled configuration
  tools actually used, controller unit tests and Rust tests/Clippy passed. Its core
  campaign passes42 assertions; the [subsequent physical campaign](../evidence/f009-reproduction-physical/results.json)
  passes46, with67 zero-pedal sampled native/VCU/actor correlations. Host, immutable
  images and LLVM repository are shared; independent person reproduction is still pending.
- [Offline saved-run replay](../evidence/f009-recorded-replay-final/index.html):
  source-hash-verified physical speed, receiver/fault snapshots, throttle and event
  playback in a standalone browser page. [Browser checks](../evidence/f009-replay-browser/verification.json)
  and [rejection gates](../evidence/f009-replay-gates/verification.json) pass. It contacts
  no live service and cannot establish current health; the [live dashboard](../specs/010-diagnosis-test-dashboard/spec.md)
  is now implemented and verified separately in F010.
- [Final real CARLA results](../evidence/f009-carla-native-final/results.json): nine selected
  scenario/runner verdicts passed, ten deferred/conditional checks skipped; all46 native/
  physical assertions passed. [Control-return correlation](../evidence/f009-carla-native-final/native/carla-control-return.json)
  records67 matches from positive native request through existing VCU/vehicle scaling to
  subsequent physical actor throttle, with zero operator pedal. This is sampled correlation,
  without an E2E sample identifier or guaranteed latency.
- [Final core results](../evidence/f005-core-final/results.json): eight selected
  scenario/runner verdicts passed; ten conditional/deferred checks skipped. All 42
  assertions in the native child passed.
- [Clean-source reproduction](../evidence/f008-reproduction-final/manifest.json):
  new frozen integration/Score/bridge checkouts, fresh native build directories,
  controller unit target, Rust tests/Clippy and the native campaign passed. This is
  the implementation agent's self-run; host/images/LLVM and baseline configuration tools
  were shared. F009 subsequently fixed shadowed compiler/schema inputs and verified actual
  fresh-tool execution in the physical and [fixture regression](../evidence/f009-fixture-regression/results.json).
  The first failed attempt is retained in `f008-reproduction-first`.
- [Fault lifecycle](../OpenSOVD/evidence/f004-receiver-signal-fix/results.json): actual loss,
  held recovery, diagnostic/DFM process restart, durable history and signal cleanup.
- [Failure cleanup](../evidence/f005-cleanup-failure/results.json) and
  [interrupted campaign](../evidence/f005-interrupted-core/results.json): scoped
  recovery passed; the interrupted campaign correctly remains failed.
- [Claim/evidence map](claim-evidence.md), [reproduction instructions](reproduction.md)
  and [upstream patch packet](../OpenSOVD/contributions/fault-storage-write-through/README.md).

`a25868e` contains receiver diagnostics and the local testbench. `6d7bef9` freezes
the native fault/campaign implementation used by the clean-source reproduction.
`3badf4a` contains the initial handover; subsequent F009 work resolves CARLA startup-client
failure and verifies physical/native acceptance. No upstream PR or message
was sent. Work remains preparation before the stated 6–8 October event.

## Restart and demonstrate

The owned testbench is shut down at handover. Follow `docs/reproduction.md` to prepare
new private state, deploy its peers and set the private input JSON. The original
Score implementation is `/home/jefferson/autoverse/vecu/s-core/cc_s-core`; receiver
instrumentation lives in a separate worktree and exported patch. Build caches remain
available. Certificates expire after seven days; generate new private state later.

```sh
/usr/bin/python3 scripts/run_campaign.py --config .local/campaign.json --scenario core --output evidence/my-demo
/usr/bin/python3 scripts/run_campaign.py --config .local/campaign.json --scenario carla --output evidence/my-physical-demo
```

Use a new output directory and a configuration naming the newly deployed state and
validated binaries. A new source/build reproduction is described in `reproduction.md`.
Check the JSON/JUnit verdicts and native HTTP observations before presenting results.

The [eight-minute technical interview](hackathon/technical-interview.md) provides
the required six-minute evidence/demo segment plus two minutes of questions.
The [final-pitch deck](hackathon/pitch.html), [speaker notes](hackathon/pitch-notes.md)
and [printable PDF](../evidence/f008-presentation-browser/pitch.pdf) target9:30.
Actual browser checks pass; a human rehearsal has not been recorded.

For the six-minute evidence/demo segment:

1. In one minute, show the existing X-Verse vehicle path and separate diagnostic process.
   Select the actual CARLA campaign for the vehicle demonstration. State which operator
   requests the harness generates and which throttle requests come from native Cruise Control.
   The fixture core is a separately labelled fallback.
2. In two minutes, show nominal accepted speed, source/session/boot/build identity,
   controller state and freshness through native OpenSOVD App data. Disconnect the
   owned GRE path: the receiver heartbeat stays alive while accepted input ages,
   and the debounced `CC.LostCommunication` fault becomes active. Restore the path
   and show held recovery. The diagnosis is lost communication, without assigning
   a physical root cause.
3. In two minutes, show diagnostic stall while controller returns continue, then
   diagnostic/DFM restart with native history retained. Open the narrow write-through
   storage patch and its original failing separate-process regression plus patched
   native tests. The integration uses App data for fault history; native `/faults`
   routing remains upstream work.
4. In one minute, show verdicts, input hashes and owned cleanup. Name the harness,
   human-signoff and FOTA limits. A saved successful run is a labelled recorded
   fallback if a fresh run is unavailable; it does not establish current acceptance.

For a three-minute pitch, spend one minute on the observable failure and control/
diagnostic separation, one on the actual loss/recovery/history evidence, and one on
the reproducible upstream patch and remaining milestones. Make no update demonstration
or full vehicle claim.

## Continuation work

| Item | Current boundary / next acceptance |
| --- | --- |
| CARLA | Verified actual0.9.15 world/Tesla/frames/physical native return in F009. A client created before server bind retained failed connection state; fresh clients recovered, proven by controlled comparison. Keep retries bounded and operator steering explicit. Requested startup map URL was ignored by the existing server; actual recorded map is Town10HD_Opt. Owned server stops may print engine crash-on-exit diagnostics; resource removal is verified, graceful engine shutdown is not claimed. |
| Independent reproduction | A real second contributor must execute setup/campaign and fill [reproduction-signoff.json](reproduction-signoff.json). A new checkout on this host is insufficient for that human requirement. |
| Native fault route | Coordinate with the existing upstream owner of native `/faults`; current App data fallback is explicit. No ownership agreement has been claimed. |
| Upstream submission | Review the bounded storage packet, upstream account/ECA requirements and full applicable CI before any authorized public submission. Local native tests do not establish full upstream CI. |
| AAOS/FOTA | Wait for the real asset. No installer, successful update or update regression has been substituted. |
| Dashboard | F010 is implemented: live OpenSOVD diagnosis, authoritative project campaigns on openDuT, cancellation/cleanup and verified evidence downloads; see docs/dashboard.md. |
| Optional extensions | E2E, plausibility/sequence profiles, native updates and VIPER remain unselected. The user added ThreadX/AutoSD feasibility; [bounded integration proposal](optional-runtime-integration.md) documents potential +0.20 eligibility and useful roles, without claiming runtime integration or awarded points. |
| Event inventory | Record the actual event-start revision and subsequent delta; do not relabel this prepared work as event-time creation. |

See `evidence/f009-bench-down` and `evidence/f009-preservation.json` for final resource
and original-source checks. Private credentials, captures and runtime configuration
stay in ignored local state. Initial harmless generated CARLA configuration files
were removed from tracked evidence; failed/blocked measurement logs are retained.

The newer self-reproduction bench is also down: [teardown](../OpenDut/evidence/f009-reproduction-bench-down/results.json).
The [current preservation recheck](../evidence/f009-preservation-recheck/verification.json)
confirms absent owned resources, unchanged locked application/configuration hashes,
both runtime images, original stopped containers, CARLA binary and all seven original
repository revision/status/diff comparisons. The [earlier partial comparison](../evidence/f009-reproduction-preservation.json)
omitted the original auditor's universal newline normalization for156 CRLF sequences.
It is retained as an audit-method failure; no original file was changed to resolve it.

Future reproduction manifests record caller attribution through `--operator` and
`--shared-host` / `--no-shared-host`, plus observed environment. Omission remains unknown;
the helper cannot attest independent human reproduction. Bounded attribution checks
are separate from the successful frozen native/physical runs.

The reproducer now stops owned command groups and finalizes exact labelled build/
ownership-repair containers on timeout/SIGINT/SIGTERM. The [actual build cancellation](../evidence/f008-real-build-interrupted/verification.json)
retains a failed verdict while both cleanup records pass. [Timeout and ownership checks](../evidence/f008-build-cleanup-after/verification.json)
and20 Python regressions pass; an unowned container or unavailable Docker cannot
appear as successful cleanup. The [updated wrapper's native core regression](../evidence/f008-process-group-native/verification.json)
passes42 assertions with cached validated binaries. The [bench is down](../OpenDut/evidence/f008-process-group-bench-down/results.json),
and [current preservation checks](../evidence/f008-process-group-preservation/verification.json)
pass. This adds no claim of another successful fresh build, human rehearsal or second
contributor's execution.

The latest user instruction defers second-contributor reproduction for now.
It no longer blocks local implementation. F010 actual dual-client/native/physical/
cancellation/browser verification is recorded in `evidence/f010-live` and
`evidence/f010-browser-acceptance`; original source/state preservation passes in
`evidence/f010-preservation`. Use [dashboard.md](dashboard.md) for launch and limits.
