"""Draft review artifacts separately from the sealed native assessment and execution."""
import json
from pathlib import Path

from score_sw_fabric.storage import validate_run_root

root = Path(__file__).parent
validate_run_root(root)
packet = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265/engineering-review') / root.name
checks = json.loads((packet / 'deterministic-review-checks.json').read_text())
assert checks['input_subjects_verified'] == 1359
N = 'native-verification'
D = N + '/historical-rust-and-copyright/prior-attempt/sources/score-crates/docs/pastey'
C = N + '/historical-rust-and-copyright/prior-attempt/sources/crates/pastey-0.2.3'
A = N + '/sources/native/score/mw/com/rust/design/identifier_pasting_assessment.md'

findings = [
    dict(label='R1', title='Exact compiler certification and use scope are unestablished', consequence='Blocks a claim that the communication use satisfies the compiler AoU; does not invalidate the measured Linux cases', sources=[D+'/docs/safety_analysis/aou.trlc:17', 'review-evidence/toolchain-MODULE.bazel:36', N+'/historical-rust-and-copyright/execution/logs/compatibility2-ferrocene.log:1'], native_obligations=['PasteyAoU.PasteyRustCompilerCertified@1'], proposed_action='Obtain the exact-build certificate, qualification package, supported host/target and procedural-macro/library/flags scope; reconcile the identified rolling/nightly build with that evidence'),
    dict(label='R2', title='Published classification is not communication qualification/adoption evidence', consequence='Blocks claiming completed qualification/adoption', sources=[D+'/docs/component_classification.rst:19', D+'/docs/component_classification.rst:223', D+'/docs/component_classification.rst:228'], native_obligations=['doc__pastey_crate_comp_class'], proposed_action='Bind the Accepted change request, adapted module safety plan, qualification reports and communication-specific adoption to the exact selected version/use case'),
    dict(label='R3', title='Upstream environment and entry-point descriptions need clarification', consequence='Unresolved classification/architecture rationale; no agent reclassification', sources=[D+'/docs/component_classification.rst:93', D+'/docs/component_classification.rst:165', D+'/docs/architecture/index.rst:44', D+'/docs/requirement/component_requirements.trlc:88', C+'/src/segment.rs:184', C+'/src/lib.rs:31'], native_obligations=['doc__pastey_crate_comp_class', 'doc__mod_pastey_architecture', 'PasteyComReq.REQ_COMP_PASTEY_011@1'], proposed_action='Clarify compile-time environment versus runtime configuration and whether hidden aliases count in the entry-point complexity rationale; retain existing native statuses until authorized disposition'),
    dict(label='R4', title='Some upstream requirement-linked tests do not establish the cited behavior', consequence='Blocks treating linked tests as demonstrated requirement closure; these upstream targets were not executed in this run', sources=[D+'/tests/pastey_test.rs:64', D+'/tests/pastey_test.rs:86', D+'/tests/pastey_test.rs:117', D+'/tests/pastey_test.rs:131', D+'/tests/pastey_test.rs:212', D+'/tests/pastey_test.rs:226'], native_obligations=['PasteyComReq.REQ_COMP_PASTEY_'+i+'@1' for i in ['005','007','010','011','015']], proposed_action='Plan direct pastey environment/hyphen/missing-variable checks, documentation output inspection, uppercase-boundary and applicable alias/replacement branches under the adopted verification scope; bind actual results'),
    dict(label='R5', title='Compile-fail results and trace links need outcome-specific evidence', consequence='Negative compilation success alone does not prove the intended error cause; parser limitations leave measured result trace incomplete', sources=[D+'/tests/pastey_test.rs:184', D+'/docs/component_classification.rst:236', N+'/historical-rust-and-copyright/prior-attempt/sources/communication/score/mw/com/rust/score_com_concept/interface_macros.rs:356'], native_obligations=['PasteyComReq.REQ_COMP_PASTEY_008@1'], proposed_action='Use valid surrounding syntax and bind expected diagnostic/causal checks for required rejections; supply independently reviewed requirement-to-result trace if the native parser cannot represent Rust results'),
    dict(label='R6', title='Historical copyright findings retain pending native dispositions', consequence='Unresolved historical quality evidence; source identity does not dismiss findings or establish a current checker result', sources=[N+'/historical-rust-and-copyright/copyright-findings.json', N+'/historical-rust-and-copyright/execution/auxiliary-help-storage-deviation.json'], native_obligations=[], proposed_action='Have native reviewers disposition the 204 retained findings without suppressing them; rerun the current-baseline checker only if required by a separately authorized broader readiness scope'),
]
for f in findings:
    f['label_kind'] = 'local_review_label_not_native_identifier'
    f['disposition'] = 'open_proposed_action; authorized_human_acceptance_pending'

