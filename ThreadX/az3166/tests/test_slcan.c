/* SPDX-License-Identifier: Apache-2.0 */
#include "slcan.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "Failed line %d: %s\n", __LINE__, #x); exit(1); } } while (0)

static struct slcan_command parse(const char *line, bool expected)
{
    struct slcan_command command;
    CHECK(slcan_parse(line, strlen(line), &command) == expected);
    return command;
}

int main(void)
{
    /* Every VCU status byte survives format -> parse unchanged. */
    for (unsigned byte = 0; byte < 256; ++byte) {
        struct can_frame frame = {.can_id = 0x1F1, .can_dlc = 8, .data = {(unsigned char)byte, 0xA5}};
        char line[SLCAN_MTU + 1];
        size_t length = slcan_format(&frame, line, sizeof(line));
        CHECK(length == 22 && line[length - 1] == '\r');
        struct slcan_command command;
        CHECK(slcan_parse(line, length - 1, &command) && command.kind == SLCAN_FRAME);
        CHECK(memcmp(&command.frame, &frame, sizeof(frame)) == 0);
    }
    char line[SLCAN_MTU + 1];
    struct can_frame lights = {.can_id = 0x1F4, .can_dlc = 8, .data = {3}};
    CHECK(slcan_format(&lights, line, sizeof(line)) == 22);
    CHECK(memcmp(line, "t1F480300000000000000\r", 22) == 0);
    struct can_frame extended = {.can_id = 0x1ABCDEF0 | CAN_EFF_FLAG, .can_dlc = 8,
        .data = {1, 2, 3, 4, 5, 6, 7, 0xFF}};
    CHECK(slcan_format(&extended, line, sizeof(line)) == SLCAN_MTU);
    CHECK(memcmp(line, "T1ABCDEF0801020304050607FF\r", SLCAN_MTU) == 0);
    struct can_frame remote = {.can_id = 0x123 | CAN_RTR_FLAG, .can_dlc = 4};
    CHECK(slcan_format(&remote, line, sizeof(line)) == 6 && memcmp(line, "r1234\r", 6) == 0);
    CHECK(slcan_format(&lights, line, 21) == 0);
    struct can_frame invalid = {.can_id = 0x800, .can_dlc = 8};
    CHECK(slcan_format(&invalid, line, sizeof(line)) == 0);
    invalid.can_id = 0x1F1 | CAN_ERR_FLAG;
    CHECK(slcan_format(&invalid, line, sizeof(line)) == 0);
    invalid.can_id = 0x1F1;
    invalid.can_dlc = 9;
    CHECK(slcan_format(&invalid, line, sizeof(line)) == 0);

    struct slcan_command command = parse("t1F1806ffffffffffffff", true);
    CHECK(command.frame.can_id == 0x1F1 && command.frame.can_dlc == 8 && command.frame.data[0] == 6);
    command = parse("T1FFFFFFF0", true);
    CHECK(command.frame.can_id == (0x1FFFFFFF | CAN_EFF_FLAG) && command.frame.can_dlc == 0);
    command = parse("R000001F18", true);
    CHECK(command.frame.can_id == (0x1F1 | CAN_EFF_FLAG | CAN_RTR_FLAG) && command.frame.can_dlc == 8);
    command = parse("r1F18", true);
    CHECK(command.frame.can_id == (0x1F1 | CAN_RTR_FLAG));
    CHECK(parse("O", true).kind == SLCAN_OPEN && parse("C", true).kind == SLCAN_CLOSE);
    CHECK(parse("V", true).kind == SLCAN_VERSION && parse("N", true).kind == SLCAN_SERIAL);
    CHECK(parse("F", true).kind == SLCAN_STATUS && parse("Z0", true).kind == SLCAN_TIMESTAMP);
    command = parse("S6", true);
    CHECK(command.kind == SLCAN_BITRATE && command.argument == 6);
    command = parse("s031C", true);
    CHECK(command.kind == SLCAN_BITRATE && command.argument == 0x031C);

    const char *malformed[] = {"", "t1F1", "t1F18", "t1F18060000000000000", "t1F1806000000000000000",
        "t8001", "t1F19", "t1F1G", "t1F18060000000000000G", "T200000000", "T1F1806", "r1F1800",
        "O1", "C0", "S9", "S", "s31C", "sXXXX", "Z1", "Z", "x", "L", "\r"};
    for (unsigned i = 0; i < sizeof(malformed) / sizeof(malformed[0]); ++i) parse(malformed[i], false);
    puts("SLCAN round trip for 256 status bytes, ext/RTR frames, commands and 23 malformed lines passed");
    return 0;
}
