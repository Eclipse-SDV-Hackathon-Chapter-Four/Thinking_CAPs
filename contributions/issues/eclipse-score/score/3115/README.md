# S-CORE #3115 — AI tooling decision and review evidence

[Issue #3115](https://github.com/eclipse-score/score/issues/3115) requests an AI tooling evaluation and a completed decision record. [PR #3307](https://github.com/eclipse-score/score/pull/3307) presents native `dec_rec__infra__ai_sdlc_tooling`, proposed version 3, at the current infrastructure path.

The recommendation is APM for packaging, Spec Kit for integration development and Harbor for comparative evaluation. Lola is a fallback; Syspilot is the preferred subsequent native-context prototype; BMAD remains an alternative; OKIT is limited to isolated prototyping; the archived Pharaoh repository contributes reviewed concepts. Native S-CORE artifacts and human accountability remain authoritative.

Start with the [complete review packet](completion/README.md), [native source](license-review/DR-010-infra.rst), [comparison](completion/comparison.md), [acceptance mapping](acceptance-mapping.md) and [merge readiness](completion/merge-readiness.md). Exact current check results are in [verification-report.json](license-review/verification-report.json); published PR, ECA, CI and reviewer state are in [publication.json](license-review/publication.json).

[License-header audit and corrected current source](license-review/README.md) supplies direct source-path checks alongside the full comparison and merge packet.

## Artifact identity and history

The original fabric source is HEAD `7e24a43c258f1dcaa2b27e02b501964847bc8714` plus captured dirty/untracked files. [Source identity](evidence/fabric/source-identity.json), [archive](evidence/fabric/source-snapshot.tar.gz) and [per-file inventory](evidence/fabric/source-files.json) bind all 1,139 selected files. Original captures for all eight tools, licenses, historical development checks, failures, controlled rendering proxies and native contribution references remain in the packet. The [evidence map](evidence-map.md) states replay limits; fixtures and historical checks do not establish production qualification or fresh dirty-worktree success.

The [original preparation](upstream-preparation/README.md) retains the first heading correction and inherited lifecycle failure. [Version 2 preparation](review-preparation/README.md) retains the subsequent passing baseline/candidate checks after upstream fix `6122462`. Version 3 changes the decision scope and is validated separately. Original authored draft bytes are retained under `completion/historical-proposals/`.

## Verify and review

Run `python3 contributions/issues/eclipse-score/score/3115/verify_packet.py` from an isolated checkout of the published evidence branch. It verifies retained bytes, identity and native references, not engineering acceptance. The broader registry and shared-workspace failures are retained with dispositions in `review-preparation/`; unrelated records/user work were not rewritten. An in-progress shared checkout may differ from the reference packets' retained manifests.

The [evidence branch](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/tree/contrib/score-ai-sdlc-3115-evidence/contributions/issues/eclipse-score/score/3115) is the portable reviewer copy. Branch rules, native CI commands, actual results and remaining human gates are recorded rather than inferred. PR #3307 is proposed as the replacement for the same-ID DR in #3140; merge one representation. Reviewers decide adequacy and may request additional comparison. Tool rollout and safety qualification remain separate engineering decisions. No issue closure or merge has been performed by this task.
