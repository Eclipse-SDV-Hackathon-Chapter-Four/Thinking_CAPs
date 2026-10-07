# Bats source inputs and configured Linux dependency findings

See [findings](review-report.md), [native results](bats-results.json),
[Bats inputs](bats-inputs.json), [completed repositories](materialized-dependencies.json),
[Buf toolchain inputs](buf-toolchain-readiness.json) and
[the next cache-only stage draft](buf-cache-stage-draft.json).

All four Bats archives match native source pins. Two Bats core aliases and the
previously incomplete Kotlin repository have completed native markers. Configured
Linux analysis remains failed; the last probe refuses the pinned Linux Buf executable.
All three selected Buf executables are available in the existing cache and match
the original-lock-bound checksum list, but remain unimported and unexecuted here.

The first mirror uses host Python 3.10 and retains an interrupted-response traceback.
Subsequent probes use a copied, hash-bound Python 3.12.14 runtime and record response
write completion explicitly. Keep failed, unknown and completed results separate.
Validation, historical preservation, process closure and hashes accompany this packet.
