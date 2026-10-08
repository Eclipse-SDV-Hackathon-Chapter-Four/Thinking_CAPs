# Qualification test — X-Verse end-to-end demonstration

Scenario tests of the system requirements, all checked automatically. QTC-02, QTC-03 and
QTC-07 drive the vehicle with [`tools/qualification_check.py`](../tools/qualification_check.py):
it presses the driver keys through Manual Control's scripted input channel
(`test/manual_control/input`, handled exactly like the keyboard) and observes every expected
reaction on Zenoh and over SOVD (`generate_report.py --qualify`). The others are evaluated
from the records of the running system.

| ID | Scenario | Steps and expected result | Evidence | Verifies |
| --- | --- | --- | --- | --- |
| QTC-01 | One-command start and stop | `run_autoverse.py --enable-camera-display --vcu-zenoh` starts every component; Ctrl+C stops them | supervisor logs: a run that reached "Supervisor is now running" and a complete shutdown (automatic) | SWR-01 |
| QTC-02 | Drive and cruise control | Hold `W` until 18 km/h, release and coast 1 s like a driver; `C`: VCU `cc_engage_sts = 1` and S-CORE `cruise_state` active over SOVD; with no pedal pressed, cruise control keeps the vehicle moving (≥ 5 km/h for 8 s, VCU throttle command > 0; regulation accuracy is not part of this simple feature); `S`: VCU disengages, vehicle stops | `qualification_check.py` (automatic, driven) | SWR-02, SWR-03, SWR-04 |
| QTC-03 | Lost speed signal | With cruise engaged press `I`: speed samples stop, DTC `CC.LostCommunication` failed and confirmed over SOVD, ADAS cancel request on Zenoh, VCU disengages, S-CORE `standby`; `I` again: speed resumes, DTC passed | `qualification_check.py` (automatic, driven) | SWR-03..SWR-07 |
| QTC-04 | OTA update of the Cuttlefish cluster | Upload the APK, push to `PC-CUTTLEFISH-01`: `downloading → installing → success`, app present | campaign record in the OTA backend (automatic) | SWR-09, SWR-10, SWR-11 |
| QTC-05 | OTA update of the Raspberry Pi | Push to `PI-ANDROID-15` over Ethernet: `success` | campaign record in the OTA backend (automatic) | SWR-10 |
| QTC-06 | OTA to an unreachable target | Push to an offline target: the campaign closes as `failed` instead of hanging | campaign record in the OTA backend (automatic) | SWR-10 |
| QTC-07 | Lost speed signal seen by the OpenSOVD vECU | Press `I`: the console qualifies U0104, the ECU DTC `01E242` reads `0x2F` through the CDA; `I` again: U0104 heals, the DTC reads `0x28`; P0500 stays passed | `qualification_check.py` (automatic, driven) | SWR-13, SWR-14 |

Before each driving case the ego vehicle is placed, stopped, at the start of the longest
straight lane of the CARLA map (spawn point 80 of Town10HD, 178 m), so the result does not
depend on where the previous run left the vehicle.

## Known defect (not in this use case)

**Set-speed keys `Z` / `X` change the target by a multiple of 5 km/h.** Found by the first
automated run of QTC-02: one `X` press raised the S-CORE set speed from 18.1 to 73.1 km/h
(+55 instead of +5). The SOME/IP bridge sends the delta once and resets it to 0 after
100 ms (`kDeltaResetDelayMs`); the S-CORE cruise-control app holds the last delta and adds
it in `UpdateState()` on every input it receives (`cruise_control.cpp`), about 11 times in
those 100 ms. The use case does not use the set-speed keys, so QTC-02 does not test them;
a fix applies a delta once per received sample (edge, not level).

