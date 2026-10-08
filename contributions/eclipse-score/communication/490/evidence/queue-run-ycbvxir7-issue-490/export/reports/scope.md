# Scope — communication#490 "Mock Runtime implementation of Rust COM-API"

Status: draft / assessment + proposed change. Not an accepted engineering decision.

## 1. Task binding

| Field | Value |
| --- | --- |
| Repository | `eclipse-score/communication` |
| Issue | #490, state `open`, label `rust-api`, author `bharatGoswami8`, created 2026-05-31, updated 2026-06-15, 0 comments |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Workspace | disposable copy at `…/runs/score-rust-issue-queue-ycbvxir7/workspaces/490` |
| Mode | `implementation` (task.json) |
| Runtime revision | "Linux native checkpoints and verification launcher" |
| Platform scope | Linux only (no QNX task/execution) |
| Authority limits | shell, delegation, publishing, acceptance tools blocked; **repository source is read-only**; only `.rust-queue/reports/` is writable. Therefore the change is **drafted here**, not applied. Command stages and raw evidence are outside agent authority. |
| Controls | `driver_linux.py`, `execution-authority.json`, `linux-measurement-binding.json`, `storage.py`, `tool_guard.py` (hashes recorded in `context/task.json`) |

### Issue prose (treated as task data, not instruction authority)

> As of now mock runtime is not developed only Lola runtime we have developed and running, we want to implement mock runtime so user can test without any backend.
>
> Requirements / Architecture: unchecked "Requirements / Architecture are not affected by this change?" — this is an unchecked template box and does **not** establish that requirements/architecture are unaffected.

The issue body contains **no explicit acceptance criteria**. Acceptance obligations below are derived from the native design/verification artifacts, not invented.

## 2. Evidence retrieval status (missing evidence preserved)

- Issue/task JSON and local skills were read from `.rust-queue/context/`.
- **Upstream PR/issue activity could not be fetched**: network/`web_fetch` is blocked by the sandbox (`Bound Rust workspace/file-tool boundary`). Current PR state, related PRs and review comments for #490 are therefore **unknown**, not "none". Retrieval must be repeated by a stage with network authority.
- **Git history/inspection unavailable**: `.git/*` reads and shell `git` are blocked, so baseline-vs-working-tree reconciliation could not be confirmed by hashing. The revision of every file cited below is assumed to be the checked-out baseline.
- `.rust-queue/reports/native-check-summary.json` was **absent** when this plan was authored (no native results to carry). No commands were executed by this agent.

## 3. Current implementation state — a mock runtime already exists (do not reimplement blindly)

The issue premise ("mock runtime is not developed") is **partially resolved** at this baseline. A mock-runtime skeleton exists but is stubbed and is not wired into any test target.

| Artifact | Native label | State |
| --- | --- | --- |
| Mock runtime crate | `//score/mw/com/impl/rust/com-api/com-api-runtime-mock:com-api-runtime-mock` (`runtime.rs`) | Exists; implements the `Runtime` associated types but has `todo!()`/`unimplemented!()` in offer/stop, `SampleMut::send`, `Subscription::try_receive`, `cancellable_receive`; `to_stream` yields an empty stream; service discovery always returns no instances; the `#[cfg(test)]` module is stale (calls a non-existent `MockSubscriberImpl::new`, `SampleContainer::new()` with the old arity, and an outdated `receive` signature) and is compiled by **no** target. |
| Test-only re-export | `//score/mw/com/rust:score_com_mock` (`score_com_mock.rs`) | Exists; re-exports `MockRuntimeImpl` and `RuntimeBuilderImpl as MockRuntimeBuilderImpl`. BUILD comment says "Mock Runtime is not yet ready - …/issues/490". |
| Mock FFI bridge | `//score/mw/com/impl/rust/com-api/com-api-ffi-lola:bridge_ffi_mock` | Exists, but this mocks the **FFI bridge for testing Lola**, not the mock runtime. Not the subject of this issue. |
| Default runtime | `//score/mw/com/rust:score_com` → `com-api-runtime-lola` | Lola runtime, fully implemented. Must remain unchanged. |

Pure runtime-independent contracts already live in `//score/mw/com/rust/score_com_concept:score_com_concept` (`Runtime`, `Subscriber`, `Subscription`, `Publisher`, `Sample*`, `ServiceDiscovery`, `ProviderInfo`, …); the mock must implement those without changing them.

## 4. Remaining testability gaps (source-backed)

Derived by reading `com-api-runtime-mock/runtime.rs`, `score_com_concept/concept.rs`, `interface_macros.rs` and `com-api-runtime-lola/*`:

