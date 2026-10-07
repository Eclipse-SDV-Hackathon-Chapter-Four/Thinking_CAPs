# Communication #250 — independent frozen source review, final correction 3

No new blocking source defect was identified in the narrowed typed, same-interface wildcard implementation. S1/S2 are repaired; actual native positive integration and LoLa unit measurements now support their buildability and the strengthened S5 assertions. This is an interim source review while the remaining native groups and Fabro lifecycle are still being collected, not a terminal all-checks verdict or engineering acceptance.

This supervisor performed read-only inspection and hashing and wrote only this report. No source/control/ledger changes, build/test execution, model call, retry, dispatch or publishing occurred. #250 has exhausted its authorized 3/3 corrections; findings below authorize no further repair.

## Binding and measured evidence available

Shared storage validation passed for the bound external SSD. Independent fresh hashing confirmed all 2,883 measured candidate subjects equal `check-source-subjects.json` (SHA-256 `03e8f54bd3455c73c126a9c80e16890c2e45ae68c22e8df1a9db08c11ea646e8`). Five files differ from correction 2; comparison with that run's original 2,878-subject baseline confirms 19 changed/added files and no removed baseline subject. The current root's `source-subjects.json` represents the imported correction-2 candidate, so its five-file delta must not be misrepresented as the full baseline patch. Baseline communication commit remains `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Protected module/lock/license/policy subjects remain unchanged against the original vector.

At the evidence snapshot used here, `execution/native-result.json` records completed groups 0, 1 and 2 with exit 0 (collector durations 274.099, 18.546 and 32.296 seconds); aggregate `passed` remains false while the six-group sequence is incomplete. This report independently checked the following raw child evidence for groups 0 and 1:

- Any integration XML: exactly `test_com_api_any` and `test_com_api_any_no_offer`, two tests, zero failures, errors or skips. Raw application log records exact three selector rejection reasons, observed offered ComplexStruct readiness, exactly two sync/async BigData builders, both marker sets `{1, 2}`, Specific compatibility and the separate sync no-offer empty result. Bazel's one target is not one child case.
- LoLa unit XML is a one-test Bazel wrapper; raw Rust stdout shows nine actual unit cases passing, including unmapped Any, never-polled future cancellation and polled-pending cancellation. These three additions are mock bridge/stop-counter cases, not three real native cancellation integrations.

Groups 3–5, complete child inventory, analyzers and final runtime lifecycle require the later terminal review. The source-stage report's statements that checks were not run are historical stage-local statements; they do not supersede later native evidence. No earlier passing candidate results were carried onto changed subjects.

## S1–S7 dispositions

**S1 resolved.** `score/mw/com/impl/rust/com-api/com-api-runtime-lola/consumer.rs:1018` now initializes `_find_guard: find_guard`, matching the field. The owning guard was retained, and the native Rust build and unit cases passed.

**S2 resolved.** `score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h:824` now declares `id##_InterfaceRegistrationHelper id##_interface_reg_instance`. The actual new registration users compiled in the passing positive integration target.

**S3 narrowed ownership/selection approach supported.** `registry_bridge_macro.cpp:60–108` resolves the explicitly registered selector through native Runtime configuration, requires exactly one LoLa binding with unset instance ID and retains the configuration-backed identifier; it does not synthesize deployment ownership or change the Runtime vtable. The integration uses builders and proxies after discovery/future drop, exercising the configuration lifetime assumption. Scope remains one configured wildcard selector per registry interface and trusted interface/configuration association. General version/quality selection, multiple compatible bindings and heterogeneous discovery are not implemented or qualified by these checks.

**S4 cancellation design supported within its measured scope.** `consumer.rs:992–1065` constructs the stop guard synchronously after a successful native start, captures it inside the outer future and transfers it into the inner future. A never-polled drop therefore retains owning stop behavior. Mock tests verify exactly one stop for both tested cancellation paths. Real cross-thread callback quiescence, repeated offer/withdrawal races and allocation reclamation remain unmeasured. Completion is a one-shot future, not #1261's update stream.

**S5 strengthened and actually exercised.** `consumer_any_apis/consumer_app.rs:216–257` observes an offered different interface before asserting the typed wildcard. Lines 298–417 consume both sync and both async builders, build both proxies, subscribe to both and require disjoint singleton marker sets whose union is `{1, 2}`. Producer markers are independently encoded by the two offered BigData instances (`producer_app.rs:252–265`); the second concrete instance is absent from the consumer manifest. The measured raw log confirms both rounds. This repairs the previous `.next()`-only and readiness coverage weaknesses without relying on handle order. Exact concrete native IDs remain opaque; marker identity is test instrumentation, not authenticated production identity. Empty-case coverage is sync-only.

