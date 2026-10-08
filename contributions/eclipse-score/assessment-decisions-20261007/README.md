# Qualification and adoption decisions for retained assessments

The assessments support reviewable proposals, with qualification, adoption and human acceptance pending. Retain locked pastey 0.2.3 for the observed Communication use, subject to the evidence below. Keep thiserror and futures unchanged while their applicability and dependency records are completed. No entry in this packet contributes a completed-fix claim.

Prepared on 2026-10-07 for the contribution owner and authorized native reviewers. [Decisions](decisions.json) records ten entries: six Communication assessments, two adjacent upstream-owned/unimplemented entries, and two S-CORE evaluation proposals. Reviewer roles are routing proposals; actual authority and accepting identities remain unassigned.

## Scope and evidence binding

The selected baselines and local statuses come from [the frozen registry selection](registry-selection.json). Communication #1265 uses integration baseline `8368bfb5b182ae6642d963b58ad4bac5dabc02c3`; its original assessment and unit/doctest evidence use `e3d126c2d7569345cf5f790310702eb00cd86b06`. Other Communication entries use `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. The S-CORE entries retain separate implementation and native-document baselines in the selection.

[Upstream retrievals](upstream/retrievals.json) bind fresh issue bodies, comments and timelines for all ten entries, related PRs #3140/#3307, score-crates #42, and current repository heads. Initial public-API rate-limit failures are retained alongside successful authenticated read-only recovery. Credentials are excluded. All ten issues were observed open; #3307 remains a draft and neither inspected PR is merged. An unmerged PR's `merge_commit_sha` is not a merged revision.

Current Communication main is `c77751819b8885a902540dbef7f0fe25cf85d51c`; current S-CORE main is `f42e760912e5f99e0db993de717155cc85679f6c`. These differ from selected evidence baselines. Results below apply to their recorded subjects. Reconcile source, lock, configuration and tool identities before using them for a different revision.

Original assessments, sealed packets, failed attempts and manifests remain at their existing repository paths. [Input bindings](input-bindings.json) pins each selected record, report, native obligation and evidence manifest by relative path, size and SHA-256. [The packet manifest](artifact-manifest.json) seals the new deliverable. This packet can be reviewed offline with the referenced repository artifacts.

## Proposed decisions and required inputs

