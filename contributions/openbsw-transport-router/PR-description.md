# Pull request draft — eclipse-openbsw/openbsw

**Title:** Add transportRouter module for diagnostic gateways

**Base:** `main` at `b0550871b7a44ae47bb9b7c68af84fb9115bfa77` · **Patch:**
[0001-transport-router.patch](0001-transport-router.patch) (one commit, signed off, `Assisted-by` trailer)

**Tag:** `tested_on_hw` (S32K148EVB, see Test Plan)

**Opened:** 7 October 2026 as https://github.com/eclipse-openbsw/openbsw/pull/665. The posted body is the text below the line, with a
request to a committer to set `tested_on_hw` and the Claude Code attribution line.

---

## Purpose of this PR
- [ ] Bugfix
- [x] New Feature
- [ ] Documentation Update
- [ ] Other (Please specify)

**Description**

This PR adds `libs/bsw/transportRouter`, a diagnostic gateway router. It routes UDS
messages by logical address between external testers (e.g. DoIP), the local
diagnostic server and diagnostic nodes reached through other transport layers
(e.g. DoCAN).

`TransportRouterSimple` stays unchanged. It sends every request to the local server
and every reply to the bus of the last request. That is right for a single ECU but
not for a gateway.

- `transport::TransportRouter` implements `ITransportMessageProvidingListener` and
  registers the existing transport layers with `addTransportLayer()`, like
  `TransportRouterSimple`. No other module changes.
- **Routing by address.** Requests go:
  - to the local address on the local bus
  - to a route address on the route's bus, with the source replaced by the
    gateway's tester address
  - to the functional address on the local bus, plus one copy per route bus

  Node responses return to the requesting tester on that tester's bus, with the
  original tester address.
- **Supervision:**
  - one outstanding request per route
  - P2 after delivery, P2* after each NRC 0x78
  - a configurable transfer budget (`transferTimeoutMs`) for delivery and for
    segmented responses

  Late and unsolicited responses are discarded. `releaseTester()` frees a
  disconnected tester's routes.
- **Errors for DoIP NACKs:** unknown target `TPMSG_INVALID_TGT_ADDRESS` (0x03), too
  large `TPMSG_SIZE_TOO_LARGE` (0x04), busy or out of buffers
  `TPMSG_NO_MSG_AVAILABLE` (0x05).
- **Configuration:** `TransportRouterConfiguration` with a span of `DiagnosticRoute`;
  `validate()` reports the first error and the offending route.
- **Observability:** `TransportRouterStatistics` (saturating counters) and
  `IRouteObserver` (`routeResponded`, `routeTimedOut`), with `RouteObserverMock` in
  `mock/gmock/include` (CMake `transportRouterMock`, Bazel `transport_router_mock`).
- **Static memory:** 4 × 4095 and 8 × 8 message buffers, 16 routes, 8 testers.
  Requests for the local server always get a full-size buffer, because the UDS
  server builds its response in the request buffer.

The module documentation is in `libs/bsw/transportRouter/doc/index.rst` (Sphinx build
without warnings).

Changed outside the module: one `add_subdirectory` line each in `libs/bsw/CMakeLists.txt`
and in the unit-test list of the top-level `CMakeLists.txt`.

**AI disclosure:** the module was largely written with an AI assistant (Anthropic Claude
Opus 5.5) and reviewed and tested by the author. Each file says so below its copyright
header, and the commit carries `Assisted-by: Anthropic Claude Opus 5.5` (Eclipse
Foundation generative AI guidelines).

**Related Issues**

Resolves #664 (feature request: Add a diagnostic gateway router that routes UDS by
logical address)

Related: #663 (DoIP client transport layer, which this router uses to reach Ethernet ECUs
in the gateway described below).

**Breaking Changes**
- [ ] Yes
- [x] No

**Test Plan**

- Unit tests: `cmake --preset tests-posix-debug`, build `transportRouterTest`, run
  `ctest -L transportRouter` (42 new tests with `StrictMock`s and a fake millisecond
  clock, plus the 4 existing `transportRouterSimpleTest` tests). Coverage of `src/`
  (gcovr): 100 % lines, 99.1 % branches, 100 % functions. Bazel:
  `bazel test //libs/bsw/transportRouter/... //libs/bsw/transportRouterSimple/...`.
- Gates on `main` `b0550871`: treefmt (clang-format 17, cmake-format, buildifier) clean,
  `tools/cr_checker` ok, clang-tidy with the repository `.clang-tidy` 0 findings, unit-test
  build with 0 warnings, gitlint ok, Sphinx documentation build without warnings.
- Integration, outside this repository: a zonal diagnostic gateway built on OpenBSW
  (DoIP server, DoCAN, the UDS server and this router).
  - On POSIX (FreeRTOS, lwIP on TAP, `vcan0`), 44 tests passed. They cover physical,
    segmented and 4095-byte transfers, NRC 0x78, busy, too-large and unknown targets,
    functional requests with responses from several nodes, tester disconnects, and
    routing to an Ethernet ECU over DoIP. Forwarding latency p95 was 1.9 ms
    (DoIP→CAN) and 0.9 ms (CAN→DoIP).
  - On the **S32K148EVB** (ThreadX 6.4.3, 100BASE-T1, no CAN adapter connected), 16
    tests passed: local UDS, rejections, routing over DoIP, and the timeout of a CAN
    route without a peer.

**Regression Tests**

Have tests been added/updated? [x] Yes [ ] No

## Notes for reviewers

- The DoIP server acknowledges a diagnostic message when the router accepts it
  (unchanged behaviour). A later delivery failure frees the route and is counted.
- DoCAN STmin and block size are per transport layer, not per route.
- The logger component is `TPGATEWAY`, so it does not clash with `TPROUTER` of
  `TransportRouterSimple` when both modules are linked.
- The DoCAN layer of an application must map each route with
  `transportSourceId` = route address and `transportTargetId` = gateway tester
  address; the module documentation shows an example.