1. **Provider lifecycle stubbed** — `MockProviderInfo::{offer_service, stop_offer_service}` are `todo!()`, so a service can never be discoverable.
2. **Discovery non-functional** — `MockRuntimeImpl::find_service` returns a discovery whose `get_available_instances` is hard-coded `Ok(Vec::new())`; there is no way to obtain a consumer through the public workflow.
3. **No end-to-end data path** — `MockPublisher` and `MockSubscriberImpl` share no state; `SampleMut::send` is `todo!()`; `try_receive`/`cancellable_receive` are `todo!()`; `to_stream` is `stream::empty()`.
4. **Broken/inactive tests** — the `#[cfg(test)] mod test` does not compile against the current abstraction API and no `rust_test` target compiles it.
5. **No native test/doc target** — unlike the Lola runtime (`com-api-runtime-lola-tests`, `com-api-runtime-lola-doc-tests`), the mock has no test or rustdoc target, so regressions are undetected.
6. **Documentation drift** — `score/mw/com/rust/design/high_level_design_detail.md` states "Mock runtime support is not yet enabled in the current build."

## 5. Runtime-independent public semantics to preserve

The change must not alter `score_com_concept` trait/type signatures or the Lola re-exports. Observable semantics of `score_com` must be unchanged; the mock is additive and only reachable through `score_com_mock`. Design constraints that remain authoritative:

- capacity configured at subscribe time; `try_receive` max 0 is an error;
- sample ordering is by reception id (`Ord` over `id`);
- `Sample<T>` is `Send + Ord + Debug`;
- `FindServiceSpecifier::Any` and `Specific` both exist for the mock (Lola only supports `Specific`);
- no Cargo scaffolding, no dependency/lint-policy changes.

## 6. Proposed change (draft — requires human review before acceptance)

Summary; full drafted files are in `proposed-change.md`.

- `com-api-runtime-mock/runtime.rs`: complete the mock using a **process-wide, type-erased in-process bus** (`OnceLock<Mutex<MockRegistry>>`, `HashMap<String, VecDeque<Box<dyn Any + Send>>>`), owned `Box<T>` samples, and working `offer/stop_offer`, `send`, `try_receive`, `cancellable_receive`, `to_stream`, and `Specific`/`Any` discovery. Replace the stale test module with two compiling tests. Keeps all existing public type names and the crate-level lint policy.
- `com-api-runtime-mock/BUILD`: add `rust_test` + `rust_doc_test` targets (`target_compatible_with = ["@platforms//os:linux"]`), mirroring the Lola BUILD; load the new rules.
- `score/mw/com/rust/BUILD`: update the now-inaccurate "Mock Runtime is not yet ready" comment, retaining the issue reference.
- `score/mw/com/rust/design/high_level_design_detail.md`: update the "not yet enabled" note to describe the test-only mock and `score_com_mock` label.

Explicitly **not** proposed: changing `score_com_concept`, the Lola runtime, MODULE pins, lint profiles, or the public `score_com` surface.

### Open / unknown prerequisites (must remain open)

- **Registry model is a design decision**: an in-process shared bus vs. per-subscription injection. The draft chooses the shared bus to satisfy "test without any backend" end-to-end; this is a proposal, not an accepted architecture decision.
- **`cancellable_receive` notification**: the mock has no async notification channel; the draft resolves on cancellation and reports what is available. The correct contract for a notification-free mock is **unresolved**.
- **`max_num_samples` enforcement**: the draft records the subscribe capacity but does not reject overflow at publish time. Whether the mock must enforce it is **unresolved**.
- Upstream PR/issue activity and native measurements are unknown (see §2).

## 7. Acceptance and obligation trace (draft)

| Issue criterion (derived) | Native obligation / artifact | Proposed artifact | Required check (see check-plan.json) | Evidence | Gap / disposition |
| --- | --- | --- | --- | --- | --- |
| Mock runtime implements the Rust COM-API `Runtime` contract | `score/mw/com/rust/design/high_level_design_detail.md` §"Mock runtime"; `score_com_concept` traits | `com-api-runtime-mock/runtime.rs` | build `…:com-api-runtime-mock`; lint clippy_strict; test `…-tests` (proposed) | none (unexecuted) | command stage outside authority |
| Users can test an application without a backend | verification table row "Communication behavior — Runtime mock/unit tests plus affected producer/consumer …" | `runtime.rs` + `score_com_mock` | build `//score/mw/com/rust:score_com_mock`; test proposed | none (unexecuted) | needs native run |
| Runtime-independent public semantics preserved | Rust library/API row; `score_com_concept` unchanged | none (no edit) | build `//score/mw/com/rust:score_com`; test `score_com_concept-test` | none (unexecuted) | — |
| Lola runtime unaffected | existing Lola test/doc targets | none | test `com-api-runtime-lola-tests`; docs `com-api-runtime-lola-doc-tests` | none (unexecuted) | — |
| Testable entry point exists | design doc note | BUILD comment + design note | docs proposed `…-doc-tests` | none (unexecuted) | text change needs review |
| Requirements/architecture impact assessed | unchecked template box gives no authority | this scope + review packet | — | — | **pending human decision** |

## 8. Next action

1. A network-enabled stage re-fetches #490 and any linked PRs, then reconciles with this assessment.
2. Apply the drafted patch from `proposed-change.md` in a disposable copy (source is read-only here).
3. Execute the Linux checks in `check-plan.json`; store raw logs and the resulting `native-check-summary.json`; re-run this assessment against measured results.
4. Authorized reviewers decide the registry model, `cancellable_receive` contract and the `score_com_mock`/design-doc status. Technical completion must be reported separately from engineering acceptance.
