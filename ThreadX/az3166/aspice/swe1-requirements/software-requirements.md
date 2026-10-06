# Software requirements specification (SWE.1)

| Item | Value |
| --- | --- |
| Software | `threadx-zonal-lights-az3166` 1.0.0 |
| Scope | Firmware in `ThreadX/az3166/src` plus the shared unit `ThreadX/src/lights_protocol.c` |
| Inputs | [System requirements](system-requirements.md), [CAN lighting contract](../../../docs/can-lighting-contract.md), [UART-CAN transport](../../docs/uart-can-transport.md) |
| Status | Baselined for the hackathon demonstration, 6 October 2026 |

Each requirement has:

- a unique ID
- a *Derived from* link to system requirements (bidirectional traceability)
- a type
- the planned verification levels: **UT** unit test (SWE.4), **IT** software
  integration test (SWE.5), **QT** software qualification test (SWE.6), **AN**
  analysis, **RV** review or inspection
- a verification criterion

The [report generator](../tools/generate_report.py) parses this file.

## Functional requirements

### SWR-001 Decode VCU status
The software shall accept a classic standard CAN frame with identifier
`0x1F1` and DLC 8 as VCU status. It shall read reverse status from byte 0
bit 1 and brake status from byte 0 bit 2, and ignore all other bits and bytes.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01, SYS-02 |
| Verification | UT, IT, QT |
| Criterion | All 256 values of byte 0 produce the expected lamp state; other bytes have no effect. |

### SWR-002 Encode light command
For every accepted VCU status the software shall emit one light command frame:
`0x1F4`, DLC 8, byte 0 bit 0 = reverse lamp, bit 1 = brake lamp, all other
bits and bytes zero.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01, SYS-02 |
| Verification | UT, IT, QT |
| Criterion | Exactly one `0x1F4` per accepted `0x1F1`, with exact payload. |

### SWR-003 Reject non-conforming frames
The software shall not change lamp state for frames with any other
identifier, a DLC other than 8, an extended identifier, the remote (RTR) flag
or the error flag. It shall count such frames as rejected.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-02 |
| Verification | UT, IT |
| Criterion | No `0x1F4` emitted for each rejected frame kind; rejected counter increases by the number sent. |

### SWR-004 Actuate lamps
The software shall drive the brake lamp output (RGB LED red, PB4) and the
reverse lamp output (user LED, PC13) to match the latest light command. It
shall do so in the same control cycle that emits the command.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01 |
| Verification | RV |
| Criterion | Visual inspection of the board LEDs for the four lamp states. |

### SWR-005 Hold state
By default the software shall hold the latest light command until the next
valid VCU status arrives. It shall not re-emit an unchanged command.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-01 |
| Verification | IT |
| Criterion | No `0x1F4` emitted during 5 s without input; the diagnostic frame keeps reporting the held state. |

### SWR-006 Optional input timeout
When built with `ZONAL_TIMEOUT_MS` > 0, the software shall:

- switch both lamps off and emit an all-off command once no valid status has
  been received for that time
- flag the state as stale
- recover on the next valid status

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-03 |
| Verification | IT |
| Criterion | With a 1000 ms build, lamps off within 1000 ms + 1 tick after the last input; recovery on the next input. |

### SWR-007 Start-up state
After reset the software shall keep both lamps off and the SLCAN channel
closed. It shall transmit nothing until a host opens the channel.

| Attribute | Value |
| --- | --- |
| Type | Safety-related |
| Derived from | SYS-03 |
| Verification | UT, IT |
| Criterion | First frame after opening is an all-off `0x1F4`; no output while closed. |

### SWR-008 Report state on link open
When the host opens the channel, the software shall acknowledge, then
transmit the current light command.

| Attribute | Value |
| --- | --- |
| Type | Functional |
| Derived from | SYS-02 |
| Verification | IT |
| Criterion | `0x1F4` with the current state follows the open acknowledgement. |

### SWR-009 Fail-safe on link close
When the host closes the channel, the software shall switch both lamps off and
stop transmitting.

| Attribute | Value |
| --- | --- |
| Type | Safety-related |
| Derived from | SYS-03 |
| Verification | IT, QT |
| Criterion | After close and re-open, the reported command is all-off. |

## Communication requirements

### SWR-010 Serial transport
The software shall use USART6 (PA11/PA12) at 115200 baud, 8N1. It shall carry
one SLCAN command per line terminated by CR and ignore LF.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-05 |
| Verification | IT |
| Criterion | Host at 115200 8N1 completes the Lawicell dialogue. |

### SWR-011 SLCAN command set
The software shall implement the Lawicell commands with the replies in the
[transport contract](../../docs/uart-can-transport.md):

- `O`, `C`, `V`, `N`, `F`
- `S0`–`S8`, `sXXXX` and `Z0`, accepted only while closed

It shall reply BELL to any other command.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02, SYS-05 |
| Verification | UT, IT |
| Criterion | Every listed command parses and returns the specified reply; unsupported commands return BELL. |

### SWR-012 Frame acknowledgement
While the channel is open, the software shall acknowledge each well-formed
frame from the host with `z` (standard) or `Z` (extended). While the channel
is closed, it shall reply BELL.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02 |
| Verification | IT |
| Criterion | Correct acknowledgement per frame kind and channel state. |

