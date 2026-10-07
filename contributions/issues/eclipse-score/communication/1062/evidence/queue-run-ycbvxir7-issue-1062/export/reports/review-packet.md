# S-CORE Rust issue review packet — issue 1062

## Scope and binding

- **Issue/repository**: eclipse-score/communication#1062 (open, label `rust-api`, no milestone).
  Latest supplied comment `updated_at 2026-09-11T14:36:07Z`.
- **Retrieval time/current state**: Live GitHub/PR state could **not** be retrieved — `web_fetch`
  to the GitHub API was blocked this session. Current issue/PR activity is **unknown**; only the
  offline `.rust-queue/context/{issue.json,comments.json,task.json}` snapshot is available.
- **Source commit**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (baseline from `task.json`).
- **User authority / permitted writes / executions**: disposable workspace only; reports under
  `.rust-queue/reports/`. Shell, delegation, publishing and acceptance tools blocked; network
  blocked; source reads bounded to 200 lines; Linux only; no QNX.
- **Process/tailoring/requirement/design/safety/policy versions**: native requirement IDs read from
  `score/mw/com/dependability/requirements/**/*.trlc` and
  `assumed_system/assumed_system_requirements.trlc` (e.g. `Communication.FEAT_Method@1`,
  `FEAT_Field@1`, `FEAT_EventType@1`, `FEAT_SafeCommunication@1`, `FEAT_DataCorruption@1`,
  `FEAT_CommunicationASILLevel@1`, `FEAT_ErrorHandling@1`, `ASR_SafeCommunication@1`). No E2E
  requirement exists. Fabric/process pins were not supplied in this workspace.
- **Source/lock/tool binding**: `MODULE.bazel` declares Bazel modules incl. `rules_rust 0.68.2-score`;
  `.bazelrc` default `--config=linux_x64_gcc_15` selects GCC 15.2.0 + Ferrocene
  `ferrocene_x86_64_unknown_linux_gnu`; static-analysis config selects
  `@score_rust_policies//clippy:linters.bzl%clippy_strict`. Tool qualification for the selected
  target is **not** established by this workflow.
- **Final patch / digests**: **no source patch** (design-mode). Source unchanged. File hashes were
  not computable (shell blocked); see `evidence-status.json`.
- **Technical completion vs acceptance**: technical design-analysis deliverable complete;
  **engineering acceptance not claimed**.

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact ID and revision | Changed artifact | Required check | Evidence/hash | Gap or proposed disposition |
| --- | --- | --- | --- | --- | --- |
| "Not designed yet … design discussion before implementation" | none (design mode) | `e2e-design-draft.md` (draft) | review by authorized engineers | this packet | No accepted design; cannot implement (OD-1..OD-3, OD-7) |
| Align with C++ E2E mechanism "if any" | C++ E2E API not published | `e2e-design-draft.md` §3 | await C++ API | comment 5634513270 | Blocked external dependency (OD-4, OD-8) |
| Add E2E for Rust Method/Field (and Event) | `FEAT_Method@1`, `FEAT_Field@1`, `FEAT_SafeCommunication@1` (proposed trace) | none | build/test/lint/docs per `check-plan.json` | none (not executed) | Rust Method/Field API absent; macro rejects them (OD-6) |
| Estimates TBD | — | — | — | — | Requires accepted design + prerequisites |
| Requirements/Architecture affected? | template checkbox unchecked | none | requirements review | issue body | Requires decision (OD-7) |
| No unaccepted safety/engineering decision implemented | — | none (no code) | — | this packet | Decision points exported in `open-decisions.json` |

Baseline reconciliation: the issue premise ("E2E protection for Rust Method/Field APIs") does **not**
match an existing baseline surface — neither E2E nor Method/Field Rust APIs exist. The existing
Event API and the C++ method design are adjacent but unaffected. Requirement/design/safety impact is
proposed, not accepted.

## Dependency and macro assessment (applicable: `interface!` macro + FFI bridge)

- **Macro contract**: `interface!` supports only `Event<T>`; `Method<T>`/`Field<T>` arms emit
  `compile_error!` (`interface_macros.rs:110-122`); negative doctests assert rejection.
  `references/dependency-and-macros.md` explicitly says: avoid inventing support the macro
  deliberately rejects.
- **Generated API surface**: `interface_common!`/`interface_consumer!`/`interface_producer!` generate
  `*Interface/*Consumer/*Producer/*OfferedProducer`; `score_com.rs:137-142` re-exports only Event
  concepts. No paste invocation for methods/fields.
