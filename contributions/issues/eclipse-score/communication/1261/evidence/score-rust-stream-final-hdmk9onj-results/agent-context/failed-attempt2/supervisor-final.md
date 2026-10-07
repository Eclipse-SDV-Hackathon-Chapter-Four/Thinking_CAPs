# Communication #1261 — independent terminal review, failed source correction 2

The attempt **does not implement #1261**. The implementation stage failed with provider HTTP 400 after producing partial descriptor changes. Four selected native compatibility groups passed, but the required check stage failed because no dedicated heterogeneous-stream regression plan exists. Fabro's terminal lifecycle says succeeded after its failure routes reached export/exit; that lifecycle is not source-task completion, issue closure, qualification or human acceptance.

Only this report was written. Source, controls, ledgers, reference repositories and historical packets were inspected read-only; no native execution, paid requests, retries, dispatch, publication or credential inspection occurred. #1261 remains 2/3 corrections used, one remaining; #250 stays stopped 3/3, #173 2/3 and the separate #560 Codex allowance 1/3. This review neither consumes nor extends them.

## Frozen source and actual scope

Shared storage validation passed for the bound external SSD. Independent fresh hashing confirms all 2,878 source subjects match `check-source-subjects.json`, SHA-256 `97e10c3b295cf690779cf89db4f72cd478e9b767693dd860209b254aabcda652`; the final-source map is identical. Only common.rs, concept.rs and the facade changed relative to the imported partial draft. The full baseline remains communication `381d43dec900ab6a9076f3f30e7bfbdee019e26e`; protected module/lock/license/policy subjects are conserved, and #250 source was not imported.

The source findings S1–S5 remain:

- LoLa's Runtime implementation has no find_all_services override and still inherits `Err(NotSupported)`. No continuous backend, configured native universe, Runtime/Configuration enumeration API, stable wildcard storage, multi-watch handle ownership or callback-to-stream implementation exists.
- common.rs adds only the unused StringView import. Existing HandleContainer helpers are not newly implemented stream support. No new C++/extern/FFIBridge identity extraction or updating snapshot callback exists.
- Owned versioned descriptors and the facade re-export are useful proposed API shape; the literal-construction unit test does not observe a remote/native identity. Quality, allocation/capacity and dedup identity remain open. ServiceDescriptor constructor/accessor replacement and the historical NotSupported enum variant require downstream compatibility disposition.
- No positive two-interface, delayed/initial-empty/pre-existing, withdrawal/re-offer/dedup or stream-drop integration was implemented; regression-plan.json and implementation.md are absent. The contract's C1–C7 remain obligations, not implemented guarantees. No bounded configured-universe backend was achieved, let alone unqualified system-wide discovery.

The Flash supervisor correctly identifies missing completion. Two of its bookkeeping observations require reconciliation: error.rs and high_level_design_detail.md contain #1261 material from the imported partial draft and are hash-identical to starting subjects, so their presence is not an inconsistency in the three-file correction delta. common.rs's HandleContainer helpers also predate this attempt; only its StringView import changed. The stale design trait table still describing interface id + instance specifier is retained documentation debt, not a completed descriptor contract. Raw child counts below supersede its XML-wrapper counts. Its 'not accepted' language is an agent recommendation and cannot record an authenticated human decision.

## Native compatibility measurement

All four native command groups have exit 0 and no timeout. `execution/native-result.json` records `passed=true`. Every corresponding command-log hash and each XML/raw test-log hash independently matches retained bytes. Collector test_records are cumulative across groups; nine unique explicit target paths were counted once, using XML for actual pytest/C++ children and raw stdout for Rust wrappers.

| Group | Selected targets | Actual children |
| --- | --- | --- |
| 0, Linux unit/compatibility | LoLa Rust unit; Configuration C++; Runtime C++; concept Rust; macro Rust | 6 + 30 + 17 + 10 + 8 passed, zero failed/ignored |
| 1, existing integration | Specific Rust sync; Specific Rust async; C++ find-any semantics | 3 + 3 + 1 pytest cases passed, zero failure/error/skip |
| 2, manual macro doctest, Linux GCC15 | explicit macros-tests target | 16 passed, 2 ignored, zero failed; XML is one Bazel wrapper |
| 3, Clippy | five selected native library aspect targets | command exit 0, five genuine SARIF reports, four retained warnings |

