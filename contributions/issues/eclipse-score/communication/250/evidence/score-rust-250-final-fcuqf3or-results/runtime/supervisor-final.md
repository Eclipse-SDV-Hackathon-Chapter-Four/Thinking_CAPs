# Communication #250 — independent final source and native measurement review

The final frozen candidate passes all six selected native Linux command groups. Independent inspection supports the narrowed typed, same-interface Any behavior and the repaired source defects. The analyzer command succeeds with four retained warnings. This recommendation supports preserving the measured contribution and stopping under the exhausted 3/3 correction budget; it does not close #250, qualify the component or constitute authorized human acceptance.

This supervisor inspected and hashed evidence read-only and wrote only this report. No source/control/ledger edits, builds/tests, runtime starts, model calls, retries, dispatch or publishing occurred. The source review remains separately preserved.

## Source and storage binding

Shared `score_sw_fabric.storage` run-root validation passed. Fresh hashing confirms all 2,883 current measured subjects match final `check-source-subjects.json`, SHA-256 `03e8f54bd3455c73c126a9c80e16890c2e45ae68c22e8df1a9db08c11ea646e8`. The source baseline remains communication `381d43dec900ab6a9076f3f30e7bfbdee019e26e`: 19 changed/added files relative to the original 2,878-subject vector, no baseline removal; five files changed relative to correction 2. Protected module/lock/license/policy subjects remain unchanged. Passing historical candidates were not substituted for this changed source.

`execution/native-result.json` has `passed=true`, six exit codes 0, no timeout, platform Linux x86_64 and `acceptance=pending_offline`. Its actual plan digest equals `effective-check-plan.json`. All six command-log hashes and every reported test XML/raw-log hash independently match their retained files. The per-check `test_records` arrays contain cumulative copies of earlier target records; this review deduplicated by the unique target/XML path and counted only the explicit targets selected in each group.

## Actual child cases, not Bazel wrappers

| Group | Explicit target evidence | Actual measured children |
| --- | --- | --- |
| 0, Linux Any | `consumer_any_apis/integration_test:test_com_api_any` | 2 pytest cases passed, 0 failure/error/skip |
| 1, LoLa Rust unit | `com-api-runtime-lola:com-api-runtime-lola-tests` | 9 Rust unit cases passed, 0 failed/ignored; XML is one Bazel wrapper |
| 2, native compatibility | `impl:runtime_test`; concept unit; macro unit | 17 C++ Runtime cases + 9 Rust concept + 8 macro cases passed, 0 failed/ignored; Rust XML wrappers are not child counts |
| 3, existing integration | Rust Specific sync; Rust Specific async; C++ find-any semantics | 3 + 3 + 1 pytest cases passed, 0 failure/error/skip |
| 4, explicit manual macro doctest, GCC 15 | `score_com_concept:score_com_concept-macros-tests` | 16 doctests passed, 2 ignored, 0 failed; XML is one wrapper |
| 5, native Clippy aspect | five selected library targets | Command exit 0; 5 actual SARIF reports, 4 warning findings |

Across nine distinct test targets, the raw child evidence totals **68 passed and 2 ignored**, with no failing/error child case. The two ignored doctests remain gaps; they are not passes. Groups' collector durations are respectively 274.099, 18.546, 32.296, 75.052, 11.326 and 12.859 seconds, which are distinct from Bazel's own elapsed times.

Exact Any children are `test_com_api_any` and `test_com_api_any_no_offer`. Exact existing sync children are `test_bigdata_exchange`, `test_mixed_primitives_exchange`, `test_complex_struct_exchange`; async children are `test_bigdata_async_with_cancellation`, `test_bigdata_async_without_cancellation`, `test_bigdata_async_stream`. The C++ integration child is `test_find_any_semantics`.

The LoLa unit stdout has nine actual passing cases, including the three added `test_any_discovery_unmapped_interface_returns_error`, `test_any_async_never_polled_stops_native_search` and `test_any_async_pending_cancellation_stops_native_search`. Those additions measure mock bridge arguments and exactly-one stop counters, not real callback quiescence or heap reclamation.

