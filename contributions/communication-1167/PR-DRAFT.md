# test: add dedicated integration coverage for idempotent COM APIs

Local draft for eclipse-score/communication#1167. Agent technical review is complete; formal engineering disposition and ECA verification remain pending.

Adds a dedicated LoLa integration test for repeated OfferService, StopOfferService, StartFindService, Subscribe and Unsubscribe calls. It compares complete discovered service identity/cardinality after the first and duplicate offers, verifies absence after each stop, repeats the same discovery callback and instance specifier three times, checks subscribed state after duplicate subscription, and checks GetNewSamples rejection after each unsubscribe. Exact sample delivery, resubscription, re-offering and cleanup use finite polling deadlines. The Python harness explicitly requires the native application to exit 0, rejecting signal exit codes permitted by the upstream wrapper.

Native discovery allocates a separate search operation per StartFindService call. Existing native tests verify watch sharing and separate callback invocation. This contribution checks unchanged discovered service state for each operation and stops them all; it preserves their distinct handles. Production APIs, visibility goldens and module lockfile are unchanged.

A separate utility patch corrects existing copyright checker BUILD/MODULE.bazel input strings to repository-relative paths. The test-only, utility-only and combined patches are exported independently.

Fresh validation on baseline `e3d126c2d7569345cf5f790310702eb00cd86b06`, Bazel 8.7.0 and Ubuntu 24.04.4:

- Full build and formatting pass.
- Dedicated integration/schema tests: 2/2 pass; application exit 0.
- Full suite: 503 pass, 0 fail, 6 platform/configuration targets skipped. No QNX execution is claimed.
- Copyright fails with 204 findings identical to the baseline with the documented checker-path overlay. The untouched baseline checker failed before scanning label-like paths. Agent disposition: pre-existing failures, no additions, no waiver; inherited header repair remains separate scope.

Current source, patches, complete evidence/products and native test OCI image: `final-review/verification-run/`. Run `01M4878Q65ENC6PJ5AEJ6NMWB3` is terminal/exported. Review: `final-review/TECHNICAL-REVIEW.md`; measured bindings: `final-review/final-binding-verification.json`; skipped targets: `final-review/verification-run/skipped-tests.json`. Original and earlier corrected packets are preserved. Publication has not been authorized or performed.
