/* SPDX-License-Identifier: Apache-2.0 */
#include "lights_protocol.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "Failed line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
int main(void)
{
    struct can_frame input = {.can_id = VCU_STATUS_ID, .can_dlc = 8}, output;
    /* Exhaust all status bits, including irrelevant engagement/reserved bits. */
    for (unsigned byte = 0; byte < 256; ++byte) {
        memset(input.data, 0xFF, sizeof(input.data));
        input.data[0] = byte;
        CHECK(lights_decode(&input, &output));
        CHECK(output.can_id == BCM_LIGHTS_ID && output.can_dlc == 8);
        CHECK(output.data[0] == ((byte >> 1) & 3));
        for (unsigned index = 1; index < 8; ++index) CHECK(output.data[index] == 0);
    }
    for (unsigned dlc = 0; dlc < 16; ++dlc) {
        input.can_dlc = dlc;
        CHECK(lights_decode(&input, &output) == (dlc == 8));
    }
    input.can_dlc = 8;
    const canid_t rejected[] = {0x1F0, 0x1F2, BCM_LIGHTS_ID,
        VCU_STATUS_ID | CAN_EFF_FLAG, VCU_STATUS_ID | CAN_RTR_FLAG, VCU_STATUS_ID | CAN_ERR_FLAG};
    for (unsigned i = 0; i < sizeof(rejected)/sizeof(rejected[0]); ++i) {
        input.can_id = rejected[i];
        memset(&output, 0xAA, sizeof(output));
        struct can_frame before = output;
        CHECK(!lights_decode(&input, &output));
        CHECK(memcmp(&before, &output, sizeof(output)) == 0);
    }
    lights_off(&output);
    CHECK(output.can_id == BCM_LIGHTS_ID && output.can_dlc == 8);
    for (unsigned i = 0; i < 8; ++i) CHECK(output.data[i] == 0);
    puts("All 256 status combinations, DLC/ID rejection and lights-off checks passed");
    return 0;
}
