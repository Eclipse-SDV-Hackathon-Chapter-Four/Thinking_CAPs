# Software architectural design (SWE.2)

| View | File | Purpose |
| --- | --- | --- |
| Context | [context.puml](diagrams/context.puml) | Bridge inside the X-COM layer and X-Verse |
| Static | [components.puml](diagrams/components.puml) | Modules, classes and interfaces |
| Dynamic | [threads.puml](diagrams/threads.puml) | Threads, queues, locks and events |
| Dynamic | [handshake.puml](diagrams/handshake.puml) | Connection and Lawicell handshake |
| Dynamic | [forwarding.puml](diagrams/forwarding.puml) | Filters, fan-out and echo suppression |
| Behaviour | [link-state.puml](diagrams/link-state.puml) | Per-port connection state machine |

## Design decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| AD-01 | Lawicell SLCAN as the serial protocol | Readable, already spoken by the AZ3166 firmware, and supported by Linux `slcand` and python-can, so devices can also be used without this bridge. |
| AD-02 | python-can as the CAN abstraction | Same library and version as the X-Verse Zenoh2CAN bridge. One code path for SocketCAN, `udp_multicast` and `virtual` (SWR-011, SWR-033). |
| AD-03 | Two threads per port (reader, writer) plus the main CAN loop | A slow UART or a reconnect never blocks the CAN side or other ports (SWR-021). |
| AD-04 | Bounded per-port queues that drop and count | Back-pressure is visible in the statistics instead of growing memory or latency (SWR-021, SWR-024). |
| AD-05 | Serial-to-serial fan-out inside the bridge | The CAN interface does not deliver a sender's frames back to the same socket, so ECUs on different ports would not see each other otherwise (SWR-008). |
| AD-06 | Count-based echo guard, on by default only for `udp_multicast` | That bus loops back own frames; one cancellation per sent frame keeps identical frames from other nodes (SWR-009). |
| AD-07 | Reader thread owns the connection lifecycle; the writer only reports errors | One place opens, handshakes and closes, so there are no races on reconnect (SWR-020). |
| AD-08 | Close (`C`) to every ECU on shutdown | Lets ECUs fall back to their safe state (SWR-023). |

## Software elements

The report generator parses this table: ID | Element | Responsibility | Satisfies.

| ID | Element | Responsibility | Satisfies |
| --- | --- | --- | --- |
| ARC-01 | SLCAN codec (`slcan.py`) | Encode and decode frame lines, tokenise the device stream | SWR-001, SWR-002, SWR-003, SWR-010 |
| ARC-02 | `IdFilter` | Per-direction id/mask/extended matching | SWR-007 |
| ARC-03 | `EchoGuard` | Cancel one looped-back copy per sent frame | SWR-009 |
| ARC-04 | `SerialLink` connection manager (reader thread) | Resolve device, open, handshake, read and dispatch tokens, detect loss, reconnect | SWR-003, SWR-004, SWR-005, SWR-020, SWR-024 |
| ARC-05 | `SerialLink` transmitter (queue and writer thread) | Filter, queue, encode and write frames; drop and count; close channel on exit | SWR-006, SWR-010, SWR-021, SWR-023 |
| ARC-06 | `Serial2CanBridge` core | Open the bus, forward serial → CAN, fan out, receive CAN → ports, statistics, shutdown | SWR-005, SWR-006, SWR-008, SWR-009, SWR-011, SWR-022, SWR-023, SWR-024, SWR-030, SWR-031, SWR-032 |
| ARC-07 | Configuration and CLI (`load_config`, `main`) | Load and validate JSON, apply `--device` overrides, logging, signals | SWR-012, SWR-023 |
| ARC-08 | Launcher (`launch/bridge_launch.py`) | Prepare `vcan0` (sudo) when the config uses SocketCAN, then start the bridge | SWR-011 |
| ARC-09 | Dependency set (`requirements*.txt`) | Pin python-can 4.2.2, pyserial 3.5 and msgpack, as X-Verse does | SWR-033 |

## Interfaces

| ID | Interface | Provider → consumer | Type and contract |
| --- | --- | --- | --- |
| IF-01 | SLCAN over serial | ECU ↔ ARC-04/05 | External. Lawicell lines, CR-terminated, 115200 8N1 by default |
| IF-02 | python-can `Bus.send` / `recv` | ARC-06 ↔ CAN bus | External. Classic frames; `udp_multicast` loops back own frames |
| IF-03 | JSON configuration | User → ARC-07 | External. `can`, `serial_ports[]`, `stats_interval_s`, `echo_window_s` ([README](../../README.md#configuration)) |
| IF-04 | CLI and signals | User → ARC-07 | External. `config`, `--device NAME=PATH`, `--log-level`; SIGINT/SIGTERM stop |
| IF-05 | `from_serial(source, message)` | ARC-04 → ARC-06 | Internal. Called on the reader thread; non-blocking apart from `bus.send` |
| IF-06 | `enqueue(message)` | ARC-06 → ARC-05 | Internal. Never blocks; filtered, offline or queue-full outcomes are counted |
| IF-07 | Statistics log line | ARC-06 → operator | External. `stats {json}` every `stats_interval_s` and at shutdown |

## Resources

| Resource | Allocation |
| --- | --- |
| Threads | 1 main + 2 per serial port (daemon threads, joined on close) |
| Memory | Bounded: `tx_queue` frames per port (default 256); echo guard entries expire after `echo_window_s` |
| Serial bandwidth | 115200 baud ≈ 500 frames/s per port; `to_serial` filters keep the load below that |
