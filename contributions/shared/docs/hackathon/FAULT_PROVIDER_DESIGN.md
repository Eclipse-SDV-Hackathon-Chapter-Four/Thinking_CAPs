# Fault Provider Design

## Scope and Source Material

This package implements a hackathon-side fault provider and runnable HTTP adapter under `contributions/eclipse-opensovd/OpenSOVD/legacy/crates`. It is based on OpenSOVD issue [#156](https://github.com/eclipse-opensovd/opensovd-core/issues/156) and the three pages of the attached draw.io architecture (Architecture, Demo flow, Repository layout).

The hackathon checkout had README placeholders, but no Cargo workspace or Rust implementation sources under `contributions/eclipse-opensovd/OpenSOVD/legacy/crates`. The code here creates those source files without replacing the existing S-CORE sources. The diagram is the controlling architecture: `cc-app` owns detection/debounce; the gateway is a timestamped, freshness-bounded translator/store; I1/I2 are JSON-lines over a Unix socket.

## Architectural Placement

The current OpenSOVD core architecture stores providers on topology entities. For this demo, `cc-app` is the producer of cruise-control diagnostics, so the provider is exposed at the app entity:

```text
S-CORE cc-app (adas_s-core)
  - 20 ms wheel check and cruise state machine
  - S-CORE DTC API owns five-cycle / 100 ms debounce
  - emits DTC status transitions and 100 ms state samples on I1
                  |
        I1/I2 JSON-lines over Unix socket
                  |
                  v
SOVD gateway
  - I1 cache keeps source timestamps and max-age
  - I2 sends set_wss_mode / clear_dtc back to cc-app
  - FaultProvider lists/reads fresh entity DTCs
                  |
                  v
OpenSOVD server on :7690
  - GET /sovd/v1/apps/cc-app/faults
  - GET /sovd/v1/apps/cc-app/faults/{code}
  - data writes use I2; data reads use gateway cache
```

If fault ownership is ECU-wide rather than app-specific, configure the same route adapter as `FaultEntityKind::Component` and attach it to the corresponding component. Avoid publishing the same DTC store independently on both app and component resources unless the API explicitly defines aggregation; duplicated views make clear and status semantics ambiguous.

In the upstream OpenSOVD model, `Component`, `App`, and `Area` can each optionally own providers. `cc-app` should initially own its diagnostic store as an `App`; an area-level faults resource should be an explicit aggregate, not an alias to one app's provider.

## Current cc-app Signals and Diagnostic Gap

The attached architecture proposes four wheel speeds, a median comparison every 20 ms, and an S-CORE DTC API that confirms failures after five cycles (100 ms). By contrast, the checked-in `adas_s-core/cc_s-core/score/cruise_control/src/cruise_control_types.h` currently exposes one `ego_velocity_sts` input, `ego_delta_speed_sts`, `vcu_cc_engage_sts`, and `sim_clock_sts`; it does not expose four wheel speeds, diagnostic status events, or a DTC API. The diagram itself flags this as an open decision: the existing CARLA input is a single speed, so the wheel median cannot yet be implemented without a source change.

Consequently, the provider does not infer an automotive fault from a speed value or from an HTTP request. The intended `cc-app` DTC backend must define and validate the failure monitor first. Candidate demo definitions in `main.rs` (`CC0001`, `CC0002`) are local 24-bit hexadecimal identifiers only:

| Demo identifier | Candidate monitor | Evidence needed before activation |
| --- | --- | --- |
| `CC0001` | Cruise input signal invalid/stale | Defined validity range, source timestamp or timeout, startup grace period, and confirmed signal-quality failure |
| `CC0002` | Cruise controller output unavailable | A real service-offer/send failure state with recovery behavior, not merely a log line |

These are not assigned SAE/ISO DTCs and must not be advertised as OBD-II codes. Do not map to a standardized code until the ECU diagnostic owner confirms the failure mode, market/application, and code allocation. The gateway must not debounce again: the five-cycle monitor and status transition belong to the S-CORE DTC backend in `cc-app`. Diagnostic thresholds and debounce periods are calibration/OEM decisions and require safety analysis where they influence driver-facing warnings or vehicle behavior.

Freeze-frame/environment data should be captured atomically at the failure edge from a coherent input snapshot. Include explicit units, source timestamp, and quality/validity information. Do not reconstruct the snapshot later from current values. The demo type currently carries a timestamp and signal-value map; production should add source identity, quality, units, and schema/version metadata.

## DTC Status Representation

The DTC identifier is represented as six hexadecimal characters (24-bit UDS number). `Fault.status` and the I1 DTC event use the full UDS status byte as an unsigned 8-bit value. The provider preserves the producer-supplied byte and event timestamp. It does not synthesize `confirmedDTC`, clear operation-cycle bits, or infer warning-indicator behavior.

| Bit | Mask | UDS status bit |
| --- | ---: | --- |
| 0 | `0x01` | `testFailed` |
| 1 | `0x02` | `testFailedThisOperationCycle` |
| 2 | `0x04` | `pendingDTC` |
| 3 | `0x08` | `confirmedDTC` |
| 4 | `0x10` | `testNotCompletedSinceLastClear` |
| 5 | `0x20` | `testFailedSinceLastClear` |
| 6 | `0x40` | `testNotCompletedThisOperationCycle` |
| 7 | `0x80` | `warningIndicatorRequested` |

List filtering uses `(status & statusMask) == statusValue`; `statusValue` must be a subset of `statusMask`. This supports combinations without reducing diagnostic status to a single active/inactive enum. UDS confirmation, operation-cycle, healing, aging, and permanent-DTC rules belong to the ECU diagnostic backend.

## Local API and Payloads

Run the gateway from `eclipse_sdv_hackathon_2026/sovd`:

```bash
cargo test
cargo run -p cruise-gateway
```

It binds to `127.0.0.1:7690` by default. `SOVD_BIND_ADDR` can override the bind address. The internal development ingestion endpoint accepts one status event. It is a temporary test bridge, not the architecture's I1 transport:

```http
POST /internal/fault-observations
Content-Type: application/json
```

```json
{
  "entity_id": "cc-app",
  "code": "CC0001",
  "status": 43,
  "timestamp": "2026-10-03T12:00:00Z",
  "severity": "high",
  "environment_data": {
    "captured_at": "2026-10-03T12:00:00Z",
    "signals": {
      "ego_velocity_kmh": 80.0,
      "vcu_cc_engage_sts": true
    }
  }
}
```

Producer-confirmed events are immediately visible. The provider uses a 5-second source-liveness max age in the binary: stale list/detail requests return `503` instead of presenting stale data as current. A future I1 sample handler must call `mark_source_alive()` every 100 ms; the current temporary HTTP bridge does not yet provide that sample path.

```http
GET /sovd/v1/apps/cc-app/faults?statusMask=1&statusValue=1
GET /sovd/v1/apps/cc-app/faults/CC0001
```

The `DELETE` routes are local prototype conveniences and currently clear only the gateway cache. The diagram marks DELETE/clear as a stretch beyond #156 and requires `clear_dtc` to travel back to `cc-app` on I2. Do not use the current DELETE handlers as the vehicle clear path or represent them as certified SOVD conformance.

## Diagram Conformance Check

| Diagram contract | Current package | Result |
| --- | --- | --- |
| `cc-app` owns 20 ms detection and five-cycle DTC debounce | Provider accepts producer-confirmed status events immediately | Aligned at provider boundary; actual DTC backend is absent from checked-in `cc-app` source |
| I1 emits timestamped DTC status events and 100 ms samples | Temporary `POST /internal/fault-observations` only | Not aligned; Unix-socket JSON-lines listener and sample cache are not implemented |
| Gateway state has source time and max-age; stale is never presented as fresh | Provider preserves event time, applies five-second source-liveness max-age, and has a sample heartbeat hook | Partially aligned; no I1 sample receiver calls the hook |
| I2 sends `set_wss_mode` and `clear_dtc` to `cc-app` | No I2 socket/client; DELETE mutates local cache | Not aligned; clear must become a source command, and data writes are not implemented here |
| FaultProvider list/status-filter and get-by-code | Implemented in the demo provider/routes | Aligned as an isolated prototype |
| OpenSOVD server advertises `faults` on entity capabilities | Standalone Axum routes only | Not aligned; upstream #156 model/entity/server work remains |
| `cc-app` has four wheel speeds for median monitor | Current S-CORE interface has a single ego-velocity input | Diagram open decision; extend source input or choose another monitor |

This package is therefore a **FaultProvider prototype**, not the full three-process architecture in the drawing. The next architecture-complete step is to freeze `interfaces/i1-sample.schema.json`, `interfaces/i1-dtc-event.schema.json`, and `interfaces/i2-command.schema.json`, then implement the Unix-socket bridge against those contracts in both `cc-app` and the gateway. The 100 ms sample must be a liveness heartbeat so an unchanged DTC does not age out merely because events are emitted only on status changes. When samples stop, the gateway should mark all cached values stale and raise a distinct communication-loss fault.

## Upstream OpenSOVD Work Required

The local gateway is runnable independently, but it does not make the unmodified `opensovd-core` advertise `EntityCapabilities.faults`. Completing issue #156 upstream requires coordinated changes:

1. In `opensovd-models`, add serializable/schema-enabled `Fault`, `FaultList`, and detail/clear request/response types. Preserve the raw status byte and 24-bit identifier. Define the normative field names, status filters, environment-data shape, and clear method against ISO 17978-3 before finalizing the public API.
2. In `opensovd-core`, add an object-safe async `FaultProvider` trait with list/read/clear operations, typed filter/error types, and exports. Avoid forcing a backend-specific debounce into the core abstraction.
3. Add optional fault-provider ownership/builders/getters to entity types. Use the same provider ownership convention as the neighboring data/bulk-data providers; ensure handlers can safely await provider calls without holding topology locks longer than the established server pattern.
4. In `opensovd-server`, add routes for supported entity kinds, validate query filters, map provider errors to SOVD generic errors, and include a `faults` URI in entity capabilities only when a provider exists. Include base URI/mount-path behavior in the URI builder.
5. Add a mock fault provider and realistic DTC fixtures. Include list, status-mask filter, detail/environment data, unknown DTC/entity/provider, clear, URI advertisement, schema, and error-mapping tests. Add end-to-end tests in `opensovd-e2e`.
6. Update OpenAPI/schema generation, user/API docs, client support where relevant, and security/authz policies.

Keep the hackathon application provider behind a small adapter so it can implement the upstream trait after that API lands. Do not fork or vendor all of OpenSOVD into this hackathon repository just to make the demo compile.

## Automotive and Security Requirements Before Vehicle Integration

- Keep diagnostic detection and UDS state transitions in the ECU/diagnostic owner; SOVD transports and exposes them. Never use the SOVD provider as a safety monitor or closed-loop control input.
- Add per-DTC monitor specification: enable conditions, threshold/hysteresis, debounce, operation-cycle semantics, healing/aging, confirmation, warning request, and environment-data capture rules.
- Define startup, missing/stale input, clock discontinuity, service restart, and communication-loss behavior. Missing samples must not silently look like a passing test. The 100 ms sample stream is the liveness signal; do not age an unchanged DTC using only its last status-change timestamp.
- Use durable storage or the ECU as the source of record if DTCs must survive gateway restart. This demo is in-memory and loses fault history on restart.
- Protect fault clear with authentication, authorization, diagnostic session/security access as required, and auditable actor/reason/time. Protect or disable `/internal/fault-observations` outside the local demo. The default loopback bind is not sufficient protection if deployment overrides it to a network interface.
- Rate-limit and validate ingestion; bound code, signal count, payload size, and environment-data values. Avoid logging sensitive vehicle/user data.
- Add freshness/source timestamps and expose degraded/stale provider health rather than serving old data as current.
- Validate all method/path/status semantics against the licensed normative standard and the OEM diagnostic specification. The implementation is a functional prototype, not a homologation or ISO-conformance claim.

## Package Structure

```text
eclipse_sdv_hackathon_2026/
  contributions/eclipse-opensovd/OpenSOVD/legacy/
    Cargo.toml
    Cargo.lock
    crates/
      cruise_diag/
        Cargo.toml
        src/lib.rs
      cruise-gateway/
        Cargo.toml
        src/lib.rs
        src/main.rs
  interfaces/ (required next: I1/I2 JSONL schemas and replay examples)
  contributions/shared/docs/hackathon/FAULT_PROVIDER_DESIGN.md
```