# License-header correction and current native verification

The current native source is [DR-010-infra.rst](DR-010-infra.rst), with [source binding](source-binding.json), [patch](native-proposal.patch) and [verification report](verification-report.json). It uses S-CORE's exact pinned Apache-2.0 RST header. The packet verifier also has the pinned Python header after its shebang; NOTICE identifies authorship and original source licenses. [The audit](packet-code-headers.json) and direct check logs cover actual source paths.

The original native copyright target resolves its `docs` input to a generated CLI. Its pass did not establish direct RST coverage. The original legal notice was present, but failed the native checker's exact template. Both this mismatch and the previously absent verifier header are corrected. Initial check/source bytes are preserved under `before/` and `direct-headers-before.*`.

All eight applicable native checks are rerun and pass on the corrected head, including docs/HTML with zero warnings and 30 FEP/FCP tests. All 925 existing needs and the decision body are unchanged. Original completion checks remain attached to their original commit. [The eight-tool comparison](../completion/comparison.md), acceptance mapping and captured branch rules remain applicable.

[Publication](publication.json) records the corrected upstream head, ECA and actual hosted workflow/review state. [Reviewer handoff](../completion/review-handoff.md) describes the remaining human gates. Archived third-party/native/fabric source retains original notices and provenance; this audit does not relicense or certify all historical source trees.

Policy copies under `policy/` identify the exact checker, template, config and native LICENSE/NOTICE bytes. The packet inventory and outer manifest bind all retained artifacts. Verifier behavior is unchanged, as recorded in utility-behavior-comparison.json.
