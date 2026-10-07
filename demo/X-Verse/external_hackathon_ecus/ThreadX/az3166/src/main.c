/* SPDX-License-Identifier: Apache-2.0 */
/* ThreadX zonal lighting controller on the MXChip AZ3166. The CAN bus is
 * simulated over the ST-LINK UART with the Lawicell SLCAN protocol, so the
 * unchanged X-Verse Zenoh2CAN bridge reaches it through python-can "slcan"
 * (or Linux slcand). The decision logic is the shared ../src/lights_protocol.c. */
#include "tx_api.h"
#include "board.h"
#include "display.h"
#include "lights_protocol.h"
#include "slcan.h"
#include <stdint.h>
#include <string.h>

#define QUEUE_DEPTH 32
#define FRAME_WORDS ((sizeof(struct can_frame) + sizeof(ULONG) - 1) / sizeof(ULONG))
#define RX_BYTES 256
#define HEARTBEAT_FLAG 1U
#define LINK_FLAG 2U
#define REDRAW_FLAG 1U
#define DIAG_ID 0x1F5U

/* Identity strings kept in the image for provenance checks (strings / hexdump). */
__attribute__((used, section(".identity"))) const char zonal_identity[] = "threadx-zonal-lights-az3166 " ZONAL_VERSION
    " ThreadX " THREADX_REVISION " cortex_m4/gnu SLCAN-over-UART";

static TX_THREAD ingress_thread, control_thread, display_thread;
static TX_QUEUE rx_byte_queue, frame_queue;
static TX_MUTEX uart_lock, status_lock;
static TX_EVENT_FLAGS_GROUP events, display_events;
static TX_TIMER heartbeat_timer;
static ULONG rx_byte_storage[RX_BYTES];
static ULONG frame_storage[QUEUE_DEPTH * FRAME_WORDS];
static ULONG ingress_stack[512], control_stack[512], display_stack[512];

static const ULONG timeout_ticks = (ULONG)ZONAL_TIMEOUT_MS * TX_TIMER_TICKS_PER_SECOND / 1000U;
static volatile bool link_open;
static volatile unsigned long rx_overflow, line_errors, tx_dropped;
static unsigned long received, rejected, dropped;  /* same meaning as Linux */

/* Display snapshot, written by the control thread under status_lock. */
static struct {
    bool reverse, brake, stale;
    unsigned long received;
} status;

static void require_tx(UINT result)
{
    if (result != TX_SUCCESS) board_fault();
}

static void stack_error(TX_THREAD *thread)
{
    (void)thread;
    board_fault();
}

static void on_uart_byte(unsigned char byte)
{
    ULONG word = byte;
    if (tx_queue_send(&rx_byte_queue, &word, TX_NO_WAIT) != TX_SUCCESS) ++rx_overflow;
}

/* One complete SLCAN line per call, never interleaved with another line. */
static void uart_send(const char *line, size_t length)
{
    require_tx(tx_mutex_get(&uart_lock, TX_WAIT_FOREVER));
    unsigned waited = 0;
    while (!board_uart_write(line, length)) {
        if (++waited > 50U) { ++tx_dropped; break; }  /* host not draining for 0.5 s */
        tx_thread_sleep(1);
    }
    require_tx(tx_mutex_put(&uart_lock));
}

static void reply(const char *text) { uart_send(text, strlen(text)); }

static void publish(const struct can_frame *frame)
{
    char line[SLCAN_MTU + 1];
    size_t length = slcan_format(frame, line, sizeof(line));
    if (length && link_open) uart_send(line, length);
}

static void heartbeat(ULONG argument)
{
    (void)argument;
    tx_event_flags_set(&events, HEARTBEAT_FLAG, TX_OR);
}

static void set_link(bool open)
{
    if (link_open == open) return;
    link_open = open;
    board_link_led(open);
    require_tx(tx_event_flags_set(&events, LINK_FLAG, TX_OR));
    require_tx(tx_event_flags_set(&display_events, REDRAW_FLAG, TX_OR));
}

