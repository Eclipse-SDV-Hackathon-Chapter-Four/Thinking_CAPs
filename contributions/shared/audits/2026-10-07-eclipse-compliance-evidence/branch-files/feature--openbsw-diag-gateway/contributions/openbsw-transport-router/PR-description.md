# Pull request draft — eclipse-openbsw/openbsw

**Title:** Add transportRouter module for diagnostic gateways

**Base:** `main` at `432b9be6098d99570ab8ebc32a7cbb895ca7bb63` · **Patch:**
[0001-transport-router.patch](0001-transport-router.patch) (one commit, signed off)

Closes: #<issue number, once the [issue](ISSUE-draft.md) is accepted>

---

## Summary

This PR adds `libs/bsw/transportRouter`, a diagnostic gateway router. It routes UDS
messages by logical address between external testers (e.g. DoIP), the local
diagnostic server and diagnostic nodes reached through other transport layers
(e.g. DoCAN).

`TransportRouterSimple` stays unchanged. It sends every request to the local server
and every reply to the bus of the last request. That is right for a single ECU but
not for a gateway.

## What it does

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
  - a transfer budget for delivery and for segmented responses

  Late and unsolicited responses are discarded. `releaseTester()` frees a
  disconnected tester's routes.
- **Errors for DoIP NACKs:** unknown target `TPMSG_INVALID_TGT_ADDRESS` (0x03), too
  large `TPMSG_SIZE_TOO_LARGE` (0x04), busy or out of buffers
  `TPMSG_NO_MSG_AVAILABLE` (0x05).
- **Configuration:** `TransportRouterConfiguration` with a span of `DiagnosticRoute`;
  `validate()` reports the first error and the offending route.
- **Observability:** `TransportRouterStatistics` (saturating counters) and
  `IRouteObserver` (`routeResponded`, `routeTimedOut`).
- **Static memory:** 4 × 4095 and 8 × 8 message buffers, 16 routes, 8 testers.
  Requests for the local server always get a full-size buffer, because the UDS
  server builds its response in the request buffer.

## Files

| Path | Change |
| --- | --- |
| `libs/bsw/transportRouter/` | New module: headers, sources, `doc/index.rst`, `BUILD.bazel`, `module.spec`, unit tests |
| `libs/bsw/CMakeLists.txt` | `add_subdirectory(transportRouter)` |
| `CMakeLists.txt` | Unit-test build: `add_subdirectory(libs/bsw/transportRouter/test)` |

## Testing

All of these were run on the PR branch; the logs are in [evidence/](evidence/):

| Check | Result |
| --- | --- |
| `tests-posix-debug`: `transportRouterTest` (42 tests) and `transportRouterSimpleTest` (4) | 46/46 passed, 0 build warnings |
| Coverage of `libs/bsw/transportRouter/src` (gcovr, without throw/unreachable branches) | 100% lines, 99.1% branches, 100% functions |
| `treefmt --no-cache` + `git diff --exit-code` (clang-format 17, cmake-format 0.6.13, buildifier 8.5.1) | clean |
| `tools/cr_checker` on the changed files | ok |
| clang-tidy with the repository `.clang-tidy` (module sources) | 0 findings (clang-tidy 19 locally; CI uses 17) |
| `bazel test //libs/bsw/transportRouter/... //libs/bsw/transportRouterSimple/...` | 2/2 passed |
| gitlint with the repository `.gitlint` | ok |

The module also runs in a POSIX zonal gateway: DoIP over lwIP/TAP, DoCAN on
`vcan0` and the OpenBSW UDS server. There it passed 28 integration tests
against simulated CAN ECUs, covering:

- physical, segmented (1003 bytes) and 4095-byte transfers
- NRC 0x78
- busy, too-large and unknown targets
- functional requests with responses from three nodes
- tester disconnects
- vehicle announcement and identification

The p95 forwarding latency was 2.9 ms (DoIP→CAN) and 0.8 ms (CAN→DoIP).

## Notes for reviewers

- The DoIP server acknowledges a diagnostic message when the router accepts it
  (unchanged behaviour). A later delivery failure frees the route and is counted.
- DoCAN STmin and block size are per transport layer, not per route.
- The logger component is `TPGATEWAY`, so it does not clash with `TPROUTER` of
  `TransportRouterSimple` when both modules are linked.
- The DoCAN layer of an application must map each route with
  `transportSourceId` = route address and `transportTargetId` = gateway tester
  address; the module documentation shows an example.
