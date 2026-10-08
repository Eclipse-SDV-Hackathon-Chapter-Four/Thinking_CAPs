# Native impact and applicability assessment

This is a proposed tooling improvement, not a qualification or approval decision.
Target: docs-as-code draft #628, 4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9.

The baseline's `.github/pull_request_template.md` requires an impact analysis against
tool requirements and design decisions, documentation, tests and coding standards.
Its `docs/internals/requirements/tooling_verification.rst` says failed and skipped
tests are not allowed for merge. Native CODEOWNERS identifies infrastructure reviewers;
no reviewer approval has been obtained. The umbrella score contribution guide requires
ECA/DCO and describes an accepted improvement request before an implementation PR.
Issue #2850 is open; issue existence does not prove that request is accepted.

| Native requirement / current record | Impact and proposed disposition |
| --- | --- |
| `tool_req__docs_common_attr_id`, implemented YES | Retrieval and checks preserve IDs. Synthetic scenario IDs are fixture data. No changes to native uniqueness enforcement. |
| `tool_req__docs_common_attr_status`, implemented YES | Context retains status verbatim; goal blocks flag status changes. No changes to metamodel status validation. |
| `tool_req__docs_test_link_testcase`, implemented YES | Existing test links feed CR-003 and existing native metrics. Existing requirement is narrower than full change-impact automation. |
| `tool_req__docs_dd_link_source_code_link`, implemented YES | Native code-link metrics are reused; links remain inert in context. No new source-link resolution. |
| `tool_req__docs_stdreq_types`, implemented YES | Standard type/content changes feed CR-002/004. No changes to allowed need types. |
| `tool_req__docs_tvr_status`, implemented YES | No new report is marked evaluated/qualified/released by an agent. This packet is draft engineering evidence. |
| New assurance change-impact tooling scope | #2850 specifies the desired MVP, but an accepted native tool-requirement instance and qualification applicability are not identified. Maintainers must assign/accept them; no lookalike IDs are invented. |

Existing `docs/internals/decisions/001-test-results-in-workflow.md` governs importing
native test results. New tests use the existing `score_pytest`/JUnit infrastructure and
existing CI report upload. No test-result import semantics are changed. Native gate,
metrics calculation, metrics schema, MODULE pins/lock, requirements lock and lint policy
remain unchanged; final evidence checks their hashes against the baseline.

The JSON rule export is equivalent to the native YAML catalog. Runtime candidate code
uses stdlib and repo-local modules. Validator/evaluator dependencies come from the
existing locked requirements (jsonschema-rs), with no new runtime dependency or pin
upgrade. Rust/unsafe/FFI, compiler-target qualification and MISRA applicability are not
part of this Python infrastructure change. Platform verification is local Linux and
native Python 3.12; remote GitHub workflow execution is pending.

Safety/process impact: impacts are deterministic review prompts with source IDs, not
proof that ISO 26262/ASPICE assurance arguments are valid. The gate's verdict is not
changed by an agent. Candidate code loading remains trusted code, not a sandbox; the
bounded adapter reads only declared inputs/rules and preserves untrusted text. Phase 2
security controls in the upstream comment remain post-MVP, not silently accepted.

Proposed review decisions: accept the draft-baseline dependency/integration strategy;
accept rule/block semantics and the synthetic corpus; classify tooling safety and
qualification relevance; confirm coverage by existing requirements or create the native
qualification ticket required by the template. All remain human decisions.