- **Failure modes to guard**: wrong/missing E2E members, type/trait mismatches, buffer
  size/layout drift between Rust and C++ `CreateDataTypeSizeInfoFromTypes` (Method), and
  error-class divergence from C++.
- **Options table** (design-stage, no code change):

| Option | Compatibility and build impact | Provenance/license/maintenance | Qualification/verification effort | Proposed rationale and gaps |
| --- | --- | --- | --- | --- |
| Retain current crate/API | No break; no E2E | Existing Apache-2.0 baseline | New E2E checks needed | Insufficient for issue goal alone |
| Replace (adopt C++ E2E API) | Depends on C++ buffer/error contract | Maintainer-provided, license-clean | Joint Rust/C++ verification | Recommended direction, blocked on OD-4 |
| Implement internally | Bounded to accepted design only | Must avoid AUTOSAR-spec license conflict | Full new qualification burden | Not viable until design accepted (OD-8) |

Proposed recommendation (not a decision): wait for the C++ E2E API, land Rust Method/Field first,
then adopt the C++-aligned mechanism. Authority required: maintainers/architecture reviewers.

## Verification and expected checks

| Check and native obligation/source | Config/target (BUILD-derived) | Subject hashes | Result/exit code | Raw evidence | Limitation/disposition |
| --- | --- | --- | --- | --- | --- |
| Build abstraction/API | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/rust:score_com` | baseline `381d43d` | **not run** (design mode) | none | Command stages outside agent authority |
| Build FFI/bridge | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola`, `...:bridge_ffi_rs`, `...:bridge_ffi_lola`, `//score/mw/com/rust/score_com_cpp_bridge:register_interface` | baseline | **not run** | none | See `check-plan.json` |
| Unit tests | `...:score_com_concept-test`, `...:score_com_concept-macros-unit-tests`, `...:com-api-runtime-lola-tests` | baseline | **not run** (Linux-only per `target_compatible_with`) | none | `score_com_concept-macros-tests` is `manual` and excluded from wildcards |
| Integration (Event) | `.../consumer_sync_apis/integration_test:test_com_api_sync`, `.../consumer_async_apis/integration_test:test_com_api_async` | baseline | **not run** | none | No Method/Field E2E test target exists — explicit unknown |
| Docs | `//docs/sphinx:sphinx_doc`, `...:com-api-runtime-lola-doc-tests` | baseline | **not run** | none | — |
| Lint | same Rust targets under `--config=clippy` (`clippy_strict`) | baseline | **not run** | none | Preserve native lint policy |
| Query | roots `//score/mw/com/rust:score_com`, `//score/mw/com/rust/score_com_concept:score_com_concept` | baseline | **not run** | none | Downstream denominator not measured |

No executed checks, no collector evidence, no fixture results. All rows above are planned checks
(see `check-plan.json`), not results. `native-check-summary.json` was absent.

## Offline decisions and portable evidence

- **Proposed decisions and reviewers**: `open-decisions.json` OD-1..OD-8; required roles:
  maintainers (C++ E2E API), Rust API owners (#782), requirements/architecture reviewers.
- **Pending acceptance / gaps**: accepted E2E design; C++ E2E API + error classes; Rust Method/Field
  API; requirements/architecture impact decision; E2E test strategy; licence-clean mechanism.
- **Packet location**: `.rust-queue/reports/` —
  `scope.md`, `e2e-design-draft.md`, `check-plan.json`, `open-decisions.json`,
  `evidence-status.json`, `review-packet.md`.
- **Manifest**: SHA-256 and byte sizes were **not** computable in this session (shell blocked);
  file paths above are the inventory. Recompute on the host if hashes are required.
- **External raw evidence**: none (no commands executed). Missing artifact:
  `.rust-queue/reports/native-check-summary.json` (absent at task start).
- **Source/tool/config identities to reproduce**: baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`;
  Bazel config `linux_x64` (`.bazelrc`); `rules_rust 0.68.2-score`; clippy aspect
  `@score_rust_policies//clippy:linters.bzl%clippy_strict`; targets in `check-plan.json`.
- **Concrete next action**: obtain the C++ E2E API (OD-4); land Rust `Method<T>`/`Field<T>` (#782,
  OD-6); accept E2E design (OD-1..OD-3, OD-7); only then implement and run the planned checks.

> Passing checks and completed execution do not supply a human decision. This packet is exported and
> the run terminates; human review occurs outside the workflow.
