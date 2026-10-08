# Software requirements — X-Verse end-to-end demonstration

Each requirement is derived from a [system requirement](system-requirements.md), allocated
to a software element of the [architecture](../swe2-architecture/architecture.md), and
verified by unit (UT), integration (ITC) or qualification (QTC) test cases. The report
generator checks this traceability in both directions.

| ID | Requirement | Derived from | Allocated to | Verified by |
| --- | --- | --- | --- | --- |
| SWR-01 | The launcher shall start the components in dependency order, start a Zenoh router when none answers on `127.0.0.1:7447`, supervise processes and containers, and stop everything it started on Ctrl+C. | SYS-05 | Launcher | UT-LAUNCHER, ITC-01, ITC-02, QTC-01 |
| SWR-02 | The virtual vehicle shall publish the vehicle state (speed, clock) on Zenoh and apply the VCU throttle, brake and steering commands to the CARLA ego vehicle. | SYS-01 | Virtual vehicle | ITC-03, ITC-12, QTC-02 |
| SWR-03 | Vehicle Manual Control shall publish the driver requests (pedals, steering, cruise control, reverse), toggle a vehicle-speed publish inhibit with the `I` key, and accept the same key presses on its scripted input channel (`test/manual_control/input`) for automated tests. | SYS-01, SYS-03 | Manual control | ITC-03, QTC-02, QTC-03 |
| SWR-04 | The VCU shall compute throttle and brake commands, engage cruise control only at 10 km/h or more, and disengage it on braking and on the ADAS cancel request. | SYS-01, SYS-03 | VCU | ITC-04, QTC-02, QTC-03 |
| SWR-05 | The Zenoh–SOME/IP bridge shall convert payloads between Zenoh keys and SOME/IP events according to its mapping, including the cruise-control cancel request (event 30603). | SYS-02, SYS-03 | SOME/IP bridge | UT-SOMEIP, ITC-05, QTC-03 |
| SWR-06 | The S-CORE cruise-control application shall compute the throttle request and, when no speed sample was accepted for the signal budget plus the failed debounce, cancel cruise control and send the cancel request until the VCU reports disengaged. | SYS-02, SYS-03 | Cruise-control app | UT-SCORE, ITC-06, QTC-03 |
| SWR-07 | The cruise-control diagnostics server shall qualify DTC `CC.LostCommunication` with the same signal contract and debounce, and serve it with the vehicle speed and cruise state over SOVD through the PR #16 `sovd_adapter`. | SYS-03 | Diagnostics server | UT-PR16, ITC-05, ITC-07, QTC-03 |
| SWR-08 | certgen shall create a CA, a server certificate and one client certificate per vehicle target, with the target id as common name. | SYS-04 | certgen | ITC-08 |
| SWR-09 | The OTA backend shall offer the operator console and API, accept device connections only with a client certificate from its CA, store artifacts with their SHA-256 and track campaigns with per-target status. | SYS-04 | OTA backend | UT-OTA, ITC-09, ITC-10, QTC-04 |
| SWR-10 | The RTCU shall register the vehicle, probe every configured target, poll for campaigns, verify the artifact digest, install it with adb and report each phase; a campaign for an unreachable target shall end as failed instead of hanging. | SYS-04 | RTCU | ITC-10, ITC-11, QTC-04, QTC-05, QTC-06 |
| SWR-11 | The Android target shall boot, accept adb installs from the RTCU and run the cluster application. | SYS-04 | Android target | ITC-13, QTC-04 |
| SWR-12 | The OpenSOVD gateway shall serve component `cruise` with `vehicle_speed`, `cruise_state`, `speed_sensor_fault_status` (time-based debounce) and the read-write injection switch `speed_sensor_stuck` over SOVD on `:7690`. | SYS-06 | OpenSOVD gateway | ITC-14, ITC-15 |
| SWR-13 | The SOVD Adapter Console shall subscribe to the vehicle speed on Zenoh, qualify P0500 (implausible speed, mirrored into the gateway's switch) and U0104 (no sample for more than 500 ms), and mirror each confirmed and healed fault as a classic DTC in the ECU simulator, read back through the CDA. | SYS-06 | SOVD Adapter Console | UT-CONSOLE, ITC-15, QTC-07 |
| SWR-14 | The classic diagnostic path shall serve the ECU simulator's DTCs over the CDA's SOVD API (UDS over DoIP behind it). | SYS-06 | CDA + ECU simulator | ITC-15, QTC-07 |
| SWR-15 | The ThreadX lighting ECU shall receive the VCU brake and reverse status as CAN frame `0x1F1` through the Zenoh2CAN bridge and answer with the light commands in `0x1F4`, published as `vehicle/lights/*_cmd`. | SYS-07 | ThreadX lighting ECU | UT-THREADX, ITC-16 |
