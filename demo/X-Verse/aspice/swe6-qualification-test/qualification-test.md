# Qualification test — X-Verse end-to-end demonstration

Scenario tests of the system requirements. Evidence is either checked automatically by the
report generator (records of the running system) or comes from a witnessed live run.

| ID | Scenario | Steps and expected result | Evidence | Verifies |
| --- | --- | --- | --- | --- |
| QTC-01 | One-command start and stop | `run_autoverse.py --enable-camera-display --vcu-zenoh` starts every component; Ctrl+C stops them | supervisor logs: a run that reached "Supervisor is now running" and a complete shutdown (automatic) | SWR-01 |
| QTC-02 | Drive and cruise control | Accelerate above 10 km/h, `C` engages cruise control, `Z`/`X` change the set speed, `S` disengages | witnessed in the live dry run | SWR-02, SWR-03, SWR-04 |
| QTC-03 | Lost speed signal | With cruise engaged press `I`: cruise control cancels, VCU disengages, DTC `CC.LostCommunication` reports failed; `I` again: DTC passes | witnessed by the whole competition in the live dry run (issue #44) | SWR-03..SWR-07 |
| QTC-04 | OTA update of the Cuttlefish cluster | Upload the APK, push to `PC-CUTTLEFISH-01`: `downloading → installing → success`, app present | campaign record in the OTA backend (automatic) | SWR-09, SWR-10, SWR-11 |
| QTC-05 | OTA update of the Raspberry Pi | Push to `PI-ANDROID-15` over Ethernet: `success` | campaign record in the OTA backend (automatic) | SWR-10 |
| QTC-06 | OTA to an unreachable target | Push to an offline target: the campaign closes as `failed` instead of hanging | campaign record in the OTA backend (automatic) | SWR-10 |
