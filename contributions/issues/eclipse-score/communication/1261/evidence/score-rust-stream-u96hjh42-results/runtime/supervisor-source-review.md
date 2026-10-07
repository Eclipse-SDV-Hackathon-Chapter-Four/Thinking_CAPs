# Communication #1261 — frozen partial source review, correction 2

The source stage failed at the provider boundary before implementing the stream backend. The frozen candidate remains API scaffolding and **does not implement #1261**. Passing compatibility groups cannot establish a missing backend or replace the absent dedicated stream regression. One original correction remains; this read-only review does not dispatch or authorize a new run.

Only this report was written. No source/control/ledger edits, native builds/tests, paid requests, global storage changes or retries occurred. Credential files and credential/auth data were not read. Shared storage validation passed for the bound external SSD.

## Frozen source proof and stage failure

Independent hashing confirms every one of 2,878 current source subjects equals `check-source-subjects.json`, SHA-256 `97e10c3b295cf690779cf89db4f72cd478e9b767693dd860209b254aabcda652`. Relative to the byte-identical imported partial draft, only these three files changed: `com-api-ffi-lola/common.rs`, public `score_com.rs` facade and `score_com_concept/concept.rs`. No new source subject was added. Protected pins/licenses/policy remain unchanged; no #250 implementation was imported. The source checkpoint is `35f2712`, with preflight snapshot `843c9ba`; those git revisions were inspected read-only.

`live-stage-observation.json` independently records implementation@1 failed with provider DeepSeek HTTP 400 `invalid_request_error`: “Invalid assistant message: content or tool_calls must be set”, request ID `67f16804-8f19-48e2-a501-4fdae6757c90`, at 2026-10-06T22:18:04.581Z. The owned runtime server log corroborates the request rejection and agent shutdown. This is a transport/model-message failure, not a native compiler failure or a failed assertion. The ledger charges correction 2/3 despite incomplete source work; one remains. #250 remains stopped 3/3, #173 remains 2/3 and the #560 extra allowance remains 1/3.

At review time native compatibility groups are executing. The first recorded group completed exit 0; aggregate native-result is not yet a terminal pass. The driver has no `regression-plan.json` and must retain its required-positive-regression gap even if all default compatibility groups pass. Final lifecycle, Flash supervisor, child inventory and analyzer outputs require later terminal binding.

## Concrete incomplete-source findings

**S1 — no LoLa heterogeneous stream backend.** `com-api-runtime-lola/runtime.rs` is unchanged: its Runtime implementation has no find_all_services override and inherits `concept.rs:161–163` returning ServiceError(NotSupported). There is no Configuration enumeration extension, mockable Runtime/IRuntime API, owned wildcard deployment storage, all-interface native watcher or Rust updating stream. Existing scoped discovery remains available, including the original unsupported typed Any behavior; this run must not repair/import #250 under #1261 authority.

**S2 — no native identity extraction or stream FFI.** The only FFI file change is unused `use crate::StringView` at `common.rs:23`; the native check-0 log also reports that unused import. No corresponding C++ entrypoint, extern declaration, FFIBridge method, identity serialization or callback/watch guard was added. Therefore nothing retrieves concrete observed HandleType identities, forwards complete heterogeneous snapshots, cleans up partial starts or handles never-polled stream drop. No assertion of native callback/Box reclamation or synchronization can be made.

**S3 — richer descriptor remains proposed data shape, not observed-service proof.** `concept.rs:340–445` adds owned String service type and binding, major/minor ServiceVersion and numeric service/instance IDs, with equality and accessors. This addresses the previous static Rust-registry string and fabricated InstanceSpecifier design limitation in shape. The facade re-exports ServiceVersion. However, the public constructor accepts arbitrary supplied values and no backend populates it from native observations. The updated unit test at `:1135–1146` constructs literal values and checks accessors; it is a data-container test, not acceptance evidence for actual discovery or full native identity.

Quality is still omitted with an open design question (`:381–384`). Dedup semantics must be decided against native watch/quality selection before treating derived equality as sufficient service identity. Native type version, binding and observed instance ID must remain separate from query aliases. Allocation of owned Strings also needs a real runtime allocation/capacity disposition; no running-phase policy compliance is proven.

**S4 — source-compatibility changes and qualification remain open.** Compared with the imported partial draft, ServiceDescriptor::new changes from two arguments to five and interface_id()/instance_specifier() accessors are removed in favor of native-shaped accessors. This may be a suitable revision of an unaccepted draft, but cannot be called universally non-breaking. The historical new NotSupported error variant also retains exhaustive-match compatibility concerns. In-repository compilation does not prove external callers/implementors remain compatible. There is no accepted descriptor contract, qualification/status change or human acceptance.

