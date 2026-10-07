# Prepared draft — human review required

# Improvement

> [!IMPORTANT]
> Submit this pull request as **Draft** until it is ready for committer review.

> [!CAUTION]
> Draft: not ready for committer review.

## Description

Draft only — not ready for review.

Adds a `MethodInArgPtr<T>` plumbing type for Rust method in-arguments and a C++/Rust size-check test
support library. ABI layout and ownership semantics are not yet settled.

## Related ticket

Addresses #781 (improvement ticket)

## Validation

Linux x86_64, baseline `381d43de`: selected tests passed. The original lint groups failed because
of an operator launcher defect (duplicate `clippy_strict` aspect), not the source. A later run with
the corrected launcher on the identical source: Clippy exit 0; the doctest target ran but contains
zero runnable examples.

## Notes for reviewers

- ABI layout and ownership semantics unresolved (supervisor: not a completed issue fix).
- Behavioral coverage is minimal; correction budget 3/3 exhausted.


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)
- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
