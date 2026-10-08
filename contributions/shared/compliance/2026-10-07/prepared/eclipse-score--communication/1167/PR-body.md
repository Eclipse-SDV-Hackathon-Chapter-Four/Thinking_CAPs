# Prepared draft — human review required

Adds one LoLa integration test covering repeated `OfferService`, `StopOfferService`, `StartFindService`, `Subscribe` and `Unsubscribe` calls. It compares discovered service identity/cardinality after duplicate offers, verifies absence after each stop, checks subscribed state and rejection after each unsubscribe, and verifies sample delivery and recovery with finite deadlines. The harness requires the application to exit 0.

Repeated discovery uses the same callback and instance specifier. Each returned search operation is checked for unchanged discovered service state and stopped; distinct operation handles follow the native implementation and existing watch-sharing/callback tests. Production APIs are unchanged.

The existing copyright checker BUILD/MODULE.bazel input strings are also corrected to filesystem paths. A separate utility patch is available for independent review.

Relates to #1167.

Validation on `e3d126c2d7569345cf5f790310702eb00cd86b06` with Bazel 8.7.0 and Ubuntu 24.04.4:

- Full build and formatting pass.
- Dedicated integration/schema tests: 2/2 pass; application exits 0.
- Full suite: 503 pass, 0 fail, 6 platform/configuration targets skipped; QNX runtime was not executed.
- Copyright reports 204 findings identical to the baseline with the checker-path correction, with no added findings. The untouched baseline checker fails before scanning its label-like paths. Inherited header repair remains separate scope; no waiver is claimed.

The patch also applies cleanly to upstream `9fa5a2f6cc78dd3f756df3ec3ea9466d38ee7dfd`. That newer upstream production subject has not been executed in the local native suite; the results above belong to the explicitly pinned baseline.


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)
- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
