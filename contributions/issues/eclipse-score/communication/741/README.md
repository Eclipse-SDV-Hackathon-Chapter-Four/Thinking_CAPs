# Communication #741 — Improvement: Move the Rust Sample example app from com/example to tutorial folder

Move the Rust example app to the tutorial — not implemented.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/741 |
| Upstream status | open, observed 2026-10-07 (updated 2026-07-22, 0 comments) |
| Local status | `not_implemented` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | none — the preserved probe does not address the issue |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Not implemented. The agent's file tools could not rename or delete, so it produced only an 852-byte
comment-only boundary probe; every query check failed with `no such package
'score/mw/com/doc/tutorial/com-api-example/com-api-gen'`. The probe is preserved as evidence but no
branch was created, because it does not address the issue.

## Open items

- The relocation itself is straightforward but still to be done (needs move/delete capability and BUILD updates).

## Evidence

- Queue run evidence: [`evidence/queue-run-ycbvxir7-issue-741/collection-summary.json`](evidence/queue-run-ycbvxir7-issue-741/collection-summary.json)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