static void handle_line(const char *line, size_t length, bool overlong)
{
    struct slcan_command command;
    if (overlong || !slcan_parse(line, length, &command)) {
        ++line_errors;
        reply("\a");
        return;
    }
    switch (command.kind) {
    case SLCAN_OPEN: set_link(true); reply("\r"); break;
    case SLCAN_CLOSE: set_link(false); reply("\r"); break;
    case SLCAN_BITRATE:  /* Nominal only: the UART carries frames, not bits. */
    case SLCAN_TIMESTAMP: reply(link_open ? "\a" : "\r"); break;
    case SLCAN_VERSION: reply("V1010\r"); break;
    case SLCAN_SERIAL: reply("NAZ31\r"); break;
    case SLCAN_STATUS: {
        static unsigned long reported;
        unsigned long losses = rx_overflow + board_uart_overruns() + dropped + tx_dropped;
        char flags[] = "F00\r";
        if (losses != reported) flags[2] = '8';  /* Lawicell bit 3: data overrun */
        reported = losses;
        reply(link_open ? flags : "\a");
        break;
    }
    case SLCAN_FRAME: {
        if (!link_open) { ++line_errors; reply("\a"); break; }
        reply(command.frame.can_id & CAN_EFF_FLAG ? "Z\r" : "z\r");
        /* The virtual bus has one other node: this controller. */
        union { ULONG words[FRAME_WORDS]; struct can_frame frame; } message = {0};
        struct can_frame output;
        message.frame = command.frame;
        if (!lights_decode(&message.frame, &output)) { ++rejected; break; }
        UINT result = tx_queue_send(&frame_queue, message.words, TX_NO_WAIT);
        if (result == TX_QUEUE_FULL) ++dropped;
        else require_tx(result);
        break;
    }
    default: ++line_errors; reply("\a"); break;
    }
}

static void ingress_entry(ULONG argument)
{
    (void)argument;
    char line[SLCAN_MTU];
    size_t length = 0;
    bool overlong = false;
    board_uart_start(on_uart_byte);
    for (;;) {
        ULONG word;
        require_tx(tx_queue_receive(&rx_byte_queue, &word, TX_WAIT_FOREVER));
        const char c = (char)word;
        if (c == '\n') continue;  /* tolerate CRLF terminals */
        if (c != '\r') {
            if (length < sizeof(line)) line[length++] = c;
            else overlong = true;
            continue;
        }
        if (length || overlong) handle_line(line, length, overlong);
        length = 0;
        overlong = false;
    }
}

static void apply(const struct can_frame *output, bool stale)
{
    const bool reverse = output->data[0] & 1U, brake = output->data[0] & 2U;
    board_lamps(reverse, brake);
    require_tx(tx_mutex_get(&status_lock, TX_WAIT_FOREVER));
    status.reverse = reverse;
    status.brake = brake;
    status.stale = stale;
    status.received = received;
    require_tx(tx_mutex_put(&status_lock));
    require_tx(tx_event_flags_set(&display_events, REDRAW_FLAG, TX_OR));
}

static void control_entry(ULONG argument)
{
    (void)argument;
    struct can_frame output;
    lights_off(&output);
    apply(&output, false);
    ULONG last_valid = 0;
    bool have_valid = false, stale = false, beat = false;
    for (;;) {
        union { ULONG words[FRAME_WORDS]; struct can_frame frame; } message = {0};
        UINT result = tx_queue_receive(&frame_queue, message.words, 1);
        if (result == TX_SUCCESS) {
            if (link_open && lights_decode(&message.frame, &output)) {
                last_valid = tx_time_get();
                have_valid = true;
                stale = false;
                ++received;
                apply(&output, false);
                publish(&output);
            }
        } else if (result != TX_QUEUE_EMPTY) require_tx(result);
        if (timeout_ticks && have_valid && !stale && tx_time_get() - last_valid >= timeout_ticks) {
            stale = true;
            lights_off(&output);
            apply(&output, true);
            publish(&output);
        }
        ULONG flags;
        if (tx_event_flags_get(&events, HEARTBEAT_FLAG | LINK_FLAG, TX_OR_CLEAR, &flags, TX_NO_WAIT) != TX_SUCCESS)
            continue;
        if (flags & LINK_FLAG) {
            if (!link_open) {  /* X-Verse link closed: fail safe, lamps off */
                lights_off(&output);
                have_valid = stale = false;
                apply(&output, false);
            }
            publish(&output);  /* a newly opened host learns the current command */
        }
        if (flags & HEARTBEAT_FLAG) {
            board_heartbeat_led(beat = !beat);
            const unsigned long seconds = tx_time_get() / TX_TIMER_TICKS_PER_SECOND;
            const unsigned long losses = rx_overflow + board_uart_overruns() + dropped + tx_dropped;
            struct can_frame diag = {.can_id = DIAG_ID, .can_dlc = 8, .data = {
                (unsigned char)(output.data[0] | (stale ? 4U : 0U) | (losses ? 8U : 0U) |
                                (display_available() ? 16U : 0U)),
                (unsigned char)received, (unsigned char)(received >> 8),
                (unsigned char)rejected, (unsigned char)line_errors,  /* modulo 256 */
                (unsigned char)seconds, (unsigned char)(seconds >> 8), (unsigned char)(seconds >> 16)}};
            publish(&diag);
            require_tx(tx_event_flags_set(&display_events, REDRAW_FLAG, TX_OR));
        }
    }
}

