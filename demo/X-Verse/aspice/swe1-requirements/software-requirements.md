# Software requirements — X-Verse end-to-end demonstration

Each requirement is derived from a [system requirement](system-requirements.md), allocated
to a software element of the [architecture](../swe2-architecture/architecture.md), and
verified by unit (UT), integration (ITC) or qualification (QTC) test cases. The report
generator checks this traceability in both directions.

| ID | Requirement | Derived from | Allocated to | Verified by |
| --- | --- | --- | --- | --- |
| SWR-01 | The launcher shall start the components in dependency order, start a Zenoh router when none answers on `127.0.0.1:7447`, supervise processes and containers, and stop everything it started on Ctrl+C. | SYS-05 | Launcher | UT-LAUNCHER, ITC-01, ITC-02, QTC-01 |
| SWR-02 | The virtual vehicle shall publish the vehicle state (speed, clock) on Zenoh and apply the VCU throttle, brake and steering commands to the CARLA ego vehicle. | SYS-01 | Virtual vehicle | ITC-03, ITC-12, QTC-02 |
| SWR-03 | Vehicle Manual Control shall publish the driver requests (pedals, steering, cruise control, reverse) and toggle a vehicle-speed publish inhibit with the `I` key. | SYS-01, SYS-03 | Manual control | ITC-03, QTC-02, QTC-03 |
| SWR-04 | The VCU shall compute throttle and brake commands, engage cruise control only at 10 km/h or more, and disengage it on braking and on the ADAS cancel request. | SYS-01, SYS-03 | VCU | ITC-04, QTC-02, QTC-03 |
| SWR-05 | The Zenoh–SOME/IP bridge shall convert payloads between Zenoh keys and SOME/IP events according to its mapping, including the cruise-control cancel request (event 30603). | SYS-02, SYS-03 | SOME/IP bridge | UT-SOMEIP, ITC-05, QTC-03 |
| SWR-06 | The S-CORE cruise-control application shall compute the throttle request and, when no speed sample was accepted for the signal budget plus the failed debounce, cancel cruise control and send the cancel request until the VCU reports disengaged. | SYS-02, SYS-03 | Cruise-control app | UT-SCORE, ITC-06, QTC-03 |
| SWR-07 | The cruise-control diagnostics server shall qualify DTC `CC.LostCommunication` with the same signal contract and debounce, and serve it with the vehicle speed and cruise state over SOVD through the PR #16 `sovd_adapter`. | SYS-03 | Diagnostics server | UT-PR16, ITC-05, ITC-07, QTC-03 |
| SWR-08 | certgen shall create a CA, a server certificate and one client certificate per vehicle target, with the target id as common name. | SYS-04 | certgen | ITC-08 |
| SWR-09 | The OTA backend shall offer the operator console and API, accept device connections only with a client certificate from its CA, store artifacts with their SHA-256 and track campaigns with per-target status. | SYS-04 | OTA backend | UT-OTA, ITC-09, ITC-10, QTC-04 |
| SWR-10 | The RTCU shall register the vehicle, probe every configured target, poll for campaigns, verify the artifact digest, install it with adb and report each phase; a campaign for an unreachable target shall end as failed instead of hanging. | SYS-04 | RTCU | ITC-10, ITC-11, QTC-04, QTC-05, QTC-06 |
| SWR-11 | The Android target shall boot, accept adb installs from the RTCU and run the cluster application. | SYS-04 | Android target | ITC-13, QTC-04 |
