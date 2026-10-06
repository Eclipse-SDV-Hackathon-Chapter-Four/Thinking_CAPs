/* SPDX-License-Identifier: Apache-2.0 */
#ifndef ZONAL_LIGHTS_PROTOCOL_H
#define ZONAL_LIGHTS_PROTOCOL_H
#include <linux/can.h>
#include <stdbool.h>
#define VCU_STATUS_ID 0x1F1U
#define BCM_LIGHTS_ID 0x1F4U

/* Classic standard CAN, DLC 8. Reverse input bit 1, brake input bit 2;
 * reverse output bit 0, brake output bit 1. Other output bytes are zero. */
bool lights_decode(const struct can_frame *input, struct can_frame *output);
void lights_off(struct can_frame *output);
#endif
