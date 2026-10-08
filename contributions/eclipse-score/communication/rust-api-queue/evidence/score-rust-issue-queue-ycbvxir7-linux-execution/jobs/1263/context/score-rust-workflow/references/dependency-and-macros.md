# Rust dependency and generated API assessment

Read for crate introduction/replacement, procedural macros or build-time generation.
A host-executed generator can affect safety-relevant target code; absence from runtime
does not establish irrelevance. Separate its generator/tool role from generated/runtime
software-component roles, and resolve each under the supplied native process/tailoring.

## Inventory the actual dependency

Record crate name/version, enabled and default features, direct/transitive usage,
host/target role, edition/MSRV compatibility, registry/source URL, resolved checksums,
source revision, patches, native aliases/re-exports and lock/module hashes. MODULE may
pin a crate-index module rather than an individual crate. Follow the resolved index and
its generated manifests/locks/BUILD files; an alias is not a version or feature inventory.
Check feature unification and host/target configuration separately where applicable.

Inspect source archive and license/notice texts, not just registry metadata. Record
provenance and archive digest, transitive licenses, owner/maintainer/release activity,
documented support and relevant advisories with retrieval time. An archived repository,
fork relationship or shared name alone proves neither insecurity nor suitability.
If relying on a fork, inspect actual code/version differences and provenance.

## Identify failure modes and native obligations

Explain how incorrect generation could create wrong identifiers, missing/wrong API
members, type/trait mismatches, erroneous access paths or behavior. Identify what the
compiler/tests detect and what could compile while remaining semantically wrong.
Assess build-script/procedural-macro execution trust and supply-chain exposure alongside
runtime consequences. Tool confidence/safety/security classification and applicability
are human engineering decisions; draft their rationale and preserve unknowns.

At the fabric's process pin `98d1d5f42dad412a09a888ea25e59c62fa6371ce`, native work
products `wp__tlm_plan` and `wp__tool_verification_report` are version 1/status `valid`.
These are type definitions, not completed project instances. If applicable, draft in
the native tool-management template, preserve its UID/version/status/confidence and
safety/security attributes, and bind validation evidence to the selected tool/use case.
Do not mark instances evaluated/qualified/released or supply a confidence decision.
For library/component roles, discover the additional native work products/requirements;
do not relabel every crate a tool or assume the tool report covers its runtime use.

## Compare alternatives

| Option | Questions to answer with evidence |
| --- | --- |
| Retain current crate | Exact required functionality, maintenance/provenance/licensing risks, qualification gaps and practical mitigations |
| Replace with another crate | Semantic/source compatibility, supported compiler/target/features, provenance changes, transitive dependencies and qualification burden |
| Implement limited functionality internally | Precisely bounded syntax, design/testing/maintenance responsibility, macro hygiene/diagnostics and native qualification implications |

Record each option's API risk, build/lock changes, verification plan and unresolved
engineering decisions. A replacement is not safer merely because maintained; internal
code does not eliminate qualification obligations. Recommend a scoped option, and implement
only where task authority permits. Do not migrate again if the baseline already changed.

## Validate generated API compatibility

Inventory every invocation/re-export and exact paste operation with source locations.
Capture the supported syntax actually used: suffix/prefix composition, accessor names,
case conversion, raw identifiers and hygiene only where used or part of the public contract.
Distinguish examples in an issue from observed implementation behavior.

Establish baseline and candidate checks for exported names, visibility, generics/lifetimes,
trait/associated-type relationships, interface IDs and signatures, plus behavior delegated
by generated methods. Exercise public downstream use through re-exports, custom IDs,
supported legacy syntax, multiple modules and relevant boundary cases. Preserve rejection
behavior for unsupported invocations using the repository-supported negative test route.
Avoid inventing support for fields/methods or syntax that the macro deliberately rejects.

Use real downstream compilation/tests as primary compatibility evidence. Compare macro
expansion only with a supported pinned tool; textual equality is insufficient by itself.
Expected-error tests must fail for the intended reason. Retain old/new API evidence,
build/lint/docs outcomes, missing checks and the exact patch/dependency/policy/tool hashes.

## Source anchors

- [Tool-management work products](https://github.com/eclipse-score/process_description/blob/98d1d5f42dad412a09a888ea25e59c62fa6371ce/process/process_areas/tool_management/tool_management_workproducts.rst).
- [Native report attributes](https://github.com/eclipse-score/process_description/blob/98d1d5f42dad412a09a888ea25e59c62fa6371ce/process/process_areas/tool_management/guidance/tool_management_reqs.rst).
- [Native tool-verification template](https://github.com/eclipse-score/process_description/blob/98d1d5f42dad412a09a888ea25e59c62fa6371ce/process/folder_templates/tools/tool_verification_report_template.rst).
