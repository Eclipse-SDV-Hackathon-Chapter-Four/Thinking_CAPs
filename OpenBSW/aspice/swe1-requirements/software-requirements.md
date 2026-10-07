# Software requirements specification (SWE.1)

| Item | Value |
| --- | --- |
| Software | OpenBSW zonal diagnostic gateway: `OpenBSW/gateway` (application, gateway units) and the contributed module `OpenBSW/contrib/libs/bsw/transportRouter` |
| Inputs | [System requirements](system-requirements.md), [README](../../README.md), ISO 13400-2 (DoIP), ISO 14229-1 (UDS), ISO 15765-2 (ISO-TP), [ThreadX CAN contract](../../../ThreadX/docs/can-lighting-contract.md), Eclipse OpenBSW `libs/bsw/{doip,docan,uds,transport,transportRouterSimple}` |
| Status | Baselined for the hackathon demonstration, 6 October 2026 (revised after implementation) |

Each requirement has:

- a unique ID
- a *Derived from* link to system requirements
- a type
- the planned verification levels:
  - **UT** unit test
  - **IT** integration test (host, with a simulated tester and simulated CAN ECUs)
  - **QT** qualification test in X-Verse with the CDA and OpenSOVD
  - **AN** analysis
  - **RV** review
- a criterion

## Terms and default values

| Term | Meaning | Default |
| --- | --- | --- |
| Gateway address | DoIP logical address of the gateway's own UDS server | `0x1010` |
| Tester addresses | Source addresses allowed to activate routing | `0x0E00`–`0x0EFF` |
| Functional address | DoIP target address for the "all zonal ECUs" group | `0xE400` |
| Route | A routing-table entry: logical address, name, transport (`docan`), CAN request/response IDs, P2/P2\* timeouts, maximum length, lost-communication DTC | see below |
| Rear lighting route | ThreadX rear lighting ECU | `0x1020`, request `0x7E1`, response `0x7E9` |
| Front zone route | Reserved for a future front-zone ECU | `0x1030`, request `0x7E2`, response `0x7EA` |
| Functional CAN ID | ISO-TP functional request identifier | `0x7DF` |
| P2 / P2\* gateway timeout | Time the gateway waits for a remote response / after NRC `0x78` | 150 ms / 5100 ms |

## DoIP interface

### SWR-001 Vehicle identification and announcement
The software shall answer DoIP vehicle identification requests on UDP port
13400: generic, by VIN and by EID. Each response shall carry the configured
VIN, the gateway address, EID and GID. After the Ethernet link is up, the
software shall send three vehicle announcements at 500 ms intervals.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-01, SYS-02 |
| Verification | IT, QT |
| Criterion | A UDP tester receives three announcements after start-up and a matching response to each identification request type; the CDA discovers the gateway. |

### SWR-002 Routing activation
The software shall accept routing activation (type `0x00`) on TCP port 13400
from source addresses in the tester range, and answer with code `0x10`. It
shall reject other source addresses with code `0x00`, and unsupported
activation types with code `0x06`. It shall support at least two simultaneous
tester connections.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02 |
| Verification | UT, IT |
| Criterion | Tester `0x0E80` is activated; `0x0123` is rejected with `0x00`; type `0x01` is rejected with `0x06`; two testers are active at the same time. |

### SWR-003 Diagnostic message acknowledgement
For each DoIP diagnostic message from an activated tester, the software shall
send a positive acknowledgement (`0x8002`) once the router has accepted the
request and handed it to the target's transport layer: the local UDS server
or the route's ISO-TP layer. The OpenBSW DoIP server sends the acknowledgement
synchronously with this hand-over; a later ISO-TP failure is counted
(SWR-018), not acknowledged. Otherwise it shall send a negative
acknowledgement (`0x8003`) with:

- `0x02` source address not activated on this connection
- `0x03` unknown target address
- `0x04` message larger than the route's limit
- `0x05` route busy or no routing buffer free

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02, SYS-03, SYS-07 |
| Verification | UT, IT |
| Criterion | Unknown target gives `0x03`, too large `0x04`, busy route `0x05`; a single-frame request is acknowledged within 50 ms. |

### SWR-004 Connection lifecycle
The software shall close a TCP connection without routing activation after
2 s, and an idle activated connection after 5 min (configurable). Closing a
connection shall release every routing resource held for that tester.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-02, SYS-07 |
| Verification | UT, IT |
| Criterion | Inactive connections are closed at the configured times; after closing, the route's resources are free again (statistics show zero pending). |