static void append(char **out, const char *text) { while (*text) *(*out)++ = *text++; }

static void append_number(char **out, unsigned long value)
{
    char digits[12];
    unsigned count = 0;
    do { digits[count++] = (char)('0' + value % 10U); value /= 10U; } while (value);
    while (count) *(*out)++ = digits[--count];
}

static void display_entry(ULONG argument)
{
    (void)argument;
    tx_thread_sleep(TX_TIMER_TICKS_PER_SECOND / 10U);  /* OLED power-up time */
    if (!display_init()) return;  /* Lamps and SLCAN do not depend on the OLED. */
    for (;;) {
        ULONG flags;
        tx_event_flags_get(&display_events, REDRAW_FLAG, TX_OR_CLEAR, &flags, TX_WAIT_FOREVER);
        require_tx(tx_mutex_get(&status_lock, TX_WAIT_FOREVER));
        const typeof(status) snapshot = status;
        require_tx(tx_mutex_put(&status_lock));
        char text[24], *out;
        display_clear();
        display_text(0, "ThreadX Zonal");
        display_text(1, link_open ? "X-Verse: online" : "X-Verse: offline");
        display_text(2, snapshot.brake ? "Brake:   ON" : "Brake:   off");
        display_text(3, snapshot.reverse ? "Reverse: ON" : "Reverse: off");
        out = text;
        append(&out, "RX ");
        append_number(&out, snapshot.received);
        append(&out, " rej ");
        append_number(&out, rejected);
        *out = '\0';
        display_text(4, text);
        out = text;
        append(&out, snapshot.stale ? "STALE up " : "up ");
        append_number(&out, tx_time_get() / TX_TIMER_TICKS_PER_SECOND);
        append(&out, "s");
        *out = '\0';
        display_text(5, text);
        if (!display_flush()) return;
    }
}

void tx_application_define(void *first_unused_memory)
{
    (void)first_unused_memory;
    require_tx(tx_thread_stack_error_notify(stack_error));
    require_tx(tx_queue_create(&rx_byte_queue, "UART RX bytes", 1, rx_byte_storage, sizeof(rx_byte_storage)));
    require_tx(tx_queue_create(&frame_queue, "CAN status", FRAME_WORDS, frame_storage, sizeof(frame_storage)));
    require_tx(tx_mutex_create(&uart_lock, "UART TX", TX_INHERIT));
    require_tx(tx_mutex_create(&status_lock, "status", TX_INHERIT));
    require_tx(tx_event_flags_create(&events, "controller events"));
    require_tx(tx_event_flags_create(&display_events, "display events"));
    require_tx(tx_timer_create(&heartbeat_timer, "zonal heartbeat", heartbeat, 0,
        TX_TIMER_TICKS_PER_SECOND, TX_TIMER_TICKS_PER_SECOND, TX_AUTO_ACTIVATE));
    require_tx(tx_thread_create(&control_thread, "zonal lighting control", control_entry, 0,
        control_stack, sizeof(control_stack), 10, 10, TX_NO_TIME_SLICE, TX_AUTO_START));
    require_tx(tx_thread_create(&ingress_thread, "SLCAN UART ingress", ingress_entry, 0,
        ingress_stack, sizeof(ingress_stack), 11, 11, TX_NO_TIME_SLICE, TX_AUTO_START));
    require_tx(tx_thread_create(&display_thread, "OLED status", display_entry, 0,
        display_stack, sizeof(display_stack), 20, 20, TX_NO_TIME_SLICE, TX_AUTO_START));
}

int main(void)
{
    board_init();
    tx_kernel_enter();
    return 0;
}
