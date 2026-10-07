# Improvement

## Description

Complete the AI tooling evaluation for #3115 with explicit recommendations and rationale for all eight listed options. Recommend APM for packaging, Spec Kit for integration development and Harbor for comparative evaluation. Keep S-CORE's native engineering workflow authoritative. Retain Lola as a fallback, Syspilot as the preferred subsequent native-context prototype, BMAD as an alternative, OKIT for isolated prototyping, and reviewed Pharaoh concepts without adopting its archived repository.

The native decision record preserves `dec_rec__infra__ai_sdlc_tooling`, remains `proposed`, and advances to version 3. Recommendations distinguish source-based engineering judgment from retained Spec Kit/fabric execution. Comparative deployment results, tool qualification and human acceptance are not invented.

This is a replacement candidate for the same-ID DR in #3140. Merge one representation at the current infrastructure path: accept this PR and supersede #3140, or incorporate this content there and supersede #3307. The contributor has not modified or closed another author's PR.

## Related ticket

Closes #3115 upon accepted merge of the evaluation decision record. Relates to #3140.

## Validation and review artifacts

[Complete review packet](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/tree/contrib/score-ai-sdlc-3115-evidence/contributions/issues/eclipse-score/score/3115/completion) includes the native source/patch, comparison and acceptance mapping, immutable source identities, exact check commands and logs, native export delta, license/qualification limits, public branch rules and reviewer handoff. The native source diff adds only the decision record. Current main already includes lifecycle link fix `6122462`; earlier failed runs are preserved.

The final local check results and hosted workflow state are recorded in `completion/verification-report.json` and `completion/publication.json`. Local results do not imply hosted CI success. The public main rules require passing ECA and one approval with code owner coverage; neither an agent recommendation nor a test result supplies that approval.