### SWR-005 Entity status and power mode
The software shall answer DoIP entity status and diagnostic power mode
requests: node type gateway, maximum and current open sockets, and power mode
"ready".

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02 |
| Verification | IT |
| Criterion | Responses contain the configured socket limits and the current connection count. |

## Routing

### SWR-010 Routing table
The software shall route by a static routing table, with one entry per
logical address. Each entry holds:

- logical address and name
- transport (`local` or `docan`)
- CAN request and response identifiers
- P2 and P2\* timeouts
- ISO-TP STmin and maximum message length

At initialisation the software shall reject the table, and not start, if any
of these occur (checked both by the generator, SWR-052, and at start-up by the
gateway table and by the router configuration check):

- duplicate logical addresses or CAN identifiers
- an identifier outside `0x7DF`–`0x7EF`
- a route that overlaps the gateway or functional address

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-03, SYS-09 |
| Verification | UT |
| Criterion | Valid tables load; each listed invalid table is rejected with an error that names the conflicting entry. |

### SWR-011 Physical routing to the gateway
A diagnostic message with the gateway address as target shall go to the
gateway's own UDS server. The response shall return to the requesting tester,
with the gateway address as source.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-03, SYS-04 |
| Verification | UT, IT |
| Criterion | `22 F1 90` to `0x1010` returns `62 F1 90 <VIN>` from source `0x1010`. |

### SWR-012 Physical routing to a CAN ECU
A diagnostic message whose target is a `docan` route shall be sent over
ISO-TP on that route's request identifier. A response from the route's
response identifier shall be sent to the tester that issued the pending
request. The DoIP source address shall be the route's logical address.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01, SYS-03 |
| Verification | IT, QT |
| Criterion | `22 F1 95` to `0x1020` appears on `0x7E1`; the simulated ECU's reply on `0x7E9` reaches the tester from `0x1020`. In X-Verse, the SOVD client reads the ThreadX ECU's software version. |

### SWR-013 Functional routing
A diagnostic message to the functional address shall go to the gateway's own
UDS server. It shall also be sent once as a single-frame ISO-TP request on the
functional CAN identifier. Each response received within P2\* (from the local
server or any `docan` route) shall be sent to the tester as a separate DoIP
diagnostic message, with that node's logical address as source. Functional
requests longer than one CAN single frame (7 bytes) shall be rejected with
NACK `0x04`.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-03 |
| Verification | UT, IT |
| Criterion | `3E 00` to `0xE400` returns one response from each reachable node; with `3E 80` (suppress positive response) the tester receives only the DoIP ACK; an 8-byte functional request is rejected with `0x04`. |

### SWR-014 Payload transparency
The software shall forward UDS payloads unchanged in both directions,
including negative responses and NRC `0x78` (response pending). It shall
never generate a UDS response on behalf of a remote ECU.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-03 |
| Verification | UT, IT |
| Criterion | Byte-for-byte equality between tester and CAN payloads for 4095-byte, negative and `0x78` responses; no UDS response reaches the tester when the simulated ECU stays silent. |

### SWR-015 Request concurrency
The software shall handle at least three outstanding physical requests at the
same time, each to a different target. It shall allow at most one outstanding
request per target. A request to a target that already has one outstanding,
or when no routing resource is free, shall be rejected with NACK `0x05` and
counted.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-07 |
| Verification | UT, IT |
| Criterion | Three parallel requests to three targets all complete; a second request to a busy target is NACKed with `0x05`; the counter increments. |

### SWR-016 Response timeout
If a remote ECU does not respond within the route's P2, the software shall
release the pending request and count a timeout. The same applies within P2\*
after each NRC `0x78`. It shall send no UDS response to the tester; the
tester's own timing handles this case.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-07 |
| Verification | UT, IT |
| Criterion | A silent ECU frees its route after P2 (±10 ms); an ECU that sends `0x78` every 4 s stays pending; a late response is discarded and counted (SWR-042). |

### SWR-017 Message size limits
The software shall route UDS messages of up to 4095 bytes. Larger
messages shall be rejected with NACK `0x04`.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-02, SYS-07 |
| Verification | UT, IT |
| Criterion | 4095-byte request and response round-trip; a 4096-byte request is rejected with `0x04`. |

