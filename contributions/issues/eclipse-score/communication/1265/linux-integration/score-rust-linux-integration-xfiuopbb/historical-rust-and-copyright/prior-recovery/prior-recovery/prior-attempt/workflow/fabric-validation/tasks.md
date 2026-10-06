# Tasks: S-CORE Rust issue workflow

Input: [spec](spec.md), [plan](plan.md). Bounded maintenance in active increment 011.

- [x] RW-T01 [US1] Inspect pinned native Rust/process sources and #1265; record source
  receipts in `source-receipts.json` (RW-002–005).
- [x] RW-T02 [US1] Author `.agents/skills/score-rust-workflow/SKILL.md`, native verification
  and issue-specific references and `agents/openai.yaml`; expose local discovery without overwriting skills
  (RW-001–004/007).
- [x] RW-T03 [US2] Author dependency/macro reference, #1265 guide and offline report
  template under `.agents/skills/score-rust-workflow/` (RW-005–006).
- [x] RW-T04 Validate structure, source/reference bindings, issue acceptance mapping,
  preserved subjects and foundation/package checks; record `validation.json` and
  `acceptance.md` (RW-001–007).

Dependencies: RW-T01 → RW-T02 → RW-T03 → RW-T04. These are authoring/validation tasks.
Engineering qualification and acceptance belong to later authorized issue work and humans;
this task list cannot record their completion.
