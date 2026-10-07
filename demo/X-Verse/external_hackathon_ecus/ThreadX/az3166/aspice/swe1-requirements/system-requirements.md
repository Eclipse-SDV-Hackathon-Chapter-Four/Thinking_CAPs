# System requirements (input to SWE.1)

These requirements are the system-level input (SYS.2 output) for the software
of the **AZ3166 zonal lighting ECU**. They come from the X-Verse lighting use
case, the [CAN lighting contract](../../../docs/can-lighting-contract.md) and the
agreed hackathon scope. This is a demonstration set; it is not a full SYS.2
specification.

### SYS-01 Lamp control from VCU status
The zonal lighting ECU shall switch the vehicle's brake and reverse lamps
according to the brake and reverse status published by the X-Verse VCU.

### SYS-02 Vehicle network contract
The ECU shall exchange the VCU status (`0x1F1`) and the BCM light command
(`0x1F4`) as defined by the X-Verse CAN lighting contract. The exchange goes
through the existing Zenoh2CAN bridge and must not modify that bridge.

### SYS-03 Safe state
The ECU shall bring both lamps to *off* at power-up, when communication with
the vehicle network ends, and on detected internal faults.

### SYS-04 Diagnostic observability
The ECU shall make its liveness, its communication health and its current
lamp state observable to developers and test equipment.

### SYS-05 Target platform
The ECU shall run on the MXChip AZ3166 board (STM32F412) under Eclipse ThreadX.
It shall connect to the vehicle network through the board's USB serial port,
because the board has no CAN transceiver.

### SYS-06 Timing
The ECU shall deliver a lamp command at its network boundary in at most
100 ms after it receives a changed VCU status.
