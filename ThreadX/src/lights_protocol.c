/* SPDX-License-Identifier: Apache-2.0 */
#include "lights_protocol.h"
#include <string.h>

void lights_off(struct can_frame *output)
{
    memset(output, 0, sizeof(*output));
    output->can_id = BCM_LIGHTS_ID;
    output->can_dlc = CAN_MAX_DLEN;
}

bool lights_decode(const struct can_frame *input, struct can_frame *output)
{
    if (input->can_id != VCU_STATUS_ID || input->can_dlc != CAN_MAX_DLEN)
        return false;  /* Also rejects RTR, error and extended-ID flags. */
    lights_off(output);
    output->data[0] = (input->data[0] >> 1U) & 0x03U;
    return true;
}
