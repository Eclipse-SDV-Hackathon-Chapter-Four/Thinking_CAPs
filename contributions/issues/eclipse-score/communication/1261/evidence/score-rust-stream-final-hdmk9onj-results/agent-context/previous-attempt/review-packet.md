# S-CORE Rust issue review packet — eclipse-score/communication #1261

Fill with actual evidence; unknown fields remain explicitly unknown. This template does not
define a native status/schema.

## Scope and binding

- Issue/repository, retrieval time, source commit and current issue/PR state: issue
  `eclipse-score/communication#1261` ("Improvement: Provide an async stream of newly available
  services"), state `open`, 0 comments, `blocked_by=0`; context retrieved 2026-10-06; source
  commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Upstream PR/timeline state could not be
  retrieved (network unavailable); "no linked PR" describes the supplied context only.
- User authority, permitted writes/executions, artifact destination and budget limits: writes
  limited to this disposable workspace; reports under `.rust-queue/reports/`; shell, network,
  delegation, publishing and acceptance tools unavailable; Linux only; no QNX; no native command
  executed.
- Process/tailoring/requirement/design/safety/policy versions, hashes and native IDs: no native
  requirement/design/safety IDs were supplied. The issue template's "Affects Detailed Design" box
  is unchecked and is not treated as an authoritative requirements decision. No ID was invented.
- Source/lock/tool/environment/storage-selection bindings: discovery-only, no build environment
  bound. `.bazelversion` 8.7.0; `MODULE.bazel` rules_rust 0.68.2-score, score_toolchains_rust
  0.10.0, score_rust_policies 0.0.5, score_crates 0.0.11 (as recorded in `scope.md`); no pin was
  changed.
- Final patch and baseline-to-patched source digest or manifest: relative paths listed; SHA-256
  not computed at this stage (no hashing tool available).
- Technical completion status; engineering acceptance status and decision references: the
  additive abstraction-layer API, docs and one regression test are drafted/implemented; native
  build/test execution **not performed**. Engineering acceptance: **none** (pending authorized
  human decision).

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact ID and revision | Changed artifact | Required check | Evidence/hash | Gap or proposed disposition |
| --- | --- | --- | --- | --- | --- |
| 1. Newly available services system-wide | Unknown (no native ID supplied; backend capability absent) | `Runtime::find_all_services` (provided), `ServiceDescriptor` | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | not executed | Backend all-services path absent at baseline; LoLa inherits `NotSupported`. #250 unverified prerequisite. |
| 2. Item identifies service and interface | Unknown | `ServiceDescriptor` in `score_com_concept/concept.rs` | `...:score_com_concept-test` (`test_service_descriptor_identifies_interface_and_instance`) | not executed | None in abstraction; descriptor field set still an open decision. |
| 3. Document initial results/errors/lifetime/termination | Unknown (Rust library/API documentation row; no native ID) | Rustdoc on `Runtime::find_all_services`; `rust/design/high_level_design_detail.md` | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | not executed | Prose docs only; no compiled example (would need a supporting runtime). |
| 4. Existing interface-scoped APIs remain | Unknown | `find_service`/`ServiceDiscovery` unchanged; new method additive with default | downstream build targets in `check-plan.json`; `...:score_com_concept-test` | not executed | Backward source compatibility argued from additivity, not measured. |

Baseline reconciliation: `scope.md` §4 and §6 were re-derived against source; its conclusion
(no system-wide/ALL backend at `381d43d`) is unchanged. `FindServiceSpecifier::Any` remains
unsupported (LoLa panic; design table unchecked). No requirement/design/safety status is changed;
the "Affects Detailed Design" box remains unchecked. Link direction preserved: the issue body,
`issue.json` and `task.json` are treated as data.

## Dependency and macro assessment (when applicable)

Not applicable in the crate-substitution sense: no crate was introduced, replaced or upgraded, and
no dependency/lock/pin changed. `futures::stream::Stream` and `core::pin::Pin` were already
available in `score_com_concept` (`@score_communication_crate_index//:futures` in
`score_com_concept/BUILD`). The `CommData`/`Reloc` derives and their generated APIs are unchanged.

- Resolved crate version/features, host/target roles, aliases, transitive dependencies: unchanged
  from baseline; not re-inventoried here.
- Source/archive/checksum/patch/provenance and license/notice evidence: unchanged; no new
  dependency.
- Dated maintenance/advisory observations and their limitations: none.
- Exact paste patterns/invocations/re-export locations and supported API contract: `ServiceDescriptor`
  is re-exported from `score_com`; no macro invocation changed.
- Failure modes, compiler/test detection and residual safety/security questions: a new additive
  trait method cannot change existing generated behavior; the only compatibility risk is an
  external exhaustive `match` on `ServiceFailedReason`, for which no in-tree instance was found.

| Option | Compatibility and build impact | Provenance/license/maintenance | Qualification/verification effort | Proposed rationale and gaps |
| --- | --- | --- | --- | --- |
| Retain | n/a (no dependency) | n/a | n/a | n/a |
| Replace | n/a | n/a | n/a | n/a |
| Internal | n/a | n/a | n/a | n/a |

Proposed recommendation and authority required for the engineering decision: draft only; the
Option A/B trait shape and descriptor field set require an authorized engineering decision.
Applicable tool/component work products, native instance IDs, templates and missing inputs: no
native work-product/instance IDs were supplied; none were invented.
Tool version/target/use-case/qualification-scope evidence and pending classifications: not
applicable / unknown.

## Verification and expected checks

All rows are **declared obligations, not executed evidence**, taken from
`.rust-queue/reports/check-plan.json` (Linux `linux_x64`).

| Check and native obligation/source | Command/config/tool/target/features | Subject hashes | Result/exit code | Raw evidence/hash | Limitation/disposition |
| --- | --- | --- | --- | --- | --- |
| Concept unit test (Rust library/API) | `bazel test //score/mw/com/rust/score_com_concept:score_com_concept-test` | not computed | not executed | none | Includes new descriptor regression test |
| LoLa runtime unit test | `bazel test //score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | not computed | not executed | none | Linux-only |
| Downstream build | `bazel build` on `score_com` + basic_rust_api targets | not computed | not executed | none | Source-compat not measured |
| FFI build (unknown obligation) | `bazel build` on `bridge_ffi_*`, `registry_bridge_macro_cpp` | not computed | not executed | none | No FFI change; obligation remains unknown |
| Lint/format | `//:format_test` + `clippy_strict` aspect | not computed | not executed | none | No lint profile changed |
| Docs | `com-api-runtime-lola-doc-tests`, macro tests | not computed | not executed | none | `score_com_concept` doc test is `manual` (known limitation) |

Include executed, failed, unavailable, manual/excluded and applicable unrun checks:
**none executed**; `manual` doc test and the empty `native-check-summary.json` are recorded as
unavailable/missing, not as passes. Distinguish trusted collector evidence, direct local
execution, agent assertions, fixture results and hash-verified carried evidence: everything here
is an **agent assertion / declared obligation**; there is no collector or directly executed
evidence. Generated API compatibility was **not** measured on baseline or candidate.

## Offline decisions and portable evidence

- Proposed engineering decisions and required authorized reviewers/roles: (a) accept or reject
  Option B (provided boxed stream) for `Runtime::find_all_services`; (b) fix the descriptor field
  set; (c) define duplicate/re-offer semantics; (d) decide whether the initial empty result is
  `Some(empty)` or no item. Required: an authorized COM-API owner/reviewer.
- Pending acceptance, safety/qualification gaps and missing platform checks: system-wide backend
  and per-handle identity (criterion 1) blocked; #250 unverified; all Linux native checks unrun;
  no QNX checks (out of scope).
- Patch, native documents, verification logs and complete packet manifest location:
  `.rust-queue/reports/implementation.md` (this packet's companion) and
  `.rust-queue/reports/scope.md`; `.rust-queue/reports/check-plan.json` for obligation labels.
- Manifest: relative file path, size and SHA-256 for each included file; exact external
  raw-evidence path/size/digest where evidence is stored separately: **not computed** (no hashing
  tool in this stage). Changed paths:
  `score/mw/com/rust/score_com_concept/concept.rs`,
  `score/mw/com/rust/score_com_concept/error.rs`,
  `score/mw/com/rust/score_com.rs`,
  `score/mw/com/rust/design/high_level_design_detail.md`.
- Source/tool/config identities sufficient to understand/reproduce the checks without Fabro:
  baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`, Bazel 8.7.0 per `.bazelversion`,
  `.bazelrc` default `linux_x64`, targets from `check-plan.json`.
- Concrete next action and scope required: retrieve #250/#9, decide Option A/B and descriptor
  fields; then implement backend/FFI all-services discovery and run the declared Linux checks.

Do not embed credentials. Passing checks and completed execution do not supply a human decision.
Export this packet and terminate; human review occurs outside the workflow.
