# Evidence and acceptance gaps — refreshed 2026-10-07

The [original completeness audit](audits/2026-10-07-completeness.json) records the
state before import. The [import record](audits/2026-10-07-import-record.json)
records the subsequent additions and corrections; the earlier audit is historical.

Diagnostics #16's five patches and CDA #543's patch are present. Their native
baseline/application/build/tests and acceptance remain pending. The former
missing-patch description has been superseded by recovery, not by validation.

The four Communication bug records #1236, #1031, #751 and #1104 now link to the
[new native contribution packet](communication-followup-20261007/README.md).
Pinned lint passes, current extraction hash-matches 516/516 configured C++ inputs,
and all 218 queries and native reports pass with zero empty file URI occurrences.
The current host suite passes 508 tests with seven explicit skips. The native
query correction supersedes the placeholder-hiding normalizer. Complete production
Config Management/FMEA integration remains blocked on legacy safety data and AoU
owner decisions; copyright checks now pass, and required hosted/platform CI/review remain
open. The original portable queue and all failed/historical evidence are preserved.

Communication #1167 has [PR #1335](https://github.com/eclipse-score/communication/pull/1335) with all six non-QNX fork Host jobs passing, zero lint findings in the new test, official ECA validation and full final-source artifacts. The pinned-baseline copyright comparison remains failed with 200 identical inherited findings and zero PR additions. Native workflow approval/required statuses, code-owner approval, copyright handling and merge queue remain pending; later upstream changes are not claimed tested by the fork. QNX is excluded by the user, without waiving upstream rules. Original human acceptance remains tied to the original measured source. [Final records](communication-1167/CURRENT-STATUS.md) preserve all attempts. Companion [PR #1341](https://github.com/eclipse-score/communication/pull/1341) repairs headers across all 2,367 code/build paths (91 changed files); its code check passes with zero findings, while 136 non-code findings remain. [Header packet](communication-1167/repository-license-headers/README.md) preserves its separate source and verification; full native suite and maintainer review for that PR remain pending.

The consolidated branch retains the twelve additional Rust queue records and
#2850/#3115 proposals. The consolidated evidence is included on `main`. Broader native engineering
acceptance remains pending. Competition eligibility and required submission format remain
unevaluated. Source integrity verification is separate from these decisions.

## Compliance follow-up

CDA issue #543 is published as native PR #601; diagnostics issue #16 as native
PR #40. Their submitted heads differ from the recovered historical patches.
Both fail the actual author's ECA check; diagnostics also lacks native DCO
sign-offs. Anthropic Claude Opus 5.5 authoring assistance was confirmed by
Jefferson; corrected PR/commit drafts are prepared locally. Public PRs remain
unchanged. See the [current compliance record](compliance/2026-10-07/README.md).

## Communication #1261, #250 and #560 readiness follow-up

The [completion packet](issues/eclipse-score/communication/rust-api-queue/completion-20261007/README.md)
provides the integrated source, scoped configured-LoLa discovery contract,
API/ABI and ownership corrections, detailed design and examples, PR draft,
bundle/archive/patch, native trace, check inventory and human/IP review subjects.
All 40 contribution code files have native Apache-2.0 notices; the changed-file
checker passes. The original sealed readiness packet and failed history are
preserved. Entirely unconfigured interface types remain outside this contribution.

The full Linux suite passes 510 of 517 selected targets, and ASan passes 509 of
517; exclusions are recorded. TSan records 404 passes, one failing new test and
112 skips. Its instrumentation explanation is an inference, not an accepted
waiver. The whole-tree notice check has 200 unchanged baseline findings, and
strict Clippy coverage of the macro-test forwarder remains incomplete. Native
semantic document findings and the network-failed module-graph query remain
visible. Licensed QCC, native owner trace/qualification, human engineering/IP,
final-head ECA and protected hosted statuses remain pending. Integrity checks
establish artifact consistency, not merge acceptance.
