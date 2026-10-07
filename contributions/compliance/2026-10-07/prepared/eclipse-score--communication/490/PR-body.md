# Prepared draft — human review required

# Improvement

> [!IMPORTANT]
> Submit this pull request as **Draft** until it is ready for committer review.

> [!CAUTION]
> Draft: not ready for committer review.

## Description

Draft only — not ready for review.

Adds an in-process mock runtime (registry-backed `find_service`, publisher and subscription) so Rust
COM-API applications can be tested without LoLa, plus design notes.

## Related ticket

Addresses #490 (improvement ticket)

## Validation

Unverified. The test group failed while loading a Bazel module extension (`rules_python` pip)
before any test ran; lint groups failed because of the operator launcher defect. No supervisor
report was produced.

## Notes for reviewers

- Needs a successful build and tests; correction budget 3/3 exhausted.
- Overlaps the #560 branch's mock runtime changes (conflict in `com-api-runtime-mock/runtime.rs`).


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)
- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