Unique actual child total: **94 passed and 2 ignored doctests**. Rust wrapper XML counts are not Rust child totals. None is a new native heterogeneous-stream case. The selected concept cases include default NotSupported and literal descriptor behavior, which cannot satisfy a real backend. Existing scoped/C++ Any compatibility preserves a useful baseline; it is not system-wide Rust stream evidence. Collector durations are 266.254, 127.676, 10.814 and 12.351 seconds, distinct from native Bazel elapsed times.

Portable analyzer reports byte-match their actual Bazel outputs. LoLa runtime retains `clippy::missing_transmute_annotations` at consumer.rs:950 and `clippy::clone_on_copy` at :1164. bridge_ffi_rs retains `unused_imports` at common.rs:23 and `clippy::result_unit_err` at bridge_ffi.rs:259. Concept, facade and bridge_ffi_lola reports have zero SARIF findings. Clippy command success is **not clean analysis**. Compiler/JDK warnings are separate, and test-code Clippy, C++ static analysis, unselected platform paths and qualification remain unmeasured.

The launcher/check-invocation return code 0 and native summary passed=true describe compatibility commands. The driver separately exits 1 for `Required dedicated heterogeneous stream regression plan absent; compatibility tests cannot establish completion.` Authoritative check@1 completion retains that failure. Do not erase this distinction when exporting summaries.

## Transport cause: decisive new evidence

This terminal evidence supersedes the earlier source report's unconfirmed output-limit hypothesis. The metadata observation was captured to stream 59,785, whereas the independently collected terminal event sequence contains 60,627 records with has_more=false and terminal_lifecycle_present=true. Full terminal events were inspected for message/control metadata, without reproducing model reasoning text.

| Stream sequence | Observed event |
| --- | --- |
| 7858 | Plain steering control requested at 22:13:20.398Z; 1,494-character guidance, text SHA-256 `19f8aa2f2bc33337b29f0f0a4a990eb386f73c6b8a39c40c9273bd95e6fae586` |
| 41068 | Implementation AssistantMessage at 22:18:00.033Z: text length 0, tool_call_count 0, reasoning present; usage 1,115 reasoning tokens and 0 output tokens |
| 41069 | UserInput at 22:18:03.625Z: length 1,494 and exact same SHA-256 as queued guidance |
| 41070 | Next LlmRequestStarted at 22:18:03.637Z |
| 41071 | Provider HTTP 400 at 22:18:04.455Z: invalid assistant message lacking content/tool_calls, request `67f16804-8f19-48e2-a501-4fdae6757c90` |

The retained filtered metadata and raw event inspection identify one assistant turn with neither text nor tool calls: 41068. No output_limit warning is present. Maximum reported per-response reasoning+output usage is 7,452, below the graph's 16,000 output cap; the failing-history turn uses 1,115. There is no evidence of Length/cap exhaustion. A larger cap is therefore **not a causal repair** for the observed failure; the earlier aggregate 40,347 reasoning count spans responses.

Pinned Lithos `openai_chat.rs:787–852,874–890` excludes reasoning from encodable content, omits content/tool_calls when neither exists and separately replays reasoning_content. Thus the observed empty assistant history has exactly the structural conditions for the rejected request on replay. The outgoing wire payload/finish reason was not captured here, so those literal fields cannot be claimed independently observed; the event sequence, encoder and provider error strongly support reasoning-only history replay as the mechanism.

The single guidance was supplied as a queued follow-up after the empty answer. Pinned Petri `crates/attractor/steps/src/pebble.rs:606–625` routes plain active steering to bus.follow_up once the current answer is reached; interruption is a separate branch. Pebble's queue_steering/steer_now and follow-up controls likewise distinguish natural-boundary delivery from interruption. No interrupt/cancel event or control establishes that steering interrupted reasoning or created the empty response. The evidence supports that it **triggered the subsequent replay request**, not that it caused the model's empty turn. Preserve both facts.

## Remaining attempt and runtime disposition

