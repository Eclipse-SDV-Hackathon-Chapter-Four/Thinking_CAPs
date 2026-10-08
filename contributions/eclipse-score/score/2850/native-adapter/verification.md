# Verification report

Latest license follow-up: [audit and raw evidence](../integration-20261007/license-audit/README.md). The current patch contains 191 files: the 185 runtime-measured implementation files are unchanged, and six inherited native files received license comments. The pinned checker passes all 164 supported native files and 15 packet scripts. The 274-case runtime evidence below predates that comment-only follow-up; no runtime tests were rerun. Original headerless collector bytes, previous patch/bindings and all failed checks are retained.

Baseline, final patch, subjects, unchanged policies/contracts and native source archive:
`evidence/source/binding.json`. Tool identities: `evidence/tool-versions.json`.
Each measured stage has the exact command, cwd, source/config SHA-256 map, selective
non-secret environment, duration, exit code and raw stdout/stderr log in `evidence/checks/`.
`evidence/check-index.json` indexes attempts. Local measurements are collector evidence;
they are not independent engineering approval or a qualification decision.

| Expected check / native source | Recorded result (runtime stages predate header follow-up) | Evidence |
| --- | --- | --- |
| Full native `bazel test --lockfile_mode=error //...` | PASS, 11 targets, 274 cases, no errors/failures/skips | `complete-native-tests.*`, `native-testlogs/`, `junit-summary.json` |
| Native documentation check | PASS, build and needs-schema checks succeeded | `complete-native-docs.*` |
| Native candidate interface and boundary tests | PASS, 32 cases | adapter native JUnit/log |
| Rule/block, corpus, trace and fail-closed integration tests | PASS, 16 cases, including both candidates/splits | assurance native JUnit/log |
| Baseline native seeds | PASS, 4/4 active tasks | `complete-base_harness-native-seeds.*`, `native-seeds/` |
| Scoped candidate native seeds | PASS, 4/4 active tasks | `complete-pinned_context_harness-native-seeds.*`, `native-seeds/` |
| Baseline search and held-out evaluation with real cheap validation | PASS, 30/30 + 10/10 | `complete-base_harness-{search,heldout}.*`, `runs/` |
| Scoped candidate search and held-out evaluation with real cheap validation | PASS, 30/30 + 10/10 | `complete-pinned_context_harness-{search,heldout}.*`, `runs/` |
| Legacy rule candidate full CLI validation | PASS, no skip flags | `complete-legacy-validation.*` |
| Index-first query, failures and candidate differences | PASS, no mismatches | `complete-query.*` |
| Actual generated needs context and gate-compatible extraction | PASS, all export fields retained; extracted metrics schema valid | `actual-built-context-and-extraction.*`, `native-build-output/` |
| Original raw generated metrics against fixed gate schema | REJECTED as expected after investigation: `include_external` metadata is not admitted by schema | original output and error retained in `native-build-output/`; native runner re-extracts through unchanged calculation |
| Pinned changed-code Ruff lint/format | PASS | `final-lint.*`, `final-format-check.*` |
| Pinned changed-code BasedPyright with warnings as failures | PASS, 0 errors / 0 warnings | `final-types.*` |
| Whole project BasedPyright in actual native IDE environment | FAIL, 0 errors / 28 warnings | `native-project-types-ide.*`, `typing-comparison.json`; all diagnostics occur in byte-identical baseline files |
| Pristine baseline whole project type comparison, same IDE | FAIL, 0 errors / 101 warnings | `baseline-project-types-ide.*`, baseline source binding |
| Pinned native copyright checker | PASS on supported changed files | `final-copyright.*`; native checker has no JSON/Markdown template |
| Native basic syntax, whitespace/conflict/key and size checks | PASS, 185 native files; native 150 KiB limit | `final-native-file-syntax.*`, retained collector |
| Native module tidy | PASS, source/policy subjects unchanged | `confirmed-native-mod-tidy.*` |
| Native actionlint 1.7.11 and workflow parsing | PASS | `final-workflow.*`; native shellcheck/pyflakes settings preserved |
| Current patch application to pristine native source | PASS; all 191 files match and nine fixed contracts unchanged | `patch-application.json`, latest license audit |
| Native and parent packet integrity | Measured separately by the offline verifiers | `manifest.json`, parent `artifact-manifest.json` |
| Native full pre-commit readiness | NOT established: whole-project typing findings remain; individual checks measured, no blanket hook success claimed | merge checklist |
| ECA/DCO, request/design/qualification acceptance and code-owner review | HUMAN / pending | merge checklist and native template/guide |
| Hosted GitHub workflow and branch protection | NOT executed/configured by this task | workflow implemented; all command paths measured locally |
| Model performance, deployment/tool qualification, Phase 2 | EXCLUDED from MVP verification | issue explicitly separates Lane B and post-MVP Phase 2 |

The native inactive task_001 is an instructional example, excluded by its own flag.
All four active original native tasks were finally run, including the actual build-backed
snapshot. Scenario inputs are static synthetic public fixtures, with explicit expected
verdict/impact oracles. The public held-out split was debugged as OSS test data; no blind
model benchmark or agent improvement is claimed. Baseline and candidate matching all
oracles verifies execution/contract correctness, not a retrieval-quality advantage.

Historical failures remain indexed: preliminary current-main checks; ambient Python/plugin
collection errors; missing runfiles in standalone setup; initial draft typing warnings;
invalid Bazel file labels; incorrect gate option/exit-code handling; incomplete oracle
propagation and the combined fixture oracle correction; legacy validator runfiles/venv
configuration; Bazel CLI runfiles path handling; RST underline and missing scratch Git
remote; and original generated metrics/schema mismatch. They are superseded only by
checks on matching final subjects, not removed or presented as passes. A reused formatter
log name lost one intermediate format-failure command record; its reported output is
explicitly reconstructed in history, and final formatting was freshly verified. An optional collector log-name collision is labelled and excluded in `collector-history/`; module tidy was rerun sequentially with an unambiguous record.

Cached native target evidence is retained with matching source/dependency identities;
new/changed subjects were rerun. Supplementary direct Python checks use 3.12.14; native
Bazel/IDE execution uses 3.12.12, Bazel 8.4.2, Ruff 0.15.9 and BasedPyright 1.39.0.
Final technical MVP verification is complete; repository-wide typing disposition and
native engineering/contributor acceptance remain unresolved merge obligations.
