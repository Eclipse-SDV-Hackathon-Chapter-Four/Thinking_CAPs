/* SPDX-License-Identifier: Apache-2.0 */
/* Clock constants shared by C and the ThreadX low-level assembly. */
#ifndef ZONAL_BOARD_CLOCK_H
#define ZONAL_BOARD_CLOCK_H
#include "tx_user.h"
#define BOARD_SYSCLK_HZ 96000000  /* PLL from the 16 MHz HSI RC */
#define BOARD_APB1_HZ   48000000
#define BOARD_APB2_HZ   96000000
#endif
