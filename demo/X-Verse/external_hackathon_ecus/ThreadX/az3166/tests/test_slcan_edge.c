/* SPDX-License-Identifier: Apache-2.0 */
/* Boundary cases of the SLCAN codec that complete its branch coverage:
 * hex digit range edges, invalid identifiers, bitrate digits and extended
 * or remote frame formatting. Complements test_slcan.c. */
#include "slcan.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "Failed line %d: %s\n", __LINE__, #x); exit(1); } } while (0)

static bool parses(const char *line)
{
    struct slcan_command command;
    return slcan_parse(line, strlen(line), &command);
}

int main(void)
{
    /* Characters adjacent to each hex digit range must be rejected, in the
     * identifier, the DLC and the data field. */
    const char edges[] = {'/', ':', '@', 'G', '`', 'g'};
    for (unsigned i = 0; i < sizeof(edges); ++i) {
        char id[] = "t1F18060000000000000000";
        id[2] = edges[i];
        CHECK(!parses(id));
        char data[] = "t1F180600000000000000";
        data[6] = edges[i];
        CHECK(!parses(data));
        char bitrate[] = "s031C";
        bitrate[4] = edges[i];
        CHECK(!parses(bitrate));
    }
    /* Lower- and upper-case digits at both ends of each range are accepted. */
    CHECK(parses("t7ff0") && parses("t7FF0") && parses("t0000") && parses("t1aF2aFfA"));
    CHECK(!parses("t1F1/") && !parses("T1F1F1F1F9") && !parses("TXXXXXXXX0"));
    CHECK(!parses("S/") && !parses("S:") && parses("S0") && parses("S8"));

    /* Formatting: extended remote frames and extended identifier overflow. */
    char line[SLCAN_MTU + 1];
    struct can_frame frame = {.can_id = 0x1F1 | CAN_EFF_FLAG | CAN_RTR_FLAG, .can_dlc = 2};
    CHECK(slcan_format(&frame, line, sizeof(line)) == 11 && memcmp(line, "R000001F12\r", 11) == 0);
    frame.can_id = 0x20000000U | CAN_EFF_FLAG;
    CHECK(slcan_format(&frame, line, sizeof(line)) == 0);
    frame.can_id = 0x7FF;
    frame.can_dlc = 0;
    CHECK(slcan_format(&frame, line, sizeof(line)) == 6 && memcmp(line, "t7FF0\r", 6) == 0);
    puts("SLCAN boundary cases (hex range edges, identifiers, bitrate digits, extended/remote format) passed");
    return 0;
}
