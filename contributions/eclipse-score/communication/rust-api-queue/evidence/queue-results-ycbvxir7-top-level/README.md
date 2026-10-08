# S-CORE Rust API queue results

All 13 selected native Fabro runs are terminal and their complete available
patches, reports, native events and Linux measurement evidence are exported. This is a
results packet, not a declaration that all issues are solved. Engineering acceptance
and adoption remain pending offline; no issue was closed and no new results were pushed.

| Issue | Artifact | Fabro status | Verification disposition | Supervisor artifact | Corrections |
|---|---|---|---|---|---|
| [#1265](issues/1265/collection-summary.json) | report/assessment | succeeded | historical reuse; no new checks | written review present | 0/0 |
| [#1264](issues/1264/collection-summary.json) | report/assessment | succeeded | failed/missing selected checks | written review present | 3/3 |
| [#1263](issues/1263/collection-summary.json) | report/assessment | succeeded | failed/missing selected checks | **written review missing** | 3/3 |
| [#794](issues/794/collection-summary.json) | report/assessment | succeeded | failed/missing selected checks | written review present | 3/3 |
| [#781](issues/781/collection-summary.json) | draft patch | succeeded | failed/missing selected checks | written review present | 3/3 |
| [#782](issues/782/collection-summary.json) | report/assessment | succeeded | failed/missing selected checks | written review present | 3/3 |
| [#1062](issues/1062/collection-summary.json) | report/assessment | succeeded | failed/missing selected checks | written review present | 3/3 |
| [#741](issues/741/collection-summary.json) | boundary-probe artifact; not an issue fix | succeeded | failed/missing selected checks | written review present | 3/3 |
| [#560](issues/560/collection-summary.json) | draft patch | succeeded | failed/missing selected checks | written review present | 1/3 |
| [#490](issues/490/collection-summary.json) | draft patch | succeeded | failed/missing selected checks | **written review missing** | 3/3 |
| [#250](issues/250/collection-summary.json) | report/assessment | succeeded | failed/missing selected checks | **written review missing** | 1/3 |
| [#1261](issues/1261/collection-summary.json) | draft patch | succeeded | failed/missing selected checks | **written review missing** | 1/3 |
| [#173](issues/173/collection-summary.json) | report/assessment | succeeded | failed/missing selected checks | **written review missing** | 2/3 |

Every observed agent, correction and supervisor call used `deepseek-v4-flash` from
DeepSeek (configured alias `deepseek-flash`), with no fallback. New issue runs used at
most three correction stages. #1265 reused historical evidence with zero new fixes;
its prior exhausted budgets were preserved. QNX #1278 was excluded.

All workspaces started from communication baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
The native scheduler ran up to five jobs; its startup concurrency flag of one was not
applied. Prerequisite hints affected submission order only. Workspaces remained
independent; no predecessor patch or backend contract was silently integrated.

Each issue directory contains a bound exported binary-capable patch (including new
files), its final changed source, reports, captured issue/context, exact workflow,
initial/final source hashes, raw protected check outputs, complete paginated native
events, final run/state records and a terminal collection summary. Per-issue manifests
and the packet manifest bind every payload. Native checkpoint commits were retained;
the collector's separate index verified each patch against final source without
changing a native index or creating another correction.

`verification-audit.json` records actual agent identities, all failed commands and
command-specific Bazel test-result events. Consult each supervisor and raw logs for
the issue-specific blocker and applicability findings. A successful Fabro export can
retain failed checks; it is not a passing native verification result.
If a supervisor stage completed without writing its required report, the missing
review remains explicit in the table and `gaps/`; native stage output is preserved
without inventing a replacement review or resetting the correction budget.

Known measurement limits: `docs` checks built their selected targets and did not execute
`rust_doc_test`. Test XML copied during an attempt may also include earlier runs;
command-specific Bazel events identify actual executed test targets. Inner Rust case
totals are not inferred from wrapper XML. Checks remain tied to their measured subject
hashes; a mismatch is stale evidence, not current verification. Native requirement,
safety, qualification and acceptance gaps remain explicit in the reports.

`provenance/` preserves source/tool/config/storage/authority bindings and verified
links to the unchanged creation and Linux launch packets. Original issue text and
license notices are preserved. Runtime binaries are identified by hash; raw tool
caches are retained on the bound SSD rather than copied here. Credentials and private
Fabro/vault/server state remain internal and are excluded from exports.

The selected SSD binding was validated before collection and cleanup. After all
selected runs became terminal and their evidence was retained, only this queue's owned
rootless Docker and private Fabro server were stopped. `lifecycle/` retains cleanup
evidence. No active queue was relocated, no disk reformatted, and no budgets reset.

Next step: review the issue packets offline and decide which proposals to adopt or
which unresolved checks need a separately authorized follow-up run.
Recommended model: deepseek-flash — the user-required model for any subsequent Fabro run.
