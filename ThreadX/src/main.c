/* SPDX-License-Identifier: Apache-2.0 */
#include "tx_api.h"
#include "lights_protocol.h"
#include <errno.h>
#include <fcntl.h>
#include <net/if.h>
#include <sched.h>
#include <signal.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>
#include <linux/can/raw.h>

#define QUEUE_DEPTH 32
#define FRAME_WORDS ((sizeof(struct can_frame) + sizeof(ULONG) - 1) / sizeof(ULONG))
#define HEARTBEAT_FLAG 1U
static TX_THREAD receive_thread, control_thread;
static TX_QUEUE receive_queue;
static TX_TIMER heartbeat_timer;
static TX_EVENT_FLAGS_GROUP events;
static ULONG queue_storage[QUEUE_DEPTH * FRAME_WORDS];
static unsigned char receive_stack[4096], control_stack[4096];
static int can_fd = -1;
static unsigned timeout_ms;
static volatile sig_atomic_t stopping;
static unsigned long received, rejected, dropped, log_dropped;
static const char *interface_name;

/* Host I/O never waits for a CAN peer or a log reader inside a ThreadX thread. */
static void record(const char *format, ...)
{
    char line[512];
    va_list args;
    va_start(args, format);
    int size = vsnprintf(line, sizeof(line), format, args);
    va_end(args);
    if (size < 0) return;
    size_t length = (size_t)size < sizeof(line) ? (size_t)size : sizeof(line) - 1;
    if (write(STDOUT_FILENO, line, length) != (ssize_t)length) ++log_dropped;
}

static uint64_t now_ms(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) { perror("clock_gettime"); exit(1); }
    return (uint64_t)ts.tv_sec * 1000U + (uint64_t)ts.tv_nsec / 1000000U;
}

static void require_tx(UINT status, const char *operation)
{
    if (status != TX_SUCCESS) {
        fprintf(stderr, "%s failed: ThreadX status %u\n", operation, status);
        exit(1);
    }
}

static void send_lights(const struct can_frame *output)
{
    if (write(can_fd, output, sizeof(*output)) != sizeof(*output)) {
        perror("CAN light command send");
        exit(1);
    }
}

static void heartbeat(ULONG argument)
{
    (void)argument;
    /* A real ThreadX timer wakes the controller; no Linux I/O in the callback. */
    require_tx(tx_event_flags_set(&events, HEARTBEAT_FLAG, TX_OR), "heartbeat event");
}

static void receive_entry(ULONG argument)
{
    (void)argument;
    while (!stopping) {
        for (unsigned batch = 0; batch < QUEUE_DEPTH && !stopping; ++batch) {
            union { ULONG words[FRAME_WORDS]; struct can_frame frame; } message = {0};
            ssize_t size = read(can_fd, &message.frame, sizeof(message.frame));
            if (size < 0 && (errno == EAGAIN || errno == EINTR)) break;
            if (size != sizeof(message.frame)) {
                perror("CAN receive"); exit(1);
            }
            struct can_frame output;
            if (!lights_decode(&message.frame, &output)) { ++rejected; continue; }
            UINT result = tx_queue_send(&receive_queue, message.words, TX_NO_WAIT);
            if (result == TX_QUEUE_FULL) ++dropped;
            else require_tx(result, "receive queue send");
        }
        tx_thread_sleep(1);
    }
}

static void control_entry(ULONG argument)
{
    (void)argument;
    struct can_frame output;
    lights_off(&output);
    send_lights(&output);
    record("{\"event\":\"started\",\"component\":\"threadx-zonal-lights\","
           "\"simulation\":true,\"version\":\"%s\",\"threadx_revision\":\"%s\","
           "\"interface\":\"%s\",\"timeout_ms\":%u}\n",
           ZONAL_VERSION, THREADX_REVISION, interface_name, timeout_ms);
    uint64_t last_valid = 0;
    bool stale = false;
    while (!stopping) {
        union { ULONG words[FRAME_WORDS]; struct can_frame frame; } message = {0};
        UINT result = tx_queue_receive(&receive_queue, message.words, 1);
        if (result == TX_SUCCESS) {
            if (lights_decode(&message.frame, &output)) {
                last_valid = now_ms();
                stale = false;
                ++received;
                send_lights(&output);
                record("{\"event\":\"lights\",\"sequence\":%lu,\"reverse\":%s,"
                       "\"brake\":%s,\"stale\":false,\"can_id\":500}\n", received,
                       output.data[0] & 1U ? "true" : "false",
                       output.data[0] & 2U ? "true" : "false");
            }
        } else if (result != TX_QUEUE_EMPTY) require_tx(result, "receive queue read");
        if (timeout_ms && last_valid && !stale && now_ms() - last_valid >= timeout_ms) {
            stale = true;
            lights_off(&output);
            send_lights(&output);
            record("{\"event\":\"input_timeout\",\"stale\":true,\"reverse\":false,\"brake\":false}\n");
        }
        ULONG flags;
        if (tx_event_flags_get(&events, HEARTBEAT_FLAG, TX_OR_CLEAR, &flags, TX_NO_WAIT) == TX_SUCCESS)
            record("{\"event\":\"heartbeat\",\"tick\":%lu,\"received\":%lu,"
                   "\"rejected\":%lu,\"queue_dropped\":%lu,\"log_dropped\":%lu,\"stale\":%s}\n",
                   tx_time_get(), received, rejected, dropped, log_dropped, stale ? "true" : "false");
    }
    lights_off(&output);
    send_lights(&output);
    record("{\"event\":\"stopped\",\"received\":%lu,\"lights_off\":true}\n", received);
    close(can_fd);
    exit(0);
}

