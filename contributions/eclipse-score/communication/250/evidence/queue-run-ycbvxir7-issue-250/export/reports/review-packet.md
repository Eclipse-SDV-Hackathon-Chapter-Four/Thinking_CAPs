# S-CORE Rust issue review packet — issue #250

## Scope and binding

- Issue/repository: `eclipse-score/communication#250`,
  `Improvement: COM-API FindServiceSpecifier::Any support`, state `open`, label `rust-api`.
  Retrieval: 2026-10-06 (context from `.rust-queue/context/{issue,comments}.json`; live
  timeline fetch **failed** — `web_fetch` blocked by the file-tool boundary).
- Source commit: baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
- User authority/limits: disposable workspace only; Linux only; DeepSeek Flash only;
  `shell`, delegation, publishing and acceptance tools blocked; no QNX; no code change made.
- Process/tailoring: `.rust-queue/context/score-rust-workflow/SKILL.md` + references
  (`native-verification.md`, `issue-types.md`). Native IDs: `SWS_CM_00302`,
  `SWS_CM_00312` observed in `instance_identifier.h` / `handle_type.h`; no requirement
  change asserted by the issue.
- Source/lock/tool bindings (from baseline `MODULE.bazel` / `.bazelrc` / `.bazelversion`):
  Bazel `8.7.0`; `rules_rust` `0.68.2-score`; `score_toolchains_rust` `0.10.0`;
  `score_rust_policies` `0.0.5`; `score_baselibs` `0.2.14`; default/`linux_x64` config uses
  GCC 15.2.0 + Ferrocene x86_64 toolchain.
- Final patch: **none** (blocker/design outcome). Baseline-to-patched digest: N/A.
- Technical completion: assessment complete. Engineering acceptance: **not claimed** —
  blocked pending decisions below.

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact ID and revision | Changed artifact | Required check | Evidence/hash | Gap or proposed disposition |
| --- | --- | --- | --- | --- | --- |
| `FindServiceSpecifier::Any` works without panic | `Runtime::find_service`; `high_level_design_detail.md:118` | none | `check-plan.json` build/test checks | `runtime.rs:40-52`; design marks `Any` `[ ]` | Blocked: no FFI/backend path; keep panic |
| Discovered ANY instance is usable (`get_instance_specifier`, build Consumer) | `ConsumerDescriptor`; `HandleType` (`SWS_CM_00312`) | none | runtime unit + integration tests | `consumer.rs:1070-1078`; `handle_type.h:82-104` | Blocked: descriptor contract cannot be met from a handle; needs FFI + design decision |
| Detailed design stays accurate | `high_level_design_detail.md:117-118` | none | docs checks | already marks `Any` unsupported | Satisfied for current state; update only after an accepted decision |
| Requirements/Architecture unaffected | issue template field | none | N/A | issue body | No requirement artifact change proposed |

Baseline reconciliation: the original premise ("LoLa does not support ANY") is only partly
true — LoLa SD supports any-instance semantics via `InstanceIdentifier`
(`i_service_discovery.h:43-51`, `flag_file_crawler.cpp:168-205`) and the native
`find_any_semantics` integration test shows the bridged `FindService(InstanceSpecifier)`
overload returning two instances when the deployment resolves to an unpinned instance id
(`find_any_semantics/client.cpp:35-72`, `service.cpp:100-123`). The Rust FFI still exposes only
the `InstanceSpecifier` overloads and cannot request "any" for a bare interface or retrieve a
discovered identity (`bridge_ffi.rs:239-259`, `common.rs:37-174`). No semantic/link-direction
change is made; no requirement/design/safety impact is introduced by this run.

## Dependency and macro assessment

Not applicable. No dependency is added, replaced or re-internalised, and no procedural
macro/API generation is changed. `reference: references/dependency-and-macros.md` consulted
only to confirm the generated-API compatibility obligation for the integration binaries.

## Verification and expected checks

No native command was executed (agent authority). The planned, BUILD-derived targets,
reasons and native obligations are in `.rust-queue/reports/check-plan.json`:

