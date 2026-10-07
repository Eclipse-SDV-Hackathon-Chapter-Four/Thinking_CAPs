# Coding guidelines (SWE.3 / SWE.4 static verification)

| ID | Rule | Check |
| --- | --- | --- |
| CG-01 | C11 (GNU extensions allowed for attributes and `typeof`), no dynamic memory, no recursion | Review; the link map has no heap users |
| CG-02 | Compile warning-free with `-Wall -Wextra -Werror` on GCC (target arm-none-eabi 10.3, host 11.4) | Build |
| CG-03 | No cppcheck findings of severity *error*, *warning*, *style*, *performance* or *portability* without a justified deviation | cppcheck 2.7 |
| CG-04 | Cyclomatic complexity ≤ 15 per function; up to 25 for flat dispatch `switch` or parser functions, with justification | lizard |
| CG-05 | Interrupt handlers never block; ThreadX calls from ISRs use `TX_NO_WAIT` | Review |
| CG-06 | Every ThreadX service result is checked (`require_tx`) or explicitly counted | Review |
| CG-07 | Fixed-size buffers carry explicit bounds; all array indexing is bounded by constants | Review, cppcheck |
| CG-08 | MISRA C:2012 is tracked as an informative baseline; compliance is not claimed | cppcheck MISRA addon |

## Justified deviations

The report generator matches these IDs against the analysis findings.

| ID | Tool / rule | Location | Justification |
| --- | --- | --- | --- |
| DEV-01 | cppcheck `comparePointers` | `startup.c` `Reset_Handler` | `.data`/`.bss` sizes are computed from linker-defined symbols that delimit one region. This is the standard Cortex-M start-up idiom, and the linker script guarantees the ordering. |
| DEV-02 | cppcheck `unsignedPositive` | `main.c` `control_entry` timeout check | False positive. With the default `ZONAL_TIMEOUT_MS=0`, the comparison is never evaluated because `timeout_ticks &&` guards it. With a non-zero timeout the expression is meaningful (unsigned tick wrap-around is intended). |
| DEV-03 | lizard CCN > 15 | `slcan.c` `slcan_parse` (22), `parse_frame` (17), `main.c` `handle_line` (18), `control_entry` (17) | Flat command dispatch and frame validation; each branch is a single protocol case. `slcan.c` is covered at 100% branch level by unit tests. `handle_line` and `control_entry` are covered by the integration tests. |
| DEV-04 | MISRA 11.4 (integer-to-pointer casts) | `board.c` `REG()` | Memory-mapped register access on a fixed MCU memory map. |
