/* SPDX-License-Identifier: Apache-2.0 */
#ifndef ZONAL_TX_USER_H
#define ZONAL_TX_USER_H
/* Same 10 ms tick as the Linux controller (../src/tx_user.h). */
#define TX_TIMER_TICKS_PER_SECOND 100
/* Fail fast on stack overflow instead of corrupting another thread. */
#define TX_ENABLE_STACK_CHECKING
#endif
