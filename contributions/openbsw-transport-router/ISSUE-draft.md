# Issue — eclipse-openbsw/openbsw (feature request)

**Filed:** 7 October 2026 as https://github.com/eclipse-openbsw/openbsw/issues/664, after the
author's review.

Open this issue first and agree on the approach before the pull request
(CONTRIBUTING.md: "talk with the team through an issue"; `pull_request.rst`: a
completely new feature must be discussed with the committers).

Target: <https://github.com/eclipse-openbsw/openbsw/issues/new?template=feature_request.md>

**Title:** Add a diagnostic gateway router that routes UDS by logical address (transportRouter)

**Labels:** enhancement

---

**Describe the feature**

OpenBSW has the building blocks of a diagnostic gateway: the DoIP server, DoCAN,
the UDS server and the transport layer. What is missing is a router that
connects them by logical address.

`TransportRouterSimple` is designed for a single ECU. Every request from `CAN_0` or
`ETH_0` goes to the local diagnostic server (`SELFDIAG`), and every reply goes to
the bus that sent the last request (`_busIdToReply`). The target address is never
used to choose a destination. As a result, an OpenBSW node cannot forward a tester's
request to another ECU behind it. That is the job of a central or zonal diagnostic
gateway: DoIP on the vehicle side, CAN (and Ethernet) ECUs behind it.

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

A new module `libs/bsw/transportRouter`, next to `transportRouterSimple`.
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
  - transfer budget (`transferTimeoutMs`) for the transport layer to deliver a
    request or receive a long response
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
  reports responded and timed-out routes; the module provides `RouteObserverMock`
  for unit tests.
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
- Ethernet ECUs behind the gateway, together with the DoIP client proposed in #663.

The module is not specific to an operating system, compiler or build system. It uses
only `transport`, `async` (`LockType`), `util` (logger) and ETL, and builds with CMake
and Bazel. Tested with GCC 11.4 (POSIX unit tests, CMake and Bazel) and on the
S32K148EVB (Arm GNU Toolchain 14.3, ThreadX).

Limitations and possible follow-ups:

- DoCAN STmin and block size are one setting per transport layer. Per-route values
  would need a small DoCAN extension.
- The DoIP server acknowledges a diagnostic message when the router accepts it, as
  it does today. Delivery failures afterwards are counted, not NACKed.
- Routing between two node buses (CAN-to-CAN tester traffic) is not in scope.

**Additional context**

- A working implementation is ready as one commit on current `main`. It has 42 unit
  tests with 100 % line and 99 % branch coverage, and passes the OpenBSW format,
  copyright, clang-tidy, Bazel and documentation gates.
- It is used in a zonal diagnostic gateway built for the Eclipse SDV Hackathon 2026
  "Thinking CAPs" blueprint (OpenSOVD CDA over DoIP to zonal ECUs). There it passed
  44 integration tests on POSIX, routing to simulated CAN ECUs over DoCAN and to a
  simulated Ethernet ECU over DoIP. They cover segmented responses, NRC 0x78, busy
  and unknown targets, functional requests and tester disconnects. On the S32K148EVB
  (no CAN adapter connected yet) it passed 16 tests: local UDS, rejections, routing
  over DoIP, and the timeout of a CAN route without a peer.
- The implementation was largely written with an AI assistant (Anthropic Claude Opus
  5.5) and reviewed and tested by me. Following the Eclipse Foundation guidelines on
  generative AI, each file states this below its copyright header, and the commit
  carries an `Assisted-by:` trailer. As asked in #663: do you want the file headers
  in another form, for example the dual `Apache-2.0 AND CC0-1.0` SPDX expression from
  the Eclipse handbook template?

Before I open the PR, I would like to know whether you agree with:

- a separate module rather than extending `TransportRouterSimple`
- the module and class names
- the configuration API
