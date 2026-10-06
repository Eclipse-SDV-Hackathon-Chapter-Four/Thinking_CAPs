/* SPDX-License-Identifier: Apache-2.0 */
#ifndef ZONAL_SLCAN_H
#define ZONAL_SLCAN_H
#include <linux/can.h>
#include <stdbool.h>
#include <stddef.h>

/* Lawicell SLCAN ASCII protocol: one command per line, terminated by '\r'.
 * The longest line is an extended data frame: T + 8 id + 1 dlc + 16 data. */
#define SLCAN_MTU 27U

enum slcan_kind {
    SLCAN_INVALID,
    SLCAN_FRAME,     /* t/T/r/R: frame from host to the simulated bus */
    SLCAN_OPEN,      /* O */
    SLCAN_CLOSE,     /* C */
    SLCAN_BITRATE,   /* Sn or sxxyy: nominal CAN bitrate; simulated */
    SLCAN_VERSION,   /* V */
    SLCAN_SERIAL,    /* N */
    SLCAN_STATUS,    /* F */
    SLCAN_TIMESTAMP, /* Zn: only Z0 (off) is accepted */
};

struct slcan_command {
    enum slcan_kind kind;
    struct can_frame frame;
    unsigned argument;
};

/* Parses one line without its terminator. Returns false for malformed input,
 * which the device answers with BELL ('\a'). */
bool slcan_parse(const char *line, size_t length, struct slcan_command *command);

/* Formats a frame as t/T/r/R line including the trailing '\r'. Returns the
 * length written, or 0 if the frame is invalid or capacity is too small. */
size_t slcan_format(const struct can_frame *frame, char *line, size_t capacity);
#endif
