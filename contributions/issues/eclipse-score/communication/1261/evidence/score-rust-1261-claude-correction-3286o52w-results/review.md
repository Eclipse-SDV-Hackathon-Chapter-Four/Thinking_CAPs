# #1261 Claude correction: measured result

**Outcome: all four selected Linux groups passed on attempt 3/3.** That includes the dedicated
heterogeneous-stream integration, which no previous candidate ever ran. This is technical
completion of the selected checks only. It is **not** engineering acceptance, issue closure or
qualification. Those remain pending offline with authorized humans.

## Authority and limits

- **Authority.** The user said "fix them by yourself" in this Claude Code session on 2026-10-07.
  This came immediately after a review that said repairs R1–R7 needed explicit new #1261 authority
  naming an editor. I interpreted it as a new **#1261-only** allowance for Claude, outside Fabro,
  capped at three corrections to match the user's standing limit.
- **Usage.** All three were used: **3/3, STOP.** The ledger is `runtime/correction-ledger.json`.
- **Unchanged.** Original #1261 3/3, #250 3/3, original queue 35/36 (#173's slot), and #560
  Codex extra 1/3.
- **Not done.** No Fabro run, no DeepSeek or other paid model dispatch, no commit, push, PR,
  issue comment or publication. No sealed packet was modified.

## Subject

- **Base.** Baseline `381d43de…` plus the sealed candidate patch `7edc8620…`. A fresh clone
  matched all 2,889 sealed subjects with zero mismatches.
- **Correction.** `export/claude-correction-vs-candidate.patch` (`d2b8a2af…`): 10 files,
  +462/−306.
- **Full proposal.** `export/communication-1261-full.patch` (`016985d4…`).
- **Subject vector.** `runtime/final-source-subjects.json`: 2,887 subjects, 8 changed,
  2 removed relative to the candidate.

## What changed

| Item | Change |
| --- | --- |
| R1 | Restored the `Runtime::MergeAdditionalConfiguration` definition signature that the candidate's diff splice removed (`runtime.cpp`) |
| D5/N3 | The merge now takes `discovery_identifiers_mutex_` and invalidates the wildcard cache. Streams opened after an add-on merge see the new types, and earlier identifiers stay valid in the address-stable deques. |
| D4/N2 | `GetConfiguredServiceWildcardIdentifiers` moved to the **end** of `IRuntime`, so pre-existing vtable slots keep their positions. The ABI break of adding a virtual is still documented. |
| R4/N1 | Callback closures capture `Weak<StreamState>`. The leaked find-service box (inherited empty `dispose`) no longer keeps the queue or maps alive, and a late callback is a no-op. |
| R5/D2/S1 | Pending items are **coalesced**: at most one per currently offered identity, dropped on withdrawal. The backlog is bounded by the offered set, so no capacity was invented. |
| R3/S2 | The HashSet-order unit assertion was replaced by an unordered comparison that checks identity fields on every item |
| — | New unit tests: unpolled flapping (2×1000 cycles) stays bounded; pending never exceeds offered; callbacks hold no strong references and the state is freed on drop |
| R6/N5 | Module and `find_all_services` API docs now state the configured-universe scope, the coalescing, that LoLa yields no runtime `Err` items, and that the stream is infinite and ends only on `Drop` |
| R7/S3 | Integration rewritten as four marker-synchronized phases with exact five-field identities, quiet windows against duplicates, a probe-stream-confirmed withdrawal boundary, and a normal `Drop` instead of `process::exit` |
| R2 | The misplaced `regression-plan.json` and `implementation.md` were removed from the native tree and preserved in `superseded-candidate/`. The dedicated target is in the check plan. |
| S5 | The integration apps import `Builder` and `OfferedProducer`, and annotate `LolaRuntimeBuilderImpl` the way baseline apps do |

## Measured verification

The runs used Bazel 8.7.0 (`d7606e67…`) in bwrap with the recorded runtime overlays, on the SSD
Linux image. Integration tests used an **owned rootless Docker** daemon whose data root was on the
SSD; it was stopped afterwards (`runtime/docker-shutdown.json`). The plan is
`runtime/check-plan-claude.json`. Attempts 1 and 2 are kept as failure history.

