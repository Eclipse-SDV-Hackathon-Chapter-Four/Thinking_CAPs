# System requirements — X-Verse end-to-end demonstration

Scope: the vehicle simulation run by `run_autoverse.py --enable-camera-display --vcu-zenoh`:
CARLA and the virtual vehicle, Vehicle Manual Control, the Zenoh VCU, the Zenoh–SOME/IP
bridge (`bridge-e2e`), the Eclipse S-CORE cruise-control ECU with its diagnostics server
(Eclipse inc_diagnostics, PR #16 `sovd_adapter`), the OTA vECU (certgen, EOL backend,
RTCU) updating the Android cluster targets, and the hackathon ECUs in
`external_hackathon_ecus/`: the OpenSOVD vECU (inc_diagnostics PR #40 gateway, SOVD Adapter
Console, classic CDA + ECU simulator) and the ThreadX zonal lighting ECU (MXChip AZ3166).

Demonstration work products; not an assessed capability level.

| ID | Requirement | Source |
| --- | --- | --- |
| SYS-01 | The system shall simulate a vehicle in CARLA that a driver controls through pedals, steering and cruise-control requests, and publish its state on the Zenoh vehicle network. | Track 2 use case "Drive" |
| SYS-02 | The cruise-control function shall run on an Eclipse S-CORE ECU that exchanges its inputs and outputs with the Zenoh vehicle network over SOME/IP. | Track 2 use case "Drive" |
| SYS-03 | When the vehicle-speed signal is lost at the cruise-control ECU, the system shall cancel cruise control and report DTC `CC.LostCommunication` over SOVD, and report recovery when the signal returns. | Track 2 use case "Diagnose"; issues #16, #44 |
| SYS-04 | The system shall update the instrument-cluster application over the air on every Android target of the vehicle, authenticate the vehicle with mutual TLS, and report the result per target. | Track 2 use case "Update"; issues #3, #12, #41 |
| SYS-05 | The whole environment shall start and stop with one command. | Demonstration operability; issue #40 |
| SYS-06 | The cruise-control diagnostics shall also be available through the OpenSOVD gateway of inc_diagnostics PR #40, and a diagnostic console shall correlate the vehicle-speed signal on the Zenoh vehicle network with the SOVD faults and the classic diagnostic path (CDA reading UDS DTCs from an ECU). | Track 2 use case "Diagnose"; inc_diagnostics PR #40 |
| SYS-07 | A zonal lighting ECU running Eclipse ThreadX shall switch the brake and reverse lights of the vehicle from the VCU status over CAN. | Hackathon ECU (ThreadX on the MXChip AZ3166) |
