# Communication #250 — Improvement: COM-API FindServiceSpecifier::Any support

Replaces the `FindServiceSpecifier::Any` panic with typed, same-interface Any discovery over LoLa find-any.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/250 |
| Upstream status | open, observed 2026-10-07 (updated 2026-07-15, 2 comments) |
| Local status | `proposed_fix_linux_verified` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | `feature/250-find-service-any` |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Linux x86_64, Bazel 8.7.0, baseline `381d43de` — six selected groups pass, 68 child
cases pass, 2 doctests ignored:

- ITF `test_com_api_any` and `test_com_api_any_no_offer` (2); LoLa unit tests (9, incl. 3 new Any cases);
  `runtime_test` (17), concept (9) and macro (8) units; existing sync (3), async (3) and C++
  `test_find_any_semantics` (1) integration; GCC 15 macro doctest (16 pass, 2 ignored).
- Clippy on five libraries: exit 0, 5 SARIF reports with 4 warnings.
- Not run: QNX, Clippy on test code, clang-tidy/CodeQL, sanitizers.

## Branch and PR

| Field | Value |
| --- | --- |
| Branch | `feature/250-find-service-any` at `84075c096b83` in `/home/jefferson/eclipse-score/communication` |
| Base | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (evidence baseline) |
| Patch (`git am`-ready) | [`communication-250.patch`](communication-250.patch) |
| Portable branch | [`feature-250-find-service-any.bundle`](feature-250-find-service-any.bundle) |
| PR title / body | [`pr-title.txt`](pr-title.txt) / [`pr-description.md`](pr-description.md) |

Branch is based on the verified baseline `381d43de`. It merges into upstream `main` (`e073dede`, 2026-10-06) without textual conflicts; the merged result has not been built or tested.

To open the PR from your fork (nothing has been pushed):

```bash
cd /home/jefferson/eclipse-score/communication
git remote add fork git@github.com:<your-user>/communication.git   # once
git rebase origin/main feature/250-find-service-any        # optional; re-run the checks if you rebase
git push fork feature/250-find-service-any
gh pr create -R eclipse-score/communication --draft --head <your-user>:feature/250-find-service-any \
  --title "$(cat /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/250/pr-title.txt)" --body-file /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/250/pr-description.md
```

Elsewhere, recreate the branch from the bundle:
`git fetch /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/250/feature-250-find-service-any.bundle feature/250-find-service-any:feature/250-find-service-any` (the clone must contain `381d43dec900`).

## Open items

- Async discovery is one-shot and returns the latest stored snapshot; native suppresses the initial empty notification, so an async request with no offers stays pending until an offer arrives.
- Scope is typed same-interface Any, not system-wide discovery; the issue thread (maintainer + #1261 author) expects 'all services on system' — align with #1261.
- Find-service callback reclamation (baseline-wide), API/ABI disposition, native trace, qualification and acceptance pending.

## Notes

- Correction budget 3/3 exhausted; no further source changes were made.
- Conflicts with the #1261 branch (FFI bridge files, `score_com.rs`) and the #560 branch (`consumer.rs`, `score_com.rs`).

## Evidence

- Final proposal and independent review: [`evidence/score-rust-250-final-fcuqf3or-results/runtime/supervisor-final.md`](evidence/score-rust-250-final-fcuqf3or-results/runtime/supervisor-final.md)
- Final verification summary: [`evidence/score-rust-250-final-fcuqf3or-results/runtime/verification-summary.json`](evidence/score-rust-250-final-fcuqf3or-results/runtime/verification-summary.json)
- Earlier correction (preserved): [`evidence/score-rust-discovery-575c85n6-results/README.md`](evidence/score-rust-discovery-575c85n6-results/README.md)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
