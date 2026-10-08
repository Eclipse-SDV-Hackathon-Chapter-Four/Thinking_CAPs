# Corrected candidate verified and exported

Fabro run `01M485DJP96AGJYWA02WE41KQA` is terminal and exported. It used stable pre-optimization fabric `b2aa9a7a49a054621f38e59f3aef6d6e5daf3cce` and the same registered build image, now attached through `/dev/loop1`. The new workspace passed native storage admission/validation; old loop27 bindings remain unchanged.

The coverage correction is applied only in `review-correction/verification-run/candidate/`. All five mandatory checks were measured fresh: formatting, focused integration/schema tests (2/2), full build and full suite pass (503 passed, 0 failed, 6 skipped). Copyright fails with exactly the same 204 normalized baseline-with-path-overlay findings; none are added. No QNX execution is claimed.

Patch, complete source, raw evidence, executable, datatype libraries, filesystem layer and complete OCI test image are exported in `review-correction/verification-run/`. All source, control, measured-log and native-product hashes were reverified. Offline review is `review-correction/OFFLINE-REVIEW.md`; local PR text is `PR-DRAFT.md`.

The workflow has only verification/export command nodes and zero model calls. The original three-attempt supervisor remains closed, with original budget/usage limitations retained. No upstream submission, merge, issue closure, ECA verification or engineering acceptance is recorded.

Mobile UI: http://172.18.17.0:43916/runs/01M485DJP96AGJYWA02WE41KQA (same Wi-Fi). Private login credentials remain internal.
