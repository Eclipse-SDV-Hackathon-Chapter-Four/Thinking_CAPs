# Improvement

> [!IMPORTANT]
> Submit this pull request as **Draft** until it is ready for committer review.

## Description

Exposes the proxy event subscription state to the Rust COM-API:

- `get_subscription_state()`, `set_subscription_state_change_handler()` and
  `unset_subscription_state_change_handler()`, backed by new LoLa FFI entry points;
- the mock runtime implementation, design notes and user-facing API examples;
- the `subscription_state_apis` test application with scripted provider/consumer integration tests.

## Related ticket

Addresses #560 (improvement ticket)

## Validation

Linux x86_64, Bazel 8.7.0, baseline `381d43de` — five selected groups pass, 14 actual
cases pass (five real LoLa integration scenarios plus scripted helper-cleanup tests).

- Clippy: exit 0 with 2 warnings (unread `Observation.invocation`, `manual_is_multiple_of`).
- Not run: QNX, Clippy on test code, clang-tidy/CodeQL, sanitizers.

## Notes for reviewers

- Engineering applicability, native trace, qualification and human acceptance pending.
- Two Clippy warnings retained.

## Readiness follow-up — 2026-10-07

The follow-up removes the redundant per-observation counter, retains the atomic counters used by assertions and replaces the parity expression with `is_multiple_of(2)`.

The earlier validation above binds the original proposal. Supplemental warning
corrections and fresh measurements are supplied in the local readiness packet;
use its final candidate/source hashes for review. Scope/API/ABI, full applicable CI,
qualification and contributor ECA/IP acceptance remain open.

Final review artifacts: [merge requirements](../rust-api-queue/readiness-review-20261007/MERGE-ARTIFACTS.md), [current PR draft](../rust-api-queue/readiness-review-20261007/pr-drafts/560.md) and [source-bound verification](../rust-api-queue/readiness-review-20261007/verification.json).