| Attempt | Group 1 units | Group 2 integration | Groups 3–4 | Cause |
| --- | --- | --- | --- | --- |
| 1 | 5/5 pass | 0/4 executed, build failed | not run | `E0599`: `Builder` trait not in scope (`consumer_app.rs:176`), which measured static concern S5 |
| 2 | 5/5 pass | 0/4 executed, build failed | not run | `E0283`: type annotations needed for `LolaRuntimeBuilderImpl<_>`, the second S5 hazard |
| **3** | **5/5 pass** | **4/4 pass** | **doctest pass; Clippy exit 0** | — |

Attempt 3 actual child cases:

- C++ `runtime_test`: 17.
- `configuration_test`: 30.
- `com-api-runtime-lola-tests`: 16 Rust tests, including all 10 `service_stream` tests.
- `score_com_concept-test`: 10.
- `score_com_concept-macros-unit-tests`: 8.
- `score_com_concept-macros-tests` (GCC 15 doctest): 16 passed, 2 ignored.
- `test_com_api_sync` and `test_com_api_async`: 3 cases each.
- `test_find_any_semantics`: 1.
- `test_com_api_all_services_stream`: 1 ITF case.

Total: 105 executed child cases passed, 0 failed, and 2 doctests ignored.

The dedicated integration log shows every phase asserted on real LoLa discovery:

1. **Initial result.** The first item was `type=/score/adp/MapApiLanesStamped version=1.0 binding=lola service_id=6432 instance_id=2`.
   Instance 2 is absent from the consumer manifest.
2. **Later offer.** The next item was `type=/score/test/MixedPrimitivesInterface version=1.0 binding=lola service_id=7001 instance_id=1`.
3. **Withdrawal.** It produced no item. Probe stream 1 confirmed the boundary, and the long-lived stream stayed quiet.
4. **Re-offer.** Exactly one item arrived, with the identical BigData identity.

The provider and consumer each logged `OK`. This **measures N4**: on withdrawal, native LoLa
discovery delivers the snapshot that withdrawal/re-offer detection depends on.

Clippy (five libraries) reported 4 warnings and failed nothing. Three are on baseline lines:
`consumer.rs:950` transmute, `consumer.rs:1164` clone-on-Copy, and `bridge_ffi.rs:262`
`Result<_, ()>`. **One is new:** `service_stream.rs:234`, "transmute used without annotations".
It is the same pattern as baseline `consumer.rs:950` and was **not fixed** because the
allowance is exhausted. No SARIF files were produced; the analyzer evidence is the raw lint log.
Test-code Clippy, C++ static analysis (clang-tidy, CodeQL), sanitizers, QNX and coverage were
not run.

## Issue criteria (snapshot) and remaining obligations

| Criterion | Measured state | Still open |
| --- | --- | --- |
| Newly available services "system-wide" | Configured LoLa universe, measured across 2 interfaces including an instance absent from the consumer manifest | **D1**: the human scope decision. Unconfigured types and non-LoLa bindings are not observed. |
| Identify service and interface | All five identity fields asserted exactly | Whether a quality-of-service selector belongs in the descriptor (open design question, unchanged) |
| Document initial results, errors and lifetime | Documented and measured: initial result, coalescing, no runtime errors, infinite stream, normal `Drop` | Human acceptance of the coalescing contract (**D2**) and of error semantics |
| Interface-scoped APIs preserved | Sync, async and FindAny integration plus units pass | ABI disposition (**D4**). Adding a virtual still breaks binary compatibility for prebuilt `IRuntime` implementers, and `FFIBridge` is extended. |

Further open items:

- **D3.** Native find-service callback reclamation is baseline-wide; it is not fixed here and
  only mitigated by `Weak`.
- **D6.** Running-phase allocation policy for callbacks is unknown.
- **Residual race.** `InstanceIdentifier::Create` deserialization also mutates `configuration_`
  outside the discovery mutex. This is a baseline path and not addressed.
- **Lint.** The new transmute warning remains.
- **Pending.** QNX, native requirement/design/safety trace, tool qualification, and offline human
  engineering acceptance. No native requirement IDs were invented.