## Meaningful Any obligations and source findings

S1's `_find_guard` field initialization and S2's C++ registration object type are repaired and now compiled by native targets. The stop guard remains synchronously created after successful start and captured before any async polling, preserving never-polled cancellation ownership.

The positive raw application log independently records exact ServiceNotFound propagation for unmapped, concrete and malformed registrations; actual offered ComplexStruct readiness; exactly two BigData builders in sync and async; Specific compatibility; and both sync/async distinct marker sets `{1, 2}`. Source builds and subscribes through both builders in each round after discovery/future drop. Provider ID 2 is absent from the consumer's concrete config. Together, these assertions repair the previous `.next()`-only weakness and make offered-other-interface exclusion non-vacuous. Marker identities are test instrumentation, not authenticated production identities or an exposed native-ID API. The separate no-offer case tests synchronous `Ok(empty)` only.

Configured selector resolution still requires exactly one LoLa wildcard with no concrete instance ID. Native configuration owns deployment records; discovery does not construct local borrowed deployments. This is an explicitly registered, typed same-interface design with trusted interface/configuration association, not a general heterogeneous universe, binding/version/quality selector or system-wide discovery implementation. No Runtime virtual method was added, but this does not establish universal ABI/downstream compatibility.

The independent source review's remaining factual qualifications govern the final assessment even if model wording is stronger:

- Async is a one-shot future consuming the latest stored callback snapshot when polled ready, not a guaranteed first-callback snapshot. `consumer.rs:979` overwrites the stored handles. Native initial empty notification is suppressed (`service_discovery/client/service_discovery_client.cpp:767–772`), so an async request with no offers may remain pending until a later offer completes that same request. Already-offered async integration success does not prove empty completion, first-callback ordering or update-stream semantics.
- The async `block_on` at `consumer_any_apis/consumer_app.rs:350` has no internal discovery deadline. The real pytest harness supplies the outer 180-second process timeout; internal deadlines cover the sync readiness/discovery and receive loops. The source-stage claim that all waits have internal deadlines is too broad.
- ComplexStruct is present in consumer configuration (`etc/config.json:197–205`) to support the Specific readiness barrier. The producer comment claiming it is exclusive to provider configuration is inaccurate. The absent-from-consumer proof concerns BigData ID 2.
- Specific descriptors return the caller's query alias, not unique authenticated producer identity. Native Specific may itself resolve a wildcard. LoLa's legacy Any accessor still panics; the additive fallible override returns an error, but its trait default delegates to legacy implementations and cannot universally guarantee absence-as-error.
- The builder's private field and mandatory FFIBridge methods leave external source compatibility unverified. Selected in-repository compatibility, doc and integration targets cannot establish every downstream struct literal or trait implementation remains compatible.
- Exactly-one native stop is not callback Box/state reclamation. The inherited find-service `dispose` is empty (`registry_bridge_macro.h:190`); failed async selector paths may return before native callable ownership is established. Closure allocation reclamation, real concurrent callback/stop quiescence and repeated offer/withdrawal races remain evidence debt. No extra fix or unreviewed destructor is authorized.

The implementation report's 'not run' statements are source-stage historical claims, superseded for the selected measured groups by this evidence; they must not erase the failed prior attempts or be confused with a complete engineering assessment.

## Clippy dispositions and compiler warnings

All five portable SARIF files match the actual native Bazel report bytes. The Clippy command and action outputs genuinely executed; exit 0 is a command outcome, not a clean analysis result.

| Library | Findings retained |
| --- | --- |
| `com-api-runtime-lola` | `clippy::missing_transmute_annotations`, `consumer.rs:989`; `clippy::clone_on_copy`, `consumer.rs:1234` |
| `bridge_ffi_rs` | two `clippy::result_unit_err` warnings at `bridge_ffi.rs:259` (existing Specific API) and `:270` (new Any API) |
| `bridge_ffi_lola` | 0 SARIF findings |
| `score_com` | 0 SARIF findings |
| `score_com_concept` | 0 SARIF findings |

