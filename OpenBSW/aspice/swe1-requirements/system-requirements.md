# System requirements (input to SWE.1)

These requirements are the system-level input for the **OpenBSW zonal
diagnostic gateway**. They come from the Thinking CAPs plan:

- the "New Physical ECU Integration" extension (ThreadX and OpenBSW zonal ECUs)
- the OpenSOVD diagnostic path, where the Classic Diagnostic Adapter (CDA) reaches classic ECUs over UDS/DoIP

This is a demonstration set.

### SYS-01 Single diagnostic entry point
An off-board SOVD client shall be able to read identification and data, read
and clear fault memory, and run diagnostic routines on the zonal ECUs of the
X-Verse vehicle. It shall do so through OpenSOVD and the CDA, using one
diagnostic network entry point. Examples of zonal ECUs are the ThreadX rear
lighting controller and future front-zone ECUs.

### SYS-02 Standard diagnostic protocols
The entry point shall use these standard protocols:

- **DoIP** (ISO 13400-2) towards the CDA
- **UDS** (ISO 14229-1) as the application protocol
- **ISO-TP** (ISO 15765-2) on classic CAN towards the zonal ECUs

### SYS-03 Address-based routing
Each diagnostic request shall reach the ECU named by its target logical
address (physical addressing). A request to a functional address shall reach
every ECU in that group. Responses shall return to the requesting tester.

### SYS-04 Gateway self-diagnostics
The gateway shall itself be a diagnosable node. It shall provide:

- identification
- its routing configuration and statistics
- fault memory entries for zonal ECUs that stop responding

### SYS-05 Non-interference with the cruise-control use case
The gateway shall not change the behaviour, timing or diagnostics of the
cruise-control demonstration. In particular, it shall not affect:

- the S-CORE application
- the `sovd_adapter` path
- the X-Verse vehicle and CARLA
- the ThreadX lighting function

It shall not modify the X-Verse baseline.

### SYS-06 X-Verse integration without hardware
The gateway shall run in the X-Verse development environment with no
dedicated hardware: on Linux, on the X-Verse CAN bus (`vcan0`), reachable by
the CDA container. Later it shall be portable to the NXP S32K148 evaluation
board.

### SYS-07 Robustness
The following shall not block routing to other ECUs, and shall not exhaust
the gateway's resources:

- an unreachable, slow or misbehaving zonal ECU
- a malformed request
- a tester that disconnects

### SYS-08 Timing
For single-frame requests and responses, the gateway shall add at most 20 ms
to a diagnostic round trip, on top of the target ECU's own response time.

### SYS-09 Consistent addressing
Logical addresses and CAN identifiers shall be defined once. They shall be
consistent across the gateway, the zonal ECUs and the CDA diagnostic
description (MDD).

### SYS-10 Open-source basis
The gateway shall be built from unmodified Eclipse OpenBSW modules at a
pinned revision. The gateway's own source shall be Apache-2.0.