void tx_application_define(void *first_unused_memory)
{
    (void)first_unused_memory;
    require_tx(tx_queue_create(&receive_queue, "CAN status", FRAME_WORDS,
        queue_storage, sizeof(queue_storage)), "queue create");
    require_tx(tx_event_flags_create(&events, "controller events"), "events create");
    require_tx(tx_timer_create(&heartbeat_timer, "zonal heartbeat", heartbeat, 0,
        TX_TIMER_TICKS_PER_SECOND, TX_TIMER_TICKS_PER_SECOND, TX_AUTO_ACTIVATE), "timer create");
    require_tx(tx_thread_create(&control_thread, "zonal lighting control", control_entry, 0,
        control_stack, sizeof(control_stack), 10, 10, TX_NO_TIME_SLICE, TX_AUTO_START), "control thread create");
    require_tx(tx_thread_create(&receive_thread, "SocketCAN ingress", receive_entry, 0,
        receive_stack, sizeof(receive_stack), 11, 11, TX_NO_TIME_SLICE, TX_AUTO_START), "receive thread create");
}

static void stop_requested(int signum) { (void)signum; stopping = 1; }

static int open_can(const char *name)
{
    unsigned index = if_nametoindex(name);
    if (!index) { perror("CAN interface"); return -1; }
    int fd = socket(PF_CAN, SOCK_RAW | SOCK_NONBLOCK | SOCK_CLOEXEC, CAN_RAW);
    if (fd < 0) { perror("SocketCAN socket"); return -1; }
    const struct can_filter filter = {VCU_STATUS_ID, CAN_SFF_MASK | CAN_EFF_FLAG | CAN_RTR_FLAG};
    const struct sockaddr_can address = {.can_family = AF_CAN, .can_ifindex = (int)index};
    if (setsockopt(fd, SOL_CAN_RAW, CAN_RAW_FILTER, &filter, sizeof(filter)) != 0 ||
        bind(fd, (const struct sockaddr *)&address, sizeof(address)) != 0) {
        perror("SocketCAN filter/bind"); close(fd); return -1;
    }
    return fd;
}

int main(int argc, char **argv)
{
    interface_name = "vcan0";
    for (int index = 1; index < argc; ++index) {
        if (!strcmp(argv[index], "--version")) {
            printf("threadx-zonal-lights %s ThreadX %s linux/gnu simulation\n", ZONAL_VERSION, THREADX_REVISION);
            return 0;
        }
        if (!strcmp(argv[index], "--interface") && index + 1 < argc) interface_name = argv[++index];
        else if (!strcmp(argv[index], "--timeout-ms") && index + 1 < argc) {
            char *end;
            errno = 0;
            unsigned long value = strtoul(argv[++index], &end, 10);
            if (errno || !*argv[index] || *end || value > 3600000) {
                fprintf(stderr, "timeout must be 0..3600000 milliseconds\n"); return 2;
            }
            timeout_ms = (unsigned)value;
        } else {
            fprintf(stderr, "Usage: %s [--interface vcan0] [--timeout-ms 0] [--version]\n", argv[0]);
            return 2;
        }
    }
    if (strlen(interface_name) >= IF_NAMESIZE || strspn(interface_name, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-") != strlen(interface_name)) {
        fprintf(stderr, "Invalid CAN interface name\n"); return 2;
    }
    /* Upstream Linux simulation needs FIFO priorities 1..3. Fail explicitly
     * instead of silently running its scheduler with ineffective priorities. */
    int policy = sched_getscheduler(0);
    struct sched_param previous, probe = {.sched_priority = TX_LINUX_PRIORITY_SCHEDULE};
    if (sched_getparam(0, &previous) != 0 || sched_setscheduler(0, SCHED_FIFO, &probe) != 0) {
        fprintf(stderr, "ThreadX Linux requires FIFO scheduling: run with CAP_SYS_NICE or sufficient rtprio.\n");
        return 2;
    }
    if (sched_setscheduler(0, policy, &previous) != 0) { perror("restore scheduler"); return 1; }
    cpu_set_t allowed, selected;
    if (sched_getaffinity(0, sizeof(allowed), &allowed) != 0) { perror("CPU affinity"); return 1; }
    CPU_ZERO(&selected);
    for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) if (CPU_ISSET(cpu, &allowed)) { CPU_SET(cpu, &selected); break; }
    if (sched_setaffinity(0, sizeof(selected), &selected) != 0) { perror("pin simulation CPU"); return 1; }
    can_fd = open_can(interface_name);
    if (can_fd < 0) return 1;
    struct sigaction action = {.sa_handler = stop_requested};
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGINT, &action, NULL) || sigaction(SIGTERM, &action, NULL)) { perror("signals"); return 1; }
    struct sigaction ignore = {.sa_handler = SIG_IGN};
    sigemptyset(&ignore.sa_mask);
    if (sigaction(SIGPIPE, &ignore, NULL)) { perror("log pipe signal"); return 1; }
    int flags = fcntl(STDOUT_FILENO, F_GETFL);
    if (flags < 0 || fcntl(STDOUT_FILENO, F_SETFL, flags | O_NONBLOCK) < 0) { perror("log flags"); return 1; }
    tx_kernel_enter();
    return 1;
}