| Check | Target(s) | Native obligation/source | Status |
| --- | --- | --- | --- |
| build | `//score/mw/com/rust/score_com_concept:score_com_concept`, `…/com-api-ffi-lola:bridge_ffi_rs`, `…:registry_bridge_macro_cpp` | BUILD rust_library / cc_library; native-verification.md | not run |
| build | `…/com-api-runtime-lola:com-api-runtime-lola`, `…/com-api-runtime-mock:com-api-runtime-mock`, `//score/mw/com/rust:score_com`, `//score/mw/com/rust:score_com_mock` | BUILD rust_library; downstream compilation | not run |
| test | `//score/mw/com/rust/score_com_concept:score_com_concept-test`, `…:score_com_concept-macros-unit-tests` | BUILD rust_test / rust_unit_test (Linux only) | not run |
| test | `…/com-api-runtime-lola:com-api-runtime-lola-tests` | BUILD rust_test (Linux only) | not run |
| test | `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | BUILD rust_test (Linux only) | not run |
| test | `…/consumer_sync_apis/integration_test:test_com_api_sync`, `…/consumer_async_apis/integration_test:test_com_api_async` | integration_testing.bzl | not run |
| test | `//score/mw/com/test/find_any_semantics/integration_test:test_find_any_semantics` | BUILD integration_test; native C++ any-semantics boundary (client `FindService` requires 2 instances) | not run |
| build | `//score/mw/com/test/find_any_semantics:service`, `:client`, `:test_datatype` | BUILD cc_binary / cc_library | not run |
| build | `//score/mw/com/test/basic_rust_api:bigdata_com_api_gen_rs`, `…/consumer_sync_apis:bigdata-consumer`, `…/consumer_async_apis:bigdata-consumer-async`, `…/producer_app:bigdata-producer` | BUILD rust_library/rust_binary | not run |
| docs | `…/com-api-runtime-lola:com-api-runtime-lola-doc-tests`, `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` (manual) | BUILD rust_doc_test | not run |
| lint | concept / runtime-lola / bridge_ffi_rs libraries | `@score_rust_policies//clippy:linters.bzl%clippy_strict` via `--config=clippy` | not run |
| query | `//score/mw/com/rust:score_com`, `//score/mw/com/rust:score_com_mock`, `…/com-api-runtime-lola:com-api-runtime-lola` | reverse-dependency enumeration | not run |

Trusted collector evidence: **absent** — `.rust-queue/reports/native-check-summary.json`
does not exist in this workspace. No carried evidence is reused; no generated-API or
baseline/candidate measurement was performed.

## Offline decisions and portable evidence

- Proposed decision: keep `FindServiceSpecifier::Any` unsupported (Option A) until B/C in
  `blocker-design-report.md` §4 is accepted. Removing the panics would violate the current
  native design status and expose behavior the FFI cannot serve.
- Required authorized reviewers/roles: Rust COM-API owner + LoLa/backend owner (for the
  FFI `InstanceIdentifier` any-semantics bridge and the `ConsumerDescriptor` contract).
- Pending acceptance / gaps: (1) semantics of `Any`; (2) backend/FFI extension approval;
  (3) `ConsumerDescriptor` contract change; (4) live PR/issue activity unverified (network
  blocked); (5) no native build/test evidence collected in this run.
- Packet location: `.rust-queue/reports/` (`scope.md`, `implementation.md`,
  `blocker-design-report.md`, `check-plan.json`, `review-packet.md`).
- Manifest: file sizes/SHA-256 could **not** be computed — hashing requires a shell, which
  is outside agent authority. Recorded as missing, not fabricated.
- Source/tool identities for reproducibility: baseline commit above; `MODULE.bazel`
  (Bazel 8.7.0, rules_rust 0.68.2-score, score_rust_policies 0.0.5); `.bazelrc`
  (`linux_x64` → GCC 15 + Ferrocene); `quality/static_analysis/static_analysis.bazelrc`
  (clippy_strict aspect).
- Concrete next action: obtain the three human decisions above; on approval, extend the
  FFI/backend and `ConsumerDescriptor` contract, then implement `Any` with regression cases
  in `com-api-runtime-lola-tests` and the basic_rust_api integration tests, measured under
  the `check-plan.json` targets.

Do not embed credentials. Passing checks and completed execution do not supply a human
decision. This packet is exported for offline review.