These four warnings are not errors or accepted suppressions. Test-code Clippy, broad C++ analysis, every binary and all dependencies were not selected by this five-library aspect run. Compiler deprecation warnings in the C++/Rust build logs and the JDK launcher warning are separate from these four Clippy SARIF findings. No warning-free, safety-clean or qualification claim is supported.

## Terminal runtime and disposition

At this review's final observation the `native-runtime/` directory contains no collected terminal files and the Flash supervisor report has not yet appeared. This report therefore verifies completed native source measurements, not the final model usage, Fabro lifecycle, export seal or owned-service shutdown. The operator must bind those terminal records separately and preserve any disagreement or missing evidence. A later successful lifecycle cannot replace the raw measurements or remove these qualifications.

#250 is at 3/3 corrections, zero remaining. #1261 remains 1/3, #173 2/3; the distinct #560 Codex allowance remains 1/3. No further source fix, retry or budget extension follows from this review. Qualification/applicability and native trace work products, external compatibility, concurrency/resource obligations, platform variants including QNX, the broader #250 system-all comment and #1261 heterogeneous stream remain open. Human acceptance is pending offline. Support ending this bounded measurement task with passing selected checks, four retained Clippy warnings and these explicit limits; issue closure remains a separate authorized engineering decision.

## Input bindings

| Input | SHA-256 |
| --- | --- |
| `check-source-subjects.json` | `03e8f54bd3455c73c126a9c80e16890c2e45ae68c22e8df1a9db08c11ea646e8` |
| `effective-check-plan.json` | `6acc379a655cb79d630909c1ab0c2a0e1c2cc259a9311c5a152c11c271872f3e` |
| `correction-ledger.json` | `03a65918b294294060c3af5bb65d032b1374f4b76d117036102c99e97511db58` |
| `supervisor-source-review.md` | `c6ca0882e081d4166046cc36643894310db91fd754308fe424a6caf08a546016` |
| `source-stage implementation.md` | `8cd88f88508dc7e4cd8f7998362a8c02fce0a84a26f6525e4127884b9222160a` |
| `regression-plan.json` | `ddd20f580ee6656b6b5a289345db995cf547cbcfee4adb07833530342cd51490` |
| `native-result.json` | `536d069ccd10ed2a2dc54028eab49c7065fc8458b41476840fee13ef1ddbe4f5` |
| `native-check-summary.json` | `2490e255bba3d16aeb7213e7f453a320e51ea3976bacbe4e429df9ae4cd0ae82` |
| `analyzer-summary.json` | `e30356ea0701aac4c1ac5a81d6aa510377cd9d26ccddadfa49dc9262c88c99d4` |
| `analyzer-evidence/score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_lola.sarif.json` | `3a52390597a3cb1f65c88a9906f9af2f94cf71767b8b0078762fd25a91a6a3f9` |
| `analyzer-evidence/score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_rs.sarif.json` | `7c0e6c7403b7299f07665900cdc3d1b4ac6844c40d212dc6f4135921d495a8a6` |
| `analyzer-evidence/score/mw/com/impl/rust/com-api/com-api-runtime-lola/com-api-runtime-lola.sarif.json` | `b8fdf290569b7fd7a7a4f520d5a4ea183e075453e826130ef261e5e3404d9a1e` |
| `analyzer-evidence/score/mw/com/rust/score_com.sarif.json` | `3a52390597a3cb1f65c88a9906f9af2f94cf71767b8b0078762fd25a91a6a3f9` |
| `analyzer-evidence/score/mw/com/rust/score_com_concept/score_com_concept.sarif.json` | `3a52390597a3cb1f65c88a9906f9af2f94cf71767b8b0078762fd25a91a6a3f9` |

The native-result binds all six retained command logs and the exact XML/raw-log subjects; every corresponding hash was independently reverified. Nine unique XML targets were parsed independently and wrapper counts were reconciled with child stdout as described above. This report makes no artifact-seal or terminal-runtime claim.
