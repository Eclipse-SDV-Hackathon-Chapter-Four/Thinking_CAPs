# Inspected integration interfaces

## Vehicle/control path
Existing Zenoh bridge mapping: clock_status string seconds -> native float32 milliseconds,
velocity_status string km/h -> native float32, delta_speed string km/h -> native float32,
and vcu/control/cc_engage_sts string -> bool. SOME/IP input service 4660, instance 1,
events/eventgroups 30500–30503. Preserve the established native byte order.

Gateway maps these to SHM service 8000 `/cruisecontrol/CruiseControlInput`, instance `cc/input`.
The receiver stores sim timestamp, ego velocity, delta speed and engagement request.
Controller engagement and target speed are private actual application state. Output SHM service
8001 `cc/output` becomes SOME/IP 3000/1 events 30600 and 30601 and returns through the bridge
as `adas/cruise_control/target_speed` and existing spelling `adas/cruise_control/thruttle_req`.
Never silently rename the return signal.

Control loop period is 50 ms. Current input summary logging is limited to 500 ms.
On engagement the controller captures current speed as target; delta commands adjust it;
disengagement clears it. Current code has no demonstrated communication-loss disengagement.
An observer timeout MUST NOT fabricate that state transition.

## Required new observation boundary
Add per-event receive/accept timestamps after the actual decode, sampled controller state
and immutable build identity. Existing `last_input_time_` refreshes across unrelated events
and cannot detect loss of only speed. Record unavailable sequence/E2E instead of inventing them.
Use Linux CLOCK_MONOTONIC and boot ID for co-located collector/provider; reject other clock domains.
Transport observation must distinguish malformed receipt from accepted data.
Prefer bounded nonblocking Unix datagrams to an independent timestamped cache. Socket unavailability
must not block control; HTTP never synchronously reads `mw::com`.

## Native OpenSOVD
Pinned source has `Component`, `App::with_component_id`, `DataProviderBuilder::read_data`,
`ReadableDataResource` and `Server::builder().base_uri(...).listener(...).topology(...)`.
Use these APIs, attach a receiver data resource to a Cruise Control App on the S-CORE component,
and discover advertised links. Router supports versioned data resources; native faults are
not in the inspected router. Fault-data exposure is not native /faults support.

## openDuT and update
openDuT connects Ethernet endpoints, not application-level proxies. Preserve a separate
management/diagnostic route during test-flow interruption. See source-based deployment research.
AAOS FOTA asset will arrive later; target/operations/version contract intentionally deferred.
