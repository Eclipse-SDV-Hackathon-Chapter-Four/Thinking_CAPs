/* SPDX-License-Identifier: Apache-2.0 */
/* Six 18-character text rows on the 128x64 OLED (7x10 font). */
#ifndef ZONAL_DISPLAY_H
#define ZONAL_DISPLAY_H
#include <stdbool.h>

bool display_init(void);
void display_clear(void);
void display_text(unsigned row, const char *text);
/* Returns false once the OLED has failed; later calls do nothing. */
bool display_flush(void);
/* True after a successful initialization until the first I2C failure. */
bool display_available(void);
#endif
