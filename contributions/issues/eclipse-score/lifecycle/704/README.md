# Lifecycle #704 — shared communication configuration

| Field | Record |
| --- | --- |
| Upstream issue | [Deduplicate mw_com_config.json files #704](https://github.com/eclipse-score/lifecycle/issues/704) |
| Local status | Fabro/DeepSeek Flash implementation verified; owner approval recorded for local PR preparation |
| Upstream status | Open at 2026-10-04; upstream PR URL not recorded |
| Baseline | `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b` |
| Source | `s-core_sw_fabric`, increment 011 lifecycle evidence |

## Problem and fix

Three communication JSON configurations repeated the same service definitions.
The patch introduces `config/mw_com_config.bzl`, which generates the three outputs
from one shared definition and explicit provider-test, client-test and integration
profiles. Existing labels, filenames, runfiles and integration package paths are
preserved. The three effective JSON objects remain equal to the baseline, including
their different safety/security and consumer settings.

## Evidence and artifacts

- [Approved current patch](imported/fabro/evidence/lifecycle-704-upstream-packet/lifecycle-704.patch),
  [PR title](pr-title.txt) and [upstream improvement PR body](pr-description.md).
- [Local upstream PR packet](imported/fabro/evidence/lifecycle-704-upstream-packet/README.md),
  [checkout verification](imported/fabro/evidence/lifecycle-704-upstream-packet/checkout-verification.json)
  and [validation index](imported/fabro/evidence/lifecycle-704-upstream-packet/validation-index.json).
- [Actual Fabro/Flash implementation evidence](imported/fabro/evidence/lifecycle-704-flash-retry/README.md),
  [native test results](imported/fabro/evidence/lifecycle-704-flash-retry/native-test-results.json),
  [configuration equivalence](imported/fabro/evidence/lifecycle-704-flash-retry/configuration-equivalence.json),
  [unit runfiles equivalence](imported/fabro/evidence/lifecycle-704-flash-retry/unit-runfiles-equivalence.json)
  and [package equivalence](imported/fabro/evidence/lifecycle-704-flash-retry/packaged-configuration-equivalence.json).
- [Owner decision and exact subjects](imported/fabro/lifecycle-704-owner-review.md),
  [advisory review](imported/fabro/evidence/lifecycle-704-flash-retry/critique-model-output.json),
  [review responses](imported/fabro/evidence/lifecycle-704-flash-retry/review-evidence-responses.md)
  and [transport retention gap](imported/fabro/evidence/lifecycle-704-flash-retry/transport-retention-gap.json).
- [Upstream activity observation](imported/fabro/evidence/lifecycle-704-upstream-packet/upstream-freshness.json),
  [contribution instructions](imported/fabro/evidence/lifecycle-704-upstream-packet/upstream-instructions/CONTRIBUTION.md.txt)
  and [license notices](imported/fabro/evidence/lifecycle-704-upstream-packet/source-license/).
- [Capture manifest](artifact-manifest.json), [provenance](provenance.json)
  and [upstream snapshot](upstream-snapshot.json).

### Earlier Codex implementation evidence

The original import remains unchanged as historical evidence. Its patch is a separate
implementation and is superseded by the approved Flash patch for the current PR draft.

- [Earlier patch](imported/lifecycle-704.patch) and
  [portable application check](imported/portable-patch-check.json).
- [Original implementation report](imported/README.md) and [summary](imported/summary.json).
- [Configuration equivalence](imported/configuration-equivalence.json),
  [packaged configuration equivalence](imported/packaged-configuration-equivalence.json)
  and [baseline configurations](imported/baseline-configurations.json).
- [Native test XML/logs](imported/logs/test-results/) and exact command records in
  [logs](imported/logs/), including failed socket-collision attempts and the passing
  isolated run; [Bazel wrapper](imported/run-bazel.py.txt).
- [Buildifier command/result](imported/logs/buildifier.json) and
  [comparison preparation](imported/comparison/preparation-summary.json).
- [Original source/license/tool snapshots](imported/upstream/),
  [original manifest](imported/manifest.json), [capture manifest](artifact-manifest.json),
  [provenance](provenance.json) and [upstream snapshot](upstream-snapshot.json).

## Current patch validation

| Native target | Passing test cases |
| --- | ---: |
| `control_provider_UT` | 3 |
| `ilm_control_UT` | 2 |
| `lm_control_impl_UT` | 36 |
| `lifecycle_config_tests` | 71 |
| `switch_run_target` | 1 |
| Total | 113 |

All five targets passed with zero failures, errors or skips. Bazel-generated outputs
match all three baseline JSON objects; the integration tar preserves its filename
and effective configuration. Buildifier formatting/lint passed. The patch applied
cleanly in a second disposable baseline checkout.

Flash produced the macro and BUILD edits through native Fabro, followed by a focused
Flash repair and separate buildifier formatting. Five generation/review requests are
retained in the later qualification; these do not measure B1–B5 live savings. The final
guarded proof completed deterministic checks and advisory review, then stopped at an
unanswered human gate. All paid ledgers and disposable servers were stopped.

The owner subsequently approved the exact patch and advisory responses for local PR
preparation. This records local approval; Eclipse committer review/CI, contribution
certifications, native impact/export closure and QNX execution remain pending. Two
legacy raw transport envelopes are missing; structured outputs/native usage remain,
and the corrected transport's final proof has complete raw records. Original packet
labels and evidence bytes are preserved. Native tests were not rerun for this export.

The earlier comparison preparation recorded zero provider calls at that earlier stage.
It does not describe the later Fabro/Flash implementation imported here.

Current approved patch SHA-256:
`c8a33936900b24c13b46298e929d4ef483d0e128d44f9a2cce97909f55702f01`.

Earlier Codex patch SHA-256:
`6de3c13813f6ab15261af443d5f20f9a54366a14b1c48a74cd6bc314a190e7df`.

## Later upstream PR

Use the prepared title, improvement-template body and approved current patch. The
local contribution branch is uncommitted and nothing has been published. Refresh
against the intended upstream branch, satisfy ECA/DCO requirements, and open the PR
as Draft when publication is authorized. Record the actual PR/merge links
in [the registry](../../../../registry.json) when available.
