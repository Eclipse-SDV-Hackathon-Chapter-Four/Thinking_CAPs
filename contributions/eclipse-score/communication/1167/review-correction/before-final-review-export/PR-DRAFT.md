# test: add dedicated integration coverage for idempotent COM APIs

**Local draft only. Semantic review, copyright disposition and ECA verification remain pending.**

Adds one dedicated LoLa integration test exercising repeated OfferService, StopOfferService, StartFindService, Subscribe and Unsubscribe calls. It checks service discovery, subscription/sample delivery, cleanup and recovery through resubscription and re-offering, using the native integration harness and finite polling deadlines. Production communication implementation is unchanged.

The current combined patch also corrects copyright checker inputs for BUILD and MODULE.bazel to use repository-relative filesystem paths. Separate test and utility patches are retained in the local review packet for the scope decision.

Relates to eclipse-score/communication#1167.

Validation on native baseline e3d126c2d7569345cf5f790310702eb00cd86b06, Bazel 8.7.0, Ubuntu 24.04.4:

- Full build and formatting pass.
- Dedicated integration/schema tests: 2/2 pass.
- Full suite: 503 pass, 6 platform/configuration targets skipped.
- Copyright check fails with 204 findings, identical to the measured baseline with only the checker-path overlay.

Open review questions: StartFindService currently uses distinct indexed callbacks; its coverage does not establish repeated identical arguments. Offer/stop discovery state should be checked before and after the duplicate operation. Passing execution is not a completed semantic review. See the local offline review packet for exact source locations, all measured evidence, skip declarations and source hashes.
