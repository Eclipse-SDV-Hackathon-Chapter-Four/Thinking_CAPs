# Communication #560 — final independent Codex supervisor review

No blocking defect was identified in the two scoped source changes. The measured build, helper tests, production integration tests, selected regressions, binary Clippy and explicit-label query passed. This supports ending the authorized correction run with its warnings and remaining obligations preserved. It is an agent recommendation; it does not accept the engineering change, qualify the API, close the issue or establish complete downstream readiness.

This supervisor read source and collected evidence, validated storage and hashed subjects. No native test, build, service start, source/control/ledger edit or publication was performed by this supervisor. The initial static report is preserved unchanged, SHA-256 `a16b492ffa86e7f0ff830a01e36bb01782a5323c77631edcb253dc31ea97debe`.

## Source binding and scope

The selected native baseline is `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Fresh independent hashing finds all 2,190 current workspace subjects equal to `attempt-1/final-source-hashes.json`. That measured source-vector file has SHA-256 `636ba2b223c228962ec2d055f15200bbdec1818f3c0bf5dd28fddd1e6c50de2f`, matching `attempt-1/measurement-binding.json`. Only the two authorized files differ from the incoming vector:

- `score/mw/com/test/basic_rust_api/subscription_state_apis/subscription_state_app.rs`: `119c05269330945392776bf0834a47933f8c3c4027de91cbc0d749717a6d9228`.
- `score/mw/com/test/basic_rust_api/subscription_state_apis/BUILD`: `27c83f6f777e3b572f44fd2f4d46c0c836b09515ff84a4c8de45b9b3d92df01c`.

The measured native result has SHA-256 `b0c40903bb5d5e50c1a821100000e4e0b45592c540bfc73ec7e9c5291c0f2764`, matching its measurement binding. All five command-log hashes, four unique XML/log payload pairs and four retained analyzer payloads match their supplied bindings. Shared storage validation succeeded for this bound SSD run root. No active workspace was relocated.

## Terminal execution evidence

Authoritative run `01M49A1PAGCVD0BTQPQ6RDPF3F` is terminal `succeeded` with a non-null successful conclusion in `native-runtime/01M49A1PAGCVD0BTQPQ6RDPF3F/final-state.json` and `final-projection.json`. The exported event collection contains 72 records with continuous stream sequence 1–72, all for this run; the final record is the successful lifecycle transition. There are zero stage retries, zero model tokens and no model usage within this native command-only run; Codex session costs are not measured here. Earlier submitted/running projections under `jobs/560/` are preserved historical snapshots, not terminal evidence.

All five native command groups returned zero without timeout: binary build; helper `rust_test`; integration tests for subscription, synchronous consumer and asynchronous consumer; binary Clippy; explicit query of the three new labels. Both test commands specify `--cache_test_results=no`. Build action reuse does not substitute for those fresh test executions. Query success resolves those explicit labels; it does not establish a complete reverse-dependency set.

## Actual case inventory

The retained production XML and bounded application logs independently establish the following cases, all with zero failures, errors or skips:

| Suite | Actual cases | Evidence |
| --- | ---: | --- |
| Subscription-state production harness | 5 | `subscription_state_apis/integration_test/test_subscription_state_apis/test.xml` and `test.log` |
| Existing synchronous consumer | 3 | `consumer_sync_apis/integration_test/test_com_api_sync/test.xml` and `test.log` |
| Existing asynchronous consumer | 3 | `consumer_async_apis/integration_test/test_com_api_async/test.xml` and `test.log` |
| Subprocess lifecycle helpers | 3 | `subscription_state_apis/subscription-state-apis-tests/test.log`; XML records one aggregate wrapper |

Paths above are relative to `attempt-1/native/native-testlogs/score/mw/com/test/basic_rust_api/`. There are 11 production/regression pytest cases and three helper Rust cases, totaling 14 actual cases. The helper XML's one wrapper must not be counted as three XML testcases or as an additional actual case.

The five production cases are `test_subscription_state_notifications`, `test_subscription_state_handler_replacement`, `test_subscription_state_handler_unset`, `test_subscription_state_handler_false_then_drop` and `test_subscription_state_handler_drop_active`. Application logs record completion of all five scenarios and successful controller exits. They exercise the real controller/provider production runtimes; their success is separate from subprocess stub coverage.

The synchronous cases are `test_bigdata_exchange`, `test_mixed_primitives_exchange` and `test_complex_struct_exchange`. The asynchronous cases are `test_bigdata_async_with_cancellation`, `test_bigdata_async_without_cancellation` and `test_bigdata_async_stream`. All six execute successfully in their native integration suites. Producer termination with status 143 is fixture cleanup and is not a failing consumer assertion.

The helper stdout records `provider_success_after_finish_is_accepted`, `provider_failure_after_finish_is_rejected` and `provider_wait_error_preserves_cleanup_and_reaps_live_child`, each `ok`, with `3 passed; 0 failed; 0 ignored`. These verify child-process lifecycle branches using shell providers and an injected wait error; they do not verify LoLa callbacks or reproduce an OS wait failure.

## Source findings and analyzer limits

Source locations below are within `subscription_state_apis/subscription_state_app.rs` unless specified otherwise. Explicit `LolaRuntimeBuilderImpl` annotations at lines 118 and 125 resolve the previous inference failure. `finish_with_wait` at lines 295–315 retains ownership through polling errors; line 316 releases the handle only after observed exit. Lines 320–322 require successful provider exit even after FINISH acknowledgement. The factored setup at lines 437–470 preserves the production same-executable provider path. Native `BUILD:45–52` runs the three focused tests on the actual binary crate. Compilation and the measured cases now substantiate the initial static findings.

`attempt-1/native/check-3.log` proves `AspectRulesLintClippy` executed and produced diagnostics/report. It retained two warnings:

- `dead_code`: unread `Observation.invocation`, line 571.
- `clippy::manual_is_multiple_of`: `marker % 2 == 0`, line 247.

The four retained outputs are hash-verified against `analyzer-artifact-binding.json`. Clippy is limited to the binary target; cfg(test) code Clippy is unmeasured. Exit zero does not mean warning-free analysis or approved warning dispositions. Build logs also retain existing C++ deprecation warnings and the Rust unread-field warning.

## Open obligations and recommendation

Native qualification, trace completeness and applicability to an adopted/certified toolchain remain separate engineering obligations. Linux x86_64 measurements do not apply to QNX or prove other platform readiness. Complete downstream dependents, examples and other use patterns were not measured by the explicit-label query or selected regression set. Reentrant callbacks, broader concurrency interleavings and stress, registration/unset failure paths, and complete FFI ownership/lifetime obligations remain outside the five production scenarios; no exhaustive concurrency or safety claim follows from passing tests.

The unchanged Drop cleanup at lines 398–410 ignores kill/wait errors and joins without its own timeout. The focused cases do not separately exercise timeout, acknowledgement failure, pipe setup failure or reader panic, and do not establish universal descendant cleanup or bounded recovery. No current production descendant or revived lost-ownership branch was identified. These are retained verification limits rather than a demonstrated defect requiring another correction.

The authoritative ledger records one of the three newly authorized Codex corrections used and two remaining, in addition to three historical corrections. No budget is reset or borrowed from the original issue queue. Ending the measured run does not consume the remaining corrections or authorize unrelated changes. Historical failures and the initial review remain preserved.

Recommendation: end source correction and retain the passing measured evidence together with warnings and applicability gaps. Package this report for authorized offline review; human acceptance remains pending and the issue remains open. Runtime shutdown and publication are separate actions and are not inferred from successful lifecycle evidence.
