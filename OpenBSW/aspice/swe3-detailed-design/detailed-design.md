# Software detailed design (SWE.3)

The software units are source files, or cohesive parts of them, allocated to
the architecture elements in [SWE.2](../swe2-architecture/architecture.md).
The diagrams in [diagrams/](diagrams/) show the units with non-trivial
control flow.

The code lives in three places:

- **Contributed module:** `contrib/libs/bsw/transportRouter` (DD-01 … DD-04). It is generic OpenBSW code and the subject of the upstream contribution.
- **Gateway units:** `gateway/lib` and `gateway/tools`.
- **Gateway application:** `gateway/app`, derived from the OpenBSW reference application.

## Software units

The report generator parses this table: ID | Unit | Source / functions | Element | Implements.

| ID | Unit | Source / functions | Element | Implements |
| --- | --- | --- | --- | --- |
| DD-01 | Router: classification and forwarding | `TransportRouter.cpp`: `getTransportMessage`, `messageReceived`, `routeRequest`, `routeFunctional`, `routeNodeResponse`, `forward` | ARC-03 | SWR-003, SWR-011, SWR-012, SWR-013, SWR-014, SWR-015, SWR-017, SWR-060 |
| DD-02 | Router: supervision and release | `TransportRouter.cpp`: `cyclic`, `routeProcessed`, `RouteContext::transportMessageProcessed`, `releaseTester`, `isResponsePending`, `notify` | ARC-03 | SWR-016, SWR-018, SWR-041, SWR-042 |
| DD-03 | Router: configuration and resources | `TransportRouter.cpp`: constructor, `validate`, `toString`, `allocate`, `releaseTransportMessage`, `learnTester`, `testerBus`, `addTransportLayer`, `removeTransportLayer`; `DiagnosticRoute.h` | ARC-03 | SWR-010, SWR-015, SWR-017, SWR-032, SWR-043 |
| DD-04 | Router statistics | `TransportRouterStatistics.cpp`: `count`, `get`, `reset` | ARC-07 | SWR-023 |
| DD-05 | Gateway routing table | `gateway/lib/src/gateway/RoutingTable.cpp`: `validate`, `indexOf`, `find`, `errorText` | ARC-04 | SWR-010 |
| DD-06 | Routing generator | `gateway/tools/gen_routing.py`: `validate`, `render_header`, `address_table`, `check_profile`, `main` | ARC-04 | SWR-010, SWR-052 |
| DD-07 | Node monitor | `gateway/lib/src/gateway/NodeMonitor.cpp`: `init`, `routeResponded`, `routeTimedOut`, `isNotResponding` | ARC-06 | SWR-024 |
| DD-08 | Fault memory | `DemoDtcManager.cpp` (extended): `registerDtc`, `reportFault`, `reportPassed`, `clearAll`, `clearByGroup`, `getDtcsByStatusMask`, `getSupportedDtcs`; `DemoReadDtcInfo.cpp`, `DemoClearDtc.cpp`; `GatewayDiagJobs.cpp`: `DtcSink` | ARC-06 | SWR-025 |
| DD-09 | Gateway identity | `gateway/lib/src/gateway/GatewayIdentity.cpp`: `vin`, `ecuSerial`, `softwareVersion` | ARC-05 | SWR-021 |
| DD-10 | Gateway UDS server | `UdsSystem.cpp`: `addDiagJobs`, `addJob`; `GatewayDiagJobs.cpp`: `ReadRoutingTable::process`, `ReadRoutingStatistics::process` | ARC-05 | SWR-020, SWR-021, SWR-022, SWR-023, SWR-027 |
| DD-11 | Transport system | `TransportSystem.cpp`: `diagnosticRoutes`, `init` (both validations), `run`, `execute` (10 ms supervision), `logStatistics` | ARC-03, ARC-07, ARC-08 | SWR-010, SWR-016, SWR-054 |
| DD-12 | Gateway DoCAN | `DoCanSystem.cpp`: `buildAddressEntries`, `init`, `run`, `shutdown`; ISO-TP parameters | ARC-02 | SWR-018, SWR-030, SWR-032 |
| DD-13 | DoIP server adaptation | `DoIpServerSystem.cpp`: `checkRoutingActivation`, `getEntityStatus`; `app.cpp`: `provideVin`, `TesterConnectionMonitor` | ARC-01 | SWR-001, SWR-002, SWR-004, SWR-005, SWR-040, SWR-041 |
| DD-14 | Platform and lifecycle | `app.cpp`: `startApp` (run levels); POSIX `CanSystem.cpp` `canInterfaceName`, `TapEthernetSystem.cpp` `run`; `main.cpp` signal handling | ARC-08 | SWR-044, SWR-050, SWR-051 |
| DD-15 | Build and dependencies | `gateway/CMakeLists.txt`, `app/application/CMakeLists.txt` (no SOME/IP, middleware or PDU routing), `dependencies.lock.json`, `scripts/bootstrap.sh` | ARC-09 | SWR-031, SWR-053 |
| DD-16 | Deployment assets | `scripts/net-up.sh`, `scripts/run.sh`, `scripts/storage.sh`; new Serial2CAN profile (planned) | ARC-10 | SWR-033, SWR-050 |

