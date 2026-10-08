# Communication #794 — Improvement: Remove bazel `tags = ["manual"]` from rust test targets

Remove `tags = ["manual"]` from Rust test targets — being handled upstream; no patch here.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/794 |
| Upstream status | open, observed 2026-10-07 (updated 2026-10-05, 1 comments) |
| Local status | `no_patch_upstream_in_progress` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | none — no source change to merge |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

No patch was produced. Upstream already handled most of this: PR #1267 (in the baseline) removed the
manual tag, and the maintainer's 2026-10-05 update reports three targets enabled (one skipped under
sanitizers) and the macro doctest still manual because `rust_doc_test` does not forward native
dependencies. A PR from here would duplicate maintainer work.

## Open items

- Remaining doctest tag depends on a `rust_doc_test` limitation (maintainer-owned).

## Evidence

- Supervisor review: [`evidence/queue-run-ycbvxir7-issue-794/export/reports/supervisor.md`](evidence/queue-run-ycbvxir7-issue-794/export/reports/supervisor.md)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
