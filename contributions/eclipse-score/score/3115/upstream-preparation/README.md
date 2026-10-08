# Current native proposal and measured verification

> Current native head: see [license-header correction and direct checks](../license-review/README.md). The original source/commit and results below are preserved.

> Historical native candidate: use [version 3 completion and validation](../completion/README.md) for the current PR. The original source, bindings and results below remain preserved.

> Historical preparation: the inherited failure below is resolved on the updated PR by upstream commit `6122462`. See [fresh passing verification](../review-preparation/README.md). These original failed runs remain unchanged.

The current candidate is [DR-010-infra.rst](DR-010-infra.rst), placed at
`docs/design_decisions/infrastructure/DR-010-infra.rst` on native baseline
`fdc04f75a2251fcd8cbfd01585fba158c4e09756`. It preserves the ID from PR #3140,
uses native decision-record fields and remains **proposed**, version 2.
The existing glob includes it without an index change. This candidate is offered
for incorporation into #3140; maintainers decide the final scope.

| Check | Measured result |
| --- | --- |
| Unchanged baseline `bazel run //:docs_check` | Exit 1: one existing lifecycle outgoing-link warning |
| Corrected candidate `bazel run //:docs_check` | Exit 1: the identical baseline warning; zero new/schema warnings |
| Native export comparison | One proposed DR added; all 925 existing needs unchanged; none removed |
| Candidate CI command `bazel run //:docs` | HTML rendered; exit 1 on the inherited lifecycle warning |
| Native `bazel run //:copyright-check` | Exit 0; target scans tool/build configuration, not RST |
| Candidate whitespace | Passed; native Apache-2.0 header retained |
| Source/configuration/tool locks | Baseline hashes unchanged; Bazel 8.6.0 official digest verified |

The pre-existing warning is at `docs/features/lifecycle/architecture/index.rst:75`:
`logic_arc_int__lifecycle__report_running_if` fulfils unknown
`feat_req__lifecycle__switch_run_targets`. It was neither repaired nor suppressed.
**Native documentation CI is not green.** Maintainers must resolve or disposition
that baseline problem before readiness. No engineering acceptance is inferred.

The first candidate additionally had a short heading underline. Its source,
failed logs and exports remain in this folder; the corrected candidate removes
that diagnostic. The historical fabric checks were not rerun.

[Verification report](verification-report.json) binds the final candidate, exact
baseline, native inputs, export delta and check dispositions. Adjacent JSON
records contain full commands, exit codes, timings and log hashes. Full raw logs,
original exports/metrics, warning files and [the rendered page](candidate-rendered.html)
are retained. The page is a rendering artifact, not a standalone website.
The storage binding describes the isolated disposable workspace; copied evidence
remains in this contribution folder and does not require that mount for reading.

Publication and review links are recorded in `publication.json` after delivery.
Human responses, adoption, qualification and issue closure remain pending.
