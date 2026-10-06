/* SPDX-License-Identifier: MIT */
/* Low-level ThreadX initialization for the AZ3166 (STM32F412, 96 MHz core).
 * Adapted from Eclipse ThreadX ports/cortex_m4/gnu/example_build/
 * tx_initialize_low_level.S (MIT, Copyright (c) 2024 Microsoft Corporation
 * and Eclipse ThreadX contributors). The vector table lives in startup.c. */
#include "board_clock.h"

    .global     _tx_thread_system_stack_ptr
    .global     _tx_initialize_unused_memory
    .global     __RAM_segment_used_end__
    .global     _tx_timer_interrupt
    .global     _vectors

SYSTICK_CYCLES = ((BOARD_SYSCLK_HZ / TX_TIMER_TICKS_PER_SECOND) - 1)

    .text 32
    .align 4
    .syntax unified

    .global  _tx_initialize_low_level
    .thumb_func
_tx_initialize_low_level:
    CPSID   i                                       @ Interrupts stay off until the scheduler starts

    LDR     r0, =_tx_initialize_unused_memory       @ First free RAM after static data and main stack
    LDR     r1, =__RAM_segment_used_end__
    ADD     r1, r1, #4
    STR     r1, [r0]

    MOV     r0, #0xE000E000                         @ SCB->VTOR = _vectors
    LDR     r1, =_vectors
    STR     r1, [r0, #0xD08]

    LDR     r0, =_tx_thread_system_stack_ptr        @ ISR stack is the reset main stack
    LDR     r1, =_vectors
    LDR     r1, [r1]
    STR     r1, [r0]

    LDR     r0, =0xE0001000                         @ Enable DWT cycle counter
    LDR     r1, [r0]
    ORR     r1, r1, #1
    STR     r1, [r0]

    MOV     r0, #0xE000E000                         @ SysTick at TX_TIMER_TICKS_PER_SECOND
    LDR     r1, =SYSTICK_CYCLES
    STR     r1, [r0, #0x14]
    MOV     r1, #0x7                                @ Core clock, interrupt, enable
    STR     r1, [r0, #0x10]

    LDR     r1, =0x00000000                         @ Rsrv, UsgF, BusF, MemM
    STR     r1, [r0, #0xD18]
    LDR     r1, =0xFF000000                         @ SVCl, Rsrv, Rsrv, Rsrv
    STR     r1, [r0, #0xD1C]
    LDR     r1, =0x40FF0000                         @ SysT, PnSV, Rsrv, DbgM
    STR     r1, [r0, #0xD20]
    BX      lr

    .global  SysTick_Handler
    .thumb_func
SysTick_Handler:
    PUSH    {r0, lr}
    BL      _tx_timer_interrupt
    POP     {r0, lr}
    BX      lr
