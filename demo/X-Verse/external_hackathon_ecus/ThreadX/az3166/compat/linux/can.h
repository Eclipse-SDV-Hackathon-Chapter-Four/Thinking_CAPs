/* SPDX-License-Identifier: Apache-2.0 */
/* Freestanding subset of <linux/can.h> for the AZ3166 build. It lets the MCU
 * firmware compile the unchanged ../src/lights_protocol.c used by the Linux
 * controller, so both targets share one implementation of the CAN contract. */
#ifndef ZONAL_COMPAT_LINUX_CAN_H
#define ZONAL_COMPAT_LINUX_CAN_H
#include <stdint.h>

#define CAN_EFF_FLAG 0x80000000U
#define CAN_RTR_FLAG 0x40000000U
#define CAN_ERR_FLAG 0x20000000U
#define CAN_SFF_MASK 0x000007FFU
#define CAN_EFF_MASK 0x1FFFFFFFU
#define CAN_MAX_DLEN 8

typedef uint32_t canid_t;

struct can_frame {
    canid_t can_id;  /* 11/29-bit identifier plus EFF/RTR/ERR flags */
    uint8_t can_dlc; /* 0..8 */
    uint8_t pad, res0, res1;
    uint8_t data[CAN_MAX_DLEN] __attribute__((aligned(8)));
};
#endif