**S6 limits preserved.** `score_com_concept/concept.rs:592–627` now explicitly documents Specific's caller-supplied query alias rather than unique authenticated producer identity. LoLa's fallible accessor returns ServiceNotFound for every Any builder; its legacy accessor still panics (`consumer.rs:1133–1149`). The trait default forwards to legacy implementations and cannot guarantee universal non-panicking absence handling. Existing in-repository compatibility targets do not prove compatibility for external struct-literal users affected by the private builder field or external FFIBridge implementations affected by the two new mandatory methods. No general ABI or downstream compatibility conclusion is warranted.

**S7 remains an applicability/resource-lifetime gap.** `registry_bridge_macro.h:190` still has an empty find-service callback `dispose`; `consumer.rs:982–990` erases the boxed closure. Invalid async selector validation can return before native callable ownership is established. Exactly-one native stop is not proof that the Rust callback Box, captured Arcs or every native allocation are reclaimed. This is retained inherited/extended evidence debt, not a newly observed crashing test. No unreviewed destructor or broad unsafe cleanup is authorized by this review.

## Remaining factual qualifications

1. `implementation.md:64` overstates a strict first-callback snapshot. `consumer.rs:978–980` overwrites stored handles on each callback; the first ready poll consumes the latest stored snapshot, which need not be the first callback. Native `service_discovery/client/service_discovery_client.cpp:767–772` suppresses initial empty notification, so a no-offer async request may remain pending and later offers can complete that existing request. The integration tests already-offered async success, not async empty completion or first-callback ordering. Preserve this distinction in final exported assessment; no source correction remains.
2. `implementation.md:79` and `consumer_app.rs:59` overstate universal internal deadlines. The async `block_on` at line 350 has no internal deadline; the actual integration's outer `wait_timeout=180` bounds the process. The sync readiness/discovery and receive loops do have internal deadlines.
3. `producer_app.rs:207–209` inaccurately says ComplexStruct is offered exclusively from the provider manifest. The consumer config also contains `/UserDefinedTest/ComplexStruct` with concrete ID 13 (`etc/config.json:197–205`), as required by the new Specific readiness barrier. The absent-from-consumer assertion applies to BigData ID 2. This comment does not invalidate the non-vacuous measured exclusion test.

These are report/comment accuracy and retained scope qualifications, not an instruction to consume another correction. No new source blocking defect was identified beyond the explicitly retained compatibility/resource concerns. Qualification, source applicability and requirement/test traces, broader #250 interpretation, #1261, external consumers, platform variants and authorized offline human acceptance remain open. Passing native checks and a successful Fabro lifecycle cannot close them.

## Input hashes at review snapshot

| Input | SHA-256 |
| --- | --- |
| final frozen source vector | `03e8f54bd3455c73c126a9c80e16890c2e45ae68c22e8df1a9db08c11ea646e8` |
| previous independent source review | `f908c2328f15426d92bfce1293ad2815d8a6fa34908600a61dd797666201cb76` |
| final implementation report | `8cd88f88508dc7e4cd8f7998362a8c02fce0a84a26f6525e4127884b9222160a` |
| regression plan | `ddd20f580ee6656b6b5a289345db995cf547cbcfee4adb07833530342cd51490` |
| effective six-group check plan | `6acc379a655cb79d630909c1ab0c2a0e1c2cc259a9311c5a152c11c271872f3e` |
| exhausted correction ledger | `03a65918b294294060c3af5bb65d032b1374f4b76d117036102c99e97511db58` |
| live native-result snapshot after groups 0–2 | `d4854f9aedc657e5c6c1bb9d43eeaa321b468f5ea8d111694f0ac28c1c57b00c` |
| positive integration raw log | `b3b2b812bdeed65b5f50cfbd9f49cc524fd404a6656ed56bf179780336f2fbc6` |
| positive integration XML | `6ceba1094728bec69b48dfa0929293d2d2f2db48862cc8a7bfb05f31d012ac12` |
| LoLa unit raw log | `be8f7d743fa3af426b3dd8222acdbfbd05bfa8a61a5a0610d9d8dd1fa8c19afd` |
| LoLa unit wrapper XML | `9dc8fa2c8fb7e3a808c05b398b61dc15da8e76987deda8cfc7372882265c313a` |

Live execution snapshots may subsequently change as later checks finish; their hashes here identify the inspected snapshot, not a final seal. Preserve this report with the terminal evidence.