A meaningful conservative mitigation, if the already authorized final original correction is admitted, is a fresh conversation with all contract/failure context in its initial task and no mid-run steering/follow-up that replays the observed empty answer. Strong required artifact/positive-regression checks must still reject premature empty completion. This removes the observed follow-up trigger while preserving source-budget controls; it does not fix the unpatched codec or guarantee a complete implementation. A supported lower/disabled thinking control could reduce reasoning-only-turn exposure but is not a verified repair and must be documented as a hypothesis. Optional larger output headroom is not this incident's remedy. No paid retry, custom provider/proxy or native codec/global tool patch is authorized by this review.

Terminal state and projection agree lifecycle succeeded, with non-null conclusion and zero retries. Stages are start/preflight succeeded, implementation failed HTTP400, check failed positive-plan guard, Flash supervisor/export/exit succeeded. Selected models list only deepseek-v4-flash/DeepSeek. Native projection usage is 300,035 input, 21,374 output, 58,820 reasoning, 10,927,104 cache-read tokens and catalog cost 94,904 USD micros; these measurements describe the Fabro run, not independent Codex session costs. Owned-service shutdown and portable packet/registry seal are separate operator responsibilities, not certified here.

Task outcome remains **incomplete/failed source correction**, compatibility measurements passed with warnings, #1261 open, human acceptance pending offline. Preserve failed implementation, missing reports/positive plan, terminal lifecycle mismatch, source vectors, nine unique target records and analyzer findings. The final original correction remains one; no #250 fixes, budget reset, qualification inference or synthesized acceptance follows.

## Input bindings

| Input | SHA-256 |
| --- | --- |
| `check-source-subjects.json` | `97e10c3b295cf690779cf89db4f72cd478e9b767693dd860209b254aabcda652` |
| `final-source-subjects.json` | `97e10c3b295cf690779cf89db4f72cd478e9b767693dd860209b254aabcda652` |
| `correction-ledger.json` | `1b05849b7e7f394f9e342947ccff0a58fb8864c46290469dc9a6becc9bbe742a` |
| `supervisor-source-review.md` | `02b91a12e6caf366d8d070bc28f7293136c3145d7f6a9dfc9a65fbbdd0efda3f` |
| `execution/native-result.json` | `bd9293f8bae2146c2666fbaed848012908bfb917d1889763a0e9c9dd26334807` |
| `effective-check-plan.json` | `5f4f5813f0eee76a939a5641d2ab5e19699f750cabd3c8cb6f4c3cea9e951dfc` |
| `native-check-summary.json` | `ae8ced186148cfeb30f7697834f36dd27c645dd45d1c68817d10ba4dadd1d8ea` |
| `Flash supervisor.md` | `489fa0e8c17a4361939065e774ab91cff62ca7ecb7500aaf159e70ea4b17de47` |
| `transport-response-observation.json` | `7bea26eae948e7b817ec7b59698a18f95ebff2b6dbea65927efdab8e493d01ef` |
| `contract-steering-response.json` | `92686e74dc13fec3db07abed060d9f645e9321b03e818b449634dcabcc13d8e7` |
| `terminal events.jsonl` | `86ce47975ee1146b51a12361294265ef3b8afd00f0c5e8a285dce0e8d3ef05aa` |
| `event-collection.json` | `a94626c2171af2ed716801dd08531f72ce91dc3909c5b6805098ab59345da71d` |
| `terminal final-state.json` | `91e06a9a1f4b9840e622df37ed7ca779cc9c1a5d57cf8a6f83683449da839d01` |
| `terminal final-projection.json` | `dcb10d58d2d92b69445aacce7ccf923b7d45f07343c60decee29084f4e4f8e38` |
| `analyzer-summary.json` | `6a50d9fb312de93ea8a66fce2aff377fd07e47d8af9d8961f79674e762ca9cf7` |
| `pinned Lithos codec` | `8f008da963a1d2a0f4b5165e11eb822f6aa0386b857bd5b30c6f83166b84e2c4` |
| `pinned Petri follow-up delivery` | `88c0c58c187a72967b4a767c46bbba22da3041e3bff5d7a196bdc151ee99d12d` |
| `pinned Pebble controls` | `c96f461ae8ad445dfca0262597bfc2357443ffba1f2894fdc04881bcc3ee1317` |

The native-result binds every inspected command log and XML/raw-log subject. analyzer-summary binds all five inspected portable reports, whose hashes were independently checked against actual Bazel source outputs. This report does not claim a portable artifact seal, authenticated human decision or completed backend.
