# Communication #173 — Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate)

Assessment of external crates in COM-API (refresh); no source change proposed.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/173 |
| Upstream status | open, observed 2026-10-07 (updated 2026-07-27, 1 comments) |
| Local status | `assessment_refreshed_no_source_change` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | none — no source change to merge |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Assessment only; the exported patch is empty. The refresh measured 39 passing child cases and 2
ignored doctests, and found the published macro source byte-identical. `paste` was already replaced by
`pastey` upstream (#1268, in the baseline); the maintainer points to score-crates#42 for pastey's
supporting artifacts.

## Open items

- Tool qualification, dependency closure, advisories and adoption decisions pending.
- One original correction slot remains; no defect justifies using it.

## Evidence

- Assessment refresh: [`evidence/score-rust-resumed-67y5042v-results/runtime/supervisor-final.md`](evidence/score-rust-resumed-67y5042v-results/runtime/supervisor-final.md)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
