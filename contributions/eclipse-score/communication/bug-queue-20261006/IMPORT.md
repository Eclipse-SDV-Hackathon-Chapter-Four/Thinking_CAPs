# Imported communication bug queue

Imported from the original `eclipse_sdv_hackathon_2026` contribution destination.
Read the original [queue README](README.md), then the latest captured
[recovery handoff](recovery-1/RESUME.md) and
[diagnosis](recovery-1/offline-followup/DIAGNOSIS-20261007.md).
All selected original source, control, license, patch, generated-product, log,
failed-attempt and review bytes are retained. These are historical measurements;
this import reruns no native checks and grants no engineering acceptance.
Original run restrictions and exhausted budgets remain unchanged. No native
upstream PR, merge, paid call, source repair or issue closure occurs in this import.

| Issue | Imported disposition |
| --- | --- |
| #1236 | Draft CI enforcement patch; 27 baseline-identical buildifier findings remain |
| #1031 | Draft AoU visibility/traceability patch; native scoped checks retained; production Config Management/FMEA integration pending |
| #751 | Latest additional correction retained: 502 passing tests, 6 skips; copyright, full candidate query-analysis, QNX and coverage remain open |
| #1104 | Draft normalizer and later exact-scope root-cause findings retained; missing locations are hidden rather than restored; full analysis/review pending |

## Large archives and verification

Six original archive paths exceed 80 MiB. Their exact bytes are stored as five
shared, SHA-256-addressed blobs, in 48 MiB parts under `large-artifacts/`.
Adjacent `<archive>.parts.json` records replace the oversized files in this
Git layout. No archived evidence is omitted or rewritten. Original nested
manifests still name the original archive paths; verify their bytes through
[import-source-inventory.json](import-source-inventory.json), or restore a
separate copy before using the original packet's tools.

From the Thinking_CAPs root:

```bash
python3 contributions/shared/scripts/verify_missing_contributions.py
python3 contributions/shared/scripts/verify_missing_contributions.py --restore-to /path/to/empty/queue-copy
```

The default verifier performs no extraction or execution. Restoration recreates
all original selected files, including the large archives, and checks their
original hashes; it requires an empty, separate destination. Captured scripts
and build commands remain read-only evidence until separately admitted.

The import records exclude generated Python caches and never follow symlinks.
[import-artifact-manifest.json](import-artifact-manifest.json) seals the stored
layout. Earlier source manifests, failed logs and later recovery records remain
individually visible; their chronology must be respected.