gaps = {
    '001': 'COM uses this concatenation operation; four paste blocks and 22 occurrences verified. Six carried current-baseline integration cases exercise generated consumers. No complete crate-wide qualification claim.',
    '005': 'Upstream case tests :camel; :upper_camel alias lacks a direct case in the supplied file.',
    '007': 'my_http_server does not exercise the explicitly required consecutive-uppercase boundary.',
    '008': 'Malformed replacement compile-fail snippet has unbalanced Rust delimiters; rejection may occur before the intended pastey diagnostic.',
    '009': 'Raw identifier and non-first # cases are linked; those upstream targets were not executed. No outcome-specific diagnosis established here.',
    '010': 'The linked test asserts struct.field == 42; it does not inspect the concatenated documentation string.',
    '011': 'The linked cases use Rust builtin env! outside identifier interpolation; they do not directly exercise pastey environment lookup/hyphen normalization/missing-variable handling.',
    '015': 'The linked negative case covers multiple tokens in from, not the separate to branch.',
}
matrix = []
for record in checks['native_component_requirements']:
    suffix = record['id'].split('_')[-1].split('@')[0]
    matrix.append({**record, 'used_in_observed_COM_paste_blocks': suffix == '001', 'static_review': gaps.get(suffix, 'Requirement-linked cases present in the supplied upstream file; execution and full static adequacy are not established by this review'), 'native_upstream_targets': ['//docs/pastey/tests:pastey_test', '//docs/pastey/tests:pastey_doc_test'], 'execution_in_this_run': 'unperformed', 'qualification_disposition': 'pending_native_scope_and_outcome_evidence; no waiver'})

review = {'issue': 'eclipse-score/communication#1265', 'review_kind': 'offline_agent_engineering_review', 'review_complete': True, 'recommended_decision': 'retain_locked_pastey_0.2.3_as_proposal', 'documentation_criteria_reviewed': True, 'baseline': '8368bfb5b182ae6642d963b58ad4bac5dabc02c3', 'assessment_original_baseline': 'e3d126c2d7569345cf5f790310702eb00cd86b06', 'input_manifest_sha256': checks['input_packet_sha256'], 'human_acceptance': 'pending', 'qualification_adoption': 'not_established', 'native_status_mutations': [], 'native_tests_rerun_during_review': False, 'replacement_introduced': False, 'supervisor': '/root/rust_issue_supervisor', 'corrections_used': 3, 'max_corrections': 3, 'remaining_corrections': 0, 'findings': findings, 'requirement_matrix': matrix, 'acceptance_mapping': [{'criterion': 'Pin/features/exact patterns', 'agent_review': 'supported_by_verified_sources'}, {'criterion': 'Provenance/license/maintenance/safety relevance', 'agent_review': 'supported_as_dated_assessment; not_security_or_safety_clearance'}, {'criterion': 'Retain/replace/internal option', 'agent_review': 'retain_current_pastey_0.2.3_recommended; human_decision_pending'}, {'criterion': 'Required qualification artifacts/replacement validation', 'agent_review': 'obligations_and_gaps_recorded; no_replacement_to_validate; actual_qualification_pending'}], 'omissions': ['full_repository_CI', 'QNX', 'sanitizer_or_coverage_measurement', 'complete_ABI_layout_proof', 'current_baseline_copyright_checker', 'native_pastey_requirement_test_execution', 'exact_build_certificate', 'communication_adoption', 'human_acceptance']}
(packet/'engineering-review.json').write_text(json.dumps(review,indent=2,sort_keys=True)+'\n')