SWR-026 (reachability routine `31 01 F000`) is not implemented. The report
shows it as an open requirement.

## Unit design notes

**DD-01 Classification.** Every message is classified by address, not by bus:

| Situation | Rule |
| --- | --- |
| Request from the local bus | Allocated from the pool unconditionally (UDS responses and copies of functional requests) |
| Source in the tester range | A request; it goes to the local, functional or a route address |
| Source is a route address on that route's bus | A node response |
| Anything else | Rejected with `TPMSG_NOT_RESPONSIBLE` |

Requests to the local and functional addresses get a full-size buffer,
because the OpenBSW UDS server builds its response in the request buffer.
Before forwarding a request to a route, the router replaces its source with
the gateway tester address (`0x0E10`). The DoCAN entry of the route is
defined for that address. The original tester is restored before the tester
side is notified (`RouteContext::transportMessageProcessed`).

**DD-02 Supervision.** `cyclic()` runs every 10 ms (DD-11). It checks each
route's deadline, using wrap-safe signed differences of the 32-bit
millisecond clock:

| State or event | Deadline |
| --- | --- |
| SENDING | `TRANSFER_TIMEOUT_MS` (2 s) |
| WAIT_RESPONSE | P2 |
| After NRC `0x78` | P2\* |
| After the first frame of a segmented response | max(P2\*, 2 s) |

`releaseTester` frees the routes and the functional window of a
disconnected tester. A response that arrives later is then discarded by the
`TPMSG_NOT_RESPONSIBLE` path and counted.

**DD-03 Resources.** The router owns these buffers:

- 4 buffers of 4095 bytes and 8 of 8 bytes
- 16 route contexts
- an 8-entry table that maps testers to buses

`allocate` picks the smallest free buffer that fits. All state is in the
object, and there is no dynamic memory (SWR-043). Every access to shared
state is guarded by `::async::LockType`. Transport-layer calls are made
outside the lock, so a re-entrant release cannot deadlock.

**DD-07 Node monitor.** It counts consecutive timeouts per route. The third
timeout sets the route's DTC once; further timeouts are ignored until the
next response. A response resets the count and reports the test as passed.
It never sends traffic of its own (AD-05).

**DD-08 Fault memory.** The gateway extends the reference application's demo
DTC store:

- **Registered DTCs:** all routes' lost-communication DTCs are supported for `19 0A` from start-up, with status `testNotCompletedSinceLastClear`.
- **ISO 14229-1 status bits:** a failed test sets `testFailed`, `testFailedThisOperationCycle`, `pendingDTC` and `confirmedDTC`.
- **Passed tests:** `reportPassed` clears `testFailed` and keeps the history bits.
- **ClearDTC:** keeps registered DTCs and restarts their status.

**DD-12 DoCAN.** There is one normal-addressing layer. It has one entry per
route (`{response ID, request ID, route address, gateway tester address}`),
sorted by reception ID as the OpenBSW filter requires. The last entry is the
functional entry, which only transmits (invalid reception ID, transmission
`0x7DF`). Frames on any other identifier are not accepted by the filter
(SWR-030).

**DD-13 DoIP adaptation.**

- Only activation type `0x00` is accepted.
- The tester range comes from `routing.yaml`.
- The entity status reports node type gateway.
- The VIN comes from the routing configuration through the DoIP VIN callback.

## Diagrams

| Diagram | Content |
| --- | --- |
| [classify.puml](diagrams/classify.puml) | Activity of `getTransportMessage` and `messageReceived` (DD-01) |
| [buffer-ownership.puml](diagrams/buffer-ownership.puml) | Who allocates and releases each buffer on a routed request (DD-01, DD-03) |
