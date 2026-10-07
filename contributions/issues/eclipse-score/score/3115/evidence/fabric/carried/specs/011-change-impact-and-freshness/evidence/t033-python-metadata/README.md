# Public Python metadata preparation

See [findings](review-report.md), [results](metadata-results.json),
[prepared metadata](metadata-manifest.json) and
[actual consumed input](consumed-metadata-manifest.json). The original 67-package
metadata failure is cleared; the newly prepared 68-package mirror needs a fresh
native retry. QNX and an unlisted registry download are refused by real native probes.

Validation and historical preservation are recorded in `validation-results.json`,
`preservation-current.json` and `manifest.json`. Keep the sealed packet unchanged.
Native source/locks and prior engineering decisions are preserved. Successful
metadata preparation does not imply native build/test or engineering acceptance.
