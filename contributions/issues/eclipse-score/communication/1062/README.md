# Communication #1062 — Improvement: E2E protection for Rust Method/Field APIs

E2E protection for Rust Method/Field APIs — design assessment only.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/1062 |
| Upstream status | open, observed 2026-10-07 (updated 2026-09-11, 3 comments) |
| Local status | `design_assessment_no_source_change` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | none — no source change to merge |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Design assessment only; no patch. A maintainer stated on 2026-09-11 that S-CORE cannot provide E2E
functionality directly based on the AUTOSAR specification because of licensing restrictions, and
that a C++ E2E protection API is being designed first.

## Open items

- Blocked on the upstream C++ E2E API design and licensing constraints.

## Evidence

- Supervisor review: [`evidence/queue-run-ycbvxir7-issue-1062/export/reports/supervisor.md`](evidence/queue-run-ycbvxir7-issue-1062/export/reports/supervisor.md)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
