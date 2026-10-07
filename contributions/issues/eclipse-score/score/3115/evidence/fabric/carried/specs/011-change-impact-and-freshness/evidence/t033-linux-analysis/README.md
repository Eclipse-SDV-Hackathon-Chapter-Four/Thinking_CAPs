# Pinned Linux analysis after metadata preparation

See [findings](review-report.md), [native results](analysis-results.json),
[consumed metadata](consumed-metadata-manifest.json) and
[remaining public module inputs](module-cache-inputs.json).

All four native probes consume all 68 captured public metadata pages without misses.
Linux analysis remains failed. The final probe refuses the exact pinned public Rust
module archive; its archive and module-version patch are absent from the retained cache.
QNX remains skipped, with external downloads blocked and no SDK bytes acquired.

Validation, preservation, process closure and the complete file hashes accompany this
packet. Keep sealed evidence unchanged. Metadata loading does not imply compilation,
test success, scope acceptance or native engineering readiness.