| Entry | Proposed disposition | Required evidence or decision | Proposed reviewer role |
| --- | --- | --- | --- |
| [Communication #1265](../communication/1265/engineering-review/score-rust-engineering-review-kohskpez/README.md) | Retain locked pastey 0.2.3 for the four observed identifier suffix patterns; formal adoption pending | Exact compiler qualification/use scope; Accepted component change request and adapted Communication safety plan; R1–R6 dispositions and accepted verification scope | Communication dependency owner, compiler qualification owner, safety and verification reviewers |
| [Communication #173](../communication/173/README.md) | Use as the umbrella dependency inventory and decision trace; evaluate each crate separately | Complete resolved transitive inventory and licenses/advisories; link individual #1263/#1264/#1265 decisions; accepted applicability and adoption records | Communication dependency and safety owners |
| [Communication #1264](../communication/1264/README.md) | Retain assessed thiserror 2.0.21 provisionally; compare manual traits only if policy or evidence warrants change | Host macro versus target library applicability; transitive provenance; public Display/Error/source contract decision and direct behavior observations; remaining lint scope | Rust API owner, dependency and verification reviewers |
| [Communication #1263](../communication/1263/README.md) | Retain assessed futures 0.3.34 provisionally; treat reduction to narrower crates as a separate change proposal | Complete transitive closure beyond the twelve named archives; license/advisory dispositions; Stream compatibility and AtomicWaker wake/cancel/callback evidence; independent review | Async runtime/API owner, dependency and verification reviewers |
| [Communication #782](../communication/782/README.md) | Align with the existing Method backend discussion before selecting an implementation scope | Agreed milestone, C++ backend/FFI contract and sync/async strategy; source-bound implementation and verification plan | Communication Method and backend owners |
| [Communication #1062](../communication/1062/README.md) | Derive Rust E2E behavior from the agreed C++ API and permitted implementation basis | Accepted C++ design, wire-layout/error/profile/coverage scope, documented permitted licensing basis and Rust verification obligations | E2E architecture owner and native licensing reviewer |
| [Communication #794](../communication/794/README.md) | Retain the upstream-work observation; resolve the remaining manual doctest through its native build owner | Native rust_doc_test dependency support and actual executed doctest results, including exclusions | Rust build/test owner |
| [Communication #741](../communication/741/README.md) | Keep not implemented; the boundary probe supplies no relocation evidence | Actual move/delete and BUILD/tutorial updates, affected native builds and queries, owner review | Tutorial and Rust build owners |
| [S-CORE #3115](../score/3115/decision-record.md) | Review the bounded pilot supplement within the existing proposed native decision record | Agreement with #3140 owners, comparative pilot thresholds/results, current native docs CI and adoption/qualification scope | Infrastructure decision-record owners and tooling reviewers |
| [S-CORE #2850](../score/2850/acceptance-mapping.md) | Evaluate retrieval as a scoped foundation for the harness | Deterministic AssuranceHarness.get_context adapter, authorized task-scoped sources, Lane A native gates and acceptance mapping; maintainer agreement | Assurance harness and documentation owners |

The [fresh #1265 maintainer comment](https://github.com/eclipse-score/communication/issues/1265#issuecomment-5979399509) confirms existing pastey usage and distinguishes supporting artifacts from qualification or certification. Closure of score-crates #42 supplies supporting work products; each integrator's adoption remains a separate decision. This distinction also applies to the published classification's valid/P2/C1/Q labels.

## Refreshed named dependency inventory

The later #173 evidence supplies twelve named crate archives with source/license metadata and generated Bazel feature configuration. [The dependency inventory](dependency-inventory.json) carries those facts, including archive checksums, from the bound original records. This resolves the original #1263 root-version gap and part of #1264's missing provenance evidence; the complete transitive closure and its review remain open.

| Dependency | Resolved version | Generated enabled features | Published crate license |
| --- | --- | --- | --- |
| pastey | 0.2.3 | none | MIT OR Apache-2.0 |
| thiserror | 2.0.21 | default, std | MIT OR Apache-2.0 |
| thiserror-impl | 2.0.21 | none | MIT OR Apache-2.0 |
| futures | 0.3.34 | alloc, async-await, default, executor, futures-executor, std | MIT OR Apache-2.0 |

Generated optional-dependency feature names differ from declared Cargo feature tables; both are preserved in the JSON. Named archive/license evidence is not complete closure acceptance or advisory clearance. The final #173 supervisor also identifies a direct `syn 2.0.119` derive-macro dependency separately from `syn 3.0.6`; the latter must not be assumed to represent the entire closure.

## Communication 1265 qualification and adoption proposal

Retain the existing source and lock without a migration. The [completed agent review](../communication/1265/engineering-review/score-rust-engineering-review-kohskpez/engineering-review.json) and [qualification checklist](../communication/1265/engineering-review/score-rust-engineering-review-kohskpez/qualification-checklist.md) supply the bounded comparison and native anchors. Returning to paste or introducing an internal generator would add compatibility and qualification work without a demonstrated benefit in the assessed use.

| Review finding | Evidence required for disposition | Acceptance condition |
| --- | --- | --- |
| R1 exact compiler | Qualification/certificate package for compiler commit `779fbed05ae9e9fe2a04137929d99cc9b3d516fd`, rolling rustc 1.94.0-nightly; host/target, flags, procedural-macro and library-use scope | Authorized compiler/safety owner demonstrates applicability to `PasteyAoU.PasteyRustCompilerCertified@1`, or records an approved alternative and its verification obligations |
| R2 component adoption | Accepted change request, adapted Communication safety plan, qualification work products, version/use-case binding | Native component/safety owner accepts adoption for this Communication configuration |
| R3 rationale | Source-bound clarification of compile-time environment lookup and documented versus doc-hidden public entry points | Authorized reviewer resolves the classification/architecture rationale without inferring a status change |
| R4 requirement coverage | Adopted scope for `PasteyComReq.REQ_COMP_PASTEY_001..015@1`; direct observations for the listed gaps and native score-crates target results | Required behavior maps to reviewed observations and measured results; supporting annotations alone remain insufficient |
| R5 rejection and trace | Valid negative-case surrounding syntax, intended diagnostic evidence, requirement-to-result trace addressing the Rust LOBSTER limitation | Verification/trace reviewer accepts causal rejection evidence and the measured trace |
| R6 copyright | Native dispositions for 204 historical findings and the adopted current checker scope | Quality owner records actual dispositions; unchanged subject hashes establish only that the documentation patch did not introduce the findings |

Generator tool-management applicability remains an explicit tailoring decision. The process pin `98d1d5f42dad412a09a888ea25e59c62fa6371ce` defines `wp__tlm_plan` and `wp__tool_verification_report` v1/status valid as types. If applicable, the native owner must instantiate the adopted template with actual identity/version, use case, confidence, safety/security attributes and bound validation evidence. No local decision label in this packet is a native work-product UID.

The immediate input is the exact compiler qualification package plus the Accepted change request and adapted safety plan. Until supplied and reviewed, formal qualification/adoption stays pending. The previous #1265 runtime's three correction slots remain exhausted; a new native verification effort needs its own explicit scope and task authority.

## Verification dispositions

| Evidence | Measured scope at its original execution | Disposition for this decision packet |
| --- | --- | --- |
| #1265 Linux integration | Six passed; zero failures/errors/skips at 8368bfb5 | Carried evidence for the two selected targets; no full ABI/layout, QNX or full CI result |
| #1265 earlier Rust/copyright | 33 passed, two ignored; 204 copyright findings at e3d126c2 | Historical evidence; ignored cases and findings remain open |
| #173 refreshed checks | 39 child cases passed, two ignored; two selected library Clippy reports with zero findings at 381d43de | The final supervisor establishes matching source vectors for eight queue workspaces, including #1263/#1264/#1265; reuse covers only its four selected groups at that queue baseline, without promoting earlier #1265 results or applying the carry to 8368bfb5 |
| #1264 original plan | Seven of eight check groups exit zero; lint blocked by duplicate clippy_strict aspect | Preserve the blocked attempt. Later #173 library lint can supply only its matching two-library scope; it does not satisfy every original lint target or Display behavior observation |
| #1263 original plan | Selected tests passed; four lint groups blocked; no original supervisor report | Later #173 evidence resolves named archive/version provenance and supplies limited check carry, while issue-specific independent review, complete closure inventory and wake/cancellation adequacy remain open |
| #741 relocation probe | Query checks failed with missing tutorial package | No implementation or acceptance evidence |
| #3115 native document checks | Proposed DR leaves 925 existing needs unchanged; inherited docs failure retained | Proposed document and historical/baseline comparison only; current PR acceptance and native CI remain separate |
| #2850 adapter | Existing chatbot checks and historical release evidence | Native deterministic adapter and harness conformance remain unbuilt |

Direct checks in this task verify retained hashes, packet coverage, links and pending-decision fields. Native tests were not rerun. Whole-closure advisories/security clearance, QNX, full CI and complete qualification are unresolved where applicable; the adopted native plan must assign scope and reasons for exclusions. No blanket applicability is inferred.

## Record an authorized decision

Use [the acceptance record template](acceptance-record-template.json) to create a separate dated record for each adopted decision. All template decision, identity, authority, date, evidence and native-record fields start empty; the template records no acceptance.

The accepting person must identify their native authority, the selected baseline/dependency/configuration, the decision (accepted, rejected or deferred), its bounded scope, each finding's disposition, and immutable evidence/native record references. Acceptance of an assessment's documentation is distinct from dependency adoption, qualification and completed implementation. Partial or deferred decisions must keep the remaining obligations open.

Record real decisions outside the frozen packet, retain their original evidence, then update contribution metadata for the scope actually accepted. An accepted documentation assessment still supplies no completed-fix claim. Reconcile new baselines and capture affected checks before changing readiness or qualification status.

## Review order and offline verification

1. Confirm reviewer authority and whether the selected baselines are the intended adoption subjects.
2. Provide #1265 compiler/adoption records and resolve native tool/component tailoring.
3. Complete #173's dependency closure and the separate thiserror/futures decisions; scope any additional verification before execution.
4. Obtain owner decisions for Method/E2E, tutorial/doctest and harness/tooling proposals using their existing native discussions.
5. Bind actual decisions using separate acceptance records and reconcile inventory status without adding assessment entries to completed-fix counts.

From the repository root:

```bash
python3 contributions/eclipse-score/assessment-decisions-20261007/verify.py
python3 contributions/shared/scripts/verify_contributions.py --json
```

The first command checks this packet and its relative input bindings; the second checks all registered retained evidence. [Verification receipt](verification.json) records the packet checks. Neither command grants engineering acceptance.
