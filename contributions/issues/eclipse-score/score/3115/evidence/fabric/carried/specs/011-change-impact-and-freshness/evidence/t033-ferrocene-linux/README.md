# US38 Linux Ferrocene evidence

[Complete offline review report](review-report.md).

`manifest.json` seals every packet file. Large exact payloads stay in the storage-bound
workspace and are referenced by SHA-256/bytes in `acquisition-results.json` and
`public-module-manifest.json`; inventories and license/notice bytes are retained here.
Native source, locks, historical packets and engineering acceptance remain unchanged.
