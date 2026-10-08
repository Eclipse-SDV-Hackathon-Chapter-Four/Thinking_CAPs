# Corrected contribution review — exported measurements

This is an agent-prepared offline review packet; engineering acceptance, ECA verification and publication remain pending. Fabro run `01M485DJP96AGJYWA02WE41KQA` uses stable fabric `b2aa9a7a49a054621f38e59f3aef6d6e5daf3cce`, native communication baseline `e3d126c2d7569345cf5f790310702eb00cd86b06`, Bazel 8.7.0 and the pinned Ubuntu 24.04.4 image. Source is `verification-run/candidate/`; the original candidate and historical results remain unchanged.

The operator clarified that the former loop27 volume is now loop1. UUIDs and the original registered backing image match; all 2,885 saved original candidate source hashes were verified. New storage admission and validation passed through stable `score_sw_fabric.storage`; old bindings are preserved. Only the originally added integration test's `main_api_idempotency.cpp` changes between the original and corrected candidate. All 2,877 native baseline-overlay source files remain unchanged. See `storage-reconciliation.json`, `source-application.json` and `verification-run/source-scope-comparison.json`.

| API | Current observable assertion | Source location |
| --- | --- | --- |
| OfferService | First offer discovers exactly the one configured service; duplicate offer succeeds and retains the complete discovered handle container | main_api_idempotency.cpp:146 |
| StopOfferService | First stop makes discovery empty; the second stop retains absence; re-offer and final cleanup succeed | main_api_idempotency.cpp:291 |
| StartFindService | One identical callable and instance specifier are reused in three calls; each returned search operation observes the original service container; synchronous discovery remains unchanged; all searches are stopped | main_api_idempotency.cpp:161 |
| Subscribe | Same sample limit used twice; state remains subscribed immediately after the duplicate; first sample batch is received exactly | main_api_idempotency.cpp:246 |
| Unsubscribe | Each of two calls is immediately followed by GetNewSamples rejection with kNotSubscribed; resubscription receives a second exact sample batch | main_api_idempotency.cpp:260 |

The callback stores per-operation discovery results under a mutex, with its captures alive until every search is stopped. The native implementation allocates distinct search handles and retains callbacks, so the test checks unchanged discovered service state without asserting equality of registration handles. Native registration semantics and adequacy for the issue's state-invariance intent remain an offline reviewer decision. No automated human disposition is recorded for prior review questions 01/02. Their proposed source corrections are now implemented in the isolated candidate.

Finite polling deadlines, native integration harness/configuration and license notices remain intact. No production implementation, public API golden, module lockfile or unrelated source changes were introduced. The combined contribution retains the earlier copyright utility path correction, with separate reviewable patches to be exported.

Fresh formatting and both focused integration/schema tests pass. Copyright still fails with exactly the same 204 normalized findings as baseline-with-checker-path-overlay; there are no added findings. The full build passes. The full suite passes all 503 executed tests, with 6 targets skipped; no QNX runtime execution is claimed. Exact target names are in `verification-run/skipped-tests.json`, and unchanged declarations are carried from the previous offline review with reverified source hashes. Historical passes do not qualify this changed source. The untouched baseline copyright command failed before scanning label-like paths; its measured comparison used only the documented checker-path overlay, and that limitation is retained.

Current raw logs and measurements are in `verification-run/evidence/`; all five mandatory check commands are retained, and tests use `--nocache_test_results` with unique native per-test temporary directories. Only repository download cache content was copied into the new workspace; previous measured test outcomes are not reused. Native build parallelism is bounded to eight jobs.

No prompt/model/human nodes or provider defaults are present in this Fabro workflow. It has only verify/export commands, with failure routed to export. Successful Fabro termination never means all native checks pass. No new paid calls occurred; the original supervisor remains exhausted at three corrections, its prior $10 envelope and unknown billed cost are retained. No submission, merge, issue closure or engineering acceptance is performed.

## Exported measurements and subject binding

The Fabro run is terminal with verify/export stages retained. Native copyright verification failed; failure was routed to export and remains visible in the native state. Successful workflow termination records completion of export rather than engineering acceptance or all native checks passing.

All 2,885 corrected candidate source hashes match the build workspace. All 2,885 historical candidate hashes are unchanged. Five measured command records match their complete source vectors and stdout/stderr hashes; all eight frozen control files match. Only known generated Ruff cache files are extra in the native workspace. Native products (45 files, including the complete 41-file OCI layout) were exported and rehashed; each OCI SHA-256 blob name matches its bytes. See `verification-run/final-subject-reverification.json`, `verification-run/final-native-state.json`, `verification-run/native-artifacts/manifest.json` and the root artifact inventory.

Current combined patch: `verification-run/communication-1167.patch`. Separate patches: `verification-run/issue-1167-tests.patch` and `verification-run/copyright-checker-paths.patch`. The source and native provenance remain understandable independently of Fabro.

The mobile UI uses the current Wi-Fi address `http://172.18.17.0:43916`; the run is `http://172.18.17.0:43916/runs/01M485DJP96AGJYWA02WE41KQA`. Its old-address redirect was corrected only after all 28 dedicated-server runs were confirmed terminal. Existing private credentials and the other optimization session's server were preserved. Login credentials remain in the internal private state directory and are not exported with the contribution.
