# Software detailed design (SWE.3)

The units are Python functions and classes. They have type annotations
(checked by mypy) and docstrings in the source. Activity diagrams in
[diagrams/](diagrams/) cover the units with non-trivial control flow.

## Software units

The report generator parses this table: ID | Unit | Source / functions | Element | Implements.

| ID | Unit | Source / functions | Element | Implements |
| --- | --- | --- | --- | --- |
| DD-01 | Frame encoder | `slcan.py`: `_check_encodable`, `encode` | ARC-01 | SWR-002, SWR-010 |
| DD-02 | Frame decoder | `slcan.py`: `decode` | ARC-01 | SWR-001 |
| DD-03 | Stream tokeniser | `slcan.py`: `LineSplitter.feed`, `tokens` | ARC-01 | SWR-003 |
| DD-04 | Identifier filter | `serial2can_bridge.py`: `IdFilter`, `_int` | ARC-02 | SWR-007 |
| DD-05 | Echo guard | `serial2can_bridge.py`: `EchoGuard.sent`, `is_echo`, `_signature` | ARC-03 | SWR-009 |
| DD-06 | Connection lifecycle | `SerialLink._read_loop`, `_open`, `_resolve_device`, `_serve`, `_end_session` | ARC-04 | SWR-020, SWR-024 |
| DD-07 | Handshake | `SerialLink._handshake`, `_command` (pending-token queue) | ARC-04 | SWR-003, SWR-004 |
| DD-08 | Token handling | `SerialLink._handle` | ARC-04 | SWR-005, SWR-007, SWR-024 |
| DD-09 | Transmit path | `SerialLink.enqueue`, `_write_loop`, `_drain_queue`, `close` | ARC-05 | SWR-006, SWR-010, SWR-021, SWR-023 |
| DD-10 | Bus forwarding | `Serial2CanBridge.__init__`, `from_serial` | ARC-06 | SWR-005, SWR-008, SWR-009, SWR-011, SWR-022, SWR-030, SWR-031, SWR-032 |
| DD-11 | CAN receive and lifecycle | `Serial2CanBridge.run`, `_dispatch`, `log_stats`, `shutdown` | ARC-06 | SWR-006, SWR-010, SWR-023, SWR-024 |
| DD-12 | Configuration and CLI | `load_config`, `main`, `request_stop` | ARC-07 | SWR-012, SWR-023 |
| DD-13 | Launcher | `launch/bridge_launch.py` | ARC-08 | SWR-011 |
| DD-14 | Dependency pins | `requirements.txt`, `requirements-dev.txt` | ARC-09 | SWR-033 |

## Unit design notes

**DD-03.** `feed()` is eager. It returns a list and clears its buffer before
handing tokens out. An earlier generator version kept a stale line when the
consumer stopped iterating early. Integration testing found that defect, and
`test_handshake_both_directions_filters_and_close` now covers it.

**DD-06.** The reader owns the port. On a lost link it clears `connected`,
closes the port and drains the queue. The session-local `established` flag
counts the disconnect even when the writer already cleared `connected`;
robustness testing found the original under-count.

**DD-07.** Command replies are read through a pending-token deque. A frame
that arrives in the same read as a reply (the AZ3166 reports its state right
after `O`) is forwarded, not dropped.

**DD-09.** The writer serialises writes with `_write_lock` (shared with
handshake commands). On a write error it only clears `connected` and closes
the port; the reader then reconnects.

**DD-10/11** ([forwarding-core.puml](diagrams/forwarding-core.puml)).

- `bus.send` and the echo record share `_send_lock`, so an echo can never
  arrive before it is recorded.
- `message.channel` is left unset, because SocketCAN would read it as an
  interface name.

## Coding guidelines

See [coding-guidelines.md](coding-guidelines.md).