**S5 — positive obligations are absent.** No dedicated two-interface consumer/provider scenario, delayed-offer/initial-empty/pre-existing snapshot tests, removal/re-offer/dedup assertions, partial-start/cancellation tests or regression-plan.json was produced. No actual stream case can run for this source. C1–C7 from the contract review all remain backend/verification obligations. The existing compatibility plan and one container-literal test cannot satisfy system-wide newly available services, initial/error/termination semantics or cleanup. Configuration-opening-time and unknown/unconfigured universe limits remain unimplemented and unaccepted rather than resolved.

## Offline transport audit: proof versus hypothesis

The inspected pinned Lithos codec `openai_chat.rs:787–852` builds message content from encodable parts and omits the content field when no such part exists; tool_calls is included only for actual ToolCall parts. `encode_content_part` at :874–890 excludes reasoning and tool-call parts from content, while the encoder separately replays non-redacted reasoning as reasoning_content. Consequently, a reasoning-only assistant message with no retained tool calls is encoded as an assistant with reasoning_content but neither content nor tool_calls. That message shape is consistent with the observed provider rejection.

The same codec's :2002–2048 tests/source behavior drops incomplete tool calls at a Length finish reason. The pinned Pebble agent `runtime/turn.rs:850–854` requests a follow-up when FinishReason::Length is returned. These source facts establish a plausible route: truncated/empty assistant answer becomes committed history and is replayed in the next request with neither required field. They do **not** prove this run's last response was Length, that a tool call was truncated or that this exact invalid message appeared in the outgoing payload.

The retained projection reports 59 messages and aggregate 40,347 reasoning tokens / 10,386 output tokens; these are multi-message totals and cannot prove exhaustion of the graph's per-response max_tokens=16000. No finish reason, last-response usage or request-body capture appears in the inspected projection or owned runtime log. Read-only queries restricted to run_session_records/run_session_events for the exact run/session found no stored record in this owned server database; no reasoning text or unrelated authentication tables were read. Thus the last reasoning-only/Length turn remains **unconfirmed** pending an authoritative run-agent response/message metadata capture.

For the remaining fresh Flash attempt, changing an actually supported response-output limit and reducing excessive reasoning is a plausible conservative mitigation of hypothesized truncation, not a proven codec fix or validation. Verify effective controls against the pinned model/agent configuration rather than inventing accepted limits. Retain the raw failure and bind the changed control/shorter implementation instructions; avoid repeating the identical run control without disposition. Codec/library edits or a paid transport probe are outside this review's authority. A fresh conversation avoids replaying malformed historical assistant turns but does not guarantee the failure cannot recur. No claim of corrected transport is supported until actual subsequent execution succeeds.

## Disposition

Preserve and export this failed attempt, three-file partial patch, provider rejection, absent reports/positive plan and bounded compatibility measurements. The goal remains unfulfilled. If the already authorized last original correction is admitted by the operator, its source must supply the actual bounded native backend and meaningful tests or report concrete inability. Do not use the separate #560 allowance, extend budgets, fix #250, infer qualification from tests or synthesize offline human acceptance.

## Input bindings at review snapshot

| Input | SHA-256 |
| --- | --- |
| `check-source-subjects.json` | `97e10c3b295cf690779cf89db4f72cd478e9b767693dd860209b254aabcda652` |
| `source-subjects.json` | `c3e94cfb474fecd542f2aa00f45b84d671e67ccd3117381c57c8fe40a46ba39a` |
| `correction-ledger.json` | `1b05849b7e7f394f9e342947ccff0a58fb8864c46290469dc9a6becc9bbe742a` |
| `live-stage-observation.json` | `ddc4a334b0829b9ff02ccd0df10fa845d40e911d75e31e4164122e2f76305913` |
| `supervisor-contract-review.md` | `f0cb5a6ac6868d8aded9fc756470c70bd6f78161ed28a00d9c2c2e1c3f21a7d9` |
| `jobs/1261/workflow.fabro` | `b24977a21adaa2824cf2463f12e4c933e5b9f7d5465fd34de185c6cfc7e296b1` |
| `common.rs` | `4d857204e5b97935d23ef9f24e95ad9836fff8e818b162327d590b35403a865c` |
| `concept.rs` | `9d8faec817c8aaa067a66677020060479312d4f5abbc2404971dff0d9d98bbf9` |
| `score_com.rs` | `3debad8129791505229c20b66db56c70b794393822287f7cbbdfff98f9a47db0` |
| `LoLa runtime.rs` | `46d7a0f5fc4236bb6a687400a660a25913e0f92bb5b45e5410c0db6d98e21042` |
| `pinned Lithos OpenAI Chat codec` | `8f008da963a1d2a0f4b5165e11eb822f6aa0386b857bd5b30c6f83166b84e2c4` |
| `pinned Pebble turn continuation` | `a6652cf0cf1e86483972e25a7a58f18eb5cd0f94f311b8acc17edb292d1a1543` |

Native execution and terminal observations are still in progress and intentionally not sealed by this source report. Frozen source subjects were verified independently; reference source files were read without modification or builds.
