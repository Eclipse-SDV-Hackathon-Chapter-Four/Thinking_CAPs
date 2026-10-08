# Prepared draft — human review required

# Improvement

> [!IMPORTANT]
> Submit this pull request as **Draft** until it is ready for committer review.

## Description

Replaces the panic for `FindServiceSpecifier::Any` with typed, same-interface Any discovery.

- Interfaces register their LoLa wildcard configuration; `find_service` and the async discovery path
  resolve `Any` through native find-any (`find_service_any` / `start_find_service_any` FFI).
- Unmapped, concrete or malformed registrations return `ServiceNotFound`.
- The async stop guard is created synchronously after a successful start, so a never-polled or
  cancelled future stops the native search.
- Adds LoLa unit tests and the `consumer_any_apis` ITF integration test.

This is typed same-interface discovery, not discovery of all interfaces (see #1261).

## Related ticket

Addresses #250 (improvement ticket)

## Validation

Linux x86_64, Bazel 8.7.0, baseline `381d43de` — six selected groups pass, 68 child
cases pass, 2 doctests ignored:

- ITF `test_com_api_any` and `test_com_api_any_no_offer` (2); LoLa unit tests (9, incl. 3 new Any cases);
  `runtime_test` (17), concept (9) and macro (8) units; existing sync (3), async (3) and C++
  `test_find_any_semantics` (1) integration; GCC 15 macro doctest (16 pass, 2 ignored).
- Clippy on five libraries: exit 0, 5 SARIF reports with 4 warnings.
- Not run: QNX, Clippy on test code, clang-tidy/CodeQL, sanitizers.

## Notes for reviewers

- Async discovery is one-shot and returns the latest stored snapshot; native suppresses the initial empty notification, so an async request with no offers stays pending until an offer arrives.
- Scope is typed same-interface Any, not system-wide discovery; the issue thread (maintainer + #1261 author) expects 'all services on system' — align with #1261.
- Find-service callback reclamation (baseline-wide), API/ABI disposition, native trace, qualification and acceptance pending.


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)
- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
