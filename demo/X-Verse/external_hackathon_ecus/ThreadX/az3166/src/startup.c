/* SPDX-License-Identifier: Apache-2.0 */
/* STM32F412 reset entry and vector table (16 core exceptions + 97 IRQs). */
#include "board.h"
#include <stdint.h>
#include <string.h>

extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss, _estack;
extern int main(void);
void __tx_PendSVHandler(void);
void SysTick_Handler(void);
void USART6_IRQHandler(void);

void Reset_Handler(void)
{
    memcpy(&_sdata, &_sidata, (size_t)((char *)&_edata - (char *)&_sdata));
    memset(&_sbss, 0, (size_t)((char *)&_ebss - (char *)&_sbss));
    main();
    board_fault();
}

/* Faults and unexpected interrupts stop with the RGB LED blue. */
static void fault_handler(void) { board_fault(); }

#define IRQ_COUNT 97
#define USART6_IRQN 71

typedef void (*vector_t)(void);
/* ThreadX Cortex-M ports never use SVC; an SVC is unexpected. */
__attribute__((section(".isr_vector"), used))
const vector_t vector_table[16 + IRQ_COUNT] = {
    [0] = (vector_t)&_estack,
    [1] = Reset_Handler,
    [2 ... 6] = fault_handler,   /* NMI, HardFault, MemManage, BusFault, UsageFault */
    [11 ... 12] = fault_handler, /* SVC, DebugMon */
    [14] = __tx_PendSVHandler,
    [15] = SysTick_Handler,
    [16 ... 16 + USART6_IRQN - 1] = fault_handler,
    [16 + USART6_IRQN] = USART6_IRQHandler,
    [16 + USART6_IRQN + 1 ... 16 + IRQ_COUNT - 1] = fault_handler,
};
