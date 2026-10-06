# Software requirements specification (SWE.1)

| Item | Value |
| --- | --- |
| Software | X-COM Serial2CAN bridge, `X-Verse/bridges/serial2can/src` |
| Inputs | [System requirements](system-requirements.md), [README](../../README.md), Lawicell SLCAN protocol |
| Status | Baselined for the hackathon demonstration, 6 October 2026 |

Each requirement has:

- a unique ID
- a *Derived from* link to system requirements
- a type
- the planned verification levels: **UT** unit test, **IT** integration test
  (host or on target), **QT** qualification test in X-Verse, **AN** analysis,
  **RV** review
- a criterion

The [report generator](../tools/generate_report.py) parses this file.

## Protocol

### SWR-001 Decode SLCAN frames
The software shall decode device lines `t`/`T`/`r`/`R` (11/29-bit, data or
remote) into CAN messages. It shall accept upper- and lower-case hex and an
optional 4-digit timestamp. It shall reject lines whose length, DLC (> 8),
identifier range or characters are invalid.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01 |
| Verification | UT |
| Criterion | All 256 status bytes round-trip; 15 malformed lines rejected. |

### SWR-002 Encode SLCAN frames
The software shall encode CAN messages as upper-case SLCAN lines terminated
by CR. It shall refuse error frames, CAN FD frames, DLC > 8, out-of-range
identifiers and data shorter than the DLC.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01 |
| Verification | UT |
| Criterion | Exact encodings for standard, extended and remote frames; refusals raise `SlcanError`. |

### SWR-003 Tokenise the device stream
The software shall split the device byte stream into CR-terminated lines and
BELL tokens, regardless of read chunk boundaries. It shall ignore LF and
discard lines longer than the longest frame line. No token shall be lost when
a consumer stops between tokens.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01, SYS-04 |
| Verification | UT, IT |
| Criterion | Split chunks give identical tokens; overlong lines are reported once; the handshake forwards the frame that follows the open reply. |

### SWR-004 Device handshake
On every connection the software shall send `C`, `V`, `S<n>` for the
configured nominal bitrate, then `O`. It shall treat a missing acknowledgement
of `O` as a connection failure. It shall forward frames the device sends
during the handshake.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-01 |
| Verification | IT |
| Criterion | Simulated and physical ECUs receive `C, V, S6, O` in order; the ECU's state report after `O` reaches the bus. |

## Forwarding

### SWR-005 Serial to CAN
The software shall transmit every frame a device sends, if it passes that
port's `from_serial` filter, on the configured CAN bus.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01 |
| Verification | IT, QT |
| Criterion | ECU frames appear on the bus; filtered IDs do not. |

### SWR-006 CAN to serial
The software shall send every frame received from the CAN bus to each
connected port whose `to_serial` filter accepts it.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01 |
| Verification | IT, QT |
| Criterion | Accepted IDs reach the ECU; filtered IDs do not. |

### SWR-007 Identifier filters
Each port shall have independent `to_serial` and `from_serial` filters with
entries `id` / `mask` / optional `extended`. A frame matches when
`(id & mask) == (filter_id & mask)`. An empty or missing list accepts all
frames. The default mask is an exact 11- or 29-bit match.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01, SYS-04 |
| Verification | UT, IT |
| Criterion | Exact, masked, extended-only and empty filters behave as specified. |

### SWR-008 Serial-to-serial fan-out
A frame from one serial port shall also be sent to every other port whose
filter accepts it, as on a shared bus. It shall never return to its source port.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01 |
| Verification | IT |
| Criterion | With two ECUs, a frame from A reaches B and the bus, but not A. |

### SWR-009 Echo suppression
On buses that loop back their own frames (default: `udp_multicast`), the
software shall drop exactly one received copy per frame it transmitted,
within `echo_window_s`.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-03 |
| Verification | UT, IT, QT |
| Criterion | An ECU's own frame is not returned to it; frames from other nodes still are. |

### SWR-010 Unsupported frames
The software shall not write error frames or CAN FD frames to serial ports.
It shall ignore error frames received from the bus.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-04 |
| Verification | IT |
| Criterion | FD and error frames never reach the ECU and are counted as filtered. |

## Bus and configuration

