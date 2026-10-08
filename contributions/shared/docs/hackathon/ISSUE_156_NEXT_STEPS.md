# Issue #156: Implementation Roadmap

This roadmap separates completion of the OpenSOVD faults resource from completion of the three-process cruise-control demo. Issue [#156](https://github.com/eclipse-opensovd/opensovd-core/issues/156) is the standard SOVD resource work; the demo additionally needs `cc-app`, the I1/I2 handover, data resources, and dashboard integration.

## 1. Agree the Fault Contract

Resolve these decisions before stabilizing public model types or routes:

- Define the DTC identifier encoding. The demo architecture uses a 24-bit UDS number; represent it consistently as six hexadecimal characters or as a validated 24-bit value.
- Preserve the full UDS status byte. Do not collapse status to an active/inactive enum or let the gateway synthesize confirmation and operation-cycle bits.
- Agree the `Fault` fields, severity type, and environment/freeze-frame schema, including timestamp, units, validity/quality, and versioning expectations.
- Define list status-mask filtering and its query parameter semantics, detail behavior, and provider-to-SOVD error mapping.
- Confirm clear semantics against ISO 17978-3. The architecture marks DELETE/clear as a stretch beyond #156; if added later, clearing must be a command to the DTC owner, not removal from only the gateway cache.
- Record which entity kinds may own faults. Start with `cc-app` as an App unless an ECU/component-level diagnostic owner is established.

**Exit criteria:** API model and route behavior agreed by maintainers; no demo-specific debounce or transport assumptions leak into OpenSOVD's core trait.

## 2. Complete Issue #156 Upstream

Implement the standard resource in the existing OpenSOVD layers rather than duplicating a standalone Axum API in the demo:

1. **`opensovd-models`:** Add serializable, schema-enabled fault list/detail types. Preserve the raw status byte and agreed DTC representation; model environment data using the agreed contract.
2. **`opensovd-core`:** Add an async, object-safe `FaultProvider`, list filter, provider error types, and public exports. The trait exposes diagnostic state; DTC detection and debounce remain in the source.
3. **Entity ownership:** Add optional provider storage, builder methods, and accessors to the agreed entity types. Follow the neighboring provider ownership patterns.
4. **`opensovd-server`:** Add collection/detail routes, validate status filters, map provider errors to SOVD error responses, and advertise `EntityCapabilities.faults` only when the entity has a provider. Respect configured base URI and mount path.
5. **Mocks and tests:** Add representative mock faults and test list, status filtering, detail/environment data, missing entity/provider/DTC, errors, schema generation, and capability URI advertisement.
6. **End-to-end and docs:** Cover the routes in `opensovd-e2e`; update API documentation and client support where appropriate.

**Exit criteria:** OpenSOVD's own server serves faults through the same topology/provider and discovery path as its other resources, with passing unit and end-to-end tests.

## 3. Freeze the Demo Handover

The diagram specifies I1/I2 as JSON-lines over a Unix socket. Freeze the interfaces before implementing either side, including replayable examples:

- `i1-sample.schema.json`: state sample every 100 ms, with source timestamp, four wheel speeds (if available), vehicle/set speed, cruise-control state, and torque request.
- `i1-dtc-event.schema.json`: DTC number, full status byte, severity, event timestamp, and event-time freeze frame; publish on status change.
- `i2-command.schema.json`: `set_wss_mode` and, if clear is in scope, `clear_dtc` commands with validation and response/error behavior.
- Add JSONL examples so `cc-app` and gateway can each be tested without the other process.

**Exit criteria:** Both teams agree on versioned schemas, timestamps, units, error handling, and compatibility rules.

## 4. Implement the `cc-app` Diagnostic Owner

Detection, confirmation, and UDS status transitions belong in `cc-app`/the S-CORE DTC backend, not the gateway:

- Integrate the S-CORE DTC API and implement the diagram's five-cycle debounce at the 20 ms monitor cadence.
- Resolve the wheel-speed input gap. The current checked-in cruise-control interface exposes a single ego-velocity signal, while the proposed median monitor needs four wheel speeds. Add and validate those inputs or agree on a monitor supported by available signals.
- Define enable conditions, signal quality/freshness, startup handling, thresholds/hysteresis, operation-cycle behavior, recovery/healing, and snapshot capture per DTC.
- Capture the freeze frame atomically at the failure edge; include source timestamp, units, and validity/quality. Do not reconstruct it from later samples.
- Make fault injection affect the actual source/function path, so the cruise controller reacts and transitions to INHIBITED as described by the demo.
- Emit timestamped I1 DTC events and 100 ms samples. The sample stream is also the gateway's liveness heartbeat.

The current `adas_s-core` source does not yet expose the diagram's four wheel speeds or DTC event interface. Do not assign standardized SAE/ISO codes to the demo identifiers without diagnostic-owner approval.

**Exit criteria:** An injected input degradation is detected and debounced by `cc-app`; it changes cruise state/torque behavior and emits an event with the correct status and freeze frame.

## 5. Implement Gateway Adapters and State

- Attach the upstream `FaultProvider` to the `cc-app` App entity and run it through the OpenSOVD server.
- Implement the I1 Unix-socket receiver. Update the local data/fault cache from source events and samples without changing source DTC status or timestamps.
- Use each 100 ms state sample to refresh source liveness, even when DTC events are unchanged. Once samples exceed configured max age, mark cached values stale, stop serving them as fresh, and expose a distinct communication-loss diagnostic.
- Implement I2 commands and correlated results. Data reads use the gateway cache; writes such as `wss-fl-mode` must travel to `cc-app` and return a meaningful result.
- If clear is added, send `clear_dtc` to the source and reflect the resulting source event/state. Do not treat a local cache delete as ECU clear.
- Keep the demo's #16 DataProvider/resources separate from the core #156 fault abstraction while wiring both into the shared SOVD server.

**Exit criteria:** Gateway works against recorded I1/I2 examples, serves only fresh data, and produces a communication-loss indication when `cc-app` or the link stops.

## 6. Verify the Complete Feature

Test in layers and use explicit acceptance criteria:

- Model serialization/schema round trips for 24-bit DTC identifier, status byte, severity, and environment data.
- Provider tests for filtering combinations, event updates, source timestamp preservation, max-age behavior, and unknown DTCs.
- Server tests for routes, SOVD errors, app capability discovery, and mounted/base URI handling.
- I1/I2 protocol tests using the JSONL fixtures, including malformed messages, disconnects, and restart/reconnect behavior.
- End-to-end tests for inject → degrade → DTC confirmation → cruise INHIBITED → GET faults/freeze frame → recovery. Use clear only if its upstream/API contract is agreed.
- Run `cc-app` and gateway independently against fixtures, then perform the full demo chain and test a killed `cc-app`/dropped socket.
- Protect write/clear operations with authentication and authorization; audit clear actor/reason/time. Disable or secure development ingestion endpoints before network deployment.

The current `contributions/eclipse-opensovd/OpenSOVD/legacy/crates` implementation is a FaultProvider prototype: its provider and local HTTP route tests do not cover the Unix-socket handover, `cc-app`, I3 data resources, or upstream OpenSOVD capability registration. These are completion gates, not assumed working behavior.