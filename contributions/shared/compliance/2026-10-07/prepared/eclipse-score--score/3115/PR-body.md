# Improvement

## Description

Add an evidence-backed review candidate for the AI SDLC tooling decision record in #3140. Use the current infrastructure folder and native template fields, retaining the existing `dec_rec__infra__ai_sdlc_tooling` identifier and `proposed` status.

Explain the integration problem within S-CORE's existing process and map `s-core_sw_fabric` experience to lifecycle loopbacks, bounded agent context, deterministic checks, native use and human review. Cover all eight issue-listed tools, separating implemented Spec Kit/fabric experience from primary-source research on alternatives. Preserve historical failures, fixture measurement limits and pending qualification.

This candidate is offered for incorporation into #3140. Maintainers determine the final decision scope and required comparative pilots.

## Related ticket

Relates to #3115 and #3140. No issue closure requested.

## Validation

Tested in an isolated checkout of current main `fdc04f75a2251fcd8cbfd01585fba158c4e09756`, using pinned Bazel 8.6.0 and docs-as-code 8.3.0 without changing policy/tool locks.

- Baseline and corrected candidate `bazel run //:docs_check` both exit 1 on the same pre-existing lifecycle link warning at `docs/features/lifecycle/architecture/index.rst:75`: `logic_arc_int__lifecycle__report_running_if` fulfils unknown `feat_req__lifecycle__switch_run_targets`. Candidate adds no documentation warnings and has zero schema warnings.
- Export comparison adds only the proposed decision record; all 925 existing needs are unchanged and none removed.
- `bazel run //:docs` renders the page, then exits 1 on that inherited warning. Documentation CI is not green.
- Native `bazel run //:copyright-check` and candidate whitespace check pass. The native copyright target scans configuration/tools rather than RST; the candidate includes its native Apache-2.0 header.
- Initial candidate heading error, correction, full commands/logs, source hashes and export delta are retained in the [verification packet](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/Thinking_CAPs/tree/contrib/score-ai-sdlc-3115-evidence/contributions/issues/eclipse-score/score/3115/upstream-preparation).

This remains a draft pending maintainer scope/review and resolution or disposition of the baseline documentation failure. Engineering acceptance and tool qualification remain pending.


## AI assistance and review

- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
