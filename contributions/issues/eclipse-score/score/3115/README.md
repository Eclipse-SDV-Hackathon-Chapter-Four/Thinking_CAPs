# S-CORE #3115 — Evidence for AI SDLC / SpecKit tooling evaluation

Prepare an evidence-backed decision-record supplement using experience from
`s-core_sw_fabric`. The selected issue is
[Evaluate AI SDLC / SpecKit Tooling](https://github.com/eclipse-score/score/issues/3115).
Its existing [PR #3140](https://github.com/eclipse-score/score/pull/3140) is open and
unmerged. This packet addresses reviewers' requests for implementation experience,
native process ownership, lifecycle loopbacks, bounded context and qualification limits.

| Field | Record |
| --- | --- |
| Captured | 2026-10-07; exact retrieval times in capture records |
| Local status | Current native review candidate prepared; fresh baseline/candidate checks retained |
| Fabric baseline | `7e24a43c258f1dcaa2b27e02b501964847bc8714`, plus captured working-tree changes and untracked source |
| Source | [Fabric source identity](evidence/fabric/source-identity.json), [snapshot](evidence/fabric/source-snapshot.tar.gz), [per-file hashes](evidence/fabric/source-files.json) |
| Upstream status | Issue open, assigned to `aryansingh0012` and `praveen-ltts`; adoption and issue closure pending |
| Existing DR | `dec_rec__infra__ai_sdlc_tooling`, proposed in PR #3140 |
| New publication | [Draft PR #3307](https://github.com/eclipse-score/score/pull/3307); [review requested](https://github.com/eclipse-score/score/issues/3115#issuecomment-6031268045) |

Start with the [current native proposal and measured verification](upstream-preparation/README.md).
The original local [decision-record proposal](decision-record.md), then the
[evidence map](evidence-map.md) and [acceptance gaps](acceptance-mapping.md).
[Issue selection](issue-selection.md) explains why #3115 fits this contribution.
[PR description](pr-description.md) and [native supplement](native/supplement.rst)
are ready for offline review. The [supplement patch](native/supplement.patch) is
bound to the captured PR head, not claimed to apply to today's reorganized `main`.

## What travels with this packet

- Original GitHub issue, comments, timeline, PR reviews and inline comments, proposed
  DR, current contribution guidance, PR template and native decision-record template.
- Revision-pinned README, license when available and repository metadata for all
  eight tools in #3115. These are read-only research, not execution results.
- Fabric source, tests, schemas, policies, profiles, Spec Kit controls, architecture,
  acceptance records, locks and handoffs, including selected untracked development files.
- Historical raw development logs, JUnit, native-export evidence, benchmark records
  and high-level follow-up reports. Failed attempts and pending acceptance remain visible.
- References to native contribution packets already retained in this repository.
  Their original bytes are preserved rather than duplicated here.
- SHA-256 manifests and an offline verifier for this packet and its source archive.

## Verify offline

From this repository root:

```bash
python3 contributions/issues/eclipse-score/score/3115/verify_packet.py
python3 scripts/verify_contributions.py
git diff --check
```

These checks establish retained-byte integrity, source-archive closure and contribution
registry consistency. They do not rerun fabric tests, native builds or provider calls.
Historical logs are evidence for their recorded subjects, not fresh validation of the
dirty source snapshot. The inventory of omitted historical bytes is an index, not
a substitute for those bytes. See [provenance](provenance.json) and the evidence map.

For future execution, unpack the source archive into a separately allocated disposable
workspace and follow its `AGENTS.md`, locks and selected increment's reproduction guide.
Inspect hooks, build rules and configuration before running checks. Native references
stay read-only; production trust roots, credentials and private server state are absent.

## Contribution route

The native DR has been reconciled against the current
`docs/design_decisions/infrastructure/` layout and template, preserving its ID.
Native checks are recorded in [the fresh verification report](upstream-preparation/verification-report.json):
no new warnings, one unchanged baseline lifecycle warning, documentation CI still failing.
Offer this pilot evidence to #3115's assignees for incorporation into PR #3140. The proposed decisions still need maintainers'
review, an agreed evaluation scope and required native documentation CI. ECA/DCO
requirements are retained in the captured contribution guide. This packet neither
closes #3115 nor proposes wholesale adoption of the fabric.


## Published review candidate

The [evidence branch](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/tree/contrib/score-ai-sdlc-3115-evidence/contributions/issues/eclipse-score/score/3115)
is published, and native [draft PR #3307](https://github.com/eclipse-score/score/pull/3307)
is offered for incorporation into #3140. A [review request](https://github.com/eclipse-score/score/issues/3115#issuecomment-6031268045)
was delivered to both #3115 assignees. Publication identities and the exact submitted
body are retained in [publication.json](upstream-preparation/publication.json).
Human responses, native CI, acceptance and qualification remain pending.
