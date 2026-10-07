# Full SOME/IP issue #84 implementation and review packet

The prepared implementation covers the three models proposed in
[issue #84](https://github.com/eclipse-score/inc_someip_gateway/issues/84):
service ID + major identity, full offered-instance identity, and discovery
requests with optional minimum minor and instance filters. It also preserves
the duplicate-registration fix from the previous scoped contribution.

Native SOCom now exposes a bounded, allocation-free local discovery snapshot.
All in-repository consumers of the renamed connector contract are migrated;
serialized IPC fields stay the same. External consumers must migrate the source
API and rebuild. Read [ACCEPTANCE.md](ACCEPTANCE.md) for the issue mapping and
[the native version/migration guide](source/score/socom/docs/version_handling.rst).

The source baseline is `f8a196c3b16d5172d898394ab99b0ed81346d63d`.
[preparation.json](preparation.json) identifies the prepared native commit.
Both [the plain patch](submission.patch) and [the DCO mail patch](submission-with-dco.patch)
are verified against a fresh baseline and reproduce every candidate source file.
The historical [scoped packet](../someip-84/README.md) is preserved separately.

Measured results for this exact source:

- Full native build: passed, 153 targets.
- Default tests: 21 targets passed, eight configuration skips.
- SOCom: 722 cases passed under default, ASAN/LSAN/UBSAN and TSAN.
- Native pre-commit, formatting, affected Clang-Tidy, docs and unit/component
  targets: passed.
- QEMU: two targets passed; four failed in unchanged host packet-capture setup
  when tcpdump tried to change root credentials (Operation not permitted).
  The guest application suite passed SOCom unit/stress, IPC and serializer
  binaries; one baseline multi-process test was skipped. Full integration
  acceptance remains pending. See [the disposition](evidence/qemu-disposition.json).

[Native results](native-results.json) bind exact commands and raw logs to the
exported source. The full default build/test, SOCom sanitizer checks, affected
Clang-Tidy profile, pre-commit, formatting and documentation checks are recorded
there. The integration attempt and any environment failure are reported explicitly.
[CI-applicability.md](CI-applicability.md) lists the remaining native matrix;
this packet does not claim a complete upstream CI pass. The traceability gate
passes its baseline zero thresholds; it reports 0/8 requirements with source/test
links and 0/996 linked tests repository-wide, not accepted trace coverage for
this new behavior.

Review artifacts:

- [PR description](PR-body.md) and [content-review issue draft](bugfix-issue-draft.md).
- [Issue acceptance map](ACCEPTANCE.md) and [agent assessment](SELF-REVIEW.md).
- [Prepared DCO](DCO.md), [AI/human review disposition](HUMAN-DISPOSITION.md) and [IP request](IP-review-request.md).
- [Source and patch hashes](candidate-files.json), [policy hashes](native-policy-hashes.json), [patch application proof](evidence/patch-verification.json) and [packet manifest](artifact-manifest.json).

The required exact-revision human AI review, committer API/semantics and
contribution-classification acceptance, IP assessment/required IP Team disposition,
and remaining applicable native CI are pending. Existing `comp__socom` and
`feat__someip_gateway` documentation IDs are preserved; native formal requirement
IDs for this behavior remain unknown. [status.json](status.json) keeps merge
readiness false.

The local DCO is prepared under the user's continuing instruction for this
contribution. The earlier scoped approval is not reused as human review of the
expanded code. No native PR has been created, no contribution published and no
issue closed.

To inspect the native source, use the complete changed-file snapshots under
`source/`, or apply the mail patch to a checkout at the stated baseline. [Reproduction instructions](REPRODUCE.md) describe the native commands. Native
Bazel pins and project policies are unchanged; verification scripts and tool
identities are included for reproduction. [verification.json](verification.json)
records final packet integrity checks, not engineering acceptance.

Assisted-by: OpenAI Codex (model revision unavailable)
