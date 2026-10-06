# Software detailed design (SWE.3)

The software units are C source files, or cohesive parts of them, allocated to
the architecture elements in [SWE.2](../swe2-architecture/architecture.md).
Activity diagrams in [diagrams/](diagrams/) show the units with non-trivial
control flow. Each function has a single responsibility and a header contract
in `board.h`, `display.h`, `slcan.h` and `lights_protocol.h`.

## Software units

The report generator parses this table: ID | Unit | Source / functions | Element | Implements.

| ID | Unit | Source / functions | Element | Implements |
| --- | --- | --- | --- | --- |
| DD-01 | Startup | `startup.c`: `Reset_Handler`, `vector_table`, `fault_handler`; `az3166.ld` | ARC-01 | SWR-007, SWR-030, SWR-042 |
| DD-02 | ThreadX port init | `tx_initialize_low_level.S`: `_tx_initialize_low_level`, `SysTick_Handler`; `tx_user.h` | ARC-02 | SWR-020, SWR-060 |
| DD-03 | Board support | `board.c`: `clock_init`, `board_init`, `pin_mode`, `pin_write`, `board_lamps`, `board_link_led`, `board_heartbeat_led`, `board_fault` | ARC-03, ARC-11 | SWR-004, SWR-022, SWR-030 |
| DD-04 | USART6 driver | `board.c`: `board_uart_start`, `board_uart_write`, `board_uart_overruns`, `USART6_IRQHandler` | ARC-04 | SWR-010, SWR-021, SWR-031, SWR-040 |
| DD-05 | OLED driver | `board.c`: `i2c_wait`, `i2c_write`, `board_oled_init`, `board_oled_page`; `display.c`; `font7x10.c` (MIT) | ARC-05 | SWR-023 |
| DD-06 | SLCAN codec | `slcan.c`: `hex_value`, `parse_hex`, `parse_frame`, `slcan_parse`, `slcan_format` | ARC-06 | SWR-011, SWR-013, SWR-014 |
| DD-07 | Lights protocol | `../src/lights_protocol.c`: `lights_decode`, `lights_off` | ARC-07 | SWR-001, SWR-002, SWR-003, SWR-007, SWR-061 |
| DD-08 | SLCAN ingress | `main.c`: `on_uart_byte`, `ingress_entry`, `handle_line`, `set_link`, `reply`, `uart_send` | ARC-08 | SWR-008, SWR-009, SWR-011, SWR-012, SWR-013, SWR-031, SWR-040, SWR-050 |
| DD-09 | Lighting control | `main.c`: `control_entry`, `apply`, `publish`, `heartbeat` | ARC-09 | SWR-001, SWR-002, SWR-004, SWR-005, SWR-006, SWR-009, SWR-020, SWR-021, SWR-040, SWR-041 |
| DD-10 | Status display | `main.c`: `display_entry`, `append`, `append_number` | ARC-10 | SWR-023 |
| DD-11 | Resource creation and fault mapping | `main.c`: `tx_application_define`, `require_tx`, `stack_error`, `main` | ARC-02, ARC-11 | SWR-030, SWR-031 |

## Unit design notes

**DD-06 SLCAN codec.** Pure functions with no global state, so they can be
unit-tested on the host. `slcan_parse` validates the exact line length per
frame kind, the hex digits, DLC ≤ 8 and the identifier range (11 or 29 bits).
`slcan_format` refuses error frames, DLC > 8, identifiers outside their range
and insufficient buffer capacity, and returns 0 when it refuses.

**DD-07 Lights protocol.** Shared with the Linux controller. `lights_decode`
rejects any `can_id` other than exactly `0x1F1`. Because the comparison
includes the flag bits, extended, RTR and error frames are rejected too. It
also rejects any DLC other than 8. On success it writes a zeroed `0x1F4` frame
with `data[0] = (status >> 1) & 3`.

**DD-08 Ingress** ([handle-line.puml](diagrams/handle-line.puml)):

- assembles at most 26 characters per line; longer lines are marked overlong
- answers every line exactly once
- replies before enqueuing, so the acknowledgement always precedes the
  resulting light command
- uses only `TX_NO_WAIT` producers

**DD-09 Control** ([control-loop.puml](diagrams/control-loop.puml)):

- polls the frame queue with a 1-tick timeout, so timeout and heartbeat events
  are serviced every 10 ms
- ignores frames when the link is closed, which avoids actuation after a close
  races with queued frames

**DD-04 UART** ([uart-driver.puml](diagrams/uart-driver.puml)):

- the TX ring is single-producer (under `uart_lock`), single-consumer (ISR)
- the TXEIE update runs with interrupts masked
- the ISR's RX callback never blocks

**DD-11 Faults.**

- Every ThreadX service result goes through `require_tx`, which calls
  `board_fault` on any error.
- `tx_thread_stack_error_notify` routes stack overflows (`TX_ENABLE_STACK_CHECKING`) to `board_fault`.
- All unused vectors and the core fault vectors point to `fault_handler`.

## Coding guidelines and static verification

See [coding-guidelines.md](coding-guidelines.md). The report records the
compiler, cppcheck, MISRA (informative) and complexity results, together with
the justified deviations.