### SWR-018 ISO-TP parameters
On CAN the software shall use:

- ISO-TP normal 11-bit addressing
- classic CAN frames with DLC 8, padded with `0xCC`
- block size 0 and STmin 5 ms in its flow control when receiving (chosen for
  SLCAN ECUs at 115200 baud; one value for all routes)
- N_As, N_Bs and N_Cr timeouts of 1000 ms

A transmission that fails with N_As or N_Bs shall free the route, be counted
as a transmission failure and be reported to the node monitor. A reception
that fails with N_Cr shall be discarded.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02 |
| Verification | UT, IT |
| Criterion | candump of a single- and a multi-frame exchange shows padded 8-byte frames and the gateway's flow control (BS 0, STmin 5 ms); a failed delivery frees the route and is counted. |

## Gateway UDS server

### SWR-020 Supported services
The gateway's own UDS server shall support:

- `0x10` sessions `01` and `03`
- `0x3E` with sub-functions `00` and `80`
- `0x22`
- `0x19` sub-functions `01`, `02` and `0A`
- `0x14` for group `FFFFFF`
- `0x31` start routine

Other requests shall get these negative response codes:

- `0x11` unsupported service
- `0x12` unsupported sub-function
- `0x13` wrong message length
- `0x31` unsupported identifier

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04 |
| Verification | UT, IT |
| Criterion | Each supported service answers positively; each listed error returns the specified NRC. |

### SWR-021 Identification data
The gateway shall return these identifiers through `0x22`:

- `F190` VIN, 17 ASCII characters
- `F18C` ECU serial number
- `F195` software version, including the gateway version, the OpenBSW revision and the routing-table hash

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04, SYS-10 |
| Verification | UT, QT |
| Criterion | Values match the build and configuration; the SOVD client shows them for the gateway component. |

### SWR-022 Routing configuration data
The gateway shall return the active routing table through `0x22 FD00`: for
each route, its logical address, transport, CAN request and response
identifiers, and P2/P2\* timeouts.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04, SYS-09 |
| Verification | UT, IT |
| Criterion | The decoded DID equals the configuration source (SWR-052). |

### SWR-023 Routing statistics data
The gateway shall return routing statistics through `0x22 FD01`:

- for each route: forwarded requests, forwarded responses, NACKs by code, timeouts, discarded late or unsolicited responses
- the number of active DoIP connections

Counters shall saturate rather than wrap.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04, SYS-07 |
| Verification | UT, IT |
| Criterion | Counters change exactly as the IT scenarios predict. |

### SWR-024 Node communication monitoring
The software shall mark a `docan` route as **not responding** after three
consecutive physical requests to it time out (SWR-016). This sets a "lost
communication" fault for that route:

- `U0140` (`0xC14000`) for the rear lighting route
- `U0141` (`0xC14100`) for the front zone route

The next valid response from that route shall make the fault test pass
again. The software shall not send CAN traffic only to monitor ECUs.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04, SYS-05 |
| Verification | UT, IT, QT |
| Criterion | Three timeouts set `testFailed` and `confirmedDTC`; a response clears `testFailed`; with no tester traffic, candump shows no gateway frames. |

### SWR-025 Fault memory
The software shall keep fault status per ISO 14229-1, using these bits:

- `testFailed`
- `testFailedThisOperationCycle`
- `pendingDTC`
- `confirmedDTC`

`0x19 02` shall report the faults that match the status mask, and `0x14 FFFFFF`
shall clear them. Fault memory may be volatile (cleared on restart).

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04 |
| Verification | UT, QT |
| Criterion | The status byte follows the test sequence; clear empties the memory; the SOVD client lists and clears the fault through the CDA. |

### SWR-026 Node reachability routine
Routine `0x31 01 F000` shall send `3E 00` to every `docan` route. It shall
return one bit per route: 1 if the route answered within P2, 0 otherwise.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04 |
| Verification | UT, IT |
| Criterion | With one simulated ECU silent, the routine reports exactly that route as unreachable. |

### SWR-027 Session handling
The gateway's own session shall return to default after 5000 ms with no
request (S3). Its session state shall be independent of the sessions of
routed ECUs, and it shall not be propagated to them.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04 |
| Verification | UT |
| Criterion | Extended session falls back to default after S3; a `10 03` to `0x1010` produces no CAN frame. |

## Non-interference

