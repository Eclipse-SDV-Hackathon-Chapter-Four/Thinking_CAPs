# Communication #1261 — Improvement: Provide an async stream of newly available services

Adds `Runtime::find_all_services()`, an async stream of interface-independent service descriptors for the LoLa backend.

| Field | Record |
| --- | --- |
| Upstream issue | https://github.com/eclipse-score/communication/issues/1261 |
| Upstream status | open, observed 2026-10-07 (updated 2026-10-03, 0 comments) |
| Local status | `proposed_fix_linux_verified` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Branch | `feature/1261-async-service-stream` |
| Upstream PR / merge | not submitted |
| Engineering acceptance | pending offline (tests and agent reviews do not imply acceptance) |

## Result

Linux x86_64, Bazel 8.7.0, baseline `381d43de`:

- `//score/mw/com/impl:runtime_test` (17), `//score/mw/com/impl/configuration:configuration_test` (30),
  `com-api-runtime-lola-tests` (16 incl. 10 stream tests), `score_com_concept-test` (10),
  `score_com_concept-macros-unit-tests` (8): pass.
- ITF: `test_com_api_sync` (3), `test_com_api_async` (3), `test_find_any_semantics` (1) and the new
  `test_com_api_all_services_stream` (initial offer, later offer of a second interface, withdrawal
  with probe-confirmed boundary, exactly one re-offer item; exact identities): pass.
- `score_com_concept-macros-tests` (GCC 15 doctest): 16 pass, 2 ignored.
- Clippy on five libraries: exit 0, 4 warnings (3 on existing lines; 1 new:
  `service_stream.rs:234` transmute without annotations, same pattern as `consumer.rs:950`).
- Not run: QNX, Clippy on test code, clang-tidy/CodeQL, sanitizers.

## Branch and PR

| Field | Value |
| --- | --- |
| Branch | `feature/1261-async-service-stream` at `4760fe47f2ed` in `/home/jefferson/eclipse-score/communication` |
| Base | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (evidence baseline) |
| Patch (`git am`-ready) | [`communication-1261.patch`](communication-1261.patch) |
| Portable branch | [`feature-1261-async-service-stream.bundle`](feature-1261-async-service-stream.bundle) |
| PR title / body | [`pr-title.txt`](pr-title.txt) / [`pr-description.md`](pr-description.md) |

Branch is based on the verified baseline `381d43de`. It merges into upstream `main` (`e073dede`, 2026-10-06) without textual conflicts; the merged result has not been built or tested.

To open the PR from your fork (nothing has been pushed):

```bash
cd /home/jefferson/eclipse-score/communication
git remote add fork git@github.com:<your-user>/communication.git   # once
git rebase origin/main feature/1261-async-service-stream        # optional; re-run the checks if you rebase
git push fork feature/1261-async-service-stream
gh pr create -R eclipse-score/communication --draft --head <your-user>:feature/1261-async-service-stream \
  --title "$(cat /home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/1261/pr-title.txt)" --body-file /home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/1261/pr-description.md
```

Elsewhere, recreate the branch from the bundle:
`git fetch /home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/communication/1261/feature-1261-async-service-stream.bundle feature/1261-async-service-stream:feature/1261-async-service-stream` (the clone must contain `381d43dec900`).

## Open items

- Scope: configured services only vs. 'system-wide' (D1) — question drafted for #1261, not posted.
- Operational-phase heap allocation in discovery callbacks (D6) — question drafted for #1261, not posted.
- Find-service callback boxes are not reclaimed (baseline `dispose` is empty) — separate issue drafted, not posted.
- Adding an `IRuntime` virtual is not binary compatible for prebuilt implementers (method appended last).
- `InstanceIdentifier::Create` also mutates the configuration outside the discovery mutex (baseline path).
- New Clippy warning at `service_stream.rs:234`; QNX, sanitizers, native trace, qualification and acceptance pending.

## Notes

- User decisions recorded 2026-10-07: D2 (coalescing), D3 (track separately), D4 (append virtual), D5 (lock + invalidate) accepted; D1 and D6 await maintainers.
- Conflicts with the #250 branch (FFI bridge files, `score_com.rs`) and the #560 branch (`score_com.rs`); rebase whichever merges later.
- Drafts for the #1261 comment and the D3 issue: `evidence/score-rust-1261-decision-record-20261007/`.

## Evidence

- Final correction and measurements: [`evidence/score-rust-1261-claude-correction-3286o52w-results/review.md`](evidence/score-rust-1261-claude-correction-3286o52w-results/review.md)
- Independent review of the failed candidate: [`evidence/score-rust-claude-independent-review-20261007/review.md`](evidence/score-rust-claude-independent-review-20261007/review.md)
- Decision record and GitHub drafts: [`evidence/score-rust-1261-decision-record-20261007/README.md`](evidence/score-rust-1261-decision-record-20261007/README.md)
- Failed DeepSeek candidate (preserved): [`evidence/score-rust-stream-final-hdmk9onj-results/README.md`](evidence/score-rust-stream-final-hdmk9onj-results/README.md)
- Every sealed packet is copied under `evidence/` with its original `artifact-manifest.json`.
  Raw Fabro event streams are stored as `events.jsonl.zst`; [`compressed-evidence.json`](compressed-evidence.json)
  records each original SHA-256 (`zstd -dc <file> | sha256sum`).
- Queue-wide records (queue definition, launch, all-issue review, #1265 run):
  [`../rust-api-queue/`](../rust-api-queue/README.md).
- [`provenance.json`](provenance.json) maps each copy to its sealed source and manifest digest;
  [`artifact-manifest.json`](artifact-manifest.json) seals this folder.

Agents drafted the code (DeepSeek V4 Flash via Fabro, with Codex/Claude corrections where noted);
deterministic tools measured it. No GitHub comment, push, PR or issue change was made.
