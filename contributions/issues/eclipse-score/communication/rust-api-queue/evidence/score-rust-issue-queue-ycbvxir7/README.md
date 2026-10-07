# Rust API Fabro queue

13 native Fabro runs are **Submitted and not started**. QNX #1278 is excluded.
The saved GitHub selection contains 14 open, unassigned `rust-api` issues without
`Flaky` in the title. This packet describes queue creation; it is not 13 issue fixes.

Every compiled run default and every agent node, including supervisor and correction
nodes, is pinned to **`deepseek-flash` / provider `deepseek`**, with empty fallbacks.
The isolated server has the real DeepSeek credential in its internal vault; this packet
contains no key or authentication material. The native catalogue reports configured=true;
live provider availability remains unmeasured. No model calls or starts were issued.

Source: eclipse-score/communication at `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Each job has a separate disposable source copy and branch on the bound external Linux
build volume. All 13 source/control/storage preflights passed, covering 2,878 source
subjects each. All 13 native graph validations passed. Seven direct guard checks passed.
Native product builds, tests, analyzers and live runtime hooks have not run for this queue.
Native Submitted states and zero usage are captured in each job's `native-state.json`
and `native-run-projection.json`, with the aggregate in `queue-verification.json`.

| Submission order | Issue | Mode | Native run ID | Maximum source corrections |
| --- | --- | --- | --- | --- |
| 1 | [#1265](https://github.com/eclipse-score/communication/issues/1265) Improvement: `paste` crate usage in the Rust COM API | reuse | 01M48JD9FH658K7YT576TBZMDN | 0 |
| 2 | [#1264](https://github.com/eclipse-score/communication/issues/1264) Improvement: `thiserror` crate usage in the Rust COM API | assessment | 01M48JD9RDK3RP70X670EE6HMG | 3 |
| 3 | [#1263](https://github.com/eclipse-score/communication/issues/1263) Improvement: `futures` crate usage in the Rust COM API | assessment | 01M48JDA0QNFM2TAYKFSA2YWYK | 3 |
| 4 | [#794](https://github.com/eclipse-score/communication/issues/794) Improvement: Remove bazel `tags = ["manual"]` from rust test targets | implementation | 01M48JDA9PPXQ4Z3RSSKSWHX87 | 3 |
| 5 | [#781](https://github.com/eclipse-score/communication/issues/781) Improvement: Implementation of MethodInArgPtr in rust side | implementation | 01M48JDAHZGPK27PM972TWCY7E | 3 |
| 6 | [#782](https://github.com/eclipse-score/communication/issues/782) Improvement: Runtime implementation for Rust Method APIs | implementation | 01M48JDAT6YRZT0FP52HS0MNC1 | 3 |
| 7 | [#1062](https://github.com/eclipse-score/communication/issues/1062) Improvement: E2E protection for Rust Method/Field APIs | design | 01M48JDB2Z5NSG7QPN3T6X3XPM | 3 |
| 8 | [#741](https://github.com/eclipse-score/communication/issues/741) Improvement: Move the Rust Sample example app from com/example to tutorial folder | implementation | 01M48JDBBDAC13S5DR3EFT6768 | 3 |
| 9 | [#560](https://github.com/eclipse-score/communication/issues/560) Improvement: Add Subscription State Change APIs Support on Rust API Lib | implementation | 01M48JDBKSA3M73YTE3WT4RA8D | 3 |
| 10 | [#490](https://github.com/eclipse-score/communication/issues/490) Improvement: Mock Runtime implementation of Rust COM-API | implementation | 01M48JDBW9K7TCR96CJJJK9T00 | 3 |
| 11 | [#250](https://github.com/eclipse-score/communication/issues/250) Improvement: COM-API FindServiceSpecifier::Any support | implementation | 01M48JDC53VN4K6VC17GX79RHX | 3 |
| 12 | [#1261](https://github.com/eclipse-score/communication/issues/1261) Improvement: Provide an async stream of newly available services | implementation | 01M48JDCDCTPSG39G84F50CNKM | 3 |
| 13 | [#173](https://github.com/eclipse-score/communication/issues/173) Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate) | assessment | 01M48JDCP6JAS18EM34S24ZCN4 | 3 |

New jobs have at most three measured source correction stages and no automatic model
retry. #1265 reuses the existing pushed assessment and historical review; its exhausted
budgets remain exhausted and it has zero new source corrections or native check nodes.
Its six Linux cases at 8368bfb5 and earlier Rust checks retain their historical baselines;
they are not current evidence for 381d43de. Context copies are labelled historical.

Assessment and design modes constrain source writes to native documentation/design
artifacts. #1062 must retain pending design decisions. Issue/backend premises such as
#250 and #490 must be checked against the selected source. Prerequisite hints in queue.json
control submission order only; runtime dependency satisfaction is not established by order.
Fabro owns execution and state. There is no separate scheduler. The metadata server limits
concurrent runs to one, but no queued run has been started.

Before execution, bind an actual hash-bound Linux measurement launcher using the driver's
`linux-measurement-binding.json` contract and qualify the native working-directory/file-tool
hooks. An absent launcher is retained as missing evidence (`passed=false`), without spending
source repairs. A successful collection/export or Fabro conclusion cannot imply passing
native checks or human engineering acceptance. No human/approval-wait nodes are present;
engineering decisions remain pending offline.

The active queue root and isolated server URL are in server-binding.json/queue.json.
Validate storage before further operations; stop on disconnection/remount. Keep provider
keys and private server state internal. The currently submitted run IDs must be reused;
do not rerun prepare_queue.py or submit_queue.py, replace the server, or create duplicates.
These scripts are preparation provenance, not a replayable scheduler. Registered packages
and current control hashes are authoritative for the submitted runs.

Queue-creation refusals are preserved under attempts/ and are not source corrections.
The first run create was explicitly refused for an unconfigured provider; native empty-state
reconciliation preceded retry. All 13 registrations and creates now have native responses.

This packet includes selected issues/comments, workflow packages, native state, source
hashes, controls, storage binding, measured preparation checks and failed preparation
attempts. Complete disposable source copies and internal Fabro storage stay at their bound
locations. Future run exports are written to each SSD job/export; copy and seal those
outputs into contributions after execution, retaining failures and pending acceptance.
No issue fix, upstream publication, qualification, acceptance or native contribution status
is claimed by queue submission. `artifact-manifest.json` binds every packet payload.
