/* SPDX-License-Identifier: Apache-2.0 */
#include "slcan.h"
#include <string.h>

static int hex_value(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

static bool parse_hex(const char *text, size_t digits, unsigned long *value)
{
    *value = 0;
    for (size_t index = 0; index < digits; ++index) {
        int nibble = hex_value(text[index]);
        if (nibble < 0) return false;
        *value = (*value << 4) | (unsigned long)nibble;
    }
    return true;
}

static bool parse_frame(const char *line, size_t length, struct can_frame *frame)
{
    const bool extended = line[0] == 'T' || line[0] == 'R';
    const bool remote = line[0] == 'r' || line[0] == 'R';
    const size_t id_digits = extended ? 8U : 3U;
    unsigned long id, dlc;
    if (length < 1U + id_digits + 1U ||
        !parse_hex(line + 1, id_digits, &id) || !parse_hex(line + 1 + id_digits, 1, &dlc) ||
        dlc > CAN_MAX_DLEN || id > (extended ? CAN_EFF_MASK : CAN_SFF_MASK))
        return false;
    const size_t header = 1U + id_digits + 1U;
    if (length != header + (remote ? 0U : dlc * 2U)) return false;
    memset(frame, 0, sizeof(*frame));
    frame->can_id = (canid_t)id | (extended ? CAN_EFF_FLAG : 0U) | (remote ? CAN_RTR_FLAG : 0U);
    frame->can_dlc = (unsigned char)dlc;
    for (size_t index = 0; !remote && index < dlc; ++index) {
        unsigned long byte;
        if (!parse_hex(line + header + index * 2U, 2, &byte)) return false;
        frame->data[index] = (unsigned char)byte;
    }
    return true;
}

bool slcan_parse(const char *line, size_t length, struct slcan_command *command)
{
    memset(command, 0, sizeof(*command));
    command->kind = SLCAN_INVALID;
    if (length == 0) return false;
    unsigned long value;
    switch (line[0]) {
    case 't': case 'T': case 'r': case 'R':
        if (!parse_frame(line, length, &command->frame)) return false;
        command->kind = SLCAN_FRAME;
        return true;
    case 'O': command->kind = SLCAN_OPEN; return length == 1;
    case 'C': command->kind = SLCAN_CLOSE; return length == 1;
    case 'V': command->kind = SLCAN_VERSION; return length == 1;
    case 'N': command->kind = SLCAN_SERIAL; return length == 1;
    case 'F': command->kind = SLCAN_STATUS; return length == 1;
    case 'S':
        if (length != 2 || line[1] < '0' || line[1] > '8') return false;
        command->kind = SLCAN_BITRATE;
        command->argument = (unsigned)(line[1] - '0');
        return true;
    case 's':
        if (length != 5 || !parse_hex(line + 1, 4, &value)) return false;
        command->kind = SLCAN_BITRATE;
        command->argument = (unsigned)value;
        return true;
    case 'Z':
        if (length != 2 || line[1] != '0') return false;
        command->kind = SLCAN_TIMESTAMP;
        return true;
    default:
        return false;
    }
}

size_t slcan_format(const struct can_frame *frame, char *line, size_t capacity)
{
    static const char digits[] = "0123456789ABCDEF";
    const bool extended = (frame->can_id & CAN_EFF_FLAG) != 0U;
    const bool remote = (frame->can_id & CAN_RTR_FLAG) != 0U;
    const canid_t id = frame->can_id & (extended ? CAN_EFF_MASK : CAN_SFF_MASK);
    const size_t id_digits = extended ? 8U : 3U;
    const size_t length = 1U + id_digits + 1U + (remote ? 0U : frame->can_dlc * 2U) + 1U;
    if ((frame->can_id & CAN_ERR_FLAG) || frame->can_dlc > CAN_MAX_DLEN ||
        (frame->can_id & ~(CAN_EFF_FLAG | CAN_RTR_FLAG)) != id || length > capacity)
        return 0;
    size_t out = 0;
    line[out++] = remote ? (extended ? 'R' : 'r') : (extended ? 'T' : 't');
    for (size_t shift = id_digits; shift-- > 0;) line[out++] = digits[(id >> (shift * 4U)) & 0xFU];
    line[out++] = digits[frame->can_dlc];
    for (size_t index = 0; !remote && index < frame->can_dlc; ++index) {
        line[out++] = digits[frame->data[index] >> 4U];
        line[out++] = digits[frame->data[index] & 0xFU];
    }
    line[out++] = '\r';
    return out;
}
