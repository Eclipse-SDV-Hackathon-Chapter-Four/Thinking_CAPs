# Software architectural design (SWE.2)

| Item | Value |
| --- | --- |
| Software | OpenBSW zonal diagnostic gateway |
| Inputs | [Software requirements](../swe1-requirements/software-requirements.md), OpenBSW reference application (`executables/referenceApp`: `DoIpServerSystem`, `DoCanSystem`, `TransportSystem`, `UdsSystem`, POSIX `TapEthernetSystem`) |
| Status | Baselined, 6 October 2026 (revised after implementation) |

| View | File | Purpose |
| --- | --- | --- |
| Context | [context.puml](diagrams/context.puml) | Gateway between OpenSOVD/CDA and the X-Verse CAN bus; the cruise-control path it stays out of |
| Static | [components.puml](diagrams/components.puml) | OpenBSW modules reused, gateway elements added, interfaces |
| Dynamic | [physical-routing.puml](diagrams/physical-routing.puml) | SOVD request → DoIP → ISO-TP → ThreadX ECU and back, with response pending and timeout |
| Dynamic | [functional-routing.puml](diagrams/functional-routing.puml) | Functional request fan-out and collection of responses |
| Behaviour | [route-state.puml](diagrams/route-state.puml) | State machine for each route's pending request |
| Deployment | [deployment.puml](diagrams/deployment.puml) | Linux host in X-Verse, and the S32K148 target |

## Design decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| AD-01 | Build the gateway as an application on the OpenBSW reference-app structure: lifecycle systems for Ethernet, DoIP, DoCAN, transport and UDS | The reference app already wires `DoIpServerSystem`, `DoCanSystem` and `UdsSystem` together; reusing them keeps OpenBSW unmodified (SWR-053) and the code portable (SWR-051). |
| AD-02 | A new, generic OpenBSW module `transportRouter` (`transport::TransportRouter`) implements `ITransportMessageProvidingListener` like `TransportRouterSimple`, but routes by target logical address. It is kept free of gateway specifics and prepared as an upstream contribution; the gateway builds it from `OpenBSW/contrib/` | `TransportRouterSimple` sends every request to the local server and every reply to the last requesting bus. A gateway needs per-address routes, one pending request per target, P2/P2* supervision, tester-address restoration and statistics (SWR-010, SWR-012, SWR-015, SWR-016). Upstreaming avoids a fork (SYS-10). |
| AD-03 | Transparent forwarding: the router never interprets or generates UDS for remote ECUs | Keeps the gateway independent of each ECU's diagnostic content; the CDA and the ECU own the semantics (SWR-014). |
| AD-04 | Track the pending tester and its bus per route; learn each tester's bus from its requests; classify messages by address, not by bus | Responses reach the right tester on the right bus, and several testers on several buses can share the gateway (SWR-012, SWR-013, SWR-041). The DoIP ACK follows OpenBSW's synchronous hand-over (SWR-003). |
| AD-05 | Monitor ECUs passively, from the outcome of routed requests | No extra CAN traffic, so no effect on the X-Verse bus (SWR-024, SWR-030). |
| AD-06 | One YAML routing source, which generates the C++ configuration and the CDA/ECU consistency check | Addresses defined once (SWR-052, SYS-09). |
| AD-07 | Linux host first, with SocketCAN `vcan0` and lwIP on TAP; S32K148 is a build-only target at first | Runs in X-Verse without hardware (SYS-06); same application code on both targets (SWR-051). |
| AD-08 | FreeRTOS POSIX core configuration by default; the ThreadX core configuration (`asyncThreadX`) is an option | FreeRTOS is the reference-app default and the best tested. ThreadX is offered so the team's RTOS choice can be aligned later without changing the application. |
| AD-09 | SOME/IP and every vehicle-signal middleware excluded from the build | No path into the cruise-control signal flow (SWR-031). |

## Software elements

The table follows the Serial2CAN report format: ID | Element | Responsibility | Satisfies.

