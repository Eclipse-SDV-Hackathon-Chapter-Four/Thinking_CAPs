/* Planning evidence only; not a contribution source file. No kernel stubs. */
#include "tx_api.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define STACK_BYTES 8192U
static TX_THREAD worker;
static TX_THREAD observer;
static ALIGN_TYPE storage[(2U * STACK_BYTES + 64U) / sizeof(ALIGN_TYPE)];
static UCHAR *worker_start;
static UCHAR *observer_start;
static volatile UINT visits;

void __real__tx_thread_stack_build(TX_THREAD *thread, VOID (*entry)(VOID));
void __wrap__tx_thread_stack_build(TX_THREAD *thread, VOID (*entry)(VOID))
{
    printf("port stack build: start=%p end=%p size=%u\n",
           thread->tx_thread_stack_start, thread->tx_thread_stack_end,
           (unsigned int) thread->tx_thread_stack_size);
    __real__tx_thread_stack_build(thread, entry);
}

static void fail(const char *message)
{
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
}

static void worker_entry(ULONG input)
{
    if (input != 17U) fail("scalar callback input");
    visits++;
    if (tx_thread_sleep(1U) != TX_SUCCESS) fail("worker sleep");
    visits++;
}

static void observer_entry(ULONG input)
{
    (void) input;
    if (tx_thread_sleep(3U) != TX_SUCCESS) fail("observer sleep");
    if (visits != 2U || worker.tx_thread_state != TX_COMPLETED)
        fail("scheduled worker did not complete across sleep/wake");
    puts("PASS: real thread creation and scheduling across sleep/wake");
    exit(0);
}

void tx_application_define(void *unused)
{
    UINT status;
    uintptr_t expected_start = (uintptr_t) worker_start;
    ULONG expected_size = STACK_BYTES;
    (void) unused;
#ifdef TX_ENABLE_STACK_CHECKING
    expected_start = (expected_start + sizeof(ULONG) - 1U) &
                     ~((uintptr_t) sizeof(ULONG) - 1U);
    expected_size -= (ULONG) sizeof(ULONG);
    if (expected_start != (uintptr_t) worker_start)
        expected_size -= (ULONG) sizeof(ULONG);
#endif
    printf("create input=%p expected_start=%p expected_size=%u\n",
           (void *) worker_start, (void *) expected_start,
           (unsigned int) expected_size);
    status = tx_thread_create(&worker, "744 worker", worker_entry, 17U,
                              worker_start, STACK_BYTES, 15U, 15U,
                              TX_NO_TIME_SLICE, TX_AUTO_START);
    if (status != TX_SUCCESS) fail("worker create");
    if ((uintptr_t) worker.tx_thread_stack_start != expected_start ||
        worker.tx_thread_stack_size != expected_size ||
        (uintptr_t) worker.tx_thread_stack_end != expected_start + expected_size - 1U)
        fail("adjusted stack metadata");
    if ((uintptr_t) worker.tx_thread_stack_ptr < expected_start ||
        (uintptr_t) worker.tx_thread_stack_ptr > expected_start + expected_size - 1U)
        fail("initial stack pointer outside supplied storage");
    status = tx_thread_create(&observer, "744 observer", observer_entry, 0U,
                              observer_start, STACK_BYTES, 16U, 16U,
                              TX_NO_TIME_SLICE, TX_AUTO_START);
    if (status != TX_SUCCESS) fail("observer create");
}

int main(int argc, char **argv)
{
    uintptr_t maximum_ulong = (uintptr_t) ((ULONG) ~((ULONG) 0));
    (void) argv;
    setvbuf(stdout, NULL, _IONBF, 0);
    worker_start = (UCHAR *) storage + (argc > 1 ? 1U : 0U);
    observer_start = (UCHAR *) storage + STACK_BYTES + 32U;
    printf("sizeof(ULONG)=%zu sizeof(ALIGN_TYPE)=%zu sizeof(void*)=%zu\n",
           sizeof(ULONG), sizeof(ALIGN_TYPE), sizeof(void *));
    printf("stack=%p ULONG_max=0x%llx\n", (void *) worker_start,
           (unsigned long long) maximum_ulong);
    if (sizeof(ALIGN_TYPE) <= sizeof(ULONG) ||
        sizeof(ALIGN_TYPE) < sizeof(void *) ||
        (uintptr_t) worker_start <= maximum_ulong)
        fail("64-bit high-address preconditions absent");
#ifdef TX_MISRA_ENABLE
    printf("real ULONG shim roundtrip=%p\n",
           TX_ULONG_TO_POINTER_CONVERT(TX_POINTER_TO_ULONG_CONVERT(worker_start)));
#endif
    tx_kernel_enter();
    fail("kernel unexpectedly returned");
    return 1;
}
