# Upstream issue draft — eclipse-openbsw/openbsw

Target: <https://github.com/eclipse-openbsw/openbsw/issues/new?template=feature_request.md>
Labels: `enhancement`

---

**Title:** Diagnostic gateway router: route UDS by logical address between DoIP, DoCAN and the local server

**Describe the feature**

OpenBSW has the building blocks of a diagnostic gateway: the DoIP server, DoCAN,
the UDS server and the transport layer. What is missing is a router that
connects them by logical address.

`TransportRouterSimple` is designed for a single ECU. Every request from `CAN_0` or
`ETH_0` goes to the local diagnostic server (`SELFDIAG`), and every reply goes to
the bus that sent the last request (`_busIdToReply`). The target address is never
used to choose a destination. As a result, an OpenBSW node cannot forward a tester's
request to another ECU behind it. That is the job of a central or zonal diagnostic
gateway: DoIP on the vehicle side, CAN ECUs behind it.

A gateway router needs:

- **Routing by target logical address:** to the local server, to a node reached
  through another transport layer, or to a functional group.
- **Per-target supervision:** at most one outstanding request per node; P2 and P2*
  timeouts; response pending (NRC 0x78) passed through unchanged.
- **Tester bookkeeping:** the original tester address is restored on responses, so
  several testers on several buses can share the gateway; a disconnected tester's
  pending requests are released at once.
- **Functional fan-out:** a functional request goes to the local server and once to
  every node bus, and the nodes' responses are collected within a window.
- **Error mapping:** routing errors are reported through `ITransportMessageProvider::ErrorCode`,
  so the existing DoIP server answers with the right diagnostic message NACK:
  unknown target `0x03`, too large `0x04`, busy or out of buffers `0x05`.
- **Observability:** statistics, and a hook for route outcomes (for example to set a
  lost-communication DTC).

**Proposed Solution**

Add a new module `libs/bsw/transportRouter`, next to `transportRouterSimple`.
`TransportRouterSimple` is not changed, and existing applications are unaffected.

- `transport::TransportRouter` implements `ITransportMessageProvidingListener` and
  plugs into the existing, unmodified transport layers in the same way as
  `TransportRouterSimple`, through `addTransportLayer()`.
- It is configured with `TransportRouterConfiguration`:
  - local address and bus
  - functional address
  - the gateway's own tester address towards the nodes
  - external tester address range
  - functional window and maximum functional length
  - a span of `DiagnosticRoute{logicalAddress, busId, p2Ms, p2StarMs, maxLength, name}`
- `validate()` checks the configuration: duplicates, overlaps with the local,
  functional or tester addresses, timing, lengths.
- Messages are classified by address, not by bus:
  - a source in the tester range is a request
  - a route's address on the route's bus is a node response
  - everything from the local bus is the local server
- `cyclic()` (e.g. every 10 ms) supervises the deadlines with a wrap-safe
  millisecond clock, which is injected (`NowMsType`).
- `TransportRouterStatistics` provides saturating counters. `IRouteObserver`
  reports responded and timed-out routes.
- All memory is static:
  - 4 × 4095-byte and 8 × 8-byte message buffers
  - 16 routes
  - 8 tester entries

  Requests for the local server always get a full-size buffer, because the UDS
  server builds its response in the request buffer.

Use cases:

- A zonal or central gateway with DoIP towards an OpenSOVD Classic Diagnostic
  Adapter or an external tester, and DoCAN towards CAN ECUs.
- Several CAN buses behind one DoIP entity.

The module is platform-, OS- and compiler-independent. It uses only `transport`,
`async` (`LockType`), `util` (logger) and ETL, and builds with CMake and Bazel.

We have an implementation ready to propose as a PR:

- 42 GoogleTest/gMock unit tests with 100% line and 99% branch coverage
- passes the treefmt, copyright and clang-tidy gates and `bazel test`
- integrated in a POSIX gateway (DoIP over TAP, DoCAN on `vcan0`) and tested end to
  end against simulated CAN ECUs, including segmented responses, NRC 0x78, busy
  and unknown targets, functional requests and tester disconnects

Limitations and possible follow-ups:

- DoCAN STmin and block size are one setting per transport layer. Per-route values
  would need a small DoCAN extension.
- The DoIP server acknowledges a diagnostic message when the router accepts it, as
  it does today. Delivery failures afterwards are counted, not NACKed.
- Routing between two node buses (CAN-to-CAN tester traffic) is not in scope.

**Additional context**

The work comes from the Eclipse SDV Hackathon 2026 "Thinking CAPs" blueprint. There,
an OpenBSW zonal gateway sits between OpenSOVD (CDA over DoIP) and zonal CAN ECUs in
a CARLA-based virtual vehicle. We would like to know if the maintainers agree with:

- adding a separate module rather than extending `TransportRouterSimple`
- the module and class names
- the configuration API

before we open the PR.
