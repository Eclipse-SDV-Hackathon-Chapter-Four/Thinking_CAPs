# Improvement

> [!IMPORTANT]
> Submit this pull request as **Draft** until it is ready for committer review.

## Description

Adds `Runtime::find_all_services()`, an asynchronous stream of interface-independent
`ServiceDescriptor` items (service type name, version, binding, binding service id and instance id).

- The LoLa backend starts one find-any watch per service type in the loaded configuration
  (including add-on configurations merged before the stream is opened) and reports any concrete
  provider instance id.
- Already offered services are yielded first; an identity is yielded again when it is re-offered
  after a withdrawal.
- Pending items are coalesced: at most one per currently offered identity, discarded if the
  service is withdrawn before being polled. The backlog is bounded by the offered services, which
  mirrors the full-list semantics of the C++ `StartFindService` handler.
- The stream is infinite and ends when dropped, which stops every native watch. Discovery
  callbacks hold only a weak reference to the stream state.
- `IRuntime` gains `GetConfiguredServiceWildcardIdentifiers()`, declared last with a default
  implementation. `Runtime` serializes add-on configuration merges with the wildcard enumeration
  and invalidates its cache; returned identifiers stay valid in address-stable storage.
- Adds LoLa backend unit tests and the `all_services_stream` ITF integration test.

## Related ticket

Addresses #1261 (improvement ticket)

## Validation

Linux x86_64, Bazel 8.7.0, baseline `381d43de`:

- `//score/mw/com/impl:runtime_test` (17), `//score/mw/com/impl/configuration:configuration_test` (30),
  `com-api-runtime-lola-tests` (16 incl. 10 stream tests), `score_com_concept-test` (10),
  `score_com_concept-macros-unit-tests` (8): pass.
- ITF: `test_com_api_sync` (3), `test_com_api_async` (3), `test_find_any_semantics` (1) and the new
  `test_com_api_all_services_stream` (initial offer, later offer of a second interface, withdrawal
  with probe-confirmed boundary, exactly one re-offer item; exact identities): pass.
- `score_com_concept-macros-tests` (GCC 15 doctest): 16 pass, 2 ignored.
- Clippy on five libraries: exit 0, 4 warnings (3 on existing lines; 1 new:
  `service_stream.rs:234` transmute without annotations, same pattern as `consumer.rs:950`).
- Not run: QNX, Clippy on test code, clang-tidy/CodeQL, sanitizers.

## Notes for reviewers

- Scope: configured services only vs. 'system-wide' (D1) — question drafted for #1261, not posted.
- Operational-phase heap allocation in discovery callbacks (D6) — question drafted for #1261, not posted.
- Find-service callback boxes are not reclaimed (baseline `dispose` is empty) — separate issue drafted, not posted.
- Adding an `IRuntime` virtual is not binary compatible for prebuilt implementers (method appended last).
- `InstanceIdentifier::Create` also mutates the configuration outside the discovery mutex (baseline path).
- New Clippy warning at `service_stream.rs:234`; QNX, sanitizers, native trace, qualification and acceptance pending.

## Readiness follow-up — 2026-10-07

The follow-up supplies an explicit `FatPtr` conversion annotation. D1/D6, the appended-virtual ABI migration and inherited callback/analysis obligations remain pending.

The earlier validation above binds the original proposal. Supplemental warning
corrections and fresh measurements are supplied in the local readiness packet;
use its final candidate/source hashes for review. Scope/API/ABI, full applicable CI,
qualification and contributor ECA/IP acceptance remain open.

Final review artifacts: [merge requirements](../rust-api-queue/readiness-review-20261007/MERGE-ARTIFACTS.md), [current PR draft](../rust-api-queue/readiness-review-20261007/pr-drafts/1261.md) and [source-bound verification](../rust-api-queue/readiness-review-20261007/verification.json).
