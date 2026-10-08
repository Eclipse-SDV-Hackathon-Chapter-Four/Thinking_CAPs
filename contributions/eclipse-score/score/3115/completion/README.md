# Complete native evaluation and merge review packet

> Current native head: see [license-header correction and direct checks](../license-review/README.md). The original source/commit and results below are preserved.

Read [the native decision record](DR-010-infra.rst), [comparison](comparison.md), [acceptance mapping](../acceptance-mapping.md) and [merge readiness](merge-readiness.md). [Source binding](source-binding.json) identifies the exact candidate commit, native ID/status/version and patch scope. [Verification report](verification-report.json) links every applicable check to commands, inputs and complete raw logs. Native exports and the rendered page are retained; the page is a rendering artifact, not a standalone site.

[rules.json](rules.json) and [ruleset.json](ruleset.json) capture the public main rules. Native contribution/template/CI inputs are copied under `native-guidance/`. [Publication](publication.json) records the final PR, ECA, hosted workflows and delivered review requests. The packet's outer SHA-256 manifest covers all these bytes; its detailed inventory records paths, sizes and hashes.

Original failures and version 2 validation remain under `../upstream-preparation/` and `../review-preparation/`. Historical fabric execution and documentary candidate comparisons remain labelled. The new version recommends tools; rollout validation and qualified use are follow-on engineering work. The native source remains proposed until an authorized decision. No merge or human approval is fabricated.

All applicable local checks pass, including formatting, module/lock hygiene, Gitlint and 30 FEP/FCP unit tests. The explicit native conditional exclusions and remaining human gates are in the readiness report.
