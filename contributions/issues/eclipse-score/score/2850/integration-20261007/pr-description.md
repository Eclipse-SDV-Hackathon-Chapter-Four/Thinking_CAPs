## 📌 Description

Implements the MVP acceptance criteria of eclipse-score/score#2850 in the native
assurance harness. Adds a bounded, deterministic AssuranceHarness context candidate,
executable CR-001–005 checks and reusable goal/solution/breakdown checks, 30 public
search scenarios and 10 separate held-out scenarios, native schema/metrics/gate replay,
complete traces with diffs and provenance, and model-free Lane A CI for baseline and
candidate. Context preserves source IDs and metadata and treats document text as inert.

Stacked follow-up to docs-as-code draft #628, targeting its `harness` branch at
4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9. Extends the existing `score_harness`
contract and preserves its active seed tasks and loader. #628 must be
integrated before this work moves to main, followed by rebase and fresh verification.
At the recorded observation, #628 is unmerged and its API reports mergeable=false.
The fixed gate, metrics implementation, evidence schema and native tool/dependency pins are unchanged.

The executor replays public synthetic before/after snapshots. Results establish fixture
correctness and reproducibility; they do not measure agent quality or approve an
ISO 26262/ASPICE assurance argument. The separate Phase 2 security proposal is post-MVP.

Related ticket: https://github.com/eclipse-score/score/issues/2850

Verification: see the attached native review packet, raw logs, JUnit reports, baseline
and candidate traces, source/config/patch hashes and reproduction instructions.
Implementation and packet prepared with Codex; author and code-owner review are pending.
The patch also supplies native-required Apache-2.0 headers for six preexisting
helper/config/package files. The original 185 implementation files remain byte-identical
to the runtime-tested patch; current copyright checks pass all 164 supported native
files. Native runtime evidence predates those six comment-only fixes and was not rerun.
Shell/Python syntax, exact insertion, whitespace and clean patch replay were checked.
Whole-project typing still reports 28 inherited warnings; changed-code checks pass.
No main-revision test result, upstream design acceptance or sign-off is claimed.

## 🚨 Impact Analysis

The native gate contract and requirement-status/ID validation are preserved. New impact
checks only identify review obligations. Existing tool requirements cover IDs, status,
test/code links and standard requirement types; acceptance of the broader change-impact
automation and qualification applicability remains a maintainer decision. See
`impact-analysis.md` for exact native IDs and dispositions.

- [ ] This change does not violate any tool requirements and is covered by existing tool requirements
- [ ] This change does not violate any design decisions
- [ ] Otherwise I have created a ticket for new tool qualification

These boxes require the actual applicability/acceptance decision; none is fabricated.
Keep this PR draft until the improvement-request/dependency/qualification route is agreed.

## ✅ Checklist

- [x] Added/updated documentation for new or changed features
- [x] Added/updated tests to cover the changes
- [x] Followed project coding standards and guidelines

Contributor must confirm ECA, sign actual commits under DCO, obtain native code-owner
review and verify hosted CI. See `merge-checklist.md` for every pending obligation.
