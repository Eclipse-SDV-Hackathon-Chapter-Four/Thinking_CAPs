# F002 research

Decision: Unix datagram observer from native receiver/controller, cached provider using actual
OpenSOVD traits. Rationale: no supported Rust mw::com binding is present; private controller state
requires minimal instrumentation; publisher-side observations cannot establish consumer acceptance.
Alternative: log scraping lacks per-event freshness and callback coherence.

Decision: Linux CLOCK_MONOTONIC + boot ID + process-start session. Rationale: producer and
provider must share a clock domain; CARLA simulation timestamps are payload only.
Alternative: cross-host nanosecond comparisons are invalid without synchronization evidence.

Decision: per-speed received and accepted timestamps. Extractors return decode success solely
to observation metadata; existing control callback policy remains untouched. No inferred E2E.

Decision: native OpenSOVD App data resource under actual configured base URI. Rationale:
F001 stable check passed for core/providers/server. Native faults routes are absent and excluded.

Decision: freshness budgets configured by CLI; not engineering-accepted deadlines. Rationale:
no stable closed-loop jitter run yet. Timeouts remain provisional in the run manifest.
