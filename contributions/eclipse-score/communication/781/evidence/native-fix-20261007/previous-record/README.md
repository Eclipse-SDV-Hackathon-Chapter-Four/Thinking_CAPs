# Communication #781 — Improvement: Implementation of MethodInArgPtr in rust side

Draft `MethodInArgPtr<T>` plumbing type with a LoLa size-check test support library.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/781 |
| Upstream status | open, observed 2026-10-07 (updated 2026-07-27, 0 comments) |
| Local status | `draft_patch_partially_verified` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | `draft/781-method-in-arg-ptr` |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Linux x86_64, baseline `381d43de`: selected tests passed. The original lint groups failed because
of an operator launcher defect (duplicate `clippy_strict` aspect), not the source. A later run with
the corrected launcher on the identical source: Clippy exit 0; the doctest target ran but contains
zero runnable examples.

## Branch and PR

| Field | Value |
| --- | --- |
| Branch | `draft/781-method-in-arg-ptr` at `494d7b78612a` in `/home/jefferson/eclipse-score/communication` |
| Base | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (evidence baseline) |
| Patch (`git am`-ready) | [`communication-781.patch`](communication-781.patch) |
| Portable branch | [`draft-781-method-in-arg-ptr.bundle`](draft-781-method-in-arg-ptr.bundle) |
| PR title / body | [`pr-title.txt`](pr-title.txt) / [`pr-description.md`](pr-description.md) |

Branch is based on the verified baseline `381d43de`. It merges into upstream `main` (`e073dede`, 2026-10-06) without textual conflicts; the merged result has not been built or tested.

To open the PR from your fork (nothing has been pushed):

```bash
cd /home/jefferson/eclipse-score/communication
git remote add fork git@github.com:<your-user>/communication.git   # once
git rebase origin/main draft/781-method-in-arg-ptr        # optional; re-run the checks if you rebase
git push fork draft/781-method-in-arg-ptr
gh pr create -R eclipse-score/communication --draft --head <your-user>:draft/781-method-in-arg-ptr \
  --title "$(cat /home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/781/pr-title.txt)" --body-file /home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/781/pr-description.md
```

Elsewhere, recreate the branch from the bundle:
`git fetch /home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/781/draft-781-method-in-arg-ptr.bundle draft/781-method-in-arg-ptr:draft/781-method-in-arg-ptr` (the clone must contain `381d43dec900`).

## Open items

- ABI layout and ownership semantics unresolved (supervisor: not a completed issue fix).
- Behavioral coverage is minimal; correction budget 3/3 exhausted.

## Notes

- Keep as a draft PR or local branch until the ABI/ownership design is agreed upstream.

## Evidence

- Supervisor review: [`evidence/queue-run-ycbvxir7-issue-781/export/reports/supervisor.md`](evidence/queue-run-ycbvxir7-issue-781/export/reports/supervisor.md)
- Corrected-launcher Clippy/doctest re-run: [`evidence/score-rust-runtime-review-tf_tonek/README.md`](evidence/score-rust-runtime-review-tf_tonek/README.md)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
