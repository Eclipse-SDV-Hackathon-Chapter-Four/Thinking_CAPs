# Offline P704 scope review

The next decision concerns native scope and applicability, not approval of the already
reviewed #704 patch. The owner’s earlier approval and budget exception remain recorded.
This draft cannot supply native engineering acceptance or start a trial itself.

| Decision | Concrete proposal | Current status |
| --- | --- | --- |
| Original source | Lifecycle main `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`, unchanged at the fresh read | Bound |
| Expected checks | Two CI build profiles; three whole-tree CI test profiles; remaining ready-job dependencies; all semantic oracles in [the matrix](native/check-matrix.json) | Proposed; native owner must accept or record tailoring |
| Inventory | All 135 discovered labels, including the five historical pilot labels | Discovery only; not 135 executed tests |
| Native impact | Preserve `feat_arc_sta__lifecycle__cfg_params_static`, version 1, valid, ASIL_B/security YES; bind source-to-Need mapping and applicable work products | Unresolved |
| QNX | Obtain authentic pinned SDK plus required access/license, or explicitly defer platform obligations in a bounded experimental scope | Unresolved; no automatic waiver |
| Verification and review | Name native owner/reviewer roles and objectives, methods, criteria, environment, anomaly/regression dispositions | Unresolved |
| Model | Same Flash alias and explicit non-thinking JSON settings in both arms | Official documentation refreshed; effective live behavior unmeasured |
| Context | Same common rendering and 24,000-byte guard | Reconstructions fit; actual native preflight still required |
| Acceptance | Review complete reports offline after workflow report/exit | Pending; no workflow human nodes |

Two scope choices are ready for review. Selecting either requires a recorded owner
decision; this report selects neither.

1. **Complete native qualification:** accept or tailor every row in the proposed matrix,
   bind the native impact/work-product denominator and roles, and resolve the QNX SDK
   dependency before execution. Whole CI is proposed because the source CI specifies it;
   it is not inferred to be the complete safety/security obligation set.
2. **Bounded Linux experiment:** explicitly authorize a Linux-only paired experiment with
   the five pilot targets and retained semantic oracles; record all deferred CI/platform
   and native impact obligations. Its result can characterize the experiment, but cannot
   satisfy full native qualification or T033 engineering acceptance. QNX fetches may still
   block Bazel dependency loading even for a Linux experiment; applicability tailoring
   alone does not repair that dependency.

The QNX URL and checksum are confirmed in the selected toolchain’s version matrix.
The earlier reverse query received a different checksum. Its cause is unknown; the bytes
are not characterized as an authenticated SDK or an access-denied page. No retry occurs
here. [The binding](native/qnx-binding.json) supplies exact hashes and original failure
references; do not weaken the checksum or substitute an unverified archive.

The initial reconstructed baseline/optimized requests were 30,493/27,140 bytes. After
common serialization changes they are 23,939/20,697 bytes. The baseline’s 61-byte margin
is narrow: require a no-provider native payload observation before enabling real requests.
These byte counts are conservative guard measurements, not provider token usage or
whole-task savings. Correction, review, tools, cache and failures remain in future totals.

DeepSeek documents the Flash alias as V4.1-Flash and usage placement in SSE.
The local synthetic final-content-chunk check succeeds. Actual requests, response model,
effective settings and native accounting still require observation. Sources:
[official pricing](https://api-docs.deepseek.com/quick_start/pricing/?tab=case-studies),
[official chat contract](https://api-docs.deepseek.com/api/create-chat-completion/).

The fresh [issue read](https://github.com/eclipse-score/lifecycle/issues/704) has no
assignee, timeline cross-reference or explicit #704 mention in 22 inspected open PRs.
This does not prove nobody is working privately. Refresh activity and source drift again
immediately before a real trial. Publication remains deferred.

Record the chosen scope, exact matrix dispositions, native denominator/roles, QNX
decision and supporting rationale in [the blank decision record](offline-decision.json).
Rebind that completed record by digest before preparing executable worker/stage/meter
instructions. Tests, successful Fabro runs and this packet never fill those fields.
