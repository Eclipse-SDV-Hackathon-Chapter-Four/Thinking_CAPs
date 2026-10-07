# Issue — eclipse-openbsw/openbsw (bug report)

**Filed:** 7 October 2026 as https://github.com/eclipse-openbsw/openbsw/issues/661

**Title:** POSIX SocketCanTransceiver can deadlock the ThreadX POSIX port under load

**Labels:** bug

---

**Describe the bug**

`platforms/posix/bsp/socketCanTransceiver` runs its socket work inside
`signalGuarded()`, which blocks every signal (`sigfillset`) for the calling thread.
In `run()` it also calls back into the CAN stack (for example
`DoCanTransmitter::dataFramesSent`), which enters the RTOS
(`_tx_thread_interrupt_control` with ThreadX). The ThreadX Linux port suspends and
resumes threads with signals, so a thread that waits for the ThreadX lock with all
signals blocked can no longer be scheduled correctly.

**Steps to reproduce the bug**

An application built with `BUILD_TARGET_RTOS=THREADX` for POSIX that sends ISO-TP
multi-frame messages over `vcan0` while receiving over lwIP (a DoIP-to-DoCAN gateway).
Load the host CPU (here: load average above 40 from parallel builds) and run traffic.

**Expected behavior and actual behavior**

Expected: the application keeps running, as with `BUILD_TARGET_RTOS=FREERTOS`.
Actual: in 2 of 4 runs the process stopped making progress. gdb showed the CAN task in
`_tx_thread_interrupt_control` called from `DoCanTransmitter::dataFramesSent` inside
`SocketCanTransceiver::guardedRun`, and the Ethernet task in `_tx_event_flags_set`
waiting for the scheduler. The same application built with FreeRTOS passed 17 runs in a
row at a load of 70 to 130.

**Environment**

Ubuntu 22.04 (kernel 6.8), GCC 11.4, OpenBSW `432b9be6` (the transceiver is unchanged on
`main` at `b0550871`), ThreadX 6.4.3 POSIX port.

**Additional context**

Possible directions: keep the RTOS signals (SIGUSR1/SIGUSR2 for ThreadX) unblocked in
`signalGuarded()`, or block signals only around the socket system calls and not around
the callbacks into the stack.
