# Rust API queue — Linux execution launch

The user authorized execution with `go`. All **13 issue start requests** were accepted
by native Fabro. QNX #1278 remains excluded. Latest observed states at
2026-10-06T14:45:14.845855+00:00 were `{"runnable": 7, "running": 5, "succeeded": 1}`.
This is a launch snapshot, not a claim that all issues are resolved.

All active issue models and the live hook qualification model are
**`deepseek-v4-flash`, provider `deepseek`**. Their configured alias is `deepseek-flash`;
compiled run defaults and every agent node have empty fallbacks. Each issue has a Flash
supervisor stage; new issues allow at most three source/plan correction stages, no
unbounded retries. #1265 is evidence reuse with zero new corrections or tests. Offline
engineering acceptance remains pending; no publication, merging or native acceptance
has been authorized or synthesized.

Fresh operational evidence at source `381d43dec900ab6a9076f3f30e7bfbdee019e26e`:

- The native Linux query and `score_com_concept-test` target passed. Cached test results
  were disabled. Raw logs, XML and Bazel events are under linux-readiness/results.
  XML counts the native wrapper as one test; no unmeasured inner-case total is claimed.
- The actual Flash hook probe allowed a bounded read and refused shell execution.
  Actual stage working directories resolve to the selected SSD workspace.
- All 13 revised graphs validated and bound source/control preflights passed.
  Started issue runs also passed their real native preflight before model stages.
- Thirteen carried runtime libraries and 103 notices were rehashed. No old product
  test results were promoted to this baseline. Runtime is a private newer library
  namespace over host Linux tools, not a qualified compiler or full CI claim.
- A new private rootless Docker daemon is bound to this queue's SSD data root, with
  credentials and private runtime/server state internal. Existing runtimes were not started.

The first command-only native probe failed at Fabro's shallow Git checkpoint push,
before any model call. Its native failure is retained under runtime-probe/. The second
probe passed after explicit source-workspace binding, clone disablement and a private
snapshot repository allowing shallow updates. The measured initial checkpoint advances
HEAD; revised preflight verifies the published native checkpoint, baseline ancestry and
all unchanged initial source subjects instead of falsely requiring identical HEAD.

The earlier 13 unstarted runs were cancelled and archived with native responses retained
in original-jobs/. The original sealed creation packet remains unchanged. Revised
registered definitions and active IDs are explicit here; no run counter was reset.

The startup CLI concurrency flag requested one but did not affect native scheduler
settings. `GET /api/v1/settings` reported **max_concurrent_runs=5**, matching five active
runs. The current native execution keeps that capacity to preserve active progress.
This corrects the original single-run capacity claim. Fabro owns dispatch/state; start
requests were submitted in order and there is no separate scheduler. Submission order
alone does not establish fulfilled engineering or backend prerequisites.

| Issue | Active native run ID | Observed state | Maximum corrections |
| --- | --- | --- | --- |
| 1265 | 01M48T910BV0WNQ2DTFE7PEJYJ | succeeded | 0 |
| 1264 | 01M48T91RFE84GZZ7V6BJE74ME | running | 3 |
| 1263 | 01M48T92EYENW49NYZS284TEMW | running | 3 |
| 794 | 01M48T93740W3Q66C2X9PS6VPX | running | 3 |
| 781 | 01M48T93XWB3PQNRW3DWQJMQ55 | running | 3 |
| 782 | 01M48T94N9RXXTJE5GD271GGGW | running | 3 |
| 1062 | 01M48T95DN8JE8SGQP7BETEMB9 | runnable | 3 |
| 741 | 01M48T964A9V9G2D20TGS8DZBM | runnable | 3 |
| 560 | 01M48T96VAH4K085F0Z1QHRNMS | runnable | 3 |
| 490 | 01M48T97EJ8WBTG3MZK693R4QX | runnable | 3 |
| 250 | 01M48T982TFZGY0MCN40SPCZW1 | runnable | 3 |
| 1261 | 01M48T98RSDKMEMCH9D8DEX631 | runnable | 3 |
| 173 | 01M48T99G1EHJJKE26XCD8JS1Z | runnable | 3 |

Per-issue SSD job/export contains the patch, reports, measured raw evidence and bound
manifest as that workflow reaches export. #1265's completed reuse export is included in
this snapshot when present; its historical checks keep their original baseline scopes.
Later job outputs need final collection/sealing into contributions. A Fabro success may
be a scoped assessment or blocker report and must not be equated with issue acceptance.

Keep the bound SSD connected. Validate storage before further operations; never move
active workspaces or recreate the queue. Reconcile these native IDs before any restart
or retry, retain failures, and never exceed the remaining per-job correction budget.
The metadata server and owned Docker daemon stay available for ongoing work. After
terminal collection, stop only these owned processes. No keys, private databases,
authentication files or private server logs are included. artifact-manifest.json binds
every payload; this packet is local and has not been committed or pushed.
