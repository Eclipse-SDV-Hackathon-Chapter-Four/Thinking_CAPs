# Software architectural design (SWE.2)

The architecture is described by PlantUML views in [diagrams/](diagrams/):

| View | File | Purpose |
| --- | --- | --- |
| Context | [context.puml](diagrams/context.puml) | ECU in the X-Verse data flow |
| Deployment | [deployment.puml](diagrams/deployment.puml) | Host, ST-LINK, MCU peripherals |
| Static | [components.puml](diagrams/components.puml) | Layered components and interfaces |
| Dynamic | [tasks.puml](diagrams/tasks.puml) | ThreadX threads, priorities, queues, mutexes, timer |
| Dynamic | [sequence.puml](diagrams/sequence.puml) | Frame flow from VCU status to light command |
| Behaviour | [link-state.puml](diagrams/link-state.puml) | Link and lamp state machine, fault state |

## Design decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| AD-01 | Simulate CAN with Lawicell SLCAN over the ST-LINK UART | The board has no CAN transceiver. SLCAN is supported by python-can and Linux `slcand`, so the X-Verse bridge stays unmodified (SWR-050). |
| AD-02 | Reuse the Linux `lights_protocol.c` unchanged; supply `<linux/can.h>` through a freestanding compat header | A single implementation of the CAN contract on both targets (SWR-061). |
| AD-03 | Three threads with fixed priorities: control 10 > ingress 11 > display 20 | Lamp decisions pre-empt parsing; the display can never delay lamps or communication (SWR-023). |
| AD-04 | ISR → bounded queue → thread; no blocking in interrupt context | Deterministic interrupt latency; overflows are counted (SWR-031, SWR-021). |
| AD-05 | Interrupt-driven TX ring with whole-line writes under a priority-inheritance mutex | Lines never interleave, and threads do not busy-wait on the UART. |
| AD-06 | Fail-safe on link close and on any fault: lamps off | Safe state for SYS-03 (SWR-009, SWR-030). |
| AD-07 | Register-level board support, no vendor HAL | Smallest dependency surface; the only fetched dependency is ThreadX (SWR-060). |
| AD-08 | Internal HSI oscillator (±1%) | The external HSE did not start the system and no debugger was available; ±1% is within UART and heartbeat tolerances. |

## Software elements

The report generator parses this table: ID | Element | Responsibility | Satisfies.

| ID | Element | Responsibility | Satisfies |
| --- | --- | --- | --- |
| ARC-01 | Startup and vectors (`startup.c`, `az3166.ld`) | Reset entry, `.data`/`.bss` init, vector table, memory map | SWR-007, SWR-030, SWR-042 |
| ARC-02 | Eclipse ThreadX kernel and port init (`tx_initialize_low_level.S`) | Scheduler, 100 Hz SysTick, queues, mutexes, timers, stack checking | SWR-020, SWR-031, SWR-060 |
| ARC-03 | Board support (`board.c`) | 96 MHz clock, lamp outputs, status LEDs, fault indication | SWR-004, SWR-022, SWR-030 |
| ARC-04 | USART6 driver (`board.c`) | 115200 8N1, RX interrupt callback, TX ring, overrun counting | SWR-010, SWR-021, SWR-031 |
| ARC-05 | OLED driver (`board.c` I2C, `display.c`) | SSD1306 on I2C1, text rendering, fail-stop on I2C error | SWR-023 |
| ARC-06 | SLCAN codec (`slcan.c`) | Parse Lawicell lines; encode frames | SWR-011, SWR-013, SWR-014 |
| ARC-07 | Lights protocol (`lights_protocol.c`, shared) | Decode `0x1F1`, encode `0x1F4`, reject non-conforming frames | SWR-001, SWR-002, SWR-003, SWR-061 |
| ARC-08 | SLCAN ingress thread (`main.c`) | Line assembly, command handling, acknowledgements, link state, frame filtering | SWR-003, SWR-008, SWR-009, SWR-011, SWR-012, SWR-013, SWR-050 |
| ARC-09 | Lighting control thread (`main.c`) | Apply lamps, publish `0x1F4`, hold/timeout, heartbeat `0x1F5`, fail-safe on close | SWR-001, SWR-002, SWR-004, SWR-005, SWR-006, SWR-007, SWR-009, SWR-020, SWR-021, SWR-040, SWR-041 |
| ARC-10 | Status display thread (`main.c`) | Render the status snapshot to the OLED on change and every second | SWR-023 |
| ARC-11 | Fault handling (`main.c`, `board.c`, `startup.c`) | Map ThreadX errors, stack overflow, CPU faults and unexpected IRQs to the safe state | SWR-030 |

## Interfaces

| ID | Interface | Provider → consumer | Type and contract |
| --- | --- | --- | --- |
| IF-01 | SLCAN over UART | Host ↔ ARC-04 | External. 115200 8N1, CR-terminated Lawicell lines ([transport contract](../../docs/uart-can-transport.md)) |
| IF-02 | `rx_byte_queue` | ARC-04 ISR → ARC-08 | ThreadX queue, 256 × 1 word, `TX_NO_WAIT` producer |
| IF-03 | `frame_queue` | ARC-08 → ARC-09 | ThreadX queue, 32 × `struct can_frame`, `TX_NO_WAIT` producer, 1-tick consumer |
| IF-04 | `uart_send()` | ARC-08, ARC-09 → ARC-04 | Whole line under `uart_lock`; drops after 0.5 s backpressure (counted) |
| IF-05 | `board_lamps()`, LED functions | ARC-09 → ARC-03 | GPIO BSRR writes, atomic per pin |
| IF-06 | `events`, `display_events` | ARC-02 timer, ARC-08 → ARC-09 → ARC-10 | ThreadX event flags: HEARTBEAT, LINK, REDRAW |
| IF-07 | `display_*()` | ARC-10 → ARC-05 | Clear, text, flush; returns false after the first I2C failure |
| IF-08 | Zenoh topics | Bridge ↔ X-Verse | `vcu/control/{brake,reverse,cc_engage}_sts`, `vcu/control/status` → `0x1F1`; `0x1F4` → `vehicle/lights/{brake,reverse}_lights_cmd`, `vehicle/lights/frame` |

## Resource allocation

| Resource | Allocation | Budget |
| --- | --- | --- |
| Flash | ≈ 16.5 KB (`.text` + `.rodata` + vectors) | 64 KiB (SWR-042) |
| Static RAM | ≈ 16 KB: 3 × 2 KiB thread stacks, 4 KiB main/ISR stack, queues 1.5 KiB, TX ring 1 KiB, OLED frame 1 KiB | 32 KiB (SWR-042) |
| CPU | Dominated by UART at 115200 baud (≤ 11.5 kB/s); ThreadX tick 10 ms | — |
| Interrupt priorities | SysTick 0x40, USART6 0x80, PendSV 0xFF | — |