| ID | Element | Responsibility | Satisfies |
| --- | --- | --- | --- |
| ARC-01 | DoIP server (`DoIpServerSystem`, OpenBSW `doip`) | Vehicle identification and announcement, routing activation, connection lifecycle, entity status, header validation, diagnostic message (N)ACK | SWR-001, SWR-002, SWR-003, SWR-004, SWR-005, SWR-040 |
| ARC-02 | DoCAN transport (`DoCanSystem`, OpenBSW `docan` + `cpp2can`) | ISO-TP on the configured identifiers: padding, flow control, STmin, N_x timeouts; drops every other identifier | SWR-018, SWR-030, SWR-032, SWR-060 |
| ARC-03 | `transport::TransportRouter` (new OpenBSW module `contrib/libs/bsw/transportRouter`) | Route by logical address to local UDS, a route's transport layer or the functional group; per-route pending state; P2/P2\* supervision; late and unsolicited response handling; NACK mapping; statistics | SWR-003, SWR-011, SWR-012, SWR-013, SWR-014, SWR-015, SWR-016, SWR-017, SWR-032, SWR-041, SWR-042, SWR-060 |
| ARC-04 | Gateway `RoutingTable` + generator (`gateway/config/routing.yaml`, `gateway/tools/gen_routing.py`) | Static routes with CAN identifiers, validated by the generator and at init; generated C++ configuration and router routes; consistency check against ECU CAN profiles | SWR-010, SWR-052 |
| ARC-05 | Gateway UDS server (`UdsSystem`, OpenBSW `uds` dispatcher + new jobs) | Sessions and S3, TesterPresent, identification DIDs, `FD00`/`FD01`, reachability routine | SWR-011, SWR-020, SWR-021, SWR-022, SWR-023, SWR-026, SWR-027 |
| ARC-06 | `NodeMonitor` + `DtcStore` (new) | Count consecutive timeouts per route, set/pass the lost-communication fault, status bits, `0x19`/`0x14` | SWR-024, SWR-025 |
| ARC-07 | `transport::TransportRouterStatistics` (module) + `TransportSystem` log | Saturating counters per route and for the router; periodic log line | SWR-023, SWR-054 |
| ARC-08 | Platform and lifecycle (OpenBSW `lifecycle`, `async`, POSIX `main`, `TapEthernetSystem`, `lwipSocket`) | Start-up order, shutdown on signals, static allocation, CAN/TAP interface selection | SWR-043, SWR-044, SWR-050, SWR-051 |
| ARC-09 | Build and dependency lock (`CMakeLists.txt`, `dependencies.lock.json`) | Pinned OpenBSW revision, unmodified-checkout check, SOME/IP excluded | SWR-031, SWR-053 |
| ARC-10 | Deployment assets (container, TAP set-up, new Serial2CAN profile) | Run alongside X-Verse and the CDA using only new files | SWR-033, SWR-050 |

The forwarding-latency budget (SWR-060) and the bus-load limit (SWR-032) are
properties of ARC-02 and ARC-03 together (one outstanding request per route,
ISO-TP flow control). Integration tests, analysis and qualification verify them.

## Interfaces

| ID | Interface | Provider → consumer | Type and contract |
| --- | --- | --- | --- |
| IF-01 | DoIP UDP/TCP 13400 | CDA ↔ ARC-01 | External. ISO 13400-2; tester range `0x0E00`–`0x0EFF`; gateway `0x1010`; functional `0xE400` |
| IF-02 | ISO-TP on CAN | ARC-02 ↔ zonal ECUs | External. ISO 15765-2 normal 11-bit, classic CAN DLC 8 padded `0xCC`; `0x7DF` functional, `0x7E1`/`0x7E9`, `0x7E2`/`0x7EA` |
| IF-03 | `ITransportMessageProvidingListener` (`getTransportMessage`, `messageReceived`, `releaseTransportMessage`) | ARC-01/02/05 → ARC-03 | Internal (OpenBSW). Buffer hand-over and routing entry point; routing errors map to DoIP NACK codes |
| IF-04 | `AbstractTransportLayer::send` + `ITransportMessageProcessedListener` | ARC-03 → ARC-01/02/05 | Internal (OpenBSW). Forwarding, and the completion that triggers the DoIP ACK/NACK |
| IF-05 | `TransportRouterConfiguration` + gateway `RoutingTable` | ARC-04 → ARC-02, ARC-03, ARC-05, ARC-06 | Internal. Router routes (`DiagnosticRoute`: address, bus, P2, P2\*, max length) and the CAN identifiers for DoCAN |
| IF-06 | `transport::IRouteObserver` (`routeResponded`, `routeTimedOut`) | ARC-03 → ARC-06 | Internal (module API). Called in the context that observed the outcome; never blocks |
| IF-07 | `routing.yaml` | Integrator → ARC-04 | External. Single source of addresses (SWR-052) |
| IF-08 | Logger output | ARC-07, ARC-08 → operator | External. Start-up identity, 30 s statistics, debug routing events |

## Resources

| Resource | Allocation |
| --- | --- |
| Tasks | OpenBSW async contexts: Ethernet/DoIP, CAN/DoCAN, diagnosis (router, UDS, monitor) |
| Memory | Static only: 4 routing buffers of 4095 bytes, 8 small buffers of 8 bytes, 1 pending context per route (16 max), 8 tester entries |
| CAN | Transmits only on `0x7DF` and the route request IDs; worst case < 10 % of 500 kbit/s (SWR-032) |
| Network | TAP interface on the host; UDP and TCP port 13400 |
