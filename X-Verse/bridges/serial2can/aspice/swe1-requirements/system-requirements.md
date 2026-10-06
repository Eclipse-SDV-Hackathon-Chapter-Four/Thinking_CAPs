# System requirements (input to SWE.1)

These requirements are the system-level input for the **X-COM Serial2CAN
bridge**. They come from the Thinking CAPs plan, where X-COM is the
communication layer "Zenoh | SOME/IP | Serial2CAN" connecting physical and
virtual ECUs to X-Verse. This is a demonstration set.

### SYS-01 Serial ECU connectivity
The X-COM layer shall connect ECUs that have no CAN transceiver to the X-Verse
CAN bus in both directions, using a serial link. Example: the ThreadX ECU on
the MXChip AZ3166.

### SYS-02 Non-intrusive integration
The bridge shall integrate with X-Verse without modifying the baseline: the
Zenoh2CAN bridge, the VCU, the virtual vehicle and CARLA.

### SYS-03 Bus deployment options
The bridge shall support the standard X-Verse CAN bus (SocketCAN `vcan0`). It
shall also support a CAN bus that needs no administrator rights on developer
machines.

### SYS-04 Robust operation
The bridge shall survive device unplug and replug, and transient serial or
CAN errors, without a restart. A slow serial device shall never stall the CAN
side.

### SYS-05 Safe shutdown
When the bridge stops, it shall tell the connected ECUs, so they can enter
their safe state.

### SYS-06 Observability
The bridge shall report operational counters that are enough to diagnose
connection, filtering and loss problems.

### SYS-07 Timing
The bridge shall add little latency: an ECU round trip through the bridge
shall stay within the timing budget of the X-Verse lighting use case
(≤ 100 ms from VCU status to CARLA lamp state).