### SWR-030 CAN identifier discipline
The software shall transmit only on the configured request identifiers and
the functional CAN identifier. It shall process only the configured response
identifiers. All other frames shall be ignored, including the lighting
frames `0x1F1`/`0x1F4` and any cruise-control signal.

| Attribute | Value |
| --- | --- |
| Type | Safety-related constraint (demonstration) |
| Derived from | SYS-05 |
| Verification | IT, QT, AN |
| Criterion | A 30-minute X-Verse run records only `0x7DF`/`0x7E1`–`0x7E2` transmissions from the gateway; replaying lighting traffic changes no gateway counter. |

### SWR-031 No vehicle-signal middleware
The software shall not open Zenoh sessions or SOME/IP services. OpenBSW's
`cpp2someip` and SOME/IP systems shall be excluded from the build.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-05 |
| Verification | AN, RV |
| Criterion | The link map contains no SOME/IP or Zenoh symbols; the configuration review confirms it. |

### SWR-032 Diagnostic bus load
Gateway-generated CAN traffic shall stay below 10 % of a 500 kbit/s bus,
averaged over any 1 s window.

| Attribute | Value |
| --- | --- |
| Type | Performance |
| Derived from | SYS-05 |
| Verification | AN, QT |
| Criterion | Worst case: 3 routes with 4095-byte transfers at the STmin floor, calculated and measured with candump during QT. |

### SWR-033 Baseline untouched
The deployment shall add only:

- new processes
- a new CAN bridge/serial profile
- a new CDA diagnostic description

It shall not change the X-Verse baseline, the existing Zenoh2CAN and
Serial2CAN profiles, the ThreadX lighting contract, S-CORE, OpenSOVD Path A,
or the CARLA scripts.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-05 |
| Verification | RV, QT |
| Criterion | The `git diff` of the integration touches only `OpenBSW/` and new configuration files; the cruise-control qualification (13 assertions, `DEMO=cruise`) passes with the gateway running and with it stopped. |

## Robustness

### SWR-040 Malformed DoIP messages
The software shall handle invalid generic headers as specified by ISO 13400-2:

| Problem | Header NACK | Then |
| --- | --- | --- |
| Incorrect pattern | `0x00` | Close the socket |
| Unknown payload type | `0x01` | Keep the connection |
| Message too large | `0x02` | Keep the connection |
| Out of memory | `0x03` | Keep the connection |
| Invalid payload length | `0x04` | Close the socket |

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-07 |
| Verification | UT, IT |
| Criterion | Each case produces the specified NACK and socket behaviour; other connections continue routing. |

### SWR-041 Tester disconnect with pending request
If a tester disconnects while a request is pending, the software shall
release the pending request at once. A later response from the ECU shall be
discarded and counted.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-07 |
| Verification | IT |
| Criterion | After the disconnect the route accepts a request from a new tester immediately. |

### SWR-042 Unsolicited responses
A CAN response with no matching pending request (unsolicited or late) shall
be discarded and counted. It shall not be forwarded to any tester.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-07 |
| Verification | UT, IT |
| Criterion | Injected frames on `0x7E9` with no pending request reach no tester and increment the counter. |

### SWR-043 Static resources
The software shall allocate all memory at initialisation and none while
running. Buffer counts and sizes shall be fixed by configuration.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-07 |
| Verification | AN |
| Criterion | No `new`, `malloc` or heap-using ETL/STL calls are reachable after `init()` (static analysis plus a heap hook in IT). |

### SWR-044 Start-up and shutdown
The software shall start its components in lifecycle order:

1. CAN, Ethernet
2. ISO-TP, router, UDS
3. DoIP announcement

On SIGINT/SIGTERM it shall, within 1 s:

- close all tester connections
- abort pending ISO-TP transfers
- stop CAN transmission
- exit with status 0

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-06, SYS-07 |
| Verification | IT |
| Criterion | No announcement is sent before CAN and ISO-TP are ready; shutdown completes within 1 s with exit status 0; candump shows no gateway frame after exit. |

## Platform and configuration

### SWR-050 Linux host target
The software shall build and run on Linux x86_64 using the OpenBSW POSIX
platform:

