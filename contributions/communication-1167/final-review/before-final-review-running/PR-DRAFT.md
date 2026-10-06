# test: add dedicated integration coverage for idempotent COM APIs

**Local draft only. Engineering review, baseline copyright disposition and ECA verification remain pending.**

Adds one dedicated LoLa integration test exercising repeated OfferService, StopOfferService, StartFindService, Subscribe and Unsubscribe calls. It compares discovered service identity/cardinality after the first and duplicate offers, verifies absence after each stop, reuses the same discovery callback and instance specifier for three registrations, checks subscribed state after the duplicate subscription, and checks GetNewSamples rejection after each unsubscribe. Exact sample delivery, resubscription, re-offering and cleanup use finite polling deadlines and the native integration harness.

The native discovery implementation creates a separate search operation for each StartFindService call. The test checks unchanged discovered service state for each returned operation and stops them all; it does not assert equal registration handles. Adequacy for the issue's state-invariance intent remains an offline reviewer decision.

The combined patch also corrects existing copyright checker inputs for BUILD and MODULE.bazel to use repository-relative filesystem paths. Separate test and utility patches are retained for the reviewer's scope decision.

Relates to eclipse-score/communication#1167.

Fresh validation of the corrected candidate on native baseline e3d126c2d7569345cf5f790310702eb00cd86b06, Bazel 8.7.0, Ubuntu 24.04.4:

- Full build and formatting pass.
- Dedicated integration/schema tests: 2/2 pass.
- Full suite: 503 pass, 0 fail, 6 platform/configuration targets skipped. No QNX execution is claimed.
- Copyright fails with 204 findings, identical to the measured baseline with only the documented checker-path overlay; the untouched baseline checker failed before scanning label-like paths.

Current source/patch: `review-correction/verification-run/candidate/` and `review-correction/verification-run/communication-1167.patch`. Native run: `01M485DJP96AGJYWA02WE41KQA`. Complete evidence, source hashes, build products and OCI test image are in that run packet. The original candidate and historical measurements remain intact. Passing execution is not engineering acceptance; see `review-correction/OFFLINE-REVIEW.md`.