report = f'''# Communication #1265 — completed offline agent engineering review

Recommend retaining the existing locked **pastey 0.2.3** for the observed COM identifier-pasting use. The baseline already uses pastey, so this issue needs an assessment rather than another migration. The documentation criteria are addressed by the assessment plus this review addendum. Formal communication qualification/adoption and authorized human acceptance remain pending because their evidence is absent. This is a completed agent review and a proposed engineering decision.

The user requested this review with “do it you” after the Linux integration work. `/root/rust_issue_supervisor` performed an independent read-only source/assurance review. The inherited native run used all **three of three** corrective fixes; this review performed no native rerun or source repair. Agents have not granted a human decision, altered native statuses, published a PR or closed the issue.

## Scope and evidence freshness

- Reviewed integration baseline: `8368bfb5b182ae6642d963b58ad4bac5dabc02c3`.
- Original assessment and Rust unit/doctest baseline: `e3d126c2d7569345cf5f790310702eb00cd86b06`. Its header is preserved. The [deterministic review checks](deterministic-review-checks.json) freshly verify the selected macro, BUILD, module and lock bytes against both recorded baselines; this carries static facts, without promoting historical dynamic results.
- Original documentation patch SHA-256: `eb687c1a36b054315970fdbb2a4833cbb5e9470fb30eb06e67a446ca87951c19`. It remains unchanged, with two documentation paths and no production Rust/dependency/API modification.
- The complete [native verification packet]({N}/README.md) is copied byte-exact: **1,359 input subjects**, manifest SHA-256 `bb7972f22c5bd69db5dc5ade910f8f5e9785890c35738ea857d57daaa691a2c8`. The original packet stays sealed. Current review checks revalidated all 1,359 subjects before and after copying, including prior failed attempts, copyright history and packaging refusal/restoration records.
- The two selected Linux integration targets retain **six passed, zero failures/errors/skips**, with cached test results disabled in that execution. This review rechecked XML hashes, exact case names, suite counts and absence of failure elements. These are carried test results and fresh integrity checks, not a new test execution.
- The earlier **33 passed / two ignored** Rust unit/doctest cases remain historical e3d126c2 evidence. The 204 historical copyright findings remain open; all 204 reported file hashes also match the current recorded baseline. This correlation is not a current copyright checker run or a false-positive disposition. Markdown was excluded by the historical native checker templates.

Linux evidence covers production generated Rust APIs, the C++ bridge and LoLa runtime through synchronous BigData/mixed primitives/complex structs and asynchronous cancellation/receive/streaming. Consumers exit zero; the fixtures intentionally terminate producers with SIGTERM/143. BigData opaque placeholders and sample-count checks do not prove complete payload layout or every field. Full CI, QNX, sanitizers/coverage and complete ABI/layout proof remain outside the executed scope. Applicability must come from the native adopted verification plan; this review invents no blanket requirement to run them.

## Issue acceptance mapping

The [current issue](https://github.com/eclipse-score/communication/issues/1265) was observed open on 2026-10-06. Its dated API response is retained in [review evidence](review-evidence/current-issue.json).

| Issue criterion | Reviewed evidence and disposition |
| --- | --- |
| Record pin, features and exact patterns | Supported by the verified archive, native root lock/generated BUILD and source inventory: pastey 0.2.3, no features, no normal/build crate dependencies, four paste blocks and 22 uses of four suffix patterns. |
| Review provenance, license, maintenance and safety relevance | Both MIT/Apache-2.0 license texts and archive checksum are retained. The dated metadata shows pastey unarchived, last push 2026-09-29; paste archived, last push 2024-10-06. These observations establish neither security clearance nor safety acceptance. Incorrect generated identifiers/associations can produce valid but wrong target code; host macro execution also creates a build-time trust boundary. |
| Document retain/replace/internal choice | Retain locked pastey 0.2.3 recommended. Returning to archived paste adds change/qualification cost without a demonstrated benefit. An internal generator would need its own syntax, hygiene, diagnostics, consumer and qualification evidence. No option is automatically safer merely by name or ownership. |
| Record qualification artifacts and validate a replacement | Required native artifacts, conditional tool-role obligations and exact-build gaps are recorded below and in the checklist. No replacement was introduced; replacement equivalence testing is inapplicable to this documentation-only candidate. Actual qualification/adoption and human acceptance remain pending. |

The observed COM patterns are `[<$id Interface>]`, `[<$id Consumer>]`, `[<$id Producer>]` and `[<$id OfferedProducer>]`. They map to `PasteyComReq.REQ_COMP_PASTEY_001@1`. No getter/setter pasting or modifier use occurs in those four blocks. Other upstream crate requirements are outside these COM call sites; this does not waive applicable crate qualification obligations.

## Review findings and proposed dispositions

R1–R6 are local review labels, not invented S-CORE requirement or finding identifiers. Every disposition remains proposed and open for authorized native review. Full path/line anchors and impacts are in [engineering-review.json](engineering-review.json).

**R1 — Exact compiler qualification scope is missing.** The supplied AoU `PasteyAoU.PasteyRustCompilerCertified@1` requires the compiler used to build pastey to be safety certified up to ASIL B. The actual compiler version evidence reports **rustc 1.94.0-nightly, Ferrocene rolling**, commit `779fbed05ae9e9fe2a04137929d99cc9b3d516fd`, LLVM 21.1.5, selected host/target `x86_64-unknown-linux-gnu`. Fresh hashes of the materialized driver and wrapper match the historical version-report subjects. The native toolchain module selects builder release 1.3.1 and archive SHA-256 `6fd7c7053a80463b2bfd24202de02e16959b18ed185c55b738148e9caac42eff`; it also carries the existing C++/math/C linker flags. No compiler was executed in this review.

The packet lacks a certificate/qualification package tying that exact build, host/target, procedural-macro use, standard-library use and flags to the AoU. Ferrocene's [public targets guidance](https://public-docs.ferrocene.dev/main/user-manual/targets/index.html) distinguishes stable qualified releases from other releases, and compiler-use library assurance from end-use library assurance. That page is explicitly a development preview, so it corroborates the need for exact-build evidence rather than proving the status of this rolling build. We do not conclude that an unprovided custom qualification cannot exist. **Proposed action:** obtain and bind the exact qualification evidence and use-scope assessment; do not infer it from the compiler brand or six passing cases. Native source: [AoU]({D}/docs/safety_analysis/aou.trlc), [toolchain module](review-evidence/toolchain-MODULE.bazel), [version report]({N}/historical-rust-and-copyright/execution/logs/compatibility2-ferrocene.log).

**R2 — Published classification does not close adoption.** `doc__pastey_crate_comp_class` publishes status `valid`, ASIL_B, security NO and P2/C1/CLAS_OUT Q, where Q is the source's classification label “Qualified”. Its next step nevertheless requires an Accepted change request, module safety-plan adaptation and subsequent component qualification activities. `doc__mod_pastey_architecture` publishes status `valid` and realizes `wp__component_arch`. Preserve those claims exactly as upstream facts. The packet does not establish their acceptance/adoption or completed qualification for this communication use case. **Proposed action:** provide the accepted native change request, adapted safety plan, qualification work products and explicit adoption binding. Source: [classification]({D}/docs/component_classification.rst), [architecture]({D}/docs/architecture/index.rst).

**R3 — Two upstream rationale statements need clarification.** Classification line 93 excludes environment-based settings, while REQ_COMP_PASTEY_011 and the actual crate support compile-time environment lookup; line 242 also acknowledges `std::env`. Classification line 165 and architecture line 44 describe one public entry point, while archive `src/lib.rs` exposes `paste` plus doc-hidden public aliases `item` and `expr`. Runtime versus compile-time configuration and documented versus all public entry points may explain the intended scope, but those distinctions are not explicit in the rationale. **Proposed action:** obtain a source-bound clarification from native maintainers/reviewers before relying on those rationale statements; do not rewrite the published valid status or reclassify P/C/Q. Sources: [classification]({D}/docs/component_classification.rst), [implementation]({C}/src/lib.rs), [environment branch]({C}/src/segment.rs).

**R4 — Requirement annotations overstate some test observations.** The supplied upstream file contains links for all 15 ASIL B component requirements, each revision 1; their TRLC records supply no explicit lifecycle status. These are separate score-crates targets, **not executed** by the communication integration run. Static review found:

- REQ011 tests builtin Rust `env!` in a function body, not pastey's `[<env!(...)>]` identifier interpolation. Hyphen normalization and pastey's absent-variable branch are not directly exercised by those cases.
- REQ010 asserts the generated struct field equals 42; it does not inspect the concatenated documentation string.
- REQ007 uses `my_http_server`, which does not exercise the required consecutive-uppercase boundary. REQ005 exercises `:camel` without a direct `:upper_camel` alias case. REQ015 covers the multi-token `from` argument without the separate `to` branch.

These are adequacy gaps in the supplied linked tests, not observed failures in the six communication cases and not a claim that no other upstream tests exist. **Proposed action:** resolve the adopted scope and add/directly bind observations for the required behaviors in a separately authorized upstream verification effort. Source: [upstream test file]({D}/tests/pastey_test.rs), [requirements]({D}/docs/requirement/component_requirements.trlc). All 15 rows and execution dispositions are retained in the JSON review.

**R5 — Negative checks and measured trace need stronger binding.** The REQ008 malformed replacement snippet contains unbalanced delimiters, so a compile-fail result can arise from ordinary Rust parsing rather than pastey's intended diagnostic. The historical communication macro rejection doctests also use generic compile-fail checks without error-specific annotations. Such results establish rejection but cannot alone identify its cause. The published classification additionally notes that LOBSTER reports omit Rust test results because of a parser limitation. Source links without measured results do not close a qualification trace. **Proposed action:** for required rejection contracts, validate surrounding syntax and bind intended diagnostic/causal evidence; provide an independently reviewed requirement-to-result trace where parser support is missing. This is a proposed verification obligation, not authorization for a new native run. Sources: [upstream tests]({D}/tests/pastey_test.rs), [historical macro source]({N}/historical-rust-and-copyright/prior-attempt/sources/communication/score/mw/com/rust/score_com_concept/interface_macros.rs), [trace limitation]({D}/docs/component_classification.rst).

**R6 — Historical copyright dispositions stay open.** All 204 reported source hashes match both recorded baselines and are outside the documentation change. This supports “not introduced by this patch”; it does not support “harmless”, “waived”, or “current checker passed”. **Proposed action:** retain pending native dispositions and resolve them under the applicable native quality scope. Historical failed attempts and the auxiliary-help global-cache deviation remain preserved. Source: [normalized findings]({N}/historical-rust-and-copyright/copyright-findings.json).

## Qualification and trace work products

Use the [qualification checklist](qualification-checklist.md) as the concrete review queue. It records what is present, what is absent, the required binding and the proposed reviewer role. It does not check off human-owned decisions.

The component role has published classification, architecture, 15 requirement records and the compiler AoU. Runtime-free code generation can still affect target safety semantics. Whether this host generator also requires a separate native tool-management assessment remains **unresolved** without the supplied project tailoring. At the process pin `98d1d5f42dad412a09a888ea25e59c62fa6371ce`, `wp__tlm_plan` and `wp__tool_verification_report` are version-1, status-valid work-product **type definitions**, not completed communication instances. Their [native definitions](review-evidence/public-sources/tool-management-workproducts.rst), [attributes](review-evidence/public-sources/tool-management-attributes.rst) and [report template](review-evidence/public-sources/tool-verification-report-template.rst) are retained with retrieval hashes. No new native UID, confidence level, safety/security decision or qualified/released instance is fabricated. If applicable, the adopted native tool template must carry the actual identification/version, use case, confidence determination, safety/security relevance and evidence.

The external dependency rule has `--cap-lints=allow`, `manual`, `noclippy`, `norustfmt`; a clean consumer lint does not cover the dependency. Crate-wide coverage, security advisory clearance and standard-library assurance are not established by this packet. Required scope must be resolved by native policy/tailoring rather than hidden workflow policy.

## Preservation, verification and handoff

This additive review contains the complete sealed input and a new [manifest](artifact-manifest.json). Raw execution commands, stage state, XML/logs, licenses, 90-subject first fixture-failure archive, older evidence and packaging-draft refusal remain readable under `native-verification/`. Large native OCI layer bytes remain in the original bound SSD workspace; their exported descriptors/hashes are retained, so report review is portable but full image rebuild/replay requires those separately identified inputs.

Private Docker/Fabro services were already measured stopped and none was relaunched. Review scratch is bound to external SSD UUID `002B-CE31`, registered ext4 image UUID `11c42dee-73a3-4c2b-ab42-a0440011d9e0`; the shared storage guard was validated before SSD reads and evidence drafting. Stop on disconnection/remount. The explicit contributions destination is honored. Existing dirty fabric work, reference repositories and sealed native packets are preserved.

The contribution registry records **agent engineering review complete; human acceptance pending**, with submission eligibility unchanged. The six native Linux results are carried evidence for baseline 8368bfb5; integrity verification does not execute tests or confer acceptance.

Next concrete engineering input: the certificate/use-scope package for compiler commit `779fbed05...`, together with the Accepted component change request and communication adoption/safety-plan records. These allow R1/R2 to be dispositioned and the verification gaps to be planned under the actual native scope.
'''
(packet/'README.md').write_text(report)

