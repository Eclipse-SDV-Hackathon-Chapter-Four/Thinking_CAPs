# Offline recovery review: communication #1261

**Technical disposition: incomplete. No implementation run or source correction is authorized by this plan.** The existing three-correction allowance is exhausted. This review turns the sealed failures into concrete work items for an authorized engineer; it does not supply engineering acceptance.

## What failed and what remains unmeasured

The first measured failure is the removed `Runtime::MergeAdditionalConfiguration` function signature in `runtime.cpp`. Its body starts at file scope on line355. GCC rejected that block before any selected test executed. One of four selected command groups was attempted; zero of five test targets executed. Three later groups were unexecuted.

The new integration target was independently omitted: the agent wrote `score/mw/com/test/basic_rust_api/regression-plan.json`, but the collector reads `.rust-queue/reports/regression-plan.json`. Even a successful compatibility build would leave the required positive-regression guard unsatisfied. The required implementation report was also placed in the source tree rather than the report directory.

The final Codex review identifies additional source and coverage concerns. Restoring the C++ signature and correcting report paths would address the first two blockers, but would not complete the issue. Static Rust application import/type-inference concerns are unverified, not measured compiler errors.

## Concrete recovery work, if separately authorized

1. **Restore compilation without changing merge behavior.** Restore the missing `Result<void> Runtime::MergeAdditionalConfiguration(const Configuration& additional_configuration) noexcept` definition signature immediately before its existing body. Preserve the wildcard-enumeration method as a separate function. Check the new provider's `OfferedProducer` import, the consumer's `Builder` import and explicit `LolaRuntimeBuilderImpl` type annotations against native maintained application patterns. Confirm any Rust diagnostic with the actual target before calling it a measured defect.

2. **Select the intended regression.** Produce the regression plan and implementation report at the exact paths required by the trusted driver. Confirm the effective plan includes `//score/mw/com/test/basic_rust_api/all_services_stream/integration_test:test_com_api_all_services_stream`, alongside `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests`. Those labels are recorded in the source proposal; they have no successful result for this candidate. Correct report placement must not be represented as proof of test adequacy.

3. **Resolve the stream contract before claiming system-wide coverage.** The current backend enumerates configured LoLa types with instance entries at first opening. It excludes unconfigured types, configured types lacking instances, non-LoLa bindings and subsequent configuration additions, and chooses one configured quality context per type. Either implement the issue's broader scope using demonstrated native capabilities or retain this as a narrower proposal requiring an authorized engineering disposition. Do not rename configured-only behavior as system-wide compliance. Preserve native requirement IDs/statuses when identified; none are invented here.

4. **Define bounded memory and sound callback ownership.** An unpolled sequence of withdrawal/re-offer transitions appends indefinitely to `VecDeque`, even with one currently offered instance. Repeated openings retain callbacks through the inherited empty dispose hook. Determine a native-compatible capacity/allocation and overflow/error contract; do not silently drop notifications or invent a capacity as policy. Prove callback cleanup against native stop's deferred deletion before freeing shared state. A stop request is not evidence of callback quiescence. Keep stable Runtime-owned deployment lifetimes and stop calls outside membership locks.

5. **Make verification discriminating.** Compare unordered identity sets in unit assertions. Use explicit provider/consumer phase coordination so initial, initially empty, later-offer, withdrawal and re-offer phases are observable. Assert exact full identities, suppress unchanged/overlapping offers and require a verified withdrawal boundary before counting re-offer. Minimum aggregate counts can pass with duplicates. Let the consumer return normally or explicitly drop its stream so native cancellation is exercised; `process::exit` bypasses stack Drop. Cover never-polled/pending Drop, partial-start rollback and failed-stop/error behavior with meaningful native or mock evidence, identified separately.

6. **Measure once against the changed subjects.** Bind the selected Linux toolchain, source vector, check plan and configurations before verification. Measure the dedicated integration and units, then relevant compatibility, doctest and library Clippy groups. Preserve the first failure and all unexecuted checks. Historical94passed cases from the preceding candidate are not fresh proof for this changed backend. Required supported dynamic checks, downstream combinations and qualification/applicability remain explicit until native evidence establishes them. This review does not prescribe unverified CLI commands or a new retry allowance.

## Acceptance mapping

| Issue obligation | Current disposition | Evidence needed |
| --- | --- | --- |
| Continuous discovery across different interfaces throughout the system | Configured-only proposal; compilation failed | Accepted scope disposition or broader native capability, discriminating real lifecycle integration |
| Identify service and interface | Owned identity proposed; fields not fully asserted | Full real identity/version/binding/instance and collision-sensitive checks |
| Document initial results, errors and lifetime/termination | Partial contract; unbounded history and retained callback state | Agreed memory/error contract, actual cancellation/rollback/quiescence measurements |
| Preserve interface-scoped APIs | Methods remain; compatibility unverified | Existing scoped integration/downstream checks and explicit IRuntime/FFIBridge ABI/source disposition |

These are issue obligations from the sealed snapshot, not invented native requirement identifiers or authenticated acceptance. The issue template's unchecked design field and its architecture checkbox do not establish applicability.

## Persistent limits

#1261 and #250 are stopped at3/3corrections. Originalqueue35/36used; the remaining original slot belongs only to#173, whose assessment is already refreshed. Extra Codex#560allowance has1/3used and is560-only. Generic “go”/“resume” does not reset or transfer these counters. Native agent runs remain DeepSeek Flash only under the existing model preference; this offline Codex review made no model dispatch, native source edit, build/test rerun or publication. All owned services remain stopped.

Review inputs were individually hashed against the unchanged sealed manifests. Complete raw evidence remains in the original packet; only selected evidence was reread. Use `input-binding.json` for exact packet paths and digests.
