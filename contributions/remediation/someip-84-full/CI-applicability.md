# Native CI applicability for full issue #84

Bound to `f8a196c3b16d5172d898394ab99b0ed81346d63d`; native policies,
workflows and hashes are preserved under `native-policy/`. Exact commands,
source bindings and outcomes are in `native-results.json` and `evidence/`.
Local execution does not constitute GitHub CI acceptance or a platform waiver.

| Obligation and native source | Local evidence | Outstanding acceptance |
| --- | --- | --- |
| CONTRIBUTION.md: ECA and DCO | Official account lookup and prepared native sign-off; no PR published | Actual PR author/committer eligibility and common PR checks |
| AGENTS.md: pre-commit; build-and-test.md: formatting | `final-precommit`, `final-format` | Checks on eventual submitted head |
| build_and_test_host.yml: default build/test | `final-build` runs `//...`; `final-host` runs `//... --build_tests_only` | Upstream run; inspect recorded conditional skips |
| Host ASAN/LSAN/UBSAN and TSAN | `final-asan`, `final-tsan` select the affected SOCom unit target | Full CI `//score/... //tests/...` matrix remains unmeasured locally |
| Linux QEMU default and sanitizer matrix | `final-qemu`: two targets pass, four fail on host tcpdump credential-change EPERM; guest applications pass; missing-tool attempt retained | Resolve/re-run default capture targets on an appropriate host; sanitizer integration matrix remains pending |
| Performance and flamegraphs | Not rerun for this expanded revision | Native workflow result or actual maintainer disposition |
| coverage.yml: 73% line gate | Not measured on this expanded revision | Native coverage workflow |
| docs.yml and quality_pack.yml | `final-docs`, `final-quality-tests`, `final-traceability`; raw metrics retained | Upstream jobs; quality trace gate is continue-on-error in baseline workflow |
| static-code-analysis.yml | `final-clang-tidy` selects `//score/socom/...` with native profile; no native lint config changed | Repository-wide clang-tidy and ruff workflows remain pending |
| Cross and QNX | Not executed locally | Apply actual event/`test-cross`/`test-qnx` conditions and authorized toolchains |
| License/Dash/IP | Native copyright and REUSE hooks; scoped AI notices, complete CC0 and IP request draft | Actual license job, committer net-new-IP assessment and required IP Team disposition |
| ci/can_merge and ci_pull_request_target/can_merge | Not evaluated: no PR exists | Applicable required jobs must succeed; no agent waiver |

The measured traceability gate reports 0/8 component requirements with source or
test links and 0/996 tests linked to requirements across the repository. Its
baseline zero thresholds pass; this supplies no formal trace coverage for the
new behavior and no native requirement acceptance. SOCom component requirements
remain an empty scaffold.

The native CI permits jobs skipped by its event/label conditions. A failed or
cancelled required job cannot be treated as an accepted omission. Native component
requirements for this behavior are an empty scaffold at the selected baseline;
committers must decide the requirement and contribution classification before
accepting this source API change.

Assisted-by: OpenAI Codex (model revision unavailable)
