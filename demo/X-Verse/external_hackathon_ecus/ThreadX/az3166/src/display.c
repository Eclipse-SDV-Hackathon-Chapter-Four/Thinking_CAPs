/* SPDX-License-Identifier: Apache-2.0 */
#include "display.h"
#include "board.h"
#include <stdint.h>
#include <string.h>

extern const uint16_t font7x10[95 * 10];

static unsigned char frame[8][128];
static bool available;

bool display_init(void)
{
    available = board_oled_init();
    return available;
}

bool display_available(void) { return available; }

void display_clear(void) { memset(frame, 0, sizeof(frame)); }

void display_text(unsigned row, const char *text)
{
    const unsigned top = 2U + row * 10U;
    for (unsigned column = 0; *text && column + 7U <= 128U; column += 7U, ++text) {
        unsigned char c = (unsigned char)*text;
        if (c < 0x20U || c > 0x7EU) c = '?';
        const uint16_t *glyph = &font7x10[(c - 0x20U) * 10U];
        for (unsigned y = 0; y < 10U && top + y < 64U; ++y)
            for (unsigned x = 0; x < 7U; ++x)
                if (glyph[y] & (0x8000U >> x))
                    frame[(top + y) / 8U][column + x] |= (unsigned char)(1U << ((top + y) % 8U));
    }
}

bool display_flush(void)
{
    for (unsigned page = 0; available && page < 8U; ++page)
        if (!board_oled_page(page, frame[page])) available = false;  /* stop retrying */
    return available;
}
