# Corrected candidate verification running

Fabro run `01M485DJP96AGJYWA02WE41KQA` is running the five mandatory native checks in a fresh disposable workspace bound to the original registered image, now `/dev/loop1`. SSD UUID, image UUID, backing file, stable fabric pin and all 2,885 original candidate source hashes were verified. The operator clarified that loop1 is the former loop27 volume. Old bindings, source and evidence are preserved unchanged.

The coverage correction is applied only in `review-correction/verification-run/candidate/`. The pinned native formatter check passes for that source; fresh build/test measurements are pending. This workflow has only verification and export command nodes, no model/provider configuration, no human nodes, and zero paid calls. The exhausted three-attempt supervisor remains closed.

Current records are in `review-correction/verification-run/`. The historical original-source result was 503 passed, 6 skipped, with 204 reproduced baseline copyright findings. Those tests do not qualify the changed source. Engineering acceptance and publication remain pending.
