# Lifecycle #704 — local upstream PR packet

The owner approved the exact Flash-produced patch and advisory review responses, then
explicitly selected local PR preparation. The contribution packet is complete; nothing
has been committed or published, and no new paid model call was made.

- [PR title](pr-title.txt) and [filled upstream improvement template](pr-body.md).
- [Portable approved patch](lifecycle-704.patch), SHA-256
  `c8a33936900b24c13b46298e929d4ef483d0e128d44f9a2cce97909f55702f01`.
- [Local owner decision](../../lifecycle-704-owner-review.md),
  [checkout verification](checkout-verification.json), [upstream freshness](upstream-freshness.json),
  [validation index](validation-index.json), [publication plan](publication-plan.json),
  and [storage binding](storage-selection.json).
- Exact copied [contribution instructions](upstream-instructions/CONTRIBUTION.md.txt),
  [improvement template](upstream-instructions/.github/PULL_REQUEST_TEMPLATE/improvement.md.txt),
  [CODEOWNERS](upstream-instructions/.github/CODEOWNERS) and [license notices](source-license/).
  `.md.txt` retains original upstream bytes without treating relative upstream links as
  files in this packet.

## Contribution checkout

Checkout: `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-704-contribution-89oztdzm/lifecycle`.
Local branch: `cleanup/lifecycle-704-mw-com-config`.
Base: `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b` on upstream `main`.

The fresh shared-storage checkout contains exactly the approved seven-path change: one
new macro, three changed BUILD files and three removed JSON files. Each resulting source
file matches the reviewed SHA-256; hook inspection, clean patch application, diff whitespace
checks and buildifier format/lint checks pass. No native source/config changes beyond the
approved patch were made. The branch is uncommitted so contributor identity and signoff
remain truthful, unresolved publication inputs rather than fabricated certifications.

## Validation and remaining review

The exact subject retains 113 passing native cases in five targets, all-three parsed JSON
equivalence, provider/client unit runfiles equality and integration tar path/value equality.
Native tests were not repeated for unchanged source solely to prepare this packet. The
[immutable earlier review packet](../lifecycle-704-flash-retry/README.md) retains logs,
actual model provenance, advisory findings and draft evidence responses, including the
explicit two-envelope transport-retention gap. Its 191-file manifest and all 20 T032
reviewed subjects remain unchanged.

The current upstream baseline still matches the tested commit. Issue #704 remains open,
unassigned, with no comments. All 22 currently open PRs were checked for exact changed-path
overlap and #704 references; none matched. This is a timestamped observation, not a promise
of future exclusivity. Recheck source/activity before any later publication.

The upstream guide requires a draft PR for this contribution stage, ECA/DCO contribution
requirements and committer review. Those certifications/roles were not verified or recorded
on the owner's behalf; no signoff or commit is created. The owner approval here is local
review authority, not Eclipse committer acceptance or an authenticated 005 native receipt.

QNX, full native impact/export closure and real-target B1–B5 savings remain unmeasured.
T032/T033 human markers remain untouched; their broader acceptance is not inferred from
this local contribution packet. All prior paid ledgers/servers remain stopped.