### SWR-013 Malformed input handling
The software shall answer malformed or over-long lines (more than 26
characters) with BELL. It shall count them and shall not actuate.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-02 |
| Verification | UT, IT |
| Criterion | All malformed test lines are rejected; no lamp change. |

### SWR-014 Frame encoding
The software shall encode transmitted frames as SLCAN `t`/`T`/`r`/`R` lines
with upper-case hexadecimal, terminated by CR.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02 |
| Verification | UT, IT |
| Criterion | Encoded lines round-trip through the parser and python-can. |

## Diagnostic requirements

### SWR-020 Diagnostic heartbeat
While the channel is open, the software shall emit diagnostic frame `0x1F5`
every 1 s ± 10% from a ThreadX timer. The frame carries the lamp state, the
stale, loss and OLED flags, the counters and the uptime, as in the transport
contract.

| Attribute | Value |
| --- | --- |
| Type | Diagnostic |
| Derived from | SYS-04 |
| Verification | IT |
| Criterion | Measured intervals within 0.9–1.1 s; uptime increments by 1 s. |

### SWR-021 Loss accounting
The software shall count UART receive overruns, queue overflows and dropped
transmissions. It shall report losses in the diagnostic frame and in the
SLCAN `F` status reply.

| Attribute | Value |
| --- | --- |
| Type | Diagnostic |
| Derived from | SYS-04 |
| Verification | IT |
| Criterion | Loss flag clear under the nominal test load. |

### SWR-022 Status LEDs
The software shall toggle the Wi-Fi LED at every heartbeat. It shall light the
Azure LED while the channel is open.

| Attribute | Value |
| --- | --- |
| Type | Diagnostic |
| Derived from | SYS-04 |
| Verification | RV |
| Criterion | Visual inspection. |

### SWR-023 OLED status display
The software shall show link state, brake, reverse, counters and uptime on
the OLED. An OLED failure shall not affect lamp control or communication.

| Attribute | Value |
| --- | --- |
| Type | Diagnostic |
| Derived from | SYS-04 |
| Verification | IT, RV |
| Criterion | OLED flag set in the diagnostic frame; the display thread runs at lowest priority and stops on I2C failure. |

## Robustness requirements

### SWR-030 Fault reaction
On a failed ThreadX service call, a thread stack overflow, a CPU fault or an
unexpected interrupt, the software shall:

- switch both lamps off
- light the RGB LED blue
- stop

| Attribute | Value |
| --- | --- |
| Type | Safety-related |
| Derived from | SYS-03 |
| Verification | RV |
| Criterion | Code review of every fault path; fault injection is planned, not executed. |

### SWR-031 Bounded, non-blocking input path
The UART interrupt shall never block. Received bytes and frames shall pass
through bounded ThreadX queues, and overflows shall be counted, not waited on.

| Attribute | Value |
| --- | --- |
| Type | Robustness |
| Derived from | SYS-03, SYS-04 |
| Verification | IT, RV |
| Criterion | No losses during the 256-frame burst; ISR review shows `TX_NO_WAIT` only. |

## Performance and resource requirements

### SWR-040 Serial round-trip time
The 95th percentile time from sending a `0x1F1` line to receiving the `0x1F4`
line at the host serial port shall be ≤ 20 ms.

| Attribute | Value |
| --- | --- |
| Type | Performance |
| Derived from | SYS-06 |
| Verification | IT |
| Criterion | p95 over 256 frames ≤ 20 ms. |

### SWR-041 End-to-end lamp latency
In X-Verse, the time from the VCU's status publication to the matching CARLA
lamp state shall be ≤ 100 ms.

| Attribute | Value |
| --- | --- |
| Type | Performance |
| Derived from | SYS-06 |
| Verification | QT |
| Criterion | Every qualification step ≤ 100 ms. |

### SWR-042 Resource budget
The firmware shall use at most 64 KiB of flash and 32 KiB of static RAM.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-05 |
| Verification | AN |
| Criterion | `arm-none-eabi-size` of the release ELF within budget. |

## Integration and platform requirements

### SWR-050 X-Verse interoperability
The software shall interoperate with the unmodified Zenoh2CAN bridge through
python-can's `slcan` interface. The bridge maps the frames to the X-Verse
topics `vcu/control/*` and `vehicle/lights/*`.

| Attribute | Value |
| --- | --- |
| Type | Interface |
| Derived from | SYS-02 |
| Verification | IT, QT |
| Criterion | Four lamp states round-trip through Zenoh and reach the CARLA actor. |

### SWR-060 RTOS platform
The software shall use Eclipse ThreadX at revision
`b91b03b9e75fa523b17127f9e0eca09dca916459` with the unmodified `cortex_m4/gnu` port.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-05 |
| Verification | AN |
| Criterion | Build pins the revision and refuses modified sources. |

### SWR-061 Shared protocol implementation
The software shall use the same `lights_protocol.c` as the Linux zonal
controller, without modification.

| Attribute | Value |
| --- | --- |
| Type | Constraint |
| Derived from | SYS-02 |
| Verification | AN |
| Criterion | SHA-256 equals the hash recorded in the Linux controller's evidence. |
