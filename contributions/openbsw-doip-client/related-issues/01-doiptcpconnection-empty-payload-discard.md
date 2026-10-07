# Issue draft — eclipse-openbsw/openbsw (bug report)

**Title:** DoIpTcpConnection stops reading after discarding a message with an empty payload

**Labels:** bug

---

**Describe the bug**

When an `IDoIpConnectionHandler` answers `headerReceived()` with the discard
continuation (`IDoIpConnection::PayloadDiscardedCallbackType`) for a message whose
payload length is 0, `DoIpTcpConnection` sets an empty discard buffer
(`setReadBuffer(span(_headerBuffer, 0))`). `tryReceive()` only reads while the
current read buffer is not empty, so the connection never leaves `ReadState::DISCARD`
and no further message is read.

`endReceiveMessage()` handles the same case correctly (payload length 0 → back to
`ReadState::HEADER`). The DoIP server does not hit the bug because it receives no
empty-payload messages over TCP, but a DoIP client receives alive check requests
(`0x0007`, payload length 0).

**Steps to reproduce the bug**

[`evidence/ReproUpstreamFindingsTest.cpp`](evidence/ReproUpstreamFindingsTest.cpp),
test `DiscardContinuationWithEmptyPayloadStopsReception`, added to `doipTest` on
`main` (`b0550871`): inject an alive check request (handler returns the discard
continuation), then another header.

**Expected behavior and actual behavior**

Expected: `headerReceived()` is called for the second message. Actual: it is not
([`evidence/repro-output.txt`](evidence/repro-output.txt)).

**Environment**

Ubuntu 22.04, GCC 11.4, CMake preset `tests-posix-debug`, `main` at `b0550871`.

**Additional context**

Possible fix: in `processNextReadChunk()`, when the handler returns the discard
continuation and `_readPayloadLength == 0`, go back to `ReadState::HEADER` and call the
discard callback, as `endReceiveMessage()` does. The proposed `doipClient` module works
around it by calling `endReceiveMessage()` itself.
