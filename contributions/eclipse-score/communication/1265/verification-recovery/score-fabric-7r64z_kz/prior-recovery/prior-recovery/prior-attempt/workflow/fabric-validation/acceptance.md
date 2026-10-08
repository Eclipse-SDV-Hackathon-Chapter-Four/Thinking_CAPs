# Rust workflow delivery record

Date: 2026-10-05. Scope: generic S-CORE Rust issue procedure, not a native issue fix.

The repository-owned [skill](../../../.agents/skills/score-rust-workflow/SKILL.md) provides
task/source/storage binding, issue-specific planning, implementation, native verification
and a portable offline report. References load by change surface. Dependency assessment
and [#1265](../../../.agents/skills/score-rust-workflow/references/communication-1265.md)
are conditional, so unrelated defects do not inherit macro-assessment work.
Local Codex discovery uses `/home/jefferson/.codex/skills/score-rust-workflow`, a symlink
to the repository skill. Discovery in an already-running session may require refresh;
the entrypoint can also be read directly. No existing skill was overwritten.

## Agent walkthrough (not native verification evidence)

| Scenario | Route and review finding |
| --- | --- |
| Ordinary Rust behavior defect in another S-CORE module | Bind native requirements, reproduce, patch and run selected regressions; dependency/example references remain conditional |
| Unsafe FFI or concurrency defect | Bind invariants/callers/native integration obligations; supported dynamic checks and unavailable capabilities remain distinct |
| #1265 dependency assessment | Actual source already uses `pastey`; determine remaining assessment obligations, preserve unresolved crate version/features, compare options and verify generated API only in authorized issue work |
| Missing QNX/compiler/checker or manual doctest exclusion | Include it in expected checks, preserve omission/failure and pending acceptance; do not claim complete platform verification |

All four #1265 acceptance areas map to concrete evidence/output purposes in its guide.
Native tool-management definitions/attributes come from the existing process pin;
communication observations are supplementary source discovery, not updated source locks.
The same common report accepts patch-based and assessment-only outcomes.

## Deterministic delivery checks

[Validation](validation.json) records actual command outcomes, source/reference/discovery
checks, preserved subjects and final delivered-file digests. [Source receipts](source-receipts.json)
bind 18 retrieved source/issue records to raw bytes on the selected external Linux build
volume. Failed guessed-path discovery is retained there; no native command was run.
Skill validation, pinned Spec Kit 1.0.12 prerequisites, foundation consistency and
package building passed. The first foundation attempt ran before `validation.json`
existed and failed on that link; the corrected rerun passed, with both outcomes retained.

No Python/Rust implementation changed. No native Rust build/test, compiler qualification,
runtime admission, paid provider call, issue closure or upstream write is claimed.
Existing optimization skill mapping and C++ profiles stay unchanged; adding this skill
does not establish a supported Fabro Rust profile or native engineering readiness.
Human-owned review items remain untouched. Workflow delivery is separate from native
qualification, issue-specific expected-check selection and offline engineering acceptance.

## Invocation

```text
Use $score-rust-workflow to solve <S-CORE repository and Rust issue URL>.
Follow the repository's native requirements and build configuration. Work in a
storage-bound disposable copy and deliver the scoped patch or assessment with
verification evidence and an offline review packet.
```
