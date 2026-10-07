# Native assurance harness MVP — S-CORE #2850

Latest license follow-up: [audit and raw evidence](../integration-20261007/license-audit/README.md). The current patch contains 191 files: the 185 runtime-measured implementation files are unchanged, and six inherited native files received license comments. The pinned checker passes all 164 supported native files and 15 packet scripts. The 274-case runtime evidence below predates that comment-only follow-up; no runtime tests were rerun. Original headerless collector bytes, previous patch/bindings and all failed checks are retained.

The native implementation covers every MVP acceptance criterion in issue #2850.
It is a reviewable patch for docs-as-code draft #628 at
`4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9`, with 191 changed/added native files,
including the 40 scenario directories. The draft dependency is unmerged.

Measured locally: all 11 native test targets / 274 cases passed with no skips;
the full native build/test and documentation check passed; baseline and scoped
candidate each passed 30 search, 10 held-out and four active native seed tasks.
The fourth seed uses an actual Sphinx build. Changed-code lint, format and strict
typing, copyright and workflow checks passed. Pristine patch application and
fixed-contract hashes were verified.

**Engineering merge readiness is pending.** The native IDE-based whole-project
type check retains 28 warnings, all in unchanged baseline files (the pristine
baseline has 101). Changed Python files have zero errors/warnings. No suppression,
gate/schema/metric-calculation change, dependency upgrade or invented native ID
was used to conceal these findings. Native ECA/DCO, requirements/design/qualification
applicability, code-owner review, draft integration and hosted CI remain pending.

- [Patch](patches/0001-score-2850-assurance-harness.patch) and [native candidate tree](candidate/)
- [Acceptance mapping and engineering review](review-packet.md)
- [Verification report](verification.md), [raw check index](evidence/check-index.json), [native JUnit summary](evidence/junit-summary.json)
- [Trace store](evidence/runs/evolution_summary.jsonl), [native seeds](evidence/native-seeds/evolution_summary.jsonl), [typing comparison](evidence/typing-comparison.json)
- [Native PR description](pr-description.md), [impact analysis](impact-analysis.md), [improvement-request draft](improvement-request.md), [merge checklist](merge-checklist.md)
- [Reproduce](reproduce.md), [source binding](evidence/source/binding.json), [patch proof](evidence/patch-application.json), [integrity manifest](manifest.json)

The snapshot executor is model-free and labelled in every score; it does not
measure agent quality or approve assurance arguments. The separate upstream
Phase 2 security comment explicitly describes post-MVP work. Historical chatbot
and preliminary adapter evidence remain separately labelled in the parent packet.
