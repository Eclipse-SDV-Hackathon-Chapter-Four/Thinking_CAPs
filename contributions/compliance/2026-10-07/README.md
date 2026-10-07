# Eclipse contribution compliance follow-up

`main` was pulled with `--ff-only` at
`f14b78b8e0e90eb65abec0bdbd7abcd8b19bc474`. Corrections are prepared on
`fix/eclipse-contribution-compliance` in a separate worktree; the original dirty
checkout and historical evidence remain preserved.

Jefferson confirmed Eclipse username **jnascimento6p0**. Its official lookup
passes, and native S-CORE PR #3307's ECA status passes for `jnsagai@gmail.com`.
This agreement does not cover another contributor. Jefferson confirmed
**Anthropic Claude Opus 5.5** assistance for CDA #601 and diagnostics #40.

The [original audit](../../audits/2026-10-07-eclipse-compliance.html) is historical.
This packet records subsequent corrections and
[dispositions for all thirteen findings](finding-dispositions.json).

## Corrected locally

- Full Apache-2.0 terms replace the abbreviated root/ThreadX notices; `NOTICE`
  retains the existing team attribution. Source/configuration licence sidecars
  preserve source bytes. Spec Kit helpers retain GitHub's MIT notice; upstream
  vendor and legacy notices remain applicable. Individual ownership and historical
  AI-generation extent are still matters for the responsible contributors.
- [Contribution guidance](../../../CONTRIBUTING.md) documents identity, AI
  disclosures, review, native checks and IP dispositions.
- The registry now verifies all five historical diagnostics patches and the
  recovered CDA patch. Current published revisions have separate snapshots,
  payload hashes and native check/review records.
- Five Rust mail submission copies replace AI human coauthors with assistance
  trailers and use Jefferson Nascimento as human author. Their source diffs are
  byte-identical to the original patches. No new DCO certifications are supplied.
- Prepared PR bodies include AI disclosures. The known generated lifecycle macro
  has a scoped file disclosure separating AI generation logic from copied profile
  data. Its amendment changes comments only; old tests/approval remain bound to
  the original source, with fresh native verification/review pending.
- Current copies of CDA/diagnostics submission checklists replace the false
  “no AI attribution” criterion and show the actual ECA failure. Earlier branch
  versions remain available in their original Git revisions.
- The original OpenBSW transportRouter packet is restored from its branch.
  Fault-storage has a portable, exact-byte copy with a new outer file manifest.
  [Additional inventory](additional-inventory.json) distinguishes native patches,
  branch scaffolds, integration examples and plans.
- The [prework declaration](../../../prework/README.md) acknowledges September
  implementation/evidence. No organizer eligibility decision is implied.

## Prepared native submission drafts

Use each registry entry's `prepared_pr_draft` and `compliance_status` fields.
Original sealed PR bodies/patches are retained as evidence. Prepared copies are
local; published PRs, native commits and shared history have not been rewritten.

| Published PR | Submitted revision | Prepared disclosure | Remaining decision |
| --- | --- | --- | --- |
| [CDA #601](https://github.com/eclipse-opensovd/classic-diagnostic-adapter/pull/601) | `fb8079c` | [PR body](prepared/eclipse-opensovd--classic-diagnostic-adapter/543/PR-body.md) / [mail patch](prepared/eclipse-opensovd--classic-diagnostic-adapter/543/published-revision-with-disclosure.patch) | Actual author account/email/legal name; ECA still fails; native checks/review; publish disclosure |
| [Diagnostics #40](https://github.com/eclipse-score/inc_diagnostics/pull/40) | `4a5c470` | [PR body](prepared/eclipse-score--inc_diagnostics/16/PR-body.md) / [mail series](prepared/eclipse-score--inc_diagnostics/16/published-revision-with-disclosure.patch) | Actual author ECA and DCO for three commits; IP disposition; current native verification/review; publish disclosure |
| [S-CORE #3307](https://github.com/eclipse-score/score/pull/3307) | `dff3812` | [PR body](prepared/eclipse-score--score/3115/PR-body.md) / [mail patch](prepared/eclipse-score--score/3115/published-revision-with-disclosure.patch) | Draft remains proposed; author-name correction and truthful sign-off consistency; inherited docs failure; review/pilots/adoption; publish disclosure |

Native PR payloads differ from the older recovered CDA/diagnostics patches. The
prepared published-revision mail patches change only mail metadata; the verifier
compares every commit's source diff independently. Corrected legal identity and
truthful DCO certification for another author require that author's action.

## Outstanding gates

All 24 registered issues have explicit review/check/file-provenance dispositions.
Current `submission_candidate` flags are false; prior candidate flags are retained
as historical metadata. This does not erase scoped SOME/IP/lifecycle implementation
results or their earlier local owner decisions.

Large SOME/IP, communication #1261/#250/#560, diagnostics and OpenBSW contributions
are flagged for project committer assessment of net new IP and any required IP
Team review. No agent-generated approval is recorded. Native engineering gaps
remain explicit: unverified #490 tests, #781 ABI/ownership, #1261 warnings/scope,
the communication bug queue's lint/analyzer/production coverage questions,
compiler qualification/adoption, platform disposition and full upstream CI.
Some root critical changes also still need real peer-review evidence.

Before official merge, the responsible human/project must review the intended
revision, confirm file-generation extent and applicable notices, resolve required
native gates, and supply genuine legal/IP decisions. This packet supplies no human
review signature, DCO certification, IP approval or competition acceptance.

## Verification

```bash
python3 scripts/test_verify_contributions.py
python3 scripts/verify_contributions.py --json
python3 scripts/verify_missing_contributions.py
python3 contributions/issues/eclipse-score/score/3115/verify_packet.py
```

These checks establish retained byte integrity and preparation consistency. They
rerun no native code or provider calls. The packet manifest deliberately excludes
itself and `verification.json`, which records the final commands/results separately.

This remediation was prepared with OpenAI Codex. Human review of these corrections
remains pending. Policy source: [Eclipse Project Handbook](https://www.eclipse.org/projects/handbook/).
