# Draft dispositions and remaining actions

These are evidence-backed review notes, not engineering acceptance, waivers or source corrections. User-authorized additional #751 correction is isolated under `../additional-751/`; the original three-repair history and all previous candidates remain unchanged. No additional paid calls or publishing.

| Issue | Measured finding | Proposed next action | Decision status |
|---|---|---|---|
| #1236 | 27 global buildifier diagnostics; all27 affected source subjects byte-identical to pinned pristine source | Review and plan separate native lint-debt cleanup; retain global enforcement failure | No waiver/acceptance granted |
| #751 | One expected list retained the old order while the parser sorts/deduplicates | Extra correction completed: 502 tests passed, 6 skipped; Linux build, formatting, regressions and named-source extraction passed; review remaining coverage/validation limits | Measured results exported; human review pending |
| #1104 | Exact impl extraction reports Illegal option -o pipefail from rules_build_error+/lang/private/script/try_build.bash | Review external dependency/native action invocation. Script has no shebang and begins set -euo pipefail; the precise tracing/fallback mechanism is unresolved | Outside additional751 scope; no dependency source changes |
| #1031 | Native public AoU/visibility/separate-consumer checks pass; production Config Management integration and FMEA/LOBSTER non-duplication remain unmeasured | Obtain the actual production consumer/profile and perform native cross-repository verification in a disposable bound workspace | Applicability/integration and human acceptance pending |

Copyright failures remain unwaived for every candidate. Source inspection establishes that configured years are not an allowlist and untracked files are included by the native scanner; see `../native-source/copyright-policy-clarification.json`. Do not backdate headers, change policy, infer accepted deviations or claim fixture readiness. Contributor/ECA checks and QNX remain pending; see `../submission-obligations.md`.

Evidence: `1236-native-lint-classification.json`, `1104-native-extraction-review.json`, exported dependency source/LICENSE, `751-proposal.json`, native result/source manifests and complete prior run history. Exact native rule names, messages and source positions remain preserved; unknown mechanisms are explicitly unresolved.

Latest [offline reviewer checklist](REVIEW-CHECKLIST-20261007.md) supersedes the earlier #751 running status. All204 copyright diagnostic subjects match pristine source bytes; this is source comparison, not a baseline analyzer rerun or waiver.
