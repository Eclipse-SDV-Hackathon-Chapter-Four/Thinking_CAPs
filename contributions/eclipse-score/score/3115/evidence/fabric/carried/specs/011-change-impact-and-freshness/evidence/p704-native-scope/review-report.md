# P704 native impact and required-check review

The pinned original and approved historical candidate differ in exactly seven paths:
one shared Starlark macro added, three BUILD files changed and three JSON files
deleted. All unrelated sources and documentation remain unchanged. The measured
source manifests contain 740 original and 738 candidate files. The native commit
is `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`; the approved replay patch SHA is
`c8a33936900b24c13b46298e929d4ef483d0e128d44f9a2cce97909f55702f01`.

## Measured scope

| Measurement | Result | Limit |
| --- | --- | --- |
| Whole-workspace native test-label discovery | 135 in both trees; 33 launch-manager, 84 integration, 5 health-monitor, 13 other | Discovery is not execution or platform applicability |
| Historical pilot subset | 5 labels; 113 earlier cases | 130 other labels discovered; old XML is not fresh verification |
| Native export builds | pass in both trees | Export does not accept tailoring or establish source-to-Need impact |
| Native documentation checks | pass after genuine Git metadata binding | Initial missing-Git failures are retained |
| Expanded native Need comparison | 144 lifecycle + 1,251 process + 916 platform, no record additions/removals/modifications | Unchanged declarations cannot classify source changes as no-impact |
| Full reverse dependency queries | failed in both trees | QNX SDK checksum failure blocks complete closure |
| Functional test cases this phase | 0 | Newly discovered labels have no new pass claims |

The architecture declaration `feat_arc_sta__lifecycle__cfg_params_static` is native
version 1/status valid, ASIL_B/security YES. Its exported fulfils/includes/belongs_to
links resolve against the generated exports with exact simple version selectors.
The source citation remains a proposed impact seed. No accepted mapping of changed
source/build dependencies into that Need or its required work products is supplied.
All nine seed links and the collected simple-selector relations resolve; the
relation-resolution inventory is retained separately.

## Proposed expected-check matrix

Preserve the existing three parsed-JSON equality oracles, provider/client runfile
paths/values, integration tar path/value, buildifier, clean patch/seven-path inventory
and source/consumer sweep. Preserve all offline advisory/human review obligations.

| Check group | Pinned source basis | Current measurement | Proposed disposition |
| --- | --- | --- | --- |
| Linux build | on-pr.yml builds //examples/... and //score/... with x86_64-linux | Not executed this phase | Retain native CI scope |
| Linux tests | on-pr.yml tests //...; 135 discovered labels | No new execution | Do not replace with five-target minimum |
| Sanitizer tests | asan_ubsan_lsan and tsan matrix test //... | Not executed | Retain jobs and their source-declared build=false issue notes |
| ARM64 Linux build | arm64-linux build=true/test=false | Not executed | Retain build; source explicitly cannot run tests on x86_64 |
| Coverage | code_coverage.yml invokes //quality/coverage:run_coverage; default threshold 66 | Not executed | Preserve declared CI criterion; no coverage claim |
| Documentation | native needs_json and docs_check targets | Fresh build/check pass in both trees | Retain outputs and initial failure/recovery records |
| Common checks, Clippy, Gitlint | ready job dependencies and reusable workflow refs | Not executed locally | No omission or upstream CI acceptance inferred |
| QNX | README and .bazelrc declare support/profiles; PR matrix excludes QNX | SDK checksum failure; no execution | Applicability needs offline decision and valid SDK evidence; absence from PR matrix is not waiver |
| Native verification planning and reviews | process wp__verification_plan and related verification work products | Source/export traced | Bind accepted scope, criteria, methods, roles and exclusions separately |

The process verification plan requires objectives, methods, criteria, environments,
resources, anomaly handling and regression strategy. The source module safety plan
is draft with role/tailoring placeholders. Feature safety/security planning and the
module verification report also retain draft status. PROJECT_CONFIG's QM value does
not supersede ASIL_B/security declarations. These facts leave accepted applicability,
role and expected-denominator bindings unresolved.

## Retained failures and recovery

The original libpfm archive URL uses an unavailable mirror. Source metadata matches
the exact MODULE.bazel.lock registry hash; the alternate upstream redirect serves
the exact expected archive SHA. Only the task-local distdir changes; source/registry
inputs do not. The native resolver then refuses a QNX SDK download whose measured
bytes fail the expected checksum. No expected hash is weakened and no substitute
SDK or credentials are introduced. After further bounded attempts produced no
closure, only the owned SDK probe processes are stopped.

The documentation archive initially lacks Git metadata, causing code-link URL
checks to fail. A local clone of the genuine pinned commit supplies metadata with
hooks disabled and the canonical existing repository URL. No commit is invented
and no native source changes. Both subsequent docs checks pass with zero schema
validation warnings. The initial logs remain unchanged.

## Offline decisions still required

- Bind a reviewed P704 expected-check set, retaining the measured CI scope or citing
  authorized tailoring for exclusions. The 135-label inventory is proposed coverage.
- Establish the changed-source/build-to-native-Need/work-product impact mapping and
  accepted planning/role/criteria inputs; unchanged documentation is not no-impact.
- Decide QNX applicability and provide verified SDK-dependent evidence when required.
- Qualify observed provider-result/meter and actual agent prompt transmission before
  a new live DeepSeek comparison.

This is an agent review draft with deterministic evidence, not human acceptance.
T032/T033 markers remain pending, existing packets are immutable and PR publication
remains deferred. No new model savings claim is made.