checklist = f'''# Qualification evidence checklist — proposed native review queue

This checklist is an agent-authored review aid. It changes no native requirement/status and records no human acceptance. R1–R6 refer to local review labels in [the review](README.md). Every acceptance remains pending outside Fabro.

| Obligation / source | Supplied evidence | Missing binding / proposed next action | Proposed native reviewer role |
| --- | --- | --- | --- |
| Exact dependency and provenance | Root lock, pastey 0.2.3 archive/hash, no features/patches/normal-build dependencies, origin Git SHA, both licenses | Apply existing maintenance/security scope; no advisory or security-clearance claim | Dependency owner / security reviewer |
| Observed generated API, REQ_COMP_PASTEY_001@1 | Four suffix patterns/22 occurrences; unchanged native macro bytes; six current-baseline Linux cases | Adopt bounded consumer evidence under the native verification plan; no full ABI/layout or crate-wide coverage claim | Communication verification owner |
| Published `doc__pastey_crate_comp_class` | Status valid, ASIL_B, security NO, P2/C1/Q at score-crates pin `4656dda8...` | Accepted change request, adapted safety plan, performed qualification activities and communication adoption (R2); clarify rationale (R3) | Component owner / safety reviewer |
| Published `doc__mod_pastey_architecture` → `wp__component_arch` | Valid published architecture, source-bound generator role | Adopt version/use case and clarify public-entry-point criterion (R2/R3) | Architecture owner |
| `PasteyAoU.PasteyRustCompilerCertified@1` mitigates `UncertifiedRustCompiler` | Exact driver/wrapper identities, rolling/nightly version, builder URL/hash, Linux host/target and native flags | Exact-build ASIL-B certificate/qualification package and applicable proc-macro/library/host-target/configuration scope (R1) | Compiler qualification / safety owner |
| 15 `PasteyComReq.REQ_COMP_PASTEY_001..015@1` records | Revision 1, ASIL B, supplied trace comments; no explicit lifecycle status in TRLC records | Determine adopted scope and complete requirement-to-observation/results mapping; annotations alone are insufficient (R4/R5) | Requirement / verification owner |
| Native `//docs/pastey/tests:pastey_test`, `:pastey_doc_test` | Native BUILD and source retained | Targets were not run here; address direct observations and negative-case causality, then obtain measured results in separately authorized work (R4/R5) | score-crates verification owner |
| Rust result trace | Native classification acknowledges LOBSTER parser limitation | Reviewed bound trace to actual execution results; no fabricated “closed” result links (R5) | Traceability owner |
| Host generator tool role, conditional | Pinned native process type definitions/templates retained | Project tailoring must determine applicability; if applicable, actual tool-management instances, confidence/safety/security decisions and validation evidence | Tool-management owner |
| Copyright/quality obligations | 204 historical findings; all current recorded file hashes match; Markdown excluded by checker templates | Native dispositions stay pending; current checker scope not executed (R6) | Native quality owner |
| Authorized decision / communication adoption | Completed agent review recommends retaining pastey; read-only supervisor review | Authorized offline acceptance with actual identity/date/source binding; never derive from tests or workflow success | Authorized engineering decision owner |

## Conditional tool-management draft inputs

The pinned native process defines `wp__tlm_plan` and `wp__tool_verification_report` at version 1/status valid. These are type definitions. The retained template's example UID, LOW confidence and YES safety/security attributes are placeholders, not communication determinations. No project instance is created here.

If tailoring makes this generator subject to tool management, proposed inputs for the real native report are: pastey 0.2.3; host procedural-macro expansion; token streams as input; generated Rust identifiers/items as output; archive/root-lock hashes; Linux host and selected target; certified-compiler assumption; generated wrong-but-compilable association failure mode; build-time environment lookup and trust boundary; consumer compilation/runtime checks and their limits; the open R1–R5 evidence gaps. Actual UID, confidence, safety/security flags, applicability and status belong to the native authorized process.

## Bound execution and historical evidence

Current Linux target/case/result bindings are in [deterministic checks](deterministic-review-checks.json). Historical Rust 33-pass/two-ignore results stay on e3d126c2. No replacement, full CI, QNX, sanitizer/coverage or current copyright execution is claimed. No native run remains active. Max three corrections are exhausted; this checklist does not authorize another recovery.
'''
(packet/'qualification-checklist.md').write_text(checklist)
(packet/'review-evidence/supervisor-review.md').write_text('''# Independent read-only supervisor review

Agent: `/root/rust_issue_supervisor`. Scope: offline assurance/source review; no builds, edits to native sources or recovery attempts. Agent recommendations are proposed dispositions, not human acceptance.

Supervisor reported that all 1,359 input subjects verify without hash drift and recommended retaining locked pastey 0.2.3 as a proposal. It verified published classification/architecture claims while preserving pending adoption; the exact compiler AoU; lack of explicit lifecycle status in all 15 TRLC component records; the environment/docstring/uppercase/replacement test-adequacy gaps; and the environment/single-entry-point rationale conflicts. The root agent independently inspected those source sections and retained them in R1–R5. The supervisor also confirmed that the six Linux cases are focused consumer/runtime evidence and that historical Rust tests do not establish fresh crate qualification or human acceptance.

This is a faithful summary of the agent's review messages. The completed export's hash binding will be independently checked before registry selection.
''')
(packet/'review-evidence/write_review.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'review': str(packet/'README.md'), 'local_findings': len(findings), 'native_requirement_rows': len(matrix), 'acceptance': 'pending_authorized_human'},indent=2))
