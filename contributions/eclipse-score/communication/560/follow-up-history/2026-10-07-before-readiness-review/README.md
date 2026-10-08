# Communication #560 — Improvement: Add Subscription State Change APIs Support on Rust API Lib

Exposes proxy event subscription state and change handlers in the Rust COM-API.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/560 |
| Upstream status | open, observed 2026-10-07 (updated 2026-06-18, 0 comments) |
| Local status | `proposed_fix_linux_verified` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | `feature/560-subscription-state-apis` |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Linux x86_64, Bazel 8.7.0, baseline `381d43de` — five selected groups pass, 14 actual
cases pass (five real LoLa integration scenarios plus scripted helper-cleanup tests).

- Clippy: exit 0 with 2 warnings (unread `Observation.invocation`, `manual_is_multiple_of`).
- Not run: QNX, Clippy on test code, clang-tidy/CodeQL, sanitizers.

## Branch and PR

| Field | Value |
| --- | --- |
| Branch | `feature/560-subscription-state-apis` at `290fea70b512` in `/home/jefferson/eclipse-score/communication` |
| Base | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (evidence baseline) |
| Patch (`git am`-ready) | [`communication-560.patch`](communication-560.patch) |
| Portable branch | [`feature-560-subscription-state-apis.bundle`](feature-560-subscription-state-apis.bundle) |
| PR title / body | [`pr-title.txt`](pr-title.txt) / [`pr-description.md`](pr-description.md) |

Branch is based on the verified baseline `381d43de`. It merges into upstream `main` (`e073dede`, 2026-10-06) without textual conflicts; the merged result has not been built or tested.

To open the PR from your fork (nothing has been pushed):

```bash
cd /home/jefferson/eclipse-score/communication
git remote add fork git@github.com:<your-user>/communication.git   # once
git rebase origin/main feature/560-subscription-state-apis        # optional; re-run the checks if you rebase
git push fork feature/560-subscription-state-apis
gh pr create -R eclipse-score/communication --draft --head <your-user>:feature/560-subscription-state-apis \
  --title "$(cat /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/560/pr-title.txt)" --body-file /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/560/pr-description.md
```

Elsewhere, recreate the branch from the bundle:
`git fetch /home/jefferson/Thinking_CAPs/contributions/eclipse-score/communication/560/feature-560-subscription-state-apis.bundle feature/560-subscription-state-apis:feature/560-subscription-state-apis` (the clone must contain `381d43dec900`).

## Open items

- Engineering applicability, native trace, qualification and human acceptance pending.
- Two Clippy warnings retained.

## Notes

- Original 3/3 corrections plus a separately authorized Codex correction (1/3 of that allowance used, 560 only).
- Conflicts with #250 and #1261 branches (`score_com.rs`, `consumer.rs`) and with the #490 draft (mock runtime).

## Evidence

- Codex correction and verification: [`evidence/score-rust-560-codex-eppa905r-results/README.md`](evidence/score-rust-560-codex-eppa905r-results/README.md)
- Final Codex supervisor review: [`evidence/score-rust-560-codex-eppa905r-results/reports/codex-supervisor-final.md`](evidence/score-rust-560-codex-eppa905r-results/reports/codex-supervisor-final.md)
- Verification summary: [`evidence/score-rust-560-codex-eppa905r-results/verification-summary.json`](evidence/score-rust-560-codex-eppa905r-results/verification-summary.json)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
