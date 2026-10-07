# Issue draft — eclipse-openbsw/openbsw (feature request)

Open this issue first and agree on the approach before the pull request
(CONTRIBUTING.md: "talk with the team through an issue"; `pull_request.rst`: a
completely new feature must be discussed with the committers).

**Title:** Add a DoIP client transport layer (doipClient)

**Labels:** enhancement

---

**Describe the feature**

OpenBSW implements the server side of DoIP (ISO 13400-2) in `libs/bsw/doip`: a node
accepts external testers. There is no client side, so an OpenBSW node cannot send
diagnostic messages to another DoIP entity.

A diagnostic gateway needs that side. It receives UDS requests from a tester over
DoIP and forwards them to the ECUs behind it. Today it can reach CAN ECUs through
DoCAN, but not Ethernet ECUs, which are reached over DoIP in zonal architectures.

I propose a new module, `libs/bsw/doipClient`, with a DoIP client transport layer.

**Proposed Solution**

`doip::DoIpClientTransportLayer`, an `AbstractTransportLayer`, so that it plugs into
the transport system in the same way as `DoCanTransportLayer`:

- One TCP connection per configured node (logical address and IP address), opened by
  the first message and kept. Routing activation with the client's logical address
  and activation type `0x00`; diagnostic messages after response code `0x10`.
- A physical message is reported as processed when the node acknowledges it
  (`0x8002` success, `0x8003` error). The report waits until TCP has released the
  buffer, because the send job reads from it.
- A delivery budget covers connection set-up, routing activation and the
  acknowledgement. When it expires, the connection is closed and the message fails.
  A refused connection or activation, or a closure by the node, fails the message at
  once; the next message reconnects.
- Functional messages go to every node with active routing.
- Diagnostic messages from a node to the client's address go to the transport
  message provider and listener, with the node as source; alive check requests are
  answered.
- It reuses `doip::DoIpTcpConnection` and the send jobs of `doip`, and any
  `tcp::AbstractSocket` (e.g. `tcp::LwipSocket`). Memory is static. No existing module
  changes.

Use case: an OpenBSW zonal diagnostic gateway that routes requests from its DoIP
server to CAN ECUs (DoCAN) and Ethernet ECUs (this module) through a router.

Not in scope: DoIP over TLS, vehicle discovery over UDP (node addresses are
configured), several logical addresses behind one DoIP entity on one connection.

Not specific to an operating system, compiler or build system; tested with GCC 11.4
(POSIX unit tests, CMake and Bazel) and on the S32K148EVB (Arm GNU Toolchain 14.3,
ThreadX).

**Additional context**

- A working implementation with unit tests (20, 94 % line coverage, OpenBSW format,
  copyright, clang-tidy and Bazel gates passed on `main`) is ready as one commit.
  It was used in a zonal diagnostic gateway: 14 integration tests on POSIX and 5 on
  the S32K148EVB route requests over DoIP to a simulated Ethernet ECU.
- The implementation was largely written with an AI assistant (Anthropic Claude Opus
  5.5) and reviewed and tested by me. Following the Eclipse Foundation guidelines on
  generative AI, each new file states this below its copyright header, and the commit
  carries an `Assisted-by:` trailer. **Question for the committers:** do you want the
  file headers in another form, for example the dual `Apache-2.0 AND CC0-1.0` SPDX
  expression from the Eclipse handbook template? The current OpenBSW copyright checker
  expects `SPDX-License-Identifier: Apache-2.0`.
- While building it I found three issues in existing code, reported separately:
  the `DoIpTcpConnection` discard continuation with an empty payload (#660),
  `SocketCanTransceiver` with the ThreadX POSIX port (#661), and
  `AbstractSocketMock::inject` (#662).