### SWR-011 CAN bus selection
The software shall open any python-can interface given in the configuration.
For SocketCAN it shall omit the bitrate (configured by the OS). For
`udp_multicast` it shall use classic frames.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02, SYS-03 |
| Verification | IT, QT |
| Criterion | Works on `virtual` and `udp_multicast`; SocketCAN `vcan0` is exercised when available. |

### SWR-012 Configuration and command line
The software shall:

- load a JSON configuration (`can`, and `serial_ports` with unique `name`
  and a `device`)
- validate the nominal bitrate against the Lawicell `S0`–`S8` set
- support `--device NAME=PATH` overrides and `--log-level`
- reject invalid configurations with an error

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02 |
| Verification | UT |
| Criterion | Shipped configs load; malformed overrides, empty port lists, duplicate names and bad bitrates are rejected. |

## Robustness and lifecycle

### SWR-020 Reconnection
The software shall detect a lost device (read or write errors), mark the
port offline, and retry every `reconnect_s`. It shall repeat the handshake on
reconnection and resolve glob device paths at each attempt. Devices that
cannot be opened shall be retried without affecting other ports.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-04 |
| Verification | IT |
| Criterion | Unplug and replug, write failure and late-appearing devices all reconnect; a non-tty device does not block other ports. |

### SWR-021 Bounded, non-blocking queueing
Each port shall have a bounded transmit queue. Frames for a full or offline
port shall be dropped and counted. The CAN receive loop shall never block on
a serial port.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-04 |
| Verification | UT, IT |
| Criterion | Queue-full and offline drops are counted; queued frames are discarded on disconnect. |

### SWR-022 CAN transmit errors
A failed CAN transmission shall be counted and logged. Forwarding to other
serial ports shall continue.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-04 |
| Verification | IT |
| Criterion | With a failing bus, the error counter increases and the other ECU still receives the frame. |

### SWR-023 Safe shutdown
On SIGINT or SIGTERM the software shall:

- send `C` to every connected device
- close the ports and the bus
- log final statistics
- exit with status 0

| Attribute | Value |
| --- | --- |
| Type | Safety-related |
| Derived from | SYS-05 |
| Verification | IT |
| Criterion | Simulated and physical ECUs receive `C`; the AZ3166 reports lamps off afterwards. |

### SWR-024 Statistics
The software shall log, every `stats_interval_s` and at shutdown, one JSON
line with:

- bus counters
- per-port counters: frames in each direction, filtered, dropped, ACK and
  BELL counts, malformed lines, connects and disconnects
- the connection state

Disconnects shall be counted exactly once per lost session.

| Attribute | Value |
| --- | --- |
| Type | Diagnostic |
| Derived from | SYS-06 |
| Verification | IT |
| Criterion | Counters match the traffic of the hardware check; a writer-detected loss counts one disconnect. |

## Performance and integration

### SWR-030 Round-trip time through the bridge
With the AZ3166 at 115200 baud, the median CAN → ECU → CAN round trip through
the bridge shall be ≤ 10 ms.

| Attribute | Value |
| --- | --- |
| Type | Performance |
| Derived from | SYS-07 |
| Verification | IT |
| Criterion | Hardware check median ≤ 10 ms over 256 frames. |

### SWR-031 End-to-end latency in X-Verse
With the bridge in the path, the time from the VCU status publication to the
matching CARLA lamp state shall be ≤ 100 ms.

| Attribute | Value |
| --- | --- |
| Type | Performance |
| Derived from | SYS-07 |
| Verification | QT |
| Criterion | Every live qualification step ≤ 100 ms. |

### SWR-032 X-Verse interoperability
The software shall carry the X-Verse lighting traffic between the unmodified
Zenoh2CAN bridge and the ECU, in the full `run_autoverse.py` environment.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-01, SYS-02 |
| Verification | QT |
| Criterion | Four lamp states, driven from Vehicle Manual Control, reach the CARLA actor. |

### SWR-033 Dependency alignment
The software shall use the same python-can version as the X-Verse Zenoh2CAN
bridge (4.2.2) and run on Python 3.10, the X-Verse interpreter.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-02 |
| Verification | AN |
| Criterion | Pinned version equals the X-Verse lock; tests run on Python 3.10. |
