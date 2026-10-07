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