- **CAN:** SocketCAN, interface selectable with `ZGW_CAN_INTERFACE`, default `vcan0`
- **Ethernet:** lwIP on a TAP interface selectable with `ZGW_TAP_INTERFACE`
  (default `tap0`), with DoIP reachable on port 13400 from the host

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-06 |
| Verification | IT, QT |
| Criterion | A host DoIP tester reaches the gateway on TAP; the gateway exchanges ISO-TP with simulated ECUs on `vcan0`; the CDA container path is qualified separately. |

### SWR-051 Embedded portability
The gateway application code shall use only OpenBSW abstractions: `async`,
`lifecycle`, transport, CAN and IP interfaces. It shall make no direct POSIX
calls, so that it also builds for the S32K148 platform.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-06 |
| Verification | AN |
| Criterion | The S32K148 build of the application compiles and links; a grep check finds no POSIX headers outside `platforms/posix`. |

### SWR-052 Single-source configuration
The routing table shall have one source, `OpenBSW/config/routing.yaml`. From it
the build shall generate:

- the gateway's C++ routing configuration
- an address table that the CDA MDD and the ECU CAN profiles are checked against

A mismatch shall fail the build.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-09 |
| Verification | UT, AN |
| Criterion | Changing an address in only one place makes the consistency check fail and names the field. |

### SWR-053 Pinned OpenBSW revision
The build shall fetch Eclipse OpenBSW at the commit recorded in a lock file,
and verify that the checkout has no tracked modifications. This is the same
scheme as ThreadX `dependencies.lock.json`.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-10 |
| Verification | AN |
| Criterion | A modified or different checkout stops the configure step with an error. |

### SWR-054 Observability
The software shall log through the OpenBSW logger:

- at start-up: its version, OpenBSW revision and routing-table hash
- every 30 s: the routing statistics
- at debug level: each routing event (source, target, SID, result)

On SIGINT/SIGTERM the POSIX platform exits at once (SWR-044), so no final
statistics line is written; the counters stay readable through `FD01` while
the gateway runs.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-04 |
| Verification | IT |
| Criterion | The start-up line names the routing-table hash; a statistics line appears within 35 s of start-up and matches `FD01`. |

## Timing

### SWR-060 Forwarding latency
For single-frame requests and responses on the Linux host target, the
gateway shall add at most 10 ms in each direction at the 95th percentile:

- from the DoIP diagnostic message to the CAN request frame
- from the CAN response frame to the DoIP response

| Attribute | Value |
| --- | --- |
| Type | Performance |
| Derived from | SYS-08 |
| Verification | IT, QT |
| Criterion | 1000 `22 F1 95` round trips measured with packet and CAN timestamps; p95 ≤ 10 ms per direction. |

## Traceability summary

| System requirement | Software requirements |
| --- | --- |
| SYS-01 | SWR-001, SWR-012 |
| SYS-02 | SWR-001, SWR-002, SWR-003, SWR-004, SWR-005, SWR-017, SWR-018 |
| SYS-03 | SWR-003, SWR-010, SWR-011, SWR-012, SWR-013, SWR-014 |
| SYS-04 | SWR-011, SWR-020, SWR-021, SWR-022, SWR-023, SWR-024, SWR-025, SWR-026, SWR-027, SWR-054 |
| SYS-05 | SWR-024, SWR-030, SWR-031, SWR-032, SWR-033 |
| SYS-06 | SWR-044, SWR-050, SWR-051 |
| SYS-07 | SWR-003, SWR-004, SWR-015, SWR-016, SWR-017, SWR-023, SWR-040, SWR-041, SWR-042, SWR-043, SWR-044 |
| SYS-08 | SWR-060 |
| SYS-09 | SWR-010, SWR-022, SWR-052 |
| SYS-10 | SWR-021, SWR-053 |

## Open points

- **OP-1:** confirm the DoIP logical addresses and functional address the CDA expects, and author the MDD for `0x1010` and `0x1020` (SWR-001, SWR-052).
- **OP-2:** the ThreadX rear lighting ECU needs a UDS-on-CAN server for SWR-012 and SWR-024 to be qualified end to end. Until then, IT uses a simulated ECU.
- **OP-3 (closed):** `TransportRouterSimple` cannot route by logical address. The router is a new OpenBSW module, `transportRouter`, prepared as an upstream contribution (AD-02).
- **OP-4:** `U0140`/`U0141` are illustrative fault codes; align them with the MDD.
- **OP-5:** ISO-TP STmin and block size are one setting for all routes (OpenBSW DoCAN parameters are per transport layer); per-route values need an upstream DoCAN extension.
