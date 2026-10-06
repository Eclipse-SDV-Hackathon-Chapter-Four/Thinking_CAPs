# Waiting for loop27 restoration

The operator explicitly reconfirmed `/dev/loop27`. The original image remains mounted as `/dev/loop1`; stable storage validation refuses the changed device-number binding. Administrator authentication is needed to restore literal loop27. The prepared `review-correction/restore-loop27.py` passed read-only preflight, but sudo refused its invocation because a password is required. No mount, storage record, queue or source candidate was changed.

`review-correction/coverage-correction.patch` remains unapplied. Patch applicability passes; no format, build or runtime checks have run for this proposed correction. After authenticated restoration, validate the original stable binding, then use a fresh bound workspace and an isolated corrected candidate for zero-model native verification.

Historical original-source results remain preserved: 503 passed, 6 skipped; copyright has 204 reproduced baseline findings. The three-attempt supervisor stays closed. No paid call occurred and no new run was created. Engineering acceptance and publication remain pending.
