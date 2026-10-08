# Demo run 20260925T154721Z

| Path | Assertion | Expected | Observed | Verdict |
|---|---|---|---|---|
| A | gateway serves the cruise resources | `vehicle_speed,cruise_state,speed_sensor_fault_status,speed_sensor_stuck` | `vehicle_speed,cruise_state,speed_sensor_fault_status,speed_sensor_stuck` | **PASS** |
| A | no demo.* ids left | `0` | `0` | **PASS** |
| A | fault status before injection | `passed` | `passed` | **PASS** |
| A | cruise control engaged | `active` | `active` | **PASS** |
| A | injection accepted | `204` | `204` | **PASS** |
| A | status right after injection | `prefailed` | `prefailed` | **PASS** |
| A | status after debounce | `failed` | `failed` | **PASS** |
| A | cruise control reacts (their logic) | `unavailable` | `unavailable` | **PASS** |
| A | status after clear | `passed` | `passed` | **PASS** |
| B | active faults before injection | `none` | `none` | **PASS** |
| B | injection accepted | `201` | `201` | **PASS** |
| B | CDA reports the DTC over SOVD | `01E240/2F` | `01E240/2F` | **PASS** |
| B | active faults after clear | `none` | `none` | **PASS** |

Debounce qualified after 5.22 s. Raw responses in `raw/`, timeline in `timeline.log`.

**Overall: PASS** (13 assertions)
