/* SPDX-License-Identifier: Apache-2.0 */
/* Register-level MXChip AZ3166 board support (no vendor HAL). */
#ifndef ZONAL_BOARD_H
#define ZONAL_BOARD_H
#include <stdbool.h>
#include <stddef.h>

#define BOARD_UART_BAUD 115200U  /* USART6 on PA11/PA12 = ST-LINK virtual COM port */

/* 96 MHz system clock from the internal HSI RC, GPIO, LEDs off, USART6 configured. */
void board_init(void);

/* Physical lamps: brake -> RGB LED red, reverse -> user LED. */
void board_lamps(bool reverse, bool brake);
/* Azure LED: X-Verse link (SLCAN channel open). Wi-Fi LED: ThreadX heartbeat. */
void board_link_led(bool on);
void board_heartbeat_led(bool on);
/* RGB LED blue, everything else off, interrupts off; never returns. */
void board_fault(void) __attribute__((noreturn));

/* Starts USART6 receive interrupts; on_byte runs in interrupt context. */
void board_uart_start(void (*on_byte)(unsigned char byte));
/* Queues a complete line for interrupt-driven transmission. All or nothing:
 * returns false without queuing anything if the TX ring lacks space. */
bool board_uart_write(const char *data, size_t length);
/* Hardware receive overruns (bytes lost before the ISR could read them). */
unsigned long board_uart_overruns(void);

/* SSD1306 128x64 OLED on I2C1 (PB8/PB9). Calls fail fast on I2C errors. */
bool board_oled_init(void);
bool board_oled_page(unsigned page, const unsigned char columns[128]);
#endif
