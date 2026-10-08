# Communication #490 — Improvement: Mock Runtime implementation of Rust COM-API

Draft in-process mock runtime for testing Rust COM-API applications without LoLa.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/490 |
| Upstream status | open, observed 2026-10-07 (updated 2026-06-15, 0 comments) |
| Local status | `draft_patch_unverified` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | `draft/490-mock-runtime` |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Unverified. The test group failed while loading a Bazel module extension (`rules_python` pip)
before any test ran; lint groups failed because of the operator launcher defect. No supervisor
report was produced.

## Branch and PR

| Field | Value |
| --- | --- |
| Branch | `draft/490-mock-runtime` at `35c58aac1d57` in `/home/jefferson/eclipse-score/communication` |
| Base | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (evidence baseline) |
| Patch (`git am`-ready) | [`communication-490.patch`](communication-490.patch) |
| Portable branch | [`draft-490-mock-runtime.bundle`](draft-490-mock-runtime.bundle) |
| PR title / body | [`pr-title.txt`](pr-title.txt) / [`pr-description.md`](pr-description.md) |

Branch is based on the verified baseline `381d43de`. It merges into upstream `main` (`e073dede`, 2026-10-06) without textual conflicts; the merged result has not been built or tested.

To open the PR from your fork (nothing has been pushed):

```bash
cd /home/jefferson/eclipse-score/communication
git remote add fork git@github.com:<your-user>/communication.git   # once
git rebase origin/main draft/490-mock-runtime        # optional; re-run the checks if you rebase
git push fork draft/490-mock-runtime
gh pr create -R eclipse-score/communication --draft --head <your-user>:draft/490-mock-runtime \
  --title "$(cat /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/490/pr-title.txt)" --body-file /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/490/pr-description.md
```

Elsewhere, recreate the branch from the bundle:
`git fetch /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/490/draft-490-mock-runtime.bundle draft/490-mock-runtime:draft/490-mock-runtime` (the clone must contain `381d43dec900`).

## Open items

- Needs a successful build and tests; correction budget 3/3 exhausted.
- Overlaps the #560 branch's mock runtime changes (conflict in `com-api-runtime-mock/runtime.rs`).

## Notes

- Keep as a draft until verified.

## Evidence

- Queue run evidence: [`evidence/queue-run-ycbvxir7-issue-490/collection-summary.json`](evidence/queue-run-ycbvxir7-issue-490/collection-summary.json)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
