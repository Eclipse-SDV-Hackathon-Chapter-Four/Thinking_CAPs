# Pull request draft — eclipse-openbsw/openbsw

**Title:** Add doipClient module for DoIP client connections

**Base:** `main` at `b0550871b7a44ae47bb9b7c68af84fb9115bfa77` · **Patch:**
[0001-doip-client.patch](0001-doip-client.patch) (one commit, signed off, `Assisted-by` trailer)

**Tag:** `tested_on_hw` (S32K148EVB, see Test Plan)

The body below follows `.github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md`. Open it
once the committers have agreed on the approach in #663.

---

## Purpose of this PR
- [ ] Bugfix
- [x] New Feature
- [ ] Documentation Update
- [ ] Other (Please specify)

**Description**

OpenBSW provides the server side of DoIP only. This PR adds the client side (external
test equipment, ISO 13400-2) as a new module, `libs/bsw/doipClient`, so an OpenBSW node
can send diagnostic messages to other DoIP entities. A diagnostic gateway can then route
requests from its DoIP server to Ethernet ECUs, in the same way as to CAN ECUs through
DoCAN.

`doip::DoIpClientTransportLayer` is an `AbstractTransportLayer`:

- opens one TCP connection per configured node with the first message and activates
  routing (activation type `0x00`); the connection is kept
- reports a message as processed when the node acknowledges it (`0x8002` success,
  `0x8003` error), once TCP has released its buffer
- fails a message whose connection set-up, routing activation or acknowledgement exceeds
  the configured delivery budget; a refused connection or activation fails it at once
- sends functional messages to every node with active routing
- passes the nodes' diagnostic messages to the transport message provider and listener,
  and answers alive check requests

It reuses `DoIpTcpConnection` and the send jobs of `doip`, and any `tcp::AbstractSocket`.
Memory is static. The module documentation is in `libs/bsw/doipClient/doc/index.rst`
(Sphinx build without warnings).

Changed outside the module: one `add_subdirectory` line each in `libs/bsw/CMakeLists.txt`
and in the unit-test list of the top-level `CMakeLists.txt`.

**AI disclosure:** the module was largely written with an AI assistant (Anthropic Claude
Opus 5.5) and reviewed and tested by the author. Each new file says so below its
copyright header, and the commit carries `Assisted-by: Anthropic Claude Opus 5.5`
(Eclipse Foundation generative AI guidelines).

**Related Issues**

Resolves #663 (feature request: Add a DoIP client transport layer)

Found while building it, reported separately: #660 (DoIpTcpConnection empty payload
discard), #661 (SocketCanTransceiver with the ThreadX POSIX port), #662
(AbstractSocketMock::inject before any read).

**Breaking Changes**
- [ ] Yes
- [x] No

**Test Plan**

- Unit tests: `cmake --preset tests-posix-debug`, build `doipClientTest`, run
  `ctest -L doipClient` (20 tests, gmock `StrictMock`s, OpenBSW async test context).
  Line coverage 94 %, function coverage 97 % (gcovr). Bazel:
  `bazel test //libs/bsw/doipClient/... //libs/bsw/doip/...`.
- Gates on `main` `b0550871`: treefmt (clang-format 17, cmake-format, buildifier) clean,
  `tools/cr_checker` ok, clang-tidy with the repository `.clang-tidy` 0 findings, unit-test
  build with 0 warnings, gitlint ok, Sphinx documentation build without warnings.
- Integration, outside this repository: a zonal diagnostic gateway built on OpenBSW routes
  tester requests through a router to an Ethernet ECU with this module (a simulated DoIP
  entity on the host). 14 tests on POSIX (connection reuse, 3000-byte response,
  4000-byte request, response pending, functional, alive check, NACK, missing ACK,
  refused activation and connection, closure by the node) and 5 on the **S32K148EVB**
  with ThreadX over 100BASE-T1 passed; routed round trip p95 4.1 ms on the board.

**Regression Tests**

Have tests been added/updated? [x] Yes [ ] No
