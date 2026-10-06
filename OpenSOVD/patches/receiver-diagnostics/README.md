# Actual receiver observation patch

Base: The-Xverse/adas_s-core 93f8ea1e6f76714496c092902e00c9b91c58cdc8.
Prepared integration-owned instrumentation, not a published upstream contribution.
Apply `s-core-observation.patch` with `git apply` in an isolated base checkout; build
`//score/cruise_control:cruise_control_main` and run its existing unit tests.

Enable `SCORE_DIAGNOSTIC_SOCKET` with the local provider's shared socket path and
`SCORE_BUILD_IDENTITY=sha256:<actual binary digest>`. Unset socket disables emission;
unset identity is reported as unknown. Linux boot ID and CLOCK_MONOTONIC are required.
Send failure drops observations; it never waits for diagnostics. Actual controller decisions
and established bridge source are preserved. Received/accepted speed clocks are per-event.
Acceptance is decode success in existing consumer semantics, not E2E or functional validation.

Sender boundary test: compile `test_sender.cpp` with C++17 and include the patched `src/`
directory; run the resulting executable. It exercises missing/full receiver queues and delivery.
Native provider/integration evidence: OpenSOVD/specs/002-receiver-diagnostics/completion.md.
